#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Extract bounded encoded reading poses for the maintained Line World examples."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parents[1]
ENTRIES = [
    ('ml', 'ml-overfitting-vids', 'ml-overfitting-subject-first-local.mp4', 'story.json'),
    ('cuda', 'cuda-alexnet-vids', 'cuda-alexnet-reusable-local.mp4', 'story.json'),
    ('seal', 'seal-paper-vids', 'seal-paper-subject-first-local.mp4', 'story.json'),
    ('reddit', 'reddit-navigation-video', 'reddit-navigation.mp4', 'story.json'),
    ('linked', 'line-world-video', 'line-world-solid-linked.mp4', 'artifacts/solid-linked/story.json'),
    ('atlas', 'line-world-video', 'line-world-solid-atlas.mp4', 'artifacts/solid-atlas/story.json')]


def main():
    root = PROJECT / 'artifacts/baseline'; root.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=18)
    for identity, project_name, video_name, story_name in ENTRIES:
        project = REPO / 'projects' / project_name
        story = json.loads((project / story_name).read_text(encoding='utf-8-sig'))
        scenes = story.get('scenes', story.get('beats')); cursor = 0; poses = []
        if not scenes and (project / story_name).with_name('timing.json').is_file():
            scenes = json.loads((project / story_name).with_name('timing.json').read_text(encoding='utf-8'))['beats']
        if not scenes: raise ValueError('No authored scene/beat clock: ' + story_name)
        for i, scene in enumerate(scenes):
            duration = scene.get('clipSeconds', scene.get('duration'))
            start = scene.get('start', cursor); poses.append({'id': scene.get('id', str(i)), 'at': start + duration * .65})
            cursor = start + duration
        folder = root / identity; folder.mkdir(exist_ok=True)
        frames = [round(p['at'] * 30) for p in poses]
        pattern = folder / 'reading-%02d.png'
        selection = '+'.join('eq(n\\,' + str(frame) + ')' for frame in frames)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(project / 'artifacts/videos' / video_name), '-vf', 'select=' + selection, '-fps_mode', 'vfr', str(pattern)], check=True)
        sheet = Image.new('RGB', (1920, ((len(poses) + 2) // 3) * 390), 'white'); draw = ImageDraw.Draw(sheet)
        for i, pose in enumerate(poses):
            x, y = i % 3 * 640, i // 3 * 390
            image = Image.open(folder / f'reading-{i+1:02}.png'); image.thumbnail((640, 360)); sheet.paste(image, (x, y))
            draw.text((x + 8, y + 365), f"{pose['at']:.2f}s / {pose['id']}", font=font, fill='#333e48')
        sheet.save(folder / 'contact.jpg', quality=95)
        (folder / 'poses.json').write_text(json.dumps(poses, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'id': identity, 'scenes': len(poses), 'seconds': cursor, 'contact': str(folder / 'contact.jpg')}), flush=True)


if __name__ == '__main__': main()
