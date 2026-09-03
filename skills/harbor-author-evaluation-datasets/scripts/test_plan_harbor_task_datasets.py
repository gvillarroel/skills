#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box regression tests for the Harbor dataset authoring planner."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).with_name("plan_harbor_task_datasets.py")


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def family(index: int) -> dict[str, Any]:
    family_id = f"artifact-authoring-{index}"
    return {
        "familyId": family_id,
        "sourceId": f"source-batch-{index}-2026-09",
        "templateId": f"summary-template-{index}-v1",
        "strata": {
            "capability": "artifact-authoring",
            "domain": "data-analysis",
            "difficulty": "medium",
            "resourceClass": "cpu-standard",
        },
        "cases": [
            {
                "taskId": f"{family_id}-single",
                "responseMode": "single_file",
                "variantAxes": {
                    "input_root": ["inputs", "fixtures/raw"],
                    "output_name": ["summary.md", "report.md"],
                    "output_root": ["results", "artifacts/final"],
                },
            },
            {
                "taskId": f"{family_id}-structured",
                "responseMode": "structured",
                "variantAxes": {
                    "input_root": ["data/source", "records"],
                    "output_name": ["summary.json", "report.json"],
                    "output_root": ["results", "artifacts/final"],
                },
            },
        ],
    }


def blueprint() -> dict[str, Any]:
    requirement = {
        "minimumFamilies": 1,
        "minimumTasks": 2,
        "responseModes": {"single_file": 1, "structured": 1},
        "strata": {
            "capability": {"artifact-authoring": 1},
            "domain": {"data-analysis": 1},
            "difficulty": {"medium": 1},
            "resourceClass": {"cpu-standard": 1},
        },
    }
    return {
        "schemaVersion": 1,
        "datasetId": "planner-regression-v1",
        "splitWeights": {"development": 1, "validation": 1},
        "coverageRequirements": {
            "development": copy.deepcopy(requirement),
            "validation": copy.deepcopy(requirement),
        },
        "families": [family(index) for index in range(1, 5)],
    }


def seeds() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "partitionSeed": "11" * 32,
        "variantSeeds": {
            "development": "22" * 32,
            "validation": "33" * 32,
        },
    }


class PlannerTests(unittest.TestCase):
    def run_cli(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(value) for value in arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def prepare_inputs(self, root: Path) -> tuple[Path, Path]:
        blueprint_path = root / "blueprint.json"
        seeds_path = root / "seeds.json"
        write_json(blueprint_path, blueprint())
        write_json(seeds_path, seeds())
        return blueprint_path, seeds_path

    def test_plan_is_order_independent_and_strong_verify_reproduces_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            blueprint_path, seeds_path = self.prepare_inputs(root)
            output_a = root / "plan-a"

            first = self.run_cli(
                "plan",
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                output_a,
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            shuffled = blueprint()
            shuffled["families"].reverse()
            for item in shuffled["families"]:
                item["cases"].reverse()
            shuffled_blueprint_path = root / "blueprint-shuffled.json"
            write_json(shuffled_blueprint_path, shuffled)
            output_b = root / "plan-b"
            second = self.run_cli(
                "plan",
                "--blueprint",
                shuffled_blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                output_b,
            )
            self.assertEqual(second.returncode, 0, second.stderr)

            for filename in ("plan.private.json", "summary.redacted.json"):
                self.assertEqual(
                    (output_a / filename).read_bytes(),
                    (output_b / filename).read_bytes(),
                )

            verified = self.run_cli(
                "verify",
                "--plan-dir",
                output_a,
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)
            result = json.loads(verified.stdout)
            self.assertIs(result["ok"], True)
            self.assertIs(result["sourceInputsReproduced"], True)

            private_text = (output_a / "plan.private.json").read_text("utf-8")
            summary = json.loads(
                (output_a / "summary.redacted.json").read_text("utf-8")
            )
            for raw_seed in (
                seeds()["partitionSeed"],
                *seeds()["variantSeeds"].values(),
            ):
                self.assertNotIn(raw_seed, private_text)
            self.assertNotIn("seedCommitments", summary)
            self.assertNotIn("tasks", summary)
            self.assertNotIn("families", summary)

            private_plan = json.loads(private_text)
            family_splits = {
                item["familyId"]: item["split"] for item in private_plan["families"]
            }
            self.assertEqual(set(family_splits.values()), {"development", "validation"})
            for task in private_plan["tasks"]:
                self.assertEqual(task["split"], family_splits[task["familyId"]])

    def test_existing_output_is_not_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            blueprint_path, seeds_path = self.prepare_inputs(root)
            output = root / "plan"
            arguments = (
                "plan",
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                output,
            )
            first = self.run_cli(*arguments)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {
                path.name: path.read_bytes() for path in output.iterdir() if path.is_file()
            }

            second = self.run_cli(*arguments)
            self.assertEqual(second.returncode, 2)
            self.assertIn("output already exists", second.stderr)
            after = {
                path.name: path.read_bytes() for path in output.iterdir() if path.is_file()
            }
            self.assertEqual(after, before)

    def test_tampering_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            blueprint_path, seeds_path = self.prepare_inputs(root)
            output = root / "plan"
            planned = self.run_cli(
                "plan",
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                output,
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)

            plan_path = output / "plan.private.json"
            plan = json.loads(plan_path.read_text("utf-8"))
            plan["datasetId"] = "tampered-dataset-v1"
            plan_path.write_bytes(
                (
                    json.dumps(
                        plan,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                        allow_nan=False,
                    )
                    + "\n"
                ).encode("utf-8")
            )
            verified = self.run_cli("verify", "--plan-dir", output)
            self.assertEqual(verified.returncode, 2)
            self.assertIn("integrity digest does not match", verified.stderr)

    def test_reused_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            blueprint_path = root / "blueprint.json"
            seeds_path = root / "seeds.json"
            write_json(blueprint_path, blueprint())
            invalid_seeds = seeds()
            invalid_seeds["variantSeeds"]["validation"] = invalid_seeds["partitionSeed"]
            write_json(seeds_path, invalid_seeds)
            result = self.run_cli(
                "plan",
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                root / "plan",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("partition and split variation seeds must be distinct", result.stderr)

    def test_unsatisfied_coverage_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid_blueprint = blueprint()
            invalid_blueprint["coverageRequirements"]["validation"][
                "minimumFamilies"
            ] = 4
            blueprint_path = root / "blueprint.json"
            seeds_path = root / "seeds.json"
            write_json(blueprint_path, invalid_blueprint)
            write_json(seeds_path, seeds())
            result = self.run_cli(
                "plan",
                "--blueprint",
                blueprint_path,
                "--seeds",
                seeds_path,
                "--output",
                root / "plan",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("coverage minimumFamilies exceed", result.stderr)


if __name__ == "__main__":
    unittest.main()
