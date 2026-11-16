#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Use repository synchronization helpers for this skill alone."""
import runpy
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[3]
helper = runpy.run_path(str(root / "scripts/sync-local-skills.py"))
for name in ('line-world-video','line-world-google-vids'):
    source = root / 'skills' / name
    destination = root / '.agents/skills' / name
    if not helper['validate_bundles']([source]):raise SystemExit(1)
    pending = helper['pending_files'](source, destination)
    for original, installed in pending:
        installed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, installed)
    if helper['pending_files'](source, destination) or not helper['validate_bundles']([destination]):raise SystemExit(1)
    print(f"Synchronized {name}: verified {len(helper['source_files'](source))} canonical files; {len(pending)} files changed.")
