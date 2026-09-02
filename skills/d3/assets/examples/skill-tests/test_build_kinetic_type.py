#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the kinetic glyph mosaic builder."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT_ROOT = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

import build_kinetic_type
import check_palette_contract
import check_self_contained_html


class KineticTypeBuilderTests(unittest.TestCase):
    def build(self, *, items: list[dict[str, str]] | None = None, colorset: str = "colorset1") -> str:
        return build_kinetic_type.build_document(
            items=items or build_kinetic_type.normalize_items([], []),
            title="Type reveals its structure",
            colorset=colorset,
            motion="energetic",
            seed=73,
        )

    def test_help_discloses_materials_and_interactions(self) -> None:
        help_text = build_kinetic_type.make_parser().format_help()
        for literal in (
            "tiles,lines,dots,hybrid",
            "hover, keyboard focus, or press",
            "--motion {calm,energetic}",
            "Exact output HTML path",
        ):
            self.assertIn(literal, help_text)

    def test_default_showcase_is_deterministic_and_embeds_runtime_unchanged(self) -> None:
        first = self.build()
        second = self.build()
        runtime = build_kinetic_type.D3_RUNTIME_PATH.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertIn(f'<script id="d3-runtime">{runtime}</script>', first)
        self.assertEqual(first.count('class="kinetic-word"'), 4)
        for variant in build_kinetic_type.VARIANTS:
            self.assertIn(f'data-variant="{variant}"', first)
        self.assertIn('data-pattern-id="d3-kinetic-glyph-mosaic"', first)
        self.assertIn("d3.scaleOrdinal", first)
        self.assertIn("getImageData", first)
        self.assertIn("prefers-reduced-motion", first)
        self.assertIn("__kineticTypeDiagnostics", first)
        self.assertIn('<link rel="icon" href="data:,">', first)

    def test_custom_text_is_escaped_and_defaults_to_hybrid(self) -> None:
        items = build_kinetic_type.normalize_items(["Signal <flow>"], [])
        document = self.build(items=items)
        self.assertEqual(items, [{"text": "Signal <flow>", "variant": "hybrid"}])
        self.assertIn("Signal &lt;flow&gt;", document)
        self.assertNotIn('<text class="base-text" x="360" y="154" text-anchor="middle" font-size="42" font-weight="900" fill="#1c1c1c">Signal <flow></text>', document)
        self.assertIn('data-variant="hybrid"', document)

    def test_variant_cardinality_and_text_limits_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one variant per --text"):
            build_kinetic_type.normalize_items(["ONE", "TWO", "THREE"], ["tiles", "lines"])
        with self.assertRaisesRegex(ValueError, "40 characters or fewer"):
            build_kinetic_type.normalize_items(["x" * 41], ["dots"])
        with self.assertRaisesRegex(ValueError, "requires at least one --text"):
            build_kinetic_type.normalize_items([], ["tiles"])

    def test_standard_and_extended_outputs_pass_bundled_static_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for colorset in ("colorset1", "colorset2"):
                artifact = root / f"kinetic-{colorset}.html"
                artifact.write_text(self.build(colorset=colorset), encoding="utf-8", newline="\n")
                self.assertEqual(check_self_contained_html.check_file(artifact), [])
                report = check_palette_contract.validate_artifact(
                    artifact,
                    colorset=colorset,
                    require_extended=colorset == "colorset2",
                )
                self.assertTrue(report["ok"], report["findings"])

    def test_main_creates_the_exact_requested_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "nested" / "kinetic.html"
            code = build_kinetic_type.main(
                [
                    str(artifact),
                    "--text",
                    "ASSEMBLE",
                    "--variant",
                    "tiles",
                    "--motion",
                    "calm",
                    "--seed",
                    "101",
                ]
            )
            self.assertEqual(code, 0)
            self.assertTrue(artifact.is_file())
            text = artifact.read_text(encoding="utf-8")
            self.assertIn("ASSEMBLE", text)
            self.assertIn('data-motion="calm"', text)
            self.assertIn('data-seed="101"', text)


if __name__ == "__main__":
    unittest.main()
