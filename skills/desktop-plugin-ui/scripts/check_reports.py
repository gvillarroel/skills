#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check advisory reports and explicitly repair exact citation URLs."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


def load_sources():
    """Load only the sibling helper; leave the read-only bundle unchanged."""
    spec = importlib.util.spec_from_file_location("desktop_plugin_ui_sources", Path(__file__).resolve().with_name("check_sources.py"))
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load bundled check_sources.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


SOURCES = load_sources()
EVIDENCE = re.compile(r"\bobserved-(?:working|failed)\b")


def parse_json(text: str):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON object key: {key}")
            result[key] = value
        return result
    return json.loads(text.removeprefix("\ufeff"), object_pairs_hook=unique_keys)


def load_evidence_ledger():
    """Load the optional typed validator without writing into the bundle."""
    location = Path(__file__).resolve().with_name("evidence_ledger.py")
    spec = importlib.util.spec_from_file_location("desktop_plugin_ui_evidence", location)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load bundled evidence_ledger.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def inspect_report(path: Path, text: str, data: object, allowed: set[str], *, require_evidence_records: bool = False):
    findings = []
    checked = 0
    # JSON quotes/backslashes are serialization syntax, not URL characters.
    # Decode once; scanning both raw JSON and decoded values invents URLs
    # such as 'schema.json\\' from quoted command examples.
    urls = SOURCES.extract_urls(text) if data is None else set()
    pending = [data]
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            urls.update(SOURCES.extract_urls(value))
        elif isinstance(value, dict):
            pending.extend(value)
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    for url in sorted(urls):
        if not SOURCES.source_family(url):
            continue
        checked += 1
        if url in allowed:
            continue
        parsed = urlsplit(url)
        candidates = sorted(candidate for candidate in allowed
                            if SOURCES.source_family(candidate) == SOURCES.source_family(url)
                            and (urlsplit(candidate).path, urlsplit(candidate).query, urlsplit(candidate).fragment)
                            == (parsed.path, parsed.query, parsed.fragment))
        findings.append({"path": str(path), "url": url, "error": "URL must equal a bundled or explicitly verified primary source", "exact_candidates": candidates})
    rows = data.get("historical_observations", []) if isinstance(data, dict) else []
    if not isinstance(rows, list):
        findings.append({"path": str(path), "field": "historical_observations", "error": "Expected an array"})
        rows = []
    for index, row in enumerate(rows):
        evidence = row.get("evidence") if isinstance(row, dict) else None
        if not isinstance(evidence, str) or not EVIDENCE.search(evidence):
            findings.append({"path": str(path), "field": f"historical_observations[{index}].evidence", "error": "Evidence must literally include observed-working or observed-failed; labels elsewhere do not satisfy this field"})
    typed_count = 0
    validation = "no-evidence-records"
    if isinstance(data, dict) and "evidence_records" in data:
        records = data["evidence_records"]
        typed_count = len(records) if isinstance(records, list) else 0
        validation = "typed-declared-basis"
        if isinstance(records, list):
            for index, record in enumerate(records):
                if isinstance(record, dict):
                    for field in ("evidence", "classification", "execution_state"):
                        if field not in record:
                            findings.append({"path": str(path), "field": f"evidence_records[{index}].{field}", "error": "Final reports require all derived fields from evidence_ledger.py; raw facts are helper inputs only"})
        try:
            result = load_evidence_ledger().classify_records({"evidence_records": records})
            for finding in result["findings"]:
                findings.append({**finding, "path": str(path)})
        except (OSError, ValueError, TypeError, KeyError) as error:
            findings.append({"path": str(path), "field": "evidence_records", "error": f"Typed evidence validation failed: {error}"})
        identifiers = {record.get("id") for record in records if isinstance(record, dict) and isinstance(record.get("id"), str)} if isinstance(records, list) else set()
        pending = [(data, "$")]
        while pending:
            value, location = pending.pop()
            if isinstance(value, dict):
                if "evidence_ids" in value:
                    references = value["evidence_ids"]
                    if not isinstance(references, list) or any(not isinstance(item, str) or not item.strip() or item not in identifiers for item in references):
                        findings.append({"path": str(path), "field": f"{location}.evidence_ids", "error": "Evidence references must be an array of existing typed record IDs"})
                pending.extend((item, f"{location}.{key}") for key, item in value.items())
            elif isinstance(value, list):
                pending.extend((item, f"{location}[{index}]") for index, item in enumerate(value))
    elif require_evidence_records:
        findings.append({"path": str(path), "field": "evidence_records", "error": "A nonempty typed evidence_records array is required; build it with evidence_ledger.py"})
    elif isinstance(data, dict) and "historical_observations" in data:
        validation = "legacy-labels-only"
    return findings, checked, len(rows), typed_count, validation


