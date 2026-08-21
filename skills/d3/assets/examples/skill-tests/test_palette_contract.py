#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unit tests for the unified D3 palette validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[3] / "scripts" / "check_palette_contract.py"
SPEC = importlib.util.spec_from_file_location("check_palette_contract", MODULE_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PaletteContractTests(unittest.TestCase):
    def validate(self, source: str, **kwargs):
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "artifact.html"
            artifact.write_text(source, encoding="utf-8")
            return CHECKER.validate_artifact(artifact, **kwargs)

    def test_standard_colorset_passes(self) -> None:
        report = self.validate(
            '<body data-colorset="colorset1"><svg style="color:#333e48"><rect fill="#9e1b32"/></svg></body>',
            colorset="colorset1",
        )
        self.assertTrue(report["ok"], report)

    def test_extended_token_fails_standard(self) -> None:
        report = self.validate(
            '<body data-colorset="colorset1"><svg><rect fill="#007298"/></svg></body>',
            colorset="colorset1",
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["forbiddenColors"], ["#007298"])

    def test_explicit_extended_requires_signature(self) -> None:
        report = self.validate(
            '<svg data-color-set="colorset2"><rect fill="#007298"/><circle fill="#e77204"/></svg>',
            colorset="colorset2",
            require_extended=True,
        )
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["extendedColorsUsed"], ["#007298", "#e77204"])

    def test_functional_and_named_colors_fail(self) -> None:
        report = self.validate(
            '<svg data-colorset="colorset1"><rect fill="red" style="stroke:rgb(0,0,0)"/></svg>',
            colorset="colorset1",
        )
        self.assertFalse(report["ok"])
        self.assertTrue(report["functionalColorSyntax"])
        self.assertEqual(report["namedPaints"], ["red"])

    def test_dynamic_script_body_is_reported_but_not_scanned(self) -> None:
        report = self.validate(
            '<body data-colorset="colorset1"><svg fill="#9e1b32"></svg><script>const paint="#007298";</script></body>',
            colorset="colorset1",
        )
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["ignoredDynamicScriptCount"], 1)

    def test_metadata_is_required(self) -> None:
        report = self.validate('<svg fill="#9e1b32"></svg>', colorset="colorset1")
        self.assertFalse(report["ok"])
        self.assertFalse(report["metadataMatches"])

    def test_yaml_palette_projections_match_json(self) -> None:
        palette_root = MODULE_PATH.parents[1] / "assets" / "palettes"
        payload = json.loads((palette_root / "colorsets.json").read_text(encoding="utf-8"))
        for colorset_id, filename in (
            ("colorset1", "colorset1.yml"),
            ("colorset2", "colorset2.yaml"),
        ):
            projected = set(
                re.findall(
                    r'^\s*value:\s*"(#[0-9a-f]{6})"\s*$',
                    (palette_root / filename).read_text(encoding="utf-8"),
                    re.MULTILINE,
                )
            )
            expected = set(payload["colorsets"][colorset_id]["allowed"])
            self.assertEqual(projected, expected, colorset_id)


if __name__ == "__main__":
    unittest.main()
