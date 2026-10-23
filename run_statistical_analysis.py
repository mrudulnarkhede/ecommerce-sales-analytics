
from pathlib import Path
import pandas as pd

from src.statistical_analysis import (
    calculate_descriptive_statistics,
    detect_iqr_outliers,
)

ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "processed" / "categorized_sales_data.csv"
OUTPUT_DIR = ROOT / "output" / "reports"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={"InvoiceNo": str, "StockCode": str},
        low_memory=False,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = calculate_descriptive_statistics(df)
    stats.to_csv(OUTPUT_DIR / "descriptive_statistics.csv", index=False)

    for column in ["Quantity", "Total_Sales"]:
        outliers = detect_iqr_outliers(df, column=column)
        outliers.to_csv(
            OUTPUT_DIR / f"{column.lower()}_outliers.csv",
            index=False,
        )
        print(f"{column} outlier rows: {len(outliers):,}")

    print("\n=== DESCRIPTIVE STATISTICS ===")
    print(stats.to_string(index=False))
    print(f"\nReports saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
