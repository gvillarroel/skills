#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the reviewed pan-first visual revision without changing speech or timing."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    story_path = ROOT / 'story.json'; source = json.loads(story_path.read_text(encoding='utf-8'))
    before = ROOT / 'artifacts/reviews/pan-before'; before.mkdir(parents=True, exist_ok=True)
    if not (before / 'story.json').exists(): shutil.copyfile(story_path, before / 'story.json')
    movie = ROOT / 'artifacts/videos/seal-google-vids-final.mp4'
    old_movie = ROOT / 'artifacts/videos/seal-google-vids-before-pan.mp4'
    if movie.exists() and not old_movie.exists(): shutil.copyfile(movie, old_movie)
    for scene in source['scenes']:
        scene['emphasis'] = 'margin'
        if scene['id'] in ('method', 'knowledge', 'few-shot'):
            scene['camera'] = {'mode': 'pan', 'zoom': 1.3, 'enterSeconds': 2.6,
                               'travelSeconds': 2, 'minTravelSeconds': 1.4,
                               'minHoldSeconds': 1.1, 'maxPanSpeed': 540}
        if scene['id'] == 'limits':
            scene['shots'] = [shot for shot in scene['shots'] if shot['at'] != 19.0]
            scene['shots'][0]['view'] = [103, 187, 510, 366]
    previous = json.loads((before / 'story.json').read_text(encoding='utf-8'))
    assert [(s['id'], s['duration'], s['script'], s['cues']) for s in source['scenes']] == [(s['id'], s['duration'], s['script'], s['cues']) for s in previous['scenes']]
    story_path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'speechAndTimingUnchanged': True,
                      'camera': 'One gentle entry, then fixed-scale pans; no per-cue zoom reset.',
                      'emphasis': 'Obstacle-checked margin marks; no rectangular overlay.',
                      'limits': 'Both page-9 limitations share a stable original-page view.'}))


if __name__ == '__main__': main()
