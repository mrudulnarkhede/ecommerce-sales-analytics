
import pandas as pd

from src.data_cleaning import clean_data
from src.product_categorization import assign_category
from src.statistical_analysis import detect_iqr_outliers


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
