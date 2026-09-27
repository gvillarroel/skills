#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently inspect every completed composition forward-test artifact."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify_defaults import PALETTES, SVG_PROBE

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "projects/library-composition/artifacts"


def main():
    report_path = OUT / "forward-review.json"
    records = json.loads(report_path.read_text()) if report_path.exists() else []
    reviewed = {record["runId"] for record in records}
    runs = sorted((ROOT / "evaluations/runs").glob("threejs-compact-*-20260927-release-*"))
    runs += sorted((ROOT / "evaluations/runs").glob("d3-compact-*-20260927-verified-*"))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        for run in runs:
            if run.name in reviewed:
                continue
            result_path = run / "evaluation-result.json"
            if not result_path.exists():
                continue
            result = json.loads(result_path.read_text())
            workspace = run / "workspace"
            case = next(c for c in ("contract", "naturalistic", "boundary", "generalization") if f"-compact-{c}-" in run.name)
            library = "d3" if run.name.startswith("d3-") else "threejs"
            artifact = {
                "d3": {"contract": "flow.html", "naturalistic": "process.html", "boundary": "boundary.html", "generalization": "dashboard/index.html"},
                "threejs": {"contract": "scene.html", "naturalistic": "signal.html", "boundary": "extended.html", "generalization": "workers.html"},
            }[library][case]
            record = {"runId": run.name, "library": library, "case": case, "strictPassed": result["passed"], "checks": []}
            try:
                for width in (1280, 390):
                    context = browser.new_context(viewport={"width": width, "height": 844}, has_touch=width < 600)
                    page = context.new_page()
                    errors = []
                    requests = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
                    context.route("https://**", lambda route: route.abort())
                    page.goto((workspace / artifact).as_uri())
                    page.wait_for_timeout(1500)
                    if library == "d3":
                        data = page.evaluate(SVG_PROBE)
                        assert data["colorset"] == "colorset1", data
                        assert set(data["paints"]) <= set(PALETTES["colorset1"]["allowed"]), data
                        assert "#ffccd5" not in data["paints"]
                        assert data["overflow"] <= 1
                        assert all(node["fits"] for node in data["nodes"])
                        if case != "generalization":
                            expected = {"contract": ["Draft", "Review", "Publish"], "naturalistic": ["Intake", "Inspect", "Approve", "Dispatch"], "boundary": ["Intake", "Verify", "Deliver"]}[case]
                            assert page.locator("g.flow-node text").all_text_contents() == expected
                            if case == "boundary":
                                assert data["viewBox"] == "0 0 960 300"
                                assert all(abs(node["paddingY"] - 18) < .1 for node in data["nodes"])
                            else:
                                assert all(28 <= node["height"] <= 40 for node in data["nodes"])
                        else:
                            assert page.locator("g.kpi").count() == 4
                            assert page.locator("g.row").count() == 6
                        record["checks"].append({"width": width, "viewBox": data["viewBox"], "paints": data["paints"], "nodes": data["nodes"], "overflow": data["overflow"]})
                    else:
                        page.wait_for_function("window.__threeRuntimeSceneReady===true")
                        data = page.evaluate("window.__threeRuntimeScene.inspect()")
                        cs = "colorset2" if case == "boundary" else "colorset1"
                        assert data["colorset"] == cs
                        assert data["tokenCount"] == (12 if case == "generalization" else 5)
                        assert data["density"] == ("comfortable" if case == "boundary" else "compact")
                        assert set(data["materialColors"]) <= set(PALETTES[cs]["allowed"])
                        assert "#ffccd5" not in data["materialColors"]
                        assert set(data["lightColors"]) == {"#ffffff"}
                        frames = page.evaluate("""() => {const api=window.__threeRuntimeScene;return Array.from({length:41},(_,i)=>{api.renderAt(i*.5);return api.inspect().tokenBounds.every(p=>Math.abs(p[0])<=1&&Math.abs(p[1])<=1&&Math.abs(p[2])<=1)})}""")
                        assert all(frames), "Token leaves frame"
                        assert page.locator("#replay").bounding_box()["height"] >= (44 if width == 390 else 32)
                        assert json.loads((workspace / "validation.json").read_text())["passed"]
                        record["checks"].append({"width": width, "colorset": cs, "tokenCount": data["tokenCount"], "framesInBounds": len(frames), "materials": data["materialColors"]})
                    assert not errors, errors
                    assert not requests, requests
                    screenshots = OUT / "forward-screenshots"
                    screenshots.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshots / f"{run.name}-{width}.png"), full_page=True)
                    context.close()
                record["artifactPassed"] = True
            except Exception as error:
                record["artifactPassed"] = False
                record["error"] = str(error)
            records.append(record)
            print(json.dumps({k: record[k] for k in ("runId", "strictPassed", "artifactPassed")}), flush=True)
        browser.close()
    (OUT / "forward-review.json").write_text(json.dumps(records, indent=2) + "\n")
    return 0 if records and all(record["artifactPassed"] for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
