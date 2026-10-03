#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact custom-renderer results with exact trial and payload identities."""
import json
from pathlib import Path
import shlex

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "projects/custom-solid-style/artifacts/data"
DEST = ROOT / "evaluations/custom-solid-style"
DEST.mkdir(parents=True, exist_ok=True)
review = json.loads((DATA / "pi-artifact-review.json").read_text(encoding="utf-8"))
assert review["jointFinalPasses"] == 20
records = []
for entry in review["attempts"]:
    folder = ROOT / "evaluations/runs" / entry["runId"]
    manifest = json.loads((folder / "run-manifest.json").read_text(encoding="utf-8"))
    event = json.loads((folder / "event-check.json").read_text(encoding="utf-8"))
    result = json.loads((folder / "evaluation-result.json").read_text(encoding="utf-8"))
    kind = "contract" if "-contract-" in entry["runId"] else "naturalistic"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", entry["skill"], "--prompt-file", f'evaluations/pi-prompts/custom-solid-style/{entry["skill"]}-{kind}.md', "--model", "openai-codex/gpt-5.6-luna", "--mode", "json", "--strict", "--run-id", entry["runId"], "--timeout-seconds", "600"]
    if kind == "contract":
        command.append("--require-exact-command-from-prompt")
    for name in manifest["expectedOutputs"]:
        command.extend(["--expect-output", name])
    compact = {key: value for key, value in entry.items() if key not in {"marks", "labels", "materials", "variants"}}
    compact.update(case=kind, date="2026-10-03", model=manifest["pi"]["model"], observedModels=event["observedModels"], command=command, commandText=shlex.join(command), outputs=manifest["expectedOutputs"], promptSha256=manifest["prompt"]["sha256"], gates=result["gates"], findings=event["findings"], toolErrorCount=sum(bool(call["isError"]) for call in event["calls"]), reads=[call["path"] for call in event["calls"] if call["tool"] == "read"], rawEvidence=f'evaluations/runs/{entry["runId"]}/')
    compact["classification"] = ("harness" if not entry["strictPassed"] and all(finding["code"] == "no-fenced-command-in-prompt" for finding in event["findings"])
                                 else "agent" if not entry["strictPassed"] else "skill" if entry.get("vendorRuntimePreserved") is False else "pass")
    compact["cohort"] = "final" if entry["strictPassed"] and entry["matchesFinalPayload"] and entry["artifactPassed"] else "superseded" if entry["strictPassed"] else "retained-failure"
    records.append(compact)
for skill in review["finalPayloads"]:
    cohort = [record for record in records if record["skill"] == skill and record["cohort"] == "final"]
    assert len(cohort) == 4
    assert sum(record["case"] == "contract" for record in cohort) == 1
    assert sum(record["case"] == "naturalistic" for record in cohort) == 3
    assert all(record["toolErrorCount"] == 0 and record["gates"]["skillIntegrity"] for record in cohort)
summary = {"schemaVersion": 1, "date": "2026-10-03", "model": "openai-codex/gpt-5.6-luna", "modelException": "Existing SKILLS.md colorset audit model exception", "finalPayloads": review["finalPayloads"], "attemptCount": len(records), "strictPassCount": review["strictPasses"], "styleArtifactPassCount": review["artifactPasses"], "finalJointPassCount": review["jointFinalPasses"], "attempts": records}
summary["matchingFinalPayloadAttemptCount"] = sum(record["matchesFinalPayload"] for record in records)
summary["matchingFinalPayloadStrictFailures"] = [{key:record[key] for key in ("runId","skill","classification","findings")} for record in records if record["matchesFinalPayload"] and not record["strictPassed"]]
summary["finalNaturalisticRepetitions"] = {skill:{"attempts":len(cohort),"strictPasses":sum(record["strictPassed"] for record in cohort),"runIds":[record["runId"] for record in cohort]} for skill in review["finalPayloads"] for cohort in [[record for record in records if record["skill"]==skill and record["matchesFinalPayload"] and record["case"]=="naturalistic"]]}
(DEST / "results-20261003.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
for name in ("deterministic-style-check.json", "gallery-style-check.json", "vector-fixture-finalization.json", "alpha-chrome-check.json", "overflow-boundary-check.json"):
    value = json.loads((DATA / name).read_text(encoding="utf-8"))
    (DEST / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key not in {"attempts", "finalPayloads"}}, indent=2))
