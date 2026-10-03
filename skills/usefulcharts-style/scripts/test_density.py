#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check density shortfalls, uncertainty and invalid evidence boundaries."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compare_density import METRICS, compare


def census(values=(100, 80, 120, 60)):
    return {"schema_version": 1, "family": "timeline",
            "comparison_basis": "same-full-poster-area",
            "counting_protocol": "usefulcharts-knowledge-v1", "coverage": "full-body",
            "image_sha256": "a"*64, "ledger": "Synthetic test ledger; not a real reference census.",
            "method": "manual-census", "census_review": "pass", "semantic_review": "pass",
            "legibility_review": "pass", "counts": {k: [v, v] for k, v in zip(METRICS, values)}}


class DensityTests(unittest.TestCase):
    def test_equal_reference_is_the_floor(self):
        self.assertTrue(compare(census(), census())["passes_measured_floor"])

    def test_extra_names_cannot_replace_explanation(self):
        result = compare(census(), census((1000, 800, 1200, 30)))
        self.assertEqual(result["status"], "below-reference")
        self.assertEqual(result["checks"][-1]["shortfall"], 30)

    def test_uncertain_intervals_use_conservative_endpoints(self):
        reference, candidate = census(), census()
        reference["counts"]["named_records"] = [100, 120]
        candidate["counts"]["named_records"] = [110, 150]
        result = compare(reference, candidate)
        self.assertFalse(result["passes_measured_floor"])
        self.assertEqual(result["checks"][0]["shortfall"], 10)

    def test_incomplete_census_is_not_zero(self):
        candidate = census()
        candidate["counts"]["context_statements"] = None
        self.assertEqual(compare(census(), candidate)["status"], "needs-evidence")

    def test_ocr_and_dense_but_unreadable_content_cannot_pass(self):
        for field, value in [("method", "ocr"), ("legibility_review", "fail"),
                             ("semantic_review", "pending"), ("coverage", "selected-crop")]:
            with self.subTest(field=field):
                candidate = census((1000, 1000, 1000, 1000))
                candidate[field] = value
                self.assertFalse(compare(census(), candidate)["passes_measured_floor"])

    def test_empty_reference_and_missing_evidence_remain_pending(self):
        reference = census((0, 0, 0, 0))
        self.assertEqual(compare(reference, census())["status"], "needs-evidence")
        for field in ("image_sha256", "ledger"):
            candidate = census()
            candidate[field] = None
            self.assertEqual(compare(census(), candidate)["status"], "needs-evidence")

    def test_family_and_comparison_basis_cannot_be_swapped(self):
        for field, value in [("family", "genealogy"), ("comparison_basis", "per-svg-pixel")]:
            candidate = census()
            candidate[field] = value
            with self.assertRaises(ValueError):
                compare(census(), candidate)

    def test_invalid_counts_are_rejected(self):
        for value in ([True, 5], [-1, 5], [9, 3], [1.5, 2], [0, float("nan")], [1], "100"):
            candidate = census()
            candidate["counts"]["named_records"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                compare(census(), candidate)

    def test_cli_reports_shortfall_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd(), prefix=".density-test-") as directory:
            folder = Path(directory)
            reference, candidate, report = (folder / name for name in ("reference.json", "candidate.json", "nested/report.json"))
            reference.write_text(json.dumps(census()), encoding="utf-8")
            candidate.write_text(json.dumps(census((100, 80, 120, 20))), encoding="utf-8")
            before = reference.read_bytes(), candidate.read_bytes()
            command = [sys.executable, str(Path(__file__).with_name("compare_density.py")), str(reference), str(candidate)]
            result = subprocess.run(command+["--report", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report.read_text())["status"], "below-reference")
            gated = subprocess.run(command+["--report", str(report), "--require-pass"], capture_output=True, text=True)
            self.assertEqual(gated.returncode, 1)
            overwrite = subprocess.run(command+["--report", str(reference)], capture_output=True, text=True)
            self.assertEqual(overwrite.returncode, 2)
            self.assertEqual(before, (reference.read_bytes(), candidate.read_bytes()))


if __name__ == "__main__":
    unittest.main()
