#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a frozen, simulation-only core bundle; never invoke a target harness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

PROJECT = Path(__file__).resolve().parents[1]

# Parameter units and mechanisms are part of the human-readable preflight.
PARAMETERS = {
    "first_model": ("model-rate-card", "Select the first model and its route-specific input/read/write/output rates and tier rule."),
    "retry_model": ("model-rate-card", "Select the second model only when validation rejects the first attempt."),
    "system_tokens": ("token", "A stable system prefix is paid on every request through its current cache bucket and can cross a full-request price tier."),
    "schema_tokens": ("token", "Tool definitions and harness instructions enlarge the stable prefix; loading fewer definitions is assumed not to remove needed tools."),
    "tool_delta": ("tool-call", "Remove a tool call and its model round trip, argument output, and retained result; an explicit quality penalty can offset the saving."),
    "batch_size": ("tool-call", "Group independent tool calls into one model wave; do not reduce the number of actual modeled tool operations."),
    "result_retention": ("1", "Keep a fraction of each tool result, reducing subsequent inputs but possibly discarding evidence."),
    "output_multiplier": ("1", "Scale model argument and final-answer tokens, affecting output billing, future input and hypothetical quality."),
    "context_cap_tokens": ("token", "Compact before a main call whose accumulated input exceeds the cap; the summary request still reads the overshoot."),
    "compaction_input_mode": ("category", "Bill compactor input as uncached or reuse eligible existing cache; do not silently assume either route."),
    "summary_tokens": ("token", "Pay for summary output and retain it in rebuilt context."),
    "recent_tokens": ("token", "Retain recent context alongside the summary and static prefix."),
    "preserve_static_prefix": ("boolean", "Keep eligible static-prefix cache after compaction, or invalidate the entire cache."),
    "cache_mode": ("category", "Partition input into ordinary input, cache reads and cache writes; terminal-uncached avoids writing the final never-reused suffix."),
    "churn_every": ("request", "Changing the early prefix invalidates descendants every selected number of main requests."),
    "attempt_cap": ("attempt", "Stop after one attempt or allow one validation-triggered retry; no unlimited geometric retry assumption."),
    "background_tokens": ("token", "Initial task and repository material adds to the starting context."),
    "required_tools": ("tool-call", "Required tool operations determine wave count and context growth."),
    "max_independent_batch": ("tool-call", "Dependency constraints cap batching; sequential long tasks cannot obtain artificial parallel savings."),
    "tool_result_tokens": ("token/tool-call", "Each retained result is injected into context and can be billed repeatedly downstream."),
    "argument_tokens": ("token/tool-call", "Model-generated arguments cost output tokens and become later input."),
    "final_output_tokens": ("token", "Final output is billed once and not sent to a later model request in this attempt."),
    "cache_ttl_seconds": ("model-ttl-map", "Assumed realized TTL by model; elapsed service, think time and idle gaps can invalidate the prefix."),
    "think_gap_seconds": ("second", "Time between waves consumes cache lifetime."),
    "idle_every": ("request", "A scheduled pause occurs at this main-request cadence."),
    "idle_gap_seconds": ("second", "Scheduled pauses can exceed cache retention and trigger expensive rebuilds."),
    "roundtrip_seconds": ("second/request", "Assumed request overhead affects service time and cache-age state, not measured model speed."),
    "prefill_seconds_per_token": ("second/token", "Assumed prefill service scales with all input tokens; no measured cache-latency benefit is claimed."),
    "output_tokens_per_second": ("token/second", "Assumed output generation speed affects elapsed time and modeled cache lifetime."),
    "tool_seconds": ("second/wave", "Assumed independent tool operations overlap within a wave."),
    "evidence_position": ("category", "Uniform or late weights determine which context lengths and accumulated summary losses matter to the quality surrogate."),
    "summary_fidelity": ("1", "Compactions multiply retained evidence; the rival mechanism requires multiple critical facts to survive every summary."),
    "rot_onset_tokens": ("token", "Assumed, not empirically estimated, onset for the context-exposure penalty."),
    "rot_beta": ("log-odds/100k-token", "Reduce correctness log odds per 100000 excess context tokens."),
    "quality_mechanism": ("category", "Contrast a weighted smooth exposure mechanism with a peak-context critical-fact cliff."),
    "critical_facts": ("fact", "In the rival model all critical facts must survive all compactions."),
    "quality_probabilities": ("model-probability-map", "Invented baseline correctness probabilities by model and workload, not benchmark measurements."),
    "trim_penalty": ("log-odds", "Potential correctness loss when shortening tool results."),
    "omission_penalty": ("log-odds/tool-call", "Potential correctness loss per removed required tool operation."),
    "output_penalty": ("log-odds", "Potential correctness loss when reducing model output."),
    "cliff_logodds_loss": ("log-odds", "Additional rival penalty beyond twice the assumed rot onset."),
    "quality_shift": ("log-odds", "Shared monthly difficulty shifts correctness in the supplemental shock process."),
    "tool_fee_usd": ("USD/tool-call", "Non-token external tool cost, held at zero in primary scenarios and independently activation-tested."),
    "validation_fee_usd": ("USD/attempt", "Validation compute cost, held at zero in primary scenarios; human review is not silently included."),
    "validator_sensitivity": ("1", "Probability of rejecting an incorrect attempt, affecting retries and undetected errors."),
    "validator_specificity": ("1", "Probability of accepting a correct attempt, affecting false rejection and exhausted tasks."),
    "retry_dependence": ("1", "Mixture weight on shared task difficulty versus independent attempt correctness, not generally a Pearson correlation."),
    "undetected_loss_usd": ("USD/error", "Assumed downstream loss per accepted incorrect task."),
    "rework_loss_usd": ("USD/exhausted-task", "Assumed recovery cost after the attempt budget is exhausted."),
}

