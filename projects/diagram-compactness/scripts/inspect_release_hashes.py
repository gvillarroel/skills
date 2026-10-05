#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare retained release manifests with the final standalone-bundle audit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
audit = json.loads((ROOT / "projects/diagram-compactness/artifacts/reviews/final-authoring-audit.json").read_text(encoding="utf-8"))
current = {row["skill"]: row["payloadSha256"] for row in audit["results"] if row["profile"] == "runtime"}
data = json.loads((ROOT / "evaluations/diagram-compactness/renderers-20261004.json").read_text(encoding="utf-8"))
for row in data["runs"]:
    if row.get("finalCohort"):
        skill = row["skill"]["name"]
        print(json.dumps({"run": row["id"], "passed": row["result"]["passed"],
                          "runtimeHash": row["skill"]["payloadSha256"],
                          "currentRuntimeHash": current[skill],
                          "currentSource": row["skill"]["payloadSha256"] == current[skill]}))
