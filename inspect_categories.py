
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent
file_path = root / "data" / "processed" / "categorized_sales_data.csv"

df = pd.read_csv(
    file_path,
    dtype={"InvoiceNo": str, "StockCode": str},
    low_memory=False
)

for category in ["Needs Review", "Other / Unclassified"]:
    print(f"\n=== {category} ===")

    products = (
        df.loc[df["Category"] == category, "Description"]
        .value_counts()
        .head(25)
    )

    print(products.to_string())

review = (
    df.groupby(["StockCode", "Description", "Category"], dropna=False)
    .size()
    .reset_index(name="Transaction_Lines")
)

review.to_csv(
    root / "output" / "reports" / "category_review.csv",
    index=False
)

print("\nSaved full category review.")
