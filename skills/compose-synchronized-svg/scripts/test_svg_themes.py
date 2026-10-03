#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise palette ownership through the actual compiler, composer, and auditors."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import compile_synchronized_svg_plan as compiler
import compose_synchronized_svg as composer
import scaffold_synchronized_svg as scaffold

SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = SCRIPTS.parent / "assets" / "templates" / "composition-brief.json"


class SvgThemeTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="svg-theme-")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def compose(self, brief: dict, name: str = "rendered") -> tuple[dict, Path]:
        plan, _ = compiler.compile_brief(brief)
        spec = self.workspace / f"{name}.json"
        svg = self.workspace / f"{name}.svg"
        spec.write_text(json.dumps(plan), encoding="utf-8")
        composer.compose(SimpleNamespace(spec=spec, output=svg, report=None, force=True))
        return plan, svg

    def validate(self, svg: Path) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_synchronized_svg.py"), str(svg), "--json"],
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_recoloring_preserves_model_geometry_and_rejects_patched_theme(self) -> None:
        original_plan, original_svg = self.compose(self.brief, "original")
        changed = copy.deepcopy(self.brief)
        changed["theme"] = {
            "colors": {"canvas": "#ffffff", "ink": "#1c1c1c", "muted": "#696969", "accent": "#6d1222"},
            "conceptColors": {"input-rate": "#363636"},
        }
        plan, svg = self.compose(changed, "brand")
        original_model = {key: value for key, value in original_plan.items() if key != "theme"}
        self.assertEqual(original_model, {key: value for key, value in plan.items() if key != "theme"})
        self.assertEqual(scaffold.initial_values(original_plan), scaffold.initial_values(plan))
        geometry_keys = {"d", "x", "y", "width", "height", "transform", "data-bind", "data-current-value"}
        def geometry(path: Path) -> list:
            return [{k: v for k, v in node.attrib.items() if k in geometry_keys} for node in ET.parse(path).iter()]
        self.assertEqual(geometry(original_svg), geometry(svg))
        code, report = self.validate(svg)
        self.assertEqual(code, 0, report)
        text = svg.read_text(encoding="utf-8")
        self.assertIn("--accent: #6d1222;", text)
        self.assertIn("--concept-input-rate: #363636;", text)
        self.assertIn('id="composition-theme"', text)
        self.assertIn('stroke="none"', text)
        self.assertIn('fill="var(--concept-', text)
        svg.write_text(text.replace("--accent: #6d1222;", "--accent: #e7e7e7;"), encoding="utf-8")
        code, report = self.validate(svg)
        self.assertNotEqual(code, 0, report)
        self.assertIn("theme token --accent", json.dumps(report))

    def test_legacy_plan_keeps_original_concept_colors(self) -> None:
        plan, _ = compiler.compile_brief(self.brief)
        del plan["theme"]
        theme = scaffold.theme_for_plan(plan)
        self.assertEqual(theme["preset"], "classic")
        self.assertEqual(theme["conceptColors"]["input-rate"], "#9e1b32")

    def test_subject_title_is_visible_and_renderer_metadata_is_preserved(self) -> None:
        self.brief["modules"][0]["title"] = "Operating inputs"
        plan, svg = self.compose(self.brief)
        self.assertEqual(plan["modules"][0]["title"], "Operating inputs")
        text = svg.read_text(encoding="utf-8")
        self.assertIn("OPERATING INPUTS", text)
        self.assertIn('data-asset-type="network-diagram"', text)
        self.brief["modules"][0]["title"] = " "
        with self.assertRaises(ValueError):
            compiler.compile_brief(self.brief)

    def test_invalid_palette_fails_preflight_before_outputs(self) -> None:
        self.brief["theme"] = {"colors": {"muted": "#e7e7e7"}}
        source = self.workspace / "bad-brief.json"
        source.write_text(json.dumps(self.brief), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "preflight_svg_brief.py"), "--brief", str(source), "--json"],
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertIn("contrast", result.stdout)
        self.assertEqual(list(self.workspace.glob("*.svg")), [])

    def test_browser_audits_static_scenario_composition_with_null_timeline(self) -> None:
        self.brief["timeline"] = None
        _, svg = self.compose(self.brief)
        report = self.workspace / "browser.json"
        result = subprocess.run(
            ["uv", "run", "--script", str(SCRIPTS / "audit_synchronized_svg.py"), str(svg),
             "--report", str(report), "--compact-report"],
            text=True, encoding="utf-8", capture_output=True, check=False, timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["ok"])

    def test_residual_partition_composes_as_stack_in_every_scenario(self) -> None:
        flow = next(module for module in self.brief["modules"] if module["assetType"] == "sankey-diagram")
        total, *parts = flow["values"]
        flow.update(assetType="stacked-bar", values=parts, stackTotal=total)
        for scenario in self.brief["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.brief["initialScenario"] = scenario["id"]
                plan, svg = self.compose(self.brief, scenario["id"])
                module = next(module for module in plan["modules"] if module["id"] == flow["id"])
                marks = [binding["value"] for binding in module["bindings"] if binding["channel"] == "width"]
                self.assertEqual(marks, parts)
                code, report = self.validate(svg)
                self.assertEqual(code, 0, report)


if __name__ == "__main__":
    unittest.main()
