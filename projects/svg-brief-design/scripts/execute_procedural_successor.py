#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Use the frozen runner at a shorter, independently probed run root."""
from pathlib import Path
import execute_procedural_generation as runner

if __name__ == "__main__":
    runner.ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp2"
    raise SystemExit(runner.main())
