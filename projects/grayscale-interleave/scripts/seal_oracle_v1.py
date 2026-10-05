#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain the initial native oracle before correcting group metadata handling."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/grayscale-interleave/artifacts/reviews/oracle-v1"
OUT.mkdir(parents=True, exist_ok=False)
shutil.copy2(ROOT / "evaluations/grayscale-interleave/review_outputs.py", OUT / "review_outputs.py")
shutil.copy2(ROOT / "projects/grayscale-interleave/artifacts/reviews/forward-native/r1-results.json", OUT / "r1-results.json")
print("Retained the initial oracle and its complete observed report before amendment.")
