#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seed only declared raw task inputs, then run the repository's isolated harness."""
from pathlib import Path
import importlib.util
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('isolated_harness',REPO/'scripts/run-pi-skill-eval.py')
harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
original=harness.copy_skill_only
def copy_with_inputs(source,target,profile):
    original(source,target,profile)
    shutil.copytree(ROOT/'artifacts/evaluation-input',target.parent.parent/'input')
harness.copy_skill_only=copy_with_inputs
if __name__=='__main__':raise SystemExit(harness.main())
