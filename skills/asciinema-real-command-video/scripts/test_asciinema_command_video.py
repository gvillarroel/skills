#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the Asciinema real-command video pipeline."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
MODULE_PATH = Path(__file__).with_name("asciinema_command_video.py")
SPEC = importlib.util.spec_from_file_location("asciinema_command_video", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def base_plan(executable: str, helper: str | None = None) -> dict[str, object]:
    args = ["{prompt}"] if helper is None else [helper, "{prompt}", "observed.txt"]
    return {
        "schema_version": 1,
        "title": "Real command test",
        "working_directory": ".",
        "declared_scope": "Local test files only.",
        "target": {
            "name": "Python",
            "executable": executable,
            "version_args": ["--version"],
        },
        "terminal": {"cols": 80, "rows": 24},
        "render": {
            "theme": "github-dark",
            "font_size": 16,
            "line_height": 1.4,
            "fps": 24,
            "speed": 1.0,
            "idle_time_limit": 1.0,
            "last_frame_duration": 1.0,
        },
        "steps": [
            {
                "id": "prompt-1",
                "prompt": "alpha",
                "args": args,
                "timeout_seconds": 30,
                "pause_after_seconds": 0.0,
                "expected_exit_codes": [0],
            }
        ],
    }


def tui_plan(executable: str) -> dict[str, object]:
    payload = base_plan(executable)
    payload["render"]["idle_time_limit"] = None
    payload["interaction"] = {
        "mode": "tui",
        "launch_args": ["--session", "{run_id}"],
        "typing_interval_seconds": 0.02,
        "pre_submit_pause_seconds": 0.1,
        "startup_timeout_seconds": 30,
        "ready_pattern": r"(?m)^READY>\s*$",
        "busy_pattern": r"(?m)^BUSY$",
        "settle_seconds": 0.25,
        "exit_text": "/exit",
        "exit_timeout_seconds": 30,
        "expected_exit_codes": [0],
    }
    del payload["steps"][0]["args"]
    del payload["steps"][0]["expected_exit_codes"]
    return payload


def one_shot_tui_plan(executable: str, actions: list[dict[str, object]]) -> dict[str, object]:
    payload = tui_plan(executable)
    payload["interaction"]["shutdown_mode"] = "target-exit"
    del payload["interaction"]["exit_text"]
    payload["steps"] = [
        {
            "id": "interaction-1",
            "actions": actions,
            "completion": "target-exit",
            "timeout_seconds": 30,
            "pause_after_seconds": 0.0,
        }
    ]
    return payload


def multi_tui_plan(
    first_executable: str = "first-tui",
    second_executable: str = "second-tui",
) -> dict[str, object]:
    first = one_shot_tui_plan(
        first_executable,
        [
            {"type": "pause", "seconds": 0.25},
            {"type": "key", "key": "q"},
        ],
    )
    second = one_shot_tui_plan(
        second_executable,
        [
            {"type": "text", "text": "beta"},
            {"type": "pause", "seconds": 0.25},
            {"type": "key", "key": "Enter"},
        ],
    )
    return {
        "schema_version": 1,
        "title": "Real multi-tool TUI test",
        "working_directory": ".",
        "declared_scope": "Two installed TUI tools and local fixture files only.",
        "terminal": first["terminal"],
        "render": first["render"],
        "tui_sessions": [
            {
                "id": "first-tool",
                "target": first["target"],
                "interaction": first["interaction"],
                "steps": first["steps"],
            },
            {
                "id": "second-tool",
                "target": second["target"],
                "interaction": second["interaction"],
                "steps": [
                    {**second["steps"][0], "id": "interaction-2"},
                ],
            },
        ],
    }


class PlanValidationTests(unittest.TestCase):
    def test_windows_subcommand_help_does_not_require_or_forward_a_plan(self) -> None:
        with mock.patch.object(MODULE, "forward_windows_command_to_wsl") as forward:
            with self.assertRaises(SystemExit) as raised, redirect_stdout(io.StringIO()):
                MODULE.main(["record", "--help"])
        self.assertEqual(raised.exception.code, 0)
        forward.assert_not_called()

    def test_bundled_lazygit_template_is_valid_from_source_directory(self) -> None:
        template_path = MODULE_PATH.parents[1] / "assets" / "templates" / "lazygit-session-plan.json"
        payload = json.loads(template_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "fixture" / "repo").mkdir(parents=True)
            plan_path = root / "source" / "session-plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
        self.assertEqual(plan.working_directory, (root / "fixture" / "repo").resolve())
        self.assertEqual(MODULE.render_end_at(plan), "before-final-key")
        self.assertEqual(plan.data["steps"][0]["actions"][-1]["key"], "q")
        self.assertEqual(
            plan.data["interaction"]["launch_args"],
            [
                "--use-config-dir",
                "{windows_working_directory}.git/lazygit-config",
                "--path",
                "{windows_working_directory}",
            ],
        )

    def test_bundled_lazygit_config_suppresses_dynamic_startup_ui(self) -> None:
        config_path = MODULE_PATH.parents[1] / "assets" / "templates" / "lazygit-config.yml"
        config = config_path.read_text(encoding="utf-8")
        self.assertIn("disableStartupPopups: true\n", config)
        self.assertIn("update:\n  method: never\n", config)
        self.assertIn("git:\n  autoFetch: false\n", config)
        self.assertNotIn("gui:\n  disableStartupPopups:", config)

    def test_bundled_multi_tui_template_is_valid_and_long_running(self) -> None:
        template_path = (
            MODULE_PATH.parents[1]
            / "assets"
            / "templates"
            / "multi-tui-session-plan.json"
        )
        plan = MODULE.load_plan(template_path)
        pauses = [
            float(action["seconds"])
            for step in MODULE.plan_steps(plan)
            for action in step.get("actions", [])
            if action["type"] == "pause"
        ]
        self.assertEqual(MODULE.plan_mode(plan), "tui-sequence")
        self.assertEqual(len(MODULE.plan_targets(plan)), 2)
        self.assertGreater(sum(pauses), 10.0)

    def test_bundled_direct_argv_template_omits_interaction(self) -> None:
        template_path = (
            MODULE_PATH.parents[1]
            / "assets"
            / "templates"
            / "direct-argv-session-plan.json"
        )
        plan = MODULE.load_plan(template_path)
        self.assertEqual(MODULE.plan_mode(plan), "argv")
        self.assertNotIn("interaction", plan.data)
        self.assertEqual(plan.data["target"]["executable"], "python3")

    def test_valid_plan_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(base_plan(sys.executable)), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            summary = MODULE.plan_summary(plan)
            self.assertEqual(summary["status"], "passed")
            self.assertEqual(summary["prompt_count"], 1)
            self.assertEqual(summary["working_directory"], str(root.resolve()))

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "Duplicate JSON key"):
                MODULE.load_json(path)

    def test_missing_prompt_placeholder_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = base_plan(sys.executable)
            payload["steps"][0]["args"] = ["literal"]
            path = root / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "exactly once"):
                MODULE.load_plan(path)

    def test_literal_python_f_string_braces_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = base_plan(sys.executable)
            payload["steps"][0]["args"] = [
                "-c",
                "h='abc'; wc=3; print(f'{h}:{wc}')",
                "{prompt}",
            ]
            path = root / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(path)
            argv = MODULE.expanded_step_argv(
                Path(sys.executable), plan.data["steps"][0]["args"], "alpha", str(uuid.uuid4())
            )
            self.assertEqual(argv[2], "h='abc'; wc=3; print(f'{h}:{wc}')")

    def test_probable_secret_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = base_plan(sys.executable)
            payload["steps"][0]["prompt"] = "Use token=github_pat_abcdefghijklmnopqrstuvwxyz123456"
            path = root / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "credential or secret"):
                MODULE.load_plan(path)

    def test_valid_tui_plan_uses_persistent_interaction_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(tui_plan(sys.executable)), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            summary = MODULE.plan_summary(plan)
            self.assertEqual(MODULE.plan_mode(plan), "tui")
            self.assertEqual(summary["mode"], "tui")
            self.assertIsNone(summary["render"]["idle_time_limit"])
            self.assertNotIn("args", plan.data["steps"][0])

    def test_multi_tui_plan_requires_and_summarizes_distinct_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "multi-tui.json"
            path.write_text(json.dumps(multi_tui_plan()), encoding="utf-8")
            plan = MODULE.load_plan(path)
            summary = MODULE.plan_summary(plan)
            self.assertEqual(MODULE.plan_mode(plan), "tui-sequence")
            self.assertEqual(summary["tui_session_count"], 2)
            self.assertEqual(summary["prompt_count"], 2)
            self.assertEqual(
                [session["id"] for session in summary["tui_sessions"]],
                ["first-tool", "second-tool"],
            )
            self.assertEqual(len(summary["targets"]), 2)

    def test_multi_tui_plan_rejects_one_repeated_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "multi-tui.json"
            path.write_text(
                json.dumps(multi_tui_plan("same-tui", "same-tui")),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MODULE.CommandVideoError, "two distinct target executables"
            ):
                MODULE.load_plan(path)

    def test_multi_tui_plan_rejects_duplicate_step_ids_across_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            payload = multi_tui_plan()
            payload["tui_sessions"][1]["steps"][0]["id"] = "interaction-1"
            path = Path(temp) / "multi-tui.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.CommandVideoError, "Duplicate step id across TUI sessions"
            ):
                MODULE.load_plan(path)

    def test_windows_working_directory_token_requires_windows_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            payload["target"]["executable"] = "python"
            payload["interaction"]["launch_args"] = [
                "--path",
                "{windows_working_directory}",
            ]
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.CommandVideoError, "native Windows .exe target"
            ):
                MODULE.load_plan(plan_path)

    def test_windows_working_directory_token_requires_and_uses_bridge(self) -> None:
        args = [
            "--use-config-dir",
            "{windows_working_directory}.git/lazygit-config",
            "--path",
            "{windows_working_directory}",
            "--session",
            "{run_id}",
        ]
        with self.assertRaisesRegex(
            MODULE.CommandVideoError, "no verified Windows path bridge"
        ):
            MODULE.expanded_launch_argv(Path("lazygit.exe"), args, "run-123")
        argv = MODULE.expanded_launch_argv(
            Path("lazygit.exe"),
            args,
            "run-123",
            windows_working_directory="Z:/",
        )
        self.assertEqual(
            argv,
            [
                "lazygit.exe",
                "--use-config-dir",
                "Z:/.git/lazygit-config",
                "--path",
                "Z:/",
                "--session",
                "run-123",
            ],
        )

    def test_tui_steps_reject_direct_argv_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            payload["steps"][0]["args"] = ["{prompt}"]
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "unknown fields"):
                MODULE.load_plan(plan_path)

    def test_tui_requires_uncapped_real_time_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            payload["render"]["idle_time_limit"] = 1.0
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "preserve real timing"):
                MODULE.load_plan(plan_path)

    def test_tui_ready_presentation_is_valid_only_for_tui_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            payload["render"]["start_at"] = "tui-ready"
            plan_path = root / "tui-plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            self.assertEqual(MODULE.render_start_at(plan), "tui-ready")

            argv_payload = base_plan(sys.executable)
            argv_payload["render"]["start_at"] = "tui-ready"
            argv_path = root / "argv-plan.json"
            argv_path.write_text(json.dumps(argv_payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "requires TUI"):
                MODULE.load_plan(argv_path)

    def test_tui_ready_state_must_not_also_be_busy(self) -> None:
        ready_pattern = r"(?m)^READY>\s*$"
        busy_pattern = r"(?m)^BUSY$"
        screen = "answer\nREADY>\nBUSY\n"
        self.assertTrue(MODULE.screen_matches_ready(screen, ready_pattern))
        self.assertTrue(MODULE.screen_matches_busy(screen, busy_pattern))

    def test_one_shot_text_and_enter_actions_are_first_class(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = one_shot_tui_plan(
                sys.executable,
                [
                    {"type": "text", "text": "beta"},
                    {"type": "pause", "seconds": 0.25},
                    {"type": "key", "key": "Enter"},
                ],
            )
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            summary = MODULE.plan_summary(plan)
            self.assertEqual(MODULE.tui_shutdown_mode(plan), "target-exit")
            self.assertEqual(summary["action_count"], 3)
            self.assertEqual(summary["text_prompt_count"], 0)
            self.assertEqual(summary["steps"][0]["completion"], "target-exit")

    def test_raw_command_key_action_does_not_invent_enter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = one_shot_tui_plan(
                sys.executable,
                [
                    {"type": "pause", "seconds": 2.0},
                    {"type": "key", "key": "q"},
                ],
            )
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            self.assertEqual(plan.data["steps"][0]["actions"][-1]["key"], "q")
            self.assertFalse(
                any(
                    action.get("key") == "Enter"
                    for action in plan.data["steps"][0]["actions"]
                )
            )

    def test_before_final_key_requires_target_exit_final_key_and_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = one_shot_tui_plan(
                sys.executable,
                [
                    {"type": "pause", "seconds": 0.25},
                    {"type": "key", "key": "q"},
                ],
            )
            payload["render"]["start_at"] = "tui-ready"
            payload["render"]["end_at"] = "before-final-key"
            payload["render"]["last_frame_duration"] = 2.0
            plan_path = root / "valid.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            self.assertEqual(MODULE.render_end_at(plan), "before-final-key")

            invalid = copy.deepcopy(payload)
            invalid["steps"][0]["actions"].append({"type": "pause", "seconds": 0.25})
            invalid_path = root / "invalid-final-action.json"
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "final action is a key"):
                MODULE.load_plan(invalid_path)

            no_hold = copy.deepcopy(payload)
            no_hold["render"]["last_frame_duration"] = 0.0
            no_hold_path = root / "invalid-hold.json"
            no_hold_path.write_text(json.dumps(no_hold), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "positive last_frame_duration"):
                MODULE.load_plan(no_hold_path)

    def test_before_final_key_is_rejected_for_direct_argv(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = base_plan(sys.executable)
            payload["render"]["end_at"] = "before-final-key"
            plan_path = root / "argv-plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "requires TUI"):
                MODULE.load_plan(plan_path)

    def test_target_exit_completion_requires_matching_shutdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            payload["steps"] = [
                {
                    "id": "quit",
                    "actions": [{"type": "key", "key": "q"}],
                    "completion": "target-exit",
                    "timeout_seconds": 30,
                    "pause_after_seconds": 0.0,
                }
            ]
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "shutdown_mode"):
                MODULE.load_plan(plan_path)

    def test_unsupported_tmux_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = one_shot_tui_plan(
                sys.executable, [{"type": "key", "key": "-t"}]
            )
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "supported named key"):
                MODULE.load_plan(plan_path)


