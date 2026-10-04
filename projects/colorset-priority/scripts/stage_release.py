#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Stage explicit CS1 release paths while preserving unrelated working changes."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXCLUDED = {
    "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html",
    "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs",
}
FILES = {"SKILLS.md", "docs/colorsets.json", "docs/colorsets.md", "scripts/test-colorsets.py", "scripts/validate-colorsets.py", "evaluations/colorset-priority-20261004.md", "projects/plantuml-style-repair/scripts/verify_cs1_priority.py"}
PREFIXES = ("skills/", "evaluations/colorset-priority-20261004/", "projects/colorset-priority/scripts/")


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    current_index = git("diff", "--cached", "--name-only", "-z").decode().split("\0")
    if any(path and not allowed(path) for path in current_index):
        raise ValueError("Unrelated changes are already staged; preserve the index for review.")
    candidates = set(git("diff", "--name-only", "-z").decode().split("\0"))
    candidates.update(git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0"))
    paths = sorted(path for path in candidates if path and allowed(path))
    if args.apply:
        for offset in range(0, len(paths), 48):
            git("add", "--", *paths[offset:offset + 48])
    result = {"applied": args.apply, "pathCount": len(paths), "paths": paths, "preservedExcluded": sorted(EXCLUDED)}
    output = ROOT / "projects/colorset-priority/artifacts/manifests/staging.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "paths"}, indent=2))
    return 0


def allowed(path: str) -> bool:
    return path not in EXCLUDED and (path in FILES or path.startswith(PREFIXES))


if __name__ == "__main__":
    raise SystemExit(main())
