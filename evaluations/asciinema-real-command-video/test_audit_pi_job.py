#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Unit tests for the Pi trace compliance auditor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


AUDITOR_PATH = Path(__file__).with_name("audit_pi_job.py")
SPEC = importlib.util.spec_from_file_location("audit_pi_job", AUDITOR_PATH)
assert SPEC and SPEC.loader
AUDITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)


def event(value: dict[str, object]) -> str:
    return json.dumps(value, sort_keys=True)


class AuditPiJobTests(unittest.TestCase):
    def make_trial(self, root: Path, *, retry: bool = False) -> tuple[Path, Path]:
        task_id = "task-one"
        instruction = "First line\nSecond line\n"
        prompt = instruction.rstrip("\r\n")
        dataset = root / "dataset"
        task = dataset / task_id
        task.mkdir(parents=True)
        (task / "instruction.md").write_text(instruction, encoding="utf-8")
        trial = root / f"{task_id}__trial"
        trace = trial / "agent" / "pi.txt"
        trace.parent.mkdir(parents=True)
        commands = [
            "uv run asciinema_command_video.py validate-plan source/session-plan.json",
            "uv run asciinema_command_video.py preflight source/session-plan.json",
            "uv run asciinema_command_video.py record source/session-plan.json",
            "uv run asciinema_command_video.py validate --plan source/session-plan.json",
        ]
        if retry:
            commands.extend(
                [
                    "mv deliverables/session.cast deliverables/session-old.cast",
                    "uv run asciinema_command_video.py record source/session-plan.json",
                ]
            )
        lines = [
            event(
                {
                    "type": "harbor_pi_wrapper",
                    "promptBytes": len(prompt.encode("utf-8")),
                    "promptSha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                }
            ),
            event(
                {
                    "type": "message_end",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    },
                }
            ),
        ]
        lines.extend(
            event(
                {
                    "type": "tool_execution_start",
                    "toolName": "bash",
                    "args": {"command": command},
                }
            )
            for command in commands
        )
        if retry:
            lines.append(
                event(
                    {
                        "type": "tool_execution_start",
                        "toolName": "write",
                        "args": {"path": "source/custom-controller.py"},
                    }
                )
            )
        lines.extend([event({"type": "agent_end"}), event({"type": "agent_settled"})])
        trace.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return trial, dataset

    def test_clean_single_pass_trace_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            trial, dataset = self.make_trial(Path(temporary_directory))
            result = AUDITOR.audit_trial(trial, dataset)
        self.assertTrue(result["ok"])
        self.assertEqual(result["recordCalls"], 1)
        self.assertTrue(result["wrapperMarkerMatches"])

    def test_retry_and_custom_controller_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            trial, dataset = self.make_trial(Path(temporary_directory), retry=True)
            result = AUDITOR.audit_trial(trial, dataset)
        self.assertFalse(result["ok"])
        self.assertEqual(result["recordCalls"], 2)
        self.assertGreater(result["retryMutations"], 0)
        self.assertEqual(result["customSourcePaths"], ["source/custom-controller.py"])


if __name__ == "__main__":
    unittest.main()
