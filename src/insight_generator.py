
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "output" / "reports"


def _read_report(filename: str, required_columns: set[str]) -> pd.DataFrame:
    """Read a report and validate its required columns."""
    path = REPORT_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Required report not found: {path}")

    df = pd.read_csv(
        path,
        low_memory=False,
        dtype={"InvoiceNo": str},
    )

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{filename} is missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError(f"Required report is empty: {path}")

    return df


def generate_findings() -> list[str]:
    """Generate factual findings from the current analytics reports."""

    categories = _read_report(
        "category_sales_summary.csv",
        {"Category", "Revenue", "Revenue_Contribution_Percent"},
    )
    products = _read_report(
        "product_sales_summary.csv",
        {"StockCode", "Product", "Revenue", "Units_Sold"},
    )
    monthly = _read_report(
        "monthly_sales_summary.csv",
        {"Year_Month", "Revenue", "Revenue_Change_Percent"},
    )
    audit = _read_report(
        "cleaning_audit.csv",
        {"Cleaning_Check", "Count"},
    )
    quantity_outliers = _read_report(
        "quantity_outliers.csv",
        {"Outlier_Value"},
    )
    sales_outliers = _read_report(
        "total_sales_outliers.csv",
        {"Outlier_Value"},
    )

    # Safely convert numeric report fields.
    for df, columns in [
        (categories, ["Revenue", "Revenue_Contribution_Percent"]),
        (products, ["Revenue", "Units_Sold"]),
        (monthly, ["Revenue", "Revenue_Change_Percent"]),
    ]:
        for column in columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if categories["Revenue"].isna().any():
        raise ValueError("Category report contains invalid revenue values.")

    if categories["Revenue_Contribution_Percent"].isna().any():
        raise ValueError("Category report contains invalid contribution values.")

    if products[["Revenue", "Units_Sold"]].isna().any().any():
        raise ValueError("Product report contains invalid numeric values.")

    if monthly["Revenue"].isna().any():
        raise ValueError("Monthly report contains invalid revenue values.")

    # Validate the cleaning audit.
    audit_counts = dict(
        zip(
            audit["Cleaning_Check"],
            pd.to_numeric(audit["Count"], errors="raise"),
        )
    )

    required_audit_keys = {
        "initial_rows",
        "excluded_rows",
        "retained_rows",
    }
    missing_audit_keys = required_audit_keys - set(audit_counts)

    if missing_audit_keys:
        raise ValueError(
            f"Cleaning audit is missing checks: {sorted(missing_audit_keys)}"
        )

    initial_rows = int(audit_counts["initial_rows"])
    excluded_rows = int(audit_counts["excluded_rows"])
    retained_rows = int(audit_counts["retained_rows"])
    duplicate_rows = int(audit_counts.get("exact_duplicate_rows", 0))

    if initial_rows <= 0:
        raise ValueError("Initial row count must be positive.")

    if min(excluded_rows, retained_rows, duplicate_rows) < 0:
        raise ValueError("Cleaning audit contains negative row counts.")

    if excluded_rows + retained_rows + duplicate_rows != initial_rows:
        raise ValueError(
            "Cleaning audit does not reconcile: excluded + retained + "
            "exact duplicates must equal initial rows."
        )

    findings = []

    # 1. Highest-revenue product.
    top_revenue_product = products.sort_values(
        ["Revenue", "StockCode"], ascending=[False, True]
    ).iloc[0]

    product_name = (
        str(top_revenue_product["Product"])
        if pd.notna(top_revenue_product["Product"])
        else str(top_revenue_product["StockCode"])
    )

    findings.append(
        f"1. Highest-revenue product: {product_name} "
        f"(StockCode {top_revenue_product['StockCode']}), "
        f"with GBP {top_revenue_product['Revenue']:,.2f} in revenue."
    )

    # 2. Highest-unit product.
    top_units_product = products.sort_values(
        ["Units_Sold", "StockCode"], ascending=[False, True]
    ).iloc[0]

    units_name = (
        str(top_units_product["Product"])
        if pd.notna(top_units_product["Product"])
        else str(top_units_product["StockCode"])
    )

    findings.append(
        f"2. Highest-unit product: {units_name} "
        f"(StockCode {top_units_product['StockCode']}), "
        f"with {top_units_product['Units_Sold']:,.0f} units sold."
    )

    # 3. Highest-revenue category.
    top_category = categories.sort_values(
        ["Revenue", "Category"], ascending=[False, True]
    ).iloc[0]

    findings.append(
        f"3. Highest-revenue category: {top_category['Category']}, "
        f"contributing "
        f"{top_category['Revenue_Contribution_Percent']:.2f}% "
        f"of recorded revenue (GBP {top_category['Revenue']:,.2f}). "
        "Categories are keyword-derived estimates, not source-provided labels."
    )

    # 4. Highest-revenue month.
    top_month = monthly.sort_values(
        ["Revenue", "Year_Month"], ascending=[False, True]
    ).iloc[0]

    findings.append(
        f"4. Highest-revenue month: {top_month['Year_Month']}, "
        f"with GBP {top_month['Revenue']:,.2f}."
    )

    # 5 and 6. Largest month-over-month increase and decrease.
    changes = monthly.dropna(subset=["Revenue_Change_Percent"])

    if not changes.empty:
        largest_increase = changes.loc[
            changes["Revenue_Change_Percent"].idxmax()
        ]
        findings.append(
            f"5. Largest month-over-month revenue increase: "
            f"{largest_increase['Year_Month']} at "
            f"{largest_increase['Revenue_Change_Percent']:.2f}%."
        )

        largest_decrease = changes.loc[
            changes["Revenue_Change_Percent"].idxmin()
        ]
        findings.append(
            f"6. Largest month-over-month revenue decrease: "
            f"{largest_decrease['Year_Month']} at "
            f"{largest_decrease['Revenue_Change_Percent']:.2f}%."
        )
    else:
        findings.append(
            "5. Month-over-month revenue increase could not be determined "
            "because comparable monthly changes are unavailable."
        )
        findings.append(
            "6. Month-over-month revenue decrease could not be determined "
            "because comparable monthly changes are unavailable."
        )

    # 7. Revenue contribution of the top five products.
    total_product_revenue = products["Revenue"].sum()
    top_five_revenue = products.nlargest(5, "Revenue")["Revenue"].sum()

    if total_product_revenue > 0:
        top_five_share = top_five_revenue / total_product_revenue * 100
        findings.append(
            f"7. The top five products account for {top_five_share:.2f}% "
            "of the product-summary revenue."
        )
    else:
        findings.append(
            "7. Top-five revenue concentration is unavailable because "
            "total product revenue is not positive."
        )

    # 8. Cleaning exclusion rate.
    exclusion_rate = excluded_rows / initial_rows * 100

    findings.append(
        f"8. Cleaning excluded {excluded_rows:,} of {initial_rows:,} "
        f"input rows ({exclusion_rate:.2f}%); "
        f"{retained_rows:,} rows were retained."
    )

    # 9. Quantity outliers.
    findings.append(
        f"9. The quantity IQR report flags {len(quantity_outliers):,} "
        "transaction lines as outliers. These are flagged, "
        "not automatically deleted."
    )

    # 10. Transaction-line sales outliers.
    findings.append(
        f"10. The transaction-line sales IQR report flags "
        f"{len(sales_outliers):,} lines as outliers. "
        "Outlier status alone does not mean a record is erroneous."
    )

    # 11. Product-level revenue distribution comparison.
    if len(products) >= 2 and total_product_revenue > 0:
        median_product_revenue = products["Revenue"].median()
        mean_product_revenue = products["Revenue"].mean()

        distribution_note = (
            "right-skewed in its summary"
            if mean_product_revenue > median_product_revenue
            else "not shown to be right-skewed by the mean-versus-median comparison"
        )

        findings.append(
            f"11. Product-level revenue is {distribution_note}: "
            f"mean GBP {mean_product_revenue:,.2f}, "
            f"median GBP {median_product_revenue:,.2f}. "
            "This comparison is descriptive, not a formal distribution test."
        )

    # Export findings as UTF-8 text.
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "findings.txt"

    report_text = (
        "E-COMMERCE SALES ANALYTICS — AUTOMATED FINDINGS\n"
        "Currency: GBP (£)\n"
        "Revenue represents the included cleaned positive-quantity sales "
        "lines; it is not profit or net revenue after returns.\n\n"
        + "\n".join(findings)
        + "\n"
    )

    output_path.write_text(report_text, encoding="utf-8")

    print(f"Generated {len(findings)} findings: {output_path}")
    for finding in findings:
        print(finding)

    return findings


if __name__ == "__main__":
    generate_findings()
