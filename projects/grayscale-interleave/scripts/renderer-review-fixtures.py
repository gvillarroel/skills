#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Inspect native rebuilt fixtures and compare geometry with committed outputs."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
BASE = 'daaee75353c63ed6dde204d57cfdbae6b9936586'  # Qualified baseline HEAD before grayscale changes.
OUT = ROOT / 'projects/grayscale-interleave/artifacts/reviews/renderer-fixtures-final'
MERMAID = ROOT / 'skills/mermaid/assets/examples/mermaid-max-complexity'
PLANT = ROOT / 'skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1'
GEOMETRY = {'x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'rx', 'ry', 'r',
            'width', 'height', 'viewBox', 'd', 'points', 'transform', 'font-size',
            'font-family', 'font-weight', 'textLength', 'lengthAdjust', 'text-anchor'}


def geometry(payload):
    root = ET.fromstring(payload)
    return [(node.tag.rsplit('}', 1)[-1], {key: value for key, value in node.attrib.items()
                                        if key in GEOMETRY},
             node.text if node.tag.endswith('text') else None)
            for node in root.iter()]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if '--summary' in sys.argv:
        proof = json.loads((OUT / 'review.json').read_text(encoding='utf-8'))
        for record in proof['mermaidGeometryComparedWithHEAD']:
            if not record['same']:
                print(json.dumps({'path': record['path'], 'counts': [record['beforeCount'], record['afterCount']],
                                  'differences': record['differences'][:8]}))
        return
    geometry_results = []
    for path in sorted((MERMAID / 'svg/colorset1').glob('*.static.svg')):
        relative = path.relative_to(ROOT).as_posix()
        before = subprocess.run(['git', 'show', f'{BASE}:{relative}'], cwd=ROOT, capture_output=True, check=True).stdout
        old, new = geometry(before), geometry(path.read_bytes())
        differences = [{'index': index, 'before': old[index], 'after': new[index]}
                       for index in range(min(len(old), len(new))) if old[index] != new[index]]
        geometry_results.append({'path': relative, 'same': old == new,
                                 'beforeCount': len(old), 'afterCount': len(new), 'differences': differences})
    selected = {
        'plantuml-archimate': PLANT / 'svg/archimate.svg',
        'plantuml-chart': PLANT / 'svg/chart.svg',
        'mermaid-flowchart': MERMAID / 'svg/colorset1/flowchart.static.svg',
        'mermaid-gantt': MERMAID / 'svg/colorset1/gantt.static.svg',
        'mermaid-treemap': MERMAID / 'svg/colorset1/treemap.static.svg',
        'mermaid-mindmap': MERMAID / 'svg/colorset1/mindmap.static.svg',
        'mermaid-xy-chart': MERMAID / 'svg/colorset1/xy-chart.static.svg',
        'mermaid-block': MERMAID / 'svg/colorset1/block.static.svg',
        'mermaid-c4': MERMAID / 'svg/colorset1/c4.static.svg',
        'mermaid-class': MERMAID / 'svg/colorset1/class.static.svg',
        'mermaid-requirement': MERMAID / 'svg/colorset1/requirement.static.svg',
    }
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={'width': 2000, 'height': 1600})
        for name, path in selected.items():
            root = ET.parse(path).getroot()
            dimensions = [float(value) for value in root.get('viewBox', '').split()]
            if len(dimensions) == 4:
                page.set_viewport_size({'width': max(1, math.ceil(dimensions[2])),
                                        'height': max(1, math.ceil(dimensions[3]))})
            page.goto(path.as_uri())
            page.evaluate('document.fonts.ready')
            proof = page.evaluate('''() => {
              const svg=document.documentElement,rectangle=svg.getBoundingClientRect();
              const texts=[...document.querySelectorAll('text,foreignObject')].map(el=>{
                const r=el.getBoundingClientRect(),s=getComputedStyle(el);
                return {text:el.textContent.trim(),bounds:{x:r.x,y:r.y,width:r.width,height:r.height},
                        fill:s.fill,color:s.color,fontSize:s.fontSize};
              }).filter(item=>item.text);
              return {width:rectangle.width,height:rectangle.height,texts};
            }''')
            page.locator('svg').screenshot(path=str(OUT / f'{name}.png'))
            (OUT / f'{name}.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
            records.append({'name': name, 'source': path.relative_to(ROOT).as_posix(),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'width': proof['width'], 'height': proof['height'], 'textCount': len(proof['texts'])})
        browser.close()
    proof = {'nativeSnapshots': records, 'mermaidGeometryComparedWithHEAD': geometry_results,
             'allMermaidNativeGeometryUnchanged': all(record['same'] for record in geometry_results),
             'manualReviewPending': True}
    (OUT / 'review.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'snapshots': len(records), 'geometryCases': len(geometry_results),
                      'geometryChanged': [record['path'] for record in geometry_results if not record['same']]}))


if __name__ == '__main__':
    main()
