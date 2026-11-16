#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "Pillow>=11,<13"]
# ///
"""Verify visible target motion during focus holds longer than two seconds."""
import argparse
import functools
import hashlib
import io
import json
import math
import subprocess
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
from inspect_focus import Quiet, browser_path

SKILL = Path(__file__).resolve().parent.parent


def changed_pixels(a, b):
    difference = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    maximum = ImageChops.lighter(ImageChops.lighter(difference.getchannel('R'), difference.getchannel('G')), difference.getchannel('B'))
    return sum(maximum.histogram()[13:])


def inspect(html, output, screenshot, plan=None, video=None, fps=30, duration=None):
    for path in [output, screenshot, *([video] if video else [])]:
        if path.resolve().is_relative_to(SKILL): raise ValueError('Keep task outputs outside the loaded skill.')
        path.parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(html.parent.resolve())))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {'ok': False, 'windows': [], 'issues': [], 'browserErrors': [], 'scope': 'Samples actual target pixels with the guide hidden for motion proof. Checks stable geometry/text and repeat seeking. This is not independent audio or semantic validation.'}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
            page.on('pageerror', lambda e: report['browserErrors'].append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{html.name}')
            page.evaluate('async()=>{await document.fonts.ready;if(window.ready)await window.ready;}')
            windows = json.loads(plan.read_text(encoding='utf-8-sig'))['windows'] if plan else page.evaluate('window.FOCUS_PLAN?.windows')
            if not windows: raise ValueError('Provide a focus-window plan, including every chart/diagram hold.')
            ids = [w['id'] for w in windows]
            if len(ids) != len(set(ids)): raise ValueError('Focus windows need unique IDs.')
            hide = page.add_style_tag(content='#guide,#guide-dot,#attention-dot,[data-lw-guide]{visibility:hidden!important}')
            def render(t): page.evaluate('t=>window.renderAt(t)', t)
            geometry_js = '''w=>{const e=document.querySelector(w.source),scope=w.scope?document.querySelector(w.scope):e?.ownerSVGElement;if(!e||!scope)throw Error('Missing target or scope');const b=e.getBoundingClientRect();return{box:{x:b.x,y:b.y,width:b.width,height:b.height},geometry:['d','x','y','cx','cy','r','x1','y1','x2','y2','width','height','points','transform'].map(k=>[k,e.getAttribute(k)]),labels:[...scope.querySelectorAll('text')].map(e=>{const b=e.getBoundingClientRect();return{text:e.textContent,box:[b.x,b.y,b.width,b.height].map(v=>Math.round(v*100)/100)}})}}'''
            for window in windows:
                start, end = window['start'], window['end']
                if type(start) not in [int, float] or type(end) not in [int, float] or not math.isfinite(start + end) or start < 0 or end <= start or window.get('kind') not in ['chart', 'diagram']:
                    raise ValueError('Declare positive chart/diagram intervals on the parent clock.')
                if end - start <= 2:
                    report['windows'].append({'id': window['id'], 'seconds': end - start, 'required': False}); continue
                times = [start + (end - start) * q for q in [.12, .31, .5, .69, .88]]
                frames, states = [], []
                for t in times:
                    render(t); state = page.evaluate(geometry_js, window); states.append(state)
                    b = state['box']; left, top = max(0, math.floor(b['x'] - 8)), max(0, math.floor(b['y'] - 8))
                    right, bottom = min(1920, math.ceil(b['x'] + b['width'] + 8)), min(1080, math.ceil(b['y'] + b['height'] + 8))
                    if right <= left or bottom <= top: raise ValueError('The focused target is outside the visible frame.')
                    frames.append(Image.open(io.BytesIO(page.screenshot())).crop((left, top, right, bottom)).copy())
                stable = all(s == states[0] for s in states[1:])
                motion = max((changed_pixels(frames[0], f) for f in frames[1:] if f.size == frames[0].size), default=0)
                minimum = max(12, round(frames[0].width * frames[0].height * .0001))
                render(times[0]); render(times[-1]); repeated = Image.open(io.BytesIO(page.screenshot()))
                b = states[-1]['box']; box = (max(0, math.floor(b['x'] - 8)), max(0, math.floor(b['y'] - 8)), min(1920, math.ceil(b['x'] + b['width'] + 8)), min(1080, math.ceil(b['y'] + b['height'] + 8)))
                repeat = repeated.crop(box).tobytes() == frames[-1].tobytes()
                item = {'id': window['id'], 'seconds': end - start, 'required': True, 'changedPixels': motion, 'minimumChangedPixels': minimum, 'stableGeometryAndLabels': stable, 'repeatSeek': repeat}
                report['windows'].append(item)
                if motion < minimum: report['issues'].append(window['id'] + ': long focus is visually static inside its actual target')
                if not stable: report['issues'].append(window['id'] + ': fixed-data geometry or reading labels move during the hold')
                if not repeat: report['issues'].append(window['id'] + ': backward/repeated seek changes the rendered result')
            hide.evaluate('e=>e.remove()')
            render(windows[0]['start'] + (windows[0]['end'] - windows[0]['start']) * .5)
            page.screenshot(path=str(screenshot))
            report['ok'] = not report['issues'] and not report['browserErrors']
            if video and report['ok']:
                seconds = duration if duration is not None else max(w['end'] for w in windows)
                if not math.isfinite(seconds) or not 0 < seconds <= 60: raise ValueError('Use a positive preview duration of at most 60 seconds.')
                args = ['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'png', '-framerate', str(fps), '-i', 'pipe:0', '-frames:v', str(round(seconds * fps)), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)]
                process = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    for n in range(round(seconds * fps)):
                        render(n / fps); process.stdin.write(page.screenshot())
                    process.stdin.close(); error = process.stderr.read().decode(); code = process.wait()
                    if code: raise ValueError(error[-1200:])
                finally:
                    if process.poll() is None: process.terminate(); process.wait()
                report['video'] = {'path': str(video), 'frames': round(seconds * fps), 'fps': fps, 'duration': seconds, 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'audio': False}
            browser.close()
    except Exception as error: report['ok'] = False; report['browserErrors'].append(str(error))
    finally: server.shutdown(); server.server_close()
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8'); return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['html', 'output', 'screenshot']: parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--plan', type=Path); parser.add_argument('--video', type=Path); parser.add_argument('--fps', type=int, choices=[24, 25, 30, 60], default=30); parser.add_argument('--duration', type=float)
    args = parser.parse_args()
    try:
        report = inspect(args.html, args.output, args.screenshot, args.plan, args.video, args.fps, args.duration)
        print(json.dumps({k: v for k, v in report.items() if k != 'windows'})); return 0 if report['ok'] else 2
    except (ValueError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__': raise SystemExit(main())
