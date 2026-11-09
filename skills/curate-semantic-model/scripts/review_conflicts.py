#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find reviewable conflicts and record explicit decisions, without editing models.

Uses normalized, sourced assertions and declared rules; not an unrestricted
natural-language contradiction detector. Python 3.11+, standard library only.
"""
import argparse
import copy
import hashlib
import itertools
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import semantic_model as core

VERSION = "1.1.2"
OPTIONS = {
    "prefer_assertion": "Prioritize one assertion and retain the others as disputed; validate the change before accepting it.",
    "separate_scopes": "Retain both under distinct contexts, versions or periods, supplying the distinguishing data.",
    "correct_assertions": "Correct or replace assertions with revised wording and evidence.",
    "revise_rule": "Review and version the rule if it does not represent the domain requirement.",
    "request_evidence": "Request evidence or scope information before deciding.",
    "defer": "Leave pending and preserve the alternatives without resolving them automatically.",
}
QUESTIONS = {
    "confirmed_conflict": "Which assertion should govern in the shared scope, or what evidence warrants a correction?",
    "possible_conflict": "What evidence would establish whether these assertions apply to the same subject and scope?",
    "constraint_conflict": "Should the graph change to meet the rule, or does the evidence warrant revising the rule?",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def must(condition, message, path="/", code="INVALID_CONFLICT_INPUT", actual=None):
    core.require(condition, message, path, code, actual)


def check_scope(scope):
    core.unknown(scope, {"context", "version", "unit", "time"}, "/scope")
    for key in ("context", "version", "unit"):
        must(key not in scope or core.nonempty(scope[key]), "Scope qualifiers must be nonempty strings", "/scope/" + key)
    temporal = scope.get("time")
    if temporal is None:
        return
    must(isinstance(temporal, dict), "time must be an object", "/scope/time")
    kind = temporal.get("kind")
    must(kind in ("all_time", "interval", "unknown"), "Unsupported temporal scope", "/scope/time/kind")
    core.unknown(temporal, {"kind", "from", "to"} if kind == "interval" else {"kind"}, "/scope/time")
    if kind == "interval":
        must(set(temporal) == {"kind", "from", "to"} and (temporal["from"] is not None or temporal["to"] is not None), "An interval needs explicit endpoints and at least one date", "/scope/time")
        values = []
        for key in ("from", "to"):
            value = temporal[key]
            try:
                parsed = date.fromisoformat(value) if isinstance(value, str) else None
            except ValueError as exc:
                raise core.EngineError("INVALID_CONFLICT_INPUT", "Invalid ISO date", "/scope/time/" + key, value) from exc
            must(value is None or parsed is not None and parsed.isoformat() == value, "Dates must use YYYY-MM-DD or null", "/scope/time/" + key)
            values.append(parsed)
        must(not all(values) or values[0] <= values[1], "Interval endpoints are inverted", "/scope/time")


def check_claims(payload, model):
    core.unknown(payload, {"schema_version", "functional_predicates", "assertions"}, "/claims")
    must(payload.get("schema_version") == "1", "Supported claims schema_version is 1")
    must(core.string_list(payload.get("functional_predicates", [])), "functional_predicates must be a string array")
    must(isinstance(payload.get("assertions"), list), "assertions must be an array")
    sources = {s["id"] for s in model["sources"]}
    nodes = {n["id"] for n in model["nodes"]}
    seen = set()
    for assertion in payload["assertions"]:
        core.unknown(assertion, {"id", "subject", "predicate", "value", "polarity", "source_ids", "scope", "normalization"}, "/assertions")
        aid = assertion.get("id")
        must(core.nonempty(aid) and aid not in seen, "Assertion IDs must be unique nonempty strings")
        seen.add(aid)
        must(core.nonempty(assertion.get("subject")) and assertion["subject"] in nodes, "Assertion subject must name a model node", "/assertions/subject")
        must(core.nonempty(assertion.get("predicate")), "Assertion predicate is required")
        must("value" in assertion and (assertion["value"] is None or type(assertion["value"]) in (str, bool, int, float)), "Assertion value must be scalar or null")
        must(assertion.get("polarity") in ("positive", "negative"), "Declare positive or negative polarity")
        ids = assertion.get("source_ids")
        must(core.string_list(ids) and bool(ids) and set(ids) <= sources, "Every assertion needs known source evidence", "/assertions/source_ids")
        check_scope(assertion.get("scope", {}))
        normalization = assertion.get("normalization", {"status": "unreviewed"})
        core.unknown(normalization, {"status", "reviewer", "rationale"}, "/assertions/normalization")
        must(normalization.get("status") in ("reviewed", "unreviewed"), "Invalid normalization status")
        if normalization["status"] == "reviewed":
            must(core.nonempty(normalization.get("reviewer")) and core.nonempty(normalization.get("rationale")), "Reviewed normalization needs a reviewer and rationale")


def equal_values(a, b):
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    return type(a) is type(b) and a == b


def compare_scopes(a, b):
    separate, uncertain = [], []
    for key in ("context", "version"):
        left, right = a.get("scope", {}).get(key), b.get("scope", {}).get(key)
        if left and right and left != right:
            separate.append(key + "_differs")
        elif key == "context" and (not left or not right) or key == "version" and bool(left) != bool(right):
            uncertain.append(key + "_unknown")
    times = [x.get("scope", {}).get("time") or {"kind": "unknown"} for x in (a, b)]
    if any(t["kind"] == "unknown" for t in times):
        uncertain.append("time_unknown")
    else:
        bounds = [(None, None) if t["kind"] == "all_time" else (t["from"], t["to"]) for t in times]
        if bounds[0][1] and bounds[1][0] and bounds[0][1] < bounds[1][0] or bounds[1][1] and bounds[0][0] and bounds[1][1] < bounds[0][0]:
            separate.append("time_disjoint")
    units = [x.get("scope", {}).get("unit") for x in (a, b)]
    if units[0] != units[1]:
        uncertain.append("unit_comparison_required")
    elif units[0] is None and any(type(x["value"]) in (int, float) for x in (a, b)):
        uncertain.append("numeric_unit_unknown")
    return ("separate" if separate else "unknown" if uncertain else "same"), separate + uncertain


def public_assertion(record, sources, kind):
    item = {"id": record["id"], "kind": kind, "statement": copy.deepcopy(record), "evidence": []}
    for sid in record.get("source_ids", []):
        source = sources[sid]
        item["evidence"].append({"source_id": sid, "locator": source["locator"], "original_excerpt": source["text"], "source_fingerprint": digest(source)})
    return item


def card(kind, rule, assertions, explanation, contract, reasons=None):
    contract_fingerprint = digest(contract)
    fingerprint = digest({"kind": kind, "rule": rule, "assertions": sorted(assertions, key=lambda x: (x["kind"], x["id"])), "contract_fingerprint": contract_fingerprint})
    options = ["correct_assertions", "revise_rule", "request_evidence", "defer"] if kind == "constraint_conflict" else ["prefer_assertion", "separate_scopes", "correct_assertions", "request_evidence", "defer"]
    return {"id": "conflict:" + fingerprint[:20], "fingerprint": fingerprint, "contract_fingerprint": contract_fingerprint, "classification": kind,
            "status": "scope_difference" if kind == "scope_difference" else "open", "semantic_status": "needs_review",
            "requires_user_decision": kind != "scope_difference", "rule": rule, "assertions": assertions,
            "explanation": explanation, "scope_notes": reasons or [],
            "resolution_options": [{"choice": key, "description": OPTIONS[key]} for key in options],
            "resolution": None}


def scan(model, contract, claims=None):
    validation = core.validate(model, contract)
    # Data-shape errors can make extraction/grounding incomplete. Preserve the
    # validation report rather than manufacture an empty successful conflict scan.
    inspectable = {"INCOMPATIBLE_RELATION", "CYCLE_FORBIDDEN", "CARDINALITY_VIOLATION", "COMPETENCY_CHECK_FAILED", "REVIEW_REQUIRED"}
    blocked = [e for e in validation["errors"] if e["code"] not in inspectable]
    require_valid_collections = all(isinstance(model.get(k), list) and all(isinstance(x, dict) and core.nonempty(x.get("id")) for x in model[k]) for k in ("sources", "nodes", "relations"))
    if blocked or not require_valid_collections:
        return {"schema_version": "1", "tool_version": VERSION, "scan_status": "incomplete", "semantic_status": "not_run", "validation": validation, "findings": [], "message": "Repair invalid records before claiming contradiction coverage.", "review_revision": digest({"model": model, "contract": contract, "claims": claims})}
    sources = {s["id"]: s for s in model["sources"]}
    findings, observed = [], set()
    relations = model["relations"]
    for a, b in itertools.combinations(relations, 2):
        ar, br = contract["relations"][a["type"]], contract["relations"][b["type"]]
        exclusive = b["type"] in ar.get("exclusive_with", []) or a["type"] in br.get("exclusive_with", [])
        same_pair = (a["from"], a["to"]) == (b["from"], b["to"]) or (ar.get("symmetric") or br.get("symmetric")) and (a["from"], a["to"]) == (b["to"], b["from"])
        if exclusive and same_pair:
            pair = tuple(sorted((a["id"], b["id"])))
            if pair in observed:
                continue
            observed.add(pair)
            findings.append(card("constraint_conflict", {"id": "exclusive_predicates", "predicates": sorted((a["type"], b["type"])), "version": contract["version"]}, [public_assertion(x, sources, "relation") for x in (a, b)], "The two relations are incompatible for the same pair under the contract. The rule does not determine which source is correct.", contract))
    for error in validation["errors"]:
        if error["code"] == "CYCLE_FORBIDDEN":
            witness, predicate = error["actual"], error["type"]
            steps = set(zip(witness, witness[1:]))
            involved = [e for e in relations if e["type"] == predicate and (e["from"], e["to"]) in steps]
            findings.append(card("constraint_conflict", {"id": "acyclic", "predicate": predicate, "version": contract["version"]}, [public_assertion(e, sources, "relation") for e in involved], "These edges close a cycle in a predicate declared to be a DAG; review the edges or the profile rule.", contract, witness))
        elif error["code"] == "CARDINALITY_VIOLATION":
            node = next(n for n in model["nodes"] if n["id"] == error["entity"])
            prefix = "/nodes/" + node["id"] + "/outgoing/"
            predicate = error["path"][len(prefix):]
            involved = [e for e in relations if e["from"] == node["id"] and e["type"] == predicate]
            items = [public_assertion(node, sources, "node")] + [public_assertion(e, sources, "relation") for e in involved]
            findings.append(card("constraint_conflict", {"id": "cardinality", "predicate": predicate, "expected": error["expected"], "actual": error["actual"], "version": contract["version"]}, items, "The set violates the declared cardinality. This does not establish that a source is false.", contract))
        elif error["code"] == "COMPETENCY_CHECK_FAILED":
            qid = error["path"].removeprefix("/checks/")
            test = next(c for c in contract["checks"] if c["id"] == qid)
            involved = [n for n in model["nodes"] if n["id"] in set(error["expected"]) | set(error["actual"])]
            ids = {sid for n in involved for sid in n.get("source_ids", [])}
            if test["query"].get("source_id") in sources:
                ids.add(test["query"]["source_id"])
            record = {"id": "check:" + qid, "query": test["query"], "expected": error["expected"], "actual": error["actual"], "source_ids": sorted(ids)}
            findings.append(card("constraint_conflict", {"id": "competency_check", "check_id": qid, "version": contract["version"]}, [public_assertion(record, sources, "competency")], "The observed answer does not match the agreed obligation. Review the change or expectation before integrating the candidate.", contract))
        elif error["code"] == "REVIEW_REQUIRED":
            edge = next(e for e in relations if e["id"] == error["entity"])
            findings.append(card("constraint_conflict", {"id": "review_required", "predicate": edge["type"], "version": contract["version"]}, [public_assertion(edge, sources, "relation")], "This relation lacks the accepted, attributed review required by the contract. Review the assertion and its evidence, or explicitly revise the rule; missing review does not establish that a source is false.", contract))
    warnings = []
    if claims is not None:
        check_claims(claims, model)
        groups = {}
        for assertion in claims["assertions"]:
            if assertion["value"] is None:
                warnings.append({"code": "UNKNOWN_VALUE_NOT_NEGATION", "assertion_id": assertion["id"]})
                continue
            groups.setdefault((assertion["subject"], assertion["predicate"]), []).append(assertion)
        for group in groups.values():
            for a, b in itertools.combinations(group, 2):
                equal = equal_values(a["value"], b["value"])
                opposition = equal and a["polarity"] != b["polarity"]
                functional = a["predicate"] in claims.get("functional_predicates", []) and a["polarity"] == b["polarity"] == "positive" and not equal
                if not opposition and not functional:
                    continue
                scope, reasons = compare_scopes(a, b)
                reviewed = all(x.get("normalization", {}).get("status") == "reviewed" for x in (a, b))
                kind = "scope_difference" if scope == "separate" else "confirmed_conflict" if scope == "same" and reviewed else "possible_conflict"
                if not reviewed:
                    reasons.append("normalization_needs_review")
                rule = {"id": "opposite_polarities" if opposition else "functional_predicate", "predicate": a["predicate"], "version": "claims-1"}
                explanation = "The assertions oppose each other under the declared rule. Review meaning and evidence; the engine does not choose a source."
                if kind == "scope_difference":
                    explanation = "The metadata declares distinct contexts, versions or periods; the assertions can coexist without contradiction within that scope."
                findings.append(card(kind, rule, [public_assertion(x, sources, "claim") for x in (a, b)], explanation, contract, reasons))
    findings.sort(key=lambda x: x["id"])
    revision = digest({"model": model, "contract": contract, "claims": claims})
    return {"schema_version": "1", "tool_version": VERSION, "scan_status": "completed", "review_revision": revision,
            "semantic_status": "needs_review" if findings else "not_run", "validation": validation, "findings": findings, "warnings": warnings,
            "counts": {"requires_user_decision": sum(x["requires_user_decision"] for x in findings), "scope_differences": sum(x["classification"] == "scope_difference" for x in findings)},
            "scope": "Declared exclusions, DAG/cardinality witnesses, normalized explicit negations and functional-property conflicts. No complete natural-language or OWL consistency claim. No conflict means none found within these implemented checks."}


def record_decisions(review, decisions):
    must(isinstance(review, dict) and review.get("schema_version") == "1" and core.nonempty(review.get("review_revision")) and isinstance(review.get("findings"), list), "Malformed conflict review")
    core.unknown(decisions, {"schema_version", "review_revision", "decisions"}, "/decisions")
    must(decisions.get("schema_version") == "1", "Supported decisions schema_version is 1")
    must(review.get("scan_status") == "completed", "Cannot resolve an incomplete scan")
    must(decisions.get("review_revision") == review.get("review_revision"), "Review inputs changed; rescan and check decisions", code="STALE_REVIEW")
    must(isinstance(decisions.get("decisions"), list), "decisions must be an array")
    result, seen = copy.deepcopy(review), set()
    cards = {}
    for item in result["findings"]:
        must(isinstance(item, dict) and all(core.nonempty(item.get(k)) for k in ("id", "fingerprint", "contract_fingerprint", "classification", "status")) and isinstance(item.get("assertions"), list) and isinstance(item.get("rule"), dict) and isinstance(item.get("resolution_options"), list), "Malformed conflict card")
        must(item["id"] not in cards and all(isinstance(a, dict) and core.nonempty(a.get("id")) and core.nonempty(a.get("kind")) for a in item["assertions"]), "Invalid or duplicate conflict identity")
        expected = digest({"kind": item["classification"], "rule": item["rule"], "assertions": sorted(item["assertions"], key=lambda x: (x["kind"], x["id"])), "contract_fingerprint": item["contract_fingerprint"]})
        must(item["fingerprint"] == expected and item["id"] == "conflict:" + expected[:20], "Review evidence changed; rescan before choosing", code="STALE_CONFLICT")
        must(all(isinstance(o, dict) and isinstance(o.get("choice"), str) and o["choice"] in OPTIONS for o in item["resolution_options"]), "Malformed resolution options")
        cards[item["id"]] = item
    for decision in decisions["decisions"]:
        core.unknown(decision, {"conflict_id", "fingerprint", "choice", "assertion_id", "reviewer", "rationale", "proposed_scopes", "replacement"}, "/decisions/decision")
        cid = decision.get("conflict_id")
        must(core.nonempty(cid) and cid in cards and cid not in seen, "Decision must name one current conflict exactly once")
        seen.add(cid)
        item = cards[cid]
        must(item["status"] in ("open", "scope_difference"), "Decision already recorded; preserve it and start a new revision")
        must(decision.get("fingerprint") == item["fingerprint"], "Conflict evidence changed", code="STALE_CONFLICT")
        allowed = {x["choice"] for x in item["resolution_options"]}
        must(isinstance(decision.get("choice"), str) and decision["choice"] in allowed, "Unsupported choice for this conflict")
        must(core.nonempty(decision.get("reviewer")) and core.nonempty(decision.get("rationale")), "Record the explicit reviewer and rationale")
        if decision["choice"] == "prefer_assertion":
            must(isinstance(decision.get("assertion_id"), str) and decision["assertion_id"] in {x["id"] for x in item["assertions"]}, "Select an assertion shown in this conflict")
        elif decision["choice"] == "separate_scopes":
            proposed = decision.get("proposed_scopes")
            must(isinstance(proposed, dict) and set(proposed) == {x["id"] for x in item["assertions"]}, "Provide proposed scopes for every assertion")
            for scope in proposed.values():
                check_scope(scope)
                must(bool(scope), "Provide an explicit scope discriminator")
            scoped = [dict(a["statement"], scope=proposed[a["id"]]) for a in item["assertions"]]
            must(len(scoped) == 2 and compare_scopes(*scoped)[0] == "separate", "The proposed scopes do not establish a contextual, version or temporal difference")
        elif decision["choice"] == "correct_assertions":
            must(core.nonempty(decision.get("replacement")), "Describe the proposed correction")
        item["resolution"] = dict(decision, recorded_at=datetime.now(timezone.utc).isoformat())
        item["status"] = "deferred" if decision["choice"] in ("defer", "request_evidence") else "decision_recorded_pending_validation"
    result["models_modified"] = False
    result["counts"] = {"requires_user_decision": sum(x["status"] == "open" and x["requires_user_decision"] for x in result["findings"]), "pending_validation": sum(x["status"] == "decision_recorded_pending_validation" for x in result["findings"]), "deferred": sum(x["status"] == "deferred" for x in result["findings"]), "scope_differences": sum(x["status"] == "scope_difference" for x in result["findings"])}
    result["resolution_scope"] = "Explicit choices recorded only. Apply the authorized correction to a new candidate, preserve disputed evidence, and rerun validation, competencies and conflict scan before declaring resolution."
    return result


def combine_for_review(model, addition):
    """Preview a complete proposed state even when its conflicts prevent staging."""
    core.unknown(addition, {"sources", "nodes", "relations", "bindings"}, "/addition")
    candidate = copy.deepcopy(model)
    for field in ("sources", "nodes", "relations"):
        must(isinstance(candidate.get(field), list) and isinstance(addition.get(field, []), list), "Model and addition collections must be arrays")
        candidate[field].extend(copy.deepcopy(addition.get(field, [])))
    must(isinstance(candidate.get("bindings", {}), dict) and isinstance(addition.get("bindings", {}), dict), "bindings must be objects")
    for source, targets in addition.get("bindings", {}).items():
        previous = candidate.get("bindings", {}).get(source, [])
        must(core.string_list(targets) and core.string_list(previous), "bindings must contain node-ID arrays")
        candidate.setdefault("bindings", {})[source] = sorted(set(previous) | set(targets))
    return candidate


def render_markdown(review):
    lines = ["# Conflicts for review", "", "Scan status " + review["scan_status"], ""]
    if review["scan_status"] == "incomplete":
        blockers = [
            {key: issue[key] for key in ("code", "path", "message")}
            for issue in review["validation"]["errors"]
        ]
        lines += ["## Scan blocked", "", review["message"], "", "Correct the input findings below and rerun the scan.", ""]
        lines += ["```json", json.dumps(blockers, ensure_ascii=False, indent=2), "```", ""]
        return "\n".join(lines)

    lines += ["Interpretation policy: Different positive values can coexist when a predicate is not declared functional. Unknown or absent values are not negations.", ""]
    unknowns = [warning for warning in review.get("warnings", []) if warning.get("code") == "UNKNOWN_VALUE_NOT_NEGATION"]
    if unknowns:
        lines += ["## Unknown values", ""]
        for warning in unknowns:
            lines += ["- `UNKNOWN_VALUE_NOT_NEGATION` — assertion " + json.dumps(warning["assertion_id"], ensure_ascii=False) + ": its null value is unknown, not evidence for negation."]
        lines += [""]
    for item in review["findings"]:
        lines += ["## " + item["id"], "", "Classification " + item["classification"], "", "Status " + item["status"], "", item["explanation"], ""]
        lines += ["**Governing rule**", "", "```json", json.dumps(item["rule"], ensure_ascii=False, indent=2), "```", ""]
        for index, assertion in enumerate(item["assertions"], 1):
            lines += [f"**Assertion {index}: {assertion['id']}**", "", "```json", json.dumps(assertion["statement"], ensure_ascii=False, indent=2), "```", ""]
            for evidence in assertion["evidence"]:
                lines += ["Source: " + evidence["source_id"] + " · " + evidence["locator"], "", "> " + evidence["original_excerpt"].replace("\n", "\n> "), ""]
        if item["scope_notes"]:
            lines += ["**Scope or witness details**", "", ", ".join(item["scope_notes"]), ""]
        if item["status"] == "open":
            question = QUESTIONS.get(item["classification"], "Which option is supported by the evidence and governing rule?")
            lines += ["**Decision question**", "", question, ""]
            lines += ["**Options**", ""] + ["- `" + option["choice"] + "` — " + option["description"] for option in item["resolution_options"]] + [""]
        elif item["status"] == "scope_difference":
            lines += ["Keep both assertions in their documented scopes. No decision is required.", ""]
        elif item["status"] == "decision_recorded_pending_validation":
            lines += ["**Validation needed**", "", "Validate the candidate against the displayed rule, rerun the competency checks, and rescan this conflict. Confirm that the candidate implements the recorded choice and preserves the evidence.", ""]
        elif item["status"] == "deferred" and item["resolution"]:
            if item["resolution"]["choice"] == "request_evidence":
                lines += ["Keep the alternatives pending until the requested evidence is available.", ""]
            else:
                lines += ["Keep the alternatives pending and revisit the recorded reason for deferral before choosing.", ""]
        if item["resolution"]:
            lines += ["**Recorded decision**", "", "```json", json.dumps(item["resolution"], ensure_ascii=False, indent=2), "```", ""]
    if not review["findings"]:
        lines += ["No cases were found by the implemented checks. This does not certify complete semantic consistency.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("scan")
    check.add_argument("--model", required=True)
    check.add_argument("--contract", required=True)
    check.add_argument("--claims")
    check.add_argument("--addition")
    resolve = commands.add_parser("decide")
    resolve.add_argument("--review", required=True)
    resolve.add_argument("--decisions", required=True)
    for command in (check, resolve):
        command.add_argument("--report", required=True)
        command.add_argument("--markdown")
    args = parser.parse_args(argv)
    inputs = {Path(v).resolve() for k, v in vars(args).items() if k in ("model", "contract", "claims", "addition", "review", "decisions") and v}
    try:
        must(not core.aliases_input(args.report, inputs), "Report cannot overwrite an input", code="INPUT_OVERWRITE_FORBIDDEN")
        if args.markdown:
            must(not core.aliases_input(args.markdown, inputs | {Path(args.report).resolve()}), "Markdown output collides with an input or JSON report", code="INPUT_OVERWRITE_FORBIDDEN")
        if args.command == "scan":
            model = core.read_json(args.model)
            if args.addition:
                must(isinstance(model, dict), "Model must be an object")
                model = combine_for_review(model, core.read_json(args.addition))
            result = scan(model, core.read_json(args.contract), core.read_json(args.claims) if args.claims else None)
        else:
            result = record_decisions(core.read_json(args.review), core.read_json(args.decisions))
        # Always create new review artifacts; never replace an existing decision log.
        for filename in (args.report, args.markdown):
            if filename:
                must(not Path(filename).exists(), "Review output already exists; choose a new revision path", code="OUTPUT_EXISTS")
        core.write_new(args.report, result, inputs)
        if args.markdown:
            output = Path(args.markdown)
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(render_markdown(result))
        code = 2 if result["scan_status"] != "completed" else 1 if any(x["status"] in ("open", "deferred", "decision_recorded_pending_validation") for x in result["findings"]) else 0
        print(json.dumps({"scan_status": result["scan_status"], "review_revision": result["review_revision"], "findings": len(result["findings"]), "report": str(Path(args.report).resolve()), "models_modified": False}, ensure_ascii=False))
        return code
    except (core.EngineError, OSError) as exc:
        print(json.dumps({"scan_status": "error", "models_modified": False, "errors": [{"code": exc.code if isinstance(exc, core.EngineError) else "OUTPUT_ERROR", "message": str(exc)}]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
