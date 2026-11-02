#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Comparable ontology case coverage and explicit residuals from supplied evidence.

This aggregator does not execute competency queries, SHACL or an OWL reasoner.
It pins local artifacts, keeps unknowns in the denominator and exposes conflicts.
Python 3.11+, standard library only.
"""
import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import semantic_model as core
import review_conflicts as conflicts

VERSION = "1.2.2"
STATUSES = {"pass", "fail", "partial", "unknown", "error"}
ACTIVE = {"open", "deferred", "decision_recorded_pending_validation"}


def must(test, message, path="/", code="INVALID_COVERAGE_INPUT"):
    core.require(test, message, path, code)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned(artifact, expected, base):
    must(core.nonempty(artifact) and core.nonempty(expected), "Provide a local artifact and SHA-256")
    path = (base / artifact).resolve()
    must(path.is_file(), "Evidence artifact does not exist: " + str(path), code="MISSING_ARTIFACT")
    must(sha(path) == expected, "Artifact changed: " + str(path), code="STALE_ARTIFACT")
    return path


def number(value):
    return type(value) is int or type(value) is float and math.isfinite(value)


def percentage(count, total):
    if not total:
        return None
    try:
        scaled = 100.0 * count
    except OverflowError as exc:
        scaled = math.inf
    try:
        # Retain ordinary historical rounding; use ratio-first arithmetic only
        # when the intermediate multiplication cannot remain finite.
        value = scaled / total if number(scaled) else (count / total) * 100.0
    except OverflowError as exc:
        raise core.EngineError("NUMERIC_OVERFLOW", "Coverage ratio is not representable as a finite number") from exc
    must(number(value), "Coverage ratio must remain finite", code="NUMERIC_OVERFLOW")
    return value


def check_suite(suite):
    core.unknown(suite, {"id", "version", "cases"}, "/suite")
    must(core.nonempty(suite.get("id")) and core.nonempty(suite.get("version")), "Suite id and version required")
    must(isinstance(suite.get("cases"), list), "cases must be an array")
    seen = set()
    for case in suite["cases"]:
        core.unknown(case, {"id", "title", "expected", "method", "kind", "required", "weight", "applicable", "exclusion_reason"}, "/suite/cases")
        cid = case.get("id")
        must(core.nonempty(cid) and cid not in seen, "Case IDs must be unique")
        seen.add(cid)
        must(all(core.nonempty(case.get(k)) for k in ("title", "expected", "method")), "Each case needs title, expected and method")
        must(core.nonempty(case.get("kind", "requirement")), "kind must be a nonempty string")
        must(isinstance(case.get("required", False), bool) and isinstance(case.get("applicable", True), bool), "required/applicable must be booleans")
        must(number(case.get("weight", 1)) and case.get("weight", 1) > 0, "Weights must be positive finite numbers")
        if not case.get("applicable", True):
            must(core.nonempty(case.get("exclusion_reason")), "Global exclusions require a reason")
            must(not case.get("required", False), "A required case cannot be excluded")


def formal_checks(candidate, base):
    payload = candidate.get("formal_checks", {})
    core.unknown(payload, {"owl_consistency", "shacl"}, "/formal_checks")
    result = {}
    for axis, statuses in [("owl_consistency", {"not_checked", "consistent", "inconsistent", "error"}), ("shacl", {"not_checked", "conformant", "nonconformant", "error"})]:
        item = payload.get(axis, {"status": "not_checked"})
        core.unknown(item, {"status", "tool", "version", "artifact", "sha256", "ontology_sha256"}, "/formal_checks/" + axis)
        must(isinstance(item.get("status"), str) and item["status"] in statuses, "Unsupported formal-check status")
        if item["status"] != "not_checked":
            must(core.nonempty(item.get("tool")) and core.nonempty(item.get("version")), "Executed formal checks need tool/version")
            must(item.get("ontology_sha256") == candidate["ontology"]["sha256"], "Formal check belongs to another ontology", code="STALE_ASSESSMENT")
            pinned(item.get("artifact"), item.get("sha256"), base)
        result[axis] = copy.deepcopy(item)
    return result


def conflict_review(candidate, base):
    binding = candidate.get("conflict_review")
    if binding is None:
        return {"scan_status": "not_provided", "open_count": None, "findings": []}
    core.unknown(binding, {"artifact", "sha256", "ontology_sha256"}, "/conflict_review")
    must(binding.get("ontology_sha256") == candidate["ontology"]["sha256"], "Conflict review belongs to another ontology", code="STALE_ASSESSMENT")
    path = pinned(binding.get("artifact"), binding.get("sha256"), base)
    report = core.read_json(path)
    must(isinstance(report, dict) and report.get("scan_status") in ("completed", "incomplete", "error"), "Malformed conflict report")
    if report["scan_status"] != "completed":
        return {"scan_status": report["scan_status"], "open_count": None, "findings": [], "artifact": str(path), "sha256": binding["sha256"]}
    validated = conflicts.record_decisions(report, {"schema_version": "1", "review_revision": report.get("review_revision"), "decisions": []})
    for item in validated["findings"]:
        must(item["status"] in ACTIVE | {"scope_difference"}, "A declared resolution needs a fresh validated scan; unsupported finding state")
    return {"scan_status": "completed", "open_count": sum(f["status"] in ACTIVE for f in validated["findings"]), "findings": validated["findings"], "artifact": str(path), "sha256": binding["sha256"]}


def metric(rows):
    total = len(rows)
    try:
        weight = sum(r["weight"] for r in rows)
    except OverflowError as exc:
        raise core.EngineError("NUMERIC_OVERFLOW", "Total case weight is not representable as a finite number") from exc
    must(number(weight), "Total case weight must remain finite", code="NUMERIC_OVERFLOW")
    statuses = {state: {"count": sum(r["effective_status"] == state for r in rows)} for state in ["pass", "fail", "partial", "unknown", "error", "conflicted"]}
    for value in statuses.values():
        value["percent"] = percentage(value["count"], total)
    passed = statuses["pass"]["count"]
    return {"applicable_cases": total, "fully_covered_cases": passed, "strict_coverage_percent": percentage(passed, total),
            "not_fully_covered_cases": total - passed, "not_fully_covered_percent": percentage(total - passed, total),
            "status_breakdown": statuses, "weighted_strict_coverage_percent": percentage(sum(r["weight"] for r in rows if r["effective_status"] == "pass"), weight),
            "weight_denominator": weight, "partial_credit_assumed": False}


def evaluate(payload, base, previous=None):
    core.unknown(payload, {"schema_version", "suite", "candidates"}, "/")
    must(payload.get("schema_version") == "1", "Supported coverage schema_version is 1")
    suite = payload.get("suite")
    check_suite(suite)
    must(isinstance(payload.get("candidates"), list), "candidates must be an array")
    case_map = {c["id"]: c for c in suite["cases"]}
    outputs, seen = [], set()
    for candidate in payload["candidates"]:
        core.unknown(candidate, {"id", "label", "ontology", "assessments", "conflict_review", "formal_checks"}, "/candidates")
        cid = candidate.get("id")
        must(core.nonempty(cid) and cid not in seen and core.nonempty(candidate.get("label")), "Candidate IDs must be unique and labels nonempty")
        seen.add(cid)
        ontology = candidate.get("ontology")
        core.unknown(ontology, {"iri", "version", "artifact", "sha256"}, "/ontology")
        must(core.nonempty(ontology.get("iri")) and core.nonempty(ontology.get("version")), "Record ontology IRI and version")
        pinned(ontology.get("artifact"), ontology.get("sha256"), base)
        formal = formal_checks(candidate, base)
        review = conflict_review(candidate, base)
        cards = {c["id"]: c for c in review["findings"]}
        must(isinstance(candidate.get("assessments"), list), "assessments must be an array")
        observations = {}
        for assessment in candidate["assessments"]:
            core.unknown(assessment, {"case_id", "status", "observed", "reason", "evidence_mode", "evidence", "result_artifact", "result_sha256", "ontology_sha256", "conflict_ids", "next_action"}, "/assessments")
            case_id = assessment.get("case_id")
            must(core.nonempty(case_id) and case_id in case_map and case_id not in observations, "Assessment IDs must be unique and refer to a registered case")
            state = assessment.get("status")
            must(isinstance(state, str) and state in STATUSES, "Unsupported result; candidate-specific exclusions are not allowed")
            must(assessment.get("ontology_sha256") == ontology["sha256"], "Assessment belongs to another ontology version/hash", code="STALE_ASSESSMENT")
            must(core.nonempty(assessment.get("observed")) and core.nonempty(assessment.get("reason")), "State what was observed and why")
            evidence = assessment.get("evidence", [])
            must(isinstance(evidence, list), "evidence must be an array")
            for item in evidence:
                core.unknown(item, {"locator", "observation"}, "/evidence")
                must(core.nonempty(item.get("locator")) and core.nonempty(item.get("observation")), "Evidence needs locator and observation")
            if state in ("pass", "fail", "partial"):
                must(assessment.get("evidence_mode") in ("executed", "reviewed") and bool(evidence), "Claimed coverage needs evidence and its assessment mode")
            if "evidence_mode" in assessment:
                must(assessment["evidence_mode"] in ("executed", "reviewed", "not_provided"), "Unsupported evidence mode; label similarity alone is not a semantic pass")
            if assessment.get("evidence_mode") == "executed":
                pinned(assessment.get("result_artifact"), assessment.get("result_sha256"), base)
            if state != "pass":
                must(core.nonempty(assessment.get("next_action")), "Every residual case needs a next action")
            ids = assessment.get("conflict_ids", [])
            must(core.string_list(ids) and len(ids) == len(set(ids)) and set(ids) <= set(cards), "Use IDs from the current pinned conflict review")
            observations[case_id] = assessment
        rows, excluded = [], []
        for case in suite["cases"]:
            if not case.get("applicable", True):
                excluded.append(copy.deepcopy(case))
                continue
            assessment = observations.get(case["id"], {"status": "unknown", "observed": "No assessment supplied", "reason": "Missing evidence is not failure or non-applicability", "evidence": [], "next_action": "Execute or review this case against the pinned candidate", "conflict_ids": []})
            active_ids = [i for i in assessment.get("conflict_ids", []) if cards[i]["status"] in ACTIVE]
            effective = "conflicted" if assessment["status"] == "pass" and active_ids else assessment["status"]
            rows.append({"case_id": case["id"], "title": case["title"], "kind": case.get("kind", "requirement"), "expected": case["expected"], "method": case["method"],
                         "required": case.get("required", False), "weight": case.get("weight", 1), "reported_status": assessment["status"], "effective_status": effective,
                         "observed": assessment["observed"], "reason": assessment["reason"], "evidence_mode": assessment.get("evidence_mode", "not_provided"), "evidence": copy.deepcopy(assessment.get("evidence", [])),
                         "conflict_ids": copy.deepcopy(assessment.get("conflict_ids", [])), "blocking_conflict_ids": active_ids,
                         "next_action": "Resolve linked contradictions and rerun the case" if effective == "conflicted" else assessment.get("next_action")})
        summary = metric(rows)
        missing_required = [r["case_id"] for r in rows if r["required"] and r["effective_status"] != "pass"]
        blocked_formal = formal["owl_consistency"]["status"] in ("inconsistent", "error") or formal["shacl"]["status"] in ("nonconformant", "error")
        gate = "not_evaluable" if not rows else "blocked_by_formal_check" if blocked_formal else "blocked_by_conflicts" if review["open_count"] else "blocked_by_required_cases" if missing_required else "conflicts_not_assessed" if review["scan_status"] != "completed" else "candidate_with_gaps" if summary["not_fully_covered_cases"] else "covered_on_declared_suite"
        outputs.append({"id": cid, "label": candidate["label"], "ontology": copy.deepcopy(ontology), "summary": summary, "by_kind": {kind: metric([r for r in rows if r["kind"] == kind]) for kind in sorted({r["kind"] for r in rows})},
                        "required_cases_not_fully_covered": missing_required, "readiness": gate, "formal_checks": formal, "conflict_review": review,
                        "cases": rows, "residual_cases": [r for r in rows if r["effective_status"] != "pass"], "excluded_cases": excluded,
                        "measurement_basis": "Aggregates supplied case assessments; artifact hashes verify identity, not the truth or completeness of the observations."})
    report = {"schema_version": "1", "tool_version": VERSION, "status": "completed", "suite": copy.deepcopy(suite), "suite_fingerprint": conflicts.digest(suite),
              "candidates": outputs, "scope": "Strict coverage is full passes divided by all globally applicable cases. Partial, unknown, error and conflicted remain in the denominator. Coverage, formal consistency and ontology conflicts are separate axes."}
    if previous is not None:
        must(isinstance(previous, dict) and previous.get("schema_version") == "1" and previous.get("status") == "completed" and isinstance(previous.get("candidates"), list), "Malformed previous coverage report")
        check_suite(previous.get("suite"))
        must(previous.get("suite_fingerprint") == conflicts.digest(previous["suite"]), "Previous suite fingerprint is stale", code="STALE_PREVIOUS_REPORT")
        old_cases = {c["id"]: c for c in previous["suite"]["cases"] if c.get("applicable", True)}
        old_ids = set()
        for old_candidate in previous["candidates"]:
            must(isinstance(old_candidate, dict) and core.nonempty(old_candidate.get("id")) and old_candidate["id"] not in old_ids and isinstance(old_candidate.get("cases"), list) and isinstance(old_candidate.get("ontology"), dict), "Malformed previous candidate")
            old_ids.add(old_candidate["id"])
            observed_ids = set()
            for row in old_candidate["cases"]:
                must(isinstance(row, dict) and core.nonempty(row.get("case_id")) and row["case_id"] in old_cases and row["case_id"] not in observed_ids, "Malformed previous case set")
                observed_ids.add(row["case_id"])
                must(isinstance(row.get("effective_status"), str) and row["effective_status"] in STATUSES | {"conflicted"} and core.exact_json_equal(row.get("weight"), old_cases[row["case_id"]].get("weight", 1)), "Malformed previous result")
            must(observed_ids == set(old_cases) and core.exact_json_equal(old_candidate.get("summary"), metric(old_candidate["cases"])), "Previous metrics or denominator do not reproduce", code="STALE_PREVIOUS_REPORT")
        if previous.get("suite_fingerprint") != report["suite_fingerprint"]:
            report["comparison"] = {"status": "not_comparable", "reason": "Suite or denominator changed; no improvement percentage is calculated"}
        else:
            old = {c["id"]: c for c in previous["candidates"]}
            changes = []
            for candidate in outputs:
                if candidate["id"] not in old:
                    changes.append({"id": candidate["id"], "status": "new_candidate"})
                    continue
                before = old[candidate["id"]]
                was = {r["case_id"]: r["effective_status"] for r in before["cases"]}
                now = {r["case_id"]: r["effective_status"] for r in candidate["cases"]}
                a, b = before["summary"]["strict_coverage_percent"], candidate["summary"]["strict_coverage_percent"]
                changes.append({"id": candidate["id"], "status": "comparable", "before_ontology": before["ontology"], "after_ontology": candidate["ontology"], "change_percentage_points": b - a if a is not None and b is not None else None,
                                "newly_fully_covered": [i for i in now if now[i] == "pass" and was.get(i) != "pass"], "regressions": [i for i in now if now[i] != "pass" and was.get(i) == "pass"], "still_not_fully_covered": [i for i in now if now[i] != "pass"]})
            report["comparison"] = {"status": "comparable", "candidates": changes, "removed_candidate_ids": sorted(set(old) - seen)}
    return report


def pct(value):
    return "not evaluable" if value is None else f"{value:.1f}%"


def render_markdown(report):
    lines = ["# Candidate ontology coverage and gaps", "", "Suite: " + report["suite"]["id"] + " · version " + report["suite"]["version"], "",
             "Coverage is measured over the declared cases. The percentage does not certify logical consistency or the universal absence of contradictions.", "",
             "| Ontology | Passed / applicable | Strict coverage | Observed failure | Partial | Unverified | Error | Cases blocked by conflicts | Open conflicts |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for candidate in report["candidates"]:
        s = candidate["summary"];b = s["status_breakdown"]
        count = candidate["conflict_review"]["open_count"]
        lines.append("| " + candidate["label"].replace("|", "\\|") + " | " + str(s["fully_covered_cases"]) + "/" + str(s["applicable_cases"]) + " | " + pct(s["strict_coverage_percent"]) + " | " + " | ".join(pct(b[k]["percent"]) for k in ("fail", "partial", "unknown", "error", "conflicted")) + " | " + (str(count) if count is not None else "not assessed") + " |")
    lines += ["", "Weighted coverage uses the weight of fully covered cases divided by total applicable case weight. The weight denominator is separate from the number of cases; partial results receive no assumed partial credit.", "",
              "| Ontology | Weighted strict coverage | Weight denominator |", "|---|---:|---:|"]
    for candidate in report["candidates"]:
        summary = candidate["summary"]
        lines.append("| " + candidate["label"].replace("|", "\\|") + " | " + pct(summary["weighted_strict_coverage_percent"]) + " | " + str(summary["weight_denominator"]) + " |")
    for candidate in report["candidates"]:
        lines += ["", "## " + candidate["label"], "", "IRI: " + candidate["ontology"]["iri"] + " · version: " + candidate["ontology"]["version"], "", "Status: " + candidate["readiness"], "",
                  "Not fully covered: " + pct(candidate["summary"]["not_fully_covered_percent"]) + ". This includes partial, unknown and error results; it is not equivalent to demonstrated noncompliance.", "",
                  "Pending required cases: " + (", ".join(candidate["required_cases_not_fully_covered"]) or "none"), "",
                  "OWL: " + candidate["formal_checks"]["owl_consistency"]["status"] + "; SHACL: " + candidate["formal_checks"]["shacl"]["status"] + "; conflict scan: " + candidate["conflict_review"]["scan_status"], ""]
        for item in candidate["conflict_review"]["findings"]:
            lines += ["### Conflict " + item["id"], "", item["classification"] + " · " + item["status"], "", item["explanation"], ""]
            for assertion in item["assertions"]:
                lines += ["Assertion/element: " + assertion["id"], "", "```json", json.dumps(assertion["statement"], ensure_ascii=False, indent=2), "```", ""]
                for evidence in assertion["evidence"]:
                    lines += ["Source: " + evidence["locator"], "", "> " + evidence["original_excerpt"].replace("\n", "\n> "), ""]
            lines += ["- `" + o["choice"] + "`: " + o["description"] for o in item["resolution_options"]] + [""]
        for row in candidate["residual_cases"]:
            lines += ["### " + row["case_id"] + " — " + row["title"], "", "Status: " + row["effective_status"] + " (original result: " + row["reported_status"] + ")", "", "Expected: " + row["expected"], "", "Observed: " + row["observed"], "", "Reason: " + row["reason"], "", "Next action: " + row["next_action"], ""]
            for evidence in row["evidence"]:
                lines += ["- " + evidence["locator"] + ": " + evidence["observation"]]
        if candidate["excluded_cases"]:
            lines += ["", "Justified common exclusions: " + "; ".join(c["id"] + ": " + c["exclusion_reason"] for c in candidate["excluded_cases"]), ""]
    if "comparison" in report:
        lines += ["", "## Progress", "", "```json", json.dumps(report["comparison"], ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--previous")
    args = parser.parse_args(argv)
    inputs = {Path(x).resolve() for x in (args.input, args.previous) if x}
    try:
        payload = core.read_json(args.input)
        base = Path(args.input).resolve().parent
        report = evaluate(payload, base, core.read_json(args.previous) if args.previous else None)
        # Protect pinned ontology, measurements, conflict reports and prior inputs.
        for candidate in payload["candidates"]:
            inputs.add((base / candidate["ontology"]["artifact"]).resolve())
            if candidate.get("conflict_review"):
                inputs.add((base / candidate["conflict_review"]["artifact"]).resolve())
            for row in candidate["assessments"]:
                if row.get("result_artifact"):
                    inputs.add((base / row["result_artifact"]).resolve())
            for formal in candidate.get("formal_checks", {}).values():
                if formal.get("artifact"):
                    inputs.add((base / formal["artifact"]).resolve())
        for output in (args.report, args.markdown):
            if output:
                must(not core.aliases_input(output, inputs) and not Path(output).exists(), "Preserve inputs and previous reports; choose a new output path", code="OUTPUT_COLLISION")
        must(not args.markdown or not core.aliases_input(args.markdown, {Path(args.report).resolve()}), "JSON/Markdown output paths collide", code="OUTPUT_COLLISION")
        core.write_new(args.report, report, inputs)
        if args.markdown:
            p = Path(args.markdown);p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(render_markdown(report))
        print(json.dumps({"status": "completed", "candidates": len(report["candidates"]), "report": str(Path(args.report).resolve())}, ensure_ascii=False))
        # A computed 90% report is a successful measurement, not a 100% acceptance.
        return 0
    except (core.EngineError, OSError) as exc:
        print(json.dumps({"status": "error", "errors": [{"code": exc.code if isinstance(exc, core.EngineError) else "IO_ERROR", "message": str(exc)}]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
