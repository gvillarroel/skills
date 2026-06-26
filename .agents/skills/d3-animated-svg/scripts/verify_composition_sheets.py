#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///

"""Verify the D3 composition-sheets page."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = SKILL_ROOT / "assets" / "examples" / "d3-animated-svg" / "composition-sheets.html"

VERIFY_JS = r"""
async ({ expectedSheets, expectedPatterns }) => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const sheets = window.D3_COMPOSITION_SHEETS || [];
  const metadata = window.D3_ANIMATED_SVG_EXAMPLES || [];
  const sheetIds = sheets.map(sheet => sheet.id);
  const findings = [];
  if (sheets.length !== expectedSheets) {
    findings.push(`Expected ${expectedSheets} sheets, found ${sheets.length}.`);
  }
  if (metadata.length !== expectedPatterns) {
    findings.push(`Expected ${expectedPatterns} metadata patterns, found ${metadata.length}.`);
  }
  if (document.body.dataset.compositionSheetCount !== String(expectedSheets)) {
    findings.push(`Body composition sheet count is ${document.body.dataset.compositionSheetCount}.`);
  }
  if (document.body.dataset.patternCount !== String(expectedPatterns)) {
    findings.push(`Body pattern count is ${document.body.dataset.patternCount}.`);
  }
  const tabIds = Array.from(document.querySelectorAll("[data-sheet-tab]")).map(tab => tab.dataset.sheetTab);
  if (tabIds.length !== expectedSheets) {
    findings.push(`Expected ${expectedSheets} sheet tabs, found ${tabIds.length}.`);
  }
  const sheetReports = [];
  for (const sheetId of sheetIds) {
    const tab = document.querySelector(`[data-sheet-tab="${sheetId}"]`);
    if (!tab) {
      findings.push(`Missing tab for ${sheetId}.`);
      continue;
    }
    tab.click();
    await sleep(80);
    const active = document.body.dataset.activeCompositionSheet;
    if (active !== sheetId) {
      findings.push(`Active sheet after clicking ${sheetId} is ${active}.`);
    }
    const rows = Array.from(document.querySelectorAll(`.pattern-row[data-composition-id="${sheetId}"]`));
    const visibleRows = rows.filter(row => !row.hidden);
    const ids = rows.map(row => row.dataset.patternId);
    const uniqueIds = new Set(ids);
    if (rows.length !== expectedPatterns) {
      findings.push(`${sheetId} has ${rows.length} rows, expected ${expectedPatterns}.`);
    }
    if (visibleRows.length !== expectedPatterns) {
      findings.push(`${sheetId} has ${visibleRows.length} visible rows, expected ${expectedPatterns}.`);
    }
    if (uniqueIds.size !== rows.length) {
      findings.push(`${sheetId} has duplicated pattern IDs.`);
    }
    const invalidIds = ids.filter(id => !/^d3-pattern-[a-z0-9][a-z0-9-]*$/.test(id || ""));
    if (invalidIds.length) {
      findings.push(`${sheetId} has invalid pattern IDs: ${invalidIds.slice(0, 5).join(", ")}.`);
    }
    const missingLinks = rows.filter(row => !row.querySelector(`a[href*="${row.dataset.patternId}"]`)).length;
    if (missingLinks) {
      findings.push(`${sheetId} has ${missingLinks} rows without a gallery link.`);
    }
    const fitCounts = rows.reduce((acc, row) => {
      acc[row.dataset.fit] = (acc[row.dataset.fit] || 0) + 1;
      return acc;
    }, {});
    for (const fit of ["strong", "ready", "support"]) {
      if (!fitCounts[fit]) findings.push(`${sheetId} has no ${fit} examples.`);
    }
    const armature = document.querySelector("#sheet-overview svg");
    if (!armature) {
      findings.push(`${sheetId} has no armature SVG.`);
    }
    sheetReports.push({
      id: sheetId,
      rows: rows.length,
      visibleRows: visibleRows.length,
      uniquePatternIds: uniqueIds.size,
      fitCounts,
      armatureElements: armature ? armature.querySelectorAll("*").length : 0
    });
  }
  const search = document.querySelector("#pattern-search");
  search.value = "asymmetric-task-overlap-saturated";
  search.dispatchEvent(new Event("input", { bubbles: true }));
  await sleep(80);
  const filteredVisible = Array.from(document.querySelectorAll(".pattern-row")).filter(row => !row.hidden);
  if (!filteredVisible.some(row => row.dataset.patternId === "d3-pattern-asymmetric-task-overlap-saturated")) {
    findings.push("Search filter did not expose d3-pattern-asymmetric-task-overlap-saturated.");
  }
  return {
    clean: findings.length === 0,
    findings,
    sheetCount: sheets.length,
    patternCount: metadata.length,
    sheetReports,
    filteredVisibleCount: filteredVisible.length,
    viewport: { width: window.innerWidth, height: window.innerHeight }
  };
}
"""


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source) or source.startswith("file://"):
        return source
    return Path(source).expanduser().resolve().as_uri()


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value)
    if not match:
        raise argparse.ArgumentTypeError("Viewport must use WIDTHxHEIGHT, for example 1366x900.")
    return int(match.group(1)), int(match.group(2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=str(DEFAULT_SOURCE), help="Composition sheets HTML file, file URL, or HTTP URL.")
    parser.add_argument("--expected-sheets", type=int, default=7)
    parser.add_argument("--expected-patterns", type=int, default=218)
    parser.add_argument("--viewport", type=parse_viewport, default=(1366, 900))
    parser.add_argument("--wait-ms", type=int, default=600)
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--expect-clean", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    width, height = args.viewport
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(source_to_url(args.source), wait_until="load", timeout=90_000)
        page.wait_for_timeout(max(args.wait_ms, 0))
        result: dict[str, Any] = page.evaluate(
            VERIFY_JS,
            {"expectedSheets": args.expected_sheets, "expectedPatterns": args.expected_patterns},
        )
        if args.screenshot:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=args.screenshot, full_page=True)
        browser.close()
    print(json.dumps(result, indent=2))
    if args.expect_clean and not result.get("clean"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
