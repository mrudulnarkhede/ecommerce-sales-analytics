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
    processed_dir: Path | None = None,
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

    orders_output_dir = processed_dir or output_dir
    orders_output_dir.mkdir(parents=True, exist_ok=True)
    orders.to_csv(orders_output_dir / "order_level_data.csv", index=False)
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

def filter_sales_data(
    df: pd.DataFrame,
    product: str | None = None,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    min_sales: float | None = None,
    max_sales: float | None = None,
    top_n: int | None = None,
) -> pd.DataFrame:
    """Filter transaction rows using product, category, date, and sales criteria.

    If top_n is supplied, retain rows belonging to the top N products
    ranked by total revenue within the already-filtered data.
    The input DataFrame is not modified.
    """
    if df.empty:
        return df.copy()

    result = df.copy()

    if product is not None:
        product_columns = [
            column
            for column in ("Product", "Description", "StockCode")
            if column in result.columns
        ]
        if not product_columns:
            raise ValueError(
                "Product filtering requires Product, Description, or StockCode."
            )

        product_mask = pd.Series(False, index=result.index)
        for column in product_columns:
            product_mask |= (
                result[column]
                .astype("string")
                .str.contains(product, case=False, na=False, regex=False)
            )
        result = result.loc[product_mask]

    if category is not None:
        if "Category" not in result.columns:
            raise ValueError("Category filtering requires a Category column.")

        result = result.loc[
            result["Category"]
            .astype("string")
            .str.contains(category, case=False, na=False, regex=False)
        ]

    if start_date is not None or end_date is not None:
        if "InvoiceDate" not in result.columns:
            raise ValueError("Date filtering requires an InvoiceDate column.")

        dates = pd.to_datetime(result["InvoiceDate"], errors="coerce")

        if start_date is not None:
            start = pd.to_datetime(start_date, errors="raise")
            result = result.loc[dates >= start]

        if end_date is not None:
            end = pd.to_datetime(end_date, errors="raise")
            result = result.loc[dates <= end]

    if min_sales is not None or max_sales is not None:
        if "Total_Sales" not in result.columns:
            raise ValueError("Sales filtering requires a Total_Sales column.")

        if min_sales is not None and max_sales is not None:
            if min_sales > max_sales:
                raise ValueError("min_sales cannot exceed max_sales.")

        if min_sales is not None:
            result = result.loc[result["Total_Sales"] >= min_sales]

        if max_sales is not None:
            result = result.loc[result["Total_Sales"] <= max_sales]

    if top_n is not None:
        if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
            raise ValueError("top_n must be a positive integer.")

        if "Total_Sales" not in result.columns:
            raise ValueError("Top-N filtering requires a Total_Sales column.")

        product_column = next(
            (
                column
                for column in ("StockCode", "Product", "Description")
                if column in result.columns
            ),
            None,
        )

        if product_column is None:
            raise ValueError(
                "Top-N filtering requires StockCode, Product, or Description."
            )

        top_products = (
            result.groupby(product_column)["Total_Sales"]
            .sum()
            .nlargest(top_n)
            .index
        )
        result = result.loc[result[product_column].isin(top_products)]

    return result.copy()