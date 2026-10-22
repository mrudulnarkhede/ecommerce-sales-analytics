
import numpy as np
import pandas as pd


def calculate_descriptive_statistics(
    df: pd.DataFrame,
    columns=None,
) -> pd.DataFrame:
    """Calculate descriptive statistics for selected numeric columns."""

    if columns is None:
        columns = [
            "Quantity",
            "UnitPrice",
            "Total_Sales",
        ]

    rows = []

    for column in columns:
        if column not in df.columns:
            continue

        values = pd.to_numeric(
            df[column], errors="coerce"
        ).dropna()

        if values.empty:
            continue

        modes = values.mode().tolist()

        q25, q50, q75 = np.percentile(
            values.to_numpy(), [25, 50, 75]
        )

        rows.append({
            "Variable": column,
            "Count": int(values.count()),
            "Mean": float(values.mean()),
            "Median": float(values.median()),
            "Modes": ", ".join(map(str, modes)),
            "Minimum": float(values.min()),
            "Maximum": float(values.max()),
            "Range": float(values.max() - values.min()),
            "Percentile_25": float(q25),
            "Percentile_50": float(q50),
            "Percentile_75": float(q75),
            "Standard_Deviation": float(values.std()),
            "Variance": float(values.var()),
            "IQR": float(q75 - q25),
            "Skewness": float(values.skew()),
            "Kurtosis": float(values.kurt()),
        })

    return pd.DataFrame(rows)


def detect_iqr_outliers(
    df: pd.DataFrame,
    column: str = "Total_Sales",
) -> pd.DataFrame:
    """Flag outliers using the 1.5 × IQR rule; do not delete them."""

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    values = pd.to_numeric(df[column], errors="coerce")
    valid = values.dropna()

    if valid.empty:
        return df.iloc[0:0].copy()

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    mask = values.lt(lower) | values.gt(upper)

    outliers = df.loc[mask].copy()
    outliers["Outlier_Value"] = values.loc[mask]
    outliers["IQR_Lower_Bound"] = lower
    outliers["IQR_Upper_Bound"] = upper

    return outliers
