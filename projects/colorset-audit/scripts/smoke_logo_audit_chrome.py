#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Smoke-test contact sheet chrome and responsive controls, excluding source logos."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/colorset-audit/artifacts"
page_path = OUT / "html/logo-audit.html"
records = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    for width, height in ((1440, 1100), (390, 844)):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(page_path.as_uri(), wait_until="load")
        page.wait_for_timeout(350)
        count = page.locator(".row").count()
        assert count == 12, count
        assert page.locator("#progress").inner_text() == "Ready"
        selections = []
        for value in page.locator("#chosen-color option").evaluate_all("items=>items.map(item=>item.value)"):
            page.locator("#chosen-color").select_option(value)
            page.wait_for_timeout(20)
            actual = page.locator(".adaptive").first.evaluate("node=>getComputedStyle(node).color")
            expected = f"rgb({int(value[1:3],16)}, {int(value[3:5],16)}, {int(value[5:7],16)})"
            assert actual == expected, (actual, expected)
            selections.append(value)
        record = page.evaluate("""() => ({overflow:document.documentElement.scrollWidth > innerWidth,
            gridColumns:getComputedStyle(document.querySelector('.row')).gridTemplateColumns.split(' ').length,
            controls:[...document.querySelectorAll('button,select')].map(node=>({id:node.id,color:getComputedStyle(node).color,
            background:getComputedStyle(node).backgroundColor,border:getComputedStyle(node).borderColor})),
            loadedImages:[...document.querySelectorAll('.cell img')].filter(img=>img.complete&&img.naturalWidth>0).length})""")
        assert not record["overflow"], record
        assert record["gridColumns"] == (7 if width > 800 else 3), record
        assert not errors, errors
        page.screenshot(path=str(OUT / f"images/logo-audit-chrome-{width}.png"), full_page=False)
        records.append({"viewport": [width, height], "rowCount": count, "paletteSelections": selections, "pageErrors": errors, **record})
        page.close()
    browser.close()
report = OUT / "data/logo-audit-chrome-smoke.json"
report.write_text(json.dumps({"ok": True, "scope": "12-row chrome/selector/responsive smoke; original brand SVG paints excluded; full audit button not clicked", "results": records}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ok": True, "results": records}, indent=2))
