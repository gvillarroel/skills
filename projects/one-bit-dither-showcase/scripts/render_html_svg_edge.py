#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Capture a settled inline SVG from local HTML using an available Chromium channel."""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


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


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT")
    width, height = (int(part) for part in match.groups())
    if width < 100 or height < 100:
        raise argparse.ArgumentTypeError("viewport dimensions must be at least 100 pixels")
    return width, height


def ensure_svg_document(markup: str) -> str:
    markup = markup.strip()
    if not markup.startswith("<svg"):
        raise SystemExit("Selected element is not an SVG")
    if "xmlns=" not in markup.split(">", 1)[0]:
        markup = markup.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + markup + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument("--selector", default="svg")
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("960x540"))
    parser.add_argument("--wait-ms", type=int, default=200)
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"input not found: {args.input}")

    install_windows_socketpair_workaround()
    width, height = args.viewport
    console_errors: list[str] = []
    page_errors: list[str] = []
    launch_errors: list[str] = []
    info: dict[str, object] | None = None

    with sync_playwright() as playwright:
        browser = None
        browser_label = ""
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
                launch_errors.append(f"{label}: {error}")
        if browser is None:
            raise SystemExit("No Chromium browser could be launched:\n" + "\n".join(launch_errors))

        page = browser.new_page(viewport={"width": width, "height": height})
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(args.input.resolve().as_uri(), wait_until="load", timeout=30000)
        page.wait_for_timeout(max(0, args.wait_ms))
        locator = page.locator(args.selector).first
        locator.wait_for(state="visible", timeout=30000)
        info = locator.evaluate(
            """svg => {
                const box = svg.getBoundingClientRect();
                const clone = svg.cloneNode(true);
                const properties = [
                    'color', 'fill', 'fill-opacity', 'stroke', 'stroke-opacity',
                    'stroke-width', 'stroke-linecap', 'stroke-linejoin',
                    'font-family', 'font-size', 'font-style', 'font-weight',
                    'letter-spacing', 'opacity', 'paint-order', 'shape-rendering',
                    'text-anchor', 'dominant-baseline', 'visibility'
                ];
                const sourceNodes = [svg, ...svg.querySelectorAll('*')];
                const cloneNodes = [clone, ...clone.querySelectorAll('*')];
                sourceNodes.forEach((source, index) => {
                    const target = cloneNodes[index];
                    if (!(target instanceof Element)) return;
                    const computed = getComputedStyle(source);
                    properties.forEach(property => {
                        const value = computed.getPropertyValue(property);
                        if (value) target.style.setProperty(property, value);
                    });
                });
                return {
                    tagName: svg.tagName.toLowerCase(),
                    markup: new XMLSerializer().serializeToString(clone),
                    width: box.width,
                    height: box.height,
                    elementCount: svg.querySelectorAll('*').length,
                    textLength: (svg.textContent || '').trim().length
                };
            }"""
        )
        if info["tagName"] != "svg" or info["elementCount"] == 0:
            raise SystemExit("The selected SVG is empty")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(ensure_svg_document(str(info["markup"])), encoding="utf-8", newline="\n")
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        locator.screenshot(path=str(args.screenshot.resolve()), animations="disabled")
        browser.close()

    if console_errors or page_errors:
        raise SystemExit("Browser errors:\n" + "\n".join(f"- {item}" for item in console_errors + page_errors))
    report = {
        "ok": True,
        "browser": browser_label,
        "output": str(args.output.resolve()),
        "screenshot": str(args.screenshot.resolve()),
        "renderedWidth": info["width"] if info else None,
        "renderedHeight": info["height"] if info else None,
        "elementCount": info["elementCount"] if info else None,
        "textLength": info["textLength"] if info else None,
        "consoleErrors": [],
        "pageErrors": [],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
