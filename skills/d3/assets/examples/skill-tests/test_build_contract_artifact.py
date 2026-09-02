#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the deterministic D3 contract artifact builder."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import build_contract_artifact


def common(root: Path, kind: str, colorset: str = "colorset1") -> dict[str, object]:
    return {
        "kind": kind, "output": root / "visual.html", "decision_output": root / "decision.json",
        "title": "Contract visual", "description": "Deterministic contract artifact.",
        "route": "visualization" if kind != "logo" else "logo", "colorset": colorset,
        "pattern_id": f"d3-test-{kind}", "svg_pattern_id": None, "svg_id": f"test-{kind}",
        "reason": "The requested relationship maps to this D3 route.", "width": 900, "height": 520,
        "attribute": [], "item": [], "unit": "Value", "mark_class": "data-mark",
        "stem_class": "stem", "dot_class": "dot", "node": [], "flow_node": [],
        "link": [], "link_value": [], "node_class": "node", "link_class": "link",
        "layout": "pre-ticked-force", "brand": None, "tagline": None,
        "logo_mode": "orbit", "wedge_count": 12, "logo_mark_class": "logo-mark",
        "wedge_class": "wedge", "brand_class": "brand-text", "tagline_class": "tagline",
        "force": False,
    }


class ContractArtifactBuilderTests(unittest.TestCase):
    def test_help_discloses_all_repeated_literal_formats(self) -> None:
        help_text = build_contract_artifact.make_parser().format_help()
        for literal in (
            "--attribute DATA-NAME=VALUE",
            "--item LABEL=NUMBER",
            "--node LABEL=ROLE",
            "--link 'SOURCE->TARGET'",
            "colorset1: primary",
            "colorset2 also: blue, orange, green, purple, yellow",
        ):
            self.assertIn(literal, help_text)

    def test_bar_uses_standard_palette_and_literal_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "bar")
            values.update(svg_id="defect-chart", item=[("Alpha", "12"), ("Beta", "19")], unit="escaped defects", attribute=[("data-chart-kind", "bar")])
            html, decision = build_contract_artifact.build(argparse.Namespace(**values))
            self.assertIn('id="defect-chart"', html)
            self.assertIn('data-chart-kind="bar"', html)
            self.assertIn('"class",spec.markClass', html)
            self.assertIn("#9e1b32", html)
            self.assertNotIn("rgba(", html.split("</style>", 1)[0])
            self.assertEqual(decision["colorset"], "colorset1")

    def test_network_uses_extended_roles_and_exact_classes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "network", "colorset2")
            values.update(svg_id="service-network", node=[("Gateway", "blue"), ("Queue", "orange"), ("Worker", "green"), ("Store", "purple")], link=[("Gateway", "Queue"), ("Queue", "Worker"), ("Worker", "Store")])
            html, _ = build_contract_artifact.build(argparse.Namespace(**values))
            for token in ("#007298", "#e77204", "#45842a", "#652f6c"):
                self.assertIn(token, html)
            self.assertIn('data-layout="pre-ticked-force"', html)
            self.assertIn('"class",spec.nodeClass', html)
            self.assertIn('"class",spec.linkClass', html)

    def test_logo_preserves_copy_and_adds_extended_orbit_system(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "logo", "colorset2")
            values.update(brand="Atlas Forge", tagline="Build with signal")
            html, decision = build_contract_artifact.build(argparse.Namespace(**values))
            self.assertIn("Atlas Forge", html)
            self.assertIn("Build with signal", html)
            self.assertIn('"class","orbit-node"', html)
            self.assertIn('"class","orbit-link"', html)
            self.assertEqual(decision["route"], "logo")

    def test_rejects_extended_role_under_standard_palette(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "network", "colorset1")
            values.update(node=[("A", "blue"), ("B", "primary")], link=[("A", "B")])
            with self.assertRaisesRegex(ValueError, "unavailable in colorset1"):
                build_contract_artifact.build(argparse.Namespace(**values))

    def test_flow_preserves_distinct_decision_and_svg_pattern_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "flow")
            values.update(
                pattern_id="d3-flow-fresh-canonical",
                svg_pattern_id="d3-source-flow",
                flow_node=["Intake", "Review", "Release"],
                link=[("Intake", "Review"), ("Review", "Release")],
                link_value=["7", "5"],
                attribute=[("data-composition-id", "flow")],
            )
            html, decision = build_contract_artifact.build(argparse.Namespace(**values))
            self.assertIn('data-pattern-id="d3-source-flow"', html)
            self.assertIn('data-composition-id="flow"', html)
            self.assertIn("Intake", html)
            self.assertEqual(decision["patternId"], "d3-flow-fresh-canonical")

    def test_flow_rejects_title_that_advances_a_later_ordered_label(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "flow")
            values.update(
                title="Flow spine: Confirm to Route",
                flow_node=["Confirm", "Classify", "Observe", "Persist", "Route"],
                link=[
                    ("Confirm", "Classify"),
                    ("Classify", "Observe"),
                    ("Observe", "Persist"),
                    ("Persist", "Route"),
                ],
                link_value=["12", "7", "6", "5"],
            )
            with self.assertRaisesRegex(ValueError, "ordered-label first occurrence"):
                build_contract_artifact.build(argparse.Namespace(**values))

    def test_wedge_logo_uses_all_extended_color_groups(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = common(Path(temporary), "logo", "colorset2")
            values.update(
                brand="Signal Works",
                tagline="Clarity in motion",
                logo_mode="wedges",
                wedge_count=16,
            )
            html, _ = build_contract_artifact.build(argparse.Namespace(**values))
            for token in ("#007298", "#e77204", "#45842a", "#652f6c"):
                self.assertIn(token, html)
            self.assertIn('data-logo-pattern="d3-test-logo"', html)
            self.assertIn('"class",spec.wedgeClass', html)


if __name__ == "__main__":
    unittest.main()
