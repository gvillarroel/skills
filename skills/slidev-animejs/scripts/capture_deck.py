#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Capture a built local Slidev deck with owned server/browser cleanup."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = Path(self.translate_path(urlsplit(self.path).path))
        if not path.exists() and not urlsplit(self.path).path.startswith('/assets/'):
            self.path = '/'
        super().do_GET()

    def log_message(self, *args):
        pass


SNAPSHOT = """() => {
  const visible=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'};
  const box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom}};
  const roots=[...document.querySelectorAll('.connected-flow,.svg-asset-slide')].filter(visible);
  return {url:location.href,roots:roots.map(root=>({bounds:box(root),clickState:root.dataset.clickState,palette:root.dataset.palette,svgs:[...root.querySelectorAll('svg')].map(s=>({viewBox:s.getAttribute('viewBox'),width:s.getAttribute('width'),height:s.getAttribute('height'),bounds:box(s),labels:[...s.querySelectorAll('text')].filter(visible).map(t=>({text:t.textContent,font:getComputedStyle(t).fontSize,bounds:box(t)})),routes:[...s.querySelectorAll('[data-route]')].map(p=>({id:p.dataset.route,source:p.dataset.source,target:p.dataset.target,d:p.getAttribute('d')}))}))})),bodyText:document.body.innerText.slice(0,1800)};
}"""
MOTION = """() => {
  const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'};
  const box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom}};
  return [...document.querySelectorAll('.connected-flow .parcel,.machine-signal,.machine-gear,.machine-block')].filter(visible).map(e=>({kind:e.getAttribute('class'),route:e.dataset.motionRoute,opacity:e.getAttribute('opacity'),bounds:box(e),svgBounds:box(e.ownerSVGElement),pivot:getComputedStyle(e).transformBox}));
}"""


def capture(deck, output, clicks=2):
    dist = deck.resolve() / 'dist'
    if not (dist / 'index.html').is_file():
        raise ValueError('Build the deck first: npm --prefix <deck> run build.')
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SpaHandler, directory=str(dist)))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_address[1]}'
    report = {'deck': str(deck), 'states': [], 'pageErrors': []}
    try:
        with urlopen(origin, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError('Owned deck server did not become ready.')
        with sync_playwright() as runtime:
            options = {} if Path(runtime.chromium.executable_path).is_file() else {'channel': 'msedge'}
            browser = runtime.chromium.launch(**options)
            try:
                context = browser.new_context(viewport={'width': 1280, 'height': 800})
                context.grant_permissions(['screen-wake-lock'], origin=origin)
                page = context.new_page()
                page.on('pageerror', lambda error: report['pageErrors'].append(str(error)))
                page.goto(origin, wait_until='networkidle')
                page.locator('svg').first.wait_for()
                page.wait_for_timeout(900)
                for state in range(clicks + 1):
                    if state:
                        page.evaluate('document.activeElement?.blur()')
                        page.keyboard.press('ArrowRight')
                        page.wait_for_timeout(300)
                    frame = page.evaluate(SNAPSHOT)
                    frame['requestedClick'] = state
                    samples = []
                    for sample in range(12):
                        samples.append(page.evaluate(MOTION))
                        if sample in (0, 5, 11):
                            page.screenshot(path=str(output / f'state-{state}-motion-{sample}.png'))
                        page.wait_for_timeout(150)
                    frame['motionSamples'] = samples
                    page.screenshot(path=str(output / f'state-{state}.png'))
                    report['states'].append(frame)
                replay = page.get_by_role('button', name='Replay', exact=False)
                if replay.count():
                    replay.first.click()
                    report['replay'] = 'button'
                else:
                    page.reload(wait_until='networkidle')
                    report['replay'] = 'reload-current-route'
                page.wait_for_timeout(500)
                report['replayState'] = page.evaluate(SNAPSHOT)
                report['replayMotion'] = page.evaluate(MOTION)
                page.screenshot(path=str(output / 'replay.png'))
                page.emulate_media(reduced_motion='reduce')
                page.wait_for_timeout(250)
                report['reducedState'] = page.evaluate(SNAPSHOT)
                page.screenshot(path=str(output / 'reduced.png'))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    target = output / 'capture.json'
    target.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return target, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deck', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--clicks', type=int, default=2)
    args = parser.parse_args()
    if not 0 <= args.clicks <= 12:
        parser.error('Click count must be between zero and twelve.')
    try:
        path, report = capture(args.deck, args.output_dir, args.clicks)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({'capture': str(path), 'states': len(report['states']), 'pageErrors': report['pageErrors']}))
    raise SystemExit(1 if report['pageErrors'] else 0)


if __name__ == '__main__':
    main()
