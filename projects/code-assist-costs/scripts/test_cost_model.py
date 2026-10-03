#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent arithmetic, boundary and activation checks of the offline model."""

from __future__ import annotations

import argparse
import ast
import copy
import csv
import importlib.util
import json
import math
from pathlib import Path
import unittest

from build_study import PROJECT, PARAMETERS, load_study, parameters

module_spec = importlib.util.spec_from_file_location("cost_model", PROJECT / "source/model.py")
model = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(model)
STUDY = load_study()


def configured(**changes):
    return parameters(STUDY, "luna", "baseline", "long", "smooth") | changes


def oracle(p, first, second):
    a, b = first["p"], second["p"]
    sensitivity, specificity = p["validator_sensitivity"], p["validator_specificity"]
    both = p["retry_dependence"] * min(a, b) + (1 - p["retry_dependence"]) * a * b
    correct = a * specificity
    undetected = (1 - a) * (1 - sensitivity)
    reach2 = 1 - correct - undetected if p["attempt_cap"] == 2 else 0
    if p["attempt_cap"] == 2:
        correct += (both * (1 - specificity) + (b - both) * sensitivity) * specificity
        undetected += ((a - both) * (1 - specificity) + (1 - a - b + both) * sensitivity) * (1 - sensitivity)
    return {"correct_completion": correct, "undetected_error": undetected, "exhausted": 1 - correct - undetected,
            "attempts": 1 + reach2, "spend_usd": first["cost"] + reach2 * second["cost"]}


class ModelTests(unittest.TestCase):
    def test_no_target_capability_imports(self):
        tree = ast.parse((PROJECT / "source/model.py").read_text())
        imports = {name.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for name in n.names}
        self.assertEqual(imports, {"itertools", "math", "platform"})

    def test_bill_buckets(self):
        card = STUDY["rateCards"]["terra"]
        row = {"input": 6000, "uncached": 1000, "read": 2000, "write": 3000, "output": 400}
        self.assertAlmostEqual(model.bill(row, card), 0.002 + 0.0004 + 0.0075 + 0.0048)
        with self.assertRaises(AssertionError):
            model.bill(row | {"input": 6001}, card)

    def test_threshold_and_route(self):
        card = STUDY["rateCards"]["luna"]
        for n in [199999, 200000, 200001, 272000, 272001]:
            row = {"input": n, "uncached": n, "read": 0, "write": 0, "output": 1000}
            expected = n * 0.2 / 1e6 * (2 if n > 200000 else 1) + .0012 * (1.5 if n > 200000 else 1)
            self.assertAlmostEqual(model.bill(row, card), expected)
            if 200000 < n <= 272000:
                self.assertLess(model.bill(row, card | {"threshold_tokens": 272000}), expected)

    def test_ten_call_prefix_oracle(self):
        card = STUDY["rateCards"]["luna"]
        rows = [{"input": 1000, "uncached": 0, "read": 1000 if i else 0, "write": 0 if i else 1000, "output": 0} for i in range(10)]
        # Marginal 1k inside a larger eligible prefix; not a stand-alone 1k cache entry.
        self.assertAlmostEqual(sum(model.bill(r, card) for r in rows), .00043)

    def test_batch_dependencies_and_tool_counts(self):
        p = configured(batch_size=2)
        a = model.attempt(p, p["first_model"])
        self.assertEqual(len(a["rows"]), 39)  # The long workload is sequential.
        p["max_independent_batch"] = 2
        b = model.attempt(p, p["first_model"])
        self.assertEqual(len(b["rows"]), 20)
        self.assertEqual(sum(x["tools"] for x in b["rows"]), 38)
        self.assertLess(b["cost"], a["cost"])

    def test_compaction_overshoot_and_rebuild(self):
        p = configured(context_cap_tokens=200000)
        a = model.attempt(p, p["first_model"])
        self.assertGreater(a["compactions"], 0)
        self.assertTrue(all(r["input"] <= 200000 for r in a["rows"] if r["kind"] == "main"))
        self.assertTrue(all(r["input"] > 200000 and r["long_tier"] for r in a["rows"] if r["kind"] == "compaction"))
        b = model.attempt(p | {"compaction_input_mode": "read", "preserve_static_prefix": True}, p["first_model"])
        self.assertLess(b["cost"], a["cost"])

    def test_cache_expiry_churn_and_last_suffix(self):
        p = configured()
        a = model.attempt(p, p["first_model"])
        expired = model.attempt(p | {"think_gap_seconds": 2400}, p["first_model"])
        churn = model.attempt(p | {"churn_every": 1}, p["first_model"])
        self.assertEqual(expired["read"], 0)
        self.assertEqual(churn["read"], 0)
        self.assertLess(a["cost"], expired["cost"])
        end = model.attempt(p | {"cache_mode": "terminal-uncached"}, p["first_model"])
        self.assertEqual(end["rows"][-1]["write"], 0)
        self.assertLess(end["cost"], a["cost"])

    def test_terminal_mass_and_closed_form(self):
        for a in [0, .1, .7, 1]:
            for b in [0, .2, .9, 1]:
                for dependence in [0, .35, .8, 1]:
                    for cap in [1, 2]:
                        p = configured(attempt_cap=cap, retry_dependence=dependence)
                        first = {"p": a, "token_cost": 2, "fee": .1, "cost": 2.1}
                        second = {"p": b, "token_cost": 3, "fee": .2, "cost": 3.2}
                        rows = model.terminal_distribution(first, second, p)
                        expected = oracle(p, first, second)
                        self.assertAlmostEqual(sum(x["probability"] for x in rows), 1)
                        for outcome, status in [("correct_completion", "correct"), ("undetected_error", "undetected"), ("exhausted", "exhausted")]:
                            self.assertAlmostEqual(sum(x["probability"] for x in rows if x["status"] == status), expected[outcome])
                        self.assertAlmostEqual(sum(x["probability"] * (x["token_usd"] + x["fee_usd"]) for x in rows), expected["spend_usd"])

    def test_repeatability_and_rival(self):
        p = configured(context_cap_tokens=100000)
        self.assertEqual(model.evaluate(p), model.evaluate(copy.deepcopy(p)))
        rival = parameters(STUDY, "luna", "cap-100k", "long", "critical-cliff")
        self.assertNotEqual(model.evaluate(rival)[0]["correct_completion"], model.evaluate(p)[0]["correct_completion"])