class VideoBundleTests(unittest.TestCase):
    def initialize_bundle(self, root: Path, name: str = "first-video") -> object:
        directory = root / name
        MODULE.initialize_video_directory(directory, template_name="single-tui")
        return MODULE.video_bundle_paths(directory)

    def write_matching_preflight(self, paths: object) -> object:
        plan = MODULE.load_plan(paths.plan)
        MODULE.write_json_atomic(
            paths.preflight,
            {
                "schema_version": 1,
                "status": "passed",
                "plan": str(plan.path),
                "plan_sha256": plan.sha256,
                "video_id": paths.directory.name,
                "video_directory": str(paths.directory),
            },
        )
        return plan

    def test_init_video_creates_one_fresh_fixed_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "first-video"
            result = MODULE.initialize_video_directory(
                directory, template_name="single-tui"
            )
            paths = MODULE.video_bundle_paths(directory)
            template = (
                MODULE.SKILL_ROOT
                / "assets"
                / "templates"
                / "session-plan.json"
            )
            self.assertEqual(paths.plan.read_bytes(), template.read_bytes())
            self.assertEqual(result["video_id"], "first-video")
            self.assertEqual(
                {Path(path).parent for path in result["artifact_layout"].values()},
                {directory.resolve()},
            )
            with self.assertRaisesRegex(MODULE.CommandVideoError, "Refusing to reuse"):
                MODULE.initialize_video_directory(
                    directory, template_name="single-tui"
                )

    def test_init_video_supports_a_valid_direct_argv_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "direct-command"
            MODULE.initialize_video_directory(
                directory, template_name="direct-argv"
            )
            plan = MODULE.load_plan(directory / "session-plan.json")
            self.assertEqual(MODULE.plan_mode(plan), "argv")
            self.assertNotIn("interaction", plan.data)

    def test_video_directory_requires_lowercase_hyphen_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(MODULE.CommandVideoError, "hyphen-case"):
                MODULE.initialize_video_directory(
                    Path(temp) / "First Video", template_name="single-tui"
                )

    def test_preflight_video_writes_and_refreshes_only_before_recording(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            paths = self.initialize_bundle(Path(temp))
            plan = MODULE.load_plan(paths.plan)
            preflight_result = {
                "schema_version": 1,
                "status": "passed",
                "plan": str(plan.path),
                "plan_sha256": plan.sha256,
            }
            args = MODULE.argparse.Namespace(video_directory=str(paths.directory))
            with mock.patch.object(
                MODULE, "preflight_session", return_value=preflight_result
            ) as preflight:
                first = MODULE.preflight_video_bundle(args)
                second = MODULE.preflight_video_bundle(args)
            self.assertEqual(preflight.call_count, 2)
            self.assertEqual(first["preflight_report"], str(paths.preflight))
            self.assertEqual(second["video_directory"], str(paths.directory))
            self.assertEqual(MODULE.load_json(paths.preflight)["status"], "passed")
            paths.cast.write_text("recording evidence", encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.CommandVideoError, "cannot change after recording evidence"
            ):
                MODULE.preflight_video_bundle(args)

    def test_record_video_derives_every_output_from_its_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            paths = self.initialize_bundle(Path(temp))
            plan = self.write_matching_preflight(paths)
            args = MODULE.argparse.Namespace(
                video_directory=str(paths.directory), retain_gif=False
            )

            def fake_record(forwarded: object) -> dict[str, object]:
                derived = {
                    "plan": Path(forwarded.plan),
                    "cast": Path(forwarded.cast),
                    "mp4": Path(forwarded.mp4),
                    "manifest": Path(forwarded.manifest),
                    "runtime_report": Path(forwarded.runtime_report),
                }
                self.assertEqual(
                    {path.parent for path in derived.values()}, {paths.directory}
                )
                self.assertEqual(derived["plan"], paths.plan)
                self.assertEqual(derived["cast"], paths.cast)
                self.assertEqual(derived["mp4"], paths.mp4)
                self.assertEqual(derived["manifest"], paths.manifest)
                self.assertEqual(derived["runtime_report"], paths.runtime_report)
                self.assertIsNone(forwarded.gif)
                return {
                    "schema_version": 1,
                    "status": "passed",
                    "plan": str(plan.path),
                    "plan_sha256": plan.sha256,
                }

            with mock.patch.object(MODULE, "record_session", side_effect=fake_record):
                result = MODULE.record_video_bundle(args)
            self.assertEqual(result["record_result"], str(paths.record_result))
            self.assertTrue(paths.record_result.is_file())
            with self.assertRaisesRegex(MODULE.CommandVideoError, "Refusing to overwrite"):
                MODULE.record_video_bundle(args)

    def test_record_video_rejects_a_plan_changed_after_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            paths = self.initialize_bundle(Path(temp))
            self.write_matching_preflight(paths)
            payload = MODULE.load_json(paths.plan)
            payload["title"] = "Changed after preflight"
            paths.plan.write_text(json.dumps(payload), encoding="utf-8")
            args = MODULE.argparse.Namespace(
                video_directory=str(paths.directory), retain_gif=False
            )
            with self.assertRaisesRegex(MODULE.CommandVideoError, "plan changed"):
                MODULE.record_video_bundle(args)

    def test_validate_video_seals_only_sibling_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            paths = self.initialize_bundle(Path(temp))
            plan = self.write_matching_preflight(paths)
            paths.recording_attempt.write_text("attempt", encoding="utf-8")
            paths.cast.write_text("cast", encoding="utf-8")
            paths.runtime_report.write_text("runtime", encoding="utf-8")
            paths.mp4.write_bytes(b"mp4")
            paths.manifest.write_text("manifest", encoding="utf-8")
            MODULE.write_json_atomic(
                paths.record_result,
                {
                    "schema_version": 1,
                    "status": "passed",
                    "plan": str(paths.plan),
                    "plan_sha256": plan.sha256,
                    "video_directory": str(paths.directory),
                },
            )
            validation = {
                "schema_version": 1,
                "status": "passed",
                "run_id": str(uuid.uuid4()),
                "checks": {"manifest": "passed"},
            }
            args = MODULE.argparse.Namespace(
                video_directory=str(paths.directory),
                tools_dir=None,
                ffprobe="ffprobe",
            )
            with mock.patch.object(
                MODULE, "validate_existing_artifacts", return_value=validation
            ):
                result = MODULE.validate_video_bundle(args)
            index = MODULE.load_json(paths.bundle_index)
            self.assertEqual(result["bundle_artifact_count"], 9)
            self.assertEqual(index["artifact_count"], 9)
            self.assertEqual(
                set(index["artifacts"]),
                {
                    "plan",
                    "preflight",
                    "recording_attempt",
                    "cast",
                    "runtime_report",
                    "mp4",
                    "manifest",
                    "record_result",
                    "validation",
                },
            )
            for artifact in index["artifacts"].values():
                self.assertNotIn("/", artifact["relative_path"])
                self.assertNotIn("\\", artifact["relative_path"])
                self.assertEqual(Path(artifact["path"]).parent, paths.directory)
            with self.assertRaisesRegex(MODULE.CommandVideoError, "Refusing to overwrite"):
                MODULE.validate_video_bundle(args)

    def test_batch_audit_detects_cross_directory_artifact_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundles = [
                self.initialize_bundle(root, "first-video"),
                self.initialize_bundle(root, "second-video"),
            ]
            for paths in bundles:
                for key, filename in MODULE.VIDEO_BUNDLE_FILENAMES.items():
                    if key in {"plan", "bundle_index", "gif_intermediary"}:
                        continue
                    (paths.directory / filename).write_text(key, encoding="utf-8")
                artifacts = {
                    key: MODULE.video_bundle_artifact_record(
                        getattr(paths, key), directory=paths.directory
                    )
                    for key in MODULE.VIDEO_BUNDLE_FILENAMES
                    if key not in {"bundle_index", "gif_intermediary"}
                }
                MODULE.write_json_atomic(
                    paths.bundle_index,
                    {
                        "schema_version": 1,
                        "status": "passed",
                        "video_id": paths.directory.name,
                        "video_directory": str(paths.directory),
                        "artifact_count": len(artifacts),
                        "run_id": str(uuid.uuid4()),
                        "artifacts": artifacts,
                    },
                )
            args = MODULE.argparse.Namespace(
                video_directories=[str(paths.directory) for paths in bundles]
            )
            result = MODULE.audit_video_bundles(args)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["video_count"], 2)
            self.assertEqual(result["video_ids"], ["first-video", "second-video"])

            second_index = MODULE.load_json(bundles[1].bundle_index)
            second_index["artifacts"]["cast"]["path"] = str(bundles[0].cast)
            MODULE.write_json_atomic(bundles[1].bundle_index, second_index)
            with self.assertRaisesRegex(MODULE.CommandVideoError, "points outside"):
                MODULE.audit_video_bundles(args)


