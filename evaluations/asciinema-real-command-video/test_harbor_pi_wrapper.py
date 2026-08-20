#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Regression tests for the Windows Pi Harbor wrapper."""

from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


WRAPPER_PATH = Path(__file__).with_name("harbor_pi_wrapper.py")
SPEC = importlib.util.spec_from_file_location("harbor_pi_wrapper", WRAPPER_PATH)
assert SPEC and SPEC.loader
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)


class FakeProcess:
    def __init__(self, command: list[str], **_: object) -> None:
        self.command = command
        self.stdout = iter(
            [json.dumps({"type": "agent_end", "echo": command[-1]}) + "\n"]
        )

    def wait(self) -> int:
        return 0


class HarborPiWrapperTests(unittest.TestCase):
    def test_multiline_prompt_is_one_exact_process_argument(self) -> None:
        prompt = "first line\nsecond line with `code`\n\nfinal paragraph"
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "pi.jsonl"
            arguments = WRAPPER.build_parser().parse_args(
                [
                    "run",
                    "--expected-version",
                    "0.84.2",
                    "--prompt-base64",
                    base64.b64encode(prompt.encode("utf-8")).decode("ascii"),
                    "--provider",
                    "openai-codex",
                    "--model",
                    "gpt-test",
                    "--thinking",
                    "high",
                    "--skill-path",
                    ".agents/skills/asciinema-real-command-video",
                    "--output",
                    str(output),
                ]
            )
            captured: list[FakeProcess] = []

            def fake_popen(command: list[str], **kwargs: object) -> FakeProcess:
                process = FakeProcess(command, **kwargs)
                captured.append(process)
                return process

            with (
                mock.patch.object(
                    WRAPPER, "resolve_pi_command", return_value=["node.exe", "pi.js"]
                ),
                mock.patch.object(WRAPPER, "pi_version", return_value="0.84.2"),
                mock.patch.object(WRAPPER.subprocess, "Popen", side_effect=fake_popen),
            ):
                self.assertEqual(WRAPPER.run_command(arguments), 0)

            self.assertEqual(captured[0].command[-1], prompt)
            self.assertNotIn("pi.cmd", captured[0].command)
            self.assertIn("--no-context-files", captured[0].command)
            self.assertIn("--no-skills", captured[0].command)
            self.assertIn("--skill", captured[0].command)
            first_event = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(first_event["promptBytes"], len(prompt.encode("utf-8")))

    def test_real_pi_entrypoint_resolves_to_node_and_javascript(self) -> None:
        command = WRAPPER.resolve_pi_command()
        self.assertGreaterEqual(len(command), 2)
        self.assertTrue(command[0].lower().endswith(("node.exe", "node")))
        self.assertTrue(command[1].replace("\\", "/").endswith("/dist/cli.js"))


if __name__ == "__main__":
    unittest.main()
