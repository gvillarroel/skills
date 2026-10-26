#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mechanical checks for the independent development-only report extractor."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).with_name("summarize-development-metrics.py")
SPEC = importlib.util.spec_from_file_location("development_metrics", SOURCE)
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


class DevelopmentMetricsTests(unittest.TestCase):
    def setUp(self):
        parent = SOURCE.parent.parent / "artifacts/audits/metrics-negative-controls"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def fixture_arm(self, decision=.915, worker=0):
        cases = ([{"id": f"decision:{index}", "passed": True, "score": .915} for index in range(10)]
                 + [{"id": f"worker:worker-hard-{index}", "passed": True, "score": 1} for index in range(10)]
                 + [{"id": f"worker:worker-soft-{index}", "passed": True, "score": worker} for index in range(8)])
        return {"verification": {"passed": True, "score": .5 * (decision + worker),
                "decisionScore": decision, "workerScore": worker, "cases": cases,
                "mode": "real", "mechanicsOnly": False,
                "observedModel": {"provider": "openai-codex", "model": "gpt-6.1-sol"}}}

    def write_iteration(self, slot, decision=.915, worker=.875):
        folder = self.root / "iterations" / f"i{slot:02}"
        folder.mkdir(parents=True)
        result = {"slot": slot, "qualified": True, "outcome": "qualified", "patchDigest": f"{slot:064x}",
                  "proposalId": f"test-only-{slot}"}
        evaluation = {"passed": True, "proposalId": result["proposalId"],
                      "baseline": self.fixture_arm(), "candidate": self.fixture_arm(decision, worker)}
        (folder / "iteration-result.json").write_text(json.dumps(result), encoding="utf-8")
        (folder / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
        trace = [{"type": "message_end", "message": {"role": "assistant", "provider": "openai-codex",
                  "model": "gpt-6.1-sol", "thinkingLevel": "medium"}},
                 {"type": "message_update", "message": {"role": "assistant"}},
                 {"type": "message_end", "message": {"role": "toolResult"}}]
        (folder / "author-events.public.jsonl").write_text("\n".join(map(json.dumps, trace)), encoding="utf-8")
        return folder

    def test_equal_decision_composite_gain_is_worker_only(self):
        self.write_iteration(1)
        report = metrics.summarize(self.root / "iterations")
        delta = report["nativeBest"]["pairedComponentDifferences"]
        self.assertEqual(delta["decisionDelta"], 0)
        self.assertEqual(delta["weightedDecisionContribution"], 0)
        self.assertAlmostEqual(delta["weightedWorkerContribution"], .4375)
        self.assertFalse(delta["decisionGainMeasuredInPair"])
        self.assertIn("No decision-score gain was measured", metrics.markdown(report))

    def test_count_completions_and_distinguish_inherited_flags(self):
        self.write_iteration(1)
        report = metrics.summarize(self.root / "iterations")
        self.assertEqual(report["calls"]["authorAssistantCompletions"], 1)
        self.assertEqual(report["calls"]["evaluatorBatchCompletions"], 2)
        self.assertEqual(report["calls"]["providerInternalHttpAttempts"], "unknown")
        arm = report["iterations"][0]["candidate"]
        self.assertEqual(arm["caseFlags"], {"total": 28, "passed": 28, "failed": 0})
        self.assertEqual(arm["workerHardCases"]["total"], 10)
        self.assertEqual(arm["workerSoftInheritedFlags"]["total"], 8)
        self.assertEqual(arm["effortObservation"], "not-exposed")
        self.assertEqual(report["observedEffortFields"], [{"field": "thinkingLevel", "value": "medium", "completions": 1}])

    def test_partial_iteration_not_counted_and_exact_digest_tiebreak(self):
        self.write_iteration(2)
        self.write_iteration(1)
        (self.root / "iterations/i03").mkdir()
        report = metrics.summarize(self.root / "iterations")
        self.assertEqual(report["completedSlots"], 2)
        self.assertEqual(report["nativeBest"]["slot"], 1)
        self.assertFalse(report["allTenFinished"])

    def test_reserved_root_is_refused(self):
        forbidden = self.root / "evaluator-private/iterations"
        forbidden.mkdir(parents=True)
        with self.assertRaises(ValueError):
            metrics.summarize(forbidden)

    def test_unreported_model_completion_is_not_fabricated(self):
        arm = metrics.evaluation_arm({})
        self.assertFalse(arm["available"])
        self.assertEqual(arm["observedEvaluatorCompletions"], 0)
        fake = self.fixture_arm()
        fake["verification"]["mode"] = "mechanics"
        fake["verification"]["mechanicsOnly"] = True
        self.assertEqual(metrics.evaluation_arm(fake)["observedEvaluatorCompletions"], 0)

    def test_failed_flag_and_bad_composite_are_visible(self):
        fake = self.fixture_arm()
        fake["verification"]["cases"][0]["passed"] = False
        fake["verification"]["score"] = .99
        arm = metrics.evaluation_arm(fake)
        self.assertFalse(arm["compositeMatchesFrozenWeights"])
        self.assertEqual(arm["decisionSafetySchemaFlags"]["failed"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
