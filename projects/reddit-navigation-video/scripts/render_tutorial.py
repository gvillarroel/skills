#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh the owned composition from editable inputs and cached narration."""
import argparse
import copy
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--audit-only', action='store_true'); args = parser.parse_args()
    skill = ROOT / 'tools/line-world-video'
    if not skill.is_dir(): skill = ROOT.parents[1] / 'skills/line-world-video'
    composition = ROOT / 'artifacts/composition'; composition.mkdir(parents=True, exist_ok=True)
    story = copy.deepcopy(json.loads((ROOT / 'story.json').read_text(encoding='utf-8')))
    for scene in story['scenes']:
        for field, folder in [('capture', 'media'), ('audio', 'audio')]:
            original = (ROOT / scene[field]).resolve()
            if not original.is_relative_to(ROOT): raise ValueError('Keep source files inside the project.')
            destination = composition / folder / original.name; destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(original, destination)
            scene[field] = destination.relative_to(composition).as_posix()
    request = composition / 'story.json'; request.write_text(json.dumps(story, indent=2) + '\n', encoding='utf-8')
    subprocess.run(['uv', 'run', '--script', str(skill / 'scripts/website_video.py'), 'build', '--project', str(composition), '--story', str(request)], check=True)
    command = ['uv', 'run', '--script', str(skill / 'scripts/website_video.py'), 'render', '--project', str(composition), '--output', str(ROOT / 'artifacts/videos/reddit-navigation.mp4'), '--report', str(ROOT / 'artifacts/reviews/render.json'), '--poster', str(ROOT / 'artifacts/images/poster.png')]
    if args.audit_only: command.append('--audit-only')
    subprocess.run(command, check=True)


if __name__ == '__main__': main()
