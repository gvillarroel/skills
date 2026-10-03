#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently inspect decoding text, offline paint, motion, replay and exact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from playwright.sync_api import Error, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
NS = {"s": "http://www.w3.org/2000/svg"}
CASES = {
    "naturalistic": [("decode", ["the", "answer", "is", "42", "next"], 720, 440, "colorset2", [])],
    "contract": [("contract", ["A", "tiny", "test", "works"], 800, 480, "colorset1", [])],
    "generalization": [("transfer", ["We", "can", "ship", "this", "small", "change", "today"], 960, 520, "colorset2", ["may", "large"])],
    "boundary": [("zero", ["A", "small", "test", "Start"], 720, 440, "colorset1", []),
                 ("all", ["We", "are", "ready", "now"], 720, 440, "colorset1", [])],
}


TEXT_INSPECTION = """() => {
  const svg=document.querySelector('svg'), frame=svg.getBoundingClientRect();
  const nodes=[...svg.querySelectorAll('text')].filter(n=>n.textContent.trim());
  return nodes.map(n=>{
    const r=n.getBoundingClientRect(); let opacity=1, shown=true;
    for(let p=n;p&&p instanceof Element;p=p.parentElement){const s=getComputedStyle(p);opacity*=Number(s.opacity);shown&&=s.display!=='none'&&s.visibility!=='hidden';}
    const blockers=new Set();
    // Only a later painted element above actual glyph hit points is an
    // obstruction. Empty glyph space and behind-text cards are not failures.
    for(let row=1;row<5;row++) for(let col=1;col<16;col++){
      const stack=document.elementsFromPoint(r.left+r.width*col/16,r.top+r.height*row/5);
      const at=stack.indexOf(n); if(at<0) continue;
      for(const p of stack.slice(0,at)){
        if(!(p instanceof SVGElement)||p===svg||n.contains(p)||p.contains(n)) continue;
        const s=getComputedStyle(p); let o=Number(s.opacity);
        for(let a=p.parentElement;a&&a!==svg;a=a.parentElement)o*=Number(getComputedStyle(a).opacity);
        if(o>.1&&s.display!=='none'&&s.visibility!=='hidden'&&(s.fill!=='none'||s.stroke!=='none')) blockers.add(p.tagName+':'+(p.id||p.getAttribute('class')||''));
      }
    }
    return {text:n.textContent.trim(), visible:shown&&opacity>.95&&r.width>0&&r.height>0,
      inside:r.left>=frame.left-1&&r.right<=frame.right+1&&r.top>=frame.top-1&&r.bottom<=frame.bottom+1,
      blockers:[...blockers],box:{x:r.x-frame.x,y:r.y-frame.y,width:r.width,height:r.height}};
  });
}"""


