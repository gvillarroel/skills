#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = SCRIPT_DIR.parent
VALIDATOR_PATH = SCRIPT_DIR / "validate_max_elements.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module("mermaid_max_elements_validator_tests", VALIDATOR_PATH)
styler = validator.load_styler()
manifest = validator.load_json(validator.MANIFEST_PATH)
diagram_types = validator.load_json(validator.DIAGRAM_TYPES_PATH)


class MaximumElementCoverageTests(unittest.TestCase):
    def test_manifest_covers_every_public_family_and_cyclic_contract(self) -> None:
        findings: list[str] = []
        cases = validator.validate_manifest(manifest, diagram_types, findings)
        self.assertEqual(findings, [])
        self.assertEqual(len(cases), 31)
        self.assertEqual(len(manifest["renderContracts"]), 11)

    def test_every_classdef_family_has_a_nine_role_capacity_fixture(self) -> None:
        classdef_families = {
            family["id"]
            for family in diagram_types["families"]
            if family["classDef"] and family["id"] != "treemap"
        }
        semantic_cases = {
            case["id"]: case
            for case in manifest["families"]
            if case["capacityKind"] == "semantic-classes"
        }
        self.assertEqual(set(semantic_cases), classdef_families)
        for case in semantic_cases.values():
            self.assertEqual(case["maxSlots"], 9)
            self.assertEqual(case["fixtureElementCount"], 9)

    def test_general_scale_has_twelve_distinct_palette_colors(self) -> None:
        for colorset in ("colorset1", "colorset2"):
            theme = styler.theme_variables(colorset, "timeline")
            colors = [theme[f"cScale{index}"] for index in range(12)]
            self.assertEqual(theme["THEME_COLOR_LIMIT"], 12)
            self.assertEqual(len(colors), 12)
            self.assertEqual(len(set(colors)), 12)

    def test_standard_xy_palette_has_five_distinct_red_neutral_colors(self) -> None:
        palette = styler.theme_variables("colorset1", "xyChart")["xyChart"][
            "plotColorPalette"
        ]
        colors = [color.strip() for color in palette.split(",")]
        self.assertEqual(len(colors), 5)
        self.assertEqual(len(set(colors)), 5)

    def test_all_sources_style_idempotently(self) -> None:
        for case in manifest["families"]:
            source = validator.source_for_case(manifest, case)
            for colorset in ("colorset1", "colorset2"):
                styled, metadata = styler.style_mermaid_block(source, colorset)
                restyled, second_metadata = styler.style_mermaid_block(
                    styled, colorset
                )
                self.assertEqual(metadata["family"], case["id"])
                self.assertEqual(second_metadata["family"], case["id"])
                self.assertEqual(restyled, styled)

    def test_dense_semantic_er_and_swimlane_receive_compact_layouts(self) -> None:
        cases = {
            case["id"]: case
            for case in manifest["families"]
            if case["id"] in {"erDiagram", "swimlane"}
        }
        er_styled, _ = styler.style_mermaid_block(
            validator.source_for_case(manifest, cases["erDiagram"]), "colorset2"
        )
        self.assertIn("  er:\n    minEntityWidth: 180\n    rankSpacing: 20", er_styled)

        swimlane_styled, _ = styler.style_mermaid_block(
            validator.source_for_case(manifest, cases["swimlane"]), "colorset2"
        )
        self.assertIn(
            "  flowchart:\n    nodeSpacing: 10\n    rankSpacing: 20",
            swimlane_styled,
        )

    def test_dense_semantic_layout_preserves_explicit_user_spacing(self) -> None:
        case = next(
            case for case in manifest["families"] if case["id"] == "swimlane"
        )
        source = (
            "---\n"
            "config:\n"
            "  flowchart:\n"
            "    nodeSpacing: 77\n"
            "    rankSpacing: 66\n"
            "---\n"
            + validator.source_for_case(manifest, case)
        )
        styled, _ = styler.style_mermaid_block(source, "colorset2")
        self.assertEqual(styled.count("flowchart:"), 1)
        self.assertIn("nodeSpacing: 77", styled)
        self.assertIn("rankSpacing: 66", styled)
        self.assertNotIn("nodeSpacing: 10", styled)

    def test_semantic_binding_gate_rejects_a_role_without_geometry(self) -> None:
        class_names = ["csPrimary", "csAccent"]
        declarations = "".join(
            styler.class_style("colorset2", class_name) for class_name in class_names
        )
        primary = styler.class_style("colorset2", "csPrimary")
        primary_fill = primary.split("fill:", 1)[1].split(",", 1)[0]
        primary_stroke = primary.split("stroke:", 1)[1].split(",", 1)[0]
        svg = (
            "<svg><style>"
            f".csPrimary&gt;*{{fill:{primary_fill};stroke:{primary_stroke};}}"
            f"{declarations}"
            "</style><g class=\"node csPrimary\"><rect/></g></svg>"
        )
        findings: list[str] = []
        validator.validate_semantic_class_bindings(
            styler,
            "flowchart",
            "colorset2",
            class_names,
            svg,
            findings,
        )
        self.assertTrue(
            any("csAccent is not bound" in finding for finding in findings),
            findings,
        )

    def test_render_contract_detects_a_missing_terminal_slot(self) -> None:
        case = next(case for case in manifest["families"] if case["id"] == "mindmap")
        contract = manifest["renderContracts"]["mindmap"]
        tokens = validator.contract_tokens(contract)
        theme = styler.theme_variables("colorset2", "mindmap")
        colors: list[str] = []
        for key in validator.contract_style_keys(contract):
            colors.extend(validator.iter_hex_colors(theme[key]))
        css_rules: list[str] = []
        for binding in contract["cssBindings"]:
            selector_start = int(binding["selectorStart"])
            for offset, selector_index in enumerate(
                range(selector_start, int(binding["selectorEnd"]) + 1)
            ):
                selector = binding["selectorTemplate"].format(index=selector_index)
                theme_key = f"{binding['themePrefix']}{int(binding['themeStart']) + offset}"
                css_rules.append(f"{selector}{{fill:{theme[theme_key]};}}")
        synthetic_svg = (
            "<svg><style>"
            + "".join(css_rules)
            + "</style>"
            + " ".join([*tokens, *colors])
            + "</svg>"
        )

        findings: list[str] = []
        validator.validate_render_contract(
            styler,
            case,
            contract,
            "colorset2",
            validator.source_for_case(manifest, case),
            synthetic_svg,
            findings,
        )
        self.assertEqual(findings, [])

        terminal_token = tokens[-1]
        broken_svg = synthetic_svg.replace(terminal_token, "", 1)
        broken_findings: list[str] = []
        validator.validate_render_contract(
            styler,
            case,
            contract,
            "colorset2",
            validator.source_for_case(manifest, case),
            broken_svg,
            broken_findings,
        )
        self.assertTrue(
            any(terminal_token in finding for finding in broken_findings),
            broken_findings,
        )

    def test_terminal_index_bindings_reach_the_actual_theme_tail(self) -> None:
        mindmap = manifest["renderContracts"]["mindmap"]["cssBindings"][0]
        self.assertEqual(
            (mindmap["selectorStart"], mindmap["selectorEnd"]), (-1, 10)
        )
        self.assertEqual(mindmap["themeStart"], 0)
        self.assertEqual(manifest["renderContracts"]["mindmap"]["styleRanges"][0]["end"], 11)

        kanban = manifest["renderContracts"]["kanban"]["cssBindings"][0]
        self.assertEqual((kanban["selectorStart"], kanban["selectorEnd"]), (1, 10))
        self.assertEqual(kanban["themeStart"], 2)
        self.assertEqual((kanban["transform"], kanban["amount"]), ("lighten", 10))

    def test_treemap_named_root_leaves_eleven_direct_group_slots(self) -> None:
        case = next(case for case in manifest["families"] if case["id"] == "treemap")
        source = validator.source_for_case(manifest, case)
        self.assertEqual(case["maxSlots"], 12)
        self.assertEqual(case["fixtureElementCount"], 12)
        self.assertIn("Treemap capacity", source)
        self.assertIn("Treemap group 11", source)
        self.assertNotIn("Treemap group 12", source)

    def test_journey_records_the_reachable_boundary_cycle(self) -> None:
        case = next(case for case in manifest["families"] if case["id"] == "journey")
        contract = manifest["renderContracts"]["journey"]
        self.assertEqual(case["maxSlots"], 7)
        self.assertEqual(case["fixtureElementCount"], 8)
        self.assertEqual(contract["ranges"][0]["end"], 6)
        self.assertEqual(contract["counts"][0]["count"], 6)
        for colorset in ("colorset1", "colorset2"):
            theme = styler.theme_variables(colorset, "journey")
            self.assertTrue(all(f"fillType{index}" in theme for index in range(8)))
            configured = [theme[f"fillType{index}"] for index in range(8)]
            self.assertEqual(len(set(configured)), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
