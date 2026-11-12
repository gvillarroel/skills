#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Grade frozen cross-assistant advisory runs; require separate semantic review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HOSTS = {"claude-code", "claude-desktop", "codex", "chatgpt", "copilot"}
OUTPUTS = {
    "contract": ("results/cross-reference.md", "results/cross-decisions.json"),
    "naturalistic": ("proposal/support-queue.md", "proposal/host-decisions.json"),
    "generalization": ("handoff/restricted-surfaces.md", "handoff/recovery-plan.json"),
    "boundary": ("review/cross-boundaries.md", "review/cross-status.json"),
}
URL = re.compile(r"https?://[^\s<>\"`'\[\]()]+")
PATTERN_HEADING = re.compile(
    r"^#{2,6}\s+`?([a-z][a-z0-9]*(?:-[a-z0-9]+)*-ui-[a-z0-9]+(?:-[a-z0-9]+)*)`?\s*(?:#+)?$",
    re.M,
)
PRIMARY_DOMAINS = (
    "anthropic.com", "claude.com", "modelcontextprotocol.io", "openai.com",
    "chatgpt.com", "github.com", "githubusercontent.com", "visualstudio.com",
    "microsoft.com",
)


def urls(text: str) -> set[str]:
    """Preserve complete paths and fragments; only strip prose punctuation."""
    return {value.rstrip(".,;:)]}") for value in URL.findall(text)}


def primary(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in PRIMARY_DOMAINS)


def nonempty(value: object) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def selected_ids(patterns: object, canonical: set[str], findings: list[str]) -> set[str]:
    if not isinstance(patterns, list) or not patterns:
        findings.append("patterns must be a nonempty array")
        return set()
    selected = set()
    for pattern in patterns:
        value = pattern if isinstance(pattern, str) else pattern.get("id") if isinstance(pattern, dict) else None
        if not isinstance(value, str) or value not in canonical:
            findings.append(f"Unknown canonical pattern: {value!r}")
        else:
            selected.add(value)
    return selected


def source_fields(row: dict, allowed: set[str], context: str, findings: list[str]) -> None:
    cited = row.get("sources")
    if not isinstance(cited, list) or not cited:
        findings.append(f"{context}: sources must contain exact bundled primary URLs")
        return
    for value in cited:
        if not isinstance(value, str) or value not in allowed or not primary(value):
            findings.append(f"{context}: source absent from copied bundle: {value!r}")


