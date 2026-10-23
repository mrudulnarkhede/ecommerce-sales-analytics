
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw" / "online_retail.csv"
OUTPUT_DIR = ROOT / "output" / "reports"


def profile_dataset(file_path: Path) -> pd.DataFrame:
    """Inspect raw retail data and generate a quality profile."""

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={"InvoiceNo": str, "StockCode": str}
    )

    if df.empty:
        raise ValueError("The dataset contains no records.")

    required_columns = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice",
        "CustomerID", "Country"
    ]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Required columns missing: {sorted(missing_columns)}"
        )

    # Convert temporary Series for validation only.
    quantity = pd.to_numeric(df["Quantity"], errors="coerce")
    price = pd.to_numeric(df["UnitPrice"], errors="coerce")
    dates = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce",
    format="mixed"
)
    checks = {
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "cancelled_invoice_lines": int(
            df["InvoiceNo"].str.startswith("C", na=False).sum()
        ),
        "negative_quantity_rows": int((quantity < 0).sum()),
        "zero_quantity_rows": int((quantity == 0).sum()),
        "invalid_quantity_rows": int(quantity.isna().sum()),
        "negative_price_rows": int((price < 0).sum()),
        "zero_price_rows": int((price == 0).sum()),
        "invalid_price_rows": int(price.isna().sum()),
        "invalid_date_rows": int(dates.isna().sum()),
        "blank_description_rows": int(
                   df["Description"].fillna("").str.strip().eq("").sum()
          ),
        "missing_customer_ids": int(df["CustomerID"].isna().sum()),
        "unique_products": int(df["StockCode"].nunique()),
        "unique_countries": int(df["Country"].nunique()),
    }

    profile = pd.DataFrame({
        "Column": df.columns,
        "Data_Type": df.dtypes.astype(str).values,
        "Missing_Count": df.isna().sum().values,
        "Missing_Percentage": (
            df.isna().mean().values * 100
        ).round(2),
        "Unique_Values": df.nunique(dropna=True).values,
    })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profile.to_csv(
        OUTPUT_DIR / "data_quality_profile.csv", index=False
    )

    pd.DataFrame(
        list(checks.items()),
        columns=["Quality_Check", "Count"]
    ).to_csv(
        OUTPUT_DIR / "data_quality_checks.csv", index=False
    )

    print("\n=== DATASET OVERVIEW ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Date range: {dates.min()} to {dates.max()}")

    print("\n=== DATA QUALITY CHECKS ===")
    for check, count in checks.items():
        print(f"{check}: {count:,}")

    print("\n=== COLUMN PROFILE ===")
    print(profile.to_string(index=False))
    print("\nProfiling complete. Raw data was not modified.")

    return profile


if __name__ == "__main__":
    try:
        profile_dataset(INPUT_FILE)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Profiling failed: {exc}")
