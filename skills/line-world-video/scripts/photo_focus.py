#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Build aligned photographic focus plans and inspect actual parent-clock colors."""
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
from inspect_focus import Quiet, browser_path


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def normalize(bindings):
    if not isinstance(bindings, list) or not bindings: raise ValueError('Provide photograph bindings.')
    ids, targets, result = set(), set(), []
    for binding in bindings:
        if not binding.get('id') or binding['id'] in ids or not binding.get('target') or binding['target'] in targets:
            raise ValueError('Use unique photograph IDs and SVG image targets.')
        ids.add(binding['id']); targets.add(binding['target'])
        transition = binding.get('transition', .35)
        if not isinstance(transition, (int, float)) or not math.isfinite(transition) or not 0 <= transition <= 2:
            raise ValueError('Photograph transition must be between zero and two seconds.')
        windows = binding.get('windows')
        if not isinstance(windows, list) or not windows: raise ValueError('Provide measured photograph focus windows.')
        for window in windows:
            if any(not isinstance(window.get(k), (int, float)) or not math.isfinite(window[k]) for k in ['start', 'end']) or window['start'] < 0 or window['end'] <= window['start']:
                raise ValueError('Use finite positive photograph focus intervals.')
        merged = []
        for window in sorted(windows, key=lambda w: w['start']):
            if merged and window['start'] <= merged[-1]['end']: merged[-1]['end'] = max(merged[-1]['end'], window['end'])
            else: merged.append({'start': window['start'], 'end': window['end']})
        result.append({**binding, 'transition': transition, 'windows': merged})
    return result


def plan(manifest, bindings, html_root, output):
    assets = {a['id']: a for a in read(manifest)['assets']}
    result = []
    for binding in normalize(read(bindings)['bindings']):
        asset = assets[binding['asset']]
        variant = next(v for v in asset['variants'] if v['id'] == binding['variant'])
        neutral = manifest.parent / variant['png']
        original = manifest.parent / (asset['id'] + '.prepared.png')
        for path, sha in [(neutral, variant['pngSha256']), (original, asset['preparedSha256'])]:
            if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                raise ValueError('Prepared photograph changed: ' + str(path))
        with Image.open(neutral) as gray, Image.open(original) as color:
            if gray.size != color.size: raise ValueError('Focus images need the same prepared crop and dimensions.')
            red, green, blue = gray.convert('RGB').split()
            if max(ImageChops.difference(a, b).getextrema()[1] for a, b in [(red, green), (green, blue), (red, blue)]) > 3:
                raise ValueError('Use a neutral grayscale treatment for secondary photographs.')
        result.append({**binding, 'neutral': neutral.resolve().relative_to(html_root.resolve()).as_posix(),
                       'color': original.resolve().relative_to(html_root.resolve()).as_posix(),
                       'transition': binding.get('transition', .35),
                       'sourceSha256': asset['sourceSha256'], 'preparedSha256': asset['preparedSha256']})
    data = {'bindings': result, 'scope': 'Original prepared colors with the identical reviewed crop, resize and orientation; no colorization.'}
    save(output, data)
    return {'ok': True, 'bindings': len(result), 'output': str(output)}


