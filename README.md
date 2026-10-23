# E-Commerce Sales Intelligence and Scalable Data Analytics Pipeline

## 1. Project Overview

This project develops a data analytics pipeline for an online retail dataset. It processes transaction records, performs data quality checks, cleans the data, assigns rule-based product categories, calculates business KPIs, conducts statistical analysis, detects outliers, and generates visualizations.

The project uses Python and pandas to transform raw retail transactions into structured reports that support sales and product performance analysis.

## 2. Objectives

- Assess data quality and identify missing, duplicate, and invalid records.
- Clean transaction data while maintaining an audit of excluded records.
- Derive product categories using transparent keyword-based rules.
- Calculate revenue, units sold, order value, and product performance metrics.
- Analyse monthly sales trends and category-level revenue.
- Calculate descriptive statistics and flag potential outliers using the IQR method.
- Generate charts for business reporting.

## 3. Dataset

**Dataset:** UCI Online Retail

**Source:** https://archive.ics.uci.edu/dataset/352/online+retail

The dataset contains online retail transactions, including invoice numbers, stock codes, product descriptions, quantities, invoice dates, unit prices, customer IDs, and countries.

The original dataset contains 541,909 rows and 8 columns.

Download the dataset separately and place `Online Retail.xlsx` in `data/raw/`. The dataset itself is not included in the Git repository.

## 4. Technology Stack

- Python
- pandas
- NumPy
- Matplotlib
- SciPy
- pytest
- openpyxl

## 5. Project Structure

```text
ecommerce-sales-analytics/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── analytics.py
│   ├── data_cleaning.py
│   ├── data_quality.py
│   ├── feature_engineering.py
│   ├── product_categorization.py
│   ├── statistical_analysis.py
│   └── visualizations.py
├── tests/
├── benchmarks/
├── output/
│   ├── charts/
│   └── reports/
├── prepare_dataset.py
├── check_categories.py
├── inspect_categories.py
├── run_analytics.py
├── run_statistical_analysis.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 6. Setup Instructions

### Prerequisites

- Python 3.10 or later recommended
- Git
- The UCI Online Retail Excel dataset

### Install dependencies

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Place `Online Retail.xlsx` in `data/raw/`.

## 7. Run the Pipeline

Run the commands from the project root in the following order.

### Step 1: Prepare the dataset

```powershell
python prepare_dataset.py
```

Creates `data/raw/online_retail.csv`.

### Step 2: Profile data quality

```powershell
python -m src.data_quality
```

Creates data quality profile and validation reports in `output/reports/`.

### Step 3: Clean transaction data

```powershell
python -m src.data_cleaning
```

Creates the cleaned dataset, cleaning audit, and excluded-record report.

### Step 4: Assign product categories

```powershell
python check_categories.py
```

Creates `data/processed/categorized_sales_data.csv`.

### Step 5: Generate business analytics

```powershell
python run_analytics.py
```

Generates order, product, category, and monthly summaries, along with key metrics.

### Step 6: Run statistical analysis

```powershell
python run_statistical_analysis.py
```

Generates descriptive statistics and IQR outlier reports.

### Step 7: Generate charts

```powershell
python -m src.visualizations
```

Creates PNG visualizations in `output/charts/`.

## 8. Main Outputs

### Data quality and cleaning

- `data_quality_profile.csv`
- `data_quality_checks.csv`
- `cleaning_audit.csv`
- `excluded_records.csv`

### Business analytics

- `order_summary.csv`
- `product_sales_summary.csv`
- `category_sales_summary.csv`
- `monthly_sales_summary.csv`
- `key_metrics.json`

### Statistical analysis

- `descriptive_statistics.csv`
- `quantity_outliers.csv`
- `total_sales_outliers.csv`

### Visualizations

- `monthly_revenue_trend.png`
- `top_10_products_by_revenue.png`
- `revenue_by_category.png`
- `quantity_distribution.png`

## 9. Methodology

The pipeline performs exact-duplicate removal, type conversion, date validation, transaction filtering, sales calculation, feature engineering, and rule-based categorization.

Revenue is calculated as quantity multiplied by unit price for retained positive-quantity sales lines. Cancellation lines and non-positive-quantity records are excluded from the cleaned completed-sales dataset and preserved in the excluded-record report.

Descriptive statistics include measures such as mean, median, standard deviation, variance, percentiles, skewness, and kurtosis. Potential outliers are flagged using the 1.5 × IQR rule and are not automatically deleted.

## 10. Limitations

- Product categories are derived from description keywords because the original dataset does not provide a product category field.
- Some products may be labelled `Needs Review` or `Other / Unclassified`.
- Missing customer IDs limit customer-level analysis.
- IQR outliers may represent legitimate bulk purchases and should not automatically be treated as errors.
- The current cleaned dataset is intended for completed positive-quantity sales analysis; it is not a net-sales calculation that reconciles returns and cancellations.
- Reported revenue represents the sum of retained transaction-line sales and is not independently reconciled against refunds, taxes, or accounting records.

## 11. Reproducibility

Keep the original dataset in `data/raw/` and regenerate processed files by running the pipeline commands in order. Raw and processed datasets, generated reports, and charts are excluded from version control through `.gitignore`.

## 12. License and Attribution

The dataset is provided by the UCI Machine Learning Repository. Refer to the dataset page for source details and applicable terms.

This project was developed for academic learning and scalable data analytics practice.