def activation(output):
    rows = []
    for key in PARAMETERS:
        witness = None
        for workload in STUDY["workloads"]:
            if witness:
                break
            for world in STUDY["qualityWorlds"]:
                if witness:
                    break
                for profile in STUDY["coreProfiles"]:
                    p = parameters(STUDY, "luna", profile, workload, world)
                    changed = copy.deepcopy(p)
                    value = p[key]
                    replacements = {
                        "first_model": STUDY["rateCards"]["sol"], "retry_model": STUDY["rateCards"]["sol"],
                        "cache_mode": "off", "compaction_input_mode": "read", "quality_mechanism": "critical-cliff",
                        "evidence_position": "uniform", "cache_ttl_seconds": {k: 1 for k in STUDY["rateCards"]},
                        "quality_probabilities": {k: .5 for k in STUDY["rateCards"]},
                        "attempt_cap": 2, "context_cap_tokens": 100000, "churn_every": 1,
                        "summary_fidelity": .5, "retry_dependence": .95,
                        "validator_sensitivity": .5, "validator_specificity": .5,
                        "idle_every": 1, "idle_gap_seconds": 2400, "think_gap_seconds": 2400,
                        "result_retention": .25, "output_multiplier": .25,
                    }
                    changed[key] = replacements.get(key, (not value) if isinstance(value, bool) else value * 1.2 + 1 if isinstance(value, (int, float)) else value)
                    before = model.evaluate(p)
                    after = model.evaluate(changed)
                    if before != after:
                        difference = next((name for name in before[0] if before[0][name] != after[0][name]), "ledger-or-quality-state")
                        witness = {"parameter": key, "status": "active", "workload": workload, "world": world, "profile": profile,
                                   "changed_from": json.dumps(value, sort_keys=True), "changed_to": json.dumps(changed[key], sort_keys=True), "first_changed_outcome": difference}
                        break
        rows.append(witness or {"parameter": key, "status": "no-witness", "workload": "", "world": "", "profile": "", "changed_from": "", "changed_to": "", "first_changed_outcome": ""})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    missing = [x["parameter"] for x in rows if x["status"] != "active"]
    print(json.dumps({"activationWitnesses": len(rows) - len(missing), "parameters": len(rows), "missing": missing}))
    assert not missing, missing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--activation-output", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ModelTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.activation_output:
        activation(args.activation_output)
