#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact manifests and outcomes from all authoring-review attempts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "evaluations/runs"
REVIEWS = ROOT / "projects/skill-authoring-audit/artifacts/reviews"


def read_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def main() -> int:
    independent = {}
    for filename in (
        "d3-independent.json", "d3-recipe-independent.json",
        "d3-final-independent.json", "d3-repaired-independent.json",
        "d3-capture-independent.json",
        "d3-builder-contract-independent.json", "d3-builder-natural-independent.json",
        "d3-builder-transfer-independent.json", "d3-builder-boundary-independent.json",
        "d3-verified-contract-independent.json", "d3-verified-natural-independent.json",
        "d3-verified-transfer-independent.json", "d3-verified-boundary-independent.json",
        "generated-reviewer-all-preliminary.json",
        "generated-reviewer-final-independent.json",
    ):
        report = read_json(REVIEWS / filename)
        for result in (report or {}).get("results", []):
            independent[result.get("runId", result.get("run"))] = result
    records = []
    for directory in sorted(RUNS.iterdir()):
        if directory.name.startswith("20261002-authoring-"):
            run = directory
        elif directory.name.startswith("generated-use-20261002-authoring-"):
            run = directory / "evaluations/runs" / directory.name.removeprefix("generated-use-")
        else:
            continue
        manifest = read_json(run / "run-manifest.json")
        result = read_json(run / "evaluation-result.json")
        routing = read_json(run / "routing-result.json")
        if manifest is None and result is None and routing is None and not (run / "events.jsonl").is_file() and (run.name.endswith("-smoke") or run.name == "20261002-authoring-local"):
            # Deterministic artifact workspaces are not model attempts.
            continue
        events = read_json(run / "event-check.json") or (routing or {}).get("events", {})
        calls = events.get("calls", [])
        errors = [call for call in calls if call.get("isError")]
        record = {
            "runId": run.name,
            "runPath": run.relative_to(ROOT).as_posix(),
            "date": "2026-10-02",
            "requestedModel": (manifest or {}).get("pi", {}).get("model") or (routing or {}).get("model"),
            "observedModels": events.get("observedModels", []),
            "payload": (manifest or {}).get("skill"),
            "prompt": (manifest or {}).get("prompt"),
            "piCommand": (manifest or {}).get("command"),
            "routingCommand": ["uv", "run", "--script", "evaluations/contracts/check-authoring-routing.py", "<fresh-run-id>"] if "routing-luna-" in run.name else None,
            "requiredOutputs": (manifest or {}).get("expectedOutputs", []) or (["routing.json"] if routing else []),
            "harnessResult": result,
            "routingResult": routing,
            "readPaths": [call["path"] for call in calls if call.get("tool") == "read" and call.get("path")],
            "toolErrorCount": len(errors),
            "failedCommands": [{key: call.get(key) for key in ("tool", "path", "command")} for call in errors],
            "independentArtifactResult": {key: value for key, value in independent[run.name].items() if key != "samples"} if run.name in independent else None,
        }
        if "routing-luna-1" in run.name:
            record["failureClass"] = "evaluator-design: answer-bearing IDs; excluded from acceptance"
        elif "routing-luna-2" in run.name:
            record["failureClass"] = "setup: invalid concurrent YAML; model not launched"
        elif "spark-1" in run.name:
            record["failureClass"] = "infrastructure: provider rejected the requested model before tools"
        elif result is not None and not result.get("passed"):
            record["failureClass"] = "forward execution: strict trace failure; retain artifact assessment separately"
        elif result is None and routing is None:
            record["failureClass"] = "incomplete or setup attempt; do not count as a pass"
        elif independent.get(run.name, {}).get("passed") is False:
            record["failureClass"] = "artifact validation: inspect retained checks and manual review"
        else:
            record["failureClass"] = None
        records.append(record)
    report = {
        "schemaVersion": 1,
        "date": "2026-10-02",
        "attemptCount": len(records),
        "excludedNonModelWorkspaces": ["20261002-authoring-local", "20261002-authoring-d3-builder-smoke", "20261002-authoring-d3-builder-boundary-smoke"],
        "acceptancePolicy": "Naturalistic cases require at least 2/3 joint passes; the unsafe-execution boundary requires 3/3. Count only the frozen final revision for its release claim.",
        "records": records,
        "scope": "Metadata routing is classification only. Fresh forward tests cover D3 and repository-reviewer-creator plus the generated Tenant Catalog reviewer. Other skill release evidence remains in SKILLS.md.",
    }
    output = ROOT / "evaluations/skill-authoring/20261002-forward-evidence.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attemptCount": len(records), "output": output.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
