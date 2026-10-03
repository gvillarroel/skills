#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Audit canonical skills and actual isolated-runtime/full bundle copies."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUTHORING = load_module("skill_authoring", ROOT / "skills/repository-reviewer-creator/scripts/check_skill_authoring.py")
RUNNER = load_module("authoring_bundle_runner", ROOT / "scripts/run-pi-skill-eval.py")
VALIDATOR = load_module("authoring_structural_validator", ROOT / "scripts/validate-skills.py")


def source_snapshot(skill: Path) -> dict:
    """Hash only authored files eligible for a full copy, avoiding dependency trees."""
    snapshot = {}
    for current, directories, filenames in os.walk(skill):
        directories[:] = sorted(name for name in directories if name not in RUNNER.COPY_IGNORE)
        for name in sorted(filenames):
            if name in RUNNER.COPY_IGNORE:
                continue
            path = Path(current) / name
            if path.suffix.lower() in RUNNER.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            snapshot[path.relative_to(skill).as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": RUNNER.sha256_file(path)}
    return snapshot


def check_bundle(skill: Path, profile: str) -> dict:
    report = AUTHORING.check_skill(skill, profile=profile)
    findings = []
    VALIDATOR.validate_skill_dir(skill, ROOT, findings, profile=profile)
    # The repository validator includes authoring checks. Preserve one copy of
    # those diagnostics and add its independent structural/resource checks.
    report["issues"].extend({"code": "bundle-structure", "path": finding.path.relative_to(skill).as_posix(), "message": finding.message} for finding in findings if not finding.message.startswith("authoring/"))
    report["passed"] = not report["issues"]
    return report


def audit(skills: Path, *, bundles: bool, temporary_parent: Path) -> dict:
    results = []
    sources = sorted(skill for skill in skills.iterdir() if skill.is_dir() and skill.name not in AUTHORING.IGNORED_DIRS)
    initial = {skill.name: source_snapshot(skill) for skill in sources}
    source_results = {}
    for skill in sources:
        before = initial[skill.name]
        source = check_bundle(skill, "source")
        source["profile"] = "source"
        source["fileCount"] = len(before)
        source["payloadSha256"] = RUNNER.snapshot_digest(before)
        results.append(source)
        source_results[skill.name] = source
        if bundles:
            temporary_parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="authoring-bundle-", dir=temporary_parent) as temporary:
                for profile in ("runtime", "full"):
                    destination = Path(temporary) / profile / skill.name
                    destination.parent.mkdir()
                    RUNNER.copy_skill_only(skill, destination, profile)
                    copied = check_bundle(destination, profile)
                    copied["profile"] = profile
                    snapshot = RUNNER.snapshot_tree(destination)
                    copied["fileCount"] = len(snapshot)
                    copied["payloadSha256"] = RUNNER.snapshot_digest(snapshot)
                    expected = {path: info for path, info in before.items() if profile == "full" or not path.startswith("assets/examples/")}
                    if snapshot != expected:
                        copied["issues"].append({"code": "bundle-copy-mismatch", "path": ".", "message": "Copied files do not match the exact source profile snapshot"})
                        copied["passed"] = False
                    results.append(copied)
    # Check the entire frozen inventory at completion. A later skill's copy
    # must not conceal edits to a skill that was already checked earlier.
    for skill in sources:
        source = source_results[skill.name]
        if source_snapshot(skill) != initial[skill.name]:
            source["issues"].append({"code": "source-changed", "path": ".", "message": "Source changed while being audited; rerun after authoring finishes"})
            source["passed"] = False
    final_names = {skill.name for skill in skills.iterdir() if skill.is_dir() and skill.name not in AUTHORING.IGNORED_DIRS}
    if set(initial) != final_names and source_results:
        source = next(iter(source_results.values()))
        source["issues"].append({"code": "source-inventory-changed", "path": ".", "message": f"Skill inventory changed during the audit: added={sorted(final_names-set(initial))}, removed={sorted(set(initial)-final_names)}"})
        source["passed"] = False
    counts = Counter(issue["code"] for result in results for issue in result["issues"])
    return {"schemaVersion": 1, "passed": bool(results) and not counts, "skillCount": len({result["skill"] for result in results}), "bundleCount": sum(result["profile"] != "source" for result in results), "issueCounts": dict(sorted(counts.items())), "results": results, "limitations": "Measurable authoring/navigation and copied payloads; no claim of model-wide behavioral certification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", type=Path, default=ROOT / "skills")
    parser.add_argument("--check-bundles", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.skills.is_dir():
        parser.error(f"Skill source directory does not exist: {args.skills}")
    report = audit(args.skills.resolve(), bundles=args.check_bundles, temporary_parent=ROOT / "evaluations/runs/skill-authoring-bundles")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    if not args.output:
        for result in report["results"]:
            for issue in result["issues"]:
                print(f"- {result['skill']} ({result['profile']})/{issue['path']}: {issue['message']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
