#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Check decoding HTML replay twice, final/reduced-motion text and matching portable SVG."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from playwright.sync_api import Error, sync_playwright


def settle(page) -> None:
    page.evaluate("""() => {
      for(const svg of document.querySelectorAll('svg')){
        if(svg.setCurrentTime)svg.setCurrentTime((svg.getCurrentTime?.()||0)+20);
        if(svg.pauseAnimations)svg.pauseAnimations();
      }
      for(const a of document.getAnimations())if(Number.isFinite(a.effect.getComputedTiming().endTime))a.finish();
    }""")
    page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")


def inspect_text(page) -> dict:
    return page.evaluate("""() => {
      const svg=document.querySelector('svg'),frame=svg.getBoundingClientRect();
      const rows=[...svg.querySelectorAll('text')].filter(n=>n.textContent.trim()).map(n=>{
        const r=n.getBoundingClientRect();let opacity=1,shown=true;
        for(let p=n;p&&p instanceof Element;p=p.parentElement){const s=getComputedStyle(p);opacity*=Number(s.opacity);shown&&=s.display!=='none'&&s.visibility!=='hidden';}
        return {text:n.textContent.trim(),visible:shown&&opacity>.95&&r.width>0&&r.height>0,
          inside:r.left>=frame.left-1&&r.right<=frame.right+1&&r.top>=frame.top-1&&r.bottom<=frame.bottom+1};
      });
      return {viewBox:svg.getAttribute('viewBox'),texts:rows};
    }""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--browser-channel", choices=["msedge", "chrome"])
    args = parser.parse_args()
    findings, checks, inspections = [], {}, []
    try:
        paths = [args.html.resolve(), args.svg.resolve()]
        bundle = Path(__file__).resolve().parents[1]
        outputs = [args.screenshot.resolve(), *([args.json_report.resolve()] if args.json_report else [])]
        if len(set(paths + outputs)) != len(paths + outputs):
            raise ValueError("Input and output paths must be distinct")
        if any(p.is_relative_to(bundle) for p in outputs):
            raise ValueError("Verification output must be outside the read-only skill bundle")
        root = ET.parse(paths[1]).getroot()
        namespace = {"s": "http://www.w3.org/2000/svg"}
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("The portable file must contain an SVG root")
        viewport = root.attrib.get("viewBox", "").split()
        if len(viewport) != 4 or viewport[:2] != ["0", "0"]:
            raise ValueError("Expected a zero-origin four-number SVG viewBox")
        width, height = (int(float(v)) for v in viewport[2:])
        if width < 100 or height < 100:
            raise ValueError("Expected a readable SVG viewport of at least 100 by 100")
        expected = Counter("".join(n.itertext()).strip() for n in root.findall(".//s:text", namespace) if "".join(n.itertext()).strip())
        if not expected:
            raise ValueError("The explanation needs visible SVG text")
        checks["portableSvg"] = not any(root.findall(".//s:" + tag, namespace) for tag in ("script", "foreignObject", "image"))
        checks["accessibleSvg"] = all(root.find("s:" + tag, namespace) is not None and (root.find("s:" + tag, namespace).text or "").strip() for tag in ("title", "desc"))
        with sync_playwright() as pw:
            browser = None
            for channel in ([args.browser_channel] if args.browser_channel else [None, "msedge", "chrome"]):
                try:
                    browser = pw.chromium.launch(headless=True, **({"channel": channel} if channel else {}))
                    break
                except Error:
                    continue
            if browser is None:
                raise ValueError("No installed Chromium browser is available; use --browser-channel with an installed Edge or Chrome")
            page = browser.new_page(viewport={"width": width + 40, "height": height + 100})
            errors, requests = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda req: requests.append(req.url) if req.url.startswith(("http://", "https://")) else None)
            page.route("http://**/*", lambda route: route.abort())
            page.route("https://**/*", lambda route: route.abort())

            def check(stage: str) -> None:
                result = inspect_text(page)
                inspections.append({"stage": stage, **result})
                checks[stage + "Text"] = Counter(r["text"] for r in result["texts"]) == expected
                checks[stage + "Visibility"] = all(r["visible"] and r["inside"] for r in result["texts"])
                checks[stage + "ViewBox"] = result["viewBox"].split() == viewport

            try:
                page.goto(paths[0].as_uri(), wait_until="load")
                settle(page)
                check("htmlFinal")
                button = page.get_by_role("button", name="Replay", exact=False).first
                checks["replayControl"] = button.count() == 1
                if checks["replayControl"]:
                    for repetition in (1, 2):
                        button.click()
                        settle(page)
                        check(f"replay{repetition}")
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot.resolve()), full_page=False)
                for label, path in (("html", paths[0]), ("svg", paths[1])):
                    page.goto(path.as_uri(), wait_until="load")
                    settle(page)
                    check(label + "Settled")
                    page.emulate_media(reduced_motion="reduce")
                    page.reload(wait_until="load")
                    settle(page)
                    check(label + "ReducedMotion")
                    page.emulate_media(reduced_motion="no-preference")
                checks["offline"] = not requests
                checks["noBrowserErrors"] = not errors
                findings.extend(errors)
            finally:
                page.close()
                browser.close()
    except (OSError, ValueError, ET.ParseError, Error) as error:
        findings.append(str(error))
    failed = [key for key, value in checks.items() if not value]
    report = {"passed": bool(checks) and not failed and not findings, "checks": checks, "failedChecks": failed,
              "findings": findings, "inspections": inspections, "screenshot": str(args.screenshot)}
    if args.json_report:
        # A rejected bundle/output path must never be written while reporting it.
        bundle = Path(__file__).resolve().parents[1]
        report_path = args.json_report.resolve()
        if report_path not in (args.html.resolve(), args.svg.resolve(), args.screenshot.resolve()) and not report_path.is_relative_to(bundle):
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "inspections"}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
