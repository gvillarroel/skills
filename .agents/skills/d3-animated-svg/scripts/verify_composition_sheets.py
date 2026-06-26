#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///

"""Verify the D3 composition-variants page."""

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
async ({ expectedSheets, minVariants, requiredVariant }) => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const sheets = window.D3_COMPOSITION_SHEETS || [];
  const variants = window.D3_COMPOSITION_VARIANTS || [];
  const metadata = window.D3_ANIMATED_SVG_EXAMPLES || [];
  const sheetIds = sheets.map(sheet => sheet.id);
  const metadataIds = new Set(metadata.map(item => item.id));
  const findings = [];
  if (sheets.length !== expectedSheets) {
    findings.push(`Expected ${expectedSheets} sheets, found ${sheets.length}.`);
  }
  if (variants.length < minVariants) {
    findings.push(`Expected at least ${minVariants} variants, found ${variants.length}.`);
  }
  if (document.body.dataset.compositionSheetCount !== String(expectedSheets)) {
    findings.push(`Body composition sheet count is ${document.body.dataset.compositionSheetCount}.`);
  }
  if (Number(document.body.dataset.compositionVariantCount || 0) !== variants.length) {
    findings.push(`Body composition variant count is ${document.body.dataset.compositionVariantCount}; script has ${variants.length}.`);
  }
  const ids = variants.map(variant => variant.id);
  const uniqueIds = new Set(ids);
  if (uniqueIds.size !== ids.length) {
    findings.push("Composition variants contain duplicate IDs.");
  }
  const invalidIds = ids.filter(id => !/^d3-composition-[a-z0-9][a-z0-9-]*-[a-z0-9][a-z0-9-]*$/.test(id || ""));
  if (invalidIds.length) {
    findings.push(`Invalid composition IDs: ${invalidIds.slice(0, 5).join(", ")}.`);
  }
  const missingSources = variants.filter(variant => !metadataIds.has(variant.sourceId)).map(variant => variant.sourceId);
  if (missingSources.length) {
    findings.push(`Variants reference missing source patterns: ${Array.from(new Set(missingSources)).slice(0, 8).join(", ")}.`);
  }
  if (requiredVariant && !uniqueIds.has(requiredVariant)) {
    findings.push(`Missing required variant ${requiredVariant}.`);
  }
  const tabIds = Array.from(document.querySelectorAll("[data-sheet-tab]")).map(tab => tab.dataset.sheetTab);
  if (tabIds.length !== expectedSheets) {
    findings.push(`Expected ${expectedSheets} sheet tabs, found ${tabIds.length}.`);
  }
  const sheetReports = [];
  for (const sheetId of sheetIds) {
    const expectedRows = variants.filter(variant => variant.compositionId === sheetId).length;
    const tab = document.querySelector(`[data-sheet-tab="${sheetId}"]`);
    if (!tab) {
      findings.push(`Missing tab for ${sheetId}.`);
      continue;
    }
    tab.click();
    await sleep(120);
    const active = document.body.dataset.activeCompositionSheet;
    if (active !== sheetId) {
      findings.push(`Active sheet after clicking ${sheetId} is ${active}.`);
    }
    const rows = Array.from(document.querySelectorAll(`.composition-card[data-composition-id="${sheetId}"]`));
    const visibleRows = rows.filter(row => !row.hidden);
    if (expectedRows < 5) {
      findings.push(`${sheetId} has only ${expectedRows} curated variants.`);
    }
    if (rows.length !== expectedRows) {
      findings.push(`${sheetId} has ${rows.length} rows, expected ${expectedRows}.`);
    }
    if (visibleRows.length !== expectedRows) {
      findings.push(`${sheetId} has ${visibleRows.length} visible rows, expected ${expectedRows}.`);
    }
    const rowIds = rows.map(row => row.dataset.compositionPatternId);
    if (new Set(rowIds).size !== rowIds.length) {
      findings.push(`${sheetId} has duplicated composition pattern IDs.`);
    }
    const strayFit = rows.filter(row => row.hasAttribute("data-fit") || row.querySelector(".fit-badge")).length;
    if (strayFit) {
      findings.push(`${sheetId} still exposes fit badges or data-fit on ${strayFit} rows.`);
    }
    const missingLinks = rows.filter(row => !row.querySelector(`a[href*="${row.dataset.patternId}"]`)).length;
    if (missingLinks) {
      findings.push(`${sheetId} has ${missingLinks} rows without a base pattern link.`);
    }
    const svgReports = rows.map(row => {
      const svg = row.querySelector("svg[data-composition-pattern-id]");
      const elements = svg ? svg.querySelectorAll("*").length : 0;
      const marks = svg ? svg.querySelectorAll("circle,rect,path,line,polygon,polyline,text").length : 0;
      const title = svg ? svg.querySelector("title")?.textContent || "" : "";
      return { id: row.dataset.compositionPatternId, elements, marks, title };
    });
    const blankSvgs = svgReports.filter(report => report.marks < 8 || !report.title);
    if (blankSvgs.length) {
      findings.push(`${sheetId} has blank or weak SVG previews: ${blankSvgs.slice(0, 5).map(report => report.id).join(", ")}.`);
    }
    const armature = document.querySelector("#sheet-overview svg");
    if (!armature) {
      findings.push(`${sheetId} has no armature SVG.`);
    }
    sheetReports.push({
      id: sheetId,
      expectedRows,
      rows: rows.length,
      visibleRows: visibleRows.length,
      uniqueCompositionIds: new Set(rowIds).size,
      previewMarksMin: Math.min(...svgReports.map(report => report.marks)),
      previewMarksMax: Math.max(...svgReports.map(report => report.marks)),
      armatureElements: armature ? armature.querySelectorAll("*").length : 0
    });
  }
  const requiredRecord = variants.find(variant => variant.id === requiredVariant);
  if (requiredRecord && document.body.dataset.activeCompositionSheet !== requiredRecord.compositionId) {
    document.querySelector(`[data-sheet-tab="${requiredRecord.compositionId}"]`)?.click();
    await sleep(120);
  }
  const search = document.querySelector("#pattern-search");
  search.value = requiredVariant || "force-network";
  search.dispatchEvent(new Event("input", { bubbles: true }));
  await sleep(80);
  const filteredVisible = Array.from(document.querySelectorAll(".composition-card")).filter(row => !row.hidden);
  if (requiredVariant && !filteredVisible.some(row => row.dataset.compositionPatternId === requiredVariant)) {
    findings.push(`Search filter did not expose ${requiredVariant}.`);
  }
  return {
    clean: findings.length === 0,
    findings,
    sheetCount: sheets.length,
    variantCount: variants.length,
    metadataPatternCount: metadata.length,
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
    parser.add_argument("--min-variants", type=int, default=50)
    parser.add_argument("--required-variant", default="d3-composition-radial-rosette-force-network")
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
            {
                "expectedSheets": args.expected_sheets,
                "minVariants": args.min_variants,
                "requiredVariant": args.required_variant,
            },
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