class DirectExecutionTests(unittest.TestCase):
    def test_prompt_metacharacters_remain_one_real_argv_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            helper = root / "target.py"
            helper.write_text(
                "from pathlib import Path\n"
                "import sys\n"
                "Path(sys.argv[2]).write_text(sys.argv[1], encoding='utf-8')\n"
                "print('REAL_TARGET:' + sys.argv[1])\n",
                encoding="utf-8",
            )
            payload = base_plan(sys.executable, str(helper))
            prompt = "alpha; touch should-not-exist && echo injected"
            payload["steps"][0]["prompt"] = prompt
            plan_path = root / "plan.json"
            report_path = root / "runtime.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            run_id = str(uuid.uuid4())
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = MODULE.execute_plan(
                    plan,
                    report_path=report_path,
                    run_id=run_id,
                    env=os.environ,
                    require_asciinema_session=False,
                    require_tty=False,
                )
            self.assertEqual(code, 0)
            self.assertEqual((root / "observed.txt").read_text(encoding="utf-8"), prompt)
            self.assertFalse((root / "should-not-exist").exists())
            report = MODULE.load_json(report_path)
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["steps"][0]["prompt_sha256"], MODULE.sha256_text(prompt))

    def test_unexpected_exit_stops_later_real_processes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            helper = root / "target.py"
            helper.write_text(
                "from pathlib import Path\n"
                "import sys\n"
                "path = Path('calls.txt')\n"
                "path.write_text((path.read_text() if path.exists() else '') + sys.argv[1] + '\\n')\n"
                "raise SystemExit(7 if sys.argv[1] == 'first' else 0)\n",
                encoding="utf-8",
            )
            payload = base_plan(sys.executable, str(helper))
            payload["steps"][0]["args"] = [str(helper), "{prompt}"]
            payload["steps"][0]["prompt"] = "first"
            second = copy.deepcopy(payload["steps"][0])
            second["id"] = "prompt-2"
            second["prompt"] = "second"
            payload["steps"].append(second)
            plan_path = root / "plan.json"
            report_path = root / "runtime.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = MODULE.execute_plan(
                    MODULE.load_plan(plan_path),
                    report_path=report_path,
                    run_id=str(uuid.uuid4()),
                    env=os.environ,
                    require_asciinema_session=False,
                    require_tty=False,
                )
            self.assertEqual(code, 1)
            self.assertEqual((root / "calls.txt").read_text(encoding="utf-8"), "first\n")
            report = MODULE.load_json(report_path)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(len(report["steps"]), 1)
            self.assertEqual(report["steps"][0]["exit_code"], 7)

    def test_existing_evidence_path_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "existing.cast"
            path.write_text("owned", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CommandVideoError, "Refusing to overwrite"):
                MODULE.ensure_output_paths([path])
            self.assertEqual(path.read_text(encoding="utf-8"), "owned")

    def test_plan_scoped_recording_attempt_is_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            source.mkdir()
            plan_path = source / "session-plan.json"
            plan_path.write_text(json.dumps(base_plan(sys.executable)), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            run_id = str(uuid.uuid4())
            paths = {
                "cast_path": root / "deliverables" / "session.cast",
                "mp4_path": root / "deliverables" / "session.mp4",
                "manifest_path": root / "deliverables" / "session.manifest.json",
                "runtime_path": root / "deliverables" / "session.runtime.json",
            }
            ledger_path, ledger = MODULE.claim_recording_attempt(
                plan, run_id=run_id, **paths
            )
            original = ledger_path.read_bytes()
            self.assertEqual(ledger["status"], "claimed")
            self.assertEqual(ledger["run_id"], run_id)
            self.assertIn("does not authorize a retry", ledger["policy"])
            with self.assertRaisesRegex(MODULE.CommandVideoError, "already claimed"):
                MODULE.claim_recording_attempt(
                    plan, run_id=str(uuid.uuid4()), **paths
                )
            self.assertEqual(ledger_path.read_bytes(), original)

    def test_multi_tui_supervisor_launches_targets_in_order_with_one_final_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = multi_tui_plan()
            payload["render"]["last_frame_duration"] = 2.5
            plan_path = root / "multi-tui.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            calls: list[dict[str, object]] = []

            def fake_execute(
                selected_plan: object,
                *,
                status_path: Path,
                gate_path: Path,
                run_id: str,
                env: object,
                session_id: str,
                final_hold_seconds: float,
            ) -> int:
                calls.append(
                    {
                        "session_id": session_id,
                        "status_path": status_path,
                        "gate_path": gate_path,
                        "run_id": run_id,
                        "final_hold_seconds": final_hold_seconds,
                    }
                )
                MODULE.write_json_atomic(
                    status_path,
                    {"status": "passed", "exit_code": 0},
                )
                return 0

            run_id = str(uuid.uuid4())
            with mock.patch.object(
                MODULE, "execute_tui_target", side_effect=fake_execute
            ):
                code = MODULE.execute_tui_sequence_targets(
                    plan,
                    state_directory=root / "state",
                    run_id=run_id,
                    env=os.environ,
                )
            self.assertEqual(code, 0)
            self.assertEqual(
                [call["session_id"] for call in calls],
                ["first-tool", "second-tool"],
            )
            self.assertEqual(
                [call["final_hold_seconds"] for call in calls], [0.0, 2.5]
            )
            self.assertEqual(
                [Path(call["gate_path"]).name for call in calls],
                ["00-first-tool.gate", "01-second-tool.gate"],
            )


class CastEvidenceTests(unittest.TestCase):
    def create_evidence(self, root: Path, *, with_input: bool = False) -> tuple[object, dict[str, object], Path]:
        payload = base_plan(sys.executable)
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(payload), encoding="utf-8")
        plan = MODULE.load_plan(plan_path)
        run_id = str(uuid.uuid4())
        prompt = payload["steps"][0]["prompt"]
        output = "\n".join(
            [
                MODULE.marker(run_id, "RUN", "BEGIN"),
                MODULE.marker(run_id, "STEP", "prompt-1", "BEGIN"),
                MODULE.marker(run_id, "PROMPT", "prompt-1", "BEGIN"),
                prompt,
                MODULE.marker(run_id, "PROMPT", "prompt-1", "END"),
                MODULE.marker(run_id, "STEP", "prompt-1", "END", "0"),
                MODULE.marker(run_id, "RUN", "END", "0"),
            ]
        )
        cast_path = root / "session.cast"
        lines = [
            json.dumps(
                {
                    "version": 3,
                    "term": {"cols": 80, "rows": 24, "type": "xterm-256color"},
                    "command": f"python asciinema_command_video.py run-plan --run-id {run_id}",
                }
            ),
            json.dumps([0.1, "o", output]),
        ]
        if with_input:
            lines.append(json.dumps([0.1, "i", "secret"]))
        lines.append(json.dumps([0.1, "x", "0"]))
        cast_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        runtime = {
            "schema_version": 1,
            "status": "passed",
            "run_id": run_id,
            "plan_sha256": plan.sha256,
            "asciinema_session": "test-session",
            "tty": {"stdin": True, "stdout": True, "stderr": True},
            "target": {"name": "Python"},
            "steps": [
                {
                    "id": "prompt-1",
                    "status": "passed",
                    "prompt_sha256": MODULE.sha256_text(prompt),
                    "exit_code": 0,
                }
            ],
        }
        return plan, runtime, cast_path

    def test_v3_cast_and_runtime_evidence_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plan, runtime, cast_path = self.create_evidence(Path(temp))
            cast = MODULE.parse_cast(cast_path)
            checks = MODULE.verify_runtime_and_cast(plan, runtime, cast)
            self.assertEqual(cast["version"], 3)
            self.assertEqual(cast["input_event_count"], 0)
            self.assertIn("prompt-text", checks)

    def test_input_capture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plan, runtime, cast_path = self.create_evidence(Path(temp), with_input=True)
            cast = MODULE.parse_cast(cast_path)
            with self.assertRaisesRegex(MODULE.CommandVideoError, "input events"):
                MODULE.verify_runtime_and_cast(plan, runtime, cast)

    def test_v2_cast_duration_uses_absolute_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "v2.cast"
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"version": 2, "width": 80, "height": 24}),
                        json.dumps([0.5, "o", "one"]),
                        json.dumps([2.0, "o", "two"]),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            parsed = MODULE.parse_cast(path)
            self.assertEqual(parsed["duration_seconds"], 2.0)
            self.assertEqual(parsed["output_text"], "onetwo")

    def test_v3_hidden_marker_time_accumulates_event_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "marker.cast"
            run_id = str(uuid.uuid4())
            ready_marker = MODULE.marker(run_id, "TUI", "READY")
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"version": 3, "term": {"cols": 80, "rows": 24}}),
                        json.dumps([0.5, "o", "starting"]),
                        json.dumps([0.25, "o", ready_marker]),
                        json.dumps([0.4, "o", "\033[?1049l"]),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertAlmostEqual(
                MODULE.cast_output_text_time(path, ready_marker), 0.75, places=6
            )
            self.assertAlmostEqual(
                MODULE.cast_output_text_time(path, "\033[?1049l"), 1.15, places=6
            )


