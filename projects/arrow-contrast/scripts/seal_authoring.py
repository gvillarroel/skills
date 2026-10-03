#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact source/runtime/full-copy checks with their detailed evidence hash."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("raced", "raced-late", "superseded", "pre-gallery", "pre-contact-sheet", "final"), required=True)
    args = parser.parse_args()
    source = ROOT / "projects/arrow-contrast/artifacts/reviews/skill-authoring-audit-final.json"
    data = source.read_bytes()
    result = json.loads(data)
    detailed = source
    if args.phase != "final":
        detailed = source.with_name(f"skill-authoring-audit-{args.phase}.json")
        detailed.write_bytes(data)
    report = {key: result[key] for key in ("schemaVersion", "passed", "skillCount", "bundleCount", "issueCounts", "limitations")}
    report.update(date="2026-10-03", phase=args.phase,
                  command=["uv", "run", "--script", "scripts/audit-skill-authoring.py", "--check-bundles", "--output", "projects/arrow-contrast/artifacts/reviews/skill-authoring-audit-final.json"],
                  detailedEvidence={"path": detailed.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "sizeBytes": len(data)},
                  results=[{key: row[key] for key in ("skill", "profile", "passed", "fileCount", "payloadSha256", "issues")} for row in result["results"]])
    if args.phase.startswith("raced"):
        report["classification"] = "Snapshot invalidated by active source edits; retained, never accepted as final evidence."
    elif args.phase in {"superseded", "pre-gallery", "pre-contact-sheet"}:
        report["classification"] = "Passing snapshot retained, superseded by subsequent concrete source repairs."
    destination = ROOT / f"evaluations/arrow-contrast/authoring-{args.phase}-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": args.phase, "passed": result["passed"], "sourceCount": result["skillCount"], "copyCount": result["bundleCount"], "issueCounts": result["issueCounts"]}, indent=2))
    if args.phase == "final" and not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
