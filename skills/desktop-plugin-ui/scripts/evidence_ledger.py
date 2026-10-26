#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Classify explicitly scoped evidence facts without inferring execution."""

from __future__ import annotations

import argparse
from copy import deepcopy
import html
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


BUNDLE = Path(__file__).resolve().parents[1]
COMMON = {"id", "claim", "host", "surface", "version", "layer", "basis"}
DERIVED = {"evidence", "classification", "execution_state"}
RESERVED_REPORT_FIELDS = {"records", "report", "passed", "schema_version", "evidence_records", "evidence_validation"}
BASIS_FIELDS = {
    "execution": {"action", "expected", "actual", "outcome"},
    "source-inspection": {"source"},
    "primary-documentation": {"source"},
    "user-report": {"reporter", "reported_result"},
    "not-run": {"reason"},
    "conditional": {"prerequisites"},
    "explicit-exclusion": {"source", "exclusion"},
}
LABELS = {
    "source-inspection": "documented",
    "primary-documentation": "documented",
    "user-report": "untested",
    "not-run": "untested",
    "conditional": "conditional",
    "explicit-exclusion": "unsupported",
}


class LedgerFinding(ValueError):
    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.finding = {"code": code, "message": message, **details}


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise LedgerFinding("invalid_arguments", message)


def result(findings: list[dict[str, Any]], records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"passed": not findings, "schema_version": 1,
            "evidence_records": records if not findings and records is not None else [],
            "findings": findings}


def classify_records(data: Any) -> dict[str, Any]:
    """Validate declared facts and derive canonical labels deterministically.

    Accept ``records`` as raw input or ``evidence_records`` for checking an
    existing normalized ledger. Do not evaluate prose truth, source contents,
    expected/actual semantic equivalence, or claims outside these records.
    ``outcome`` is the caller's declared result of an actually executed action.
    """
    if not isinstance(data, dict):
        return result([{"code": "invalid_input", "field": "$", "message": "Expected a JSON object."}])
    if "schema_version" in data and (type(data["schema_version"]) is not int or data["schema_version"] != 1):
        return result([{"code": "invalid_schema_version", "field": "schema_version", "message": "Only schema_version 1 is supported."}])
    containers = [key for key in ("records", "evidence_records") if key in data]
    if len(containers) != 1:
        return result([{"code": "invalid_container", "field": "$", "message": "Provide exactly one records or evidence_records array."}])
    key = containers[0]
    raw = data[key]
    if not isinstance(raw, list) or not raw:
        return result([{"code": "invalid_records", "field": key, "message": "Expected a nonempty array of evidence facts."}])
    findings: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    for index, row in enumerate(raw):
        location = f"{key}[{index}]"
        before = len(findings)

        def add(code: str, message: str, field: str = "") -> None:
            findings.append({"code": code, "field": f"{location}.{field}" if field else location, "message": message})

        if not isinstance(row, dict):
            add("invalid_record", "Expected an object containing one scoped claim.")
            continue
        if any(not isinstance(field, str) for field in row):
            add("invalid_field_name", "Record fields must be string JSON object keys.")
            continue
        for field in sorted(COMMON):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                add("missing_context", "Expected a nonempty string; use unknown explicitly for an unrecorded version.", field)
        identity = row.get("id")
        if isinstance(identity, str) and identity.strip():
            if identity != identity.strip():
                add("invalid_id", "An ID must not have surrounding whitespace.", "id")
            elif identity in identifiers:
                add("duplicate_id", "Each evidence ID must be unique.", "id")
            identifiers.add(identity)
        basis = row.get("basis")
        if not isinstance(basis, str) or basis not in BASIS_FIELDS:
            add("invalid_basis", "Use one supported evidence basis.", "basis")
            continue
        required = BASIS_FIELDS[basis]
        for field in sorted(set(row) - COMMON - DERIVED - required):
            add("unexpected_field", "This field does not belong to the selected basis; split distinct claims or execution into separate records.", field)
        for field in sorted(required):
            value = row.get(field)
            if field == "prerequisites":
                if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
                    add("invalid_prerequisites", "Expected a nonempty array of nonempty prerequisite strings.", field)
            elif not isinstance(value, str) or not value.strip():
                add("missing_basis_field", "Expected a nonempty string for this basis.", field)
        if basis == "execution" and row.get("outcome") not in ("pass", "fail"):
            add("invalid_outcome", "An executed action needs the explicit string outcome pass or fail.", "outcome")
        if len(findings) != before:
            continue
        label = ("observed-working" if row["outcome"] == "pass" else "observed-failed") if basis == "execution" else LABELS[basis]
        state = "executed" if basis == "execution" else "not-run"
        expected = {"evidence": label, "classification": label, "execution_state": state}
        for field, value in expected.items():
            if field in row and row[field] != value:
                add("classification_mismatch", f"The declared basis derives {field}={value}; remove or correct the conflicting derived field.", field)
        if len(findings) == before:
            normalized.append({**deepcopy(row), **expected})
    return result(findings, normalized)


def markdown_cell(value: str) -> str:
    # Preserve literal source URLs for the exact-source checker. Escape table
    # and Markdown syntax in surrounding text without rewriting URL paths or
    # queries (for example underscores and ampersands).
    parts = re.split(r"(https?://[^\s<>\"'|`]+)", value)
    for index in range(0, len(parts), 2):
        text = html.escape(parts[index], quote=False).replace("\\", "\\\\")
        for character in ("|", "`", "[", "]", "*", "_"):
            text = text.replace(character, "\\" + character)
        parts[index] = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    return "".join(parts)


