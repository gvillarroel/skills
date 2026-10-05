#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize retained compactness trials without dumping full event traces."""
from pathlib import Path
import json
import sys
import os

prefix = sys.argv[1] if len(sys.argv) > 1 else ""

root = Path(__file__).resolve().parents[3]
for run in sorted(p for p in (root / "evaluations/runs").iterdir()
                  if "compact" in p.name and "20261004" in p.name and p.name.startswith(prefix)):
    manifest = run / "run-manifest.json"
    if not manifest.exists():
        continue
    data = json.loads(manifest.read_text(encoding="utf-8"))
    result_path = run / "evaluation-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
    events = run / "events.jsonl"
    records = []
    if events.exists():
        for line in events.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    errors = sorted({
        str(record.get("message", {}).get("errorMessage"))
        for record in records if isinstance(record, dict)
        and record.get("message", {}).get("errorMessage")
    })
    authored = []
    if not result:
        for parent, dirs, files in os.walk(run / "workspace"):
            dirs[:] = [d for d in dirs if d not in {"skills", "node_modules", ".git"}]
            authored.extend((Path(parent) / name).relative_to(run / "workspace").as_posix()
                            for name in files)
            if len(authored) >= 20:
                authored = authored[:20]
                break
    print(json.dumps({"run": run.name, "skill": data["skill"]["name"],
                      "model": data["pi"]["model"], "result": result,
                      "errors": errors, "pendingArtifacts": authored}, ensure_ascii=True))
