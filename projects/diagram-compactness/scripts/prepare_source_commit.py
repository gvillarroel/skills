#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Review and optionally stage only this revision's explicitly owned sources."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
SKILLS = {"mermaid", "plantuml-colorset-renderer", "usefulcharts-style", "d3",
          "svg-brief-design", "procedural-svg-animation", "diagram-composition",
          "compose-synchronized-svg", "threejs-animated-3d", "hyperframes-explainer",
          "video", "slidev-animejs", "slidev-echarts", "echarts-animated-svg",
          "slidev-quality-audit"}
EXCLUDED = {
    "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html",
    "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs",
}


def git_paths(*command: str) -> list[str]:
    output = subprocess.run(["git", *command], cwd=ROOT, check=True,
                            capture_output=True).stdout.decode("utf-8")
    return [path.replace("\\", "/") for path in output.split("\0") if path]


def owner(path: str) -> str | None:
    if path in EXCLUDED:
        return None
    if path == "SKILLS.md":
        return "backlog"
    parts = Path(path).parts
    if len(parts) > 2 and parts[0] == "skills" and parts[1] in SKILLS:
        return "canonical"
    if path.startswith("evaluations/diagram-compactness/") and Path(path).suffix in {".md", ".json"}:
        return "evaluation"
    if path.startswith("evaluations/pi-prompts/") and any(Path(path).name.startswith(prefix)
             for prefix in ("compactness-composition-", "diagram-compact-", "diagram-compaction-", "diagram-compactness-")):
        return "prompt"
    if path.startswith("projects/diagram-compactness/scripts/") and Path(path).suffix in {".py", ".ts", ".mjs"}:
        return "project-script"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    paths = sorted(set(git_paths("diff", "--name-only", "-z"))
                   | set(git_paths("diff", "--cached", "--name-only", "-z"))
                   | set(git_paths("ls-files", "--others", "--exclude-standard", "-z")))
    candidates, preserved = [], []
    for relative in paths:
        category = owner(relative)
        if not category:
            preserved.append(relative)
            continue
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or any(part in {"node_modules", "__pycache__", "artifacts", "runs"} for part in Path(relative).parts):
            raise ValueError(f"Unsafe or generated staging candidate: {relative}")
        payload = path.read_bytes()
        candidates.append({"path": relative, "category": category, "bytes": len(payload),
                           "sha256": hashlib.sha256(payload).hexdigest()})
    candidate_paths = [item["path"] for item in candidates]
    if args.stage:
        existing = git_paths("diff", "--cached", "--name-only", "-z")
        if any(path not in candidate_paths for path in existing):
            raise ValueError("Existing staged changes include files outside this revision.")
        subprocess.run(["git", "add", "--", *candidate_paths], cwd=ROOT, check=True)
        staged = sorted(git_paths("diff", "--cached", "--name-only", "-z"))
        if staged != candidate_paths:
            raise ValueError("The staged diff does not match the exact reviewed candidate list.")
        subprocess.run(["git", "diff", "--cached", "--check"], cwd=ROOT, check=True)
    counts = {category: sum(item["category"] == category for item in candidates)
              for category in sorted({item["category"] for item in candidates})}
    report = {"candidatePaths": candidate_paths, "candidates": candidates, "counts": counts,
              "preservedPaths": preserved, "staged": args.stage}
    output = ROOT / "projects/diagram-compactness/artifacts/reviews/final-staging-manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidateCount": len(candidates), "counts": counts, "preservedPaths": preserved,
                      "staged": args.stage, "manifest": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
