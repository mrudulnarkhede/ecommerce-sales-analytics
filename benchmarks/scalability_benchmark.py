
"""Benchmark CSV loading, cleaning, aggregation, and DataFrame memory."""

import argparse
import gc
import logging
import tempfile
import time
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

from src.data_cleaning import clean_data
from src.analytics import (
    calculate_order_summary,
    build_product_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "reports" / "scalability_benchmark.csv"
DEFAULT_SIZES = [1_000, 10_000, 100_000, 500_000]
DEFAULT_REPEATS = 3


def generate_synthetic_data(rows: int, seed: int = 42) -> pd.DataFrame:
    """Generate reproducible retail transaction data."""
    rng = np.random.default_rng(seed)

    start = pd.Timestamp("2011-01-01")
    dates = start + pd.to_timedelta(
        rng.integers(0, 330 * 24 * 60, size=rows), unit="m"
    )

    product_ids = rng.integers(1, 2001, size=rows)
    quantities = rng.integers(1, 15, size=rows)
    prices = np.round(rng.uniform(1.0, 100.0, size=rows), 2)

    return pd.DataFrame({
        "InvoiceNo": [
            f"{value:07d}"
            for value in rng.integers(1000000, 1000000 + max(rows // 2, 1), size=rows)
        ],
        "StockCode": [f"P{value:05d}" for value in product_ids],
        "Description": [f"Product {value}" for value in product_ids],
        "Quantity": quantities,
        "InvoiceDate": dates.strftime("%Y-%m-%d %H:%M:%S"),
        "UnitPrice": prices,
        "CustomerID": rng.integers(10000, 20000, size=rows),
        "Country": rng.choice(
            ["United Kingdom", "France", "Germany", "Spain"],
            size=rows,
        ),
    })


def benchmark_size(rows: int, repeats: int) -> dict:
    """Measure CSV loading, cleaning, aggregation, and memory."""
    load_times = []
    clean_times = []
    aggregate_times = []
    memory_values = []
    input_rows = []
    retained_rows = []

    with tempfile.TemporaryDirectory(prefix="sales_benchmark_") as temp_dir:
        csv_path = Path(temp_dir) / "synthetic_sales.csv"
        generate_synthetic_data(rows).to_csv(csv_path, index=False)

        for _ in range(repeats):
            gc.collect()

            start = time.perf_counter()
            raw_df = pd.read_csv(csv_path)
            load_times.append(time.perf_counter() - start)

            memory_values.append(
                raw_df.memory_usage(index=True, deep=True).sum() / (1024**2)
            )
            input_rows.append(len(raw_df))

            start = time.perf_counter()
            cleaned_df, audit, excluded_df = clean_data(raw_df)
            clean_times.append(time.perf_counter() - start)
            retained_rows.append(len(cleaned_df))

            if cleaned_df.empty:
                raise ValueError(
                    f"Cleaning removed all rows in the {rows:,}-row benchmark."
                )

            start = time.perf_counter()
            orders = calculate_order_summary(cleaned_df)
            products = build_product_summary(
                cleaned_df.assign(Category="Benchmark")
            )
            # Force the aggregation results to be evaluated.
            _ = len(orders), len(products)
            aggregate_times.append(time.perf_counter() - start)

            del raw_df, cleaned_df, audit, excluded_df, orders, products
            gc.collect()

    return {
        "Rows_Requested": rows,
        "Rows_Loaded_Median": int(median(input_rows)),
        "Rows_Retained_Median": int(median(retained_rows)),
        "Repeats": repeats,
        "Load_Seconds_Median": round(median(load_times), 4),
        "Cleaning_Seconds_Median": round(median(clean_times), 4),
        "Aggregation_Seconds_Median": round(median(aggregate_times), 4),
        "Input_DataFrame_Memory_MB_Median": round(median(memory_values), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark the retail analytics pipeline at multiple scales."
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=DEFAULT_SIZES,
        help="Dataset row counts, e.g. --sizes 1000 10000 100000 500000",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help="Number of timed runs per dataset size (default: 3)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the benchmark CSV report.",
    )
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats must be at least 1.")
    if not args.sizes or any(size < 1 for size in args.sizes):
        parser.error("All dataset sizes must be positive integers.")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    results = []

    for size in args.sizes:
        logging.info("Benchmarking %s rows (%s runs)", f"{size:,}", args.repeats)
        result = benchmark_size(size, args.repeats)
        results.append(result)
        logging.info(
            "Load %.4fs | Clean %.4fs | Aggregate %.4fs",
            result["Load_Seconds_Median"],
            result["Cleaning_Seconds_Median"],
            result["Aggregation_Seconds_Median"],
        )

    report = pd.DataFrame(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output, index=False)

    print("\n=== SCALABILITY BENCHMARK COMPLETE ===")
    print(report.to_string(index=False))
    print(f"\nSaved benchmark report: {args.output.resolve()}")


if __name__ == "__main__":
    main()
