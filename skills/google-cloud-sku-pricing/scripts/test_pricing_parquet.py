#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==1.4.4", "pyarrow==25.0.1", "pytz==2025.2"]
# ///
"""Regression tests for the pricing Parquet exporter and query helper."""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import pyarrow.parquet as pq


SCRIPT_DIR = Path(__file__).resolve().parent


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXPORTER = import_path("pricing_parquet_exporter", SCRIPT_DIR / "export_pricing_parquet.py")
QUERY = import_path("pricing_parquet_query", SCRIPT_DIR / "parquet_pricing.py")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class PricingParquetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.raw = self.root / "raw"
        self.raw.mkdir()
        services = [
            {
                "name": "services/SERVICE-1",
                "serviceId": "SERVICE-1",
                "displayName": "Test Compute",
            }
        ]
        skus = [
            {
                "name": "skus/SKU-A",
                "skuId": "SKU-A",
                "displayName": "Regional core A",
                "service": "services/SERVICE-1",
                "geoTaxonomy": {
                    "type": "TYPE_REGIONAL",
                    "regionalMetadata": {"region": {"region": "us-central1"}},
                },
                "productTaxonomy": {
                    "taxonomyCategories": [
                        {"category": "GCP"},
                        {"category": "Test Cores"},
                    ]
                },
            },
            {
                "name": "skus/SKU-B",
                "skuId": "SKU-B",
                "displayName": "Regional core B",
                "service": "services/SERVICE-1",
                "geoTaxonomy": {
                    "type": "TYPE_REGIONAL",
                    "regionalMetadata": {"region": {"region": "us-east1"}},
                },
                "productTaxonomy": {
                    "taxonomyCategories": [
                        {"category": "GCP"},
                        {"category": "Test Cores"},
                    ]
                },
            },
        ]

        def price(sku_id: str, first_nanos: int, second_nanos: int) -> dict[str, object]:
            return {
                "name": f"skus/{sku_id}/price",
                "currencyCode": "USD",
                "skuPrices": [
                    {
                        "consumptionModel": "consumptionModels/DEFAULT-1",
                        "consumptionModelDescription": "Default",
                        "valueType": "rate",
                        "rate": {
                            "aggregationInfo": {
                                "level": "LEVEL_ACCOUNT",
                                "interval": "INTERVAL_MONTHLY",
                            },
                            "unitInfo": {
                                "unit": "h",
                                "unitDescription": "hour",
                                "unitQuantity": {"value": "100"},
                            },
                            "tiers": [
                                {
                                    "startAmount": {"value": "0"},
                                    "listPrice": {
                                        "currencyCode": "USD",
                                        "nanos": first_nanos,
                                    },
                                },
                                {
                                    "startAmount": {"value": "1000"},
                                    "listPrice": {
                                        "currencyCode": "USD",
                                        "nanos": second_nanos,
                                    },
                                },
                            ],
                        },
                    }
                ],
            }

        prices = [price("SKU-A", 400_000_000, 300_000_000), price("SKU-B", 500_000_000, 250_000_000)]
        paths_and_rows = [
            (self.raw / "services.jsonl", "services", services),
            (self.raw / "skus.jsonl", "skus", skus),
            (self.raw / "prices-usd.jsonl", "prices", prices),
        ]
        sources = []
        for path, collection, rows in paths_and_rows:
            write_jsonl(path, rows)
            sources.append(
                {
                    "collection": collection,
                    "endpoint": f"https://example.invalid/{collection}",
                    "file": path.name,
                    "pages": 1,
                    "rows": len(rows),
                    "sha256": EXPORTER.sha256_file(path),
                }
            )
        EXPORTER.write_json(
            self.raw / "manifest.json",
            {
                "schemaVersion": 1,
                "apiVersion": "v2beta",
                "currencyCode": "USD",
                "paginationComplete": True,
                "retrievalStartedAt": "2026-08-26T00:00:00+00:00",
                "retrievalCompletedAt": "2026-08-26T00:01:00+00:00",
                "snapshotId": "gcp-pricing-test",
                "sources": sources,
            },
        )
        self.parquet = self.root / "pricing.parquet"
        self.manifest = self.root / "pricing.manifest.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def export(self) -> dict[str, object]:
        return EXPORTER.export_parquet(
            self.raw,
            self.parquet,
            self.manifest,
            "USD",
            EXPORTER.pa.Codec.maximum_compression_level("zstd"),
            2,
            2,
            False,
        )

    def test_export_is_exact_complete_and_zstd_compressed(self) -> None:
        result = self.export()
        self.assertEqual(result["normalization"]["price_tiers"], 4)
        self.assertEqual(result["parquet"]["compression"], "ZSTD")
        self.assertEqual(
            result["parquet"]["compressionLevel"],
            EXPORTER.pa.Codec.maximum_compression_level("zstd"),
        )
        parquet = pq.ParquetFile(self.parquet)
        self.assertEqual(parquet.metadata.num_rows, 4)
        for row_group in range(parquet.metadata.num_row_groups):
            for column in range(parquet.metadata.num_columns):
                self.assertEqual(
                    parquet.metadata.row_group(row_group).column(column).compression,
                    "ZSTD",
                )
        table = pq.read_table(self.parquet, columns=["unit_quantity", "tier_start", "list_price"])
        self.assertEqual(str(table.schema.field("list_price").type), "decimal128(38, 9)")
        self.assertEqual(table.column("list_price").to_pylist()[0], Decimal("0.400000000"))

    def test_query_helper_preserves_tiers_costs_filters_and_comparison(self) -> None:
        self.export()
        connection = QUERY.connect(self.parquet)
        try:
            rate = QUERY.rate(connection, "SKU-A", "Default", Decimal("1500"))
            self.assertEqual(rate["tier_start"], "1000")
            self.assertEqual(rate["price_per_base_unit"], "0.003")
            cost = QUERY.progressive_cost(connection, "SKU-A", "Default", Decimal("1500"))
            self.assertEqual(cost["total_cost"], "5.5")
            count = QUERY.count_skus(connection, "SERVICE-1", "us-central1", "Test Cores")
            self.assertEqual(count["count"], 1)
            comparison = QUERY.compare(
                connection, ["SKU-A", "SKU-B"], "Default", Decimal("1500")
            )
            self.assertEqual(comparison["cheapest_sku_id"], "SKU-B")
            self.assertEqual(comparison["difference_per_base_unit"], "0.0005")
            self.assertEqual(
                comparison["snapshot"]["retrieved_at"], "2026-08-26T00:01:00+00:00"
            )
        finally:
            connection.close()

    def test_source_hash_mismatch_fails_closed(self) -> None:
        manifest_path = self.raw / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["sources"][0]["sha256"] = "0" * 64
        EXPORTER.write_json(manifest_path, manifest)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.export()


if __name__ == "__main__":
    unittest.main()
