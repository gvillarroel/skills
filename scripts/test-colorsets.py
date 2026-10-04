#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test observable palette rejections and fidelity-aware SVG extraction."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("validate-colorsets.py")
SPEC = importlib.util.spec_from_file_location("colorset_validator", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ColorAuditTests(unittest.TestCase):
    def contract_with(self, modify):
        directory = MODULE.ROOT / "projects/solid-colorset-style/artifacts/tmp"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            root = Path(temp)
            (root / "docs").mkdir()
            contract = json.loads((MODULE.ROOT / "docs/colorsets.json").read_text(encoding="utf-8"))
            modify(contract)
            (root / "docs/colorsets.json").write_text(json.dumps(contract), encoding="utf-8")
            output = root / "mark.svg"
            output.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#9e1b32"/></svg>', encoding="utf-8")
            return MODULE.validate(root, [output], "colorset1")

    def test_solid_sequence_cannot_drop_or_duplicate_colors(self):
        def drop(contract):
            contract["colorsets"]["colorset1"]["solidSequence"].pop()
        def duplicate(contract):
            contract["colorsets"]["colorset2"]["solidSequence"].append("#9e1b32")
        self.assertFalse(self.contract_with(drop)["ok"])
        self.assertFalse(self.contract_with(duplicate)["ok"])

    def test_cs1_rejects_out_of_order_categories_even_with_complete_membership(self):
        for early, later in (("#333e48", "#9e1b32"), ("#6d1222", "#4f4f4f"),
                             ("#000000", "#e7e7e7"), ("#ffffff", "#000000"),
                             ("#ffccd5", "#ffffff")):
            for field in ("sequence", "solidSequence"):
                def change(contract):
                    colors = contract["colorsets"]["colorset1"][field]
                    colors.remove(early)
                    colors.insert(colors.index(later), early)
                result = self.contract_with(change)
                self.assertFalse(result["ok"], (field, early, later))
                self.assertTrue(any(row.get("field") == field for row in result["findings"]))

    def test_cs1_priority_change_keeps_text_and_complete_solid_contract(self):
        self.assertTrue(self.contract_with(lambda contract: None)["ok"])

    def test_text_decision_rejects_weak_contrast_and_non_black_white(self):
        for fill, text in (("#9e1b32", "#000000"), ("#f1c319", "#ffffff"), ("#007298", "#333e48")):
            def change(contract):
                contract["colorsets"]["colorset2"]["textOnFill"][fill] = text
            self.assertFalse(self.contract_with(change)["ok"], (fill, text))

    def test_text_decision_requires_every_solid_token(self):
        def change(contract):
            del contract["colorsets"]["colorset1"]["textOnFill"]["#ffccd5"]
        self.assertFalse(self.contract_with(change)["ok"])

    def inspect(self, body, mode="colorset1"):
        directory = MODULE.ROOT / "projects/colorset-audit/artifacts/tmp"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            path = Path(temp) / "diagram.svg"
            path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" data-colorset="{mode}">{body}</svg>', encoding="utf-8")
            return MODULE.validate(MODULE.ROOT, [path], mode)

    def test_exact_colors_alpha_and_source_metadata(self):
        result = self.inspect('<metadata>{"sourcePalette":["#abcdef"]}</metadata><rect fill="#9e1b32"/><path style="stroke:rgba(51,62,72,.5)"/>')
        self.assertTrue(result["ok"], result)

    def test_rogue_paint_cannot_hide_beside_valid_token(self):
        result = self.inspect('<rect fill="#9e1b32"/><circle fill="#abcdef"/>')
        self.assertFalse(result["ok"])
        self.assertEqual(result["findings"][0]["offPalette"], ["#abcdef"])

    def test_gradients_css_and_animation_values_are_checked(self):
        for body in ('<linearGradient><stop stop-color="#abcdef"/></linearGradient>', '<style>.x{fill:#abcdef}</style><rect class="x"/>', '<animate attributeName="fill" values="#9e1b32;#abcdef"/>', '<animate attributeName="fill" values="white;blue"/>'):
            self.assertFalse(self.inspect(body)["ok"], body)

    def test_named_and_hsl_paints_are_checked(self):
        for value in ("red", "tomato", "hsl(120,100%,50%)", "rgb(100% 0% 0%)", "rgb(999,0,0)", "oklch(50% .25 230)"):
            self.assertFalse(self.inspect(f'<rect fill="{value}"/>')["ok"], value)

    def test_composite_css_names_and_gradient_stops_fail(self):
        for value in ("border:1px solid tomato", "background:linear-gradient(to right, red, black)"):
            self.assertFalse(self.inspect(f'<style>.x{{{value}}}</style>')["ok"], value)

    def test_smil_lifetime_fill_is_not_paint(self):
        self.assertTrue(self.inspect('<rect fill="#9e1b32"><animate attributeName="x" values="0;10" fill="freeze"/></rect>')["ok"])

    def test_nested_gradient_rgb_functions_are_complete(self):
        self.assertTrue(self.inspect('<style>.x{background:linear-gradient(to right,rgba(51,62,72,.5) 0%,rgb(255 255 255) 100%)}</style>')["ok"])
        self.assertFalse(self.inspect('<style>.x{background:radial-gradient(circle at center,rgba(51,62,72,.5),rgb(1 2 3))}</style>')["ok"])

    def test_referenced_named_css_variable_cannot_hide_paint(self):
        self.assertFalse(self.inspect('<style>:root{--ink:tomato}.x{fill:var(--ink)}</style><rect class="x"/>')["ok"])
        self.assertTrue(self.inspect('<style>:root{--scheme:light;--ink:#333e48}.x{fill:var(--ink)}</style><rect class="x"/>')["ok"])

    def test_inline_html_svg_paints_are_checked(self):
        directory = MODULE.ROOT / "projects/colorset-audit/artifacts/tmp"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            path = Path(temp) / "inline.html"
            path.write_text('<html data-colorset="colorset1"><svg><rect fill="red"/><stop stop-color="#abcdef"/></svg></html>', encoding="utf-8")
            result = MODULE.validate(MODULE.ROOT, [path], "colorset1")
            self.assertFalse(result["ok"])
            self.assertIn("#abcdef", result["findings"][0]["offPalette"])

    def test_html_vendor_and_input_color_tables_are_not_rendered_paint(self):
        directory = MODULE.ROOT / "projects/colorset-audit/artifacts/tmp"
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            path = Path(temp) / "vendor.html"
            path.write_text('<html data-colorset="colorset1"><style>body{color:#333e48;background:white}</style><script>const decoder="#777777",source="color:tomato",library="rgb(";</script><svg><rect fill="#9e1b32"/></svg></html>', encoding="utf-8")
            self.assertTrue(MODULE.validate(MODULE.ROOT, [path], "colorset1")["ok"])

    def test_extended_hue_fails_cs1_and_passes_cs2(self):
        self.assertFalse(self.inspect('<rect fill="#007298"/>')["ok"])
        self.assertTrue(self.inspect('<rect fill="#007298"/>', "colorset2")["ok"])

    def test_declared_mode_conflict_is_a_failure(self):
        directory = MODULE.ROOT / "projects/colorset-audit/artifacts/tmp"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            path = Path(temp) / "wrong.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset2"><rect fill="#9e1b32"/></svg>', encoding="utf-8")
            self.assertFalse(MODULE.validate(MODULE.ROOT, [path], "colorset1")["ok"])


if __name__ == "__main__":
    unittest.main()
