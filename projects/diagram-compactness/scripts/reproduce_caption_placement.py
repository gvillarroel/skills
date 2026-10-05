#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52", "pillow>=11"]
# ///
"""Preserve original Slidev cases and compare old/new native caption placement."""
from __future__ import annotations

import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('qualification', ROOT / 'skills/slidev-echarts/scripts/qualify_concept_graph.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not Path(self.translate_path(self.path)).is_file() and not self.path.startswith('/assets/'):
            self.path = '/'
        super().do_GET()

    def log_message(self, *args):
        pass


SNAPSHOT = r"""() => {
  const opacity=e=>{let value=1;for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);value*=Number(s.opacity);if(s.visibility==='hidden'||s.display==='none')return 0}return value};
  const svg=[...document.querySelectorAll('svg')].find(e=>{const m=e.getScreenCTM();return e.getBoundingClientRect().width>250&&m&&Math.abs(m.a*m.d-m.b*m.c)>1e-6&&opacity(e)>.1&&[...e.querySelectorAll('text')].some(t=>t.textContent==='Failed sample')});
  if(!svg)throw Error('Original conceptual graph is missing');
  const inverse=svg.getScreenCTM().inverse(),quad=e=>{const b=e.getBBox(),m=inverse.multiply(e.getScreenCTM());return [[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>[m.a*x+m.c*y+m.e,m.b*x+m.d*y+m.f])};
  const paths=[...svg.querySelectorAll('path')].filter(e=>opacity(e)>.1);
  const shafts=paths.filter(e=>getComputedStyle(e).fill==='none'&&parseFloat(getComputedStyle(e).strokeWidth)>0).map(e=>{const m=inverse.multiply(e.getScreenCTM()),length=e.getTotalLength(),points=[];for(let i=0;i<=360;i++){const p=e.getPointAtLength(length*i/360);points.push([m.a*p.x+m.c*p.y+m.e,m.b*p.x+m.d*p.y+m.f])}return {d:e.getAttribute('d'),width:parseFloat(getComputedStyle(e).strokeWidth),points}});
  const labels=[...svg.querySelectorAll('text')].map(e=>({text:e.textContent,quad:quad(e),font:getComputedStyle(e).font,fontSize:parseFloat(getComputedStyle(e).fontSize)}));
  const bodies=paths.filter(e=>{const b=e.getBBox();return getComputedStyle(e).fill!=='none'&&(e.getAttribute('d').startsWith('M0 0L')||(b.width<=3&&b.height<=3))}).map(e=>({d:e.getAttribute('d'),quad:quad(e),fill:getComputedStyle(e).fill}));
  return {labels,shafts,bodies,canvas:{width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height}};
}"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(workspace: Path, clicks: int, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(workspace / 'deck/dist')))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    result = {'states': [], 'pageErrors': []}
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 800})
                page.context.grant_permissions(['screen-wake-lock'], origin=f'http://127.0.0.1:{server.server_port}')
                page.on('pageerror', lambda error: result['pageErrors'].append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}/1', wait_until='networkidle')
                page.locator('.slidev-page,.slidev-layout').first.wait_for()
                for state in ['initial', *[f'click-{i}' for i in range(1, clicks + 1)], 'replay', 'resized', 'reduced-motion']:
                    if state.startswith('click'):
                        page.keyboard.press('ArrowRight')
                    elif state == 'replay':
                        for _ in range(clicks):
                            page.keyboard.press('ArrowLeft')
                        for _ in range(clicks):
                            page.keyboard.press('ArrowRight')
                    elif state == 'resized':
                        page.set_viewport_size({'width': 1024, 'height': 768})
                    elif state == 'reduced-motion':
                        page.emulate_media(reduced_motion='reduce')
                    page.evaluate('document.fonts.ready')
                    page.wait_for_function("[...document.querySelectorAll('[data-render-ready]')].filter(e=>e.getBoundingClientRect().width>0).every(e=>e.dataset.renderReady==='true')")
                    page.wait_for_timeout(500)
                    page.wait_for_function("[...document.querySelectorAll('svg')].some(e=>e.getBoundingClientRect().width>250&&[...e.querySelectorAll('text')].some(t=>t.textContent==='Failed sample'))")
                    proof = page.evaluate(SNAPSHOT)
                    proof['state'] = state
                    proof['captionShaftGaps'] = []
                    for label in proof['labels']:
                        if label['text'] in ['Retest', 'Failed sample']:
                            gap = min(oracle.segment_quad_distance(a, b, label['quad']) - shaft['width'] / 2 for shaft in proof['shafts'] for a, b in zip(shaft['points'], shaft['points'][1:]))
                            body_gap = min(min(oracle.segment_quad_distance(body['quad'][i], body['quad'][(i+1)%4], label['quad']) for i in range(4)) for body in proof['bodies'])
                            proof['captionShaftGaps'].append({'label': label['text'], 'gap': gap, 'completeHeadBodyGap': body_gap})
                    # Default native screenshot: do not substitute animations='disabled'.
                    page.screenshot(path=str(output / f'{state}.png'))
                    proof['pngSha256'] = digest(output / f'{state}.png')
                    result['states'].append(proof)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'projects/diagram-compactness/artifacts') or output.exists():
        parser.error('Use a fresh project-owned artifact directory.')
    output.mkdir(parents=True)
    results = []
    for number, clicks, crop in [(2, 1, (475, 400, 725, 560)), (3, 2, (475, 455, 725, 615))]:
        trial = ROOT / f'evaluations/runs/compact-slidev-echarts-20261004-sol-first-probe-final-natural-{number}/workspace'
        original = trial / 'deck/components/SampleWorkflow.vue'
        original_hash = digest(original)
        pair = {'case': number, 'sourceSha256': original_hash, 'variants': {}}
        for variant in ['old', 'new']:
            workspace = output / f'natural-{number}' / variant
            shutil.copytree(trial / 'deck', workspace / 'deck', ignore=shutil.ignore_patterns('node_modules', 'dist'))
            dependencies = trial / 'deck/node_modules'
            assert dependencies.is_dir(), dependencies
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(workspace / 'deck/node_modules'), str(dependencies)], check=True, capture_output=True)
            bundle = trial / 'skills/slidev-echarts' if variant == 'old' else ROOT / 'skills/slidev-echarts'
            templates = workspace / 'skills/slidev-echarts/assets/templates'
            templates.mkdir(parents=True)
            for filename in ['echarts-colorsets.mjs', 'concept-graph-labels.mjs']:
                shutil.copy2(bundle / 'assets/templates' / filename, templates / filename)
            assert digest(workspace / 'deck/components/SampleWorkflow.vue') == original_hash
            build = subprocess.run(['npm.cmd', 'run', 'build'], cwd=workspace / 'deck', capture_output=True, text=True, encoding='utf-8')
            (workspace / 'build.log').write_text(build.stdout + build.stderr, encoding='utf-8')
            assert build.returncode == 0, workspace / 'build.log'
            proof = capture(workspace, clicks, workspace / 'capture')
            (workspace / 'native.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
            pair['variants'][variant] = proof
            for state in ['resized', 'reduced-motion']:
                with Image.open(workspace / 'capture' / f'{state}.png') as image:
                    image.crop(crop).resize(((crop[2]-crop[0])*4, (crop[3]-crop[1])*4), Image.Resampling.NEAREST).save(workspace / f'{state}-caption-4x.png')
        for before, after in zip(pair['variants']['old']['states'], pair['variants']['new']['states']):
            assert before['state'] == after['state']
            assert before['canvas'] == after['canvas']
            assert before['bodies'] == after['bodies'], (number, before['state'], 'Native bodies/heads changed')
            assert before['shafts'] == after['shafts'], (number, before['state'], 'Native shaft geometry/strokes changed')
            assert [(label['text'], label['font']) for label in before['labels']] == [(label['text'], label['font']) for label in after['labels']]
            assert all(record['gap'] >= 1 for record in after['captionShaftGaps']), (number, after['state'], after['captionShaftGaps'])
            assert all(record['completeHeadBodyGap'] >= 1 for record in after['captionShaftGaps'])
        assert not pair['variants']['new']['pageErrors']
        assert any(record['gap'] < 0 for state in pair['variants']['old']['states'] for record in state['captionShaftGaps']), 'Original collision was not reproduced'
        assert digest(original) == original_hash
        results.append(pair)
    report = {'ok': True, 'nativeDefaultScreenshots': True, 'sourceGeometryFontsStrokesHeadsPreserved': True, 'originalsUnchanged': True, 'cases': results}
    (output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'ok': True, 'output': str(output), 'cases': [record['case'] for record in results]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
