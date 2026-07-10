#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_script("pi_eval_runner", ROOT / "scripts" / "run-pi-skill-eval.py")
SUMMARIZER = load_script("pi_event_summarizer", ROOT / "scripts" / "summarize-pi-json-events.py")


def write_fake_pi(path: Path) -> None:
    path.write_text(
        """from __future__ import annotations
import json
import os
import sys
from pathlib import Path

if "--version" in sys.argv:
    print("fake-pi 1.0")
    raise SystemExit(0)

output = Path("outputs/result.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"ok": True, "items": [{"value": None}]}), encoding="utf-8")
if os.environ.get("FAKE_PI_MUTATE") == "1":
    Path("skills/demo-skill/SKILL.md").write_text("mutated", encoding="utf-8")

events = [
    {"type": "session", "version": 3, "id": "fake", "cwd": str(Path.cwd())},
    {"type": "message_end", "message": {"role": "assistant", "provider": "openai-codex", "model": "gpt-5.3-codex-spark", "usage": {"input": 10, "output": 5, "totalTokens": 15}}},
    {"type": "tool_execution_start", "toolCallId": "read-1", "args": {"path": "../prompt.md"}},
    {"type": "tool_execution_end", "toolCallId": "read-1", "toolName": "read", "isError": False, "result": "prompt"},
    {"type": "tool_execution_start", "toolCallId": "shell-1", "args": {"command": "mkdir -p outputs && write result"}},
    {"type": "tool_execution_end", "toolCallId": "shell-1", "toolName": "shell", "isError": False, "result": "ok"},
]
for event in events:
    print(json.dumps(event))
""",
        encoding="utf-8",
    )


