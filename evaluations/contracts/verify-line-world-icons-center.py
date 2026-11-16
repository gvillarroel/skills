#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "Pillow>=11,<13"]
# ///
"""Independently inspect forward-created glyph pixels and container geometry."""
import argparse
import functools
import http.server
import io
import json
import os
import threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cache = Path(os.environ.get('LOCALAPPDATA', ''))/'ms-playwright'
    browsers = sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'), reverse=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=str(browsers[0]) if browsers else None)
        for workspace in args.workspace:
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(workspace.resolve())))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/film/index.html')
            page.evaluate('async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready;}')
            samples = []; first = None
            for time in [2, 5, 8, 2]:
                page.evaluate('t=>renderAt(t)', time)
                raw = page.screenshot(); im = Image.open(io.BytesIO(raw)).convert('RGB')
                observed = page.evaluate('''()=>{const box=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,w:b.width,h:b.height};},faces=[...document.querySelectorAll('[data-lw-surface="item"]')],inside=(a,b)=>a.x>=b.x-1&&a.y>=b.y-1&&a.x+a.w<=b.x+b.w+1&&a.y+a.h<=b.y+b.h+1;return [...document.querySelectorAll('[data-lw-icon="monochrome"]')].filter(e=>!e.closest('defs')).map(icon=>{const b=box(icon),face=faces.filter(f=>inside(b,box(f))).sort((a,z)=>box(a).w*box(a).h-box(z).w*box(z).h)[0],content=icon.closest('[data-lw-content]');return{icon:b,face:face?box(face):null,fill:face?getComputedStyle(face).fill:null,content:content?box(content):null,text:content?[...content.querySelectorAll('text')].map(t=>getComputedStyle(t).fill):[]}})}''')
                for obj in observed:
                    f = obj['face']; c = obj['content']; g = obj['icon']
                    obj['centered'] = bool(f and c and abs(c['x']+c['w']/2-f['x']-f['w']/2) <= 2 and abs(c['y']+c['h']/2-f['y']-f['h']/2) <= 2)
                    obj['contained'] = bool(f and c and c['x'] >= f['x']-1 and c['y'] >= f['y']-1 and c['x']+c['w'] <= f['x']+f['w']+1 and c['y']+c['h'] <= f['y']+f['h']+1)
                    active = obj['fill'] == 'rgb(158, 27, 50)'
                    target = (255, 255, 255) if active else (51, 62, 72)
                    crop = im.crop((int(g['x']), int(g['y']), int(g['x']+g['w']+1), int(g['y']+g['h']+1)))
                    data = crop.tobytes(); count = sum(all(abs(data[i+j]-target[j]) <= 8 for j in range(3)) for i in range(0, len(data), 3))
                    obj['expectedInkPixels'] = count; obj['active'] = active
                    expected_text = 'rgb(255, 255, 255)' if active else 'rgb(51, 62, 72)'
                    obj['textCorrect'] = bool(obj['text']) and all(x == expected_text for x in obj['text'])
                    obj['ok'] = obj['centered'] and obj['contained'] and obj['textCorrect'] and count > 20
                if first is None: first = raw
                samples.append({'seconds': time, 'objects': observed, 'ok': bool(observed) and all(o['ok'] for o in observed)})
            repeat = first == raw
            results.append({'workspace': str(workspace), 'states': samples, 'repeatPixels': repeat, 'browserErrors': errors, 'ok': not errors and repeat and all(x['ok'] for x in samples)})
            page.close(); server.shutdown(); server.server_close()
        browser.close()
    result = {'ok': all(x['ok'] for x in results), 'cases': results, 'scope': 'Evaluator-owned loaded geometry, actual screenshot pixels and deterministic return seeking.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'cases': len(results), 'failed': [r['workspace'] for r in results if not r['ok']]}))
    return 0 if result['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
