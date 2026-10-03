#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Independently inspect generated structure, source citations, and input integrity."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("fixture", choices=["tenant", "export"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("reviewer_validator", root / "skills/repository-reviewer-creator/scripts/validate_reviewer.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = json.loads((root / "skills/repository-reviewer-creator/assets/examples/reviewer-fixtures/fixtures.json").read_text(encoding="utf-8"))[args.fixture]
    workspace = args.run / "workspace"
    reviewer = workspace / "generated" / f"{fixture['slug']}-reviewer"
    structure = module.validate(reviewer)
    problems = list(structure["errors"])
    input_root = workspace / "input-repo"
    for name, expected in fixture["files"].items():
        path = input_root / name
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            problems.append(f"Input source changed or missing: {name}")
    extras = []
    if input_root.is_dir():
        extras = [p.relative_to(input_root).as_posix() for p in input_root.rglob("*") if p.is_file() and p.relative_to(input_root).as_posix() not in fixture["files"]]
    if extras:
        problems.append(f"Unexpected writes in input snapshot: {extras}")
    profile_path = reviewer / "references/repository-profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8")) if profile_path.is_file() else {}
    cited_paths = []
    for source in profile.get("sources", []):
        if source.get("status") != "read":
            continue
        location = source.get("location", "").split("#", 1)[0]
        if location.startswith("input-repo/"):
            location = location[len("input-repo/"):]
        if location not in fixture["files"]:
            problems.append(f"Inspected citation is not a supplied source: {location}")
        else:
            cited_paths.append(location)
    report = {
        "passed": not problems,
        "problems": problems,
        "structure": structure,
        "cited_paths": cited_paths,
        "input_extra_files": extras,
        "human_content_review_required": True,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
