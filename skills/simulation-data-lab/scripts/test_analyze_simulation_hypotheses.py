#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box tests for machine-readable simulation hypothesis analysis."""

from __future__ import annotations

import copy
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).with_name("run_simulation_experiment.py")
ANALYZER = Path(__file__).with_name("analyze_simulation_hypotheses.py")
VALIDATOR = Path(__file__).with_name("validate_simulation_bundle.py")
TEMPLATE_SPEC = SKILL_ROOT / "assets/templates/experiment.json"
TEMPLATE_MODEL = SKILL_ROOT / "assets/templates/model.py"


class AnalyzerTests(unittest.TestCase):
    def run_cli(self, script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(item) for item in arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def prepare_bundle(self, root: Path, spec: dict[str, Any]) -> None:
        root.mkdir(parents=True)
        (root / "experiment.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        shutil.copyfile(TEMPLATE_MODEL, root / "model.py")
        plan = self.run_cli(
            RUNNER,
            "plan",
            "--spec",
            root / "experiment.json",
            "--output-dir",
            root / "design",
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)
        run = self.run_cli(RUNNER, "run", "--root", root, "--model", "model.py")
        self.assertEqual(run.returncode, 0, run.stderr)

    def analyze_and_validate(self, root: Path) -> dict[str, Any]:
        analyzed = self.run_cli(ANALYZER, "--root", root)
        self.assertEqual(analyzed.returncode, 0, analyzed.stderr)
        validated = self.run_cli(VALIDATOR, "--root", root)
        self.assertEqual(validated.returncode, 0, validated.stderr)
        return json.loads((root / "analysis/hypothesis-results.json").read_text("utf-8"))

    def template_spec(self) -> dict[str, Any]:
        spec = json.loads(TEMPLATE_SPEC.read_text("utf-8"))
        spec["replications"] = 6
        return spec

    def test_paired_analysis_reports_every_design_point_and_complete_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            result = report["results"][0]
            self.assertEqual(
                [(item["designPointId"], item["role"]) for item in result["designPointResults"]],
                [("low-demand", "challenge"), ("typical-demand", "primary")],
            )
            self.assertTrue(
                all(item["sample"]["completePairs"] == 6 for item in result["designPointResults"])
            )
            self.assertTrue(result["challengeSearch"]["performed"])

    def test_unpaired_analysis_uses_independent_samples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["seedPolicy"] = "independent-by-run"
            spec["hypotheses"][0]["analysis"]["pairing"] = "independent"
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            for point in report["results"][0]["designPointResults"]:
                self.assertIsNone(point["sample"]["completePairs"])
                self.assertEqual(point["interval"]["method"], "normal-wald-unpaired-v1")

    def test_deterministic_analysis_has_no_interval_and_zero_mcse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["uncertaintyMode"] = "deterministic"
            spec["replications"] = 1
            spec["seedPolicy"] = "independent-by-run"
            analysis = spec["hypotheses"][0]["analysis"]
            analysis["pairing"] = "deterministic"
            analysis["intervalMethod"] = "none"
            analysis["intervalLevel"] = None
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            for point in report["results"][0]["designPointResults"]:
                self.assertIsNone(point["interval"])
                self.assertEqual(point["mcse"], 0.0)

    def test_planner_rejects_unclassified_design_point(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir(parents=True)
            spec = self.template_spec()
            extra = copy.deepcopy(spec["designPoints"][0])
            extra["designPointId"] = "unclassified-demand"
            extra["parameters"][0]["value"] = 80
            spec["designPoints"].append(extra)
            (root / "experiment.json").write_text(
                json.dumps(spec, indent=2) + "\n", encoding="utf-8"
            )
            result = self.run_cli(
                RUNNER,
                "plan",
                "--spec",
                root / "experiment.json",
                "--output-dir",
                root / "design",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("must classify every design point", result.stderr)

    def test_not_identifiable_analysis_does_not_invent_an_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["scenarios"] = [spec["scenarios"][0]]
            hypothesis = spec["hypotheses"][0]
            hypothesis["scenarioIds"] = ["baseline-stock"]
            hypothesis["estimand"] = "causal effect of an unspecified policy versus baseline"
            hypothesis["analysis"] = {
                "kind": "not-identifiable",
                "reason": "No intervention scenario or counterfactual mechanism was supplied.",
            }
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            result = report["results"][0]
            self.assertEqual(result["status"], "not-identifiable-from-design")
            self.assertEqual(result["designPointResults"], [])
            self.assertFalse(result["challengeSearch"]["performed"])
            with (root / "data/outcomes.csv").open("r", encoding="utf-8", newline="") as handle:
                self.assertGreater(len(list(csv.DictReader(handle))), 0)


if __name__ == "__main__":
    unittest.main()
