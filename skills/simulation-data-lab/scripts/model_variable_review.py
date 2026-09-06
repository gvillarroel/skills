#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate a declared variable review and render its frozen, human-facing views.

This module never discovers variables by running a target or executes review
text. A valid declaration is not proof of model completeness or implementation.
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
from typing import Any


DIMENSIONS = {
    "outcome-backtrace", "lifecycle", "dependencies-and-feedback",
    "heterogeneity-and-selection", "time-and-scale", "constraints-and-accounting",
    "rival-mechanisms", "evidence-gaps",
}
TREATMENTS = {"modeled", "fixed", "excluded", "unresolved"}
IMPACTS = {"high", "medium", "low", "unknown"}
ROLES = {"control", "exogenous", "state", "derived", "structural", "outcome"}
ID = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
MISSING = object()
MAX_ITEMS = 200


def _keys(value, required, label):
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError(f"{label} must contain exactly: {', '.join(sorted(required))}")


def _text(value, label, choices=None):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError(f"{label} must be nonempty text of at most 2000 characters")
    if choices is not None and value not in choices:
        raise ValueError(f"{label} must be one of: {', '.join(sorted(choices))}")
    return value


def _items(value, label, *, minimum=0):
    if not isinstance(value, list) or not minimum <= len(value) <= MAX_ITEMS:
        raise ValueError(f"{label} must be a list with {minimum} to {MAX_ITEMS} entries")
    return value


def _references(value, allowed, label, *, minimum=0):
    items = _items(value, label, minimum=minimum)
    for item in items:
        _text(item, label)
    if len(set(items)) != len(items) or set(items) - allowed:
        raise ValueError(f"{label} contains duplicate or unknown references")
    return items


def parameter_bindings(spec):
    bindings = {}
    for group, identity in (("scenarios", "scenarioId"), ("designPoints", "designPointId")):
        for owner in spec[group]:
            for parameter in owner["parameters"]:
                bindings.setdefault(parameter["name"], []).append({
                    "scope": group, "ownerId": owner[identity], "value": parameter["value"],
                    "unit": parameter["unit"], "sourceType": parameter["sourceType"],
                })
    return bindings


def _raw_review(spec):
    extensions = spec.get("extensions", {})
    namespace = extensions.get("simulation-data-lab", {}) if isinstance(extensions, dict) else {}
    return namespace.get("variableReview", MISSING) if isinstance(namespace, dict) else MISSING