OUTCOMES = {
    "token_usd": "USD/task", "fees_usd": "USD/task", "spend_usd": "USD/task",
    "correct_completion": "1", "undetected_error": "1", "exhausted": "1", "attempts": "attempt/task",
    "input_tokens": "token/task", "output_tokens": "token/task", "cache_read_share": "1",
    "compactions": "compaction/task", "max_context_tokens": "token", "service_seconds": "second/task",
    "risk_adjusted_usd": "USD/task",
}


def load_study():
    return json.loads((PROJECT / "source/study-20260906.json").read_text(encoding="utf-8"))


def parameters(study, model, profile, workload, world):
    p = dict(study["policyDefaults"])
    p.update(study["coreProfiles"][profile])
    p["first_model"] = study["rateCards"][model]
    retry = study["escalation"][model] if profile == "escalate-two" else model
    p["retry_model"] = study["rateCards"][retry]
    p.update(study["environmentDefaults"])
    p.update(study["workloads"][workload])
    p.update(study["qualityWorlds"][world])
    return p


def declarations(values):
    return [{"name": name, "value": value, "unit": PARAMETERS[name][0],
             "sourceType": "literature" if name in ("first_model", "retry_model") else "assumed",
             "description": PARAMETERS[name][1]}
            for name, value in values.items()]


