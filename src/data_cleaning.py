from pathlib import Path
import logging
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = ROOT / "data" / "raw" / "online_retail.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "output" / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def load_raw_data(file_path: Path) -> pd.DataFrame:
    """Load and validate the raw retail dataset."""

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={"InvoiceNo": str, "StockCode": str}
    )

    if df.empty:
        raise ValueError("The input dataset is empty.")

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {sorted(missing_columns)}"
        )

    return df


def clean_data(df: pd.DataFrame):
    """
    Clean transaction records and generate an audit summary.

    Returns:
        cleaned_df: Valid transaction records for sales analysis.
        audit_df: Counts describing cleaning decisions.
        excluded_df: Records excluded from sales analysis.
    """

    initial_rows = len(df)

    # Work on a copy; never modify the original input.
    data = df.copy()

    audit = {
        "initial_rows": initial_rows,
    }

    # 1. Normalize text fields.
    for column in ["InvoiceNo", "StockCode", "Description", "Country"]:
        data[column] = data[column].astype("string").str.strip()

    # Restore genuine missing values after string conversion.
    for column in ["Description", "Country"]:
        data[column] = data[column].replace("", pd.NA)

    # 2. Identify exact duplicate rows.
    duplicate_mask = data.duplicated(keep="first")

    audit["exact_duplicate_rows"] = int(duplicate_mask.sum())

    # Keep the first copy of each exact duplicate.
    data = data.loc[~duplicate_mask].copy()

    # 3. Convert numerical and date columns.
    data["Quantity"] = pd.to_numeric(
        data["Quantity"], errors="coerce"
    )

    data["UnitPrice"] = pd.to_numeric(
        data["UnitPrice"], errors="coerce"
    )

    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"],
        errors="coerce",
        dayfirst=True
    )

    data["CustomerID"] = pd.to_numeric(
        data["CustomerID"], errors="coerce"
    ).astype("Int64")

    # 4. Identify transaction types.
    data["Is_Cancellation"] = (
        data["InvoiceNo"].str.startswith("C", na=False)
    )

    data["Is_Return"] = data["Quantity"].lt(0).fillna(False)

    # 5. Build validation masks.
    invalid_quantity = (
        data["Quantity"].isna()
        | data["Quantity"].le(0)
    )

    invalid_price = (
        data["UnitPrice"].isna()
        | data["UnitPrice"].le(0)
    )

    invalid_date = data["InvoiceDate"].isna()

    invalid_invoice = (
        data["InvoiceNo"].isna()
        | data["InvoiceNo"].eq("")
    )

    invalid_product = (
        data["StockCode"].isna()
        | data["StockCode"].eq("")
    )

    # Negative quantities are flagged as returns, not ordinary sales.
    # Cancellation lines are excluded from completed-sales analysis.
    excluded_mask = (
        invalid_quantity
        | invalid_price
        | invalid_date
        | invalid_invoice
        | invalid_product
        | data["Is_Cancellation"]
    )

    excluded_df = data.loc[excluded_mask].copy()

    audit["invalid_quantity_rows"] = int(invalid_quantity.sum())
    audit["invalid_price_rows"] = int(invalid_price.sum())
    audit["invalid_date_rows"] = int(invalid_date.sum())
    audit["invalid_invoice_rows"] = int(invalid_invoice.sum())
    audit["invalid_product_rows"] = int(invalid_product.sum())
    audit["cancellation_rows"] = int(data["Is_Cancellation"].sum())
    audit["return_rows"] = int(data["Is_Return"].sum())
    audit["excluded_rows"] = int(excluded_mask.sum())

    # 6. Retain valid positive-quantity sales lines.
    cleaned = data.loc[~excluded_mask].copy()

    # 7. Add useful analytical features.
    cleaned["Total_Sales"] = (
        cleaned["Quantity"] * cleaned["UnitPrice"]
    )

    cleaned["Order_Year"] = cleaned["InvoiceDate"].dt.year
    cleaned["Order_Month"] = cleaned["InvoiceDate"].dt.month

    cleaned["Year_Month"] = (
        cleaned["InvoiceDate"].dt.to_period("M").astype(str)
    )

    cleaned["Day_Of_Week"] = (
        cleaned["InvoiceDate"].dt.day_name()
    )

    # Protect against impossible calculated values.
    if not np.isfinite(cleaned["Total_Sales"]).all():
        raise ValueError(
            "Non-finite sales values detected after calculation."
        )

    audit["retained_rows"] = len(cleaned)
    audit["final_rows"] = len(cleaned)

    audit_df = pd.DataFrame(
        list(audit.items()),
        columns=["Cleaning_Check", "Count"]
    )

    return cleaned, audit_df, excluded_df


def run_cleaning_pipeline():
    """Load, clean, and export processed data and audit files."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data(RAW_FILE)

    cleaned_df, audit_df, excluded_df = clean_data(raw_df)

    if cleaned_df.empty:
        raise ValueError(
            "No valid sales records remain after cleaning."
        )

    cleaned_path = PROCESSED_DIR / "cleaned_sales_data.csv"
    audit_path = REPORT_DIR / "cleaning_audit.csv"
    excluded_path = REPORT_DIR / "excluded_records.csv"

    cleaned_df.to_csv(cleaned_path, index=False)
    audit_df.to_csv(audit_path, index=False)
    excluded_df.to_csv(excluded_path, index=False)

    logging.info("Initial rows: %s", len(raw_df))
    logging.info("Retained sales rows: %s", len(cleaned_df))
    logging.info("Excluded rows: %s", len(excluded_df))

    print("\nCleaning completed successfully.")
    print(f"Cleaned dataset: {cleaned_path}")
    print(f"Cleaning audit: {audit_path}")
    print(f"Excluded records: {excluded_path}")

    print("\nCleaning summary:")
    print(audit_df.to_string(index=False))

    return cleaned_df


if __name__ == "__main__":
    run_cleaning_pipeline()