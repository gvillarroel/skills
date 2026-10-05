#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Verify the deployed catalog and actual native timeline click/motion states."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.request import urlopen
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
PATTERN_ID = "slidev-animejs-timeline-machine"
INDEX_URL = "https://gvillarroel.github.io/skills/"
EXAMPLE_URL = INDEX_URL + "examples/slidev-animejs/#/20"

SNAPSHOT = """root => {
  const box=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,right:b.right,bottom:b.bottom,width:b.width,height:b.height}};
  const stage=root.querySelector('.svg-asset-stage'),s=box(stage),bases=[...root.querySelectorAll('.machine-cable-base')],cables=[...root.querySelectorAll('.machine-cable')];
  const query=location.hash.includes('?')?location.hash.split('?')[1]:location.search;
  return {stage:s,clickIndex:Number(new URLSearchParams(query).get('clicks')||0),onScreen:s.x>=0&&s.right<=innerWidth&&s.y>=0&&s.bottom<=innerHeight,
    baseCount:bases.length,complete:bases.every((b,i)=>b.getAttribute('d')===cables[i].getAttribute('d')&&getComputedStyle(b).strokeDasharray==='none'&&Number(getComputedStyle(b).opacity)>=.8),
    movers:[...root.querySelectorAll('.machine-signal,.machine-gear,.machine-block')].map(e=>{const b=box(e);return{kind:e.getAttribute('class'),bounds:b,transform:getComputedStyle(e).transform,inside:b.x>=s.x&&b.right<=s.right&&b.y>=s.y&&b.bottom<=s.bottom}})};
}"""


def semantic_pass(frame: dict) -> bool:
    return (frame['onScreen'] and frame['baseCount'] == 2 and frame['complete']
            and len(frame['movers']) == 6 and all(mover['inside'] for mover in frame['movers']))


def observed_motion(samples: list[dict]) -> bool:
    return len({json.dumps(frame['movers'], sort_keys=True) for frame in samples}) > 1


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "projects/diagram-compactness/artifacts/reviews/published-example")
    parser.add_argument("--local-pages", action="store_true", help="Exercise the same verifier against the generated Pages tree before publishing.")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.is_relative_to(ROOT):
        parser.error("The output directory must stay inside the project workspace.")
    output.mkdir(parents=True, exist_ok=True)
    server = None
    thread = None
    index_url = INDEX_URL
    if args.local_pages:
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'dist/pages')))
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        index_url = f'http://127.0.0.1:{server.server_port}/'
    example_url = index_url + 'examples/slidev-animejs/#/20'
    with urlopen(index_url, timeout=30) as response:
        index = response.read().decode("utf-8")
    report = {"patternId": PATTERN_ID, "publishedUrl": EXAMPLE_URL, "verifiedUrl": example_url,
              "catalogListed": "examples/slidev-animejs/" in index,
              "states": [], "pageErrors": []}
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {"channel": "msedge"}
        browser = runtime.chromium.launch(**options)
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            parsed = urlsplit(index_url)
            context.grant_permissions(["screen-wake-lock"], origin=f'{parsed.scheme}://{parsed.netloc}')
            page = context.new_page()
            page.on("pageerror", lambda error: report["pageErrors"].append(str(error)))
            page.goto(example_url, wait_until="networkidle")
            selector = f'.slidev-page-20 [data-pattern-id="{PATTERN_ID}"].svg-asset-slide'
            page.locator(selector).wait_for(state="visible")
            for state in range(3):
                if state:
                    page.keyboard.press("ArrowRight")
                    page.wait_for_function("expected => Number(new URLSearchParams(location.hash.includes('?')?location.hash.split('?')[1]:location.search).get('clicks')||0) === expected", arg=state)
                frame = {"state": state, "url": page.url, "samples": []}
                if "/20" not in page.url:
                    frame["leftTimelineSlide"] = True
                    report["states"].append(frame)
                    break
                for sample in range(35):
                    frame["samples"].append(page.locator(selector).evaluate(SNAPSHOT))
                    if sample in (5, 20, 34):
                        page.screenshot(path=str(output / f"state-{state}-motion-{sample}.png"))
                    page.wait_for_timeout(100)
                report["states"].append(frame)
            page.reload(wait_until="networkidle")
            page.locator(selector).wait_for(state="visible")
            page.wait_for_timeout(300)
            report["replaySamples"] = []
            for _ in range(12):
                report["replaySamples"].append(page.locator(selector).evaluate(SNAPSHOT))
                page.wait_for_timeout(100)
            page.screenshot(path=str(output / "replay.png"))
            page.emulate_media(reduced_motion="reduce")
            page.wait_for_timeout(300)
            report["reducedSamples"] = []
            for _ in range(12):
                report["reducedSamples"].append(page.locator(selector).evaluate(SNAPSHOT))
                page.wait_for_timeout(100)
            page.screenshot(path=str(output / "reduced.png"))
        finally:
            browser.close()
            if server:
                server.shutdown()
                server.server_close()
                thread.join(timeout=10)
    report["motionObserved"] = all(observed_motion(state['samples']) for state in report['states'])
    report["replayMotionObserved"] = observed_motion(report.get('replaySamples', []))
    block_extents = [max((mover['bounds']['right'] - sample['stage']['x']
                          for sample in state['samples'] for mover in sample['movers']
                          if 'machine-block' in mover['kind']), default=0)
                     for state in report['states']]
    report['blockMaximumRightByClick'] = block_extents
    block_minimum = [min((mover['bounds']['x'] - sample['stage']['x']
                          for sample in state['samples'] for mover in sample['movers']
                          if 'machine-block' in mover['kind']), default=0)
                     for state in report['states']]
    report['blockMinimumLeftByClick'] = block_minimum
    # Anime.js writes the SVG rectangle's x attribute. The inherited maximum
    # x is common to every alternating timeline; the second step changes the
    # other end of travel from x=214 to x=286. Verify the observed native range.
    report['stepTwoTravelVariantObserved'] = (len(block_extents) == 3
                                              and (abs(block_minimum[2] - block_minimum[0]) > 10
                                                   or abs(block_extents[2] - block_extents[0]) > 10))
    report["passed"] = (report["catalogListed"] and len(report["states"]) == 3
                        and not report["pageErrors"] and report['motionObserved'] and report['replayMotionObserved']
                        and report['stepTwoTravelVariantObserved']
                        and all(semantic_pass(frame) for frame in report.get('replaySamples', []))
                        and len(report.get('replaySamples', [])) == 12
                        and all(semantic_pass(frame) for frame in report.get('reducedSamples', []))
                        and len(report.get('reducedSamples', [])) == 12
                        and all(not state.get("leftTimelineSlide")
                                and all(frame['clickIndex'] == state['state'] and semantic_pass(frame)
                                        for frame in state["samples"])
                                for state in report["states"]))
    (output / "browser.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "catalogListed": report["catalogListed"],
                      "pageErrors": report["pageErrors"], "urls": [state["url"] for state in report["states"]],
                      "report": str(output / "browser.json")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
