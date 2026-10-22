from pathlib import Path
import pandas as pd

from src.product_categorization import add_categories

root = Path(__file__).resolve().parent

df = pd.read_csv(
    root / "data" / "processed" / "cleaned_sales_data.csv",
    dtype={"InvoiceNo": str, "StockCode": str},
    low_memory=False
)

categorized = add_categories(df)

print("\nCategory counts:")
print(categorized["Category"].value_counts())

print("\nSample classifications:")
print(
    categorized[
        ["StockCode", "Description", "Category"]
    ].head(20).to_string(index=False)
)

output = root / "data" / "processed" / "categorized_sales_data.csv"
categorized.to_csv(output, index=False)

print(f"\nSaved to: {output}")