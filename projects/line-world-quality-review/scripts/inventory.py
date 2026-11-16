#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory this conversation's video versions and inspect actual encoded frames."""
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parents[1]
NAMES = ['ml-overfitting-vids', 'cuda-alexnet-vids', 'seal-paper-vids', 'reddit-navigation-video', 'line-world-video']


def main():
    output = PROJECT / 'artifacts'; output.mkdir(parents=True, exist_ok=True)
    paths = [p for name in NAMES for p in (REPO / 'projects' / name / 'artifacts/videos').glob('*.mp4')]
    paths += [REPO / 'projects/line-world-video/artifacts' / name / (name + '.mp4') for name in ['focus-motion-demo', 'photo-focus-demo']]
    records = []
    for p in paths:
        if not p.is_file(): continue
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)], text=True))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        records.append({'path': p.relative_to(REPO).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'seconds': float(probe['format']['duration']), 'frames': int(video.get('nb_frames', 0)), 'width': video['width'], 'height': video['height'], 'fps': video['r_frame_rate'], 'audio': any(s['codec_type'] == 'audio' for s in probe['streams']), 'bytes': p.stat().st_size})
    (output / 'inventory-current.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files':len(records),'uniqueDigests':len({r['sha256'] for r in records}),'output':str(output/'inventory-current.json')}))


if __name__ == '__main__': main()