class TuiCastEvidenceTests(unittest.TestCase):
    def verify_action_evidence(
        self,
        root: Path,
        actions: list[dict[str, object]],
        *,
        hold_before_final_key: bool = False,
    ) -> list[str]:
        payload = one_shot_tui_plan(sys.executable, actions)
        if hold_before_final_key:
            payload["render"]["end_at"] = "before-final-key"
            payload["render"]["last_frame_duration"] = 2.0
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(payload), encoding="utf-8")
        plan = MODULE.load_plan(plan_path)
        run_id = str(uuid.uuid4())
        step = payload["steps"][0]
        output_fragments = [
            MODULE.marker(run_id, "RUN", "BEGIN"),
            MODULE.marker(run_id, "STEP", "interaction-1", "BEGIN"),
        ]
        observed_actions = []
        keystroke_count = 0
        enter_submitted = False
        for index, action in enumerate(actions, start=1):
            action_type = action["type"]
            action_digest = MODULE.sha256_json(action)
            output_fragments.append(
                MODULE.marker(
                    run_id,
                    "ACTION",
                    "interaction-1",
                    str(index),
                    "BEGIN",
                    str(action_type).upper(),
                    action_digest,
                )
            )
            observed = {
                "index": index,
                "type": action_type,
                "action_sha256": action_digest,
            }
            if action_type == "text":
                text_value = action["text"]
                text_hash = MODULE.sha256_text(text_value)
                screen = f"READY> {text_value}\n"
                observed.update(
                    {
                        "text_sha256": text_hash,
                        "keystroke_count": len(text_value),
                        "visible_before_next_key": True,
                        "screen": screen,
                        "screen_sha256": MODULE.sha256_text(screen),
                    }
                )
                keystroke_count += len(text_value)
                output_fragments.extend(
                    [
                        MODULE.marker(
                            run_id,
                            "TYPING",
                            "interaction-1",
                            str(index),
                            "BEGIN",
                            text_hash,
                        ),
                        MODULE.marker(
                            run_id,
                            "TYPING",
                            "interaction-1",
                            str(index),
                            "END",
                            text_hash,
                        ),
                    ]
                )
            elif action_type == "key":
                key_value = action["key"]
                observed["key"] = key_value
                keystroke_count += 1
                if hold_before_final_key and index == len(actions):
                    output_fragments.append(MODULE.marker(run_id, "TUI", "FINAL-KEY"))
                if key_value == "Enter":
                    enter_submitted = True
                    output_fragments.append(
                        MODULE.marker(run_id, "SUBMIT", "interaction-1", "ENTER")
                    )
                else:
                    output_fragments.append(
                        MODULE.marker(run_id, "KEY", "interaction-1", key_value)
                    )
            else:
                observed["seconds"] = float(action["seconds"])
            observed_actions.append(observed)
            output_fragments.append(
                MODULE.marker(
                    run_id,
                    "ACTION",
                    "interaction-1",
                    str(index),
                    "END",
                    str(action_type).upper(),
                    action_digest,
                )
            )
        completion_screen = "REAL TARGET FINAL SCREEN\n"
        output_fragments.extend(
            [
                MODULE.marker(run_id, "STEP", "interaction-1", "END", "0"),
                MODULE.marker(run_id, "TARGET", "EXIT", "0"),
                MODULE.marker(run_id, "RUN", "END", "0"),
            ]
        )
        cast_path = root / "session.cast"
        cast_path.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "version": 3,
                            "term": {"cols": 80, "rows": 24},
                            "command": (
                                "python asciinema_command_video.py run-plan "
                                f"--run-id {run_id}"
                            ),
                        }
                    ),
                    json.dumps([0.1, "o", "\n".join(output_fragments)]),
                    json.dumps([0.1, "x", "0"]),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        target_status = {"status": "passed", "exit_code": 0}
        runtime = {
            "schema_version": 1,
            "status": "passed",
            "mode": "tui",
            "run_id": run_id,
            "plan_sha256": plan.sha256,
            "asciinema_session": "test-session",
            "tty": {"stdin": True, "stdout": True, "stderr": True},
            "target": {"name": "Python", "final_exit_code": 0},
            "interaction": {
                "mode": "tui",
                "input_delivery": "tmux-send-keys",
                "shutdown_mode": "target-exit",
                "target_status": target_status,
            },
            "steps": [
                {
                    "id": "interaction-1",
                    "status": "passed",
                    "input_kind": "actions",
                    "input_sha256": MODULE.tui_step_input_sha256(step),
                    "typing_method": "tmux-send-keys",
                    "keystroke_count": keystroke_count,
                    "enter_submitted": enter_submitted,
                    "action_count": len(actions),
                    "actions": observed_actions,
                    "completion": "target-exit",
                    "completion_screen": completion_screen,
                    "completion_screen_sha256": MODULE.sha256_text(completion_screen),
                    "ready_after_response": False,
                    "busy_after_response": False,
                    "target_exited_after_actions": True,
                }
            ],
        }
        return MODULE.verify_runtime_and_cast(plan, runtime, MODULE.parse_cast(cast_path))

    def test_tui_keystroke_and_completion_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = tui_plan(sys.executable)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            run_id = str(uuid.uuid4())
            step = payload["steps"][0]
            prompt = step["prompt"]
            prompt_hash = MODULE.sha256_text(prompt)
            typed_screen = f"READY> {prompt}\n"
            response_screen = "REAL_RESPONSE\nREADY>\n"
            output = "\n".join(
                [
                    MODULE.marker(run_id, "RUN", "BEGIN"),
                    MODULE.marker(run_id, "STEP", "prompt-1", "BEGIN"),
                    MODULE.marker(run_id, "TYPING", "prompt-1", "BEGIN", prompt_hash),
                    MODULE.marker(run_id, "TYPING", "prompt-1", "END", prompt_hash),
                    MODULE.marker(run_id, "SUBMIT", "prompt-1", "ENTER"),
                    MODULE.marker(run_id, "STEP", "prompt-1", "END", "0"),
                    MODULE.marker(run_id, "TARGET", "EXIT", "0"),
                    MODULE.marker(run_id, "RUN", "END", "0"),
                ]
            )
            cast_path = root / "session.cast"
            cast_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "version": 3,
                                "term": {"cols": 80, "rows": 24, "type": "xterm-256color"},
                                "command": (
                                    "python asciinema_command_video.py run-plan "
                                    f"--run-id {run_id}"
                                ),
                            }
                        ),
                        json.dumps([0.1, "o", output]),
                        json.dumps([0.1, "x", "0"]),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            runtime = {
                "schema_version": 1,
                "status": "passed",
                "mode": "tui",
                "run_id": run_id,
                "plan_sha256": plan.sha256,
                "asciinema_session": "test-session",
                "tty": {"stdin": True, "stdout": True, "stderr": True},
                "target": {"name": "Python", "final_exit_code": 0},
                "interaction": {
                    "mode": "tui",
                    "input_delivery": "tmux-send-keys",
                    "submit_key": "Enter",
                },
                "steps": [
                    {
                        "id": "prompt-1",
                        "status": "passed",
                        "prompt_sha256": prompt_hash,
                        "typing_method": "tmux-send-keys",
                        "keystroke_count": len(prompt),
                        "submit_key": "Enter",
                        "prompt_visible_before_submit": True,
                        "ready_after_response": True,
                        "busy_after_response": False,
                        "typed_screen": typed_screen,
                        "typed_screen_sha256": MODULE.sha256_text(typed_screen),
                        "response_screen": response_screen,
                        "response_screen_sha256": MODULE.sha256_text(response_screen),
                    }
                ],
            }
            checks = MODULE.verify_runtime_and_cast(plan, runtime, MODULE.parse_cast(cast_path))
            self.assertIn("timed-keystrokes", checks)
            self.assertIn("enter-submission", checks)
            self.assertIn("tui-ready", checks)
            self.assertIn("target-exit", checks)

    def test_one_shot_text_enter_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            checks = self.verify_action_evidence(
                Path(temp),
                [
                    {"type": "text", "text": "beta"},
                    {"type": "pause", "seconds": 0.25},
                    {"type": "key", "key": "Enter"},
                ],
            )
            self.assertIn("explicit-tui-actions", checks)
            self.assertIn("timed-keystrokes", checks)
            self.assertIn("enter-submission", checks)
            self.assertIn("target-exit-completion", checks)

    def test_raw_quit_key_evidence_passes_without_enter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            checks = self.verify_action_evidence(
                Path(temp),
                [
                    {"type": "pause", "seconds": 2.0},
                    {"type": "key", "key": "q"},
                ],
            )
            self.assertIn("command-keys", checks)
            self.assertIn("target-exit-completion", checks)
            self.assertNotIn("enter-submission", checks)

    def test_before_final_key_marker_is_required_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            checks = self.verify_action_evidence(
                Path(temp),
                [
                    {"type": "pause", "seconds": 0.25},
                    {"type": "key", "key": "q"},
                ],
                hold_before_final_key=True,
            )
            self.assertIn("before-final-key-marker", checks)

    def test_multi_tui_runtime_proves_order_boundaries_and_distinct_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = tui_plan("first-tui")
            second = tui_plan("second-tui")
            second["steps"][0]["id"] = "prompt-2"
            second["steps"][0]["prompt"] = "beta"
            payload = {
                "schema_version": 1,
                "title": "Two authentic TUIs",
                "working_directory": ".",
                "declared_scope": "Two local test TUIs.",
                "terminal": first["terminal"],
                "render": first["render"],
                "tui_sessions": [
                    {
                        "id": "first-tool",
                        "target": first["target"],
                        "interaction": first["interaction"],
                        "steps": first["steps"],
                    },
                    {
                        "id": "second-tool",
                        "target": second["target"],
                        "interaction": second["interaction"],
                        "steps": second["steps"],
                    },
                ],
            }
            plan_path = root / "multi-tui.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            run_id = str(uuid.uuid4())
            output_fragments = [MODULE.marker(run_id, "RUN", "BEGIN")]
            observed_sessions = []
            observed_targets = []
            flattened_steps = []
            for index, session in enumerate(payload["tui_sessions"], start=1):
                session_id = session["id"]
                planned_step = session["steps"][0]
                prompt = planned_step["prompt"]
                prompt_hash = MODULE.sha256_text(prompt)
                typed_screen = f"READY> {prompt}\n"
                response_screen = "REAL RESULT\nREADY>\n"
                target = {
                    "session_id": session_id,
                    "name": session["target"]["name"],
                    "requested_executable": session["target"]["executable"],
                    "resolved_executable": f"/tools/{session_id}",
                    "executable_sha256": ("a" if index == 1 else "b") * 64,
                    "final_exit_code": 0,
                }
                interaction = {
                    "mode": "tui",
                    "input_delivery": "tmux-send-keys",
                    "shutdown_mode": "exit-text",
                    "startup_ready_at_utc": "2026-08-21T00:00:00Z",
                    "target_status": {"status": "passed", "exit_code": 0},
                }
                observed_step = {
                    "id": planned_step["id"],
                    "status": "passed",
                    "prompt_sha256": prompt_hash,
                    "typing_method": "tmux-send-keys",
                    "keystroke_count": len(prompt),
                    "submit_key": "Enter",
                    "prompt_visible_before_submit": True,
                    "ready_after_response": True,
                    "busy_after_response": False,
                    "typed_screen": typed_screen,
                    "typed_screen_sha256": MODULE.sha256_text(typed_screen),
                    "response_screen": response_screen,
                    "response_screen_sha256": MODULE.sha256_text(response_screen),
                }
                output_fragments.extend(
                    [
                        MODULE.marker(
                            run_id,
                            "TUI-SEQUENCE",
                            "HANDOFF",
                            str(index),
                            session_id,
                        ),
                        MODULE.marker(run_id, "TUI-SESSION", session_id, "BEGIN"),
                        MODULE.marker(run_id, "TUI-SESSION", session_id, "READY"),
                        MODULE.marker(run_id, "STEP", planned_step["id"], "BEGIN"),
                        MODULE.marker(
                            run_id,
                            "TYPING",
                            planned_step["id"],
                            "BEGIN",
                            prompt_hash,
                        ),
                        MODULE.marker(
                            run_id,
                            "TYPING",
                            planned_step["id"],
                            "END",
                            prompt_hash,
                        ),
                        MODULE.marker(
                            run_id, "SUBMIT", planned_step["id"], "ENTER"
                        ),
                        MODULE.marker(
                            run_id, "STEP", planned_step["id"], "END", "0"
                        ),
                        MODULE.marker(
                            run_id, "TUI-SESSION", session_id, "EXIT", "0"
                        ),
                        MODULE.marker(run_id, "TARGET", "EXIT", "0"),
                    ]
                )
                observed_targets.append(target)
                observed_sessions.append(
                    {
                        "id": session_id,
                        "index": index,
                        "target": target,
                        "interaction": interaction,
                        "steps": [observed_step],
                    }
                )
                flattened_steps.append(observed_step)
            output_fragments.append(MODULE.marker(run_id, "RUN", "END", "0"))
            cast_path = root / "session.cast"
            cast_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "version": 3,
                                "term": {"cols": 80, "rows": 24},
                                "command": (
                                    "python asciinema_command_video.py run-plan "
                                    f"--run-id {run_id}"
                                ),
                            }
                        ),
                        json.dumps([0.1, "o", "\n".join(output_fragments)]),
                        json.dumps([0.1, "x", "0"]),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            runtime = {
                "schema_version": 1,
                "status": "passed",
                "mode": "tui-sequence",
                "run_id": run_id,
                "plan_sha256": plan.sha256,
                "asciinema_session": "test-session",
                "tty": {"stdin": True, "stdout": True, "stderr": True},
                "target": {"name": "multi-tool-tui-sequence", "final_exit_code": 0},
                "targets": observed_targets,
                "tui_sessions": observed_sessions,
                "steps": flattened_steps,
            }
            checks = MODULE.verify_runtime_and_cast(
                plan, runtime, MODULE.parse_cast(cast_path)
            )
            self.assertIn("multi-tui-sequence", checks)
            self.assertIn("multi-target-provenance", checks)
            self.assertIn("tui-session-boundaries", checks)