def replace_urls(text: str, replacements: dict[str, str]):
    """Replace complete URL tokens simultaneously, preserving punctuation."""
    counts = {old: 0 for old in replacements}

    def replace(match):
        raw = match.group(0)
        url = raw.rstrip(".,;:)]")
        if url not in replacements:
            return raw
        counts[url] += 1
        return replacements[url] + raw[len(url):]

    return SOURCES.URL.sub(replace, text), counts


def atomic_write(path: Path, text: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, nargs="+")
    parser.add_argument("--replace-url", nargs=2, action="append", default=[], metavar=("OLD", "NEW"), help="Replace every exact OLD URL token with an exact bundled primary URL; repeatable")
    parser.add_argument("--allow-url", action="append", default=[], help="Additional independently fetched and verified primary URL for validation")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 1 on findings; default diagnostics exit 0")
    parser.add_argument("--require-evidence-records", action="store_true", help="Require typed evidence records in each JSON report and at least one JSON companion; Markdown still receives URL checks")
    args = parser.parse_args()
    bundled = SOURCES.catalog()
    allowed = set(bundled)
    findings = []
    replacements = {}
    for url in args.allow_url:
        if not SOURCES.primary_family(url):
            findings.append({"url": url, "error": "--allow-url requires an HTTPS URL on a recognized exact primary host or GitHub owner"})
        else:
            allowed.add(url)
    for old, new in args.replace_url:
        if SOURCES.extract_urls(old) != {old}:
            findings.append({"url": old, "error": "Replacement OLD must be one complete literal URL"})
        elif new not in bundled or not SOURCES.primary_family(new):
            findings.append({"url": new, "error": "Replacement NEW must equal an exact bundled primary-source URL"})
        elif old in replacements and replacements[old] != new:
            findings.append({"url": old, "error": "Conflicting replacement targets for the same OLD URL"})
        else:
            replacements[old] = new
    plans = []
    seen = set()
    bundle = SOURCES.BUNDLE.resolve()
    for report in args.reports:
        try:
            resolved = report.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if args.replace_url and any(candidate.is_relative_to(bundle) for candidate in (resolved, Path(os.path.abspath(report)))):
                raise ValueError("Refusing to repair any path inside this read-only skill bundle")
            if not resolved.is_file():
                raise ValueError("Report must be an existing regular file")
            with resolved.open(encoding="utf-8", newline="") as handle:
                original = handle.read()
            is_json = report.suffix.lower() == ".json" or resolved.suffix.lower() == ".json"
            if is_json:
                parse_json(original)
            updated, counts = replace_urls(original, replacements)
            data = parse_json(updated) if is_json else None
            plans.append((resolved, original, updated, data, counts, is_json))
        except (OSError, UnicodeError, ValueError) as error:
            findings.append({"path": str(report), "error": str(error)})
    # Preflight failures prevent every planned write. Source/evidence findings
    # are diagnosed afterward and never cause implicit content repairs.
    if args.require_evidence_records and not any(plan[-1] for plan in plans):
        findings.append({"field": "evidence_records", "error": "Typed checking requires a JSON report companion; Markdown alone cannot certify evidence"})
    repair_blocked = bool(findings)
    changes = []
    checked_sources = checked_rows = checked_typed = 0
    validation_modes = set()
    for path, original, updated, data, counts, is_json in plans:
        if args.replace_url and not repair_blocked and updated != original:
            try:
                atomic_write(path, updated)
                changes.extend({"path": str(path), "old": old, "new": replacements[old], "occurrences": count} for old, count in counts.items() if count)
            except OSError as error:
                findings.append({"path": str(path), "error": f"Atomic repair failed: {error}"})
                updated = original
                data = parse_json(original) if is_json else None
        elif repair_blocked:
            updated = original
            data = parse_json(original) if is_json else None
        report_findings, source_count, row_count, typed_count, validation = inspect_report(path, updated, data, allowed, require_evidence_records=args.require_evidence_records and is_json)
        findings.extend(report_findings)
        checked_sources += source_count
        checked_rows += row_count
        checked_typed += typed_count
        if is_json:
            validation_modes.add(validation)
    print(json.dumps({"passed": not findings, "checked_official_urls": checked_sources, "checked_historical_observations": checked_rows, "checked_evidence_records": checked_typed, "evidence_validation": sorted(validation_modes), "replacements": changes, "findings": findings, "limitations": "Declared-basis validation cannot prove factual truth, omitted-claim coverage, artifact authenticity or host paint. Legacy records receive label checks only."}, indent=2))
    return 1 if findings and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