def variable_review():
    controls = set(load_study()["policyDefaults"]) | {"first_model", "retry_model"}
    variables = []
    for name, (unit, mechanism) in PARAMETERS.items():
        variables.append({
            "variableId": name.replace("_", "-"), "label": name.replace("_", " ").capitalize(),
            "role": "control" if name in controls else "exogenous", "unit": unit,
            "treatment": "fixed" if name in {"tool_fee_usd", "validation_fee_usd", "quality_shift", "roundtrip_seconds", "prefill_seconds_per_token", "output_tokens_per_second", "tool_seconds", "think_gap_seconds"} else "modeled",
            "parameterNames": [name], "affectsOutcomes": list(OUTCOMES),
            "mechanism": mechanism,
            "evidence": "Published route price card, frozen on 2026-09-06." if name in ("first_model", "retry_model") else "Explicit synthetic assumption, not calibrated to the user or a production harness.",
            "decisionImpact": "medium" if "seconds" in name else "high",
            "reason": "Expose this input for one-factor and interaction comparisons. Outcome links are a broad decision-relevance declaration, not proof of every direct code dependency.",
            "nextCheck": "See parameter-activation.csv for a changed-input witness; inspect ledger or quality intermediates when a parameter is inactive outside its triggering region.",
        })
    omissions = [
        ("empirical-quality", "Actual model correctness and validator calibration", "unresolved", "high", "Real ranking could reverse; selected quality probabilities are invented. Existing task-specific evidence would reduce this gap."),
        ("harness-implementation", "Harness-specific hidden prompts and feature support", "unresolved", "high", "Tool loading, partial-prefix retention, compactor cache access and explicit cache writes may not be exposed by every harness."),
        ("tokenization", "Equal source text across tokenizers", "unresolved", "high", "Equal token counts do not establish equal information; measured existing token ledgers would be needed for a brand comparison."),
        ("quotas-capacity", "Rate limits, concurrency and account eligibility", "unresolved", "high", "Million-task volume may require a fleet or contract; a cheap mathematical route may be unavailable."),
        ("monthly-billing", "Seat fees, included credits and nonlinearity", "modeled", "high", "Handled in the declared analysis extension; expected invoice requires integrating over usage, not invoicing its mean."),
        ("task-mix-shocks", "Task heterogeneity and correlated month-level difficulty", "modeled", "high", "Declared synthetic mixture and shared quality shifts drive monthly predictive risk in the extension."),
        ("cross-session-cache", "Cache sharing, routing, eviction and early cancellations", "excluded", "high", "Attempts begin cold; real cross-session reuse could reduce spend while eviction and abandonment could increase it."),
        ("reasoning-budget", "Reasoning effort and hidden billed output", "unresolved", "high", "Represented only through aggregate output and quality knobs; no measured effort-to-quality response is known."),
        ("human-rework", "Human time, CI, Actions, review and downstream incidents", "unresolved", "high", "Loss prices are user-replaceable assumptions; validation fees default to zero; Code Review Actions minutes are outside token billing."),
        ("pricing-contract", "Taxes, currency, discounts and changing flex allowances", "excluded", "high", "Prices are a dated USD snapshot. No Auto discount on fixed routing, batch discount, annual legacy regime or tax is applied."),
        ("task-validity", "Task correctness is richer than a binary event", "unresolved", "high", "Partial utility, security, compliance, deadline losses and mandatory checks can invalidate a nominal saving."),
        ("queueing-feedback", "Congestion, cancellations and provider outages", "excluded", "high", "No queue-capacity claim; synthetic quality shocks do not model unavailable service or timeout billing."),
        ("storage-embeddings", "Retrieval index, embeddings and state storage", "excluded", "medium", "The assumed background retrieval is not priced as a new indexing service; include it before comparing a new RAG architecture."),
    ]
    for vid, label, treatment, impact, mechanism in omissions:
        variables.append({"variableId": vid, "label": label, "role": "structural", "unit": "1", "treatment": treatment,
                          "parameterNames": [], "affectsOutcomes": [], "mechanism": mechanism,
                          "evidence": "Declared extension or unresolved real-world evidence gap.", "decisionImpact": impact,
                          "reason": "Do not infer completeness or real-world optimality from a numerical pass.",
                          "nextCheck": "Read model-review-followup.md and the declared extension; use existing evidence or a new mathematical sensitivity design, never a live pilot."})
    interactions = []
    for iid, ids, mechanism in [
        ("prefix-cache-tier", ["system-tokens", "schema-tokens", "cache-mode", "first-model"], "Stable prefix additions can be cheap cache reads or can push the whole request across a pricing discontinuity."),
        ("tools-waves-growth", ["required-tools", "batch-size", "max-independent-batch", "tool-result-tokens"], "Tools create both output and repeated input; dependency-constrained batching changes wave count."),
        ("compaction-quality-cache", ["context-cap-tokens", "summary-fidelity", "quality-mechanism", "preserve-static-prefix", "compaction-input-mode"], "Compaction trades expensive summaries and cold rebuilds against shorter context and possible information loss."),
        ("retry-validator-difficulty", ["first-model", "retry-model", "validator-sensitivity", "validator-specificity", "retry-dependence"], "Retry outcomes share task difficulty, and imperfect validation can stop early on an incorrect answer."),
        ("cache-time", ["cache-ttl-seconds", "idle-gap-seconds", "output-tokens-per-second", "churn-every"], "A prefix hit depends on identity and elapsed retention, not a context-independent hit probability."),
        ("quality-risk-spend", ["quality-probabilities", "undetected-loss-usd", "rework-loss-usd", "tool-delta"], "Token savings can be overwhelmed by additional failures or undetected errors."),
    ]:
        interactions.append({"interactionId": iid, "variableIds": ids, "treatment": "modeled", "decisionImpact": "high", "mechanism": mechanism,
                             "reason": "A one-factor derivative alone cannot represent this joint change.", "nextCheck": "Compare the factorial grid, core contrasts and boundary oracles; retain challenge-world reversals."})
    checks = {
        "outcome-backtrace": ["first-model", "quality-probabilities", "human-rework"],
        "lifecycle": ["background-tokens", "required-tools", "attempt-cap", "human-rework"],
        "dependencies-and-feedback": ["max-independent-batch", "retry-dependence", "compaction-input-mode"],
        "heterogeneity-and-selection": ["task-mix-shocks", "empirical-quality", "validator-sensitivity"],
        "time-and-scale": ["cache-ttl-seconds", "monthly-billing", "quotas-capacity", "queueing-feedback"],
        "constraints-and-accounting": ["first-model", "context-cap-tokens", "pricing-contract", "task-validity"],
        "rival-mechanisms": ["quality-mechanism", "summary-fidelity", "cross-session-cache"],
        "evidence-gaps": ["empirical-quality", "tokenization", "harness-implementation"],
    }
    return {"schemaVersion": 1, "scope": "Finite exploratory code-assist policy set with mathematical token ledgers and assumed quality; no empirical harness winner or guarantee that every relevant variable was discovered.",
            "variables": variables, "interactions": interactions,
            "coverageChecks": [{"dimension": dimension, "status": "reviewed", "variableIds": ids,
                                "note": "Included mechanisms and material gaps are explicitly listed; review status is not a completeness certificate."} for dimension, ids in checks.items()],
            "openQuestions": ["What existing task-specific quality and tokenization evidence is available?", "What quality floor, budget, rework loss and compliance checks does the user require?", "Which billing route, account limits and cache controls are actually available?"]}


