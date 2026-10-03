#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Capture independently rendered treemap geometry and paint for review."""

import argparse
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


DOM_REVIEW = r"""() => {
  const svg = document.querySelector('svg');
  if (!svg) throw new Error('The artifact has no rendered SVG.');
  const box = element => {
    const b = element.getBoundingClientRect();
    return {x:b.x, y:b.y, width:b.width, height:b.height};
  };
  const items = Array.from(svg.querySelectorAll('rect,path,text')).map(element => {
    const style = getComputedStyle(element);
    const attributes = Object.fromEntries(Array.from(element.attributes).map(a => [a.name,a.value]));
    let effectiveOpacity = 1;
    for (let ancestor = element; ancestor; ancestor = ancestor.parentElement) {
      effectiveOpacity *= Number.parseFloat(getComputedStyle(ancestor).opacity || '1');
    }
    const datum = element.__data__;
    const text = element.localName === 'text' && element.querySelector('tspan') ?
      Array.from(element.childNodes).map(node => node.textContent.trim()).filter(Boolean).join(' ') : element.textContent.trim();
    return {tag:element.localName, text, attributes,
      fill:style.fill, stroke:style.stroke, strokeWidth:style.strokeWidth,
      opacity:style.opacity, effectiveOpacity, fillOpacity:style.fillOpacity, fontSize:style.fontSize,
      datum:datum && typeof datum === 'object' ? {name:datum.data?.name || datum.name,
        parent:datum.parent?.data?.name, value:datum.value,
        depth:datum.depth, children:datum.children?.length} : null,
      box:box(element), parentAttributes:element.parentElement ?
        Object.fromEntries(Array.from(element.parentElement.attributes).map(a => [a.name,a.value])) : {}};
  });
  return {svgAttributes:Object.fromEntries(Array.from(svg.attributes).map(a => [a.name,a.value])),
    title:svg.querySelector('title')?.textContent,
    description:svg.querySelector('desc')?.textContent,
    svgBox:box(svg), documentWidth:document.documentElement.scrollWidth,
    viewportWidth:innerWidth, items};
}"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--basename', default='portfolio-treemap')
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {'workspace': str(workspace), 'states': []}
    with sync_playwright() as playwright:
        options = {}
        if sys.platform == 'win32' and not Path(playwright.chromium.executable_path).exists():
            options['channel'] = 'msedge'
        browser = playwright.chromium.launch(**options)
        for extension in ['html', 'svg']:
            artifact = workspace / f'{args.basename}.{extension}'
            for width in [960, 420]:
                context = browser.new_context(viewport={'width': width, 'height': 720}, reduced_motion='reduce')
                page = context.new_page()
                errors, network = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: network.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
                page.goto(artifact.as_uri(), wait_until='load')
                page.wait_for_timeout(1200)
                state = page.evaluate(DOM_REVIEW)
                state.update({'format':extension, 'width':width, 'pageErrors':errors, 'networkRequests':network})
                page.screenshot(path=str(output / f'{extension}-{width}.png'), full_page=False)
                report['states'].append(state)
                context.close()
        browser.close()
    destination = output / 'render-review.json'
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report':str(destination), 'renderedStates':len(report['states']),
                      'pageErrors':sum(len(state['pageErrors']) for state in report['states']),
                      'networkRequests':sum(len(state['networkRequests']) for state in report['states'])}))


if __name__ == '__main__':
    main()
