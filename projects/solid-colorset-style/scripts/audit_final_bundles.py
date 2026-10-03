#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6"]
# ///
"""Audit current sources and reuse copied-bundle checks only by exact payload digest."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts/reviews"
SPEC = importlib.util.spec_from_file_location("bundle_audit", ROOT / "scripts/audit-skill-authoring.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def main():
    caches = []
    for path in ART.glob("skill-authoring-audit*.json"):
        if path.name == "skill-authoring-audit-final-current.json":
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        caches.extend((path.relative_to(ROOT).as_posix(), row) for row in report["results"]
                      if row["profile"] in {"runtime", "full"} and row["passed"])
    sources = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir() and path.name not in AUDIT.AUTHORING.IGNORED_DIRS)
    initial = {path.name: AUDIT.source_snapshot(path) for path in sources}

    def check(skill):
        before = initial[skill.name]
        source = AUDIT.check_bundle(skill, "source")
        source.update(profile="source", fileCount=len(before), payloadSha256=AUDIT.RUNNER.snapshot_digest(before), evidenceType="fresh-source-check")
        results = [source]
        for profile in ("runtime", "full"):
            expected = {name: value for name, value in before.items() if profile == "full" or not name.startswith("assets/examples/")}
            digest = AUDIT.RUNNER.snapshot_digest(expected)
            matching = [(path, row) for path, row in caches if row["skill"] == skill.name and row["profile"] == profile and row["payloadSha256"] == digest and row["fileCount"] == len(expected)]
            if matching:
                path, prior = matching[-1]
                copied = dict(prior, evidenceType="exact-digest-copied-check-reused", validationReport=path)
            else:
                parent = ROOT / "evaluations/runs/skill-authoring-bundles"
                parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(prefix="final-current-", dir=parent) as temporary:
                    destination = Path(temporary) / skill.name
                    AUDIT.RUNNER.copy_skill_only(skill, destination, profile)
                    copied = AUDIT.check_bundle(destination, profile)
                    actual = AUDIT.RUNNER.snapshot_tree(destination)
                    copied.update(profile=profile, fileCount=len(actual), payloadSha256=AUDIT.RUNNER.snapshot_digest(actual), evidenceType="fresh-copied-check")
                    if actual != expected:
                        copied["issues"].append({"code": "bundle-copy-mismatch", "path": ".", "message": "Copied files differ from current profile snapshot"})
                        copied["passed"] = False
            results.append(copied)
        return results

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = [row for group in pool.map(check, sources) for row in group]
    final_names = sorted(path.name for path in (ROOT / "skills").iterdir()
                         if path.is_dir() and path.name not in AUDIT.AUTHORING.IGNORED_DIRS)
    if final_names != [path.name for path in sources]:
        results[0]["issues"].append({"code": "source-inventory-changed", "path": ".",
                                     "message": "Skill inventory changed during final audit"})
        results[0]["passed"] = False
    for source in sources:
        if AUDIT.source_snapshot(source) != initial[source.name]:
            row = next(row for row in results if row["skill"] == source.name and row["profile"] == "source")
            row["issues"].append({"code": "source-changed", "path": ".", "message": "Source changed during final audit"})
            row["passed"] = False
    counts = Counter(issue["code"] for row in results for issue in row["issues"])
    report = {"date": "2026-10-03", "passed": bool(results) and not counts,
              "skillCount": len(sources), "bundleCount": 2 * len(sources),
              "reusedCopiedChecks": sum(row["evidenceType"] == "exact-digest-copied-check-reused" for row in results),
              "issueCounts": dict(counts), "results": results,
              "scope": "Fresh current-source checks plus copied-profile validations. Prior successful copies are reused only when every current file size/hash yields the identical profile digest. All changed profiles are recopied and revalidated. Full source snapshots are checked again at completion; committed CI independently runs all fresh copies."}
    target = ART / "skill-authoring-audit-final-current.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    compact = {key: value for key, value in report.items() if key not in {"results"}}
    (ROOT / "evaluations/solid-colorset-style/bundle-audit-20261003.json").write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(compact, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
