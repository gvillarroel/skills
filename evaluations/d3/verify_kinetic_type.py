#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Independently verify the live D3 kinetic-type interaction contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


DEFAULT_EXPECTED = (
    ("TRACE", "tiles"),
    ("SIGNAL", "lines"),
    ("SYSTEM", "dots"),
    ("REVEAL", "hybrid"),
)


def add(findings: list[str], condition: bool, message: str) -> None:
    if not condition:
        findings.append(message)


def inspect_page(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """() => ({
          renderState: document.body.dataset.renderState,
          patternId: document.body.dataset.patternId,
          colorset: document.body.dataset.colorset,
          motion: document.body.dataset.motion,
          seed: document.body.dataset.seed,
          pageTitle: document.querySelector('h1')?.textContent?.trim() || '',
          diagnostics: window.__kineticTypeDiagnostics,
          cards: [...document.querySelectorAll('.kinetic-word')].map(button => {
            const svg = button.querySelector('svg');
            const base = svg.querySelector('.base-text');
            const layer = svg.querySelector('.piece-layer');
            const geometry = [...svg.querySelectorAll('.piece-geometry')];
            return {
              text: button.dataset.text,
              variant: button.dataset.variant,
              pressed: button.getAttribute('aria-pressed'),
              pinned: button.classList.contains('is-pinned'),
              focused: document.activeElement === button,
              title: svg.querySelector(':scope > title')?.textContent || '',
              description: svg.querySelector(':scope > desc')?.textContent || '',
              baseText: base?.textContent || '',
              baseOpacity: Number.parseFloat(getComputedStyle(base).opacity),
              layerOpacity: Number.parseFloat(getComputedStyle(layer).opacity),
              pieceCount: Number(svg.dataset.pieceCount || 0),
              tileCount: Number(svg.dataset.tileCount || 0),
              lineCount: Number(svg.dataset.lineCount || 0),
              dotCount: Number(svg.dataset.dotCount || 0),
              animationNames: [...new Set(geometry.map(node => getComputedStyle(node).animationName))],
            };
          }),
        })"""
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--expect-card",
        action="append",
        default=[],
        metavar="TEXT:VARIANT",
        help="Expected card in order; repeat for every card",
    )
    parser.add_argument("--expect-pattern", default="d3-kinetic-glyph-mosaic")
    parser.add_argument("--expect-colorset", default="colorset1")
    parser.add_argument("--expect-motion", default="energetic")
    parser.add_argument("--expect-seed", default="104729")
    parser.add_argument("--expect-title")
    args = parser.parse_args()

    expected = []
    for raw_card in args.expect_card:
        if ":" not in raw_card:
            parser.error(f"--expect-card must use TEXT:VARIANT syntax: {raw_card!r}")
        text, variant = raw_card.rsplit(":", 1)
        if not text or variant not in {"tiles", "lines", "dots", "hybrid"}:
            parser.error(f"invalid --expect-card value: {raw_card!r}")
        expected.append((text, variant))
    if not expected:
        expected = list(DEFAULT_EXPECTED)

    source = args.input.resolve()
    if not source.is_file():
        parser.error(f"input HTML does not exist: {source}")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    browser_errors: dict[str, list[str]] = {"console": [], "page": [], "request": []}
    evidence: dict[str, Any] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()
        page.on(
            "console",
            lambda message: browser_errors["console"].append(message.text)
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: browser_errors["page"].append(str(error)))
        page.on(
            "requestfailed",
            lambda request: browser_errors["request"].append(
                f"{request.method} {request.url}: {request.failure}"
            ),
        )
        page.goto(source.as_uri(), wait_until="load")
        page.locator('body[data-render-state="ready"]').wait_for(timeout=30_000)

        idle = inspect_page(page)
        evidence["idle"] = idle
        add(findings, idle["renderState"] == "ready", "page did not reach ready state")
        add(
            findings,
            idle["patternId"] == args.expect_pattern,
            "body pattern ID is incorrect",
        )
        add(findings, idle["colorset"] == args.expect_colorset, "colorset metadata is incorrect")
        add(findings, idle["motion"] == args.expect_motion, "motion metadata is incorrect")
        add(findings, idle["seed"] == args.expect_seed, "seed metadata is incorrect")
        if args.expect_title is not None:
            add(findings, idle["pageTitle"] == args.expect_title, "visible page title is incorrect")
        add(findings, bool(idle["diagnostics"]["ready"]), "diagnostics are not ready")
        add(
            findings,
            len(idle["cards"]) == len(expected),
            f"card count is not {len(expected)}",
        )

        for index, ((expected_text, expected_variant), card) in enumerate(
            zip(expected, idle["cards"], strict=False), start=1
        ):
            prefix = f"card {index}"
            add(findings, card["text"] == expected_text, f"{prefix} text metadata is incorrect")
            add(findings, card["variant"] == expected_variant, f"{prefix} variant is incorrect")
            add(findings, card["baseText"] == expected_text, f"{prefix} readable base text changed")
            add(findings, bool(card["title"]), f"{prefix} is missing a direct title")
            add(findings, bool(card["description"]), f"{prefix} is missing a direct description")
            add(findings, card["pressed"] == "false", f"{prefix} is pressed while idle")
            add(findings, card["pieceCount"] > 0, f"{prefix} has no sampled geometry")
            add(findings, card["layerOpacity"] == 0, f"{prefix} piece layer is visible while idle")

        if len(idle["cards"]) == len(expected) == 4:
            add(findings, idle["cards"][0]["tileCount"] > 0, "tiles card has no tiles")
            add(findings, idle["cards"][1]["lineCount"] > 0, "lines card has no lines")
            add(findings, idle["cards"][2]["dotCount"] > 0, "dots card has no dots")
            hybrid = idle["cards"][3]
            add(
                findings,
                all(hybrid[key] > 0 for key in ("tileCount", "lineCount", "dotCount")),
                "hybrid card does not contain every material",
            )

        first = page.locator(".kinetic-word").nth(0)
        first.click()
        page.wait_for_timeout(350)
        pinned = inspect_page(page)
        evidence["pinned"] = pinned["cards"][0]
        add(findings, pinned["cards"][0]["pressed"] == "true", "click did not set aria-pressed")
        add(findings, bool(pinned["cards"][0]["pinned"]), "click did not pin the card")
        add(
            findings,
            pinned["cards"][0]["layerOpacity"] >= 0.99,
            "pinned geometry is not fully visible after its transition",
        )
        add(findings, pinned["cards"][0]["baseOpacity"] < 0.2, "pinned base text is not subdued")
        first.screenshot(path=str(output_dir / "pinned-tiles.png"))

        first.click()
        page.wait_for_timeout(100)
        reset = inspect_page(page)["cards"][0]
        evidence["reset"] = reset
        add(findings, reset["pressed"] == "false", "second click did not reset aria-pressed")
        add(findings, not reset["pinned"], "second click did not clear the pinned state")

        page.mouse.move(1300, 850)
        page.keyboard.press("Tab")
        page.wait_for_timeout(350)
        second = page.locator(".kinetic-word").nth(1)
        focused = inspect_page(page)["cards"][1]
        evidence["focused"] = focused
        add(findings, bool(focused["focused"]), "Tab did not move keyboard focus to the second card")
        add(findings, focused["layerOpacity"] >= 0.99, "keyboard focus does not reveal geometry")
        second.screenshot(path=str(output_dir / "focused-lines.png"))
        context.close()

        reduced_context = browser.new_context(
            viewport={"width": 1366, "height": 900}, reduced_motion="reduce"
        )
        reduced_page = reduced_context.new_page()
        reduced_page.on(
            "console",
            lambda message: browser_errors["console"].append(message.text)
            if message.type == "error"
            else None,
        )
        reduced_page.on("pageerror", lambda error: browser_errors["page"].append(str(error)))
        reduced_page.goto(source.as_uri(), wait_until="load")
        reduced_page.locator('body[data-render-state="ready"]').wait_for(timeout=30_000)
        reduced_first = reduced_page.locator(".kinetic-word").first
        reduced_first.hover()
        reduced_page.wait_for_timeout(100)
        reduced = inspect_page(reduced_page)["cards"][0]
        evidence["reducedMotion"] = reduced
        add(findings, reduced["layerOpacity"] == 1, "reduced-motion reveal is hidden")
        add(
            findings,
            set(reduced["animationNames"]) <= {"none"},
            "reduced-motion geometry still has active animation",
        )
        reduced_first.screenshot(path=str(output_dir / "reduced-motion-tiles.png"))
        reduced_context.close()
        browser.close()

    for category, messages in browser_errors.items():
        if messages:
            findings.append(f"browser {category} errors: {messages}")

    report = {
        "ok": not findings,
        "artifact": str(source),
        "findings": findings,
        "browserErrors": browser_errors,
        "evidence": evidence,
        "screenshots": sorted(path.name for path in output_dir.glob("*.png")),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
