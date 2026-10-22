import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from validated transaction data.
    Does not modify the input DataFrame.
    """

    required = {
        "InvoiceNo",
        "StockCode",
        "Quantity",
        "UnitPrice",
        "InvoiceDate",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    result = df.copy()

    result["InvoiceDate"] = pd.to_datetime(
        result["InvoiceDate"], errors="raise"
    )

    result["Quantity"] = pd.to_numeric(
        result["Quantity"], errors="raise"
    )

    result["UnitPrice"] = pd.to_numeric(
        result["UnitPrice"], errors="raise"
    )

    if (result["Quantity"] <= 0).any():
        raise ValueError("Quantity must be positive for sales analysis.")

    if (result["UnitPrice"] <= 0).any():
        raise ValueError("UnitPrice must be positive for sales analysis.")

    result["Total_Sales"] = (
        result["Quantity"] * result["UnitPrice"]
    )

    result["Order_Year"] = result["InvoiceDate"].dt.year
    result["Order_Month"] = result["InvoiceDate"].dt.month

    result["Year_Month"] = (
        result["InvoiceDate"].dt.to_period("M").astype(str)
    )

    result["Day_Of_Week"] = (
        result["InvoiceDate"].dt.day_name()
    )

    return result