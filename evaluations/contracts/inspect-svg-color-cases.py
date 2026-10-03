#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independent browser and arithmetic evidence for the water/microgrid color cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


def identify(records: list[dict], patterns: dict[str, str]) -> dict[str, str]:
    result = {}
    for role, pattern in patterns.items():
        candidates = [record["id"] for record in records if re.search(pattern, record["id"] + " " + record.get("label", ""), re.I)]
        if len(candidates) != 1:
            raise ValueError(f"Cannot unambiguously identify {role}: {candidates}")
        result[role] = candidates[0]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--topic", choices=["water", "microgrid"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"ok": False, "topic": args.topic, "svg": str(args.svg), "sha256": hashlib.sha256(args.svg.read_bytes()).hexdigest(), "states": [], "errors": []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1000}, reduced_motion="reduce")
        page = context.new_page()
        page.on("pageerror", lambda error: report["errors"].append(str(error)))
        page.goto(args.svg.resolve().as_uri())
        page.wait_for_function("() => window.svgSync && document.documentElement.dataset.syncReady === 'true'")
        plan = page.evaluate("() => window.svgSync.getPlan()")
        if args.topic == "water":
            inputs = identify(plan["concepts"], {"demand": "demand", "capacity": "capacity", "fraction": "leak"})
            outputs = identify(plan["derived"], {"processed": "processed", "delivered": "deliver", "leakage": "leak", "unmet": "unmet", "load": "load"})
            cases = [("normal", (120, 150, .15)), ("peak", (180, 150, .20)), ("repair", (180, 150, .08)), ("zero", (0, 150, .15))]
        else:
            inputs = identify(plan["concepts"], {"demand": "demand", "solar": "solar", "wind": "wind", "capacity": "capacity"})
            outputs = identify(plan["derived"], {"renewables": "renewable.*(total|output|available|generation)|total.*renewable", "used": "renewable.*used|used.*renewable", "imports": "import", "curtailed": "curtail", "load": "load", "share": "renewable.*(share|fraction)"})
            cases = [("morning", (90, 35, 25, 120)), ("midday", (110, 100, 45, 120)), ("evening", (145, 10, 30, 120)), ("zero", (0, 10, 30, 120))]
        report["inputMapping"], report["outputMapping"] = inputs, outputs
        report["theme"] = plan.get("theme")
        for name, values in cases:
            patch = dict(zip(inputs.values(), values))
            if args.topic == "water":
                demand, capacity, fraction = values
                processed = min(demand, capacity)
                leakage = processed * fraction
                expected = {"processed": processed, "leakage": leakage, "delivered": processed - leakage, "unmet": demand - processed, "load": demand / capacity}
            else:
                demand, solar, wind, capacity = values
                renewables = solar + wind
                used = min(demand, renewables)
                expected = {"renewables": renewables, "used": used, "imports": demand - used, "curtailed": renewables - used, "load": demand / capacity, "share": used / max(demand, 1)}
            snapshot = page.evaluate("patch => window.svgSync.setState(patch)", patch)
            actual = snapshot["derivedValues"]
            errors = [f"{role}: expected {value}, got {actual.get(outputs[role])}" for role, value in expected.items() if not math.isclose(actual.get(outputs[role], math.nan), value, rel_tol=1e-9, abs_tol=1e-9)]
            bound = page.evaluate("() => [...document.querySelectorAll('[data-bind]')].map(n=>({id:n.dataset.bind,value:Number(n.dataset.currentValue)}))")
            canonical = {**snapshot["sourceValues"], **actual}
            for item in bound:
                if not math.isclose(item["value"], canonical[item["id"]], rel_tol=1e-9, abs_tol=1e-9):
                    errors.append(f"Stale bound mark: {item['id']}")
            page.screenshot(path=str(args.output / f"{name}.png"), animations="disabled")
            if name == cases[0][0]:
                for index, module in enumerate(page.locator("[data-module-id]").all()):
                    module.screenshot(path=str(args.output / f"module-{index + 1}.png"), animations="disabled")
            report["states"].append({"name": name, "sourceValues": snapshot["sourceValues"], "expected": expected, "actual": {role: actual[identity] for role, identity in outputs.items()}, "boundMarkCount": len(bound), "errors": errors})
            report["errors"].extend(f"{name}: {error}" for error in errors)
        report["typography"] = page.evaluate("""() => ['.title','.module-kicker','.module-question','.module-claim','.module-content text','.relationship-key-label'].map(selector=>{const n=document.querySelector(selector);const s=n&&getComputedStyle(n);return {selector,fontSize:s?.fontSize,fill:s?.fill};})""")
        if args.topic == "microgrid":
            expected_brand = {"canvas": "#f8faf9", "surface": "#ffffff", "ink": "#172d2a", "muted": "#526663", "accent": "#087f78"}
            for role, color in expected_brand.items():
                rendered = page.evaluate("role => getComputedStyle(document.documentElement).getPropertyValue('--'+role).trim().toLowerCase()", role)
                if rendered != color:
                    report["errors"].append(f"Brand role {role}: expected {color}, got {rendered}")
        context.close()
        browser.close()
    report["ok"] = not report["errors"]
    (args.output / "independent-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "states": len(report["states"]), "errors": report["errors"], "report": str(args.output / "independent-check.json")}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
