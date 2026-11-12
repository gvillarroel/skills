#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise typed evidence/report integration without touching host accounts."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "skills/desktop-plugin-ui"
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/typed-report-checker-tests-20261025"
BASE = "https://modelcontextprotocol.io/extensions/apps/overview"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path: Path) -> dict[str, str]:
    return {str(item.relative_to(path)): digest(item) for item in path.rglob("*") if item.is_file()}


def common(identity: str, basis: str, claim: str, layer: str) -> dict:
    return {"id": identity, "claim": claim, "host": "Synthetic evidence study",
            "surface": "Study fixture", "version": "unknown", "layer": layer,
            "basis": basis}


def raw_records() -> list[dict]:
    return [
        {**common("policy-refusal", "execution", "The expected policy refusal was returned.", "policy protocol"),
         "action": "Request a form under the declining policy", "expected": "decline",
         "actual": "decline", "outcome": "pass"},
        {**common("source-declaration", "source-inspection", "The source handler declares a fullscreen request.", "static source inspection"),
         "source": "Inspected synthetic widget.ts handler; runtime was not executed"},
        {**common("documented-contract", "primary-documentation", "The primary contract describes MCP Apps.", "documentation"),
         "source": BASE},
        {**common("human-visibility", "user-report", "The user reported that the chart was visible.", "human report"),
         "reporter": "User", "reported_result": "The fresh chart is expanded and visible"},
        {**common("paint-not-run", "not-run", "Signed-in assistant paint was not exercised.", "assistant rendering"),
         "reason": "The user chose to continue without account sign-in"},
        {**common("conditional-renderer", "conditional", "A renderer depends on the available host bridge.", "deployment prerequisites"),
         "prerequisites": ["An actual renderer", "The negotiated host bridge"]},
        {**common("explicit-exclusion", "explicit-exclusion", "This synthetic contract excludes a device feature.", "explicit contract"),
         "source": "Synthetic contract section 4", "exclusion": "The named synthetic host excludes camera access"},
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="run-001")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", args.run_id):
        parser.error("Use a short filesystem-safe run ID")
    out = ARTIFACTS / args.run_id
    if out.exists():
        parser.error("Refusing to overwrite a retained test run; choose a fresh --run-id")
    out.mkdir(parents=True)
    bundle = out / "bundle"
    resources = [SOURCE / "SKILL.md", *(SOURCE / "references").glob("*.md"),
                 *(SOURCE / "scripts" / name for name in ("check_sources.py", "check_reports.py", "evidence_ledger.py"))]
    for source in resources:
        if not source.is_file():
            parser.error(f"Required integration resource is missing: {source.name}")
        target = bundle / source.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    baseline = snapshot(bundle)
    checker = bundle / "scripts/check_reports.py"
    ledger = bundle / "scripts/evidence_ledger.py"
    cases = []

    def record(name: str, passed: bool, **details) -> None:
        cases.append({"name": name, "passed": passed, **details})

    # Use the actual helper CLI, then independently assert the expected labels.
    generation = out / "helper-generation"
    generation.mkdir()
    source_input = generation / "facts.json"
    source_input.write_text(json.dumps({"records": raw_records()}, indent=2), encoding="utf-8")
    generated_json = generation / "ledger.json"
    generated_md = generation / "ledger.md"
    command = [sys.executable, str(ledger), "--input", str(source_input), "--output", str(generated_json),
               "--markdown", str(generated_md), "--fail-on-findings"]
    run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=20)
    try:
        response = json.loads(run.stdout)
        normalized = json.loads(generated_json.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        response = {}; normalized = {}
    expected_labels = ["observed-working", "documented", "documented", "untested", "untested", "conditional", "unsupported"]
    actual_labels = [row.get("evidence") for row in normalized.get("evidence_records", [])]
    expected_states = ["executed", "not-run", "not-run", "not-run", "not-run", "not-run", "not-run"]
    actual_states = [row.get("execution_state") for row in normalized.get("evidence_records", [])]
    record("actual-helper-cli-seven-bases", run.returncode == 0 and response.get("passed") is True
           and actual_labels == expected_labels and actual_states == expected_states
           and generated_md.is_file() and snapshot(bundle) == baseline,
           command=command, actual_labels=actual_labels, actual_states=actual_states,
           output=response, stderr=run.stderr)
    if not normalized.get("evidence_records"):
        result = {"passed": False, "case_count": len(cases), "cases": cases}
        (out / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2)); return 1

    def report(rows=None) -> dict:
        return {"evidence_records": deepcopy(normalized["evidence_records"] if rows is None else rows),
                "sources": [BASE], "host_acceptance_verified": False,
                "task_empirical_tests_performed": False}

    def check(name: str, files: dict[str, object], *, flags=(), passed=True, exit_code=0, count=None) -> dict:
        directory = out / name
        directory.mkdir()
        paths = []
        before = {}
        for filename, content in files.items():
            path = directory / filename
            text = content if isinstance(content, str) else json.dumps(content, indent=2)
            path.write_text(text, encoding="utf-8")
            paths.append(path); before[path] = path.read_bytes()
        command = [sys.executable, str(checker), *map(str, paths), *flags]
        run = subprocess.run(command, cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=20)
        errors = []
        try:
            data = json.loads(run.stdout)
        except ValueError:
            data = {}; errors.append("The checker did not return diagnostic JSON")
        if run.returncode != exit_code or data.get("passed") is not passed:
            errors.append(f"Unexpected exit/passed: {run.returncode}/{data.get('passed')}")
        if count is not None and data.get("checked_evidence_records") != count:
            errors.append(f"Wrong typed-record count: {data.get('checked_evidence_records')}")
        if not passed and not data.get("findings"):
            errors.append("Rejected input has no diagnostic finding")
        if "evidence_validation" not in data:
            errors.append("Missing explicit evidence validation mode")
        if snapshot(bundle) != baseline:
            errors.append("The copied runtime bundle changed")
        if any(path.read_bytes() != original for path, original in before.items()):
            errors.append("Checking unexpectedly mutated an input report")
        record(name, not errors, errors=errors, command=command, output=data, stderr=run.stderr)
        return data

    required = ("--require-evidence-records",)
    check("normalized-seven-bases", {"report.md": generated_md.read_text(encoding="utf-8"), "report.json": report()}, flags=required, count=7)
    check("raw-final-records-need-normalization", {"report.json": report(raw_records())}, flags=required, passed=False)
    check("actual-ledger-artifact", {"ledger.md": generated_md.read_text(encoding="utf-8"), "ledger.json": normalized}, flags=required, count=7)
    for field in ("evidence", "classification", "execution_state"):
        data = report(); data["evidence_records"][0].pop(field)
        check(f"missing-derived-{field}", {"report.json": data}, flags=required, passed=False)
    data = report(); data["evidence_records"][0].pop("evidence")
    check("optional-typed-final-still-needs-derived-fields", {"report.json": data}, passed=False)
    for field, value, index in (("evidence", "observed-failed", 4), ("classification", "observed-working", 1),
                                ("execution_state", "executed", 3), ("evidence", "observed-working", 1)):
        data = report(); data["evidence_records"][index][field] = value
        check(f"tampered-{field}-{index}", {"report.json": data}, flags=required, passed=False)
    data = report(); data["evidence_records"][1]["actual"] = "A runtime request completed"
    check("source-cannot-carry-runtime-result", {"report.json": data}, flags=required, passed=False)
    data = report(); data["evidence_records"][4]["outcome"] = "fail"
    check("not-run-cannot-carry-failure", {"report.json": data}, flags=required, passed=False)
    data = report(); data["evidence_records"][0].pop("outcome")
    check("execution-needs-outcome", {"report.json": data}, flags=required, passed=False)
    for name, value in (("empty", []), ("object", {}), ("null", None), ("string", "observed-working")):
        check(f"invalid-container-{name}", {"report.json": {"evidence_records": value}}, flags=required, passed=False)
    check("missing-typed-records", {"report.json": {"sources": [BASE]}}, flags=required, passed=False)
    check("top-level-array-cannot-certify-typed", {"report.json": []}, flags=required, passed=False)
    check("markdown-only-cannot-certify-typed", {"report.md": generated_md.read_text(encoding="utf-8")}, flags=required, passed=False)
    check("every-json-needs-typed-records", {"valid.json": report(), "missing.json": {}}, flags=required, passed=False)
    check("two-json-ledgers-are-scoped", {"first.json": report(), "second.json": report()}, flags=required, count=14)
    data = report(); data["findings"] = [{"evidence_ids": ["policy-refusal", "paint-not-run"], "nested": {"evidence_ids": ["source-declaration"]}}]
    check("nested-valid-evidence-links", {"report.json": data}, flags=required, count=7)
    data = report(); data["findings"] = [{"evidence_ids": []}]
    check("empty-optional-reference-array", {"report.json": data}, flags=required, count=7)
    for name, value in (("unknown", ["does-not-exist"]), ("blank", [""]), ("whitespace", [" "]),
                        ("number", [7]), ("nonarray", "policy-refusal"), ("null", None)):
        data = report(); data["findings"] = [{"nested": {"evidence_ids": value}}]
        check(f"invalid-evidence-link-{name}", {"report.json": data}, flags=required, passed=False)
    data = report(); data["evidence_records"].append(deepcopy(data["evidence_records"][0]))
    check("duplicate-evidence-id", {"report.json": data}, flags=required, passed=False)
    duplicate_basis = json.dumps(report()).replace('"basis": "source-inspection"',
                                                  '"basis": "execution", "basis": "source-inspection"', 1)
    check("duplicate-basis-key-rejected", {"report.json": duplicate_basis}, flags=required, passed=False)
    duplicate_label = json.dumps(report()).replace('"evidence": "observed-working"',
                                                  '"evidence": "observed-failed", "evidence": "observed-working"', 1)
    check("duplicate-label-key-rejected", {"report.json": duplicate_label}, flags=required, passed=False)
    data = report(); data["evidence_records"][0] = None
    check("nonobject-evidence-record", {"report.json": data}, flags=required, passed=False)
    failure = {**common("bind-failed", "execution", "The attempted tab binding failed.", "controller binding"),
               "action": "Bind the discovered tab", "expected": "A bound tab", "actual": "Tab not found", "outcome": "fail",
               "evidence": "observed-failed", "classification": "observed-failed", "execution_state": "executed"}
    check("genuine-execution-failure-is-valid", {"report.json": report([failure])}, flags=required, count=1)
    check("expected-refusal-is-working", {"report.json": report([normalized["evidence_records"][0]])}, flags=required, count=1)
    data = report(); data["evidence_records"][4]["evidence"] = "observed-failed"
    check("ci-rejects-misclassification", {"report.json": data}, flags=(*required, "--fail-on-findings"), passed=False, exit_code=1)
    check("legacy-label-check-is-preserved", {"report.json": {"historical_observations": [{"evidence": "observed-working; actual historical engine result"}]}}, count=0)
    check("optional-typed-ledger-still-checks-tamper", {"report.json": data}, passed=False)

    result = {"passed": all(row["passed"] for row in cases), "case_count": len(cases),
              "passed_count": sum(row["passed"] for row in cases),
              "source_sha256": {name: digest(SOURCE / "scripts" / name) for name in ("check_reports.py", "evidence_ledger.py")},
              "bundle_unchanged": snapshot(bundle) == baseline,
              "scope": "Copied-runtime CLI integration; no account, UI, provider or network operation.", "cases": cases}
    (out / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, indent=2))
    if not result["passed"]:
        print(json.dumps([{"name": row["name"], "errors": row.get("errors", [])} for row in cases if not row["passed"]], indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
