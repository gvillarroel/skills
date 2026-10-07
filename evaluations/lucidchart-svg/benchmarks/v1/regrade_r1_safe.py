#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Guard the aggregate destination before delegating to the unchanged sealed R1.

Run: uv run --script regrade_r1_safe.py --report evaluations/runs/NEW.json
Historical reports must remain absent for a fresh regrade; no trial is resampled.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true", help="Validate destination without running the sealed regrader")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    revision = Path(__file__).resolve().parent / "verifier-revisions" / "r1"
    manifest = json.loads((revision / "correction-manifest.json").read_text(encoding="utf-8"))
    report = args.report.resolve()
    if not report.is_relative_to(root / "evaluations" / "runs") or report.exists():
        parser.error("Use a fresh aggregate file under ignored evaluations/runs")
    for subject in manifest["subjects"]:
        if report.is_relative_to((root / subject["workspace"]).resolve()):
            parser.error("Aggregate reports must remain outside every evaluated workspace")
    if args.check_only:
        print(json.dumps({"destination_allowed": True, "writes_performed": False, "report": str(report)}))
        return 0
    return subprocess.run([sys.executable, str(revision / "regrade_cohort.py"), "--report", str(report)], check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
