#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Render showcase SVGs in Edge and require pixel parity with generated previews."""

from __future__ import annotations

import io
import json
import socket
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


PROJECT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT / "artifacts"


def install_windows_socketpair_workaround() -> None:
    if sys.platform != "win32":
        return

    def loopback_socketpair(
        family: int = socket.AF_INET,
        socket_type: int = socket.SOCK_STREAM,
        protocol: int = 0,
    ) -> tuple[socket.socket, socket.socket]:
        if family not in {socket.AF_INET, socket.AF_INET6} or socket_type != socket.SOCK_STREAM or protocol != 0:
            raise ValueError("The Windows loopback socket pair supports only TCP over IPv4 or IPv6")
        host = "127.0.0.1" if family == socket.AF_INET else "::1"
        listener = socket.socket(family, socket_type, protocol)
        client = socket.socket(family, socket_type, protocol)
        server: socket.socket | None = None
        try:
            listener.bind((host, 0))
            listener.listen(1)
            client.settimeout(5)
            client.connect(listener.getsockname())
            client.settimeout(None)
            server, _ = listener.accept()
            return server, client
        except Exception:
            if server is not None:
                server.close()
            client.close()
            raise
        finally:
            listener.close()

    socket.socketpair = loopback_socketpair


def dimensions(svg: Path) -> tuple[int, int]:
    root = ET.parse(svg).getroot()
    return int(root.attrib["width"]), int(root.attrib["height"])


def compare(expected: Image.Image, actual: Image.Image) -> tuple[int, int]:
    if expected.size != actual.size:
        return expected.width * expected.height, 255
    difference = ImageChops.difference(expected.convert("RGBA"), actual.convert("RGBA"))
    extrema = difference.getextrema()
    maximum = max(channel[1] for channel in extrema)
    getter = getattr(difference, "get_flattened_data", difference.getdata)
    changed = sum(1 for pixel in getter() if pixel != (0, 0, 0, 0))
    return changed, maximum


def main() -> int:
    install_windows_socketpair_workaround()
    svg_paths = sorted((ARTIFACTS / "stylized").glob("*.svg"))
    if not svg_paths:
        raise SystemExit("No stylized SVGs found")
    screenshot_dir = ARTIFACTS / "browser-renders"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = None
        browser_label = ""
        errors: list[str] = []
        for label, options in (
            ("bundled Chromium", {}),
            ("Microsoft Edge", {"channel": "msedge"}),
            ("Google Chrome", {"channel": "chrome"}),
        ):
            try:
                browser = playwright.chromium.launch(**options)
                browser_label = label
                break
            except PlaywrightError as error:
                errors.append(f"{label}: {error}")
        if browser is None:
            raise SystemExit("No Chromium browser could be launched:\n" + "\n".join(errors))

        for svg in svg_paths:
            width, height = dimensions(svg)
            page = browser.new_page(viewport={"width": width + 32, "height": height + 32})
            console_errors: list[str] = []
            page_errors: list[str] = []
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(svg.resolve().as_uri(), wait_until="load", timeout=30000)
            locator = page.locator("svg").first
            screenshot_bytes = locator.screenshot(animations="disabled", omit_background=True)
            actual = Image.open(io.BytesIO(screenshot_bytes)).convert("RGBA")
            expected_path = ARTIFACTS / "previews" / f"{svg.stem}.png"
            with Image.open(expected_path) as opened:
                expected = opened.convert("RGBA")
            changed_pixels, maximum_delta = compare(expected, actual)
            browser_path = screenshot_dir / f"{svg.stem}.png"
            actual.save(browser_path)
            reports.append(
                {
                    "svg": str(svg.resolve()),
                    "preview": str(expected_path.resolve()),
                    "browserRender": str(browser_path.resolve()),
                    "width": width,
                    "height": height,
                    "changedPixels": changed_pixels,
                    "maximumChannelDelta": maximum_delta,
                    "consoleErrors": console_errors,
                    "pageErrors": page_errors,
                    "ok": changed_pixels == 0 and not console_errors and not page_errors,
                }
            )
            page.close()
        browser.close()

    payload = {
        "ok": all(report["ok"] for report in reports),
        "browser": browser_label,
        "artifactCount": len(reports),
        "artifacts": reports,
    }
    report_path = ARTIFACTS / "validation" / "browser-parity.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**payload, "report": str(report_path.resolve())}, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
