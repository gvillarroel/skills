#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the normalized technical-logo bundle."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS = SKILL_ROOT / "assets" / "logos"
SPEC = importlib.util.spec_from_file_location(
    "sync_normalized_logos", SCRIPT_DIR / "sync_normalized_logos.py"
)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class LogoAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (ASSETS / "logo_manifest.json").read_text(encoding="utf-8")
        )

    def test_inventory_exceeds_goal_and_has_required_providers(self) -> None:
        logos = self.manifest["logos"]
        self.assertEqual(self.manifest["logoCount"], 1648)
        self.assertGreaterEqual(len(logos), 400)
        counts = {
            provider: sum(item["provider"] == provider for item in logos)
            for provider in ("AWS", "GCP", "Devicon", "Simple Icons")
        }
        self.assertEqual(counts, {"AWS": 860, "GCP": 93, "Devicon": 578, "Simple Icons": 117})

    def test_ids_and_source_artwork_are_unique(self) -> None:
        logos = self.manifest["logos"]
        self.assertEqual(len({item["id"] for item in logos}), len(logos))
        self.assertEqual(len({item["assetPath"] for item in logos}), len(logos))
        self.assertEqual(len({item["sourceSha256"] for item in logos}), len(logos))

    def test_representative_cloud_and_company_logos_exist(self) -> None:
        ids = {item["id"] for item in self.manifest["logos"]}
        required = {
            "aws-compute-lambda",
            "aws-storage-simple-storage-service",
            "gcp-compute-cloud-run",
            "gcp-compute-compute-engine",
            "gcp-data-analytics-big-query",
            "gcp-storage-cloud-storage",
            "devicon-amazonwebservices",
            "devicon-googlecloud",
            "devicon-azure",
            "devicon-docker",
            "devicon-github",
            "devicon-kubernetes",
            "devicon-oracle",
            "simpleicons-apache",
            "simpleicons-angular",
            "simpleicons-android",
        }
        self.assertFalse(required - ids)

    def test_every_svg_and_embedded_source_passes_validator(self) -> None:
        self.assertEqual(SYNC.validate(ASSETS, self.manifest), [])

    def test_license_log_has_one_row_per_logo_and_source_license_texts(self) -> None:
        log = (ASSETS / "license_log.md").read_text(encoding="utf-8")
        rows = [line for line in log.splitlines() if line.startswith("| `") and ".svg` |" in line]
        self.assertEqual(len(rows), self.manifest["logoCount"])
        self.assertTrue((ASSETS / "licenses" / "CC-BY-ND-2.0.txt").is_file())
        self.assertTrue((ASSETS / "licenses" / "MIT.txt").is_file())
        self.assertTrue((ASSETS / "licenses" / "Apache-2.0.txt").is_file())
        self.assertTrue((ASSETS / "licenses" / "BSD-3-Clause.txt").is_file())
        self.assertTrue((ASSETS / "licenses" / "CC0-1.0.txt").is_file())


if __name__ == "__main__":
    unittest.main()
