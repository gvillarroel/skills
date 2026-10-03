#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Capture a procedural SVG with native browser motion and reduced-motion review."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg', type=Path)
    parser.add_argument('--screenshot', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--wait-ms', type=int, default=900)
    parser.add_argument('--browser-channel')
    args = parser.parse_args()
    source = args.svg.resolve()
    if source == args.screenshot.resolve() or (args.report and source == args.report.resolve()):
        parser.error('Source, screenshot and report paths must differ')
    if not source.is_file() or not 0 <= args.wait_ms <= 120000:
        parser.error('Provide an existing SVG and wait-ms in 0..120000')
    findings = []
    with sync_playwright() as playwright:
        browser = None
        launch_errors = []
        for channel in ([args.browser_channel] if args.browser_channel else [None, 'msedge', 'chrome']):
            try:
                browser = playwright.chromium.launch(**({'channel':channel} if channel else {}))
                break
            except Exception as error:
                launch_errors.append(str(error).splitlines()[0])
        if browser is None:
            raise RuntimeError('No local Chromium browser available: ' + '; '.join(launch_errors))
        try:
            page = browser.new_page(viewport={'width':1100,'height':850})
            page.on('pageerror', lambda error: findings.append(str(error)))
            page.goto(source.as_uri(), wait_until='load')
            svg = page.locator('svg').first
            baseline = svg.screenshot()
            page.wait_for_timeout(args.wait_ms)
            args.screenshot.parent.mkdir(parents=True,exist_ok=True)
            current = svg.screenshot(path=str(args.screenshot.resolve()))
            evidence = page.evaluate('''() => {
              const svg=document.documentElement;
              return {palette:svg.getAttribute('data-palette'),patternId:svg.getAttribute('data-pattern-id'),motion:svg.getAttribute('data-motion'),viewBox:svg.getAttribute('viewBox'),drawingElements:svg.querySelectorAll('path,circle,rect,line,polygon,polyline,text').length};
            }''')
            page.emulate_media(reduced_motion='reduce')
            page.reload(wait_until='load')
            reduced = page.locator('svg').first.screenshot()
            evidence.update({'ok':not findings and evidence['drawingElements'] >= 4,'pageErrors':findings,'firstFrameSha256':hashlib.sha256(baseline).hexdigest(),'intermediateFrameSha256':hashlib.sha256(current).hexdigest(),'frameChanged':baseline != current,'reducedFrameSha256':hashlib.sha256(reduced).hexdigest(),'screenshot':str(args.screenshot),'browserChannel':channel or 'managed-chromium'})
        finally:
            browser.close()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2))
    return 0 if evidence['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