class RunnerUnitTests(unittest.TestCase):
    def test_safe_workspace_paths(self) -> None:
        self.assertTrue(RUNNER.is_safe_workspace_relative(Path("outputs/result.json")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path(".")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path("../result.json")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path("C:/result.json")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path("C:result.json")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path(r"\outside.json")))
        self.assertFalse(RUNNER.is_safe_workspace_relative(Path("outputs/result.json:stream")))
        self.assertTrue(RUNNER.targets_skill_payload(Path("skills/demo-skill/SKILL.md")))

    def test_nested_value_distinguishes_missing_from_null(self) -> None:
        payload = {"items": [{"value": None}]}
        self.assertEqual(RUNNER.nested_value(payload, "items.0.value"), (True, None))
        self.assertEqual(RUNNER.nested_value(payload, "items.1.value"), (False, None))
        self.assertEqual(RUNNER.nested_value(payload, "items.0.missing"), (False, None))

    def test_json_field_check_rejects_missing_null(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            (workspace / "result.json").write_text('{"present": null}', encoding="utf-8")
            report = RUNNER.output_json_field_report(workspace, ["result.json::missing=null"])
            self.assertFalse(report["passed"])
            self.assertEqual(report["findings"][0]["code"], "json-output-field-missing")

    def test_runtime_copy_excludes_examples_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            (source / "assets/examples").mkdir(parents=True)
            (source / "node_modules/pkg").mkdir(parents=True)
            (source / "SKILL.md").write_text("skill", encoding="utf-8")
            (source / "assets/examples/fixture.txt").write_text("fixture", encoding="utf-8")
            (source / "node_modules/pkg/index.js").write_text("dependency", encoding="utf-8")

            runtime = root / "runtime"
            RUNNER.copy_skill_only(source, runtime, "runtime")
            self.assertTrue((runtime / "SKILL.md").is_file())
            self.assertFalse((runtime / "assets/examples").exists())
            self.assertFalse((runtime / "node_modules").exists())

            full = root / "full"
            RUNNER.copy_skill_only(source, full, "full")
            self.assertTrue((full / "assets/examples/fixture.txt").is_file())
            self.assertFalse((full / "node_modules").exists())
            runtime_patterns = RUNNER.strict_forbidden_read_patterns("demo-skill", "runtime")
            full_patterns = RUNNER.strict_forbidden_read_patterns("demo-skill", "full")
            self.assertIn(RUNNER.STRICT_ASSETS_EXAMPLES_READ_PATTERN, runtime_patterns)
            self.assertNotIn(RUNNER.STRICT_ASSETS_EXAMPLES_READ_PATTERN, full_patterns)

    def test_snapshot_detects_real_changes_but_ignores_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("before", encoding="utf-8")
            before = RUNNER.snapshot_tree(root)
            (root / "__pycache__").mkdir()
            (root / "__pycache__/cache.pyc").write_bytes(b"cache")
            self.assertTrue(RUNNER.compare_snapshots(before, RUNNER.snapshot_tree(root))["passed"])
            (root / "SKILL.md").write_text("after", encoding="utf-8")
            report = RUNNER.compare_snapshots(before, RUNNER.snapshot_tree(root))
            self.assertFalse(report["passed"])
            self.assertEqual(report["modified"], ["SKILL.md"])
            (root / "SKILL.md").write_text("before", encoding="utf-8")
            (root / "output").mkdir()
            (root / "output/generated.txt").write_text("unexpected", encoding="utf-8")
            report = RUNNER.compare_snapshots(before, RUNNER.snapshot_tree(root))
            self.assertFalse(report["passed"])
            self.assertEqual(report["added"], ["output/generated.txt"])

    def test_event_checks_verify_prompt_model_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events = root / "events.jsonl"
            skill_file = root / "workspace/skills/d3-composition-evaluator/SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("skill", encoding="utf-8")
            records = [
                {"type": "message_end", "message": {"role": "assistant", "provider": "openai-codex", "model": "gpt-5.3-codex-spark"}},
                {"type": "tool_execution_start", "toolCallId": "1", "args": {"path": "../prompt.md"}},
                {"type": "tool_execution_end", "toolCallId": "1", "toolName": "read", "isError": False, "result": "ok"},
                {"type": "tool_execution_start", "toolCallId": "2", "args": {"path": str(skill_file)}},
                {"type": "tool_execution_end", "toolCallId": "2", "toolName": "read", "isError": False, "result": "skill"},
                {"type": "tool_execution_start", "toolCallId": "3", "args": {"path": "assets/examples/generated.md"}},
                {"type": "tool_execution_end", "toolCallId": "3", "toolName": "write", "isError": False, "result": "written"},
            ]
            events.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            report = RUNNER.event_check_report(
                events_path=events,
                prompt="Do the task.",
                require_prompt_read_first=True,
                require_exact_command_from_prompt=False,
                require_observed_model=True,
                requested_model="openai-codex/gpt-5.3-codex-spark",
                fail_on_invalid_json=True,
                fail_on_tool_error=True,
                forbid_read_regex=RUNNER.strict_forbidden_read_patterns(
                    "d3-composition-evaluator", "runtime"
                ),
                forbid_command_regex=[],
            )
            self.assertTrue(report["passed"])
            self.assertEqual(report["observedModels"], [{"provider": "openai-codex", "model": "gpt-5.3-codex-spark"}])
            events.write_text(events.read_text(encoding="utf-8") + "[]\n", encoding="utf-8")
            report = RUNNER.event_check_report(
                events_path=events,
                prompt="Do the task.",
                require_prompt_read_first=True,
                require_exact_command_from_prompt=False,
                require_observed_model=True,
                requested_model="openai-codex/gpt-5.3-codex-spark",
                fail_on_invalid_json=True,
                fail_on_tool_error=True,
                forbid_read_regex=[],
                forbid_command_regex=[],
            )
            self.assertFalse(report["passed"])
            self.assertEqual(report["findings"][0]["code"], "invalid-event-json")

    def test_event_checks_reject_normalized_sibling_skill_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events = root / "events.jsonl"
            sibling = root / "workspace/skills/other-skill/SKILL.md"
            sibling.parent.mkdir(parents=True)
            sibling.write_text("skill", encoding="utf-8")
            records = [
                {"type": "message_end", "message": {"role": "assistant", "provider": "openai-codex", "model": "gpt-5.3-codex-spark"}},
                {"type": "tool_execution_start", "toolCallId": "1", "args": {"path": "../prompt.md"}},
                {"type": "tool_execution_end", "toolCallId": "1", "toolName": "read", "isError": False, "result": "ok"},
                {"type": "tool_execution_start", "toolCallId": "2", "args": {"path": "skills/d3-composition-evaluator/../other-skill/SKILL.md"}},
                {"type": "tool_execution_end", "toolCallId": "2", "toolName": "read", "isError": False, "result": "skill"},
            ]
            events.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            report = RUNNER.event_check_report(
                events_path=events,
                prompt="Do the task.",
                require_prompt_read_first=True,
                require_exact_command_from_prompt=False,
                require_observed_model=True,
                requested_model="openai-codex/gpt-5.3-codex-spark",
                fail_on_invalid_json=True,
                fail_on_tool_error=True,
                forbid_read_regex=[r"(?i)^skills[\\/](?!d3-composition-evaluator(?:[\\/]|$))"],
                forbid_command_regex=[],
            )
            self.assertFalse(report["passed"])
            self.assertEqual(report["findings"][0]["policyPath"], "skills/other-skill/SKILL.md")


class RunnerIntegrationTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        skill = root / ".agents/skills/demo-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Test fixture.\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        (root / "evaluations/runs").mkdir(parents=True)
        fake_pi = root / "fake_pi.py"
        write_fake_pi(fake_pi)
        return fake_pi

    def run_fixture(self, root: Path, fake_pi: Path, run_id: str, mutate: bool = False) -> int:
        argv = [
            "run-pi-skill-eval.py",
            "demo-skill",
            "--prompt",
            "Create outputs/result.json.",
            "--mode",
            "json",
            "--strict",
            "--run-id",
            run_id,
            "--expect-output",
            "outputs/result.json",
            "--expect-output-json-field",
            "outputs/result.json::ok=true",
        ]
        environment = {"FAKE_PI_MUTATE": "1" if mutate else "0"}
        with (
            mock.patch.object(RUNNER, "repo_root", return_value=root),
            mock.patch.object(RUNNER, "pi_command_prefix", return_value=[sys.executable, str(fake_pi)]),
            mock.patch.object(sys, "argv", argv),
            mock.patch.dict(os.environ, environment, clear=False),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return RUNNER.main()

    def test_strict_fake_pi_run_writes_reproducible_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake_pi = self.make_repo(root)
            self.assertEqual(self.run_fixture(root, fake_pi, "strict-pass"), 0)
            run = root / "evaluations/runs/strict-pass"
            result = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
            manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
            artifacts = json.loads((run / "artifact-check.json").read_text(encoding="utf-8"))
            self.assertTrue(result["passed"])
            self.assertTrue(result["gates"]["skillIntegrity"])
            self.assertEqual(manifest["pi"]["model"], "openai-codex/gpt-5.3-codex-spark")
            self.assertEqual(manifest["environment"]["piVersion"], "fake-pi 1.0")
            self.assertRegex(artifacts["outputs"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_strict_run_fails_when_skill_copy_is_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake_pi = self.make_repo(root)
            self.assertEqual(self.run_fixture(root, fake_pi, "mutated", mutate=True), 6)
            report = json.loads(
                (root / "evaluations/runs/mutated/skill-integrity-check.json").read_text(encoding="utf-8")
            )
            self.assertFalse(report["passed"])
            self.assertEqual(report["modified"], ["SKILL.md"])

    def test_run_id_traversal_is_rejected_before_workspace_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake_pi = self.make_repo(root)
            argv = [
                "run-pi-skill-eval.py",
                "demo-skill",
                "--prompt",
                "Task",
                "--run-id",
                "../escape",
            ]
            with (
                mock.patch.object(RUNNER, "repo_root", return_value=root),
                mock.patch.object(RUNNER, "pi_command_prefix", return_value=[sys.executable, str(fake_pi)]),
                mock.patch.object(sys, "argv", argv),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(RUNNER.main(), 2)
            self.assertFalse((root / "evaluations/escape").exists())

            skill_output_argv = [
                "run-pi-skill-eval.py",
                "demo-skill",
                "--prompt",
                "Task",
                "--mode",
                "json",
                "--strict",
                "--run-id",
                "skill-output",
                "--expect-output",
                "skills/demo-skill/SKILL.md",
            ]
            with (
                mock.patch.object(RUNNER, "repo_root", return_value=root),
                mock.patch.object(RUNNER, "pi_command_prefix", return_value=[sys.executable, str(fake_pi)]),
                mock.patch.object(sys, "argv", skill_output_argv),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(RUNNER.main(), 2)
            self.assertFalse((root / "evaluations/runs/skill-output").exists())


class SummarizerTests(unittest.TestCase):
    def test_summary_requires_spark_and_valid_json(self) -> None:
        self.assertEqual(SUMMARIZER.result_size("é"), 2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events = root / "events.jsonl"
            output = root / "summary.json"
            records = [
                {"type": "session", "version": 3, "id": "fake", "cwd": str(root)},
                {"type": "message_end", "message": {"role": "assistant", "provider": "openai-codex", "model": "gpt-5.3-codex-spark", "usage": {"totalTokens": 12}}},
                {"type": "tool_execution_start", "toolCallId": "1", "args": {"path": "../prompt.md"}},
                {"type": "tool_execution_end", "toolCallId": "1", "toolName": "read", "isError": False, "result": "prompt"},
            ]
            events.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            argv = [
                "summarize-pi-json-events.py",
                str(events),
                "--output",
                str(output),
                "--require-model",
                "gpt-5.3-codex-spark",
                "--require-tool-call",
                "--fail-on-invalid-json",
            ]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(SUMMARIZER.main(), 0)
            summary = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(summary["passed"])
            self.assertEqual(summary["models"], {"gpt-5.3-codex-spark": 1})
            self.assertEqual(summary["usageTotals"]["totalTokens"], 12)

            other_model = {
                "type": "message_end",
                "message": {"role": "assistant", "provider": "openai-codex", "model": "fallback-model"},
            }
            events.write_text(
                events.read_text(encoding="utf-8")
                + "[]\n"
                + json.dumps(other_model)
                + "\nnot-json\n",
                encoding="utf-8",
            )
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(SUMMARIZER.main(), 1)
            failed = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(failed["invalidJsonLineCount"], 1)
            self.assertEqual(failed["invalidEventRecordCount"], 1)
            self.assertIn(
                "observed-model-set-mismatch",
                {finding["code"] for finding in failed["findings"]},
            )


if __name__ == "__main__":
    unittest.main()
