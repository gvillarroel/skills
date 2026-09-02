#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==1.4.4", "pytz==2025.2"]
# ///
"""Cross-check all frozen pricing questions against the Parquet helper."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = Path(__file__).resolve().parent
DATASET_ROOT = REPOSITORY_ROOT / "evaluations" / "datasets" / "google-cloud-sku-pricing-100"
PARQUET_PATH = (
    REPOSITORY_ROOT
    / "projects"
    / "google-cloud-sku-pricing-parquet"
    / "artifacts"
    / "data"
    / "google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.parquet"
)
PARQUET_HELPER_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "google-cloud-sku-pricing"
    / "scripts"
    / "parquet_pricing.py"
)
BENCHMARKS = {
    "v1": DATASET_ROOT / "processed" / "benchmark.sqlite",
    "v2": DATASET_ROOT / "processed" / "v2" / "benchmark.sqlite",
}


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE_TEST = import_path("pricing_base_benchmark", EVALUATION_DIR / "test_benchmark.py")
PARQUET_HELPER = import_path("pricing_parquet_helper", PARQUET_HELPER_PATH)


class ParquetBenchmarkTests(unittest.TestCase):
    def test_all_v1_and_v2_answers_match_exactly(self) -> None:
        self.assertTrue(PARQUET_PATH.is_file(), "Generate the pricing Parquet artifact first")
        original_helper = BASE_TEST.HELPER
        BASE_TEST.HELPER = PARQUET_HELPER
        try:
            for revision, benchmark_path in BENCHMARKS.items():
                with self.subTest(revision=revision):
                    catalog = PARQUET_HELPER.connect(PARQUET_PATH)
                    benchmark = sqlite3.connect(benchmark_path)
                    benchmark.row_factory = sqlite3.Row
                    try:
                        rows = list(
                            benchmark.execute(
                                "SELECT question_id, family, prompt, expected_json "
                                "FROM questions ORDER BY question_id"
                            )
                        )
                        self.assertEqual(len(rows), 100)
                        for row in rows:
                            with self.subTest(
                                revision=revision,
                                question_id=row["question_id"],
                                family=row["family"],
                            ):
                                expected = json.loads(row["expected_json"])
                                actual = BASE_TEST.helper_answer(
                                    catalog, row["family"], row["prompt"]
                                )
                                self.assertEqual(actual, expected)
                    finally:
                        benchmark.close()
                        catalog.close()
        finally:
            BASE_TEST.HELPER = original_helper


if __name__ == "__main__":
    unittest.main()
