
from pathlib import Path
import pandas as pd

from src.analytics import export_analytics

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

    required = {
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "Total_Sales",
  
        "Year_Month",
        "Category",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Categorized dataset is empty.")

    print(f"Loaded {len(df):,} categorized transaction rows.")

    export_analytics(df, OUTPUT_DIR)

    print(f"\nAnalytics reports saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
