#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Cross-check every canonical benchmark answer through the bundled helper."""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import re
import sqlite3
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPOSITORY_ROOT / "skills" / "google-cloud-sku-pricing" / "scripts" / "sku_pricing.py"
DATASET_ROOT = REPOSITORY_ROOT / "evaluations" / "datasets" / "google-cloud-sku-pricing-100"
BENCHMARK_REVISIONS = {
    "v1": (
        DATASET_ROOT / "processed" / "catalog.sqlite",
        DATASET_ROOT / "processed" / "benchmark.sqlite",
    ),
    "v2": (
        DATASET_ROOT / "processed" / "v2" / "catalog.sqlite",
        DATASET_ROOT / "processed" / "v2" / "benchmark.sqlite",
    ),
}

SPEC = importlib.util.spec_from_file_location("sku_pricing_helper", HELPER_PATH)
assert SPEC and SPEC.loader
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def captures(pattern: str, prompt: str) -> tuple[str, ...]:
    match = re.fullmatch(pattern, prompt)
    if match is None:
        raise AssertionError(f"Prompt does not match its frozen family grammar: {prompt}")
    return match.groups()


def helper_answer(connection: sqlite3.Connection, family: str, prompt: str) -> dict[str, object]:
    if family == "geography":
        (sku_id,) = captures(r"For SKU `([^`]+)`, return exactly .*", prompt)
        payload = HELPER.describe(connection, sku_id)
        return {"geo_type": payload["geo_type"], "regions": payload["regions"]}
    if family == "sku_identity":
        (sku_id,) = captures(r"For SKU `([^`]+)`, return exactly its .*", prompt)
        payload = HELPER.describe(connection, sku_id)
        return {
            "sku_description": payload["sku_description"],
            "service_name": payload["service_name"],
        }
    if family == "model_inventory":
        (sku_id,) = captures(r"For SKU `([^`]+)`, return exactly `model_count`.*", prompt)
        payload = HELPER.describe(connection, sku_id)
        models = [
            {
                "consumption_model_id": row["consumption_model_id"],
                "consumption_model_description": row["consumption_model_description"],
            }
            for row in payload["models"]
        ]
        return {"model_count": len(models), "models": models}
    if family == "list_rate":
        sku_id, usage = captures(
            r"For SKU `([^`]+)` using consumption model `Default` at usage `([^`]+)`, return exactly .*",
            prompt,
        )
        payload = HELPER.rate(connection, sku_id, "Default", Decimal(usage))
        return {
            "currency": payload["currency"],
            "unit": payload["unit"],
            "pricing_unit_quantity": payload["pricing_unit_quantity"],
            "tier_start": payload["tier_start"],
            "price_per_pricing_unit": payload["price_per_pricing_unit"],
        }
    if family == "normalized_rate":
        sku_id, usage = captures(
            r"For SKU `([^`]+)`, model `Default`, and usage `([^`]+)`, normalize .*",
            prompt,
        )
        payload = HELPER.rate(connection, sku_id, "Default", Decimal(usage))
        return {
            "currency": payload["currency"],
            "unit": payload["unit"],
            "tier_start": payload["tier_start"],
            "price_per_base_unit": payload["price_per_base_unit"],
        }
    if family == "marginal_tier":
        sku_id, usage = captures(
            r"For SKU `([^`]+)` using model `Default` at exact usage `([^`]+)`, return .*",
            prompt,
        )
        payload = HELPER.rate(connection, sku_id, "Default", Decimal(usage))
        return {
            "tier_start": payload["tier_start"],
            "price_per_pricing_unit": payload["price_per_pricing_unit"],
            "currency": payload["currency"],
        }
    if family == "progressive_cost":
        sku_id, usage = captures(
            r"For SKU `([^`]+)` with model `Default`, calculate progressive tiered list cost for usage `([^`]+)`. .*",
            prompt,
        )
        payload = HELPER.progressive_cost(connection, sku_id, "Default", Decimal(usage))
        return {"currency": payload["currency"], "total_cost": payload["total_cost"]}
    if family == "region_membership":
        sku_id, region = captures(
            r"Does SKU `([^`]+)` explicitly include region `([^`]+)` in its geographic metadata\? .*",
            prompt,
        )
        payload = HELPER.describe(connection, sku_id)
        return {"region": region, "present": region in payload["regions"]}
    if family == "filtered_count":
        service_id, region, category = captures(
            r"Count distinct SKUs whose service ID is `([^`]+)`, geographic region is `([^`]+)`, "
            r"and taxonomy contains exact category `([^`]+)`. .*",
            prompt,
        )
        payload = HELPER.count_skus(connection, service_id, region, category)
        return {"count": payload["count"]}
    if family == "compatible_comparison":
        sku_block, usage = captures(
            r"Compare the compatible SKUs (.+) using model `Default` at usage `([^`]+)`. .*",
            prompt,
        )
        sku_ids = re.findall(r"`([^`]+)`", sku_block)
        payload = HELPER.compare(connection, sku_ids, "Default", Decimal(usage))
        return {
            "cheapest_sku_id": payload["cheapest_sku_id"],
            "difference_per_base_unit": payload["difference_per_base_unit"],
            "ranked_sku_ids": [row["sku_id"] for row in payload["ranked"]],
            "currency": payload["currency"],
            "unit": payload["unit"],
        }
    raise AssertionError(f"Unknown family: {family}")


class FrozenBenchmarkTests(unittest.TestCase):
    def assert_revision_is_reproducible(
        self, revision: str, catalog_path: Path, benchmark_path: Path
    ) -> None:
        self.assertTrue(catalog_path.is_file(), f"Generate the {revision} frozen catalog first")
        self.assertTrue(
            benchmark_path.is_file(), f"Generate the {revision} frozen benchmark first"
        )
        catalog = HELPER.connect(catalog_path)
        benchmark = sqlite3.connect(benchmark_path)
        benchmark.row_factory = sqlite3.Row
        try:
            rows = list(
                benchmark.execute(
                    "SELECT question_id, family, prompt, expected_json FROM questions ORDER BY question_id"
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
                    actual = helper_answer(catalog, row["family"], row["prompt"])
                    self.assertEqual(actual, expected)
        finally:
            benchmark.close()
            catalog.close()

    def test_all_answers_are_reproducible_by_the_runtime_helper(self) -> None:
        for revision, (catalog_path, benchmark_path) in BENCHMARK_REVISIONS.items():
            with self.subTest(revision=revision):
                self.assert_revision_is_reproducible(revision, catalog_path, benchmark_path)


if __name__ == "__main__":
    unittest.main()