def validate_variable_review(spec) -> dict[str, Any] | None:
    review = _raw_review(spec)
    if review is MISSING:
        return None  # Historical specs retain their original contract and hashes.
    _keys(review, {"schemaVersion", "scope", "variables", "interactions", "coverageChecks", "openQuestions"}, "variableReview")
    if type(review["schemaVersion"]) is not int or review["schemaVersion"] != 1:
        raise ValueError("variableReview.schemaVersion must be integer 1")
    _text(review["scope"], "variableReview.scope")
    bindings = parameter_bindings(spec)
    outcomes = {item["name"] for item in spec["outcomes"]}
    variables = _items(review["variables"], "variableReview.variables", minimum=1)
    ids, documented, reached = set(), set(), set()
    for variable in variables:
        _keys(variable, {
            "variableId", "label", "role", "unit", "treatment", "parameterNames", "affectsOutcomes",
            "mechanism", "evidence", "decisionImpact", "reason", "nextCheck",
        }, "variableReview.variable")
        identity = _text(variable["variableId"], "variableId")
        if not ID.fullmatch(identity) or identity in ids:
            raise ValueError("variableReview variable IDs must be unique lowercase hyphen-case IDs")
        ids.add(identity)
        for field in ("label", "unit", "mechanism", "evidence", "reason", "nextCheck"):
            _text(variable[field], f"{identity}.{field}")
        _text(variable["role"], f"{identity}.role", ROLES)
        _text(variable["treatment"], f"{identity}.treatment", TREATMENTS)
        _text(variable["decisionImpact"], f"{identity}.decisionImpact", IMPACTS)
        names = _references(variable["parameterNames"], set(bindings), f"{identity}.parameterNames")
        effects = _references(variable["affectsOutcomes"], outcomes, f"{identity}.affectsOutcomes")
        if variable["treatment"] in {"excluded", "unresolved"} and names:
            raise ValueError(f"{identity}: an excluded or unresolved variable cannot own implemented parameters")
        if documented.intersection(names):
            raise ValueError(f"{identity}: parameter ownership is duplicated; record dependencies as interactions")
        for name in names:
            if any(binding["unit"] != variable["unit"] for binding in bindings[name]):
                raise ValueError(f"{identity}: review unit differs from parameter {name}")
        documented.update(names)
        if variable["treatment"] in {"modeled", "fixed"}:
            reached.update(effects)
    if set(bindings) - documented:
        raise ValueError("variableReview leaves declared parameters undocumented: " + ", ".join(sorted(set(bindings)-documented)))
    if outcomes - reached:
        raise ValueError("variableReview lacks a represented path to outcomes: " + ", ".join(sorted(outcomes-reached)))

    by_id = {item["variableId"]: item for item in variables}
    interaction_ids = set()
    for interaction in _items(review["interactions"], "variableReview.interactions"):
        _keys(interaction, {"interactionId", "variableIds", "treatment", "decisionImpact", "mechanism", "reason", "nextCheck"}, "variableReview.interaction")
        identity = _text(interaction["interactionId"], "interactionId")
        if not ID.fullmatch(identity) or identity in interaction_ids:
            raise ValueError("variableReview interaction IDs must be unique lowercase hyphen-case IDs")
        interaction_ids.add(identity)
        participants = _references(interaction["variableIds"], ids, f"{identity}.variableIds", minimum=1)
        _text(interaction["treatment"], f"{identity}.treatment", TREATMENTS)
        _text(interaction["decisionImpact"], f"{identity}.decisionImpact", IMPACTS)
        for field in ("mechanism", "reason", "nextCheck"):
            _text(interaction[field], f"{identity}.{field}")
        if interaction["treatment"] in {"modeled", "fixed"} and any(
            by_id[item]["treatment"] in {"excluded", "unresolved"} for item in participants
        ):
            raise ValueError(f"{identity}: a represented interaction contains an omitted variable")

    checked = set()
    for check in _items(review["coverageChecks"], "variableReview.coverageChecks"):
        _keys(check, {"dimension", "status", "variableIds", "note"}, "variableReview.coverageCheck")
        dimension = _text(check["dimension"], "coverageCheck.dimension", DIMENSIONS)
        if dimension in checked:
            raise ValueError("variableReview repeats a review dimension")
        checked.add(dimension)
        _text(check["status"], "coverageCheck.status", {"reviewed", "not-applicable"})
        _text(check["note"], "coverageCheck.note")
        _references(check["variableIds"], ids, "coverageCheck.variableIds", minimum=1 if check["status"] == "reviewed" else 0)
    if checked != DIMENSIONS:
        raise ValueError("variableReview is missing review dimensions: " + ", ".join(sorted(DIMENSIONS-checked)))
    for question in _items(review["openQuestions"], "variableReview.openQuestions"):
        _text(question, "variableReview.openQuestion")
    return review


def variable_review_summary(spec):
    review = validate_variable_review(spec)
    base = {"exhaustiveness": "not-certified", "implementationCoverage": "declarations-only-not-code-proof"}
    if review is None:
        return {**base, "status": "not-recorded"}
    critical = lambda items, key: sorted(
        item[key] for item in items
        if item["treatment"] in {"excluded", "unresolved"} and item["decisionImpact"] in {"high", "unknown"}
    )
    variables = critical(review["variables"], "variableId")
    interactions = critical(review["interactions"], "interactionId")
    return {
        **base, "status": "limitations-required" if variables or interactions else "review-recorded",
        "candidateCount": len(review["variables"]), "criticalVariableIds": variables,
        "criticalInteractionIds": interactions, "documentedParameterNames": sorted(parameter_bindings(spec)),
    }


def review_row_count(spec):
    review = _raw_review(spec)
    return 0 if review is MISSING else len(review["variables"])


def _md(value):
    text = html.escape(str(value), quote=False).replace("\\", "\\\\")
    for token in ("|", "`", "*", "[", "]", "#"):
        text = text.replace(token, "\\" + token)
    return " ".join(text.splitlines())