def structured_findings(data: dict, case: str, canonical: set[str], allowed: set[str]) -> tuple[list[str], set[str]]:
    findings: list[str] = []
    for field in ("host_acceptance_verified", "task_empirical_tests_performed"):
        if data.get(field) is not False:
            findings.append(f"{field} must be false for this advisory task")
    if case == "boundary" and data.get("product_confirmed") is not False:
        findings.append("Boundary review must preserve product uncertainty")
    if case != "boundary" and not nonempty(data.get("snapshot_date")):
        findings.append("snapshot_date missing")
    patterns = data.get("patterns")
    selected = selected_ids(patterns, canonical, findings)
    if case == "contract":
        if len(selected) < 10:
            findings.append("Contract requires at least ten distinct canonical patterns")
        for row in patterns if isinstance(patterns, list) else []:
            if not isinstance(row, dict) or not all(nonempty(row.get(key)) for key in ("id", "input", "rule", "fallback", "validation", "evidence")):
                findings.append("Contract pattern missing input/rule/fallback/validation/evidence")
    if case != "boundary":
        rows = data.get("hosts")
        if not isinstance(rows, list) or not rows:
            findings.append("hosts must be a nonempty array")
            rows = []
        present = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                findings.append(f"hosts[{index}] is not an object")
                continue
            host_id = row.get("host_id")
            if host_id not in HOSTS:
                findings.append(f"Unknown host_id {host_id!r}")
            else:
                present.add(host_id)
            for field in ("host", "surface", "ui_method", "limits", "evidence", "validation"):
                if not nonempty(row.get(field)):
                    findings.append(f"hosts[{index}]: missing {field}")
            if not isinstance(row.get("limits"), list):
                findings.append(f"hosts[{index}]: limits must be an array")
            source_fields(row, allowed, f"hosts[{index}]", findings)
        if case in {"contract", "naturalistic"} and present != HOSTS:
            findings.append("Host coverage missing: " + ", ".join(sorted(HOSTS - present)))
    else:
        assessments = data.get("assessments")
        if not isinstance(assessments, list) or not assessments:
            findings.append("Boundary assessments missing")
            assessments = []
        for index, row in enumerate(assessments):
            if not isinstance(row, dict) or not all(nonempty(row.get(key)) for key in ("topic", "status", "reason", "fallback", "evidence_layer", "validation")):
                findings.append(f"assessments[{index}]: missing decision fields")
            if isinstance(row, dict):
                source_fields(row, allowed, f"assessments[{index}]", findings)
    observations = data.get("historical_observations")
    if not isinstance(observations, list) or not observations:
        findings.append("Historical empirical evidence must be retained separately")
        observations = []
    for index, row in enumerate(observations):
        if not isinstance(row, dict) or not all(nonempty(row.get(key)) for key in ("host_id", "surface", "version", "evidence_layer", "result", "evidence")):
            findings.append(f"historical_observations[{index}]: incomplete evidence scope")
    if observations and not re.search(r"observed[- ](?:working|failed)", json.dumps(observations), re.I):
        findings.append("Historical observations must preserve recorded empirical evidence labels")
    if case == "generalization" and not isinstance(data.get("checks"), list):
        findings.append("Generalization requires checks array")
    return findings, selected


def semantic_flags(text: str) -> list[str]:
    """Collect review cues without treating ordinary negations as verdicts."""
    broad = re.compile(
        r"\b(?:Codex|Copilot|Claude(?:\s+Code)?)\s+(?:has\s+no|cannot|can't|does\s+not\s+support)\s+"
        r"(?:(?:show|render|display|use)\s+)?(?:any\s+)?(?:UI|forms?|images?|canvases|plugins?|HTML)\b[^.\n]{0,160}",
        re.I,
    )
    return list(dict.fromkeys(match.group(0) for match in broad.finditer(text)))


