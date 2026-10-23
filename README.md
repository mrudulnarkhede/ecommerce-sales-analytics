# E-Commerce Sales Data Analysis and Visualization

## 1. Project Overview

This project analyzes an online retail transaction dataset using Python. It includes data quality assessment, data cleaning, product categorization, business analytics, descriptive statistics, outlier detection, monthly sales analysis, and data visualization.

The pipeline transforms raw retail transactions into cleaned datasets, summary reports, charts, and automated findings. The objective is to understand product performance, revenue patterns, and data quality while documenting the limitations of the analysis.

## 2. Objectives

- Assess the quality of the raw retail transaction data.
- Identify and handle missing values, duplicates, invalid records, cancellations, and returns.
- Calculate total revenue, total units sold, average order value, and other business metrics.
- Identify the highest-revenue product and highest-selling product by quantity.
- Estimate category-wise revenue using rule-based product categorization.
- Analyze monthly revenue trends.
- Calculate descriptive statistics and identify potential outliers.
- Generate visualizations and save the analytical results to files.

## 3. Analysis Questions

This project addresses the following questions:

1. What is the total revenue and total quantity sold?
2. Which product generates the highest revenue?
3. Which product has the highest total quantity sold?
4. Which estimated product category contributes the most revenue?
5. How does revenue change from month to month?
6. What do descriptive statistics and outlier analysis reveal about the transaction data?

## 4. Dataset

**Dataset:** UCI Online Retail

**Source:** [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)

The dataset contains transactions from a UK-based online retailer. The original dataset contains 541,909 rows and 8 columns.

### Dataset columns

| Column | Description |
|---|---|
| InvoiceNo | Invoice or transaction identifier |
| StockCode | Product identifier |
| Description | Product description |
| Quantity | Number of units in the transaction line |
| InvoiceDate | Date and time of the transaction |
| UnitPrice | Price per unit |
| CustomerID | Customer identifier, where available |
| Country | Customer's country |

The original dataset is supplied as an Excel file named `Online Retail.xlsx`. Place it in `data/raw/` before running the pipeline. The source dataset is not included in this Git repository.

### Currency and units

Revenue and unit-price values are reported in British pounds sterling (GBP, £), based on the dataset's unit-price values.

Revenue is calculated as quantity multiplied by unit price for retained positive-quantity sales lines. It is not profit and does not represent net revenue after fully reconciling returns, cancellations, refunds, taxes, or accounting adjustments.

## 5. Technology Stack

- **Python** — pipeline and analytical logic
- **pandas** — CSV processing, data cleaning, grouping, and summaries
- **NumPy** — numerical calculations and percentiles
- **Matplotlib** — charts and visualizations
- **SciPy** — scientific and statistical support where used
- **pytest** — automated tests
- **openpyxl** — reading the source Excel dataset