def build_spec(study):
    scenarios = []
    for model in study["rateCards"]:
        for profile in study["coreProfiles"]:
            p = parameters(study, model, profile, "short", "no-rot")
            keys = set(study["policyDefaults"]) | {"first_model", "retry_model"}
            scenarios.append({"scenarioId": f"{model}-{profile}", "label": f"{model} / {profile}",
                              "description": "Hypothetical harness configuration, not a measured product behavior.",
                              "tags": [model, profile], "parameters": declarations({k: p[k] for k in sorted(keys)})})
    points = []
    for workload in study["workloads"]:
        for world in study["qualityWorlds"]:
            p = dict(study["environmentDefaults"]) | study["workloads"][workload] | study["qualityWorlds"][world]
            points.append({"designPointId": f"{workload}-{world}", "description": "Synthetic workload and uncalibrated rival quality world; no world probability assigned.", "parameters": declarations(p)})
    hypotheses = []
    contrasts = [("slim", "token_usd", 0), ("one-less-tool", "token_usd", 0), ("batch-two", "token_usd", 0),
                 ("cap-200k", "token_usd", 0), ("cap-200k", "correct_completion", 0), ("escalate-two", "risk_adjusted_usd", 0)]
    for model in study["rateCards"]:
        for profile, outcome, threshold in contrasts:
            op = "ge" if outcome == "correct_completion" else "le"
            hypotheses.append({"hypothesisId": f"{model}-{profile}-{outcome.replace('_', '-')}",
                               "claim": f"{profile} changes {outcome} in the prespecified beneficial direction relative to baseline at all declared points.",
                               "claimScope": "conditional-real-world", "assumptionIds": ["a-prices", "a-workload", "a-quality", "a-retry"],
                               "externalValidationRequired": True, "outcome": outcome, "scenarioIds": [f"{model}-baseline", f"{model}-{profile}"],
                               "estimand": f"Exact expectation difference in {outcome}: comparison minus baseline; no Monte Carlo error.",
                               "analysis": {"kind": "scenario-contrast", "estimator": "mean-difference", "baselineScenarioId": f"{model}-baseline", "comparisonScenarioId": f"{model}-{profile}",
                                            "primaryDesignPointIds": ["long-smooth"], "challengeDesignPointIds": [x["designPointId"] for x in points if x["designPointId"] != "long-smooth"],
                                            "pairing": "deterministic", "intervalMethod": "none", "intervalLevel": None, "aggregationRule": "all-design-points"},
                               "practicalThreshold": {"value": threshold, "unit": OUTCOMES[outcome], "operator": op},
                               "decisionRule": "Compare exact expectations with zero, including equality as non-worsening. Report magnitude separately; this screening threshold is not proof of a worthwhile saving.",
                               "falsificationRule": "Seek a sign reversal in the no-rot or critical-cliff worlds and in shorter tasks; one reversal challenges the universal claim."})
    return {"schemaVersion": 1, "experimentId": study["studyId"], "title": "Code-assist cost and quality policy simulation",
            "description": study["boundary"], "phase": "exploratory", "paradigm": "discrete-event", "timeUnit": "second",
            "engine": {"name": "python-standard-library", "versionConstraint": ">=3.11"}, "rootSeed": 20260906,
            "uncertaintyMode": "deterministic", "seedPolicy": "independent-by-run", "replications": 1,
            "scenarios": scenarios, "designPoints": points,
            "outcomes": [{"name": name, "unit": unit, "description": "Exact expectation under the declared request ledger and probability model; not an observed measurement."} for name, unit in OUTCOMES.items()],
            "hypotheses": hypotheses,
            "assumptions": [{"assumptionId": key, "statement": value, "sourceType": "literature" if key == "a-prices" else "assumed"} for key, value in {
                "a-prices": "Dated Copilot token-billing rate cards, not direct API or legacy request-based plans; original URLs are in study-20260906.json.",
                "a-workload": "Synthetic sequential append-only traces, cold attempt starts, specified cache realization and optional compaction. Hardware capacity and harness support are not established.",
                "a-quality": "All correctness levels, context-rot onsets, fidelity and loss functions are hypothetical. Rival worlds have no probability weights and do not calibrate present-day models.",
                "a-retry": "At most two fresh-context attempts, imperfect validation and explicit shared-difficulty mixture; no actual agent execution."}.items()],
            "extensions": {"simulation-data-lab": {"executionBoundary": {"mode": "mathematical-simulation-only", "targetExecution": "forbidden", "liveTargetCalls": "forbidden", "calibrationInputs": "existing-evidence-or-explicit-assumptions", "enforcementScope": "workflow-contract-not-a-security-sandbox"}, "variableReview": variable_review()},
                           "code-assist-study": {"controlFile": "study-20260906.json", "extensionManifest": "analysis/policy-study/manifest.json", "description": "Frozen factorial, monthly stochastic risk and supplemental sensitivity design; separately validated, not certified by the core CSV validator."}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.relative_to(PROJECT)
    root.mkdir(parents=True, exist_ok=False)
    study = load_study()
    spec = build_spec(study)
    (root / "experiment.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(PROJECT / "source/model.py", root / "model.py")
    shutil.copyfile(PROJECT / "source/study-20260906.json", root / "study-20260906.json")
    manifest = {"phase": "exploratory", "beforeResults": True, "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()},
                "coreRuns": len(spec["scenarios"]) * len(spec["designPoints"]), "executionBoundary": study["boundary"]}
    (root / "preflight-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"root": str(root), "coreRuns": manifest["coreRuns"], "candidateVariables": len(spec["extensions"]["simulation-data-lab"]["variableReview"]["variables"])}))


if __name__ == "__main__":
    main()
