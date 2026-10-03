#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Rebuild accepted earlier plans with the final native builders, without altering trials."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    scripts = args.skill_root.resolve() / "scripts"
    records = []
    for suffix in ("native-contract-1", "color-transfer-1", "color-transfer-3", "json-naturalistic-1"):
        run_id = "diagram-composition-20260928-" + suffix
        source = args.runs / run_id / "workspace" / "out" / "plan.json"
        target = args.output.resolve() / suffix
        target.mkdir(parents=True, exist_ok=True)
        brief = target / "brief.json"
        brief.write_bytes(source.read_bytes())
        commands = [
            ["build_panels.py", "--spec", brief, "--output-spec", target / "plan.json", "--report", target / "build.json"],
            ["compose_diagram.py", "compose", "--spec", target / "plan.json", "--output", target / "figure.svg", "--report", target / "report.json"],
            ["audit_diagram.py", "audit", "--input", target / "figure.svg", "--report", target / "audit.json", "--screenshot", target / "preview.png"],
        ]
        for command in commands:
            subprocess.run(["uv", "run", "--script", str(scripts / command[0]),
                            *map(str, command[1:]), "--overwrite"], check=True, capture_output=True)
        audit = json.loads((target / "audit.json").read_text(encoding="utf-8"))
        original_sha = hashlib.sha256((source.parent / "figure.svg").read_bytes()).hexdigest()
        unchanged = original_sha == audit["sourceSha256"]
        records.append({"sourceRun": run_id, "inputPlanSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "sourceSvgSha256": audit["sourceSha256"], "originalSvgSha256": original_sha,
                        "byteIdentical": unchanged, "ok": audit["ok"] and unchanged,
                        "minimumObservedPx": audit["minimumObservedPx"], "issues": audit["issues"]})
    (args.output / "summary.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records))
    raise SystemExit(0 if all(record["ok"] for record in records) else 1)


if __name__ == "__main__":
    main()