## 6. Project Structure

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
│   ├── insight_generator.py
│   ├── product_categorization.py
│   ├── statistical_analysis.py
│   └── visualizations.py
├── tests/
├── benchmarks/
├── output/
│   ├── charts/
│   └── reports/
├── prepare_dataset.py
├── run_pipeline.py
├── run_analytics.py
├── run_statistical_analysis.py
├── requirements.txt
├── .gitignore
└── README.md
```

The project may contain additional helper scripts and generated files. The exact files present in the repository are authoritative.

## 7. Setup Instructions

### Prerequisites

- Python 3.10 or later
- Git
- The UCI Online Retail Excel dataset

### Step 1: Clone the repository

```powershell
git clone https://github.com/mrudulnarkhede/ecommerce-sales-analytics.git
cd ecommerce-sales-analytics
```

### Step 2: Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, follow your system's approved Python environment activation instructions.

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Place the dataset

Download `Online Retail.xlsx` from the UCI dataset page and place it in:

```text
data/raw/Online Retail.xlsx
```

Prepare the CSV dataset using the project's dataset preparation script if required by the pipeline.

## 8. Running the Project

Run the commands from the project root with the virtual environment activated.

### Recommended: Run the complete pipeline

```powershell
python run_pipeline.py
```

The main pipeline performs the data quality checks, cleaning, product categorization, business analytics, statistical analysis, chart generation, and automated findings generation.

### Run the automated tests

```powershell
python -m pytest -q
```

The tests help verify that key project functions behave as expected.

### Individual scripts

The repository also contains scripts for preparing the dataset, running analytics, and running statistical analysis. The complete `run_pipeline.py` workflow is the recommended entry point for generating the integrated outputs.

## 9. Data Cleaning and Preparation

The pipeline checks the raw dataset for data quality issues before generating analytical outputs.

The checks include:

- Exact duplicate records
- Cancelled invoice lines
- Negative and non-positive quantities
- Negative and zero unit prices
- Invalid dates and transaction identifiers
- Missing product descriptions
- Missing customer identifiers

The cleaning stage applies the project's validation and filtering rules. It generates a cleaning audit and an excluded-record report so that removed records can be inspected.

The raw dataset is profiled without modifying the original source file.

Negative quantities can represent returns, and cancellation records can represent cancelled transactions. These records are handled according to the cleaning rules rather than being treated automatically as ordinary completed sales.

## 10. Data Structures and Processing

The project uses Python data structures and data-processing tools, including:

- Lists for collecting and processing results
- Dictionaries for storing metrics and validation results
- pandas DataFrames for tabular data, filtering, and grouping
- NumPy arrays and numerical operations for statistical calculations

These structures support reusable processing functions, conditional filtering, summary calculations, and report generation.

## 11. Business and Statistical Analysis

### Business analytics

The pipeline calculates metrics and summaries such as:

- Total revenue
- Total units sold
- Number of retained transaction lines
- Number of unique orders
- Average order value
- Average transaction-line value
- Median order value
- Product-level revenue and quantity summaries
- Category-level revenue summaries
- Monthly revenue summaries

### Descriptive statistics

The statistical report includes:

- Count
- Mean
- Median
- Mode
- Minimum and maximum
- Range
- 25th, 50th, and 75th percentiles
- Standard deviation
- Variance
- Interquartile range (IQR)
- Skewness and kurtosis

Statistics are calculated for applicable numerical columns, including quantity, unit price, and transaction-line sales values.

### Outlier analysis

Potential outliers are identified using the 1.5 × IQR rule. The project generates reports for quantity and transaction-line sales values.

Outliers are flagged for inspection; they are not automatically removed simply because they fall outside the IQR thresholds.

### Date and monthly analysis

The pipeline processes transaction dates and generates monthly revenue summaries. These summaries support month-to-month trend analysis and visualization.

## 12. Visualizations

The pipeline generates six charts in the latest successful run. The chart directory may also contain earlier chart versions from previous runs.

The main visualizations include:

1. Monthly sales trend
2. Top products by revenue
3. Revenue by product category
4. Category-month revenue heatmap
5. Revenue concentration
6. Sales or quantity distribution

Chart filenames currently generated by the pipeline include:

- `monthly_sales_trend.png`
- `top_products.png`
- `top_10_products_by_revenue.png`
- `revenue_by_category.png`
- `category_revenue.png`
- `category_month_heatmap.png`
- `revenue_concentration.png`
- `sales_distribution.png`
- `quantity_distribution.png`

Some charts may communicate related information using different views. The current contents of `output/charts/` show which image files are available.

## 13. Main Output Files

### Processed datasets

Files are saved under `data/processed/`, including:

- `cleaned_sales_data.csv`
- `categorized_sales_data.csv`
- `order_level_data.csv`

### Reports

Files are saved under `output/reports/`, including:

- `data_quality_profile.csv`
- `data_quality_checks.csv`
- `cleaning_audit.csv`
- `excluded_records.csv`
- `key_metrics.json`
- `order_summary.csv`
- `product_sales_summary.csv`
- `category_sales_summary.csv`
- `monthly_sales_summary.csv`
- `category_month_pivot.csv`
- `descriptive_statistics.csv`
- `quantity_outliers.csv`
- `total_sales_outliers.csv`
- `outlier_analysis.csv`
- `findings.txt`
- `scalability_benchmark.csv`

The reports produced by a particular run depend on the pipeline's configured output functions.

### Charts

PNG visualizations are saved in:

```text
output/charts/
```

## 14. Key Findings

The automated findings report is saved to `output/reports/findings.txt`.

In the latest successful run, the report generated 11 findings. These include:

- The product with the highest recorded revenue
- The product with the highest total quantity sold
- The estimated category with the highest revenue contribution
- The month with the highest revenue
- The largest month-to-month revenue increase and decrease
- The revenue contribution of the top five products
- The number and proportion of excluded records
- Quantity and sales values flagged as IQR outliers
- The relationship between mean and median product-level revenue

The findings should be interpreted in the context of the cleaning rules, dataset limitations, and calculated metrics. Refer to the generated report for the latest numerical results.

## 15. Limitations

- The source dataset does not include a product category column. Product categories are estimated using keyword-based rules applied to product descriptions.
- Some products may be assigned to `Needs Review` or `Other / Unclassified`.
- Customer IDs are missing for some records, which limits customer-level analysis.
- Negative quantities may represent returns, and cancellation records may represent cancelled transactions.
- The cleaned sales dataset focuses on retained positive-quantity sales lines. It does not fully reconcile returns, cancellations, refunds, taxes, or accounting adjustments.
- Revenue is not profit.
- IQR outliers may be legitimate transactions, such as bulk purchases, and should be reviewed before any removal.
- Findings describe patterns in the dataset and do not establish causal relationships.

## 16. Reproducibility and Version Control

Keep the original dataset in `data/raw/`. Run the complete pipeline from the project root to regenerate processed data, reports, charts, and findings.

Generated files and datasets may be excluded from Git version control through `.gitignore`. Download or prepare the source dataset separately before running the project in a new environment.

## 17. Testing

Run:

```powershell
python -m pytest -q
```

During the latest reported validation, all 15 tests passed. Run the tests again after making code changes to confirm the current result.

## 18. License and Attribution

The dataset is provided through the UCI Machine Learning Repository. Refer to the [UCI Online Retail dataset page](https://archive.ics.uci.edu/dataset/352/online+retail) for source details and applicable terms.

This project was developed for academic learning and scalable data analytics practice.