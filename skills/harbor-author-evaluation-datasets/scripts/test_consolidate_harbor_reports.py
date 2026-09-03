#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box regression tests for the Harbor aggregate report consolidator."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).with_name("consolidate_harbor_reports.py")
OUTPUT_FILES = {
    "comparison-report.json",
    "comparison-report.md",
    "quality-comparison.svg",
    "resource-comparison.svg",
    "efficiency-frontier.svg",
}


def metric(count: int, total: float) -> dict[str, float | int]:
    return {"count": count, "total": total, "average": total / count}


def report(label: str = "baseline") -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "source": "harbor",
        "title": "Harbor Final Evaluation Report",
        "generatedAt": "2026-09-02T19:00:00+00:00",
        "comparison": {
            "enabled": True,
            "fairnessBasis": "same frozen task and runtime contract",
            "warning": None,
        },
        "jobs": [
            {
                "jobId": f"job-{label}",
                "label": label,
                "complete": True,
                # Native harbor-run-results reports can contain naive job timestamps.
                "startedAt": "2026-09-02T18:00:00",
                "finishedAt": "2026-09-02T18:01:00",
                "summary": {
                    "requestedTrials": 2,
                    "completedTrials": 2,
                    "passedTrials": 1,
                    "verifierFailedTrials": 1,
                    "erroredTrials": 0,
                    "passRate": 0.5,
                    "reward": metric(2, 1.0),
                    "totalTokens": metric(2, 360.0),
                    "agentLatencyMs": metric(2, 3000.0),
                    "costUsd": metric(2, 0.3),
                },
                "trials": [
                    {
                        "trialName": "SEALED-TASK-NAME-MUST-NOT-LEAK",
                        "taskName": "SEALED-TASK-NAME-MUST-NOT-LEAK",
                        "resultPath": "C:/private/SEALED-PATH-MUST-NOT-LEAK/result.json",
                        "prompt": "SEALED-PROMPT-MUST-NOT-LEAK",
                        "answer": "SEALED-ANSWER-MUST-NOT-LEAK",
                        "tokens": {
                            "input": 100,
                            "cachedInput": 40,
                            "output": 20,
                            "total": 120,
                            "reasoning": 5,
                        },
                    },
                    {
                        "trialName": "SEALED-SECOND-TASK-MUST-NOT-LEAK",
                        "tokens": {
                            "input": 200,
                            "cachedInput": 50,
                            "output": 40,
                            "total": 240,
                            "reasoning": 7,
                        },
                    },
                ],
            }
        ],
    }


def write_json(path: Path, value: Any, *, allow_nan: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, allow_nan=allow_nan) + "\n", encoding="utf-8"
    )


