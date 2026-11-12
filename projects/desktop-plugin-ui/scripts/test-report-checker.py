#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently exercise exact report repair and historical evidence checks."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "skills/desktop-plugin-ui"
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/report-checker-tests"
BUNDLE = ARTIFACTS / "bundle"
CHECKER = BUNDLE / "scripts/check_reports.py"
BASE = "https://modelcontextprotocol.io/extensions/apps/overview"
WRONG = BASE.replace(".io", ".org")
ANCHOR = "https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#downloadFile"
WRONG_ANCHOR = ANCHOR.replace(".io", ".org")
EXTRA = "https://learn.microsoft.com/en-us/visualstudio/extensibility/visual-studio-extensibility-overview"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload():
    return {str(path.relative_to(BUNDLE)): digest(path) for path in BUNDLE.rglob("*") if path.is_file()}


def report(url=BASE, evidence="observed-working; historical engine scope"):
    return {"sources": [url], "historical_observations": [{"result": "observed-working", "evidence": evidence}]}


def main():
    global ARTIFACTS, BUNDLE, CHECKER
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="report-checker-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
    args = parser.parse_args()
    ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts" / args.run_id
    if not ARTIFACTS.resolve().is_relative_to(ROOT / "projects/desktop-plugin-ui/artifacts"):
        parser.error("The run ID must resolve inside the owning project's artifacts")
    if ARTIFACTS.exists():
        parser.error("Choose a fresh run ID; retained evidence is not overwritten")
    BUNDLE = ARTIFACTS / "bundle"
    CHECKER = BUNDLE / "scripts/check_reports.py"
    ARTIFACTS.mkdir(parents=True)
    for source in [SOURCE / "SKILL.md", SOURCE / "scripts/check_sources.py", SOURCE / "scripts/check_reports.py", *(SOURCE / "references").glob("*.md")]:
        target = BUNDLE / source.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    hardlink_source = BUNDLE / "references/hardlink-probe.md"
    hardlink_source.write_text(WRONG, encoding="utf-8")
    baseline = payload()
    cases = []

    def run(name, contents, *, flags=(), passed=True, expected_exit=0, field=None, candidate=None, expected=None, count=None, extra_files=None):
        directory = ARTIFACTS / name
        directory.mkdir(exist_ok=True)
        files = []
        before = {}
        for filename, content in contents.items():
            path = directory / filename
            value = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            path.write_text(value, encoding="utf-8", newline="")
            files.append(path)
            before[filename] = path.read_bytes()
        for filename, value in (extra_files or {}).items():
            (directory / filename).write_text(value, encoding="utf-8")
        command = [sys.executable, str(CHECKER), *map(str, files), *flags]
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=20)
        errors = []
        try:
            decoded = json.loads(result.stdout)
        except ValueError:
            decoded = {}
            errors.append("No diagnostic JSON")
        if result.returncode != expected_exit or decoded.get("passed") is not passed:
            errors.append(f"Unexpected exit/passed: {result.returncode}, {decoded.get('passed')}")
        if field and not any(finding.get("field") == field for finding in decoded.get("findings", [])):
            errors.append("Missing exact evidence-field finding")
        if candidate and not any(candidate in finding.get("exact_candidates", []) for finding in decoded.get("findings", [])):
            errors.append("Missing exact allowed candidate")
        if count is not None and sum(row["occurrences"] for row in decoded.get("replacements", [])) != count:
            errors.append("Wrong all-occurrence repair count")
        for filename, original in before.items():
            actual = (directory / filename).read_bytes()
            wanted = expected.get(filename) if expected else None
            if wanted is None and actual != original:
                errors.append(f"Unrequested content mutation: {filename}")
            elif wanted is not None and actual.decode("utf-8") != wanted:
                errors.append(f"Unexpected repaired content: {filename}")
            if filename.endswith(".json") and wanted is not None:
                json.loads(actual)
        if payload() != baseline:
            errors.append("Copied skill payload changed, including bytecode")
        cases.append({"name": name, "passed": not errors, "errors": errors, "command": command, "output": decoded, "stderr": result.stderr})

    run("clean-markdown", {"report.md": f"[Source]({BASE})"})
    run("clean-evidence-field", {"report.json": report()})
    quoted = report(); quoted["command"] = f'validate --schema "{BASE}"'
    run("json-command-quotes-are-serialization-not-url", {"report.json": quoted})
    quoted_bad = report(); quoted_bad["command"] = f'validate --schema "{WRONG}"'
    run("json-quoted-command-source-still-checked", {"report.json": quoted_bad}, passed=False, candidate=BASE)
    keyed = report(); keyed[BASE] = {"url": ANCHOR}
    run("json-url-key-and-value-remain-checked", {"report.json": keyed})
    trailing = report(); trailing["sources"] = [BASE + "\\"]
    run("json-literal-backslash-is-not-stripped", {"report.json": trailing}, passed=False)
    duplicate = '{"sources":' + json.dumps([BASE]) + ',"sources":' + json.dumps([WRONG]) + '}'
    run("json-duplicate-keys-remain-rejected", {"report.json": duplicate}, passed=False)
    run("source-diagnostic-only", {"report.md": WRONG}, passed=False, candidate=BASE)
    escaped_good = json.dumps(report()).replace("https://", "https:\\/\\/")
    escaped_bad = json.dumps(report(WRONG)).replace("https://", "https:\\/\\/")
    run("escaped-json-citation-passes", {"report.json": escaped_good})
    run("escaped-json-source-is-checked", {"report.json": escaped_bad}, passed=False, candidate=BASE)
    run("escaped-json-is-not-literal-repair", {"report.json": escaped_bad}, flags=["--replace-url", WRONG, BASE], passed=False, candidate=BASE, count=0)
    run("result-label-is-not-evidence", {"report.json": report(evidence="Historical result only")}, passed=False, field="historical_observations[0].evidence")
    run("missing-evidence", {"report.json": {"historical_observations": [{"result": "observed-working"}]}}, passed=False, field="historical_observations[0].evidence")
    run("nonstring-evidence", {"report.json": report(evidence=["observed-working"])}, passed=False, field="historical_observations[0].evidence")
    run("noncanonical-label-case", {"report.json": report(evidence="Observed-working")}, passed=False, field="historical_observations[0].evidence")
    run("history-must-be-array", {"report.json": {"historical_observations": {}}}, passed=False, field="historical_observations")
    run("ci-evidence-failure", {"report.json": report(evidence="No label")}, flags=["--fail-on-findings"], passed=False, expected_exit=1)
    markdown = f"[First]({WRONG}).\n{WRONG}\n`{WRONG}`\n"
    run("duplicate-markdown-repair", {"report.md": markdown}, flags=["--replace-url", WRONG, BASE], expected={"report.md": markdown.replace(WRONG, BASE)}, count=3)
    crlf = f"First: {WRONG}\r\nSecond: {WRONG}\r\n"
    run("repair-preserves-crlf", {"report.md": crlf}, flags=["--replace-url", WRONG, BASE], expected={"report.md": crlf.replace(WRONG, BASE)}, count=2)
    bom_json = "\ufeff" + (json.dumps(report(WRONG), indent=2) + "\n").replace("\n", "\r\n")
    bom_md = "\ufeff" + f"Source: {WRONG}\r\n"
    run("repair-preserves-bom-crlf", {"report.json": bom_json, "report.md": bom_md}, flags=["--replace-url", WRONG, BASE], expected={"report.json": bom_json.replace(WRONG, BASE), "report.md": bom_md.replace(WRONG, BASE)}, count=2)
    data = report(WRONG); data["sources"] = [WRONG, WRONG]; data["note"] = "Café " + WRONG
    original = json.dumps(data, ensure_ascii=False)
    run("duplicate-json-repair", {"report.json": original}, flags=["--replace-url", WRONG, BASE], expected={"report.json": original.replace(WRONG, BASE)}, count=3)
    both = WRONG + "\n" + WRONG_ANCHOR + "\n" + WRONG
    run("repeatable-explicit-repairs", {"report.md": both}, flags=["--replace-url", WRONG, BASE, "--replace-url", WRONG_ANCHOR, ANCHOR], expected={"report.md": both.replace(WRONG, BASE).replace(WRONG_ANCHOR, ANCHOR)}, count=3)
    run("simultaneous-no-cascade", {"report.md": WRONG + "\n" + BASE}, flags=["--replace-url", WRONG, BASE, "--replace-url", BASE, ANCHOR], expected={"report.md": BASE + "\n" + ANCHOR}, count=2)
    longer = WRONG + "#unverified"
    run("url-prefix-is-not-exact", {"report.md": WRONG + "\n" + longer}, flags=["--replace-url", WRONG, BASE], passed=False, expected={"report.md": BASE + "\n" + longer}, count=1)
    run("invalid-unlisted-target", {"report.md": WRONG}, flags=["--replace-url", WRONG, "https://modelcontextprotocol.io/unlisted"], passed=False, count=0)
    run("invalid-spoof-target", {"report.json": report(WRONG)}, flags=["--replace-url", WRONG, WRONG], passed=False, count=0)
    run("invalid-old-is-not-url", {"report.md": WRONG}, flags=["--replace-url", "replace words", BASE], passed=False, count=0)
    run("conflicting-targets", {"report.md": WRONG}, flags=["--replace-url", WRONG, BASE, "--replace-url", WRONG, ANCHOR], passed=False, count=0)
    run("invalid-json-unmodified", {"report.json": '{"source":"' + WRONG + '",}'}, flags=["--replace-url", WRONG, BASE], passed=False, count=0)
    run("batch-preflight-no-partial-repair", {"good.json": report(WRONG), "bad.json": "{broken}"}, flags=["--replace-url", WRONG, BASE], passed=False, count=0)
    unlabeled = json.dumps(report(WRONG, "Historical facts only"))
    run("repair-does-not-invent-evidence", {"report.json": unlabeled}, flags=["--replace-url", WRONG, BASE], passed=False, field="historical_observations[0].evidence", expected={"report.json": unlabeled.replace(WRONG, BASE)}, count=1)
    run("allow-verified-source", {"report.md": EXTRA}, flags=["--allow-url", EXTRA])
    run("reject-spoof-allow", {"report.md": BASE}, flags=["--allow-url", "https://learn.microsoft.com.attacker.invalid/page"], passed=False)
    run("allow-is-not-repair-catalog", {"report.md": WRONG}, flags=["--allow-url", EXTRA, "--replace-url", WRONG, EXTRA], passed=False, count=0)
    run("safe-sibling-import", {"report.json": report()}, extra_files={"check_sources.py": "raise RuntimeError('Wrong CWD import executed')\n"})

    for name, target in (("bundle-write-refused", BUNDLE / "SKILL.md"), ("resolved-alias-refused", ARTIFACTS / "bundle-alias.md")):
        try:
            if name == "resolved-alias-refused":
                target.unlink(missing_ok=True)
                target.symlink_to(BUNDLE / "SKILL.md")
            result = subprocess.run([sys.executable, str(CHECKER), str(target), "--replace-url", WRONG, BASE], capture_output=True, text=True, encoding="utf-8", timeout=20)
            decoded = json.loads(result.stdout)
            passed = result.returncode == 0 and not decoded["passed"] and any("read-only skill bundle" in finding["error"] for finding in decoded["findings"]) and payload() == baseline
            cases.append({"name": name, "passed": passed, "output": decoded})
        except OSError as error:
            cases.append({"name": name, "passed": name == "resolved-alias-refused", "skipped": str(error)})
    external_link = ARTIFACTS / "hardlink-report.md"
    external_link.unlink(missing_ok=True)
    os.link(hardlink_source, external_link)
    result = subprocess.run([sys.executable, str(CHECKER), str(external_link), "--replace-url", WRONG, BASE], capture_output=True, text=True, encoding="utf-8", timeout=20)
    decoded = json.loads(result.stdout)
    cases.append({"name": "atomic-write-breaks-hardlink-without-bundle-mutation", "passed": result.returncode == 0 and decoded["passed"] and external_link.read_text(encoding="utf-8") == BASE and payload() == baseline, "output": decoded})
    outcome = {"passed": all(case["passed"] for case in cases), "passedCount": sum(case["passed"] for case in cases), "caseCount": len(cases), "checkerSha256": digest(CHECKER), "cases": cases}
    (ARTIFACTS / "result.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in outcome.items() if key != "cases"}, indent=2))
    for case in cases:
        if not case["passed"]:
            print(json.dumps(case, indent=2))
    return 0 if outcome["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