def sample_time(page, seconds: float) -> None:
    page.evaluate("""seconds=>{
      for(const svg of document.querySelectorAll('svg')){
        if(svg.pauseAnimations) svg.pauseAnimations();
        if(svg.setCurrentTime) svg.setCurrentTime(seconds);
      }
      for(const a of document.getAnimations()){
        const timing=a.effect.getComputedTiming();
        if(Number.isFinite(timing.endTime)){a.pause();a.currentTime=Math.min(seconds*1000,timing.endTime);}
      }
    }""", seconds)
    # Force the next painted frame rather than reading stale animation style.
    page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", action="append", required=True)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--skip-harness", action="store_true", help="Only for non-LLM deterministic contract checks")
    args = parser.parse_args()
    results = []
    with sync_playwright() as pw:
        browser = None
        for channel in (None, "msedge", "chrome"):
            try:
                browser = pw.chromium.launch(headless=True, **({"channel": channel} if channel else {}))
                break
            except Error:
                continue
        if browser is None:
            raise RuntimeError("No installed Chromium browser is available")
        for run_id in args.run_id:
            run = ROOT / "evaluations/runs" / run_id
            checks, samples, screenshots, errors, requests = {}, [], [], [], []
            if not args.skip_harness:
                checks["strictHarness"] = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))["passed"]
            for stem, tokens, width, height, colorset, alternates in CASES[args.case]:
                html, svg_path = (run / "workspace/out" / f"{stem}.{extension}" for extension in ("html", "svg"))
                prefix = stem + ":"
                checks[prefix + "exactOutputs"] = all(p.is_file() and p.stat().st_size > 0 for p in (html, svg_path))
                if not checks[prefix + "exactOutputs"]:
                    continue
                svg = ET.parse(svg_path).getroot()
                checks[prefix + "dimensions"] = svg.attrib.get("viewBox") == f"0 0 {width} {height}"
                checks[prefix + "accessible"] = all(svg.find("s:" + name, NS) is not None and (svg.find("s:" + name, NS).text or "").strip() for name in ("title", "desc"))
                checks[prefix + "portableSvg"] = not any(svg.findall(".//s:" + tag, NS) for tag in ("script", "foreignObject", "image"))
                for path in (html, svg_path):
                    command = [sys.executable, str(ROOT / "skills/d3/scripts/check_palette_contract.py"), str(path), "--colorset", colorset]
                    if colorset == "colorset2":
                        command.append("--require-extended")
                    result = subprocess.run(command, capture_output=True, text=True)
                    checks[prefix + path.suffix + "Palette"] = result.returncode == 0
                    if result.returncode:
                        errors.append(result.stdout + result.stderr)
                page = browser.new_page(viewport={"width": width + 40, "height": height + 100})
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("request", lambda req: requests.append(req.url) if req.url.startswith(("http://", "https://")) else None)
                page.route("http://**/*", lambda route: route.abort())
                page.route("https://**/*", lambda route: route.abort())
                try:
                    for extension, path in (("html", html), ("svg", svg_path)):
                        page.goto(path.as_uri(), wait_until="load")
                        motion_states = []
                        for seconds in (0, .45, 1.25, 2.25, 3.4, 20):
                            sample_time(page, seconds)
                            rows = page.evaluate(TEXT_INSPECTION)
                            # Intro animation may reveal text. Every visible
                            # glyph must remain unobstructed; all tokens must
                            # be visible and inside the frame after settlement.
                            key = prefix + extension + f"@{seconds:g}"
                            checks[key + "Unobstructed"] = all(not r["blockers"] for r in rows if r["visible"])
                            checks[key + "Bounds"] = all(r["inside"] for r in rows if r["visible"])
                            if seconds >= 3.4:
                                checks[key + "ExactTokens"] = all(sum(r["text"] == token and r["visible"] for r in rows) == 1 for token in tokens)
                                checks[key + "Alternates"] = all(any(r["text"] == label and r["visible"] for r in rows) for label in alternates)
                                checks[key + "VisibleText"] = all(r["visible"] for r in rows)
                            samples.append({"artifact": stem + "." + extension, "time": seconds, "texts": rows})
                            if seconds in (.45, 1.25, 2.25):
                                state = page.evaluate("""() => [...document.querySelectorAll('svg rect,svg circle,svg path,svg line')].map(n=>{
                                  const b=n.getBBox(),s=getComputedStyle(n),m=n.getCTM();
                                  return [n.tagName,b.x,b.y,b.width,b.height,s.opacity,s.fill,s.stroke,m.a,m.b,m.c,m.d,m.e,m.f];
                                })""")
                                motion_states.append(json.dumps(state))
                                if extension == "html" and seconds in (.45, 1.25):
                                    screenshot = ROOT / "projects/skill-authoring-audit/artifacts/screenshots" / f"{run_id}-{stem}-motion-{seconds:g}.png"
                                    screenshot.parent.mkdir(parents=True, exist_ok=True)
                                    page.screenshot(path=str(screenshot), full_page=False)
                                    screenshots.append(screenshot.relative_to(ROOT).as_posix())
                        if extension == "html":
                            checks[prefix + "VisibleMotion"] = len(set(motion_states)) > 1
                        screenshot = ROOT / "projects/skill-authoring-audit/artifacts/screenshots" / f"{run_id}-{stem}-{extension}.png"
                        screenshot.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(screenshot), full_page=False)
                        screenshots.append(screenshot.relative_to(ROOT).as_posix())
                        if extension == "html":
                            button = page.get_by_role("button", name="Replay", exact=False).first
                            checks[prefix + "Replay"] = button.count() == 1
                            for repetition in (1, 2):
                                button.click()
                                sample_time(page, 20)
                                rows = page.evaluate(TEXT_INSPECTION)
                                checks[prefix + f"Replay{repetition}"] = all(any(r["text"] == t and r["visible"] and r["inside"] and not r["blockers"] for r in rows) for t in tokens)
                        page.emulate_media(reduced_motion="reduce")
                        page.reload(wait_until="load")
                        sample_time(page, 0)
                        rows = page.evaluate(TEXT_INSPECTION)
                        checks[prefix + extension + "ReducedMotionInitial"] = all(any(r["text"] == t and r["visible"] and r["inside"] and not r["blockers"] for r in rows) for t in tokens)
                        sample_time(page, 20)
                        rows = page.evaluate(TEXT_INSPECTION)
                        checks[prefix + extension + "ReducedMotion"] = all(any(r["text"] == t and r["visible"] and r["inside"] and not r["blockers"] for r in rows) for t in tokens)
                        page.emulate_media(reduced_motion="no-preference")
                except (Error, OSError, ValueError) as error:
                    errors.append(str(error))
                    checks[prefix + "BrowserInspection"] = False
                finally:
                    page.close()
            checks["offline"] = not requests
            checks["noBrowserErrors"] = not errors
            results.append({"run": run_id, "case": args.case, "passed": all(checks.values()), "checks": checks,
                            "samples": samples, "screenshots": screenshots, "errors": errors, "requests": requests,
                            "manualSemanticReviewRequired": True})
        browser.close()
    report = {"passed": all(r["passed"] for r in results), "case": args.case, "results": results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "results": [{"run": r["run"], "passed": r["passed"], "failedChecks": [k for k, v in r["checks"].items() if not v], "errors": r["errors"]} for r in results]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
