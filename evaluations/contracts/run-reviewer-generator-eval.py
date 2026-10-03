#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the standard skill harness with contained temporary files and Git discovery."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from reviewer_harness_environment import install


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    helper = root / "scripts/run-pi-skill-eval.py"
    spec = importlib.util.spec_from_file_location("contained_reviewer_harness", helper)
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    install(harness)
    sys.argv = [str(helper), "repository-reviewer-creator", *sys.argv[1:]]
    return harness.main()


if __name__ == "__main__":
    sys.exit(main())
