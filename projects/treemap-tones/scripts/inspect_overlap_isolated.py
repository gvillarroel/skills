#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "Pillow>=11"]
# ///
"""Reuse the independent overlap paint/geometry audit for isolated artifacts."""

import argparse
import importlib.util
import json
from pathlib import Path
import re

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('overlap_verifier', ROOT / 'projects/task-overlap-transparency/scripts/verify_overlap.py')
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((ROOT / 'projects/task-overlap-transparency/artifacts/baseline/verification.json').read_text(encoding='utf-8'))['states'][0]
    palette = json.loads((ROOT / 'skills/d3/assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets']['colorset1']
    reference = {'regions':baseline['regions'], 'tasks':baseline['tasks'], 'dotRadius':2.25,
                 'allowed':palette['allowed'], **baseline['invariants']}
    report = {'passed':False, 'states':[], 'errors':[], 'networkRequests':[]}
    with sync_playwright() as playwright:
        browser = VERIFIER.launch(playwright)
        for extension, reduced in [('html',False),('html',True),('svg',False),('svg',True)]:
            page = browser.new_page(viewport={'width':1440,'height':1100}, reduced_motion='reduce' if reduced else 'no-preference')
            page.on('pageerror',lambda error:report['errors'].append(str(error)))
            page.on('request',lambda request:report['networkRequests'].append(request.url) if request.url.startswith(('http:','https:')) else None)
            page.goto((args.workspace.resolve()/f'dense-overlap.{extension}').as_uri(),wait_until='load')
            page.wait_for_timeout(1800)
            replays = [0,1,2] if extension == 'html' and not reduced else [0]
            for replay in replays:
                if replay:
                    button = page.get_by_role('button',name=re.compile('Replay',re.IGNORECASE))
                    if button.count() != 1:
                        report['errors'].append('The HTML has no unambiguous Replay button.')
                        break
                    button.click()
                    page.wait_for_timeout(1800)
                page.evaluate('const svg=document.querySelector("svg");svg.pauseAnimations();svg.setCurrentTime(5)')
                state = page.evaluate(VERIFIER.INSPECT,{'reference':reference})
                state.update({'format':extension,'reducedMotion':reduced,'replay':replay})
                if state['tasks'] != baseline['tasks']:
                    state['findings'].append('Task positions, leaders, labels, or memberships differ from the generated layout.')
                if state['invariants'] != baseline['invariants']:
                    state['findings'].append('Membership/collision/crossing invariants changed.')
                for face in page.locator('.task-label-bg').all():
                    stroke = face.evaluate('(element)=>getComputedStyle(element).stroke')
                    if stroke != 'none':
                        state['findings'].append('An external task label face has a decorative border.')
                        break
                name = f'{extension}-{"reduced" if reduced else "normal"}-{replay}'
                png = output / f'{name}.png'
                page.screenshot(path=str(png),full_page=False)
                bounds = page.locator('svg').bounding_box()
                if bounds is None:
                    state['findings'].append('Rendered SVG has no bounds.')
                else:
                    image = Image.open(png).convert('RGB')
                    for sample in state['samples']:
                        x = round(sample['screenPoint']['x'] + bounds['x'])
                        y = round(sample['screenPoint']['y'] + bounds['y'])
                        observed = list(image.getpixel((x,y)))
                        sample['observedRgb'] = observed
                        sample['maximumChannelError'] = max(abs(a-b) for a,b in zip(observed,sample['expectedRgb']))
                        if sample['maximumChannelError'] > 5:
                            state['findings'].append(f'Actual source-over pixel disagrees by {sample["maximumChannelError"]:.3f} channel units.')
                state['clean'] = not state['findings']
                report['states'].append(state)
            page.close()
        browser.close()
    report['passed'] = not report['errors'] and not report['networkRequests'] and len(report['states']) == 6 and all(state['clean'] for state in report['states'])
    (output/'independent-grade.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'renderedStates':len(report['states']),
                      'errors':report['errors'],'networkRequests':report['networkRequests'],
                      'findings':{f"{state['format']}/{state['reducedMotion']}/{state['replay']}":state['findings'] for state in report['states']}}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
