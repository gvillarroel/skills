#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Remove only disposable `_wsl-root` trees from one completed Harbor job."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import stat
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_directory", type=Path)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def retry_read_only(function, path, _error) -> None:
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    function(path)


def main() -> int:
    args = parse_args()
    job = args.job_directory.resolve(strict=True)
    repo = Path(__file__).resolve().parents[2]
    allowed = (repo / "evaluations" / "runs").resolve(strict=True)
    if not job.is_relative_to(allowed):
        raise SystemExit(f"Job is outside evaluations/runs: {job}")
    for required in ("config.json", "lock.json", "result.json"):
        if not (job / required).is_file():
            raise SystemExit(f"Completed Harbor job marker is missing: {required}")

    targets: list[Path] = []
    for trial in sorted(path for path in job.iterdir() if path.is_dir()):
        target = trial / "_wsl-root"
        if not target.exists():
            continue
        resolved_trial = trial.resolve(strict=True)
        if resolved_trial.parent != job or target.name != "_wsl-root":
            raise SystemExit(f"Refusing unexpected cleanup target: {target}")
        targets.append(target)

    for target in targets:
        print(f"{'REMOVE' if args.execute else 'WOULD_REMOVE'} {target}")
        if args.execute:
            shutil.rmtree(target, onexc=retry_read_only)
    print(f"target_count={len(targets)} executed={str(args.execute).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
