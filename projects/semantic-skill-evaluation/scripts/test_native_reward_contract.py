#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prevent primary-only Oracle success from authorizing an impossible gate."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("reward_contract", Path(__file__).with_name("check_native_reward_contract.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

CONFIG = {"schemaVersion": 2, "harbor": {"rewardKey": "reward", "passThreshold": 1, "requiredRewards": {"artifact_gate": 1}}}


def oracle():
    return {"schemaVersion": 1, "source": "harbor", "harborVersion": "0.18.0", "rewardKey": "reward", "passThreshold": 1,
            "jobs": [{"complete": True, "completenessProblems": [],
                      "summary": {"requestedTrials": 2, "completedTrials": 2, "passedTrials": 2, "erroredTrials": 0},
                      "trials": [{"agent": "oracle", "passed": True, "error": None, "rewards": {"reward": 1, "artifact_gate": 1}} for _ in range(2)]}]}


class RewardContractTests(unittest.TestCase):
    def test_complete_actual_interface_accepts_multiple_cohorts(self):
        result = guard.inspect(CONFIG, [oracle(), oracle()])
        self.assertTrue(result["passed"])
        self.assertEqual(result["trialsChecked"], 4)

    def test_primary_success_cannot_hide_absent_required_metric(self):
        report = oracle()
        for trial in report["jobs"][0]["trials"]:
            del trial["rewards"]["artifact_gate"]
        result = guard.inspect(CONFIG, [report])
        self.assertFalse(result["passed"])
        self.assertEqual(result["failureCounts"], {"missing-required-reward:artifact_gate": 2})

    def test_boolean_or_below_threshold_gate_cannot_pass(self):
        for value in (True, 0):
            with self.subTest(value=value):
                report = oracle()
                report["jobs"][0]["trials"][0]["rewards"]["artifact_gate"] = value
                self.assertFalse(guard.inspect(CONFIG, [report])["passed"])

    def test_clean_topline_cannot_hide_incomplete_or_wrong_agent_evidence(self):
        for mutate in (lambda r: r["jobs"][0].update(complete=False),
                       lambda r: r["jobs"][0]["trials"][0].update(agent="evaluated-skill")):
            report = oracle()
            mutate(report)
            self.assertFalse(guard.inspect(CONFIG, [report])["passed"])

    def test_reordered_json_objects_do_not_change_preflight(self):
        report = oracle()
        report["jobs"][0]["trials"][0]["rewards"] = {"artifact_gate": 1, "reward": 1}
        self.assertEqual(guard.inspect(CONFIG, [report]), guard.inspect(CONFIG, [oracle()]))

    def test_conflicting_or_invalid_contract_is_not_silently_repaired(self):
        report = oracle()
        report["rewardKey"] = "different-primary"
        self.assertFalse(guard.inspect(CONFIG, [report])["passed"])
        config = deepcopy(CONFIG)
        config["harbor"]["requiredRewards"]["artifact_gate"] = float("nan")
        with self.assertRaises(ValueError):
            guard.inspect(config, [oracle()])


if __name__ == "__main__":
    unittest.main()
