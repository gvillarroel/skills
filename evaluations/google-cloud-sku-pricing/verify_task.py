#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score one frozen Google Cloud SKU pricing question batch."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import os
from pathlib import Path
import sys
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def shape_mismatches(expected: Any, actual: Any, path: str = "answer") -> list[str]:
    """Describe structural/value mismatch locations without leaking answers."""

    if type(expected) is not type(actual):
        return [f"{path}:type"]
    if isinstance(expected, Mapping):
        findings: list[str] = []
        expected_keys = set(expected)
        actual_keys = set(actual)
        for key in sorted(expected_keys - actual_keys):
            findings.append(f"{path}.{key}:missing")
        for key in sorted(actual_keys - expected_keys):
            findings.append(f"{path}.{key}:unexpected")
        for key in sorted(expected_keys & actual_keys):
            findings.extend(shape_mismatches(expected[key], actual[key], f"{path}.{key}"))
        return findings
    if isinstance(expected, Sequence) and not isinstance(expected, (str, bytes)):
        findings = []
        if len(expected) != len(actual):
            findings.append(f"{path}:length")
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            findings.extend(shape_mismatches(expected_item, actual_item, f"{path}[{index}]"))
        return findings
    return [] if expected == actual else [f"{path}:value"]


def score(expected_payload: Any, actual_payload: Any) -> dict[str, Any]:
    expected_rows = expected_payload.get("answers", []) if isinstance(expected_payload, dict) else []
    expected_by_id = {
        row.get("id"): row.get("answer")
        for row in expected_rows
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    findings: dict[str, list[str]] = {}
    actual_by_id: dict[str, Any] = {}
    envelope_findings: list[str] = []

    if not isinstance(actual_payload, dict):
        envelope_findings.append("root:type")
    else:
        extra_root = sorted(set(actual_payload) - {"answers"})
        if extra_root:
            envelope_findings.extend(f"root.{key}:unexpected" for key in extra_root)
        actual_rows = actual_payload.get("answers")
        if not isinstance(actual_rows, list):
            envelope_findings.append("root.answers:type")
        else:
            for index, row in enumerate(actual_rows):
                if not isinstance(row, dict):
                    envelope_findings.append(f"root.answers[{index}]:type")
                    continue
                if set(row) != {"id", "answer"}:
                    envelope_findings.append(f"root.answers[{index}]:shape")
                question_id = row.get("id")
                if not isinstance(question_id, str):
                    envelope_findings.append(f"root.answers[{index}].id:type")
                    continue
                if question_id in actual_by_id:
                    envelope_findings.append(f"root.answers[{index}].id:duplicate")
                    continue
                actual_by_id[question_id] = row.get("answer")

    correct_ids: list[str] = []
    for question_id, expected_answer in expected_by_id.items():
        if question_id not in actual_by_id:
            findings[question_id] = ["answer:missing"]
            continue
        mismatches = shape_mismatches(expected_answer, actual_by_id[question_id])
        if mismatches:
            findings[question_id] = mismatches
        else:
            correct_ids.append(question_id)

    unexpected_ids = sorted(set(actual_by_id) - set(expected_by_id))
    envelope_findings.extend(f"answer:{question_id}:unexpected" for question_id in unexpected_ids)
    total = len(expected_by_id)
    correct = len(correct_ids)
    reward = correct / total if total else 0.0
    return {
        "ok": correct == total and not envelope_findings,
        "reward": reward,
        "correct": correct,
        "total": total,
        "correctIds": sorted(correct_ids),
        "mismatches": findings,
        "envelopeFindings": envelope_findings,
    }


def main() -> int:
    workspace = Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    verifier_dir = Path(
        os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")
    ).resolve()
    verifier_dir.mkdir(parents=True, exist_ok=True)
    expected_path = Path(__file__).with_name("expected.json")
    actual_path = workspace / "answers.json"

    try:
        expected = read_json(expected_path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Evaluator contract is unreadable: {type(error).__name__}", file=sys.stderr)
        return 2
    try:
        actual = read_json(actual_path)
    except OSError:
        actual = None
        parse_finding = "answers.json:missing"
    except json.JSONDecodeError:
        actual = None
        parse_finding = "answers.json:invalid-json"
    else:
        parse_finding = ""

    result = score(expected, actual)
    if parse_finding:
        result["envelopeFindings"].append(parse_finding)
        result["ok"] = False
    reward_payload = {
        "reward": result["reward"],
        "correctness": result["reward"],
        "format": 1.0 if not result["envelopeFindings"] else 0.0,
    }
    (verifier_dir / "verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (verifier_dir / "reward.json").write_text(
        json.dumps(reward_payload, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