class TerminalControlContractTests(unittest.TestCase):
    def test_tui_lifecycle_covers_record_interact_shutdown_and_convert(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(tui_plan(sys.executable)), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            contract = MODULE.terminal_control_contract(
                plan,
                asciinema=Path("/tools/asciinema"),
                agg=Path("/tools/agg"),
                tmux=Path("/usr/bin/tmux"),
                ffmpeg=Path("/usr/bin/ffmpeg"),
                ffprobe=Path("/usr/bin/ffprobe"),
                targets=[Path("/usr/bin/target")],
                pty_allocator=Path("/usr/bin/script"),
            )
            states = contract["state_order"]
            self.assertEqual(states[0], "preflight-passed")
            self.assertLess(states.index("recording-started"), states.index("target-launched"))
            self.assertLess(
                states.index("input-action-delivered"),
                states.index("interaction-step-complete"),
            )
            self.assertLess(
                states.index("interaction-step-complete"),
                states.index("target-exit-requested"),
            )
            self.assertLess(states.index("target-exited"), states.index("recording-stopped"))
            self.assertLess(states.index("cast-validated"), states.index("render-complete"))
            self.assertEqual(states[-1], "media-validated")
            self.assertEqual(Path(contract["components"]["multiplexer"]).name, "tmux")

    def test_multi_tui_lifecycle_declares_handoff_and_repeated_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plan_path = Path(temp) / "multi-tui.json"
            plan_path.write_text(json.dumps(multi_tui_plan()), encoding="utf-8")
            plan = MODULE.load_plan(plan_path)
            contract = MODULE.terminal_control_contract(
                plan,
                asciinema=Path("/tools/asciinema"),
                agg=Path("/tools/agg"),
                tmux=Path("/usr/bin/tmux"),
                ffmpeg=Path("/usr/bin/ffmpeg"),
                ffprobe=Path("/usr/bin/ffprobe"),
                targets=[Path("/usr/bin/first"), Path("/usr/bin/second")],
                pty_allocator=Path("/usr/bin/script"),
            )
            self.assertEqual(contract["mode"], "tui-sequence")
            self.assertIn("target-handoff", contract["state_order"])
            self.assertIn("target-launched", contract["repeatable_states"])
            self.assertEqual(
                contract["components"]["targets"],
                [str(Path("/usr/bin/first")), str(Path("/usr/bin/second"))],
            )

    def test_preflight_parser_accepts_all_terminal_components(self) -> None:
        args = MODULE.build_parser().parse_args(
            [
                "preflight",
                "source/plan.json",
                "--tools-dir",
                ".tools/asciinema",
                "--asciinema",
                "arcv-asciinema",
                "--agg",
                "arcv-agg",
                "--tmux",
                "arcv-tmux",
                "--ffmpeg",
                "arcv-ffmpeg",
                "--ffprobe",
                "arcv-ffprobe",
                "--json",
            ]
        )
        self.assertEqual(args.command, "preflight")
        self.assertEqual(args.tmux, "arcv-tmux")
        self.assertEqual(args.ffprobe, "arcv-ffprobe")
        self.assertTrue(args.json)


class ToolPinTests(unittest.TestCase):
    def test_lazygit_longpaths_preflight_requires_project_local_true(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            native_git = root / "git"
            native_git.write_bytes(b"test-git")
            native_git.chmod(0o755)
            with (
                mock.patch.object(MODULE, "NATIVE_WSL_GIT", native_git),
                mock.patch.object(MODULE, "command_output", return_value=(0, "true\n")),
            ):
                result = MODULE.lazygit_longpaths_preflight(
                    working_directory=root, env={"PATH": ""}
                )
            self.assertEqual(result["scope"], "project-local")
            self.assertIs(result["value"], True)

            with (
                mock.patch.object(MODULE, "NATIVE_WSL_GIT", native_git),
                mock.patch.object(MODULE, "command_output", return_value=(1, "")),
                self.assertRaisesRegex(
                    MODULE.CommandVideoError, "core.longpaths=true"
                ),
            ):
                MODULE.lazygit_longpaths_preflight(
                    working_directory=root, env={"PATH": ""}
                )

    def test_temporary_windows_path_bridge_is_locked_and_released(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subst = root / "subst.exe"
            subst.write_bytes(b"test-subst")
            preflight = {
                "mode": "temporary-subst-drive",
                "token": MODULE.WINDOWS_WORKING_DIRECTORY_TOKEN,
                "source_working_directory": str(root),
                "windows_source_path": r"C:\very\long\workspace",
                "wslpath": str(root / "wslpath"),
                "wslpath_sha256": "a" * 64,
                "subst": str(subst),
                "subst_sha256": MODULE.sha256_file(subst),
                "candidate_drive_count": len(MODULE.SUBST_DRIVE_LETTERS),
            }
            completed = subprocess.CompletedProcess([], 0, stdout="")
            with (
                mock.patch.object(
                    MODULE, "windows_path_bridge_preflight", return_value=preflight
                ),
                mock.patch.object(MODULE.tempfile, "gettempdir", return_value=temp),
                mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run,
            ):
                bridge = MODULE.acquire_windows_working_directory_bridge(
                    working_directory=root,
                    env={"PATH": ""},
                    run_id=str(uuid.uuid4()),
                )
                lock_path = Path(bridge["_lock_path"])
                self.assertTrue(lock_path.is_file())
                self.assertEqual(bridge["mount_root"], "Z:/")
                released = MODULE.release_windows_working_directory_bridge(
                    bridge, working_directory=root, env={"PATH": ""}
                )
            self.assertTrue(released["released"])
            self.assertFalse(lock_path.exists())
            self.assertEqual(run.call_count, 2)

    def test_windows_path_translation_is_deterministic(self) -> None:
        translated = MODULE.windows_path_to_wsl(Path(r"C:\Workspace With Space\demo.cast"))
        self.assertEqual(translated, "/mnt/c/Workspace With Space/demo.cast")

    def test_supported_assets_have_complete_sha256_pins(self) -> None:
        self.assertEqual(len(MODULE.PINNED_TOOL_ASSETS), 4)
        for tools in MODULE.PINNED_TOOL_ASSETS.values():
            self.assertEqual(set(tools), {"asciinema", "agg"})
            for metadata in tools.values():
                self.assertRegex(metadata["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(metadata["url"].startswith("https://github.com/asciinema/"))
                self.assertGreater(metadata["size"], 1_000_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