def inspect(run: Path, require_model: str) -> dict:
    findings: list[str] = []
    manifest = load(run / "run-manifest.json")
    result = load(run / "evaluation-result.json")
    event_check = load(run / "event-check.json")
    integrity = load(run / "skill-integrity-check.json")
    artifact_check = load(run / "artifact-check.json")
    case = next((name for name in OUTPUTS if f"-cross-{name}" in manifest.get("prompt", {}).get("source", "")), None)
    if case is None:
        raise ValueError("Prompt does not identify a cross-assistant case")
    expected = OUTPUTS[case]
    if set(manifest.get("expectedOutputs", [])) != set(expected):
        findings.append("Manifest must declare both exact case output paths and no substitutes")
    if manifest.get("pi", {}).get("model") != require_model:
        findings.append("Manifest model differs from required recorded model")
    if manifest.get("pi", {}).get("mode") != "json" or manifest.get("eventPolicy", {}).get("strict") is not True:
        findings.append("Release run must use strict JSON mode")
    if result.get("passed") is not True or result.get("piExitCode") != 0 or result.get("timedOut") is not False:
        findings.append("Strict harness result failed")
    for name, gate in (("events", event_check), ("skill integrity", integrity), ("artifacts", artifact_check)):
        if gate.get("passed") is not True:
            findings.append(f"{name} gate failed")
    if integrity.get("beforeDigest") != manifest.get("skill", {}).get("payloadSha256") or integrity.get("beforeDigest") != integrity.get("afterDigest"):
        findings.append("Integrity digests do not match the frozen manifest payload")
    observed = {str(row.get("provider")) + "/" + str(row.get("model")) for row in event_check.get("observedModels", [])}
    if observed != {require_model}:
        findings.append("Observed model does not match required model exactly")
    workspace = run / "workspace"
    bundle = workspace / "skills/desktop-plugin-ui"
    source = "\n".join(path.read_text(encoding="utf-8-sig") for path in bundle.rglob("*.md"))
    canonical = set(PATTERN_HEADING.findall(source))
    source_catalog = bundle / "scripts/check_sources.py"
    allowed = urls(source + "\n" + source_catalog.read_text(encoding="utf-8-sig"))
    if len(canonical) < 10:
        findings.append("Copied bundle exposes fewer than ten canonical pattern headings")
    texts = []
    digests = {}
    data = {}
    recorded_artifacts = {row.get("path"): row for row in artifact_check.get("outputs", [])}
    for relative in expected:
        artifact = workspace / relative
        if not artifact.is_file() or artifact.stat().st_size == 0:
            findings.append(f"Missing or empty exact artifact: {relative}")
            continue
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        digests[relative] = digest
        if recorded_artifacts.get(relative, {}).get("sha256") != digest:
            findings.append(f"Artifact changed since harness check: {relative}")
        content = artifact.read_text(encoding="utf-8-sig")
        texts.append(content)
        unknown = {value for value in urls(content) if primary(value)} - allowed
        if unknown:
            findings.append(f"{relative}: primary URLs absent from copied bundle: " + ", ".join(sorted(unknown)))
        if artifact.suffix == ".json":
            data = json.loads(content)
    structured, selected = structured_findings(data, case, canonical, allowed)
    findings.extend(structured)
    calls = event_check.get("calls", [])
    checker_coverage = set()
    command_review = []
    for index, call in enumerate(calls):
        command = call.get("command") or ""
        if "check_sources.py" in command and not call.get("isError"):
            for relative in expected:
                last_write = max((i for i, row in enumerate(calls) if row.get("tool") in {"write", "edit"} and (row.get("path") or "").replace("\\", "/").endswith(relative)), default=-1)
                if relative in command and index > last_write:
                    checker_coverage.add(relative)
        if re.search(r"(?im)^\s*(?:curl|wget|Invoke-WebRequest|claude|copilot|codex|gh)\b|^\s*(?:npm|pip|winget)\s+install\b", command):
            command_review.append({"line": call.get("line"), "command": command[:500]})
    if checker_coverage != set(expected):
        findings.append("Trace does not show successful source checks after final writes for both artifacts")
    checker_result = {"passed": False, "error": "Required outputs unavailable"}
    if len(digests) == 2:
        checked = subprocess.run(
            [sys.executable, str((bundle / "scripts/check_sources.py").resolve()), *[str((workspace / path).resolve()) for path in expected], "--fail-on-findings"],
            cwd=workspace, capture_output=True, text=True, timeout=30,
        )
        try:
            checker_result = json.loads(checked.stdout)
        except json.JSONDecodeError:
            checker_result = {"passed": False, "error": checked.stderr[:500] or checked.stdout[:500]}
        if checked.returncode != 0 or checker_result.get("passed") is not True:
            findings.append("Independent source checker failed")
    combined = "\n".join(texts)
    return {
        "run": run.name, "case": case, "payloadSha256": manifest["skill"]["payloadSha256"],
        "model": manifest["pi"]["model"], "strictPassed": result.get("passed") is True,
        "structuralEvidencePassed": not findings, "canonicalPatternCount": len(canonical),
        "selectedPatternCount": len(selected), "artifactSha256": digests,
        "sourceCheckerPassed": checker_result.get("passed") is True,
        "agentCheckerCoveredArtifacts": sorted(checker_coverage), "findings": findings,
        "broadExclusionReviewCues": semantic_flags(combined), "externalCommandReview": command_review,
        "semanticReviewRequired": True,
    }


