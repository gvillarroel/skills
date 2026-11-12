#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run plugin-authoring metadata routing with frozen evaluator-side answers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "20261025-plugin-build-routing-sol-1"
MODEL = "openai-codex/gpt-6.1-sol"
EXPECTED = {
    "claude-desktop-build": True,
    "chatgpt-desktop-build": True,
    "codex-build": True,
    "pi-extension-build": True,
    "claude-code-build": True,
    "plugin-host-compatibility": True,
    "plugin-nielsen-review": True,
    "generic-website": False,
    "general-nielsen-review": False,
    "api-pricing": False,
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_metadata() -> str:
    """Read the frontmatter line by line; never consume the skill body."""
    path = ROOT / "skills/desktop-plugin-ui/SKILL.md"
    with path.open(encoding="utf-8-sig") as handle:
        if handle.readline().strip() != "---":
            raise ValueError("Skill frontmatter is missing")
        lines = []
        for _ in range(128):
            line = handle.readline()
            if not line:
                break
            if line.strip() == "---":
                return "".join(lines).strip()
            lines.append(line)
    raise ValueError("Skill frontmatter did not terminate within 128 lines")


def main() -> int:
    metadata = read_metadata()
    template = Path(__file__).with_name("plugin-build-routing-prompt.md").read_text(encoding="utf-8")
    if template.count("{{SKILL_METADATA}}") != 1:
        raise ValueError("Routing prompt needs exactly one metadata placeholder")
    prompt = template.replace("{{SKILL_METADATA}}", metadata)
    run = ROOT / "evaluations/runs" / RUN_ID
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    write_json(run / "acceptance.json", EXPECTED)
    spec = importlib.util.spec_from_file_location("desktop_ui_routing_harness", ROOT / "scripts/run-pi-skill-eval.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the evaluator harness")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    prefix = harness.pi_command_prefix()
    version_result = subprocess.run([*prefix, "--version"], capture_output=True, text=True, timeout=30)
    version = version_result.stdout.strip()
    (run / "pi-version.txt").write_text(version + "\n" + version_result.stderr, encoding="utf-8")
    if version_result.returncode or version != "1.4.0":
        raise RuntimeError(f"Required Pi 1.4.0, found {version!r}")
    command = [*prefix, "--model", MODEL, "--thinking", "high", "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session", "--no-mcp", "--print", "Use the read tool to read ../prompt.md first, then follow that task. No skill body is loaded."]
    write_json(run / "command.json", command)
    write_json(run / "run-manifest.json", {
        "runId": RUN_ID, "model": MODEL, "piVersion": version,
        "createdAt": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
        "command": command, "cwd": str(workspace), "noForcedSkill": "--skill" not in command,
        "noSkillBodyProvided": True, "skillMetadata": metadata,
        "metadataSha256": hashlib.sha256(metadata.encode("utf-8")).hexdigest(),
        "promptSha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "scope": "metadata decision control; not automatic product skill selection",
        "requiredOutput": "results/routing.json",
    })
    exit_code = None
    failure = None
    with (run / "events.jsonl").open("w", encoding="utf-8") as output, (run / "stderr.txt").open("w", encoding="utf-8") as error:
        try:
            result = subprocess.run(command, cwd=workspace, stdout=output, stderr=error, timeout=240)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            failure = "infrastructure: Pi exceeded the 240-second routing-control timeout"
    trace = harness.event_check_report(events_path=run / "events.jsonl", prompt=prompt, require_prompt_read_first=True, require_exact_command_from_prompt=False, require_observed_model=True, requested_model=MODEL, fail_on_invalid_json=True, fail_on_tool_error=True, forbid_read_regex=[r"^(?!\.\./prompt\.md$).+"], forbid_command_regex=[r"(?s).+"])
    write_json(run / "event-check.json", trace)
    artifact = workspace / "results/routing.json"
    errors = []
    decisions = []
    if artifact.is_file() and artifact.stat().st_size:
        try:
            decoded = json.loads(artifact.read_text(encoding="utf-8"))
            if not isinstance(decoded, dict) or set(decoded) != {"decisions"} or not isinstance(decoded["decisions"], list):
                errors.append("Artifact must contain only a decisions array")
            else:
                decisions = decoded["decisions"]
        except (ValueError, OSError) as error:
            errors.append(f"Cannot parse output artifact: {error}")
    else:
        errors.append("Missing nonempty exact required output results/routing.json")
    if len(decisions) != len(EXPECTED):
        errors.append(f"Expected exactly {len(EXPECTED)} decisions")
    if [decision.get("id") if isinstance(decision, dict) else None for decision in decisions] != list(EXPECTED):
        errors.append("Decision IDs/order differ from the prompt")
    grades = []
    for case_id, expected in EXPECTED.items():
        decision = next((row for row in decisions if isinstance(row, dict) and row.get("id") == case_id), {})
        schema_ok = set(decision) == {"id", "use", "reason"} and type(decision.get("use")) is bool and isinstance(decision.get("reason"), str) and bool(decision["reason"].strip())
        grades.append({"id": case_id, "expectedUse": expected, "actualUse": decision.get("use"), "schemaPassed": schema_ok, "passed": schema_ok and decision["use"] is expected, "reason": decision.get("reason")})
    extras = sorted(str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file() and path != artifact)
    if extras:
        errors.append(f"Unexpected extra artifacts: {extras}")
    passed = exit_code == 0 and trace["passed"] and not errors and all(row["passed"] for row in grades)
    report = {"passed": passed, "correct": sum(row["passed"] for row in grades), "total": len(EXPECTED), "exitCode": exit_code, "noForcedSkill": "--skill" not in command, "noSkillBodyProvided": True, "tracePassed": trace["passed"], "metadataSha256": hashlib.sha256(metadata.encode("utf-8")).hexdigest(), "errors": errors, "failureClassification": failure if failure else None if passed else "agent-or-harness: inspect retained trace and artifact", "artifactSha256": hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else None, "grades": grades}
    write_json(run / "result.json", report)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
