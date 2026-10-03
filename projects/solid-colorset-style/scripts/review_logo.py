#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Inspect actual logo contact-sheet captions while preserving source logo pixels."""
import json
from pathlib import Path
import subprocess
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts"


def main():
    html = ART / "previews/logo-audit.html"
    result = subprocess.run([sys.executable, "skills/technical-logo-assets/scripts/build_logo_audit.py", "--output", str(html)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr)
    states = []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        for width in (1440, 390):
            page = browser.new_page(viewport={"width": width, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(html.as_uri())
            page.wait_for_selector(".unavailable p")
            state = page.evaluate(r'''() => {
              const issues=[];
              const lum=c=>{const v=c.match(/[\d.]+/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2]};
              for(const n of document.querySelectorAll('.cell label,.cell p,button')){const s=getComputedStyle(n),b=getComputedStyle(n.closest('.cell')||n),L=lum(b.backgroundColor),expected=(L+.05)/.05>=1.05/(L+.05)?'rgb(0, 0, 0)':'rgb(255, 255, 255)';if(s.color!==expected)issues.push({text:n.textContent,color:s.color,background:b.backgroundColor,expected})}
              const borders=[...document.querySelectorAll('.cell,button,select')].filter(n=>parseFloat(getComputedStyle(n).borderTopWidth)>0).length;
              return {issues,borders,unavailableParagraphs:document.querySelectorAll('.unavailable p').length,rows:document.querySelectorAll('.row').length,overflow:document.documentElement.scrollWidth>innerWidth+1};
            }''')
            state.update(width=width, errors=errors)
            states.append(state)
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            screenshot = ART / "screenshots" / f"logo-captions-{width}.png"
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot))
            page.close()
        browser.close()
    findings = [row for row in states if row["issues"] or row["borders"] or row["errors"] or row["overflow"] or row["rows"] != 12]
    report = {"date": "2026-10-03", "passed": not findings, "states": states, "findings": findings,
              "scope": "Computed caption/button contrast and borderless chrome at desktop/mobile; original vector/logo paints are source identity and excluded."}
    destination = ROOT / "evaluations/solid-colorset-style/logo-browser-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "states": len(states), "findings": findings}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
