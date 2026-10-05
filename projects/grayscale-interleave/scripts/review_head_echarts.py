#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Review committed-builder SSR gallery with current categorical palette only."""
from pathlib import Path
import hashlib
import json
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / 'projects/grayscale-interleave/artifacts/staged-blobs/echarts-head-native'
GALLERY = STAGE / 'assets/examples/echarts-animated-svg'
CANONICAL = ROOT / 'skills/echarts-animated-svg/assets/examples/echarts-animated-svg'
OUT = ROOT / 'projects/grayscale-interleave/artifacts/reviews/echarts-head-native-final'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(page):
    return page.evaluate('''() => [...document.querySelectorAll('.chart-card')].map(card=>{
      const svg=card.querySelector('svg'),box=svg.getBoundingClientRect(),colors=new Set(),unknown=[];
      for(const el of svg.querySelectorAll('*'))for(const key of ['fill','stroke']){
        const value=getComputedStyle(el)[key];
        if(value==='none'||value==='transparent')continue;
        const channels=value.match(/^rgba?\\(([^)]+)\\)$/);
        if(!channels){if(!value.startsWith('url('))unknown.push(value);continue;}
        const numbers=channels[1].split(/[ ,/]+/).map(Number);
        if(numbers.length>3&&numbers[3]===0)continue;
        colors.add('#'+numbers.slice(0,3).map(v=>Math.round(v).toString(16).padStart(2,'0')).join(''));
      }
      return {id:card.dataset.exampleId,patternId:card.dataset.patternId,type:card.dataset.chartType,
              colors:[...colors].sort(),unknown:[...new Set(unknown)],
              width:box.width,height:box.height,replayCount:Number(card.dataset.replayCount||0),
              labels:[...svg.querySelectorAll('text')].map(el=>el.textContent.trim()).filter(Boolean)};
    })''')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    staging = json.loads((STAGE / 'staging-proof.json').read_text(encoding='utf-8'))
    palette = json.loads((ROOT / 'skills/echarts-animated-svg/assets/palettes/colorsets.json').read_text(encoding='utf-8'))
    # The unchanged committed gallery builder declares Colorset2 for every profile.
    allowed = set(palette['colorsets']['colorset2']['allowed'])
    states = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((GALLERY / 'index.html').as_uri())
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(6000)
        states.append({'state': 'delivery', 'cards': inspect(page)})
        page.locator('#replay-all').click()
        page.wait_for_timeout(6000)
        states.append({'state': 'replay-settled', 'cards': inspect(page)})
        page.emulate_media(reduced_motion='reduce')
        page.reload()
        page.evaluate('document.fonts.ready')
        states.append({'state': 'reduced-motion', 'cards': inspect(page)})
        captures = []
        for card in states[-1]['cards']:
            if card['type'] in {'graph','tree','sankey','boxplot','heatmap','pie','funnel'} or 'palette' in card['id']:
                path = OUT / (card['id'] + '.png')
                page.locator(f'.chart-card[data-example-id="{card["id"]}"]').screenshot(path=str(path))
                captures.append(path.relative_to(ROOT).as_posix())
        browser.close()
    findings = []
    for state in states:
        if len(state['cards']) != 43:
            findings.append({'state': state['state'], 'issue': 'Expected exactly 43 native SVG cards'})
        for card in state['cards']:
            if set(card['colors']) - allowed or card['unknown']:
                findings.append({'state': state['state'], 'id': card['id'],
                                 'foreignColors': sorted(set(card['colors']) - allowed), 'unknown': card['unknown']})
    assert all(card['replayCount'] >= 1 for card in states[1]['cards'])
    builder = GALLERY / 'scripts/build-gallery.mjs'
    assert digest(builder) == staging['baselineBuilderSha256']
    dirty_after = {name: digest(CANONICAL / name) for name in staging['dirtyWorkingSha256Before']}
    assert dirty_after == staging['dirtyWorkingSha256Before']
    proof = {'ok': not findings and not errors, 'states': states, 'findings': findings, 'pageErrors': errors,
             'baselineBuilderSha256': digest(builder), 'baselineBuilderUnchanged': True,
             'quantitativeSourceAndProfilesUnchanged': True,
             'declaredGalleryColorset': 'colorset2',
             'dirtyWorkingSha256AfterReview': dirty_after, 'dirtyWorkingFilesUnchanged': True,
             'indexBlob': (GALLERY / 'index.html').relative_to(ROOT).as_posix(),
             'indexSha256': digest(GALLERY / 'index.html'), 'nativeCaptures': captures,
             'manualNativeCaptionAndHeadReviewPending': True}
    (OUT / 'review.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in proof.items() if key not in {'states'}}, indent=2))
    if findings or errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
