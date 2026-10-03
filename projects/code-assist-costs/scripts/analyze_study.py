#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy==2.3.5"]
# ///
"""Run a frozen offline policy grid and synthetic monthly risk extension.

Run with the local Python interpreter when its installed NumPy is used; the
manifest records that version. The uv metadata supplies a reproducible fallback.
No target harness, model service, credential, or network client is invoked.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import platform

import numpy as np

from build_study import PROJECT, load_study, parameters
from test_cost_model import oracle

model_spec = importlib.util.spec_from_file_location("cost_model_analysis", PROJECT / "source/model.py")
model = importlib.util.module_from_spec(model_spec)
model_spec.loader.exec_module(model)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    assert rows, path
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def checked(p):
    result, first, second, terminal = model.evaluate(p)
    expected = oracle(p, first, second)
    for name, value in expected.items():
        assert math.isclose(value, result[name], rel_tol=1e-10, abs_tol=1e-12), name
    for attempt in [first, second]:
        for row in attempt["rows"]:
            card = p["first_model"] if row["model_id"] == p["first_model"]["model_id"] else p["retry_model"]
            assert row["input"] == row["read"] + row["write"] + row["uncached"]
            assert min(row[k] for k in ["read", "write", "uncached", "input", "output"]) >= 0
            multiplier = card["long_input_factor"] if row["input"] > card["threshold_tokens"] else 1
            out_multiplier = card["long_output_factor"] if row["input"] > card["threshold_tokens"] else 1
            independent = ((row["input"] - row["read"] - row["write"]) * card["input_usd_mtok"] * multiplier
                           + row["read"] * card["read_usd_mtok"] * multiplier + row["write"] * card["write_usd_mtok"] * multiplier
                           + row["output"] * card["output_usd_mtok"] * out_multiplier) / 1e6
            assert math.isclose(independent, row["usd"], rel_tol=1e-12, abs_tol=1e-12)
            if row["kind"] == "main":
                assert row["input"] <= p["context_cap_tokens"]
    result["spend_per_correct_usd"] = result["spend_usd"] / result["correct_completion"]
    return result, first, second, terminal


def core_tables(study, root, out):
    observed = {}
    with (root / "data/runs.csv").open(encoding="utf-8", newline="") as stream:
        run_keys = {x["run_id"]: (x["scenario_id"], x["design_point_id"]) for x in csv.DictReader(stream)}
    with (root / "data/outcomes.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            observed[(*run_keys[row["run_id"]], row["outcome_name"])] = float(row["value"])
    rows, ledgers, changes, lookup = [], [], [], {}
    for mid, profile, workload, world in itertools.product(study["rateCards"], study["coreProfiles"], study["workloads"], study["qualityWorlds"]):
        p = parameters(study, mid, profile, workload, world)
        result, first, second, terminal = checked(p)
        for name, value in result.items():
            if name != "spend_per_correct_usd":
                assert math.isclose(value, observed[(f"{mid}-{profile}", f"{workload}-{world}", name)], rel_tol=1e-12, abs_tol=1e-12)
        key = (mid, profile, workload, world)
        lookup[key] = result
        rows.append({"source_type": "simulated", "model": mid, "profile": profile, "workload": workload, "world": world, **result,
                     "first_attempt_correctness": first["p"], "first_attempt_tokens_usd": first["token_cost"],
                     "first_main_calls": sum(r["kind"] == "main" for r in first["rows"]),
                     "first_compactions": first["compactions"], "first_long_tier_calls": sum(r["long_tier"] for r in first["rows"])})
        if world == "smooth":  # The ledger is unchanged across quality worlds for a fixed attempt.
            for index, attempt in enumerate([first, second] if p["attempt_cap"] == 2 else [first], 1):
                ledgers.extend({"source_type": "simulated", "model": mid, "profile": profile, "workload": workload,
                                "planned_attempt": index, **r} for r in attempt["rows"])
    for mid, profile, workload, world in lookup:
        if profile == "baseline":
            continue
        result, baseline = lookup[(mid, profile, workload, world)], lookup[(mid, "baseline", workload, world)]
        delta_correct = result["correct_completion"] - baseline["correct_completion"]
        delta_spend = result["spend_usd"] - baseline["spend_usd"]
        break_even = delta_spend / delta_correct if delta_correct and delta_spend / delta_correct >= 0 else ""
        changes.append({"source_type": "simulated", "model": mid, "profile": profile, "workload": workload, "world": world,
                        "delta_spend_usd": delta_spend, "delta_token_usd": result["token_usd"] - baseline["token_usd"],
                        "delta_correct_completion": delta_correct, "delta_risk_adjusted_usd": result["risk_adjusted_usd"] - baseline["risk_adjusted_usd"],
                        "spend_change_pct": 100 * delta_spend / baseline["spend_usd"],
                        "delta_usd_per_1000_tasks": delta_spend * 1000, "delta_usd_per_million_tasks": delta_spend * 1e6,
                        "equal_loss_per_failed_task_break_even_usd": break_even,
                        "break_even_note": "Equal loss for every non-correct-completed task, unlike the primary two-loss objective; blank means no nonnegative crossing."})
    write_csv(out / "core-results.csv", rows)
    write_csv(out / "request-ledger.csv", ledgers)
    write_csv(out / "one-factor-effects.csv", changes)
    return lookup


def grid_tables(study, out):
    controls = list(study["grid"])
    policies = []
    for mid in study["rateCards"]:
        for values in itertools.product(*(study["grid"][x] for x in controls)):
            policies.append({"policy_id": f"g{len(policies)+1:05d}", "model": mid, **dict(zip(controls, values))})
    results, winners, robustness = [], [], []
    for workload in study["workloads"]:
        world_results = {}
        for world in study["qualityWorlds"]:
            block = []
            for policy in policies:
                p = parameters(study, policy["model"], "baseline", workload, world)
                p.update({k: policy[k] for k in controls if k != "retry_policy"})
                p["attempt_cap"] = 1 if policy["retry_policy"] == "single" else 2
                retry = study["escalation"][policy["model"]] if policy["retry_policy"] == "escalate" else policy["model"]
                p["retry_model"] = study["rateCards"][retry]
                result, first, second, terminal = checked(p)
                feasible = result["correct_completion"] >= study["selection"]["correct_completion_min"] and result["undetected_error"] <= study["selection"]["undetected_error_max"]
                row = {"source_type": "simulated", **policy, "workload": workload, "world": world, "feasible": feasible, **result}
                block.append(row)
            results.extend(block)
            world_results[world] = {x["policy_id"]: x for x in block}
            for objective, metric, eligible in [
                ("minimum-token-spend", "token_usd", block),
                ("minimum-expected-loss", "risk_adjusted_usd", block),
                ("minimum-spend-per-correct-with-quality-floor", "spend_per_correct_usd", [x for x in block if x["feasible"]]),
            ]:
                if not eligible:
                    winners.append({"workload": workload, "world": world, "objective": objective, "status": "infeasible", "eligible_policies": 0,
                                    "policy_id": "", "model": "", "token_usd": "", "spend_per_correct_usd": "", "correct_completion": "", "undetected_error": "", "risk_adjusted_usd": ""})
                    continue
                winner = min(eligible, key=lambda r: (r[metric], r["policy_id"]))
                winners.append({"workload": workload, "world": world, "objective": objective, "status": "selected-under-model", "eligible_policies": len(eligible),
                                **{k: winner[k] for k in ["policy_id", "model", "token_usd", "spend_per_correct_usd", "correct_completion", "undetected_error", "risk_adjusted_usd"]}})
        best_loss = {world: min(r["risk_adjusted_usd"] for r in block.values()) for world, block in world_results.items()}
        robust_candidates = []
        for policy in policies:
            pid = policy["policy_id"]
            max_regret = max(block[pid]["risk_adjusted_usd"] - best_loss[world] for world, block in world_results.items())
            robust_candidates.append((max_regret, pid))
        regret, pid = min(robust_candidates)
        robustness.append({"workload": workload, "objective": "minimax-absolute-expected-loss-regret", "policy_id": pid, "max_regret_usd": regret,
                           "feasible_all_worlds": all(block[pid]["feasible"] for block in world_results.values()),
                           "note": "Finite declared worlds without probability weights; not a real-world guarantee."})
    write_csv(out / "policies.csv", [{"source_type": "assumed", **p} for p in policies])
    write_csv(out / "policy-grid.csv", results)
    write_csv(out / "selected-policies.csv", winners)
    write_csv(out / "robust-regret.csv", robustness)
    return {"policies": len(policies), "gridCells": len(results), "selections": winners, "robustness": robustness}


def supplemental(study, out):
    rows, prefix, routes, billing = [], [], [], []
    conf = study["supplementalSensitivity"]
    for mid, profile, world in itertools.product(study["rateCards"], ["baseline", "cap-100k", "cap-200k", "cap-200k-reuse", "escalate-two"], study["qualityWorlds"]):
        for parameter, levels in [
            ("summary_fidelity", conf["summaryFidelities"]), ("retry_dependence", conf["retryDependence"]),
            ("rot_onset_tokens", conf["rotOnsets"]), ("idle_gap_seconds", conf["cacheIdleSeconds"]), ("rework_loss_usd", conf["reworkLosses"]),
        ]:
            for level in levels:
                p = parameters(study, mid, profile, "long", world) | {parameter: level}
                result, first, second, terminal = checked(p)
                rows.append({"source_type": "simulated", "model": mid, "profile": profile, "workload": "long", "world": world,
                             "parameter": parameter, "value": level, **result})
    for mid, card in study["rateCards"].items():
        n, tokens = conf["prefixCalls"], conf["prefixAddedTokens"]
        for mode, cost in [("one-write-rest-reads", tokens * (card["write_usd_mtok"] + (n-1)*card["read_usd_mtok"]) / 1e6),
                           ("ordinary-input-every-call", n*tokens*card["input_usd_mtok"]/1e6),
                           ("write-every-call-no-hits", n*tokens*card["write_usd_mtok"]/1e6)]:
            prefix.append({"source_type": "simulated", "model": mid, "cache_case": mode, "calls_per_task": n, "added_system_tokens": tokens,
                           "delta_usd_per_task": cost, "delta_usd_per_1000_tasks": cost*1000, "delta_usd_per_million_tasks": cost*1e6,
                           "condition": "Marginal addition inside an eligible prefix; no price tier crossing, compaction, output or quality change."})
    for n in conf["routeInputs"]:
        for name, threshold in [("copilot", 200000), ("direct-api", 272000)]:
            card = study["rateCards"]["luna"] | {"threshold_tokens": threshold}
            row = {"input": n, "uncached": 0, "read": n, "write": 0, "output": 1000}
            routes.append({"source_type": "simulated", "route": name, "input_tokens": n, "output_tokens": 1000, "input_bucket": "fully-cached-read", "usd_per_request": model.bill(row, card)})
    # Piecewise examples and exact pairwise fee crossings, not capacity claims.
    for usage in [0, 10, 15, 30, 44, 50, 70, 100, 131, 150, 200, 1000, 100000]:
        charges = {p["id"]: p["fee"] + max(usage-p["allowance"], 0) for p in study["billing"]["plans"]}
        billing.append({"token_usage_usd": usage, **charges, "lowest_invoice_plan": min(charges, key=charges.get),
                        "interpretation": "Invoice at stated usage, not expected invoice of an uncertain month."})
    write_csv(out / "sensitivity.csv", rows)
    write_csv(out / "system-prefix-monthly.csv", prefix)
    write_csv(out / "luna-route-boundary.csv", routes)
    write_csv(out / "subscription-invoices.csv", billing)


def monthly(study, out):
    cfg = study["monthlyMonteCarlo"]
    output, traces = [], []
    for mid, profile, volume in itertools.product(cfg["models"], cfg["profiles"], study["billing"]["monthlyVolumes"]):
        seed_material = f"{cfg['seed']}:{mid}:{profile}:{volume}:monthly-process-v1".encode()
        seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")
        rng = np.random.Generator(np.random.PCG64(seed))
        count = cfg["replications"]
        shocks = rng.choice(len(cfg["shocks"]), size=count, p=[x["probability"] for x in cfg["shocks"]])
        usage, fee, correct = np.zeros(count), np.zeros(count), np.zeros(count)
        exact_mean, normal_mean = 0, None
        for shock_index, shock in enumerate(cfg["shocks"]):
            categories = []
            for workload, mix in cfg["mixture"].items():
                p = parameters(study, mid, profile, workload, cfg["world"]) | {"quality_shift": shock["quality_shift"]}
                result, first, second, terminal = checked(p)
                for t in terminal:
                    categories.append(t | {"probability": t["probability"] * mix})
            probs = np.array([x["probability"] for x in categories])
            probs /= probs.sum()
            token_values = np.array([x["token_usd"] for x in categories])
            fee_values = np.array([x["fee_usd"] for x in categories])
            good = np.array([x["status"] == "correct" for x in categories], dtype=float)
            mean = volume * float(probs @ token_values)
            exact_mean += shock["probability"] * mean
            if shock_index == 0:
                normal_mean = mean
            mask = shocks == shock_index
            draws = rng.multinomial(volume, probs, size=int(mask.sum()))
            usage[mask] = draws @ token_values
            fee[mask] = draws @ fee_values
            correct[mask] = draws @ good
        mcse = float(np.std(usage, ddof=1) / math.sqrt(count))
        assert abs(float(usage.mean()) - exact_mean) <= max(1e-10, 10*mcse)
        budget = cfg["budgetMultiplier"] * normal_mean
        exceed = float(np.mean(usage > budget))
        epsilon = math.sqrt(math.log(2/.05)/(2*count))
        row = {"source_type": "simulated", "model": mid, "profile": profile, "tasks_per_month": volume,
               "synthetic_months": count, "seed": seed, "exact_mean_token_usd": exact_mean,
               "mc_mean_token_usd": float(usage.mean()), "mean_mcse_usd": mcse,
               "predictive_p05_usd": float(np.quantile(usage, .05)), "predictive_p95_usd": float(np.quantile(usage, .95)),
               "normal_month_expected_usd": normal_mean, "budget_usd": budget, "probability_over_budget": exceed,
               "risk_mc_interval_low": max(0, exceed-epsilon), "risk_mc_interval_high": min(1, exceed+epsilon),
               "mc_mean_correct_fraction": float(correct.mean()/volume),
               "interval_note": "Predictive quantiles are not confidence intervals. Risk interval: pointwise 95% Hoeffding conditional on the invented independent-month process."}
        for plan in study["billing"]["plans"]:
            invoices = plan["fee"] + np.maximum(usage-plan["allowance"], 0) + fee
            row[f"{plan['id']}_expected_invoice_usd"] = float(invoices.mean())
            row[f"{plan['id']}_invoice_at_mean_usage_usd"] = plan["fee"] + max(float(usage.mean()) - plan["allowance"], 0) + float(fee.mean())
        output.append(row)
        traces.extend({"source_type": "simulated", "model": mid, "profile": profile, "tasks_per_month": volume, "month_id": i+1,
                       "shock": cfg["shocks"][int(shocks[i])]["id"], "token_usd": float(usage[i]), "correct_tasks": int(correct[i])}
                      for i in range(count))
    write_csv(out / "monthly-risk.csv", output)
    write_csv(out / "synthetic-months.csv", traces)
    return {"syntheticMonths": len(traces), "cases": len(output), "numpyVersion": np.__version__, "rng": "numpy.Generator-PCG64"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    root.relative_to(PROJECT)
    study = json.loads((root / "study-20260906.json").read_text(encoding="utf-8"))
    assert study == load_study(), "Frozen controls differ from current source"
    assert digest(root / "model.py") == digest(PROJECT / "source/model.py"), "Frozen model differs from current source"
    out = root / "analysis/policy-study"
    out.mkdir(exist_ok=False)
    core_tables(study, root, out)
    grid = grid_tables(study, out)
    supplemental(study, out)
    mc = monthly(study, out)
    inventory = []
    for path in sorted(out.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            count = sum(1 for _ in reader)
        inventory.append({"path": path.name, "sha256": digest(path), "rows": count, "columns": fields})
    manifest = {"schemaVersion": 1, "namespace": "code-assist-policy-study", "phase": "exploratory", "executionBoundary": study["boundary"],
                "pythonVersion": platform.python_version(), "sourceHashes": {str(p.relative_to(PROJECT)): digest(p) for p in [PROJECT / "source/model.py", PROJECT / "source/study-20260906.json", PROJECT / "scripts/analyze_study.py", PROJECT / "scripts/build_study.py", PROJECT / "scripts/test_cost_model.py"]},
                "coreSpecSha256": digest(root / "experiment.json"), "tables": inventory, "policyCount": grid["policies"], "gridCells": grid["gridCells"],
                "monteCarlo": mc, "numericalChecks": {"independentClosedForm": "pass-all-evaluated-cells", "ledgerPriceDotProduct": "pass-all-evaluated-requests", "coreReconciliation": "pass-8568-outcomes", "monthlyExactMeanVsMC": "within-ten-MCSE"},
                "limitations": ["Not a certification by the core bundle validator.", "No empirical calibration of task quality, context rot, harness behavior or monthly shocks.", "A finite grid winner is not a global optimum or a causal real-world result.", "Plan allowances and actual controls or account capacity must be available for a hypothetical policy to be actionable."]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "policies": grid["policies"], "gridCells": grid["gridCells"], **mc, "output": str(out)}))
    print(json.dumps({"selections": grid["selections"], "robustness": grid["robustness"]}))


if __name__ == "__main__":
    main()