def render_markdown(data: dict[str, Any]) -> str:
    """Render only normalized, checked facts; never classify prose again."""
    checked = classify_records({"evidence_records": data.get("evidence_records")})
    if not checked["passed"]:
        raise LedgerFinding("invalid_markdown_input", "Markdown requires a valid normalized ledger.")
    lines = ["# Evidence ledger", "", "Classification checks declared structure, not the truth of the underlying facts.", "",
             "| ID | Claim | Basis | Scope | Evidence | Execution / result |",
             "| --- | --- | --- | --- | --- | --- |"]
    for row in checked["evidence_records"]:
        scope = "; ".join(f"{field}: {row[field]}" for field in ("host", "surface", "version", "layer"))
        details = [row["execution_state"]]
        for field in ("action", "expected", "actual", "outcome", "source", "reporter", "reported_result", "reason", "exclusion"):
            if field in row:
                details.append(f"{field}: {row[field]}")
        if "prerequisites" in row:
            details.append("prerequisites: " + "; ".join(row["prerequisites"]))
        cells = (row["id"], row["claim"], row["basis"], scope, row["evidence"], "; ".join(details))
        lines.append("| " + " | ".join(markdown_cell(value) for value in cells) + " |")
    return "\n".join(lines) + "\n"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key, value in pairs:
        if key in data:
            raise LedgerFinding("duplicate_json_key", f"Duplicate JSON object key: {key}")
        data[key] = value
    return data


def output_path(path: Path, input_path: Path, previous: list[Path]) -> Path:
    resolved = path.resolve()
    lexical = Path(os.path.abspath(path))
    if resolved.is_relative_to(BUNDLE) or lexical.is_relative_to(BUNDLE):
        raise LedgerFinding("bundle_write_refused", "Outputs must stay outside the read-only skill bundle.", path=str(path))
    if resolved == input_path.resolve():
        raise LedgerFinding("input_overwrite_refused", "Keep the source evidence input separate from generated outputs.", path=str(path))
    if resolved in previous:
        raise LedgerFinding("duplicate_output", "JSON and Markdown outputs must use different paths.", path=str(path))
    if resolved.exists() and not resolved.is_file():
        raise LedgerFinding("invalid_output", "An output must be a regular file path.", path=str(path))
    return resolved


def write_outputs(plans: list[tuple[Path, str]]) -> None:
    """Stage every output before committing; create temporary files locally."""
    staged: list[tuple[Path, Path]] = []
    try:
        for target, text in plans:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=target.parent,
                                             prefix=f".{target.name}.", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                staged.append((temporary, target))
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _target in staged:
            temporary.unlink(missing_ok=True)


def report_output(data: dict[str, Any], checked: dict[str, Any]) -> dict[str, Any]:
    """Attach caller-owned report fields without overwriting classifications.

    Domain ``findings`` may belong to the report; classifier diagnostics stay
    separate under a protected ``evidence_validation`` object. CLI stdout
    continues to use the original normalized diagnostic shape.
    """
    if "report" not in data:
        return checked
    metadata = data["report"]
    if not isinstance(metadata, dict):
        raise LedgerFinding("invalid_report", "Optional report metadata must be an object.", field="report")
    collisions = sorted(set(metadata) & RESERVED_REPORT_FIELDS)
    if collisions:
        raise LedgerFinding("reserved_report_field", "Report metadata cannot replace classifier-owned fields.", fields=collisions)
    try:
        json.dumps(metadata, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise LedgerFinding("invalid_report_value", "Report metadata must contain finite JSON values.", field="report") from error
    return {**deepcopy(metadata), "evidence_records": deepcopy(checked["evidence_records"]),
            "evidence_validation": {"passed": True, "schema_version": 1, "findings": []}}


def main() -> int:
    parser = Parser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON facts containing records or evidence_records and optional report metadata")
    parser.add_argument("--output", required=True, type=Path, help="Normalized JSON ledger or report outside the skill")
    parser.add_argument("--markdown", type=Path, help="Optional Markdown table rendered from the same normalized records")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 1 for invalid data or paths; default diagnostics exit 0")
    try:
        args = parser.parse_args()
    except LedgerFinding as error:
        print(json.dumps(result([error.finding]), indent=2))
        return 2
    try:
        with args.input.open(encoding="utf-8-sig") as handle:
            data = json.load(handle, object_pairs_hook=reject_duplicate_keys)
        checked = classify_records(data)
        if checked["passed"]:
            document = report_output(data, checked)
            outputs: list[Path] = []
            json_path = output_path(args.output, args.input, outputs)
            outputs.append(json_path)
            markdown_path = output_path(args.markdown, args.input, outputs) if args.markdown is not None else None
            plans = [(json_path, json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n")]
            if markdown_path is not None:
                plans.append((markdown_path, render_markdown(checked)))
            write_outputs(plans)
    except LedgerFinding as error:
        checked = result([error.finding])
    except (OSError, UnicodeError, ValueError) as error:
        checked = result([{"code": "input_or_output_error", "message": str(error)}])
    # ASCII-safe JSON keeps stdout portable on Windows pipes with legacy
    # encodings, while the explicit UTF-8 artifact preserves original text.
    print(json.dumps(checked, indent=2))
    return 1 if not checked["passed"] and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
