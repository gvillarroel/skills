#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Stage sealed owned gallery blobs without modifying unrelated working drafts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PATHS = {
    "builder": "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs",
    "gallery": "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html",
}


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, input=data, capture_output=True, check=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in PATHS:
        parser.add_argument(f"--{name}", type=Path, required=True)
        parser.add_argument(f"--{name}-sha256", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    rows = []
    for name, target in PATHS.items():
        source = getattr(args, name).resolve()
        if not source.is_relative_to(ROOT / "projects/colorset-priority/artifacts"):
            raise ValueError("Sealed sources must remain in this project's ignored artifacts.")
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != getattr(args, name + "_sha256"):
            raise ValueError(f"The sealed {name} artifact no longer matches its reviewed hash.")
        if b"\r" in data or not data.endswith(b"\n") or data.endswith(b"\n\n"):
            raise ValueError("Sealed gallery sources require LF and exactly one final LF.")
        working_before = hashlib.sha256((ROOT / target).read_bytes()).hexdigest()
        object_id = git("hash-object", "-w", "--stdin", data=data).decode().strip()
        if args.apply:
            git("update-index", "--cacheinfo", "100644", object_id, target)
            if git("show", ":" + target) != data:
                raise ValueError("Staged Git bytes differ from the reviewed artifact.")
        working_after = hashlib.sha256((ROOT / target).read_bytes()).hexdigest()
        if working_before != working_after:
            raise ValueError("The working draft changed during selective staging.")
        rows.append({"path": target, "sealedSha256": digest, "gitObject": object_id,
                     "workingDraftSha256": working_before, "workingDraftPreserved": True})
    result = {"applied": args.apply, "headBefore": git("rev-parse", "HEAD").decode().strip(), "resources": rows}
    report = ROOT / "projects/colorset-priority/artifacts/manifests/owned-gallery-staging.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
