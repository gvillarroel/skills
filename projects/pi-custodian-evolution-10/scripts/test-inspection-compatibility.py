#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mechanical negative controls for the separate inspection compatibility check."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("check-inspection-compatibility.py")
spec = importlib.util.spec_from_file_location("inspection_compatibility_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
STUDY = Path(__file__).resolve().parents[1]
BASELINE = Path("C:/Users/villa/dev/.pi/durable/repo-custodian")


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        parent = STUDY / "artifacts/audits/compatibility-negative-controls"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="input-", dir=parent)
        self.root = Path(self.temporary.name)
        self.baseline_bytes = (BASELINE / "scripts/custodian.py").read_bytes()
        self.before = checker.sha(self.baseline_bytes)

    def tearDown(self):
        self.assertEqual(checker.sha((BASELINE / "scripts/custodian.py").read_bytes()), self.before)
        self.temporary.cleanup()

    def check(self, replacement=None):
        paths = []
        if replacement is not None:
            target = self.root / "negative-source.json"
            target.write_text(json.dumps({"changes": [{"path": "scripts/custodian.py",
                "beforeHash": self.before, "content": replacement}]}), encoding="utf-8")
            paths.append(target)
        args = SimpleNamespace(baseline_project=BASELINE, candidate_file=paths, iterations_root=None,
                               temporary_root=STUDY / "artifacts/c")
        return checker.run(args)

    def test_actual_original_api_passes(self):
        result = self.check()
        self.assertTrue(result["passed"])
        self.assertTrue(result["baselineCompatibility"]["passed"])

    def test_missing_policy_information_is_rejected(self):
        source = self.baseline_bytes.decode("utf-8")
        needle = '"validationCommands": self.commands(repo), '
        self.assertEqual(source.count(needle), 1)
        result = self.check(source.replace(needle, ""))
        self.assertFalse(result["passed"])
        failures = [item["name"] for item in result["candidates"][0]["manualCompatibility"]["checks"] if not item["passed"]]
        self.assertEqual(failures, ["validation-policy-capability-preserved"])

    def test_incomplete_policy_is_not_equivalent(self):
        source = self.baseline_bytes.decode("utf-8")
        needle = '"validationCommands": self.commands(repo)'
        self.assertEqual(source.count(needle), 1)
        result = self.check(source.replace(needle, '"validationCommands": []'))
        self.assertFalse(result["passed"])

    def test_claimed_execution_without_running_checks_is_rejected(self):
        source = self.baseline_bytes.decode("utf-8")
        needle = '"ownedMerge": self.saved(repo), '
        self.assertEqual(source.count(needle), 1)
        patched = source.replace(needle, needle + '"validationStatus": "passed", "validationReceipts": [{"status": "passed"}], ')
        result = self.check(patched)
        self.assertFalse(result["passed"])
        failures = [item["name"] for item in result["candidates"][0]["manualCompatibility"]["checks"] if not item["passed"]]
        self.assertEqual(failures, ["checks-not-claimed-passed"])


if __name__ == "__main__":
    unittest.main()
