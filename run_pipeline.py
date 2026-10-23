
from pathlib import Path
import logging
import sys

import pandas as pd

from src.data_cleaning import run_cleaning_pipeline
from src.data_quality import profile_dataset
from src.product_categorization import add_categories
from src.analytics import export_analytics
from src.statistical_analysis import (
    calculate_descriptive_statistics,
    detect_iqr_outliers,
)
from src.visualizations import generate_charts
from src.insight_generator import generate_findings
import argparse

import src.data_cleaning as cleaning_module
import src.data_quality as quality_module
import src.visualizations as visualization_module
import src.insight_generator as insight_module


ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "data" / "raw" / "online_retail.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "output" / "reports"



def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the e-commerce sales analytics pipeline."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "raw" / "online_retail.csv",
        help="Path to the input retail CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT,
        help="Root directory for generated outputs.",
    )
    args = parser.parse_args(argv)

    input_file = args.input.resolve()
    output_root = args.output.resolve()

    global PROCESSED_DIR, REPORT_DIR
    PROCESSED_DIR = output_root / "data" / "processed"
    REPORT_DIR = output_root / "output" / "reports"
    charts_dir = output_root / "output" / "charts"

    cleaning_module.RAW_FILE = input_file
    cleaning_module.PROCESSED_DIR = PROCESSED_DIR
    cleaning_module.REPORT_DIR = REPORT_DIR

    quality_module.OUTPUT_DIR = REPORT_DIR

    visualization_module.REPORT_DIR = REPORT_DIR
    visualization_module.CHART_DIR = charts_dir
    visualization_module.PROCESSED_FILE = (
        PROCESSED_DIR / "categorized_sales_data.csv"
    )

    insight_module.REPORT_DIR = REPORT_DIR

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:

        # Step 1: Profile raw data quality.
        logging.info("Step 1/7: Profiling raw data quality")
        profile_dataset(input_file)

        # Step 2: Clean raw transaction data.
        logging.info("Step 2/7: Cleaning raw data")
        cleaned_df = run_cleaning_pipeline()

        if cleaned_df.empty:
            raise ValueError("Cleaning produced no sales rows.")

        # Step 3: Categorize products.
        logging.info("Step 3/7: Categorizing products")
        categorized_df = add_categories(cleaned_df)

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        categorized_path = PROCESSED_DIR / "categorized_sales_data.csv"
        categorized_df.to_csv(categorized_path, index=False)

        logging.info(
            "Saved %s categorized rows to %s",
            f"{len(categorized_df):,}",
            categorized_path,
        )

        # Step 4: Generate KPIs and analytical summaries.
        logging.info("Step 4/7: Generating analytics")
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        export_analytics(categorized_df, REPORT_DIR)

        # Step 5: Generate descriptive statistics and outlier reports.
        logging.info("Step 5/7: Generating statistical reports")

        stats = calculate_descriptive_statistics(categorized_df)
        stats.to_csv(
            REPORT_DIR / "descriptive_statistics.csv",
            index=False,
        )

        all_outliers = []

        for column in ["Quantity", "Total_Sales"]:
            outliers = detect_iqr_outliers(
                categorized_df,
                column=column,
            )

            outliers = outliers.copy()
            outliers["Outlier_Column"] = column

            # Keep the individual outlier reports.
            outlier_path = REPORT_DIR / f"{column.lower()}_outliers.csv"
            outliers.to_csv(outlier_path, index=False)

            all_outliers.append(outliers)

            logging.info(
                "%s outliers: %s",
                column,
                f"{len(outliers):,}",
            )

        # Combine both types of outliers into one report.
        combined_outliers = pd.concat(
            all_outliers,
            ignore_index=True,
        )
        combined_outliers.to_csv(
            REPORT_DIR / "outlier_analysis.csv",
            index=False,
        )

        logging.info(
            "Saved combined outlier report: %s",
            REPORT_DIR / "outlier_analysis.csv",
        )

        # Step 6: Generate charts and category-month pivot.
        logging.info("Step 6/7: Generating charts")
        generate_charts()

        # Step 7: Generate automated findings.
        logging.info("Step 7/7: Generating automated findings")
        findings = generate_findings()

        if len(findings) < 8:
            raise ValueError(
                f"Expected at least 8 findings, got {len(findings)}."
            )

        print("\nPIPELINE COMPLETED SUCCESSFULLY")
        print(f"Cleaned data: {PROCESSED_DIR / 'cleaned_sales_data.csv'}")
        print(f"Categorized data: {categorized_path}")
        print(f"Reports: {REPORT_DIR}")
        print(f"Charts: {charts_dir}")
        print(f"Automated findings: {len(findings)}")

    except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
        logging.error("Pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
