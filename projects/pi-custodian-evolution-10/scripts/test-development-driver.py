#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Driver mechanics tests with fake author/native commands; no model or live writes."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name("run-development.py")
spec = importlib.util.spec_from_file_location("development_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
ROOT = Path(__file__).resolve().parents[1]


class DriverTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / "artifacts/driver-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent, prefix="fixture-")
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        live = Path("C:/Users/villa/dev/.pi/durable/repo-custodian")
        for name in driver.ALLOWED:
            target = self.project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((live / name).read_bytes())
        config = {"provider": {"model": driver.MODEL, "thinkingLevel": "medium", "catalogFile": "catalog.json", "piCliPath": "fixture-pi.js"}}
        driver.write_json(self.project / "config.evo10.json", config)
        self.request = {"id": "custodian-evo10-development-20261025", "digest": "f" * 64,
                        "allowedPaths": list(driver.ALLOWED), "evidence": [{"id": "fixture-evidence-id"}],
                        "source": [{"path": name, "sha256": driver.sha((self.project / name).read_bytes())} for name in driver.ALLOWED],
                        "configDigest": driver.sha((self.project / "config.evo10.json").read_bytes()), "frozenVerifier": []}
        driver.write_json(self.root / "request.json", self.request)
        driver.write_json(self.root / "preflight.json", {"passed": True, "mechanicsOnly": True})
        self.args = SimpleNamespace(project=self.project, config="config.evo10.json", request_file=self.root / "request.json",
                                    artifacts=self.root / "run", preflight_file=self.root / "preflight.json", start=True, resume=False)
        self.proposals = {}
        self.calls = []

    def tearDown(self):
        self.temporary.cleanup()

    def fake_command(self, argv, cwd, seconds, max_bytes=0):
        self.calls.append(argv)
        if "--mode" in argv:
            slot = int(cwd.parent.name[1:])
            file = cwd / driver.ALLOWED[0]
            file.write_bytes(file.read_bytes() + f"\nFixture iteration {slot}.\n".encode())
            metadata = {"hypothesis": f"Fixture hypothesis {slot}", "decision": "Mechanics-only fake candidate",
                        "expectedBenefit": "Validate orchestration only", "regressionRisks": ["Not model-quality evidence"]}
            events = [{"type": "tool_execution_start", "toolCallId": "read", "toolName": "read", "args": {"path": driver.ALLOWED[0]}},
                      {"type": "tool_execution_end", "toolCallId": "read", "toolName": "read", "isError": False},
                      {"type": "tool_execution_start", "toolCallId": "write", "toolName": "write", "args": {"path": driver.ALLOWED[0]}},
                      {"type": "tool_execution_end", "toolCallId": "write", "toolName": "write", "isError": False},
                      {"type": "message_end", "message": {"role": "assistant", "provider": driver.PROVIDER, "model": driver.MODEL,
                       "content": [{"type": "thinking", "thinking": "PRIVATE_FIXTURE_THINKING"}, {"type": "text", "text": json.dumps(metadata)}]}}]
            stdout = "\n".join(json.dumps(event) for event in events)
        elif "propose" in argv:
            candidate = driver.read_json(Path(argv[argv.index("--input") + 1]))
            slot = len(self.proposals) + 1
            identity = f"fixture-proposal-{slot}"
            self.proposals[identity] = candidate
            stdout = json.dumps({**candidate, "id": identity})
        else:
            identity = argv[argv.index("--proposal") + 1]
            slot = int(identity.rsplit("-", 1)[1])
            verification = {"passed": True, "score": slot / 10, "cases": [{"id": "mechanics-only", "passed": True, "score": slot / 10}]}
            stdout = json.dumps({"proposalId": identity, "digest": f"{slot:064x}", "passed": True,
                                 "baseline": {"verification": {**verification, "score": 0}}, "candidate": {"verification": verification}})
        return {"returnCode": 0, "timedOut": False, "overflow": False, "durationSeconds": 0,
                "stdout": stdout, "stderr": ""}

    def test_ten_slots_native_calls_best_seeds_and_no_live_mutation(self):
        before = {name: (self.project / name).read_bytes() for name in driver.ALLOWED}
        with patch.object(driver, "run_command", self.fake_command):
            result = driver.run_study(self.args)
        self.assertTrue(result["completedRequestedSlots"])
        self.assertEqual(result["startedSlots"], 10)
        self.assertEqual(result["finishedSlots"], 10)
        self.assertEqual(result["best"]["slot"], 10)
        self.assertEqual(len(self.calls), 30)
        self.assertFalse(result["automaticActivation"])
        for name, data in before.items():
            self.assertEqual((self.project / name).read_bytes(), data)
        last = result["iterations"][-1]
        self.assertEqual(last["seed"], 9)
        for events in self.args.artifacts.rglob("author-events.public.jsonl"):
            self.assertNotIn("PRIVATE_FIXTURE_THINKING", events.read_text())

    def test_protected_function_edit_is_refused(self):
        original = (self.project / driver.ALLOWED[1]).read_text()
        self.assertIn('def environment():', original)
        altered = original.replace('def environment():', 'def environment():\n    raise RuntimeError("forbidden")')
        with self.assertRaises(ValueError):
            driver.python_scope(original, altered)
        with self.assertRaises(ValueError):
            driver.python_scope(original, original + '\nDENY = None\n')
        with self.assertRaises(ValueError):
            driver.python_scope(original, original + '\nCustodian.scan = lambda self, blobs: None\n')

    def test_tool_execute_and_dynamic_description_changes_are_refused(self):
        text = (self.project / driver.ALLOWED[2]).read_text()
        with self.assertRaises(ValueError):
            driver.tool_scope(text, text.replace("600000", "1"))
        with self.assertRaises(ValueError):
            driver.tool_scope(text, text.replace("description:'", "description:`${danger()}"))

    def test_outside_read_tool_error_wrong_model_are_trace_failures(self):
        stdout = "\n".join(json.dumps(event) for event in [
            {"type": "tool_execution_start", "toolCallId": "x", "toolName": "read", "args": {"path": "../secret"}},
            {"type": "tool_execution_end", "toolCallId": "x", "toolName": "read", "isError": True},
            {"type": "message_end", "message": {"role": "assistant", "model": "wrong", "provider": "wrong", "content": []}}])
        _, check, _ = driver.trace_check(stdout, self.project)
        self.assertFalse(check["passed"])
        self.assertIn("outside-allowed-file", check["findings"])
        self.assertIn("tool-error", check["findings"])
        self.assertIn("observed-model-mismatch", check["findings"])

    def test_preflight_gate_must_pass_and_dry_run_has_no_calls(self):
        self.args.start = False
        with patch.object(driver, "run_command", side_effect=AssertionError("No process should run")):
            result = driver.run_study(self.args)
        self.assertFalse(result["started"])
        driver.write_json(self.args.preflight_file, {"passed": False})
        with self.assertRaises(ValueError):
            driver.run_study(self.args)

    def test_failed_author_consumes_one_slot_without_retry(self):
        original = self.fake_command
        count = 0

        def command(argv, cwd, seconds, max_bytes=0):
            nonlocal count
            if "--mode" in argv:
                count += 1
                if count == 1:
                    return {"returnCode": 1, "timedOut": False, "overflow": False, "durationSeconds": 0,
                            "stdout": "", "stderr": "fixture failure"}
            return original(argv, cwd, seconds, max_bytes)

        with patch.object(driver, "run_command", command):
            result = driver.run_study(self.args)
        self.assertEqual(result["startedSlots"], 10)
        self.assertEqual(result["iterations"][0]["outcome"], "failed")
        self.assertEqual(count, 10)
        self.assertEqual(len(self.proposals), 9)

    def test_actual_fake_cli_and_timeout_are_bounded(self):
        result = driver.run_command([sys.executable, "-c", "print('{\"mechanicsOnly\":true}')"], self.root, 2)
        self.assertEqual(result["returnCode"], 0)
        self.assertEqual(json.loads(result["stdout"]), {"mechanicsOnly": True})
        stopped = driver.run_command([sys.executable, "-c", "import time;time.sleep(20)"], self.root, .1)
        self.assertTrue(stopped["timedOut"])
        self.assertIsNotNone(stopped["returnCode"])

    def test_private_reasoning_delta_is_omitted(self):
        event = {"type": "message_update", "assistantMessageEvent": {"type": "reasoning_delta", "delta": "PRIVATE_FIXTURE"}}
        self.assertNotIn("PRIVATE_FIXTURE", json.dumps(driver.public_event(event)))


if __name__ == "__main__":
    unittest.main()
