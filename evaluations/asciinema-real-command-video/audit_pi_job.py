#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit Pi traces for prompt integrity and single-pass skill compliance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


SKILL_COMMAND = r"asciinema_command_video\.py\s+"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def audit_trial(trial: Path, dataset_root: Path) -> dict[str, object]:
    task_id = trial.name.split("__", 1)[0]
    expected = (dataset_root / task_id / "instruction.md").read_text(encoding="utf-8")
    trace_path = trial / "agent" / "pi.txt"
    wrapper_marker: dict[str, object] = {}
    user_prompt = ""
    commands: list[str] = []
    written_paths: list[str] = []
    event_types: list[str] = []
    invalid_json_lines = 0

    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            invalid_json_lines += 1
            continue
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("type") or "")
        event_types.append(event_type)
        if event_type == "harbor_pi_wrapper":
            wrapper_marker = event
        if event_type == "message_end":
            message = event.get("message") or {}
            if message.get("role") == "user" and not user_prompt:
                content = message.get("content") or []
                user_prompt = "".join(
                    str(item.get("text") or "")
                    for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
        if event_type == "tool_execution_start":
            tool = event.get("toolName")
            arguments = event.get("args") or {}
            if tool == "bash":
                commands.append(str(arguments.get("command") or ""))
            elif tool in {"write", "edit"}:
                written_paths.append(str(arguments.get("path") or "").replace("\\", "/"))

    accepted_prompts = {expected, expected.rstrip("\r\n")}
    prompt_complete = user_prompt in accepted_prompts
    prompt_sha256 = sha256_text(user_prompt)
    prompt_bytes = len(user_prompt.encode("utf-8"))
    marker_matches = bool(
        wrapper_marker
        and wrapper_marker.get("promptSha256") == prompt_sha256
        and wrapper_marker.get("promptBytes") == prompt_bytes
    )
    command_text = "\n".join(commands)
    record_calls = len(re.findall(SKILL_COMMAND + r"record(?:\s|$)", command_text))
    preflight_calls = len(re.findall(SKILL_COMMAND + r"preflight(?:\s|$)", command_text))
    plan_validation_calls = len(
        re.findall(SKILL_COMMAND + r"validate-plan(?:\s|$)", command_text)
    )
    validation_calls = len(
        re.findall(SKILL_COMMAND + r"validate(?:\s|$)", command_text)
    )
    custom_source_paths = sorted(
        {
            path
            for path in written_paths
            if re.search(r"(?:^|/)source/", path)
            and not path.endswith("/source/session-plan.json")
            and path != "source/session-plan.json"
        }
    )
    direct_recorder_calls = len(
        re.findall(r"(?:^|\s)(?:[^\s]*asciinema)(?:\.exe)?\s+rec(?:\s|$)", command_text)
    )
    retry_mutations = len(
        re.findall(
            r"(?:rm|mv)[^\n]*(?:deliverables/)?session(?:\.|-)",
            command_text,
            flags=re.IGNORECASE,
        )
    )
    agent_completed = "agent_end" in event_types and "agent_settled" in event_types
    findings: list[str] = []
    if not prompt_complete:
        findings.append("Pi did not receive the complete frozen instruction")
    if not marker_matches:
        findings.append("wrapper prompt bytes or SHA-256 do not match Pi's user message")
    if record_calls != 1:
        findings.append(f"expected exactly one skill record call; observed {record_calls}")
    if preflight_calls < 1:
        findings.append("explicit skill preflight call is missing")
    if plan_validation_calls < 1:
        findings.append("skill plan validation call is missing")
    if validation_calls < 1:
        findings.append("independent skill validation call is missing")
    if custom_source_paths:
        findings.append(f"custom source controllers were written: {custom_source_paths}")
    if direct_recorder_calls:
        findings.append(f"direct Asciinema recorder calls bypassed the skill: {direct_recorder_calls}")
    if retry_mutations:
        findings.append(f"prior session artifacts were moved or removed: {retry_mutations}")
    if not agent_completed:
        findings.append("Pi trace did not reach agent_end and agent_settled")

    return {
        "taskId": task_id,
        "ok": not findings,
        "findings": findings,
        "promptComplete": prompt_complete,
        "promptBytes": prompt_bytes,
        "promptSha256": prompt_sha256,
        "wrapperMarkerMatches": marker_matches,
        "recordCalls": record_calls,
        "preflightCalls": preflight_calls,
        "planValidationCalls": plan_validation_calls,
        "validationCalls": validation_calls,
        "customSourcePaths": custom_source_paths,
        "directRecorderCalls": direct_recorder_calls,
        "retryMutations": retry_mutations,
        "agentCompleted": agent_completed,
        "invalidJsonLines": invalid_json_lines,
    }


def main() -> int:
    args = parse_arguments()
    job_root = args.job_root.resolve()
    dataset_root = args.dataset_root.resolve()
    results = [
        audit_trial(trial, dataset_root)
        for trial in sorted(path for path in job_root.iterdir() if path.is_dir())
    ]
    aggregate = {
        "schemaVersion": 1,
        "jobRoot": str(job_root),
        "datasetRoot": str(dataset_root),
        "caseCount": len(results),
        "passCount": sum(1 for result in results if result["ok"]),
        "results": results,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0 if aggregate["passCount"] == aggregate["caseCount"] else 1


if __name__ == "__main__":
    sys.exit(main())
