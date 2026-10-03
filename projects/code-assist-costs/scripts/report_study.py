#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a local SQLite exploration surface and report from validated CSVs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sqlite3

from build_study import OUTCOMES, PARAMETERS


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + ["| " + " | ".join(str(x) for x in row) + " |" for row in rows])


def cash(x, digits=3):
    return f"${float(x):,.{digits}f}"


def pct(x):
    return f"{100*float(x):.2f}%"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    project = Path(__file__).resolve().parents[1]
    root.relative_to(project)
    ext = root / "analysis/policy-study"
    assert json.loads((ext / "validation.json").read_text())["ok"]
    assert json.loads((root / "validation-report.json").read_text())["ok"]
    out = root / "analysis/exploration"
    out.mkdir(exist_ok=False)
    dictionaries = []
    db = sqlite3.connect(out / "study.sqlite")
    for path in sorted(ext.glob("*.csv")):
        name = path.stem.replace("-", "_")
        rows = read(path)
        fields = list(rows[0])
        types = {}
        for field in fields:
            values = [r[field] for r in rows if r[field] != ""]
            try:
                for value in values:
                    float(value)
                types[field] = "REAL" if values else "TEXT"
            except ValueError:
                types[field] = "TEXT"
        db.execute(f'CREATE TABLE "{name}" (' + ",".join(f'"{field}" {types[field]}' for field in fields) + ")")
        db.executemany(f'INSERT INTO "{name}" VALUES (' + ",".join("?" for _ in fields) + ")",
                       ([None if r[f] == "" else float(r[f]) if types[f] == "REAL" else r[f] for f in fields] for r in rows))
        dictionaries.append({"table": name, "source": f"../policy-study/{path.name}", "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                             "rows": len(rows), "fields": [{"name": field, "sqliteType": types[field],
                             "unit": OUTCOMES.get(field, PARAMETERS.get(field, ("USD" if "usd" in field else "1" if any(x in field for x in ["probability", "fraction", "correctness"]) else "category-or-count", ""))[0])} for field in fields]})
    db.executescript("""
    CREATE UNIQUE INDEX policy_key ON policies(policy_id);
    CREATE UNIQUE INDEX grid_key ON policy_grid(policy_id, workload, world);
    CREATE UNIQUE INDEX core_key ON core_results(model, profile, workload, world);
    CREATE UNIQUE INDEX month_key ON synthetic_months(model, profile, tasks_per_month, month_id);
    CREATE VIEW selected_policy_details AS
    SELECT s.*, p.schema_tokens, p.result_retention, p.batch_size, p.context_cap_tokens,
           p.retry_policy, p.output_multiplier, p.tool_delta, p.cache_mode
    FROM selected_policies s LEFT JOIN policies p USING(policy_id);
    """)
    queries = [
        "SELECT workload, world, model, policy_id, token_usd, correct_completion, context_cap_tokens, retry_policy FROM selected_policy_details WHERE objective = 'minimum-spend-per-correct-with-quality-floor' ORDER BY workload, world;",
        "SELECT profile, workload, delta_usd_per_1000_tasks, delta_usd_per_million_tasks, delta_correct_completion FROM one_factor_effects WHERE model='luna' AND world='smooth' ORDER BY workload, delta_usd_per_1000_tasks;",
        "SELECT model, profile, value AS summary_fidelity, token_usd, correct_completion, spend_per_correct_usd FROM sensitivity WHERE parameter='summary_fidelity' AND world='critical-cliff' AND model='sol' ORDER BY profile, value;",
        "SELECT model, profile, tasks_per_month, mc_mean_token_usd, predictive_p05_usd, predictive_p95_usd, probability_over_budget FROM monthly_risk ORDER BY model, profile, tasks_per_month;",
    ]
    query_results = []
    for index, query in enumerate(queries, 1):
        result = db.execute(query).fetchall()
        query_results.append({"query": index, "rows": len(result), "ok": bool(result)})
        assert result
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    db.commit()
    db.close()
    (out / "queries.sql").write_text("-- SQLite queries; open study.sqlite. All outcomes are simulated.\n\n" + "\n\n".join(queries) + "\n", encoding="utf-8")
    dictionary = {"currency": "USD", "tableGrains": {
        "policy_grid": "One policy/workload/epistemic-world exact expectation.",
        "core_results": "One core model/profile/workload/world exact expectation.",
        "request_ledger": "One planned request within an attempt, before reach-probability weighting.",
        "one_factor_effects": "Comparison minus same-model baseline at one workload/world.",
        "sensitivity": "One supplemental changed parameter level at one core profile/world.",
        "synthetic_months": "One independent synthetic month with shared within-month difficulty shock.",
        "monthly_risk": "One policy/volume aggregate over 20000 synthetic months.",
        "selected_policies": "One finite-grid objective/workload/world selection, including infeasibility.",
        "robust_regret": "One minimax absolute expected-loss regret selection per workload.",
        "policies": "One assumed parameter configuration, not observed production behavior."},
        "importantDefinitions": {"spend_per_correct_usd": "Ratio E[spend]/P(accepted correct), not E[spend/correct].", "risk_adjusted_usd": "Expected spend + undetected-error loss + exhausted-task recovery loss; all loss prices assumed.",
                                 "request_clock_seconds": "Synthetic attempt-relative clock, not wall-clock measurements.", "monthly_quantiles": "Predictive variability under the invented process, not confidence in empirical validity.",
                                 "blank_numeric_cells": "Not applicable or infeasible, never numeric zero.", "seed_storage": "Exact seeds remain in canonical CSV/manifest; SQLite REAL conversion is not an authoritative RNG seed representation."},
        "tables": dictionaries}
    (out / "data-dictionary.json").write_text(json.dumps(dictionary, indent=2) + "\n", encoding="utf-8")
    core = read(ext / "core-results.csv")
    selected = read(ext / "selected-policies.csv")
    policies = {r["policy_id"]: r for r in read(ext / "policies.csv")}
    effects = read(ext / "one-factor-effects.csv")
    prefix = read(ext / "system-prefix-monthly.csv")
    monthly = read(ext / "monthly-risk.csv")
    text = ["# Code-assist cost simulation: results", "", "All amounts are USD. This is an exploratory mathematical model, not a Pi/Copilot benchmark. Prices are dated September 6, 2026; task quality, context rot, summary fidelity, validator performance and disturbances are explicitly assumed.", "",
            "## Scope and audit", "", "612 validated core cells, 5760 policy configurations per workload/world (51840 grid cells), 320000 synthetic months, 49 parameter-activation witnesses and 62 reviewed candidate variables. Nine test methods cover arithmetic and boundaries, including 128 two-attempt/single-attempt probability settings. No target system was executed. The separate core and extension audits pass; the model-variable review remains limitations-required.", "",
            "## 1000 extra system tokens, ten requests per task", "", "One initial write and nine reads within a larger eligible prefix, holding tiers, output, quality, tool count and compaction fixed. These figures are variable token-usage costs, not necessarily marginal invoices inside an included allowance.", "",
            table(["Model", "Cache case", "Extra / 1000 tasks", "Extra / 1M tasks"], [[r["model"], r["cache_case"], cash(r["delta_usd_per_1000_tasks"], 2), cash(r["delta_usd_per_million_tasks"], 2)] for r in prefix]), "",
            "## One-factor comparisons for Luna", "", "Negative cost differences mean savings. Hypothetical smooth-quality world, one attempt; a task is not the same as a model request.", "",
            table(["Task", "Change", "Delta / 1000 tasks", "Delta / 1M tasks", "Correct-completion delta (pp)"], [[r["workload"], r["profile"], cash(r["delta_usd_per_1000_tasks"], 2), cash(r["delta_usd_per_million_tasks"], 2), f"{100*float(r['delta_correct_completion']):+.2f}"] for r in effects if r["world"] == "smooth" and r["model"] == "luna" and r["profile"] in ["slim", "one-less-tool", "batch-two", "half-tool-output", "prefix-churn"]]), "",
            "## Long context and compaction", "", "The baseline long task has 38 sequential tool operations and 39 main requests; context starts at 49k and reaches 809k. Compaction calls, summary output, context rebuild and lost cache are charged. The reuse profile instead assumes compactor reads and static-prefix cache survive.", "",
            table(["Model", "Policy", "Token spend / task", "Compactions", "Calls in long-price tier", "Assumed correct completion"], [[r["model"], r["profile"], cash(r["token_usd"], 5), r["first_compactions"], r["first_long_tier_calls"], pct(r["correct_completion"])] for r in core if r["world"] == "smooth" and r["workload"] == "long" and r["profile"] in ["baseline", "cap-100k", "cap-180k", "cap-200k", "cap-272k", "cap-200k-reuse"]]), "",
            "## Conditional selections", "", "Minimize spend per correct completion subject to at least 95% correct completion and at most 1% undetected errors. These illustrative constraints and model correctness probabilities are assumptions, not empirical rankings. No candidate passes the long-task critical-cliff world.", "",
            table(["Task", "World", "Selection", "Spend / 1000 tasks", "Assumed correct completion", "Policy"], [[r["workload"], r["world"], r["model"] or "infeasible", cash(float(r["token_usd"])*1000, 2) if r["token_usd"] else "—", pct(r["correct_completion"]) if r["correct_completion"] else "—", r["policy_id"] or "—"] for r in selected if r["objective"] == "minimum-spend-per-correct-with-quality-floor"]), ""]
    for pid in sorted({r["policy_id"] for r in selected if r["policy_id"] and r["objective"] == "minimum-spend-per-correct-with-quality-floor"}):
        p = policies[pid]
        text.append(f"- `{pid}`: {p['model']}; schema {p['schema_tokens']} tokens; tool-result retention {p['result_retention']}; batch {p['batch_size']} subject to dependencies; cap {p['context_cap_tokens']}; {p['retry_policy']}; output multiplier {p['output_multiplier']}; tool delta {p['tool_delta']}; {p['cache_mode']}.")
    text += ["", "The mathematically cheapest feasible short-task policy drops a tool under the assumed smooth penalty. It is not the robust loss-minimizing policy: the robust short-task choice keeps required tools and full outputs. Review both objectives before implementing an apparent saving.", "",
             "## Synthetic monthly variability", "", "Mixture: 60% short, 30% feature, 10% long. Shared hypothetical difficulty shocks are included. The budget is 105% of normal-month expected token usage. Quantiles describe invented process variability, not real-world confidence. A million tasks is algebraic scaling, not demonstrated account capacity.", "",
             table(["Model/policy", "Tasks", "Exact mean usage", "Predictive p05–p95", "Over budget", "Mean MCSE"], [[f"{r['model']}/{r['profile']}", r["tasks_per_month"], cash(r["exact_mean_token_usd"], 2), f"{cash(r['predictive_p05_usd'],2)}–{cash(r['predictive_p95_usd'],2)}", pct(r["probability_over_budget"]), cash(r["mean_mcse_usd"], 2)] for r in monthly]), "",
             "Zero observed exceedances in 20000 synthetic months does not imply zero true risk. Pointwise 95% Hoeffding uncertainty on risk is ±0.96 percentage points, clipped to [0,1], conditional on the declared monthly generator. It does not cover structural uncertainty.", "",
             "## Billing and affordability", "", "At the current flex allowances, the least-cost individual monthly plan among Pro/Pro+/Max switches around $44 and $131 of token usage, respectively. At high usage Max reduces the invoice by $100 relative to raw token usage, but does not make million-task usage inexpensive. Availability, quotas, taxes and future allowances are unresolved. Fixed routing receives no assumed Auto discount. The monthly table distinguishes expected invoices from invoices at mean usage.", "",
             "## Limits and next useful evidence", "", "The most decision-sensitive unresolved inputs are task-specific correctness, summary fidelity, retry dependence, validator quality, route-specific cache behavior and real business loss. Neither a single 200k rule nor a universal context-rot onset is defensible. Use existing evidence or additional mathematical scenarios to narrow them; do not launch a live evaluation under this simulation-only workflow.", "",
             "Explore `analysis/exploration/study.sqlite` with `queries.sql`, or open the canonical `analysis/policy-study/*.csv`. Core `analysis/explore.sql` is a separate DuckDB starter for the skill's normalized run tables. The preflight inventory and post-run review expose included, fixed and unresolved variables; unrecognized factors may remain.", ""]
    (root / "analysis/results.md").write_text("\n".join(text), encoding="utf-8")
    inventory = {"ok": True, "sqliteIntegrityCheck": "ok", "queries": query_results,
                 "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()},
                 "reportSha256": hashlib.sha256((root / "analysis/results.md").read_bytes()).hexdigest()}
    (out / "manifest.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "tables": len(dictionaries), "queries": query_results, "report": str(root / "analysis/results.md")}))


if __name__ == "__main__":
    main()
