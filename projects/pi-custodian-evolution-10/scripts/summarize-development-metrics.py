#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize completed development artifacts only; never opens reserved gate data."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
RESERVED = {"evaluator-private", "validation", "holdout"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    if RESERVED.intersection(path.parts):
        raise ValueError("Reserved gate artifacts must not enter development metrics.")
    before = path.read_bytes()
    value = json.loads(before.decode("utf-8-sig"))
    if path.read_bytes() != before:
        raise ValueError("An artifact changed during the metrics read.")
    return value, sha(before)


def finite(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def author_observations(path):
    models, efforts, calls, invalid = Counter(), Counter(), 0, 0
    usage = Counter()
    if not path.is_file():
        return {"observedAssistantCompletions": 0, "models": [], "effortFields": [],
                "usage": {}, "invalidJsonLines": 0, "traceAvailable": False}
    before = path.read_bytes()
    for line in before.decode("utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            invalid += 1
            continue
        if event.get("type") != "message_end" or not isinstance(event.get("message"), dict):
            continue
        message = event["message"]
        if message.get("role") != "assistant":
            continue
        calls += 1
        provider, model = message.get("provider"), message.get("model")
        if isinstance(provider, str) and isinstance(model, str):
            models[(provider, model)] += 1
        for field in ("thinkingLevel", "providerThinkingLevel"):
            if isinstance(message.get(field), str):
                efforts[(field, message[field])] += 1
        for key in ("input", "output", "cacheRead", "cacheWrite", "totalTokens"):
            value = message.get("usage", {}).get(key) if isinstance(message.get("usage"), dict) else None
            if finite(value) is not None:
                usage[key] += value
    if path.read_bytes() != before:
        raise ValueError("Author trace changed during the metrics read.")
    return {"observedAssistantCompletions": calls,
            "models": [{"provider": provider, "model": model, "completions": count}
                       for (provider, model), count in sorted(models.items())],
            "effortFields": [{"field": field, "value": value, "completions": count}
                             for (field, value), count in sorted(efforts.items())],
            "effortObservation": "exposed" if efforts else "not-exposed",
            "usage": dict(usage), "invalidJsonLines": invalid,
            "traceAvailable": True, "traceSha256": sha(before)}


def flag_counts(cases, predicate):
    selected = [case for case in cases if isinstance(case, dict) and predicate(str(case.get("id", "")))]
    return {"total": len(selected), "passed": sum(case.get("passed") is True for case in selected),
            "failed": sum(case.get("passed") is not True for case in selected)}


def paired_deltas(row):
    before, after = row["baseline"], row["candidate"]
    if not all(finite(arm.get(field)) is not None
               for arm in (before, after) for field in ("compositeScore", "decisionScore", "workerScore")):
        return None
    decision = after["decisionScore"] - before["decisionScore"]
    worker = after["workerScore"] - before["workerScore"]
    return {"compositeDelta": after["compositeScore"] - before["compositeScore"],
            "decisionDelta": decision, "workerDelta": worker,
            "weightedDecisionContribution": .5 * decision,
            "weightedWorkerContribution": .5 * worker,
            "decisionGainMeasuredInPair": decision > 0,
            "meaning": "Observed paired component differences; no operator causality or general accuracy claim."}


def evaluation_arm(arm):
    verifier = arm.get("verification")
    if not isinstance(verifier, dict):
        try:
            verifier = json.loads(arm.get("verifier", {}).get("stdout", ""))
        except (TypeError, ValueError):
            verifier = None
    if not isinstance(verifier, dict):
        return {"available": False, "observedEvaluatorCompletions": 0,
                "callObservation": "No model completion in the returned verifier object; partial invocations are unknown."}
    cases = verifier.get("cases") if isinstance(verifier.get("cases"), list) else []
    observed = verifier.get("observedModel") if isinstance(verifier.get("observedModel"), dict) else {}
    model = {field: observed[field] for field in ("provider", "model", "stopReason") if isinstance(observed.get(field), str)}
    effort = {field: observed[field] for field in ("thinkingLevel", "providerThinkingLevel") if isinstance(observed.get(field), str)}
    real_completion = (verifier.get("mode") == "real" and verifier.get("mechanicsOnly") is False
                       and isinstance(observed.get("provider"), str) and isinstance(observed.get("model"), str))
    composite, decision, worker = (finite(verifier.get(field)) for field in ("score", "decisionScore", "workerScore"))
    consistent = None if None in (composite, decision, worker) else abs(composite - .5 * decision - .5 * worker) < 1e-9
    return {"available": True, "compositeScore": composite, "decisionScore": decision, "workerScore": worker,
            "compositeMatchesFrozenWeights": consistent, "passedHardFlags": verifier.get("passed"),
            "caseFlags": flag_counts(cases, lambda identity: True),
            "decisionSafetySchemaFlags": flag_counts(cases, lambda identity: identity.startswith("decision:")),
            "workerHardCases": flag_counts(cases, lambda identity: identity.startswith("worker:worker-hard-")),
            "workerSoftInheritedFlags": flag_counts(cases, lambda identity: identity.startswith("worker:worker-soft-")),
            "workerSoftFlagMeaning": "These repeat global hard-gate status; they are not eight additional independent safety cases.",
            "observedModel": model, "observedEffortFields": effort,
            "effortObservation": "exposed" if effort else "not-exposed",
            "observedEvaluatorCompletions": 1 if real_completion else 0,
            "mode": verifier.get("mode"), "mechanicsOnly": verifier.get("mechanicsOnly"),
            "durationMs": finite(verifier.get("durationMs")),
            "callObservation": "One fresh batch SDK completion reported per real arm; provider-internal HTTP retries are not observable here."}


def summarize(iterations):
    root = iterations.resolve(strict=True)
    if RESERVED.intersection(root.parts) or root.name != "iterations":
        raise ValueError("Read only the development iterations directory.")
    rows, artifact_hashes = [], {}
    for folder in sorted(root.glob("i[0-9][0-9]")):
        result_path = folder / "iteration-result.json"
        if not result_path.is_file():
            continue
        result, result_hash = load(result_path)
        artifact_hashes[str(result_path)] = result_hash
        row = {"slot": result.get("slot"), "operator": result.get("operator"), "seed": result.get("seed"),
               "nativeQualified": result.get("qualified") is True, "outcome": result.get("outcome"),
               "patchDigest": result.get("patchDigest"), "proposalId": result.get("proposalId"),
               "author": author_observations(folder / "author-events.public.jsonl")}
        evaluation_path = folder / "evaluation.json"
        if evaluation_path.is_file():
            evaluation, checksum = load(evaluation_path)
            artifact_hashes[str(evaluation_path)] = checksum
            row["nativeEvaluationPassed"] = evaluation.get("passed")
            row["baseline"] = evaluation_arm(evaluation.get("baseline", {}))
            row["candidate"] = evaluation_arm(evaluation.get("candidate", {}))
            row["evaluationDigest"] = evaluation.get("digest")
            row["identityMatches"] = evaluation.get("proposalId") == result.get("proposalId")
        else:
            row.update(baseline={"available": False, "observedEvaluatorCompletions": 0},
                       candidate={"available": False, "observedEvaluatorCompletions": 0},
                       nativeEvaluationPassed=None, identityMatches=None)
        row["pairedComponentDifferences"] = paired_deltas(row)
        rows.append(row)
    slots = [row["slot"] for row in rows]
    if len(set(slots)) != len(slots) or any(type(slot) is not int or not 1 <= slot <= 10 for slot in slots):
        raise ValueError("Completed iteration identities are invalid or repeated.")
    qualified = [row for row in rows if row["nativeQualified"] and finite(row["candidate"].get("compositeScore")) is not None]
    ordered = sorted(qualified, key=lambda row: (-row["candidate"]["compositeScore"], row["patchDigest"]))
    author_calls = sum(row["author"]["observedAssistantCompletions"] for row in rows)
    evaluator_calls = sum(row[arm]["observedEvaluatorCompletions"] for row in rows for arm in ("baseline", "candidate"))
    model_counts = Counter()
    effort_fields = Counter()
    for row in rows:
        for model in row["author"]["models"]:
            model_counts[(model["provider"], model["model"])] += model["completions"]
        for field in row["author"]["effortFields"]:
            effort_fields[(field["field"], field["value"])] += field["completions"]
        for arm in ("baseline", "candidate"):
            value = row[arm]
            model = value.get("observedModel", {})
            if value["observedEvaluatorCompletions"]:
                model_counts[(model.get("provider"), model.get("model"))] += 1
            for field, observed in value.get("observedEffortFields", {}).items():
                effort_fields[(field, observed)] += value["observedEvaluatorCompletions"]
    return {"version": 1, "atUtc": datetime.now(timezone.utc).isoformat(), "completedSlots": len(rows),
            "allTenFinished": set(slots) == set(range(1, 11)), "qualifiedSlots": len(qualified), "iterations": rows,
            "nativeBest": {"slot": ordered[0]["slot"], "patchDigest": ordered[0]["patchDigest"],
                           "compositeScore": ordered[0]["candidate"]["compositeScore"],
                           "pairedComponentDifferences": ordered[0]["pairedComponentDifferences"]} if ordered else None,
            "calls": {"authorAssistantCompletions": author_calls, "evaluatorBatchCompletions": evaluator_calls,
                      "totalObservedCompletions": author_calls + evaluator_calls,
                      "providerInternalHttpAttempts": "unknown"},
            "observedModels": [{"provider": provider, "model": model, "completions": count}
                               for (provider, model), count in sorted(model_counts.items())],
            "observedEffortFields": [{"field": field, "value": value, "completions": count}
                                    for (field, value), count in sorted(effort_fields.items())],
            "effortObservation": "not-exposed" if not effort_fields else "partially-or-fully-exposed-see-fields",
            "artifactHashes": artifact_hashes,
            "limits": ["Development artifacts only; no reserved gates were opened or read.",
                       "Native qualification is separate from manual compatibility and production readiness.",
                       "One fresh stochastic case batch per evaluation arm; no replication or confidence interval.",
                       "Model effort is not inferred from requested settings when absent from SDK response metadata."]}


def markdown(report):
    lines = ["# Development metrics", "", "Native scores and compatibility are separate release conditions.", "",
             "| Slot | Outcome | Base composite | Candidate composite | Base decision | Candidate decision | Base worker | Candidate worker | Author completions | Eval completions |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in report["iterations"]:
        before, after = row["baseline"], row["candidate"]
        def metric(obj, name):
            return f"{obj[name]:.4f}" if finite(obj.get(name)) is not None else "unknown"
        values = [row["slot"], row["outcome"], metric(before, "compositeScore"), metric(after, "compositeScore"),
                  metric(before, "decisionScore"), metric(after, "decisionScore"), metric(before, "workerScore"), metric(after, "workerScore"),
                  row["author"]["observedAssistantCompletions"], before["observedEvaluatorCompletions"] + after["observedEvaluatorCompletions"]]
        lines.append("| " + " | ".join(str(value) for value in values) + " |")
    lines.extend(["", f"Completed slots: {report['completedSlots']}/10. Native qualified: {report['qualifiedSlots']}.",
                  "", "Observed completion counts: " + json.dumps(report["calls"]),
                  "", "Observed models: " + json.dumps(report["observedModels"]),
                  "", "Effort observation: " + report["effortObservation"] + ".",
                  "", "Observed response effort fields: " + json.dumps(report["observedEffortFields"]), ""])
    best = report["nativeBest"]
    if best and best.get("pairedComponentDifferences"):
        delta = best["pairedComponentDifferences"]
        lines.extend([f"Native best: slot {best['slot']} with paired composite delta {delta['compositeDelta']:.4f}, "
                      f"weighted decision contribution {delta['weightedDecisionContribution']:.4f}, "
                      f"and weighted worker contribution {delta['weightedWorkerContribution']:.4f}.", ""])
        if not delta["decisionGainMeasuredInPair"]:
            lines.extend(["No decision-score gain was measured in the selected pair.", ""])
    lines.extend(["| Slot | Arm | All case flags | Decision safety/schema | Worker hard cases | Inherited soft-case flags |",
                  "| --- | --- | ---: | ---: | ---: | ---: |"])
    for row in report["iterations"]:
        for arm_name in ("baseline", "candidate"):
            arm = row[arm_name]
            def flags(key):
                value = arm.get(key)
                return f"{value['passed']}/{value['total']}" if isinstance(value, dict) else "unknown"
            lines.append("| " + " | ".join([str(row["slot"]), arm_name, flags("caseFlags"),
                flags("decisionSafetySchemaFlags"), flags("workerHardCases"), flags("workerSoftInheritedFlags")]) + " |")
    lines.extend(["", "The eight soft-case flags inherit global hard-gate status; they are not eight additional independent safety tests.", ""])
    lines.extend("- " + item for item in report["limits"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--require-ten", action="store_true")
    args = parser.parse_args()
    report = summarize(args.iterations_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("completedSlots", "allTenFinished", "qualifiedSlots", "nativeBest", "calls", "observedModels", "effortObservation")}))
    return 0 if not args.require_ten or report["allTenFinished"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"passed": False, "errorCategory": type(error).__name__, "rawDiagnosticsSuppressed": True}))
        raise SystemExit(1)
