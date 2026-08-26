#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit the two direct, sealed pricing holdout trials."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


WINDOWS_PATH = re.compile(r"[A-Za-z]:[/\\][^\"'\s;&|]+")
NETWORK_MARKERS = ("http://", "https://", "curl ", "wget ", "gcloud ", "bq ")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def iter_events(path: Path) -> Iterable[dict[str, Any]]:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            yield event


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def normalized_windows_path(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").lower()


def tool_calls(events: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for event in events:
        if event.get("type") != "message_end":
            continue
        message = event.get("message") or {}
        if message.get("role") != "assistant":
            continue
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "toolCall":
                yield block


def audit_trial(trial_root: Path, expected_model: str, source_digest: str) -> dict[str, Any]:
    findings: list[str] = []
    verification = read_json(trial_root / "verification" / "verification.json")
    if verification.get("reward") != 1.0 or not verification.get("ok"):
        findings.append("verification")
    if verification.get("correct") != 10 or verification.get("total") != 10:
        findings.append("verification-count")
    if verification.get("mismatches") or verification.get("envelopeFindings"):
        findings.append("verification-findings")

    answers_path = trial_root / "answers.json"
    try:
        answers = read_json(answers_path)
    except (OSError, json.JSONDecodeError, ValueError):
        answers = {}
        findings.append("answers")
    if len(answers.get("answers") or []) != 10:
        findings.append("answer-count")

    staged_skill = trial_root / ".agents" / "skills" / "google-cloud-sku-pricing"
    staged_digest = tree_digest(staged_skill)
    if staged_digest != source_digest:
        findings.append("skill-digest")

    event_rows = list(iter_events(trial_root / "pi.txt"))
    models: set[str] = set()
    model_errors = 0
    for event in event_rows:
        for value in (event, event.get("message") or {}):
            if not isinstance(value, dict):
                continue
            if value.get("model"):
                models.add(str(value["model"]))
            if str(value.get("stopReason", "")).lower() == "error" or value.get(
                "errorMessage"
            ):
                model_errors += 1
    if models != {expected_model}:
        findings.append(f"models:{sorted(models)}")
    if model_errors:
        findings.append(f"model-errors:{model_errors}")

    root_text = normalized_windows_path(str(trial_root.resolve()))
    calls = list(tool_calls(event_rows))
    forbidden_calls: list[str] = []
    writes: list[str] = []
    for call in calls:
        name = str(call.get("name", ""))
        arguments = call.get("arguments") or {}
        if not isinstance(arguments, dict):
            forbidden_calls.append(f"{name}:arguments")
            continue
        if name in {"read", "write"}:
            path_value = str(arguments.get("path", ""))
            normalized = normalized_windows_path(path_value)
            if not (normalized == root_text or normalized.startswith(root_text + "/")):
                forbidden_calls.append(f"{name}:outside-workspace")
            if name == "write":
                writes.append(normalized)
        elif name == "bash":
            command = str(arguments.get("command", ""))
            lowered = command.lower()
            if any(marker.lower() in lowered for marker in NETWORK_MARKERS):
                forbidden_calls.append("bash:network")
            if "expected.json" in lowered or "benchmark.sqlite" in lowered:
                forbidden_calls.append("bash:evaluator-data")
            if re.search(r"(^|[\s/\\])\.\.([/\\\s]|$)", command):
                forbidden_calls.append("bash:ancestor")
            for absolute in WINDOWS_PATH.findall(command):
                normalized = normalized_windows_path(absolute)
                if not (normalized == root_text or normalized.startswith(root_text + "/")):
                    forbidden_calls.append("bash:outside-workspace")
                    break
        else:
            forbidden_calls.append(f"unexpected-tool:{name}")
    expected_write = normalized_windows_path(str(answers_path.resolve()))
    if writes != [expected_write]:
        findings.append(f"writes:{writes}")
    if forbidden_calls:
        findings.append(f"forbidden-tool-calls:{sorted(set(forbidden_calls))}")

    return {
        "ok": not findings,
        "task": trial_root.name,
        "reward": verification.get("reward"),
        "correct": verification.get("correct"),
        "total": verification.get("total"),
        "models": sorted(models),
        "modelErrorEvents": model_errors,
        "toolCalls": len(calls),
        "writeCalls": len(writes),
        "sourceSkillDigest": source_digest,
        "stagedSkillDigest": staged_digest,
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    repository_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=repository_root
        / "evaluations"
        / "runs"
        / "google-cloud-sku-pricing-holdout-v2-gpt54mini",
    )
    parser.add_argument(
        "--source-skill",
        type=Path,
        default=repository_root / "skills" / "google-cloud-sku-pricing",
    )
    parser.add_argument("--model", default="gpt-5.4-mini")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_digest = tree_digest(args.source_skill.resolve())
    trials = [
        audit_trial(args.run_root.resolve() / task, args.model, source_digest)
        for task in ("holdout-01", "holdout-02")
    ]
    result = {
        "ok": all(trial["ok"] for trial in trials),
        "model": args.model,
        "questionCount": sum(int(trial.get("total") or 0) for trial in trials),
        "correctCount": sum(int(trial.get("correct") or 0) for trial in trials),
        "trials": trials,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