def build_variable_review_files(spec):
    review = validate_variable_review(spec)
    if review is None:
        return {}
    summary = variable_review_summary(spec)
    bindings = parameter_bindings(spec)
    variables = sorted(review["variables"], key=lambda item: item["variableId"])
    rows = []
    for item in variables:
        rows.append({
            "experiment_id": spec["experimentId"], "source_type": "model-review-declaration",
            "variable_id": item["variableId"], "label": item["label"], "role": item["role"],
            "unit": item["unit"], "treatment": item["treatment"], "decision_impact": item["decisionImpact"],
            "affects_outcomes_json": json.dumps(item["affectsOutcomes"], ensure_ascii=False),
            "parameter_bindings_json": json.dumps({name: bindings[name] for name in item["parameterNames"]}, ensure_ascii=False, sort_keys=True),
            **{field: item[field] for field in ("mechanism", "evidence", "reason")}, "next_check": item["nextCheck"],
        })
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    lines = [
        "# Model variable review", "", _md(review["scope"]), "",
        "This is a frozen pre-simulation review of declared candidates, not a certificate that all possible variables were found.",
        "Implementation links, evidence, and impact assessments are declarations to verify, not measured sensitivity or code-coverage proof.",
        "Only mathematical simulations are permitted; missing evidence does not authorize executing the target system.", "",
        f"Review status: **{summary['status']}**. Statistical support under the model does not resolve omitted mechanisms.", "",
        "## Variables considered", "", "| Variable | Role | Treatment | Decision impact | Unit | Affected outcomes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in variables:
        lines.append("| " + " | ".join(_md(item[field]) for field in ("label", "role", "treatment", "decisionImpact", "unit")) + " | " + _md(", ".join(item["affectsOutcomes"]) or "Decision scope only") + " |")
    lines.extend(["", "## Decision-critical omissions", ""])
    for label, ids in (("Variables", summary["criticalVariableIds"]), ("Interactions", summary["criticalInteractionIds"])):
        lines.append(f"{label}: {_md(', '.join(ids) or 'none recorded (not proof of absence)')}.")
        lines.append("")
    lines.extend(["Do not present an unconditional recommendation while decision-critical omissions remain unresolved. A narrower conditional calculation can still be useful.", "", "## Variable explanations and verification plan", ""])
    for item in variables:
        lines.extend([f"### {_md(item['label'])} ({item['variableId']})", ""])
        for field, label in (("mechanism", "How it can affect the answer"), ("evidence", "Evidence or assumption"), ("reason", "Why this treatment"), ("nextCheck", "Next mathematical check or existing-evidence question")):
            lines.extend([f"{label}: {_md(item[field])}", ""])
        for name in item["parameterNames"]:
            detail = "; ".join(f"{b['scope']}/{b['ownerId']}: {json.dumps(b['value'], ensure_ascii=False)} {b['unit']} ({b['sourceType']})" for b in bindings[name])
            lines.extend([f"Declared values for {_md(name)}: {_md(detail)}.", ""])
    lines.extend(["## Interactions and feedback", ""])
    for item in review["interactions"]:
        lines.extend([f"### {item['interactionId']} ({item['treatment']}; {item['decisionImpact']} impact)", "", f"Variables: {_md(', '.join(item['variableIds']))}.", "", _md(item["mechanism"]), "", f"Treatment reason: {_md(item['reason'])}", "", f"Next check: {_md(item['nextCheck'])}", ""])
    lines.extend(["## Blind-spot review", ""])
    for check in review["coverageChecks"]:
        lines.extend([f"- {check['dimension']} ({check['status']}): {_md(check['note'])} Variables: {_md(', '.join(check['variableIds']) or 'not applicable')}."])
    lines.extend(["", "## Questions for the human reviewer", ""])
    lines.extend(f"- {_md(question)}" for question in review["openQuestions"])
    if not review["openQuestions"]:
        lines.append("No additional questions recorded; this does not establish completeness.")
    lines.extend(["", "## After the simulation", "", "Revisit this inventory against activation checks, sensitivity results, failed regions, and rival mechanisms. Report new gaps and any effect on the decision in analysis/model-review-followup.md. Keep this frozen review unchanged; a changed model or study needs a fresh bundle.", ""])
    return {"variable-inventory.csv": buffer.getvalue().encode("utf-8"), "model-review.md": "\n".join(lines).encode("utf-8")}
