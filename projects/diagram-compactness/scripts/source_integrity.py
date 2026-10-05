#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Hash live canonical runtime files using the isolated harness's exact policy."""
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("compactness_runtime_harness", ROOT / "scripts/run-pi-skill-eval.py")
HARNESS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(HARNESS)


def runtime_digest(skill: str) -> str:
    bundle = ROOT / "skills" / skill
    if not bundle.is_dir() or not bundle.resolve().is_relative_to((ROOT / "skills").resolve()):
        raise ValueError(f"Unknown canonical skill: {skill}")
    snapshot = {}
    for current, directories, filenames in os.walk(bundle):
        parent = Path(current)
        directories[:] = sorted(name for name in directories
                                if name not in HARNESS.COPY_IGNORE
                                and (parent / name).relative_to(bundle) not in HARNESS.RUNTIME_EXCLUDED_DIRS)
        for name in sorted(filenames):
            path = parent / name
            if name in HARNESS.COPY_IGNORE or path.suffix.lower() in HARNESS.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            snapshot[path.relative_to(bundle).as_posix()] = {"sizeBytes": path.stat().st_size,
                                                            "sha256": HARNESS.sha256_file(path)}
    return HARNESS.snapshot_digest(snapshot)