class ConsolidatorTests(unittest.TestCase):
    maxDiff = None

    def run_cli(
        self, reports: list[Path], output: Path, *arguments: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                *(str(path) for path in reports),
                "--output-dir",
                str(output),
                "--generated-at",
                "2026-09-02T20:00:00+00:00",
                *(str(value) for value in arguments),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_outputs_are_deterministic_redacted_and_accessible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline_path = root / "PRIVATE-SOURCE-PATH-A" / "final-report.json"
            candidate_path = root / "PRIVATE-SOURCE-PATH-B" / "final-report.json"
            write_json(baseline_path, report())
            write_json(candidate_path, report("candidate <script>alert(1)</script>"))

            output_a = root / "comparison-a"
            output_b = root / "comparison-b"
            first = self.run_cli([baseline_path, candidate_path], output_a)
            second = self.run_cli([baseline_path, candidate_path], output_b)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                {path.name for path in output_a.iterdir() if path.is_file()},
                OUTPUT_FILES,
            )
            for name in OUTPUT_FILES:
                self.assertEqual(
                    (output_a / name).read_bytes(), (output_b / name).read_bytes()
                )

            combined = b"\n".join(
                (output_a / name).read_bytes() for name in sorted(OUTPUT_FILES)
            ).decode("utf-8")
            for secret in (
                "SEALED-TASK-NAME-MUST-NOT-LEAK",
                "SEALED-SECOND-TASK-MUST-NOT-LEAK",
                "SEALED-PATH-MUST-NOT-LEAK",
                "SEALED-PROMPT-MUST-NOT-LEAK",
                "SEALED-ANSWER-MUST-NOT-LEAK",
                "PRIVATE-SOURCE-PATH-A",
                "PRIVATE-SOURCE-PATH-B",
            ):
                self.assertNotIn(secret, combined)

            normalized = json.loads(
                (output_a / "comparison-report.json").read_text("utf-8")
            )
            self.assertEqual(
                [source["locator"] for source in normalized["sourceReports"]],
                ["input-1", "input-2"],
            )
            self.assertEqual(normalized["runs"][0]["tokens"]["input"]["total"], 300)
            self.assertEqual(normalized["runs"][0]["tokens"]["cache"]["total"], 90)
            self.assertEqual(normalized["runs"][0]["tokens"]["total"]["total"], 360)

            markdown = (output_a / "comparison-report.md").read_text("utf-8")
            self.assertNotIn("<script>", markdown)
            self.assertIn(r"\<script\>", markdown)
            self.assertIn("0.500 (2/2)", markdown)

            namespace = "{http://www.w3.org/2000/svg}"
            for name in sorted(OUTPUT_FILES):
                if not name.endswith(".svg"):
                    continue
                svg = ET.parse(output_a / name).getroot()
                self.assertEqual(svg.get("role"), "img")
                self.assertEqual(svg.get("aria-labelledby"), "chart-title chart-desc")
                self.assertIsNotNone(svg.find(f"{namespace}title"))
                self.assertIsNotNone(svg.find(f"{namespace}desc"))
                self.assertFalse(svg.findall(f".//{namespace}script"))
                self.assertFalse(svg.findall(f".//{namespace}image"))
                self.assertFalse(svg.findall(f".//{namespace}foreignObject"))
                for element in svg.iter():
                    for attribute, value in element.attrib.items():
                        if attribute.endswith("href"):
                            self.assertTrue(value.startswith("#"), value)

    def test_invalid_accounting_and_timestamps_fail_closed(self) -> None:
        mutations: list[tuple[str, Any, str]] = []

        cached = report()
        for trial in cached["jobs"][0]["trials"]:
            trial["tokens"]["cachedInput"] = 1000
        mutations.append(("cached", cached, "cached input exceeds total input tokens"))

        total = report()
        total["jobs"][0]["summary"]["totalTokens"] = metric(2, 362.0)
        mutations.append(("total", total, "total tokens must equal input plus output"))

        counts = report()
        counts["jobs"][0]["summary"]["erroredTrials"] = 1
        mutations.append(("counts", counts, "must sum to completed trials"))

        coverage = report()
        coverage["jobs"][0]["summary"]["reward"] = metric(3, 1.5)
        mutations.append(("coverage", coverage, "count exceeds completedTrials"))

        malformed_alias = report()
        malformed_alias["jobs"][0]["trials"][0]["tokens"]["cache"] = []
        mutations.append(
            ("malformed-alias", malformed_alias, "tokens.cache must be a finite number")
        )

        mixed_time = report()
        mixed_time["jobs"][0]["startedAt"] += "+00:00"
        mutations.append(("mixed-time", mixed_time, "must either both include a timezone"))

        invalid_generated = report()
        invalid_generated["generatedAt"] = "not-a-timestamp"
        mutations.append(("generated", invalid_generated, "must be an ISO 8601 timestamp"))

        nonfinite = report()
        nonfinite["jobs"][0]["summary"]["costUsd"] = {
            "count": 2,
            "total": float("nan"),
            "average": float("nan"),
        }
        mutations.append(("nonfinite", nonfinite, "must be a finite number"))

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for case, value, expected_error in mutations:
                with self.subTest(case=case):
                    report_path = root / case / "final-report.json"
                    write_json(
                        report_path,
                        value,
                        allow_nan=case == "nonfinite",
                    )
                    result = self.run_cli([report_path], root / f"output-{case}")
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertIn(expected_error, result.stderr)
                    self.assertFalse((root / f"output-{case}").exists())

    def test_partial_aggregate_totals_are_labeled_with_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            value = report()
            summary = value["jobs"][0]["summary"]
            summary["reward"] = metric(1, 1.0)
            summary["totalTokens"] = metric(1, 120.0)
            summary["agentLatencyMs"] = metric(1, 1000.0)
            summary["costUsd"] = metric(1, 0.1)
            report_path = root / "report" / "final-report.json"
            write_json(report_path, value)
            output = root / "comparison"
            result = self.run_cli([report_path], output)
            self.assertEqual(result.returncode, 0, result.stderr)

            markdown = (output / "comparison-report.md").read_text("utf-8")
            for expected in (
                "1.000 (1/2)",
                "120 (1/2)",
                "0.1000 (1/2)",
                "1.0 s (1/2)",
            ):
                self.assertIn(expected, markdown)
            svg_text = (output / "resource-comparison.svg").read_text("utf-8")
            self.assertIn("120.00 (1/2)", svg_text)
            self.assertIn("$0.1000 (1/2)", svg_text)
            self.assertIn("1.00s (1/2)", svg_text)

            namespace = "{http://www.w3.org/2000/svg}"
            resource_svg = ET.parse(output / "resource-comparison.svg").getroot()
            token_row_rects = [
                element
                for element in resource_svg.findall(f".//{namespace}rect")
                if element.get("height") == "26"
            ]
            token_row_fills = {element.get("fill") for element in token_row_rects}
            self.assertIn("#1E293B", token_row_fills)
            self.assertIn("#64748B", token_row_fills)
            for component_color in ("#38BDF8", "#A78BFA", "#34D399"):
                self.assertNotIn(component_color, token_row_fills)
            gray_bars = [
                element
                for element in token_row_rects
                if element.get("fill") == "#64748B"
            ]
            self.assertEqual(len(gray_bars), 1)
            gray_x = float(gray_bars[0].get("x", "nan"))
            gray_width = float(gray_bars[0].get("width", "nan"))
            self.assertEqual(gray_x, 318.0)
            self.assertGreater(gray_width, 0.0)
            self.assertLessEqual(gray_width, 610.0)
            self.assertLessEqual(gray_x + gray_width, 928.0)

    def test_existing_outputs_require_explicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_path = root / "final-report.json"
            write_json(report_path, report())
            output = root / "comparison"
            first = self.run_cli([report_path], output)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {name: (output / name).read_bytes() for name in OUTPUT_FILES}

            refused = self.run_cli([report_path], output)
            self.assertEqual(refused.returncode, 2)
            self.assertIn("refusing to overwrite", refused.stderr)
            self.assertEqual(
                before, {name: (output / name).read_bytes() for name in OUTPUT_FILES}
            )

            replaced = self.run_cli([report_path], output, "--overwrite")
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            self.assertEqual(
                before, {name: (output / name).read_bytes() for name in OUTPUT_FILES}
            )


if __name__ == "__main__":
    unittest.main()
