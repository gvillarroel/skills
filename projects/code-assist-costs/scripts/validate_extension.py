#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy==2.3.5"]
# ///
"""Independently audit the policy-study CSV extension without importing its model."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-9), (a, b)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    project = Path(__file__).resolve().parents[1]
    root.relative_to(project)
    out = root / "analysis/policy-study"
    manifest = json.loads((out / "manifest.json").read_text())
    study = json.loads((root / "study-20260906.json").read_text())
    assert manifest["coreSpecSha256"] == sha(root / "experiment.json")
    for name, value in manifest["sourceHashes"].items():
        path = (project / name).resolve()
        path.relative_to(project)
        assert sha(path) == value, name
    for table in manifest["tables"]:
        path = (out / table["path"]).resolve()
        path.relative_to(out)
        assert sha(path) == table["sha256"], path
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == table["columns"]
            assert sum(1 for _ in reader) == table["rows"]
    policies = {r["policy_id"]: r for r in read_csv(out / "policies.csv")}
    assert len(policies) == manifest["policyCount"] == 5760
    grid = defaultdict(list)
    for row in read_csv(out / "policy-grid.csv"):
        assert row["source_type"] == "simulated"
        near(float(row["correct_completion"]) + float(row["undetected_error"]) + float(row["exhausted"]), 1)
        near(row["spend_per_correct_usd"], float(row["spend_usd"]) / float(row["correct_completion"]))
        near(row["spend_usd"], float(row["token_usd"]) + float(row["fees_usd"]))
        loss = study["workloads"][row["workload"]]
        near(row["risk_adjusted_usd"], float(row["spend_usd"]) + float(row["undetected_error"]) * loss["undetected_loss_usd"] + float(row["exhausted"]) * loss["rework_loss_usd"])
        expected_feasible = float(row["correct_completion"]) >= study["selection"]["correct_completion_min"] and float(row["undetected_error"]) <= study["selection"]["undetected_error_max"]
        assert (row["feasible"] == "True") == expected_feasible
        for key, value in policies[row["policy_id"]].items():
            if key != "source_type":
                assert row[key] == value
        grid[row["workload"], row["world"]].append(row)
    assert sum(map(len, grid.values())) == manifest["gridCells"] == 51840
    for block in grid.values():
        assert len(block) == len({r["policy_id"] for r in block}) == 5760
    objectives = {"minimum-token-spend": "token_usd", "minimum-expected-loss": "risk_adjusted_usd", "minimum-spend-per-correct-with-quality-floor": "spend_per_correct_usd"}
    for winner in read_csv(out / "selected-policies.csv"):
        block = grid[winner["workload"], winner["world"]]
        if winner["objective"] == "minimum-spend-per-correct-with-quality-floor":
            block = [r for r in block if r["feasible"] == "True"]
        assert len(block) == int(winner["eligible_policies"])
        if not block:
            assert winner["status"] == "infeasible" and not winner["policy_id"]
        else:
            metric = objectives[winner["objective"]]
            best = min(block, key=lambda r: (float(r[metric]), r["policy_id"]))
            assert best["policy_id"] == winner["policy_id"]
            for name in ["token_usd", "spend_per_correct_usd", "correct_completion", "undetected_error", "risk_adjusted_usd"]:
                near(best[name], winner[name])
    for winner in read_csv(out / "robust-regret.csv"):
        losses = {world: {r["policy_id"]: float(r["risk_adjusted_usd"]) for r in grid[winner["workload"], world]} for world in study["qualityWorlds"]}
        minima = {w: min(values.values()) for w, values in losses.items()}
        candidates = [(max(losses[w][pid] - minima[w] for w in losses), pid) for pid in policies]
        regret, pid = min(candidates)
        assert winner["policy_id"] == pid
        near(winner["max_regret_usd"], regret)
    ledger_rows = 0
    for row in read_csv(out / "request-ledger.csv"):
        card = study["rateCards"][row["model_id"]]
        ordinary, read, write, output = (int(row[k]) for k in ["uncached", "read", "write", "output"])
        near(int(row["input"]), ordinary+read+write)
        long = int(row["input"]) > card["threshold_tokens"]
        near(row["usd"], ((ordinary*card["input_usd_mtok"] + read*card["read_usd_mtok"] + write*card["write_usd_mtok"])*(card["long_input_factor"] if long else 1)
                          + output*card["output_usd_mtok"]*(card["long_output_factor"] if long else 1))/1e6)
        ledger_rows += 1
    groups = defaultdict(list)
    with (out / "synthetic-months.csv").open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            groups[row["model"], row["profile"], row["tasks_per_month"]].append((int(row["month_id"]), float(row["token_usd"]), int(row["correct_tasks"])))
    for row in read_csv(out / "monthly-risk.csv"):
        samples = groups[row["model"], row["profile"], row["tasks_per_month"]]
        n = int(row["synthetic_months"])
        assert sorted(x[0] for x in samples) == list(range(1, n+1))
        values = np.array([x[1] for x in samples])
        near(row["mc_mean_token_usd"], values.mean())
        near(row["mean_mcse_usd"], values.std(ddof=1)/math.sqrt(n))
        near(row["predictive_p05_usd"], np.quantile(values, .05))
        near(row["predictive_p95_usd"], np.quantile(values, .95))
        risk = float(np.mean(values > float(row["budget_usd"])))
        near(row["probability_over_budget"], risk)
        epsilon = math.sqrt(math.log(40)/(2*n))
        near(row["risk_mc_interval_low"], max(0, risk-epsilon))
        near(row["risk_mc_interval_high"], min(1, risk+epsilon))
        near(row["mc_mean_correct_fraction"], np.mean([x[2] for x in samples])/int(row["tasks_per_month"]))
        for plan in study["billing"]["plans"]:
            near(row[f"{plan['id']}_expected_invoice_usd"], np.mean(plan["fee"]+np.maximum(values-plan["allowance"], 0)))
    report = {"ok": True, "validationScope": "Extension integrity, accounting, selection and Monte Carlo summary replay; no empirical validity or completeness certificate.",
              "tables": len(manifest["tables"]), "gridCells": 51840, "ledgerRows": ledger_rows, "monthlyRows": sum(map(len, groups.values())),
              "validatorSha256": sha(Path(__file__)), "manifestSha256": sha(out / "manifest.json"), "numpyVersion": np.__version__}
    (out / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
