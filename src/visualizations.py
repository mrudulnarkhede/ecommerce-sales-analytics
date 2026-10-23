
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "output" / "reports"
CHART_DIR = ROOT / "output" / "charts"
PROCESSED_FILE = ROOT / "data" / "processed" / "categorized_sales_data.csv"


def _require_columns(
    df: pd.DataFrame,
    columns: set[str],
    source: str,
) -> None:
    """Validate that a DataFrame contains required columns."""
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{source} is missing required columns: {sorted(missing)}"
        )


def generate_charts() -> None:
    """Generate six charts and export the category-month revenue pivot."""

    required_files = [
        REPORT_DIR / "monthly_sales_summary.csv",
        REPORT_DIR / "category_sales_summary.csv",
        REPORT_DIR / "product_sales_summary.csv",
        PROCESSED_FILE,
    ]

    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(f"Required input file not found: {path}")

    monthly = pd.read_csv(required_files[0])
    categories = pd.read_csv(required_files[1])
    products = pd.read_csv(required_files[2])

    data = pd.read_csv(
        PROCESSED_FILE,
        usecols=[
            "Year_Month",
            "Category",
            "Quantity",
            "Total_Sales",
        ],
        low_memory=False,
    )

    if data.empty:
        raise ValueError("The processed sales dataset is empty.")

    _require_columns(
        monthly, {"Year_Month", "Revenue"}, "Monthly summary"
    )
    _require_columns(
        categories, {"Category", "Revenue"}, "Category summary"
    )
    _require_columns(
        products, {"StockCode", "Product", "Revenue"}, "Product summary"
    )

    if data[["Year_Month", "Category", "Total_Sales"]].isna().any().any():
        raise ValueError(
            "Year_Month, Category and Total_Sales must not contain missing values."
        )

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Monthly revenue trend
    monthly = monthly.sort_values("Year_Month")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["Year_Month"], monthly["Revenue"], marker="o")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (GBP £)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "monthly_revenue_trend.png", dpi=150)
    plt.close(fig)

    # 2. Top five products by revenue
    top_five = products.nlargest(5, "Revenue").sort_values("Revenue")

    fig, ax = plt.subplots(figsize=(10, 5))
    labels = top_five["Product"].fillna(top_five["StockCode"]).astype(str)
    ax.barh(labels, top_five["Revenue"])
    ax.set_title("Top 5 Products by Revenue")
    ax.set_xlabel("Revenue (GBP £)")
    ax.set_ylabel("Product")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "top_products.png", dpi=150)
    plt.close(fig)

    # 3. Revenue by category
    category_plot = categories.sort_values("Revenue")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(category_plot["Category"], category_plot["Revenue"])
    ax.set_title("Revenue by Product Category")
    ax.set_xlabel("Revenue (GBP £)")
    ax.set_ylabel("Category")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "category_revenue.png", dpi=150)
    plt.close(fig)

    # 4. Transaction-line sales distribution
    sales = pd.to_numeric(data["Total_Sales"], errors="coerce").dropna()
    if sales.empty:
        raise ValueError("No valid sales values are available for the histogram.")

    # Limit the display to the 99th percentile for readability.
    upper_limit = sales.quantile(0.99)
    visible_sales = sales[sales <= upper_limit]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(visible_sales, bins=50)
    ax.set_title("Transaction-Line Sales Distribution (up to 99th percentile)")
    ax.set_xlabel("Sales per transaction line (GBP £)")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "sales_distribution.png", dpi=150)
    plt.close(fig)

    # 5. Revenue concentration: top 20 products and their cumulative
    # contribution to total product revenue.
    ranked = products.sort_values(
        ["Revenue", "StockCode"],
        ascending=[False, True],
    ).copy()

    total_product_revenue = ranked["Revenue"].sum()
    top_twenty = ranked.head(20).copy()

    if total_product_revenue > 0:
        top_twenty["Cumulative_Revenue_Percent"] = (
            top_twenty["Revenue"].cumsum()
            / total_product_revenue
            * 100
        )
    else:
        top_twenty["Cumulative_Revenue_Percent"] = np.nan

    top_twenty.to_csv(
        REPORT_DIR / "top_products_revenue_concentration.csv",
        index=False,
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(top_twenty))

    ax.bar(x, top_twenty["Revenue"], alpha=0.75, label="Product revenue")
    ax.set_xlabel("Products ranked by revenue")
    ax.set_ylabel("Revenue (GBP £)")
    ax.set_title("Revenue Concentration: Top 20 Products")
    ax.set_xticks(x)
    ax.set_xticklabels(
        top_twenty["StockCode"].astype(str),
        rotation=60,
        ha="right",
    )

    ax2 = ax.twinx()
    if total_product_revenue > 0:
        ax2.plot(
            x,
            top_twenty["Cumulative_Revenue_Percent"],
            marker="o",
            label="Cumulative share of total revenue",
        )
        ax2.set_ylabel("Cumulative share of total product revenue (%)")
        ax2.set_ylim(0, 100)

    fig.tight_layout()
    fig.savefig(CHART_DIR / "revenue_concentration.png", dpi=150)
    plt.close(fig)

    # 6. Category-by-month revenue heatmap.
    category_month = data.pivot_table(
        index="Category",
        columns="Year_Month",
        values="Total_Sales",
        aggfunc="sum",
        fill_value=0,
    )

    # Arrange months chronologically.
    category_month = category_month.reindex(
        sorted(category_month.columns),
        axis=1,
    )
    category_month.to_csv(REPORT_DIR / "category_month_pivot.csv")

    fig, ax = plt.subplots(
        figsize=(max(12, len(category_month.columns) * 0.9), 6)
    )
    image = ax.imshow(
        category_month.to_numpy(),
        aspect="auto",
        interpolation="nearest",
    )
    ax.set_title("Monthly Revenue by Product Category")
    ax.set_xlabel("Month")
    ax.set_ylabel("Product Category")
    ax.set_xticks(np.arange(len(category_month.columns)))
    ax.set_xticklabels(category_month.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(category_month.index)))
    ax.set_yticklabels(category_month.index)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Revenue (GBP £)")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "category_month_heatmap.png", dpi=150)
    plt.close(fig)

    print("Six charts generated successfully.")
    print(f"Charts directory: {CHART_DIR}")
    print(f"Category-month pivot: {REPORT_DIR / 'category_month_pivot.csv'}")


if __name__ == "__main__":
    generate_charts()
