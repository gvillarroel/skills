#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Remove only regenerable dependencies from completed compactness trials."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[3]
RUNS = (ROOT / "evaluations/runs").resolve()
PRESERVED = ("compact-slidev-quality-audit-20261004-preparation-release",
             "compact-slidev-quality-audit-20261004-trial-release",
             "compact-slidev-echarts-20261004-sol-capture-final")


def candidates() -> list[Path]:
    found = []
    for run in RUNS.iterdir():
        if not run.is_dir() or not (run / "evaluation-result.json").is_file():
            continue
        if not ((run.name.startswith("compact-") and "-20261004-" in run.name)
                or run.name.startswith("20261004-compaction-")
                or run.name.startswith("20261004-diagram-compact-")
                or run.name.startswith("20261004-composition-compactness-")):
            continue
        if any(run.name.startswith(prefix) for prefix in PRESERVED):
            continue
        workspace = (run / "workspace").resolve()
        if not workspace.is_relative_to(RUNS) or not workspace.is_dir():
            continue
        for relative in ("node_modules", "deck/node_modules", "out/node_modules"):
            path = workspace / relative
            resolved = path.resolve()
            if (path.is_dir() and not path.is_symlink() and resolved.is_relative_to(workspace)
                    and resolved.is_relative_to(RUNS) and "skills" not in path.relative_to(workspace).parts):
                found.append(path)
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    paths = candidates()
    report = {"applied": args.apply, "freeBeforeBytes": shutil.disk_usage(ROOT).free,
              "paths": [str(path.relative_to(ROOT)) for path in paths], "removed": [], "errors": []}
    if args.apply:
        for path in paths:
            # Recheck absolute boundaries immediately before each recursive delete.
            resolved = path.resolve()
            workspace = next(parent for parent in path.parents if parent.name == "workspace")
            if path.is_symlink() or not resolved.is_relative_to(workspace.resolve()) or not resolved.is_relative_to(RUNS):
                raise ValueError(f"Dependency target escaped the completed trial workspace: {path}")
            try:
                shutil.rmtree(path)
                report["removed"].append(str(path.relative_to(ROOT)))
            except OSError as error:
                report["errors"].append({"path": str(path.relative_to(ROOT)), "reason": str(error)})
    report["freeAfterBytes"] = shutil.disk_usage(ROOT).free
    output = ROOT / "projects/diagram-compactness/artifacts/reviews/dependency-cleanup.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"paths", "removed"}}))
    print(json.dumps({"candidateCount": len(paths), "removedCount": len(report["removed"]), "report": str(output)}))
    return int(bool(report["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
