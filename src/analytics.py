from pathlib import Path
import json

import numpy as np
import pandas as pd


def calculate_order_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate transaction lines into one row per invoice."""

    required = {"InvoiceNo", "Total_Sales", "Quantity"}

    if not required.issubset(df.columns):
        raise ValueError(
            f"Missing columns: {sorted(required - set(df.columns))}"
        )

    orders = (
        df.groupby("InvoiceNo", as_index=False)
        .agg(
            Order_Value=("Total_Sales", "sum"),
            Total_Units=("Quantity", "sum"),
            Line_Count=("StockCode", "size"),
        )
    )

    return orders


def calculate_kpis(
    df: pd.DataFrame,
    orders: pd.DataFrame,
) -> dict:
    """Calculate overall sales performance metrics."""

    if df.empty or orders.empty:
        raise ValueError("Cannot calculate KPIs from empty data.")

    product_revenue = df.groupby("StockCode")["Total_Sales"].sum()
    product_units = df.groupby("StockCode")["Quantity"].sum()
    category_revenue = df.groupby("Category")["Total_Sales"].sum()

    metrics = {
        "total_revenue": round(float(df["Total_Sales"].sum()), 2),
        "total_units_sold": int(df["Quantity"].sum()),
        "transaction_line_count": int(len(df)),
        "unique_order_count": int(orders["InvoiceNo"].nunique()),
        "average_order_value": round(
            float(orders["Order_Value"].mean()), 2
        ),
        "average_transaction_line_value": round(
            float(df["Total_Sales"].mean()), 2
        ),
        "median_order_value": round(
            float(orders["Order_Value"].median()), 2
        ),
        "highest_revenue_product": str(
            product_revenue.idxmax()
        ),
        "highest_unit_selling_product": str(
            product_units.idxmax()
        ),
        "highest_revenue_category": str(
            category_revenue.idxmax()
        ),
    }

    return metrics


def build_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate product-level sales performance."""

    return (
        df.groupby("StockCode", as_index=False)
        .agg(
            Product=("Description", "first"),
            Category=("Category", "first"),
            Revenue=("Total_Sales", "sum"),
            Units_Sold=("Quantity", "sum"),
            Transaction_Lines=("InvoiceNo", "size"),
        )
        .sort_values("Revenue", ascending=False)
    )


def build_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate category-level sales and revenue contribution."""

    summary = (
        df.groupby("Category", as_index=False)
        .agg(
            Revenue=("Total_Sales", "sum"),
            Units_Sold=("Quantity", "sum"),
            Transaction_Lines=("InvoiceNo", "size"),
            Unique_Orders=("InvoiceNo", "nunique"),
        )
    )

    total_revenue = summary["Revenue"].sum()

    if total_revenue != 0:
        summary["Revenue_Contribution_Percent"] = (
            summary["Revenue"] / total_revenue * 100
        )
    else:
        summary["Revenue_Contribution_Percent"] = np.nan

    return summary.sort_values("Revenue", ascending=False)


def build_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize revenue, units, and orders by calendar month."""

    monthly = (
        df.groupby("Year_Month", as_index=False)
        .agg(
            Revenue=("Total_Sales", "sum"),
            Units_Sold=("Quantity", "sum"),
            Unique_Orders=("InvoiceNo", "nunique"),
        )
        .sort_values("Year_Month")
    )

    monthly["Revenue_Change_Percent"] = (
        monthly["Revenue"].pct_change() * 100
    )

    return monthly


def export_analytics(
    df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Generate analytical tables and export results."""

    output_dir.mkdir(parents=True, exist_ok=True)

    orders = calculate_order_summary(df)

    # The real dataset doesn't contain a Category column.
    # Category mapping must be implemented before category analytics.
    required_category = {"Category"}

    if not required_category.issubset(df.columns):
        raise ValueError(
            "Category column is missing. Implement a documented "
            "product-to-category mapping before category analytics."
        )

    kpis = calculate_kpis(df, orders)

    products = build_product_summary(df)
    categories = build_category_summary(df)
    monthly = build_monthly_summary(df)

    orders.to_csv(output_dir / "order_level_data.csv", index=False)
    products.to_csv(output_dir / "product_sales_summary.csv", index=False)
    categories.to_csv(output_dir / "category_sales_summary.csv", index=False)
    monthly.to_csv(output_dir / "monthly_sales_summary.csv", index=False)

    with open(
        output_dir / "key_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(kpis, file, indent=4)

    print("\n=== BUSINESS ANALYTICS COMPLETE ===")

    for key, value in kpis.items():
        print(f"{key}: {value}")

    return kpis