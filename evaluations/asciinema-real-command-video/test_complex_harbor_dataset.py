#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Tests for the complex and long-form Harbor dataset builder."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


BUILDER_PATH = Path(__file__).with_name("build_complex_harbor_dataset.py")
SPEC = importlib.util.spec_from_file_location("complex_harbor_builder", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class ComplexHarborDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        external_root = os.environ.get(
            "ASCIINEMA_VIDEO_COMPLEX_HARBOR_DATASET_ROOT"
        )
        if external_root:
            cls.temporary_directory = None
            cls.root = Path(external_root).resolve()
            return
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary_directory.name) / "dataset"
        completed = subprocess.run(
            [
                sys.executable,
                str(BUILDER_PATH),
                "--output-root",
                str(cls.root),
                "--run-id",
                "complex-terminal-video-test",
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
        if cls.temporary_directory is not None:
            cls.temporary_directory.cleanup()

    def contracts(self) -> list[dict[str, object]]:
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self.root.glob("*/*/tests/contract.json"))
        ]

    def test_split_shape_and_complexity_counts(self) -> None:
        manifest = json.loads(
            (self.root / "dataset-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(
            manifest["stats"]["splitCounts"],
            {"development": 3, "validation": 3, "holdout": 3},
        )
        self.assertEqual(manifest["stats"]["longVideoTaskCount"], 8)
        self.assertEqual(manifest["stats"]["explicitActionTaskCount"], 5)
        self.assertEqual(manifest["stats"]["multiStepTaskCount"], 2)

    def test_long_videos_also_require_long_source_casts(self) -> None:
        long_contracts = [
            contract
            for contract in self.contracts()
            if float(contract["minDurationSeconds"]) > 10.0
        ]
        self.assertEqual(len(long_contracts), 8)
        for contract in long_contracts:
            self.assertGreater(float(contract["minSourceDurationSeconds"]), 10.0)
            self.assertEqual(contract["fps"], 30)

    def test_explicit_tuis_freeze_exact_key_and_pause_sequences(self) -> None:
        action_contracts = [
            contract for contract in self.contracts() if int(contract["minActionCount"]) > 0
        ]
        self.assertEqual(len(action_contracts), 5)
        for contract in action_contracts:
            self.assertGreaterEqual(int(contract["minPauseActionCount"]), 4)
            self.assertGreaterEqual(float(contract["minPlannedPauseSeconds"]), 10.0)
            self.assertTrue(contract["requiredKeySequence"])
            self.assertIn("command-keys", contract["requiredChecks"])

    def test_prompt_sequences_are_exact_for_multi_step_tasks(self) -> None:
        by_id = {contract["taskId"]: contract for contract in self.contracts()}
        self.assertEqual(
            by_id["complex-dev-copilot-three-prompt-tui"]["requiredPromptSequence"],
            BUILDER.COPILOT_PROMPTS,
        )
        self.assertEqual(
            by_id["complex-val-gh-three-repository-argv"]["requiredPromptSequence"],
            BUILDER.GH_REPOSITORIES,
        )

    def test_task_payload_and_job_configs_are_complete(self) -> None:
        for split in ("development", "validation", "holdout"):
            config = (self.root / f"{split}-job.yaml").read_text(encoding="utf-8")
            self.assertIn("WorkspaceWindowsPi", config)
            self.assertIn("n_concurrent_trials: 1", config)
            self.assertIn("thinking: high", config)
            for task_root in (self.root / split).iterdir():
                self.assertTrue((task_root / "instruction.md").is_file())
                self.assertTrue((task_root / "task.toml").is_file())
                self.assertTrue((task_root / "tests" / "verify_task.py").is_file())
                instruction = (task_root / "instruction.md").read_text(encoding="utf-8")
                contract = json.loads(
                    (task_root / "tests" / "contract.json").read_text(encoding="utf-8")
                )
                self.assertIn(json.dumps(contract, indent=2, sort_keys=True), instruction)

    def test_holdout_is_long_and_requires_path_bridge_evidence(self) -> None:
        holdout = [
            contract for contract in self.contracts() if contract["split"] == "holdout"
        ]
        self.assertEqual(len(holdout), 3)
        self.assertTrue(
            all(float(contract["minDurationSeconds"]) > 10.0 for contract in holdout)
        )
        by_id = {contract["taskId"]: contract for contract in holdout}
        lazygit = by_id["complex-holdout-lazygit-deep-path-tui"]
        self.assertIn(
            "windows-working-directory-bridge", lazygit["requiredChecks"]
        )
        self.assertIn("lazygit-path-clean", lazygit["requiredChecks"])
        self.assertIn("lazygit-project-longpaths", lazygit["requiredChecks"])

    def test_no_task_authorizes_mutation_or_contains_credentials(self) -> None:
        for contract in self.contracts():
            self.assertEqual(contract["authorizedMutation"], "none")
        for path in self.root.rglob("*"):
            if path.is_file():
                payload = path.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn("OPENAI_API_KEY=", payload)
                self.assertNotIn("ghp_", payload)


if __name__ == "__main__":
    unittest.main()