def inspect(html, plan_path, output, screenshot=None, video=None, duration=None, fps=30):
    from playwright.sync_api import sync_playwright
    html = html.resolve()
    report = {'ok': False, 'photos': [], 'issues': [], 'scope': 'Declared SVG photo pairs at sampled focus times; exact endpoint pixels, fixed bounds and repeated seek. Not speech or full-film certification.'}
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(html.parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
            errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{html.name}')
            page.evaluate('''async()=>{await document.fonts.ready;if(window.ready)await window.ready;for(const t of Object.values(window.__timelines||{}))t?.pause?.(0);window.gsap?.ticker?.sleep?.();}''')
            embedded = page.evaluate('window.PHOTO_FOCUS_PLAN?.bindings')
            bindings = read(plan_path)['bindings'] if plan_path else embedded
            bindings = normalize(bindings)
            if plan_path:
                relevant = lambda b: {k: b.get(k) for k in ['id', 'target', 'neutral', 'color', 'transition', 'windows']}
                if [relevant(b) for b in bindings] != [relevant(b) for b in normalize(embedded)]:
                    raise ValueError('External and actual browser photographic focus plans differ.')
            report['actualBrowserPlanVerified'] = True
            hide = page.add_style_tag(content='#guide,#guide-dot,#attention-dot,[data-lw-guide]{visibility:hidden!important}')
            def render(t): page.evaluate('t=>{window.renderAt(t);window.gsap?.ticker?.sleep?.();}', t)
            def capture(binding):
                box = page.locator(binding['target']).bounding_box()
                if not box or min(box['width'], box['height']) <= 0: raise ValueError('Photograph is hidden or has no bounds.')
                crop = (max(0, math.floor(box['x'])), max(0, math.floor(box['y'])), min(1920, math.ceil(box['x'] + box['width'])), min(1080, math.ceil(box['y'] + box['height'])))
                if crop[2] <= crop[0] or crop[3] <= crop[1]: raise ValueError('Photograph is outside the frame.')
                return Image.open(io.BytesIO(page.screenshot())).convert('RGB').crop(crop), box
            for b in bindings:
                checks = []
                actual = page.evaluate('''b=>{const n=document.querySelector(b.target),c=[...document.querySelectorAll('[data-lw-photo-color]')].find(e=>e.dataset.lwPhotoColor===b.id);return!!n&&!!c&&new URL(c.getAttribute('href'),document.baseURI).href===new URL(b.color,document.baseURI).href&&(!b.neutral||new URL(n.getAttribute('href'),document.baseURI).href===new URL(b.neutral,document.baseURI).href)}''', b)
                if not actual: raise ValueError('Rendered photograph differs from its declared neutral/original pair: ' + b['id'])
                for w in b['windows']:
                    middle = (w['start'] + w['end']) / 2
                    render(middle)
                    overlay = page.locator('[data-lw-photo-color]').evaluate_all('(es,id)=>es.filter(e=>e.dataset.lwPhotoColor===id).length', b['id'])
                    if overlay != 1: raise ValueError('Bind one original-color layer per photograph.')
                    # Independent reference captures use the actual paired layers, not reported state.
                    def opacity(value): page.evaluate('([id,v])=>{[...document.querySelectorAll("[data-lw-photo-color]")].find(e=>e.dataset.lwPhotoColor===id).style.opacity=String(v)}', [b['id'], value])
                    opacity(0); neutral, reference_box = capture(b)
                    source_opacity = page.locator(b['target']).evaluate('e=>Number(getComputedStyle(e).opacity)')
                    opacity(source_opacity); original, _ = capture(b)
                    render(middle); active, box = capture(b)
                    render(w['end']); exited, exit_box = capture(b)
                    render(w['start']); entered, enter_box = capture(b)
                    render(middle); repeated, repeat_box = capture(b)
                    fade = min(b.get('transition', .35), (w['end'] - w['start']) / 2)
                    render(w['start'] + fade / 2 if fade else middle); transition, transition_box = capture(b)
                    same = lambda a, c: a.size == c.size and a.tobytes() == c.tobytes()
                    item = {'start': w['start'], 'end': w['end'], 'originalColorAtFocus': same(active, original),
                            'neutralAtExit': same(exited, neutral), 'neutralAtEntry': same(entered, neutral) if fade else same(entered, original),
                            'repeatSeek': same(repeated, active), 'fixedBounds': all(p == reference_box for p in [box, exit_box, enter_box, repeat_box, transition_box]),
                            'visibleColorDifference': ImageChops.difference(original, neutral).getbbox() is not None,
                            'smoothIntermediate': (not same(transition, original) and not same(transition, neutral)) if fade else True}
                    checks.append(item)
                    for key in ['originalColorAtFocus', 'neutralAtExit', 'neutralAtEntry', 'repeatSeek', 'fixedBounds']:
                        if not item[key]: report['issues'].append(b['id'] + ': ' + key + ' failed')
                    if item['visibleColorDifference'] and not item['smoothIntermediate']: report['issues'].append(b['id'] + ': intermediate transition is missing')
                report['photos'].append({'id': b['id'], 'checks': checks})
            hide.evaluate('e=>e.remove()')
            if screenshot:
                render((bindings[0]['windows'][0]['start'] + bindings[0]['windows'][0]['end']) / 2)
                screenshot.parent.mkdir(parents=True, exist_ok=True); page.screenshot(path=str(screenshot))
            if video:
                if duration is None or not 0 < duration <= 60: raise ValueError('Preview duration must be above zero and at most 60 seconds.')
                video.parent.mkdir(parents=True, exist_ok=True); frames = round(duration * fps)
                cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'png', '-framerate', str(fps), '-i', 'pipe:0', '-frames:v', str(frames), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)]
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    for frame in range(frames): render(frame / fps); proc.stdin.write(page.screenshot())
                    proc.stdin.close(); stderr = proc.stderr.read().decode(); code = proc.wait()
                    if code: raise ValueError('Preview encoding failed: ' + stderr)
                finally:
                    if proc.poll() is None: proc.kill(); proc.wait()
                report['video'] = {'file': str(video), 'frames': frames, 'fps': fps, 'duration': frames / fps, 'audio': False, 'sha256': hashlib.sha256(video.read_bytes()).hexdigest()}
            report['issues'] += errors; browser.close(); report['ok'] = not report['issues']
    finally:
        server.shutdown(); save(output, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('plan'); p.add_argument('--manifest', type=Path, required=True); p.add_argument('--bindings', type=Path, required=True); p.add_argument('--html-root', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('inspect'); p.add_argument('--html', type=Path, required=True); p.add_argument('--plan', type=Path); p.add_argument('--output', type=Path, required=True); p.add_argument('--screenshot', type=Path); p.add_argument('--video', type=Path); p.add_argument('--duration', type=float); p.add_argument('--fps', type=int, choices=[24, 25, 30, 60], default=30)
    args = parser.parse_args()
    try:
        result = plan(args.manifest, args.bindings, args.html_root, args.output) if args.command == 'plan' else inspect(args.html, args.plan, args.output, args.screenshot, args.video, args.duration, args.fps)
        print(json.dumps({k: v for k, v in result.items() if k != 'photos'})); return 0 if result['ok'] else 2
    except (ValueError, KeyError, OSError, StopIteration) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
