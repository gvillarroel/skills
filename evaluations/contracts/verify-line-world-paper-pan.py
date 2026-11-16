#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Independently inspect source/encoded pan fixtures without importing the skill."""
import argparse
import functools
import hashlib
import http.server
import json
import os
import subprocess
import threading
from pathlib import Path
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def inspect(run):
    workspace = run / 'workspace'; film = workspace / 'film'; video = workspace / 'clips/01-method.mp4'
    failures = []
    def require(value, label):
        if not value: failures.append(label)
    story = json.loads((film / 'story.json').read_text(encoding='utf-8'))
    manifest = json.loads((film / 'paper.json').read_text(encoding='utf-8'))
    require(hashlib.sha256((film / 'source.pdf').read_bytes()).hexdigest() == manifest['pdfSha256'], 'original-pdf-digest')
    for page in manifest['pages']:
        require(hashlib.sha256((film / page['image']).read_bytes()).hexdigest() == page['sha256'], 'original-page-capture')
    require(story['scenes'][0]['id'] == 'method' and story['scenes'][0]['duration'] == 12, 'ordered-scene-clock')
    audit = json.loads((workspace / 'review/audit.json').read_text(encoding='utf-8'))
    require(audit['ok'] and not audit['scenes'][0]['findings'] and audit['scenes'][0]['trajectoryFrames'] == 360, 'complete-source-audit')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    visual = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    require(visual['width'] == 1920 and visual['height'] == 1080 and int(visual['nb_frames']) == 360, 'encoded-geometry-and-frames')
    require(abs(float(probe['format']['duration'])-12) < .05, 'encoded-duration')
    decoded = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], capture_output=True)
    require(decoded.returncode == 0 and not decoded.stderr.strip(), 'complete-encoded-decode')
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(film)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    bins = sorted((Path(os.environ.get('LOCALAPPDATA', '')) / 'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'), reverse=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=str(bins[0]) if bins else None, headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html?capture=1'); page.evaluate('async()=>await ready')
            states = page.evaluate('()=>Array.from({length:360},(_,n)=>renderClip(0,n/30))')
            require(not any(s['issues'] for s in states), 'all-frame-clearance')
            require(all(states[n]['camera']['k'] >= states[n-1]['camera']['k']-1e-5 for n in range(1, 360)), 'no-zoom-out')
            a = page.evaluate('()=>renderClip(0,4)'); b = page.evaluate('()=>renderClip(0,9)')
            require(a['camera']['k'] > 1 and a['camera']['k'] == b['camera']['k'], 'fixed-reading-scale')
            require(abs(a['camera']['x']-b['camera']['x']) > 50, 'real-lateral-pan')
            page.evaluate('()=>renderClip(0,11.9)'); again = page.evaluate('()=>renderClip(0,9)')
            require(b == again, 'repeat-seek')
            tags = page.locator('#current [data-role="paper-emphasis"]').evaluate_all('(els)=>els.map(el=>el.tagName)')
            require(all(tag == 'line' for tag in tags), 'no-closed-highlight-rectangle')
            require(page.locator('#current image').count() == 1, 'actual-source-image')
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    frame = run / 'encoded-nine.png'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '9', '-i', str(video), '-frames:v', '1', str(frame)], capture_output=True, check=True)
    guide = b['guide']; x = round(guide['x']); y = round(guide['y']); radius = max(2, round(guide['r']/3))
    with Image.open(frame) as image:
        rgb = ImageStat.Stat(image.convert('RGB').crop((x-radius, y-radius, x+radius+1, y+radius+1))).median
    require(max(abs(a-b) for a, b in zip(rgb, [158, 27, 50])) <= 30, 'encoded-guide-arrival')
    result = {'ok': not failures, 'findings': failures, 'frames': 360, 'cameraAt4': a['camera'], 'cameraAt9': b['camera'],
              'videoSha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'scope': 'Independent local source, actual encoded media and visible guide checks; no live editor claim.'}
    (run / 'artifact-quality.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('run', type=Path, nargs='+'); args = parser.parse_args()
    results = [{'run': str(run), **inspect(run)} for run in args.run]
    print(json.dumps(results)); return 0 if all(r['ok'] for r in results) else 2


if __name__ == '__main__': raise SystemExit(main())
