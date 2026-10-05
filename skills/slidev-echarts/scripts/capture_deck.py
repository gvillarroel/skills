#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Capture a built Slidev deck with owned SPA server and browser cleanup."""
from __future__ import annotations

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
        route = urlsplit(self.path).path
        if not Path(self.translate_path(route)).exists() and not route.startswith('/assets/'):
            self.path = '/'
        super().do_GET()

    def log_message(self, *args):
        pass


SNAPSHOT = """() => {
  const box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom}};
  const visible=e=>{const b=box(e);if(!b.width||!b.height)return false;for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false}return true};
  let roots=[...document.querySelectorAll('.slidev-page')].filter(visible);
  if(!roots.length)roots=[...document.querySelectorAll('.slidev-layout')].filter(visible);
  const nativeBounds=e=>{const b=box(e),s=box(e.ownerSVGElement);return {x:b.x-s.x,y:b.y-s.y,width:b.width,height:b.height}};
  const gap=(a,b)=>Math.hypot(Math.max(b.x-a.x-a.width,a.x-b.x-b.width,0),Math.max(b.y-a.y-a.height,a.y-b.y-b.height,0));
  return {url:location.href,viewport:{width:innerWidth,height:innerHeight},roots:roots.map(root=>({bounds:box(root),readiness:[...root.querySelectorAll('[data-render-ready],[data-arrow-check],[data-workflow-state],[data-state],[data-story-state]')].map(e=>({...e.dataset})),svgs:[...root.querySelectorAll('svg')].filter(visible).map(svg=>{
    const paths=[...svg.querySelectorAll('path')].filter(visible);
    const nodes=paths.filter(e=>{const b=e.getBBox();return getComputedStyle(e).fill!=='none'&&b.width<=3&&b.height<=3}).map(e=>({bounds:nativeBounds(e),fill:getComputedStyle(e).fill}));
    const heads=paths.filter(e=>e.getAttribute('d').startsWith('M0 0L')).map(e=>({bounds:nativeBounds(e),fill:getComputedStyle(e).fill,gap:Math.min(...nodes.map(n=>gap(nativeBounds(e),n.bounds)))}));
    return {viewBox:svg.getAttribute('viewBox'),width:svg.getAttribute('width'),height:svg.getAttribute('height'),bounds:box(svg),labels:[...svg.querySelectorAll('text')].filter(visible).map(e=>({text:e.textContent,fontSize:parseFloat(getComputedStyle(e).fontSize),bounds:nativeBounds(e)})),nodes,heads,pathCount:paths.length};
  })})),bodyText:document.body.innerText.slice(0,1800)};
}"""


def capture(deck: Path, output: Path, clicks: int = 2, slide: int = 1, settle_ms: int = 900):
    dist = deck.resolve() / 'dist'
    if not (dist / 'index.html').is_file():
        raise ValueError('Build the deck first: npm --prefix <deck> run build.')
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SpaHandler, directory=str(dist)))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_address[1]}'
    report = {'deck': str(deck), 'serverOrigin': origin, 'states': [], 'pageErrors': []}
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
                page.goto(f'{origin}/{slide}', wait_until='networkidle')
                page.locator('.slidev-page,.slidev-layout').first.wait_for()
                page.evaluate('document.fonts.ready')
                def settle():
                    page.wait_for_timeout(settle_ms)
                    page.wait_for_function("""() => [...document.querySelectorAll('[data-render-ready]')].filter(e=>{const b=e.getBoundingClientRect();if(!b.width||!b.height)return false;for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false}return true}).every(e=>e.dataset.renderReady==='true')""", timeout=10000)
                    page.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
                settle()
                for state in range(clicks + 1):
                    if state:
                        page.evaluate('document.activeElement?.blur()')
                        page.keyboard.press('ArrowRight')
                        settle()
                    frame = page.evaluate(SNAPSHOT)
                    frame['requestedClick'] = state
                    page.screenshot(path=str(output / f'state-{state}.png'))
                    report['states'].append(frame)
                replay = page.get_by_role('button', name='Replay', exact=False)
                if replay.count():
                    replay.first.click()
                    report['replay'] = 'button'
                else:
                    page.reload(wait_until='networkidle')
                    report['replay'] = 'reload-current-route'
                settle()
                report['replayState'] = page.evaluate(SNAPSHOT)
                page.screenshot(path=str(output / 'replay.png'))
                page.set_viewport_size({'width': 1024, 'height': 768})
                settle()
                report['resizedState'] = page.evaluate(SNAPSHOT)
                page.screenshot(path=str(output / 'resized.png'))
                page.emulate_media(reduced_motion='reduce')
                settle()
                report['reducedState'] = page.evaluate(SNAPSHOT)
                page.screenshot(path=str(output / 'reduced.png'))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    report['serverClosed'] = True
    target = output / 'capture.json'
    target.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return target, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deck', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--clicks', type=int, default=2)
    parser.add_argument('--slide', type=int, default=1)
    parser.add_argument('--settle-ms', type=int, default=900)
    args = parser.parse_args()
    if not 0 <= args.clicks <= 12 or args.slide < 1 or not 0 <= args.settle_ms <= 10000:
        parser.error('Use zero to twelve clicks, a positive slide number and zero to 10000 settle milliseconds.')
    workspace = Path.cwd().resolve()
    resource_root = Path(__file__).resolve().parents[1]
    for path in [args.deck, args.output_dir]:
        if not path.resolve().is_relative_to(workspace):
            parser.error('Run from the task workspace with deck and output paths inside that workspace.')
        if path.resolve().is_relative_to(resource_root):
            parser.error('Keep the built deck and captures outside the read-only skill resource directory.')
    try:
        path, report = capture(args.deck, args.output_dir, args.clicks, args.slide, args.settle_ms)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({'capture': str(path), 'states': len(report['states']), 'pageErrors': report['pageErrors'], 'serverClosed': report['serverClosed']}))
    return 1 if report['pageErrors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
