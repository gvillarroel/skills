#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Offline request accounting and exact two-attempt decision mathematics.

No target execution, networking, live calibration, or inference client exists
in this model. Monetary rates are supplied by the frozen experiment, while
quality, workload, cache realization, and validation behavior are assumptions.
"""

from __future__ import annotations

import itertools
import math
import platform


MODEL_METADATA = {
    "modelId": "code-assist-cost-quality-expectation",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "none-exact-expectations",
    "rngVersion": platform.python_version(),
    "reproducibility": "exact-within-locked-environment",
}


def logistic(value):
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    z = math.exp(value)
    return z / (1 + z)


def bill(row, card):
    """Partitioned input buckets are mutually exclusive, not additive surcharges."""
    assert row["uncached"] >= 0 and row["read"] >= 0 and row["write"] >= 0
    assert row["input"] == row["uncached"] + row["read"] + row["write"]
    long = row["input"] > card["threshold_tokens"]
    input_factor = card["long_input_factor"] if long else 1
    output_factor = card["long_output_factor"] if long else 1
    return (
        (row["uncached"] * card["input_usd_mtok"]
         + row["read"] * card["read_usd_mtok"]
         + row["write"] * card["write_usd_mtok"]) * input_factor
        + row["output"] * card["output_usd_mtok"] * output_factor
    ) / 1_000_000


def attempt(p, card):
    """Return a deterministic token ledger and a hypothetical correctness rate."""
    stable = int(p["system_tokens"] + p["schema_tokens"])
    current = int(stable + p["background_tokens"])
    tools = max(0, int(p["required_tools"] + p["tool_delta"]))
    batch = max(1, min(int(p["batch_size"]), int(p["max_independent_batch"])))
    groups = [min(batch, tools - i) for i in range(0, tools, batch)] + [0]
    cached = 0
    last_access = -math.inf
    now = 0.0
    compact_count = 0
    main_contexts, fidelities, rows = [], [], []
    ttl = p["cache_ttl_seconds"][card["model_id"]]

    def record(kind, total, read, write, output, tool_count=0):
        nonlocal now
        row = {
            "request_index": len(rows) + 1, "kind": kind, "input": total,
            "uncached": total - read - write, "read": read, "write": write,
            "output": output, "tools": tool_count, "clock_seconds": now,
            "model_id": card["model_id"],
        }
        row["usd"] = bill(row, card)
        row["long_tier"] = total > card["threshold_tokens"]
        latency = p["roundtrip_seconds"] + total * p["prefill_seconds_per_token"]
        latency += output / p["output_tokens_per_second"]
        if tool_count:
            latency += p["tool_seconds"]  # Independent tools in one wave overlap.
        row["service_seconds"] = latency
        now += latency
        rows.append(row)

    for step, group in enumerate(groups):
        if step:
            now += p["think_gap_seconds"]
            if p["idle_every"] and step % int(p["idle_every"]) == 0:
                now += p["idle_gap_seconds"]
        if now - last_access > ttl:
            cached = 0
        if p["churn_every"] and step and step % int(p["churn_every"]) == 0:
            cached = 0  # A changed early prefix invalidates all modeled descendants.
        if current > p["context_cap_tokens"]:
            read = min(cached, current) if p["compaction_input_mode"] == "read" else 0
            record("compaction", current, read, 0, int(p["summary_tokens"]))
            compact_count += 1
            cached = min(cached, stable) if p["preserve_static_prefix"] else 0
            current = stable + int(p["summary_tokens"] + p["recent_tokens"])
            assert current <= p["context_cap_tokens"], "Rebuilt context exceeds its cap"
            if read:
                last_access = now
        read = min(cached, current) if p["cache_mode"] != "off" else 0
        if p["cache_mode"] == "off":
            write = 0
        elif group == 0 and p["cache_mode"] == "terminal-uncached":
            write = 0  # This newly added suffix has no later use in this attempt.
        else:
            write = current - read
        output = int(round(p["output_multiplier"] * (
            p["argument_tokens"] * group if group else p["final_output_tokens"]
        )))
        record("main", current, read, write, output, group)
        main_contexts.append(current)
        fidelities.append(p["summary_fidelity"] ** compact_count)
        if p["cache_mode"] != "off":
            cached = max(read + write, cached)
            last_access = now
        current += output + int(round(group * p["tool_result_tokens"] * p["result_retention"]))

    weights = [i + 1 if p["evidence_position"] == "late" else 1 for i in range(len(groups))]
    exposure = sum(w * max(0, length - p["rot_onset_tokens"]) / 100000
                   for w, length in zip(weights, main_contexts)) / sum(weights)
    fidelity = sum(w * f for w, f in zip(weights, fidelities)) / sum(weights)
    if p["quality_mechanism"] == "critical-cliff":
        exposure = max(0, max(main_contexts) - p["rot_onset_tokens"]) / 100000
        fidelity = p["summary_fidelity"] ** (compact_count * p["critical_facts"])
    baseline = p["quality_probabilities"][card["model_id"]]
    penalty = p["rot_beta"] * exposure
    penalty += p["trim_penalty"] * (1 - p["result_retention"])
    penalty += p["omission_penalty"] * max(0, -p["tool_delta"])
    penalty += p["output_penalty"] * (1 - p["output_multiplier"])
    if p["quality_mechanism"] == "critical-cliff" and max(main_contexts) > 2 * p["rot_onset_tokens"]:
        penalty += p["cliff_logodds_loss"]
    probability = 0.0 if fidelity == 0 else logistic(
        math.log(baseline / (1 - baseline)) + math.log(fidelity) - penalty + p["quality_shift"]
    )
    token_cost = math.fsum(row["usd"] for row in rows)
    fee = tools * p["tool_fee_usd"] + p["validation_fee_usd"]
    return {
        "rows": rows, "p": probability, "token_cost": token_cost, "fee": fee,
        "cost": token_cost + fee, "input": sum(row["input"] for row in rows),
        "output": sum(row["output"] for row in rows), "read": sum(row["read"] for row in rows),
        "compactions": compact_count, "max_context": max(row["input"] for row in rows),
        "latency": sum(row["service_seconds"] for row in rows), "tools": tools,
        "exposure": exposure, "fidelity": fidelity,
    }


def terminal_distribution(first, second, p):
    """Enumerate correctness vectors and acceptance gates for <=2 attempts.

