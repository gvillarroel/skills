#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a frozen Harbor task subset with source and task digests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task-id", action="append", required=True)
    parser.add_argument("--reason", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    task_ids = list(dict.fromkeys(args.task_id))
    if len(task_ids) != len(args.task_id):
        raise SystemExit("Task IDs must be unique.")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item) for item in task_ids):
        raise SystemExit("Task IDs must be lowercase hyphen-case.")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    task_digests: dict[str, str] = {}
    for task_id in task_ids:
        task = source / task_id
        for required in ("instruction.md", "task.toml", "environment", "tests"):
            if not (task / required).exists():
                raise SystemExit(f"Task {task_id} is missing {required}.")
        destination = output / task_id
        shutil.copytree(task, destination)
        task_digests[task_id] = tree_digest(destination)

    manifest = {
        "schemaVersion": 1,
        "source": str(source),
        "sourceSha256": tree_digest(source),
        "reason": args.reason,
        "taskCount": len(task_ids),
        "taskIds": task_ids,
        "taskDigests": task_digests,
    }
    (output / "selection-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
