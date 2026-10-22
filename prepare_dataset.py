
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent
input_file = project_root / "data" / "raw" / "Online Retail.xlsx"
output_file = project_root / "data" / "raw" / "online_retail.csv"

try:
    if not input_file.exists():
        raise FileNotFoundError(
            f"Dataset not found: {input_file}"
        )

    df = pd.read_excel(
        input_file,
        dtype={"InvoiceNo": str, "StockCode": str}
    )

    df.columns = df.columns.str.strip()

    required = {
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice",
        "CustomerID", "Country"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    output_file.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(output_file, index=False)

    print("Dataset prepared successfully!")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Saved to: {output_file}")
    print("\nFirst five records:")
    print(df.head())

except (FileNotFoundError, ValueError, OSError) as exc:
    print(f"Dataset preparation failed: {exc}")
except Exception as exc:
    print(f"Unexpected error: {exc}")
    raise
