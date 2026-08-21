#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Unit tests for the Harbor terminal-video evaluator."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


VERIFIER_PATH = Path(__file__).with_name("verify_task.py")
SPEC = importlib.util.spec_from_file_location("verify_task", VERIFIER_PATH)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class VerifyTaskTests(unittest.TestCase):
    def test_complexity_contract_matches_prompt_and_action_runtime(self) -> None:
        prompt = "First real prompt"
        plan = {
            "steps": [
                {"id": "prompt-one", "prompt": prompt},
                {
                    "id": "navigate",
                    "actions": [
                        {"type": "text", "text": "taz"},
                        {"type": "pause", "seconds": 5.5},
                        {"type": "key", "key": "BSpace"},
                        {"type": "key", "key": "Enter"},
                    ],
                },
            ]
        }
        runtime = {
            "steps": [
                {"prompt_sha256": VERIFIER.sha256_text(prompt)},
                {
                    "actions": [
                        {
                            "type": "text",
                            "text_sha256": VERIFIER.sha256_text("taz"),
                        },
                        {"type": "pause", "seconds": 5.5},
                        {"type": "key", "key": "BSpace"},
                        {"type": "key", "key": "Enter"},
                    ]
                },
            ]
        }
        contract = {
            "requiredPromptSequence": [prompt],
            "requiredTextSequence": ["taz"],
            "requiredKeySequence": ["BSpace", "Enter"],
            "minActionCount": 4,
            "minPauseActionCount": 1,
            "minPlannedPauseSeconds": 5.0,
            "minSourceDurationSeconds": 12.0,
        }
        findings: list[str] = []
        ok, evidence = VERIFIER.verify_complexity_contract(
            contract,
            plan,
            runtime,
            {"recording": {"duration_seconds": 12.5}},
            findings,
        )
        self.assertTrue(ok)
        self.assertEqual(findings, [])
        self.assertEqual(evidence["observed"]["actionCount"], 4)

    def test_complexity_contract_rejects_short_or_changed_runtime(self) -> None:
        plan = {
            "steps": [
                {
                    "id": "navigate",
                    "actions": [
                        {"type": "pause", "seconds": 2.0},
                        {"type": "key", "key": "Enter"},
                    ],
                }
            ]
        }
        runtime = {
            "steps": [
                {
                    "actions": [
                        {"type": "pause", "seconds": 1.0},
                        {"type": "key", "key": "Escape"},
                    ]
                }
            ]
        }
        findings: list[str] = []
        ok, evidence = VERIFIER.verify_complexity_contract(
            {
                "requiredKeySequence": ["Enter"],
                "minActionCount": 3,
                "minPauseActionCount": 2,
                "minPlannedPauseSeconds": 10.0,
                "minSourceDurationSeconds": 10.0,
            },
            plan,
            runtime,
            {"recording": {"duration_seconds": 4.0}},
            findings,
        )
        self.assertFalse(ok)
        self.assertFalse(evidence["checks"]["runtimeMatchesPlan"])
        self.assertFalse(evidence["checks"]["sourceDuration"])
        self.assertGreaterEqual(len(findings), 5)

    def test_legacy_contract_has_no_complexity_requirements(self) -> None:
        findings: list[str] = []
        ok, evidence = VERIFIER.verify_complexity_contract(
            {}, {"steps": []}, {"steps": []}, {}, findings
        )
        self.assertTrue(ok)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertEqual(findings, [])

    def test_argv_exit_status_uses_runtime_steps(self) -> None:
        runtime = {
            "steps": [
                {
                    "status": "passed",
                    "exit_code": 0,
                    "expected_exit_codes": [0],
                }
            ]
        }
        self.assertTrue(VERIFIER.runtime_exit_ok("argv", runtime, {}, 1))
        runtime["steps"][0]["exit_code"] = 1
        self.assertFalse(VERIFIER.runtime_exit_ok("argv", runtime, {}, 1))

    def test_tui_exit_status_uses_target_final_exit(self) -> None:
        self.assertTrue(VERIFIER.runtime_exit_ok("tui", {}, {"final_exit_code": 0}, 2))
        self.assertFalse(VERIFIER.runtime_exit_ok("tui", {}, {"final_exit_code": 1}, 2))

    def test_effective_checks_normalize_argv_contract_terms(self) -> None:
        checks = VERIFIER.effective_validation_checks(
            {
                "checks": ["exit-codes"],
                "presentation": {"source_cast_duration_seconds": 1.25},
            }
        )
        self.assertTrue({"exit-codes", "target-exit", "real-time-duration"} <= checks)

    def test_effective_checks_normalize_legacy_before_final_key_label(self) -> None:
        checks = VERIFIER.effective_validation_checks(
            {
                "checks": ["before-final-key-presentation"],
                "presentation": {
                    "start_at": "tui-ready",
                    "source_cast_duration_seconds": 15.0,
                },
            }
        )
        self.assertIn("tui-ready-presentation", checks)

    def test_collected_artifact_workspace_wins_over_empty_app(self) -> None:
        required = ["source/session-plan.json", "deliverables/session.mp4"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            app = root / "app"
            artifacts = root / "artifacts"
            app.mkdir()
            for relative in required:
                path = artifacts / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("evidence", encoding="utf-8")
            with mock.patch.dict(
                os.environ,
                {
                    "HARBOR_APP_DIR": str(app),
                    "HARBOR_ARTIFACT_DIR": str(artifacts),
                },
                clear=False,
            ):
                selected = VERIFIER.select_workspace({"requiredFiles": required})
            self.assertEqual(selected, artifacts.resolve())

    def test_complete_app_workspace_wins_a_tie(self) -> None:
        required = ["source/session-plan.json", "deliverables/session.mp4"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            app = root / "app"
            artifacts = root / "artifacts"
            for candidate in (app, artifacts):
                for relative in required:
                    path = candidate / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("evidence", encoding="utf-8")
            with mock.patch.dict(
                os.environ,
                {
                    "HARBOR_APP_DIR": str(app),
                    "HARBOR_ARTIFACT_DIR": str(artifacts),
                },
                clear=False,
            ):
                selected = VERIFIER.select_workspace({"requiredFiles": required})
            self.assertEqual(selected, app.resolve())

    def test_wsl_media_path_is_translated_only_for_windows_executable(self) -> None:
        source = Path("/mnt/c/Users/test/session.mp4")
        self.assertEqual(
            VERIFIER.media_input_path(source, "/tools/ffprobe.exe"),
            r"C:\Users\test\session.mp4",
        )
        self.assertEqual(
            VERIFIER.media_input_path(source, "/usr/bin/ffprobe"),
            str(source),
        )

    def test_before_final_key_target_only_presentation_requires_cast_checks(self) -> None:
        manifest = {
            "presentation": {
                "start_at": "tui-ready",
                "end_at": "before-final-key",
                "trim_leading_seconds": 1.0,
                "trim_trailing_seconds": 2.0,
                "final_hold_seconds": 2.0,
                "final_key_marker_seconds": 3.0,
            }
        }
        required = {
            "before-final-key-marker",
            "before-final-key-presentation",
        }
        self.assertTrue(VERIFIER.target_only_presentation_ok(manifest, required))
        self.assertFalse(
            VERIFIER.target_only_presentation_ok(
                manifest, {"before-final-key-marker"}
            )
        )

    def test_tui_exit_target_only_presentation_remains_supported(self) -> None:
        manifest = {
            "presentation": {
                "start_at": "tui-ready",
                "end_at": "tui-exit",
                "trim_leading_seconds": 1.0,
                "trim_trailing_seconds": 0.1,
                "final_hold_seconds": 0.5,
                "terminal_restore_seconds": 4.0,
            }
        }
        self.assertTrue(VERIFIER.target_only_presentation_ok(manifest, set()))


if __name__ == "__main__":
    unittest.main()
