#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "pillow>=10.0.0"]
# ///
"""Independently inspect exact colors, scenario arithmetic, and rendered text."""

import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
LOCAL = ROOT / "projects/svg-text-contrast/artifacts"
sys.path.insert(0, str(ROOT / "skills/compose-synchronized-svg/scripts"))
from playwright.sync_api import sync_playwright
from text_contrast import audit_text_contrast


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    results = []
    cohort = read(LOCAL / "luna-cohort.json")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for row in cohort:
            workspace = ROOT / "evaluations/runs" / row["runId"] / "workspace"
            record = {"runId": row["runId"], "errors": [], "textStates": []}
            destination = LOCAL / "luna" / row["case"]
            destination.mkdir(parents=True, exist_ok=True)
            try:
                folder = "boundary" if row["case"] == "boundary" else "pairs" if row["case"] == "contract" else "dark"
                outputs = workspace / "outputs" / folder
                brief = read(outputs / "brief.json")
                if folder == "boundary":
                    assert brief["theme"] == {"colors": {"canvas": "#fff0a8", "surface": "#fff0a8", "ink": "#ffffff"}}
                    assert read(outputs / "preflight.json")["ok"] is False
                    assert not [path for path in workspace.rglob("*.svg") if "skills" not in path.relative_to(workspace).parts]
                    record["rejectedWithoutChangingColorsOrPublishingSvg"] = True
                else:
                    plan = read(outputs / "plan.json")
                    expected = {"canvas": "#ffffff", "surface": "#ffffff", "ink": "#767676", "muted": "#767676"} if folder == "pairs" else {"canvas": "#101820", "surface": "#18242f"}
                    for role, color in expected.items():
                        assert brief["theme"]["colors"][role] == color and plan["theme"]["colors"][role] == color, role
                    if folder == "pairs":
                        assert plan["theme"]["conceptColors"]["input-rate"] == "#888888"
                        template = read(ROOT / "skills/compose-synchronized-svg/assets/templates/composition-brief.json")
                        for key in ("concepts", "derived", "modules", "scenarios"):
                            assert brief[key] == template[key], key
                    svg = outputs / ("atlas.svg" if folder == "pairs" else "dashboard.svg")
                    if folder == "dark":
                        command = ["uv", "run", "--script", "evaluations/contracts/inspect-svg-color-cases.py", str(svg), "--topic", "water", "--output", str(destination)]
                        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                        assert result.returncode == 0, result.stderr or result.stdout
                        record["arithmetic"] = read(destination / "independent-check.json")
                        mapping = record["arithmetic"]["inputMapping"]
                        concepts = {item["id"]: item for item in plan["concepts"]}
                        for role, domain in {"demand": [0, 240], "capacity": [80, 220], "fraction": [0, .35]}.items():
                            assert concepts[mapping[role]]["domain"] == domain, role
                        expected_scenarios = {(120, 150, .15), (180, 150, .20), (180, 150, .08)}
                        actual_scenarios = {tuple(item["values"][mapping[role]] for role in ("demand", "capacity", "fraction")) for item in plan["scenarios"]}
                        assert actual_scenarios == expected_scenarios
                    page = browser.new_page(viewport={"width": 1600, "height": 1000})
                    page.goto(svg.as_uri())
                    page.wait_for_function("window.svgSync && document.documentElement.dataset.syncReady === 'true'")
                    page.evaluate("() => {svgSync.pause();svgSync.pauseCamera();}")
                    for role, color in expected.items():
                        assert page.evaluate("role => getComputedStyle(document.documentElement).getPropertyValue('--'+role).trim().toLowerCase()", role) == color
                    scenarios = page.evaluate("() => svgSync.getPlan().scenarios")
                    for scenario in scenarios:
                        page.evaluate("id => svgSync.applyScenario(id)", scenario["id"])
                        page.wait_for_timeout(150)
                        snapshot = page.evaluate("() => svgSync.serializeSnapshot()")
                        contrast = audit_text_contrast(page)
                        assert snapshot == page.evaluate("() => svgSync.serializeSnapshot()")
                        record["textStates"].append({"scenario": scenario["id"], **{k: v for k, v in contrast.items() if k != "findings"}})
                        assert contrast["ok"], contrast
                    if folder == "dark":
                        page.evaluate("patch => svgSync.setState(patch)", {mapping["demand"]: 0, mapping["capacity"]: 150, mapping["fraction"]: .15})
                        contrast = audit_text_contrast(page)
                        record["textStates"].append({"scenario": "zero", **{k: v for k, v in contrast.items() if k != "findings"}})
                        assert contrast["ok"], contrast
                    page.close()
            except (AssertionError, OSError, KeyError, ValueError) as error:
                record["errors"].append(str(error))
            record["ok"] = not record["errors"]
            results.append(record)
            print(json.dumps({"runId": row["runId"], "ok": record["ok"], "errors": record["errors"]}), flush=True)
        browser.close()
    (LOCAL / "luna-independent.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 1 if any(not item["ok"] for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
