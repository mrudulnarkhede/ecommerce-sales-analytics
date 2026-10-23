
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "output" / "reports"
CHART_DIR = ROOT / "output" / "charts"


def generate_charts():
    monthly_file = REPORT_DIR / "monthly_sales_summary.csv"
    category_file = REPORT_DIR / "category_sales_summary.csv"
    product_file = REPORT_DIR / "product_sales_summary.csv"
    data_file = ROOT / "data" / "processed" / "categorized_sales_data.csv"

    for path in [monthly_file, category_file, product_file, data_file]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    monthly = pd.read_csv(monthly_file)
    categories = pd.read_csv(category_file)
    products = pd.read_csv(product_file)
    data = pd.read_csv(
        data_file,
        usecols=["Quantity", "Total_Sales"],
        low_memory=False,
    )

    # 1. Monthly revenue trend
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["Year_Month"], monthly["Revenue"], marker="o")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "monthly_revenue_trend.png", dpi=150)
    plt.close()

    # 2. Top 10 products by revenue
    top_products = products.nlargest(10, "Revenue").sort_values("Revenue")
    plt.figure(figsize=(10, 6))
    plt.barh(top_products["Product"].fillna(top_products["StockCode"]),
             top_products["Revenue"])
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue (£)")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "top_10_products_by_revenue.png", dpi=150)
    plt.close()

    # 3. Revenue by category
    category_plot = categories.sort_values("Revenue")
    plt.figure(figsize=(10, 6))
    plt.barh(category_plot["Category"], category_plot["Revenue"])
    plt.title("Revenue by Product Category")
    plt.xlabel("Revenue (£)")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "revenue_by_category.png", dpi=150)
    plt.close()

    # 4. Quantity distribution (limited to readable central range)
    positive_quantity = data.loc[
        data["Quantity"].gt(0), "Quantity"
    ]
    upper_limit = positive_quantity.quantile(0.99)
    plt.figure(figsize=(10, 5))
    plt.hist(
        positive_quantity[positive_quantity <= upper_limit],
        bins=50,
    )
    plt.title("Quantity Distribution (up to 99th percentile)")
    plt.xlabel("Quantity per transaction line")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "quantity_distribution.png", dpi=150)
    plt.close()

    print("Charts generated successfully:")
    for path in sorted(CHART_DIR.glob("*.png")):
        print(path)


if __name__ == "__main__":
    generate_charts()
