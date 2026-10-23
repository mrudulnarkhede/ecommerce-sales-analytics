
import pandas as pd
import pytest

from src.data_cleaning import clean_data
from src.product_categorization import assign_category
from src.statistical_analysis import detect_iqr_outliers
from src.analytics import (
    calculate_order_summary,
    calculate_kpis,
    build_product_summary,
    build_category_summary,
    build_monthly_summary,
)


def sample_sales_data():
    """Create a small, predictable dataset for analytics tests."""
    return pd.DataFrame({
        "InvoiceNo": ["1001", "1001", "1002", "1002"],
        "StockCode": ["A", "B", "A", "C"],
        "Description": ["Item A", "Item B", "Item A", "Item C"],
        "Quantity": [2, 1, 3, 2],
        "UnitPrice": [5.0, 10.0, 5.0, 20.0],
        "Total_Sales": [10.0, 10.0, 15.0, 40.0],
        "InvoiceDate": pd.to_datetime([
            "2011-01-10",
            "2011-01-10",
            "2011-02-15",
            "2011-02-15",
        ]),
        "Year_Month": ["2011-01", "2011-01", "2011-02", "2011-02"],
        "Category": [
            "Home and Decor",
            "Stationery and Paper",
            "Home and Decor",
            "Toys and Games",
        ],
    })


def test_category_assignment():
    assert assign_category("WHITE METAL LANTERN") == "Home and Decor"


def test_cleaning_excludes_invalid_sales():
    df = pd.DataFrame({
        "InvoiceNo": ["1001", "1002", "1003"],
        "StockCode": ["A", "B", "C"],
        "Description": ["Valid item", "Return item", "Free item"],
        "Quantity": [2, -1, 1],
        "InvoiceDate": [
            "2011-01-01 10:00:00",
            "2011-01-01 10:01:00",
            "2011-01-01 10:02:00",
        ],
        "UnitPrice": [5.0, 5.0, 0.0],
        "CustomerID": [123, 123, 123],
        "Country": ["United Kingdom"] * 3,
    })

    cleaned, audit, excluded = clean_data(df)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Total_Sales"] == 10.0
    assert len(excluded) == 2


def test_iqr_outlier_detection_flags_extreme_value():
    df = pd.DataFrame({"Total_Sales": [10, 11, 12, 10, 11, 1000]})

    outliers = detect_iqr_outliers(df, "Total_Sales")

    assert len(outliers) == 1
    assert outliers.iloc[0]["Outlier_Value"] == 1000



def test_order_summary_calculates_order_totals():
    df = sample_sales_data()

    orders = calculate_order_summary(df)

    assert len(orders) == 2
    order_values = orders.set_index("InvoiceNo")["Order_Value"]
    assert order_values.loc["1001"] == pytest.approx(20.0)
    assert order_values.loc["1002"] == pytest.approx(55.0)




def test_kpis_calculate_average_order_value():
    df = sample_sales_data()
    orders = calculate_order_summary(df)

    kpis = calculate_kpis(df, orders)

    assert kpis["total_revenue"] == pytest.approx(75.0)
    assert kpis["unique_order_count"] == 2
    assert kpis["average_order_value"] == pytest.approx(37.5)



def test_product_summary_ranks_products_by_revenue():
    df = sample_sales_data()

    summary = build_product_summary(df)

    assert summary.iloc[0]["StockCode"] == "C"
    assert summary.iloc[0]["Revenue"] == pytest.approx(40.0)


def test_category_summary_contains_revenue_contribution():
    df = sample_sales_data()

    summary = build_category_summary(df)

    assert "Revenue_Contribution_Percent" in summary.columns
    assert summary["Revenue"].sum() == pytest.approx(75.0)
    assert summary["Revenue_Contribution_Percent"].sum() == pytest.approx(100.0)


def test_monthly_summary_groups_revenue_by_month():
    df = sample_sales_data()

    summary = build_monthly_summary(df)
    summary = summary.set_index("Year_Month")

    assert summary.loc["2011-01", "Revenue"] == pytest.approx(20.0)
    assert summary.loc["2011-02", "Revenue"] == pytest.approx(55.0)


def test_cleaning_does_not_modify_raw_input():
    df = pd.DataFrame({
        "InvoiceNo": ["1001"],
        "StockCode": ["A"],
        "Description": ["Valid item"],
        "Quantity": [2],
        "InvoiceDate": ["2011-01-01 10:00:00"],
        "UnitPrice": [5.0],
        "CustomerID": [123],
        "Country": ["United Kingdom"],
    })
    original = df.copy(deep=True)

    clean_data(df)

    pd.testing.assert_frame_equal(df, original)


def test_cleaning_rejects_missing_required_columns():
    df = pd.DataFrame({
        "InvoiceNo": ["1001"],
        "Quantity": [2],
    })

    with pytest.raises((KeyError, ValueError)):
        clean_data(df)
