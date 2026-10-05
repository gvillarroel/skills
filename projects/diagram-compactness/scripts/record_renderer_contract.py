#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record retained current-source PlantUML contract closure from raw evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
name = "20261004-compaction-plantuml-contract-luna-2"
run = ROOT / "evaluations/runs" / name
manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
result = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
summary = json.loads((run / "observed-event-summary.json").read_text(encoding="utf-8"))
assert result["passed"] and summary["passed"]
target = ROOT / "evaluations/diagram-compactness/renderers-20261004.json"
data = json.loads(target.read_text(encoding="utf-8"))
for row in data["runs"]:
    if row["id"] == "20261004-compaction-plantuml-contract-luna-1":
        row["finalCohort"] = False
        row["lineageQualification"] = "Only agents/openai.yaml added the compact-layout default-prompt sentence; all runtime guidance/resources are byte-identical. Superseded by current-byte contract-luna-2."
data["runs"] = [row for row in data["runs"] if row["id"] != name]
data["runs"].append({"id": name, "skill": manifest["skill"], "prompt": manifest["prompt"],
                     "model": manifest["pi"]["model"], "result": result,
                     "expectedOutputs": manifest["expectedOutputs"], "finalCohort": True,
                     "readPaths": [row["path"] for row in summary["readPaths"]],
                     "readSurfacePassed": True,
                     "independentArtifactPassed": True,
                     "independentArtifactPath": "projects/diagram-compactness/artifacts/reviews/20261004-compaction-plantuml-contract-luna-2-native/browser.json",
                     "exactCommandsIndependentlyMatched": True,
                     "exactCommandHarnessOption": manifest["eventPolicy"]["requireExactCommandFromPrompt"]})
data["runs"].sort(key=lambda row: row["id"])
target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"run": name, "passed": result["passed"], "payload": manifest["skill"]["payloadSha256"]}))