The dependence parameter mixes independent planned outcomes with a shared
uniform difficulty variable. For unequal model probabilities it is a mixture
weight, not the Pearson correlation. Validators have conditional sensitivity
and specificity, independent across attempts given correctness.
"""
    attempts = [first] if p["attempt_cap"] == 1 else [first, second]
    rates = [a["p"] for a in attempts]
    cuts = sorted(set([0.0, 1.0, *rates]))
    shared = {}
    for low, high in zip(cuts, cuts[1:]):
        key = tuple((low + high) / 2 < probability for probability in rates)
        shared[key] = shared.get(key, 0.0) + high - low
    terminal = {}
    for vector in itertools.product((False, True), repeat=len(attempts)):
        independent = math.prod(q if good else 1 - q for good, q in zip(vector, rates))
        mass = (1 - p["retry_dependence"]) * independent + p["retry_dependence"] * shared.get(vector, 0)
        reach = mass
        for i, good in enumerate(vector):
            accept = p["validator_specificity"] if good else 1 - p["validator_sensitivity"]
            key = (i + 1, "correct" if good else "undetected")
            terminal[key] = terminal.get(key, 0.0) + reach * accept
            reach *= 1 - accept
        key = (len(attempts), "exhausted")
        terminal[key] = terminal.get(key, 0.0) + reach
    assert abs(math.fsum(terminal.values()) - 1) < 1e-12
    return [{"attempts": n, "status": status, "probability": prob,
             "token_usd": first["token_cost"] + (second["token_cost"] if n == 2 else 0),
             "fee_usd": first["fee"] + (second["fee"] if n == 2 else 0)}
            for (n, status), prob in sorted(terminal.items())]


def evaluate(p):
    first = attempt(p, p["first_model"])
    second = attempt(p, p["retry_model"]) if p["attempt_cap"] == 2 else first
    terminal = terminal_distribution(first, second, p)
    reach2 = sum(item["probability"] for item in terminal if item["attempts"] == 2)
    correct = sum(item["probability"] for item in terminal if item["status"] == "correct")
    undetected = sum(item["probability"] for item in terminal if item["status"] == "undetected")
    exhausted = sum(item["probability"] for item in terminal if item["status"] == "exhausted")
    token_cost = first["token_cost"] + reach2 * second["token_cost"]
    fees = first["fee"] + reach2 * second["fee"]
    total_input = first["input"] + reach2 * second["input"]
    result = {
        "token_usd": token_cost, "fees_usd": fees, "spend_usd": token_cost + fees,
        "correct_completion": correct, "undetected_error": undetected, "exhausted": exhausted,
        "attempts": 1 + reach2, "input_tokens": total_input,
        "output_tokens": first["output"] + reach2 * second["output"],
        "cache_read_share": (first["read"] + reach2 * second["read"]) / total_input,
        "compactions": first["compactions"] + reach2 * second["compactions"],
        "max_context_tokens": max(first["max_context"], second["max_context"]),
        "service_seconds": first["latency"] + reach2 * second["latency"],
        "risk_adjusted_usd": token_cost + fees + undetected * p["undetected_loss_usd"] + exhausted * p["rework_loss_usd"],
    }
    return result, first, second, terminal


def simulate(run):
    p = run["parameters"]
    result, first, second, terminal = evaluate(p)
    probability_ok = abs(result["correct_completion"] + result["undetected_error"] + result["exhausted"] - 1) < 1e-12
    ledger_cost = math.fsum(item["probability"] * (item["token_usd"] + item["fee_usd"]) for item in terminal)
    accounting_ok = math.isclose(ledger_cost, result["spend_usd"], rel_tol=1e-12, abs_tol=1e-12)
    valid = probability_ok and accounting_ok and all(math.isfinite(x) and x >= 0 for x in result.values())
    return {"outcomes": result, "diagnostics": [{
        "check_id": "probability-and-spend-accounting", "status": "pass" if valid else "fail",
        "invalidates_hypotheses": not valid,
        "message": "Disjoint terminal-state mass, expected ledger spend, and finite nonnegative outcomes checked.",
    }]}
