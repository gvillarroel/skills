#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Tests for the sequential multi-tool TUI Harbor dataset builder."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


BUILDER_PATH = Path(__file__).with_name("build_multi_tui_harbor_dataset.py")
SPEC = importlib.util.spec_from_file_location("multi_tui_harbor_builder", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class MultiTuiHarborDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary_directory.name) / "dataset"
        completed = subprocess.run(
            [
                sys.executable,
                str(BUILDER_PATH),
                "--output-root",
                str(cls.root),
                "--run-id",
                "multi-tui-terminal-video-test",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary_directory.cleanup()

    def contracts(self) -> list[dict[str, object]]:
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self.root.glob("*/*/tests/contract.json"))
        ]

    def test_split_shape_and_multi_tool_counts(self) -> None:
        manifest = json.loads(
            (self.root / "dataset-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schemaVersion"], 3)
        self.assertEqual(
            manifest["stats"]["splitCounts"],
            {"development": 1, "validation": 1, "holdout": 1},
        )
        self.assertEqual(manifest["stats"]["multiTuiTaskCount"], 3)
        self.assertEqual(manifest["stats"]["twoToolTaskCount"], 2)
        self.assertEqual(manifest["stats"]["threeToolTaskCount"], 1)

    def test_every_contract_requires_long_ordered_multi_tui_evidence(self) -> None:
        for contract in self.contracts():
            self.assertEqual(contract["schemaVersion"], 3)
            self.assertEqual(contract["mode"], "tui-sequence")
            self.assertGreaterEqual(len(contract["sessionIds"]), 2)
            self.assertEqual(
                len(contract["sessionIds"]), len(contract["targetNames"])
            )
            self.assertEqual(
                len(contract["sessionIds"]), len(contract["executableSequence"])
            )
            self.assertGreater(float(contract["minDurationSeconds"]), 10.0)
            self.assertGreater(
                float(contract["minSourceDurationSeconds"]),
                float(contract["minDurationSeconds"]),
            )
            self.assertTrue(
                {
                    "multi-tui-sequence",
                    "multi-target-provenance",
                    "tui-session-boundaries",
                    "real-time-duration",
                }.issubset(set(contract["requiredChecks"]))
            )

    def test_validation_case_covers_three_distinct_tui_tools_and_bridge(self) -> None:
        by_id = {contract["taskId"]: contract for contract in self.contracts()}
        contract = by_id["multi-tui-val-television-fzf-lazygit"]
        self.assertEqual(
            contract["targetNames"], ["Television", "fzf", "lazygit"]
        )
        self.assertEqual(len(contract["executableSequence"]), 3)
        self.assertIn(
            "windows-working-directory-bridges", contract["requiredChecks"]
        )
        self.assertIn("before-final-key-presentation", contract["requiredChecks"])

    def test_holdout_freezes_copilot_prompt_and_final_television_target(self) -> None:
        by_id = {contract["taskId"]: contract for contract in self.contracts()}
        contract = by_id["multi-tui-holdout-copilot-television"]
        self.assertEqual(
            contract["requiredPromptSequence"], [BUILDER.HOLDOUT_COPILOT_PROMPT]
        )
        self.assertEqual(
            contract["targetNames"], ["GitHub Copilot CLI", "Television"]
        )
        self.assertEqual(contract["sessionIds"][-1], "television-final")

    def test_task_payload_and_job_configs_are_complete(self) -> None:
        for split in ("development", "validation", "holdout"):
            config = (self.root / f"{split}-job.yaml").read_text(encoding="utf-8")
            self.assertIn("WorkspaceWindowsPi", config)
            self.assertIn("n_concurrent_trials: 1", config)
            task_roots = list((self.root / split).iterdir())
            self.assertEqual(len(task_roots), 1)
            task_root = task_roots[0]
            self.assertTrue((task_root / "instruction.md").is_file())
            self.assertTrue((task_root / "tests" / "verify_task.py").is_file())
            contract = json.loads(
                (task_root / "tests" / "contract.json").read_text(encoding="utf-8")
            )
            instruction = (task_root / "instruction.md").read_text(encoding="utf-8")
            self.assertIn(json.dumps(contract, indent=2, sort_keys=True), instruction)


if __name__ == "__main__":
    unittest.main()
