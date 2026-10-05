#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare a retained read-only trial bundle with canonical source files."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run_id")
parser.add_argument("skill")
args = parser.parse_args()
snapshot = ROOT / "evaluations/runs" / args.run_id / "workspace/skills" / args.skill
current = ROOT / "skills" / args.skill
snapshot.resolve().relative_to(ROOT)
current.resolve().relative_to(ROOT)
rows = []
for path in sorted(snapshot.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts:
        continue
    relative = path.relative_to(snapshot)
    target = current / relative
    before = path.read_bytes()
    after = target.read_bytes() if target.is_file() else b""
    if before == after:
        continue
    diff = []
    try:
        diff = list(difflib.unified_diff(before.decode("utf-8").splitlines(),
                                         after.decode("utf-8").splitlines(),
                                         fromfile="trial", tofile="current"))
    except UnicodeDecodeError:
        pass
    rows.append({"path": relative.as_posix(), "before": hashlib.sha256(before).hexdigest(),
                 "after": hashlib.sha256(after).hexdigest(), "diff": diff[:100]})
print(json.dumps({"run": args.run_id, "skill": args.skill, "changedFiles": rows}))
