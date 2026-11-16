#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a small Spanish-labelled, silent acceptance demonstration of long-focus motion."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRIMARY = ROOT / 'skills/line-world-video'
OUTPUT = ROOT / 'projects/line-world-video/artifacts/focus-motion-demo'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PRIMARY / 'assets/runtime/focus-motion.js', OUTPUT / 'focus-motion.js')
    plan = {'windows': [
        {'id': 'model-input', 'source': '#input-edge', 'scope': '#diagram', 'kind': 'diagram', 'start': .3, 'end': 3.9, 'mode': 'trace'},
        {'id': 'model-output', 'source': '#output-edge', 'scope': '#diagram', 'kind': 'diagram', 'start': .3, 'end': 3.9, 'mode': 'trace'},
        {'id': 'curve-reading', 'source': '#curve', 'scope': '#chart', 'kind': 'chart', 'start': 4.2, 'end': 8.9, 'mode': 'trace'}
    ]}
    (OUTPUT / 'focus.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    html = '''<!doctype html><html lang="es"><meta charset="utf-8"><style>
body{margin:0;background:#fff}svg{display:block;width:100vw;height:100vh;font-family:Arial,sans-serif}text{fill:#333e48;font-size:30px;font-variant-numeric:tabular-nums}.small{font-size:24px;fill:#696969}
</style><svg id="stage" viewBox="0 0 1920 1080" role="img" aria-label="Illustrative model flow and curve with parent-clock focus motion">
<path d="M960 0V1080" stroke="#cfcfcf" stroke-width="1.5"/>
<g id="diagram"><rect x="180" y="510" width="150" height="110" fill="#e7e7e7"/><rect x="430" y="510" width="150" height="110" fill="#e7e7e7"/><rect x="680" y="510" width="150" height="110" fill="#e7e7e7"/>
<path id="input-edge" d="M330 565H430" fill="none" stroke="#696969" stroke-width="2.2"/><path id="output-edge" d="M580 565H680" fill="none" stroke="#696969" stroke-width="2.2"/>
<text x="255" y="576" text-anchor="middle">Datos</text><text x="505" y="576" text-anchor="middle">Modelo</text><text x="755" y="576" text-anchor="middle">Salida</text></g>
<g id="chart"><path d="M1130 300V750H1810" fill="none" stroke="#cfcfcf" stroke-width="2"/>
<path id="curve" d="M1160 700C1250 650 1300 570 1380 550S1570 430 1740 400" fill="none" stroke="#696969" stroke-width="3"/>
<circle cx="1160" cy="700" r="6" fill="#696969"/><circle cx="1380" cy="550" r="6" fill="#696969"/><circle cx="1740" cy="400" r="6" fill="#696969"/>
<text x="1160" y="795" class="small" text-anchor="middle">0</text><text x="1740" y="795" class="small" text-anchor="middle">4</text><text x="1100" y="710" class="small" text-anchor="end">0,2</text><text x="1100" y="410" class="small" text-anchor="end">0,8</text><text x="1740" y="365" text-anchor="middle">0,82</text><text x="1465" y="1000" class="small" text-anchor="middle">Datos ilustrativos</text></g>
<circle id="guide" cx="505" cy="478" r="10" fill="#9e1b32"/></svg>
<script src="focus-motion.js"></script><script>
window.FOCUS_PLAN=PLAN;
const motion=LineWorldFocusMotion.attach(document.querySelector('#stage'),FOCUS_PLAN.windows);
window.renderAt=t=>{const q=Math.max(0,Math.min(1,(t-3.9)/.3)),u=q*q*(3-2*q),g=document.querySelector('#guide');g.setAttribute('cx',505+1255*u);g.setAttribute('cy',478-168*u);return{seconds:t,motion:motion.render(t)}};
window.ready=document.fonts.ready.then(()=>renderAt(0));
</script></html>'''.replace('PLAN;', json.dumps(plan) + ';')
    (OUTPUT / 'scene.html').write_text(html, encoding='utf-8')
    subprocess.run(['uv', 'run', '--script', str(PRIMARY / 'scripts/inspect_focus_motion.py'), '--html', str(OUTPUT / 'scene.html'), '--output', str(OUTPUT / 'motion-review.json'), '--screenshot', str(OUTPUT / 'poster.png'), '--video', str(OUTPUT / 'focus-motion-demo.mp4'), '--duration', '9'], check=True)
    print(json.dumps({'ok': True, 'output': str(OUTPUT), 'duration': 9, 'audio': False}))


if __name__ == '__main__': main()
