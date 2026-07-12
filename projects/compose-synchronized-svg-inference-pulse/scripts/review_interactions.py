#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///

"""Exercise the Inference Pulse SVG through real pointer and keyboard input."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, Playwright, sync_playwright


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects" / "compose-synchronized-svg-inference-pulse"
SVG = PROJECT / "artifacts" / "svgs" / "inference-pulse.svg"
REPORT = PROJECT / "artifacts" / "reviews" / "interaction-review.json"
SCREENSHOTS = PROJECT / "artifacts" / "screenshots"


def launch_browser(playwright: Playwright) -> Browser:
    attempts: list[str] = []
    for options in ({}, {"channel": "chrome"}, {"channel": "msedge"}):
        try:
            return playwright.chromium.launch(headless=True, **options)
        except Exception as error:  # pragma: no cover - depends on local browser installation
            attempts.append(str(error).splitlines()[0])
    raise RuntimeError("Unable to launch Chromium: " + " | ".join(attempts))


def main() -> int:
    if not SVG.is_file():
        raise SystemExit(f"Missing SVG: {SVG}")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, **details: Any) -> None:
        checks.append({"id": check_id, "ok": bool(passed), "details": details})
        print(f"{check_id}: {'PASS' if passed else 'FAIL'}", flush=True)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1200},
            reduced_motion="no-preference",
        )
        page = context.new_page()
        page.set_default_timeout(10_000)
        console_errors: list[str] = []
        page_errors: list[str] = []
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(SVG.as_uri(), wait_until="load")
        page.wait_for_function("() => window.svgSync && document.documentElement.dataset.syncReady === 'true'")

        before_autoplay = page.evaluate("() => window.svgSync.snapshot().timeMs")
        page.wait_for_timeout(180)
        after_autoplay = page.evaluate("() => window.svgSync.snapshot().timeMs")
        record(
            "autoplay-advances",
            after_autoplay > before_autoplay,
            beforeTimeMs=before_autoplay,
            afterTimeMs=after_autoplay,
        )
        page.evaluate("() => { window.svgSync.pause(); window.svgSync.seek(0); }")

        relationship_count = page.locator("[data-relationship-id]").count()
        record("relationship-contract", relationship_count == 18, relationshipCount=relationship_count)

        admission = page.locator("#module-focus-toggle-token-admission-admit-focus")
        admission.click()
        clicked_focus = page.evaluate("() => window.svgSync.snapshot().focusId")
        page.wait_for_timeout(80)
        paused_time = page.evaluate("() => window.svgSync.snapshot().timeMs")
        page.wait_for_timeout(100)
        paused_time_after = page.evaluate("() => window.svgSync.snapshot().timeMs")
        record(
            "pointer-module-focus-pauses",
            clicked_focus == "admit-focus" and paused_time_after == paused_time,
            focusId=clicked_focus,
            timeMs=paused_time_after,
        )
        active_after_click = page.locator("[data-relationship-id][data-active='true']").count()
        record(
            "focused-relationship-highlight",
            active_after_click >= 1,
            activeRelationshipCount=active_after_click,
        )
        admission.click()
        record(
            "pointer-module-focus-toggle",
            page.evaluate("() => window.svgSync.snapshot().focusId") is None,
        )

        admission.focus()
        page.keyboard.press("Enter")
        keyboard_focus = page.evaluate("() => window.svgSync.snapshot().focusId")
        page.keyboard.press("Escape")
        escaped_focus = page.evaluate("() => window.svgSync.snapshot().focusId")
        record(
            "keyboard-focus-and-escape",
            keyboard_focus == "admit-focus" and escaped_focus is None,
            focused=keyboard_focus,
            escaped=escaped_focus,
        )

        timeline = page.locator("[data-timeline-rail]")
        timeline.focus()
        page.keyboard.press("End")
        end_snapshot = page.evaluate("() => window.svgSync.snapshot()")
        page.keyboard.press("Home")
        home_snapshot = page.evaluate("() => window.svgSync.snapshot()")
        record(
            "timeline-keyboard-seams",
            end_snapshot["timeMs"] == 0
            and end_snapshot["phaseId"] == "ready"
            and home_snapshot["timeMs"] == 0
            and home_snapshot["phaseId"] == "ready",
            end={"timeMs": end_snapshot["timeMs"], "phaseId": end_snapshot["phaseId"]},
            home={"timeMs": home_snapshot["timeMs"], "phaseId": home_snapshot["phaseId"]},
        )

        box = timeline.locator(".timeline-track").bounding_box()
        if box is None:
            record("timeline-pointer-seek", False, error="timeline has no bounding box")
        else:
            page.mouse.click(box["x"] + box["width"] * 0.75, box["y"] + box["height"] / 2)
            pointer_snapshot = page.evaluate("() => window.svgSync.snapshot()")
            record(
                "timeline-pointer-seek",
                16500 <= pointer_snapshot["timeMs"] <= 19500,
                timeMs=pointer_snapshot["timeMs"],
                phaseId=pointer_snapshot["phaseId"],
            )

        page.locator("#control-scenario-ready-baseline").click()
        scenario_snapshot = page.evaluate("() => window.svgSync.snapshot()")
        record(
            "scenario-control",
            scenario_snapshot["scenarioId"] == "ready-baseline",
            scenarioId=scenario_snapshot["scenarioId"],
        )

        page.locator("#control-play").click()
        play_before = page.evaluate("() => window.svgSync.snapshot().timeMs")
        page.wait_for_timeout(180)
        play_after = page.evaluate("() => window.svgSync.snapshot().timeMs")
        page.locator("#control-play").click()
        pause_before = page.evaluate("() => window.svgSync.snapshot().timeMs")
        page.wait_for_timeout(120)
        pause_after = page.evaluate("() => window.svgSync.snapshot().timeMs")
        record(
            "play-pause-control",
            play_after > play_before and math.isclose(pause_after, pause_before, abs_tol=0.001),
            playBefore=play_before,
            playAfter=play_after,
            pauseBefore=pause_before,
            pauseAfter=pause_after,
        )

        page.evaluate("() => window.svgSync.seek(22000)")
        adapt_state = page.evaluate("() => window.svgSync.snapshot()")
        active_adapt = page.locator("[data-relationship-id][data-active='true']").count()
        record(
            "mixed-interpolation",
            72 < adapt_state["sourceValues"]["arrival-rate"] < 120
            and adapt_state["sourceValues"]["replica-count"] == 4,
            arrivalRate=adapt_state["sourceValues"]["arrival-rate"],
            replicaCount=adapt_state["sourceValues"]["replica-count"],
        )
        record(
            "adaptive-feedback-highlight",
            active_adapt >= 3,
            activeRelationshipCount=active_adapt,
        )
        pulse_before = page.locator("[data-relationship-id][data-active='true'] [data-relationship-pulse]").first.get_attribute("cx")
        page.evaluate("() => window.svgSync.seek(22500)")
        pulse_after = page.locator("[data-relationship-id][data-active='true'] [data-relationship-pulse]").first.get_attribute("cx")
        record(
            "relationship-pulse-follows-master-time",
            pulse_before is not None and pulse_after is not None and pulse_before != pulse_after,
            beforeCx=pulse_before,
            afterCx=pulse_after,
        )

        screenshot_states = {
            "admission": 4000,
            "prefill": 12750,
            "adaptive-feedback": 22000,
        }
        screenshot_paths: dict[str, str] = {}
        for label, time_ms in screenshot_states.items():
            page.evaluate("ms => { window.svgSync.pause(); window.svgSync.seek(ms); }", time_ms)
            page.wait_for_timeout(60)
            screenshot_path = SCREENSHOTS / f"inference-pulse-{label}.png"
            page.screenshot(path=str(screenshot_path), animations="disabled", timeout=60000)
            screenshot_paths[label] = str(screenshot_path)

        record("browser-errors", not console_errors and not page_errors, console=console_errors, page=page_errors)
        context.close()
        browser.close()

    failures = [check["id"] for check in checks if not check["ok"]]
    report = {
        "ok": not failures,
        "artifact": str(SVG),
        "failures": failures,
        "checks": checks,
        "screenshots": screenshot_paths,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