def self_test() -> int:
    headings = "## claude-ui-native-pane\n### `copilot-ui-cli-forms`\n## codex-ui-form-negotiation\n## Ordinary prose\n"
    assert set(PATTERN_HEADING.findall(headings)) == {"claude-ui-native-pane", "copilot-ui-cli-forms", "codex-ui-form-negotiation"}
    assert urls("[x](https://docs.github.com/path#section).") == {"https://docs.github.com/path#section"}
    assert primary("https://code.visualstudio.com/api/extension-guides/ai/mcp")
    assert not primary("https://openai.com.evil.invalid/path")
    assert semantic_flags("Codex cannot show UI.") == ["Codex cannot show UI"]
    assert semantic_flags("Copilot has no forms.") == ["Copilot has no forms"]
    assert not semantic_flags("Copilot's tested ACP ui/show method is unavailable; other surfaces differ.")
    findings, selected = structured_findings({"host_acceptance_verified": True}, "contract", set(), set())
    assert findings and not selected
    canonical = {f"test-ui-control-{index}" for index in range(10)}
    allowed = {"https://code.visualstudio.com/api/extension-guides/ai/mcp"}
    valid = {
        "snapshot_date": "2026-10-24", "host_acceptance_verified": False,
        "task_empirical_tests_performed": False,
        "hosts": [{"host_id": host, "host": host, "surface": "named surface", "ui_method": "bounded method", "limits": ["bounded limit"], "evidence": "documented", "validation": "real host check", "sources": list(allowed)} for host in sorted(HOSTS)],
        "patterns": [{"id": value, "input": "typed inputs", "rule": "concrete rule", "fallback": "text fallback", "validation": "bounded test", "evidence": "conditional"} for value in sorted(canonical)],
        "historical_observations": [{"host_id": "copilot", "surface": "terminal", "version": "test build", "evidence_layer": "actual terminal UI", "result": "cancel returned null", "evidence": "observed-working"}],
    }
    assert structured_findings(valid, "contract", canonical, allowed) == ([], canonical)
    missing_host = json.loads(json.dumps(valid)); missing_host["hosts"].pop()
    assert any("Host coverage" in value for value in structured_findings(missing_host, "naturalistic", canonical, allowed)[0])
    weak_contract = json.loads(json.dumps(valid)); weak_contract["patterns"].pop()
    assert any("at least ten" in value for value in structured_findings(weak_contract, "contract", canonical, allowed)[0])
    wrong_url = json.loads(json.dumps(valid)); wrong_url["hosts"][0]["sources"] = ["https://code.visualstudio.com/unverified"]
    assert any("source absent" in value for value in structured_findings(wrong_url, "contract", canonical, allowed)[0])
    erased = json.loads(json.dumps(valid)); erased["historical_observations"][0]["evidence"] = "untested"
    assert any("empirical evidence labels" in value for value in structured_findings(erased, "contract", canonical, allowed)[0])
    assert not any("Host coverage" in value for value in structured_findings(missing_host, "generalization", canonical, allowed)[0])
    assert any("uncertainty" in value for value in structured_findings({**valid, "product_confirmed": True}, "boundary", canonical, allowed)[0])
    print(json.dumps({"passed": True, "selfTests": 15}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", help="Run-name prefix under evaluations/runs")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-model", default="openai-codex/gpt-5.6-luna", help="Recorded exception; default Spark was rejected by the account")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.prefix or not args.output:
        parser.error("--prefix and --output are required unless --self-test is used")
    reports = []
    for run in sorted((ROOT / "evaluations/runs").glob(args.prefix + "*")):
        if not (run / "run-manifest.json").is_file() or not (run / "evaluation-result.json").is_file():
            continue
        try:
            reports.append(inspect(run, args.require_model))
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
            reports.append({"run": run.name, "strictPassed": False, "structuralEvidencePassed": False, "findings": [str(error)], "semanticReviewRequired": True})
    payloads = sorted({row["payloadSha256"] for row in reports if "payloadSha256" in row})
    passed = bool(reports) and len(payloads) == 1 and all(row["strictPassed"] and row["structuralEvidencePassed"] for row in reports)
    report = {"passed": passed, "runs": reports, "completedCount": len(reports), "payloads": payloads, "singleFrozenPayload": len(payloads) == 1, "semanticReviewRequired": True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "completed": len(reports), "payloads": payloads, "output": str(args.output)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
