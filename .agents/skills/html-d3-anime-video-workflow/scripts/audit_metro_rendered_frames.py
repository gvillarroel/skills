#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import random
import re
import socket
import statistics
import subprocess
import sys
import threading
import time
from functools import partial
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit rendered Metro frames in Chromium for square edges, grid alignment, and visible gray hierarchy."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-package", type=Path, help="Optional source-package.json for video id, duration, and format.")
    parser.add_argument("--video-id", help="renderConceptFrame video id. Defaults to source-package outputId.")
    parser.add_argument("--duration", type=float, help="Duration in seconds. Defaults to source-package durationSeconds.")
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--width", type=int, help="Viewport width. Defaults to source-package format.width or 1280.")
    parser.add_argument("--height", type=int, help="Viewport height. Defaults to source-package format.height or 720.")
    parser.add_argument("--selector", default="#stage")
    parser.add_argument("--grid", type=float, default=4.0)
    parser.add_argument("--max-rounded-rects", type=int, default=0)
    parser.add_argument("--max-rounded-line-signals", type=int, default=0)
    parser.add_argument("--max-offgrid-ratio", type=float, default=0.0)
    parser.add_argument("--min-shared-edge-ratio", type=float, default=0.25)
    parser.add_argument("--min-gray-levels", type=int, default=4)
    parser.add_argument("--min-gray-luminance-spread", type=float, default=80.0)
    parser.add_argument("--min-gray-level-area-ratio", type=float, default=0.005)
    parser.add_argument("--min-gray-sample-pass-ratio", type=float, default=0.5)
    parser.add_argument("--min-final-gray-levels", type=int, default=4)
    parser.add_argument("--min-final-gray-luminance-spread", type=float, default=80.0)
    parser.add_argument("--max-median-text-area-ratio", type=float, default=0.14)
    parser.add_argument("--max-largest-text-box-area-ratio", type=float, default=0.08)
    parser.add_argument("--min-median-mark-to-text-ratio", type=float, default=1.5)
    parser.add_argument("--max-title-band-text-count", type=int, default=0)
    parser.add_argument("--max-ellipsized-text-count", type=int, default=0)
    parser.add_argument("--max-rendered-internal-padding-px", type=float, default=0.5)
    parser.add_argument("--max-untagged-inset-rects", type=int, default=0)
    parser.add_argument("--min-untagged-inset-area-ratio", type=float, default=0.35)
    parser.add_argument("--min-untagged-inset-size-px", type=float, default=12.0)
    parser.add_argument("--max-padded-module-interiors", type=int, default=0)
    parser.add_argument("--min-padded-module-child-count", type=int, default=2)
    parser.add_argument("--min-padded-module-area-ratio", type=float, default=0.04)
    parser.add_argument("--min-padded-module-offset-px", type=float, default=3.5)
    parser.add_argument("--max-red-rect-area-ratio", type=float, default=0.10)
    parser.add_argument("--min-zone-elements", type=int, default=0)
    parser.add_argument("--require-zero-padding-policy", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--install-browser", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--launch-timeout-ms", type=int, default=8_000)
    parser.add_argument("--navigation-timeout-ms", type=int, default=30_000)
    return parser.parse_args()


def read_source_package(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def source_format(source: dict[str, Any]) -> dict[str, Any]:
    value = source.get("format")
    return value if isinstance(value, dict) else {}


def resolve_config(args: argparse.Namespace) -> dict[str, Any]:
    source = read_source_package(args.source_package)
    fmt = source_format(source)
    video_id = args.video_id or str(source.get("outputId") or "")
    if not video_id:
        raise ValueError("--video-id is required when --source-package does not provide outputId")
    duration = args.duration if args.duration is not None else float(source.get("durationSeconds") or 0)
    if duration <= 0:
        raise ValueError("--duration is required when --source-package does not provide durationSeconds")
    width = args.width or int(fmt.get("width") or 1280)
    height = args.height or int(fmt.get("height") or 720)
    return {
        "source": source,
        "videoId": video_id,
        "duration": duration,
        "width": width,
        "height": height,
        "title": str(source.get("title") or ""),
        "checkedDate": str(source.get("checkedDate") or ""),
        "masonryLayout": source.get("masonryLayout") if isinstance(source.get("masonryLayout"), dict) else {},
    }


def sample_times(duration: float, samples: int) -> list[float]:
    if samples <= 0:
        raise ValueError("--samples must be positive")
    if samples == 1:
        return [0.0]
    tail = max(0.0, duration - min(0.25, duration / 20))
    return [round(tail * index / (samples - 1), 3) for index in range(samples)]


CHROMIUM_UNSAFE_PORTS = {
    1,
    7,
    9,
    11,
    13,
    15,
    17,
    19,
    20,
    21,
    22,
    23,
    25,
    37,
    42,
    43,
    53,
    69,
    77,
    79,
    87,
    95,
    101,
    102,
    103,
    104,
    109,
    110,
    111,
    113,
    115,
    117,
    119,
    123,
    135,
    137,
    139,
    143,
    161,
    179,
    389,
    427,
    465,
    512,
    513,
    514,
    515,
    526,
    530,
    531,
    532,
    540,
    548,
    554,
    556,
    563,
    587,
    601,
    636,
    989,
    990,
    993,
    995,
    1719,
    1720,
    1723,
    2049,
    3659,
    4045,
    5060,
    5061,
    6000,
    6566,
    6665,
    6666,
    6667,
    6668,
    6669,
    6697,
    10080,
}


def free_port() -> int:
    for _ in range(100):
        port = random.randint(49152, 65535)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    for _ in range(100):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
        if port not in CHROMIUM_UNSAFE_PORTS:
            return port
    raise RuntimeError("Could not find a Chromium-safe free localhost port")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def serve_directory(directory: Path):
    port = free_port()
    handler = partial(QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def goto_with_retry(page: Any, url: str, attempts: int = 4, timeout_ms: int = 30_000, html: Path | None = None) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.25 * (attempt + 1))
    if html is not None:
        page.set_content(html.read_text(encoding="utf-8"), wait_until="domcontentloaded", timeout=timeout_ms)
        return
    if last_error is not None:
        raise last_error


def install_chromium() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    return "\n".join(part for part in (result.stdout[-1200:], result.stderr[-1200:]) if part)


def local_browser_candidates() -> list[Path]:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    return [path for path in candidates if path.exists()]


def launch_chromium(playwright: Any, *, install_browser: bool, timeout_ms: int) -> tuple[Any, list[str]]:
    errors: list[str] = []
    for browser_path in local_browser_candidates():
        try:
            return (
                playwright.chromium.launch(
                    executable_path=str(browser_path),
                    headless=True,
                    timeout=timeout_ms,
                    args=["--no-sandbox"],
                ),
                errors,
            )
        except Exception as exc:
            errors.append(f"{browser_path}: {exc}")
    for kwargs in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
        try:
            return playwright.chromium.launch(headless=True, timeout=timeout_ms, **kwargs), errors
        except Exception as exc:
            errors.append(f"{kwargs or {'bundled': True}}: {exc}")
    if install_browser:
        errors.append(f"install chromium: {install_chromium()}")
        try:
            return playwright.chromium.launch(headless=True, timeout=timeout_ms), errors
        except Exception as exc:
            errors.append(f"post-install bundled: {exc}")
    raise RuntimeError("Could not launch Chromium. " + " | ".join(errors))


def sample_rendered_frames(
    html: Path,
    times: list[float],
    config: dict[str, Any],
    selector: str,
    install_browser: bool,
    launch_timeout_ms: int,
    navigation_timeout_ms: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(f"Playwright import failed: {exc}") from exc

    browser_notes: list[str] = []
    samples: list[dict[str, Any]] = []
    with serve_directory(html.parent) as base_url:
        with sync_playwright() as playwright:
            browser, browser_notes = launch_chromium(
                playwright,
                install_browser=install_browser,
                timeout_ms=launch_timeout_ms,
            )
            try:
                page = browser.new_page(viewport={"width": int(config["width"]), "height": int(config["height"])})
                page.set_default_timeout(navigation_timeout_ms)
                page.set_default_navigation_timeout(navigation_timeout_ms)
                goto_with_retry(page, f"{base_url}/{html.name}", timeout_ms=navigation_timeout_ms, html=html)
                page.wait_for_function("() => typeof window.renderConceptFrame === 'function'", timeout=navigation_timeout_ms)
                for index, seconds in enumerate(times):
                    frame = page.evaluate(
                        """
                        ({ videoId, seconds, selector }) => {
                          const state = window.renderConceptFrame(videoId, seconds, { capture: true });
                          const stage = document.querySelector(selector) || document.querySelector("svg");
                          if (!stage) {
                            throw new Error(`No stage matched selector ${selector}`);
                          }
                          const numericAttr = (node, name) => {
                            const raw = node.getAttribute(name);
                            if (raw === null || raw === "") return null;
                            const parsed = Number(raw);
                            return Number.isFinite(parsed) ? parsed : null;
                          };
                          const numericCssLength = (raw) => {
                            if (!raw) return null;
                            const value = String(raw).trim().toLowerCase();
                            if (!value || value === "auto" || value === "none" || value === "normal") return null;
                            const match = value.match(/^(-?\\d+(?:\\.\\d+)?)(px)?$/);
                            if (!match) return null;
                            const parsed = Number(match[1]);
                            return Number.isFinite(parsed) ? parsed : null;
                          };
                          const styleValue = (node, name) => window.getComputedStyle(node).getPropertyValue(name).trim();
                          const insideCameraLayer = (node) => {
                            let current = node.parentElement;
                            while (current && current.nodeType === 1 && current !== stage) {
                              if (current.getAttribute("id") === "camera-layer") return true;
                              current = current.parentElement;
                            }
                            return false;
                          };
                          const effectiveVisibility = (node) => {
                            let opacity = 1;
                            let current = node;
                            while (current && current.nodeType === 1) {
                              const style = window.getComputedStyle(current);
                              const currentOpacity = Number(style.opacity || "1");
                              if (style.display === "none" || style.visibility === "hidden" || !Number.isFinite(currentOpacity)) {
                                return { visible: false, opacity: 0 };
                              }
                              opacity *= currentOpacity;
                              if (current === stage) break;
                              current = current.parentElement;
                            }
                            return { visible: opacity > 0.01, opacity };
                          };
                          const visible = (node) => {
                            return effectiveVisibility(node).visible;
                          };
                          const renderedRect = (node) => {
                            const bbox = node.getBBox();
                            const matrix = node.getCTM();
                            if (!matrix) return null;
                            const point = stage.createSVGPoint();
                            const transform = (x, y) => {
                              point.x = x;
                              point.y = y;
                              const transformed = point.matrixTransform(matrix);
                              return { x: transformed.x, y: transformed.y };
                            };
                            const corners = [
                              transform(bbox.x, bbox.y),
                              transform(bbox.x + bbox.width, bbox.y),
                              transform(bbox.x, bbox.y + bbox.height),
                              transform(bbox.x + bbox.width, bbox.y + bbox.height),
                            ];
                            const xs = corners.map((corner) => corner.x);
                            const ys = corners.map((corner) => corner.y);
                            const x = Math.min(...xs);
                            const y = Math.min(...ys);
                            const width = Math.max(...xs) - x;
                            const height = Math.max(...ys) - y;
                            return { x, y, width, height };
                          };
                          const radiusValue = (node, name) => {
                            const attrValue = numericAttr(node, name);
                            const styleValuePx = numericCssLength(styleValue(node, name));
                            const baseValue = node[name] && node[name].baseVal ? Number(node[name].baseVal.value) : null;
                            const values = [attrValue, styleValuePx, baseValue]
                              .filter((value) => Number.isFinite(value))
                              .map((value) => Math.abs(value));
                            return values.length ? Math.max(...values) : 0;
                          };
                          const rects = Array.from(stage.querySelectorAll("rect"))
                            .filter(visible)
                            .map((node, rectIndex) => {
                              const rendered = renderedRect(node);
                              const effective = effectiveVisibility(node);
                              const fillOpacity = Number(node.getAttribute("fill-opacity") || styleValue(node, "fill-opacity") || "1");
                              return {
                                index: rectIndex,
                                x: rendered ? rendered.x : numericAttr(node, "x"),
                                y: rendered ? rendered.y : numericAttr(node, "y"),
                                width: rendered ? rendered.width : numericAttr(node, "width"),
                                height: rendered ? rendered.height : numericAttr(node, "height"),
                                rawX: numericAttr(node, "x"),
                                rawY: numericAttr(node, "y"),
                                rawWidth: numericAttr(node, "width"),
                                rawHeight: numericAttr(node, "height"),
                                insideCameraLayer: insideCameraLayer(node),
                                rx: radiusValue(node, "rx") || 0,
                                ry: radiusValue(node, "ry") || 0,
                                fill: node.getAttribute("fill") || styleValue(node, "fill"),
                                fillOpacity: String((Number.isFinite(fillOpacity) ? fillOpacity : 1) * effective.opacity),
                                stroke: node.getAttribute("stroke") || styleValue(node, "stroke"),
                                dataBoxId: node.getAttribute("data-box-id"),
                                dataFillFor: node.getAttribute("data-fill-for"),
                                dataFillAxis: node.getAttribute("data-fill-axis") || "all",
                                dataZoneId: node.getAttribute("data-zone-id"),
                                dataZoneRole: node.getAttribute("data-zone-role"),
                                dataZoneIndex: node.getAttribute("data-zone-index"),
                                dataZoneActive: node.getAttribute("data-zone-active"),
                                dataSourceAnchor: node.getAttribute("data-source-anchor"),
                                dataSourceAnchorJson: node.getAttribute("data-source-anchor-json"),
                                dataSemanticBinding: node.getAttribute("data-semantic-binding"),
                                dataSemanticBindingJson: node.getAttribute("data-semantic-binding-json"),
                                dataSemanticGlyph: node.getAttribute("data-semantic-glyph"),
                                dataMasonryModule: node.getAttribute("data-masonry-module"),
                                dataMasonryWall: node.getAttribute("data-masonry-wall"),
                                dataMasonryOrder: node.getAttribute("data-masonry-order"),
                                dataPaddingExempt: node.getAttribute("data-padding-exempt"),
                              };
                            });
                          const lineLike = Array.from(stage.querySelectorAll("line, polyline, path"))
                            .filter(visible)
                            .map((node, lineIndex) => ({
                              index: lineIndex,
                              tag: node.tagName.toLowerCase(),
                              strokeLinecap: node.getAttribute("stroke-linecap") || styleValue(node, "stroke-linecap"),
                              strokeLinejoin: node.getAttribute("stroke-linejoin") || styleValue(node, "stroke-linejoin"),
                              stroke: node.getAttribute("stroke") || styleValue(node, "stroke"),
                            }));
                          const texts = Array.from(stage.querySelectorAll("text"))
                            .filter(visible)
                            .map((node, textIndex) => {
                              const rendered = renderedRect(node);
                              const effective = effectiveVisibility(node);
                              const text = (node.textContent || "").replace(/\\s+/g, " ").trim();
                              return {
                                index: textIndex,
                                text,
                                x: rendered ? rendered.x : null,
                                y: rendered ? rendered.y : null,
                                width: rendered ? rendered.width : null,
                                height: rendered ? rendered.height : null,
                                opacity: effective.opacity,
                              };
                            })
                            .filter((item) => item.text);
                          return {
                            sample: state,
                            stagePolicy: {
                              edgeStyle: stage.getAttribute("data-edge-style"),
                              boxInteriorPolicy: stage.getAttribute("data-box-interior-policy"),
                              internalPaddingPx: stage.getAttribute("data-internal-padding-px"),
                              grayLevels: stage.getAttribute("data-gray-levels"),
                            },
                            rects,
                            lineLike,
                            texts,
                          };
                        }
                        """,
                        {"videoId": str(config["videoId"]), "seconds": seconds, "selector": selector},
                    )
                    samples.append({"sample": index, "seconds": seconds, **frame})
            finally:
                browser.close()
    return samples, browser_notes


def parse_color(value: object) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    raw = value.strip().lower()
    if raw in {"", "none", "transparent", "currentcolor"}:
        return None
    if re.fullmatch(r"#[0-9a-f]{3}", raw):
        raw = "#" + "".join(ch * 2 for ch in raw[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", raw):
        return int(raw[1:3], 16), int(raw[3:5], 16), int(raw[5:7], 16)
    match = re.fullmatch(
        r"rgba?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)(?:\s*,\s*[\d.]+)?\s*\)",
        raw,
    )
    if match:
        return tuple(max(0, min(255, round(float(part)))) for part in match.groups())  # type: ignore[return-value]
    return None


def parse_opacity(value: object) -> float:
    if value is None:
        return 1.0
    try:
        return float(str(value).strip())
    except ValueError:
        return 1.0


def is_offgrid(value: float, grid: float) -> bool:
    if grid <= 0:
        return False
    nearest = round(value / grid) * grid
    return abs(value - nearest) > 0.01


def shared_edge_ratio(values: list[float]) -> float:
    if not values:
        return 0.0
    rounded = [round(value, 2) for value in values]
    counts: dict[float, int] = {}
    for value in rounded:
        counts[value] = counts.get(value, 0) + 1
    shared = sum(1 for value in rounded if counts[value] > 1)
    return shared / len(rounded)


def rect_geometry(rect: dict[str, Any]) -> tuple[float, float, float, float] | None:
    x = rect.get("x")
    y = rect.get("y")
    width = rect.get("width")
    height = rect.get("height")
    if not all(isinstance(value, (int, float)) for value in (x, y, width, height)):
        return None
    return float(x), float(y), float(width), float(height)


def rect_area(geometry: tuple[float, float, float, float]) -> float:
    return max(0.0, geometry[2]) * max(0.0, geometry[3])


def zero_padding_geometry_checks(rects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parents = {
        str(rect.get("dataBoxId")): rect
        for rect in rects
        if isinstance(rect.get("dataBoxId"), str) and rect.get("dataBoxId")
    }
    checks: list[dict[str, Any]] = []
    for rect in rects:
        fill_for = rect.get("dataFillFor")
        if not isinstance(fill_for, str) or not fill_for:
            continue
        parent = parents.get(fill_for)
        if not parent:
            checks.append({"fillFor": fill_for, "missingParent": True, "maxInternalPaddingPx": float("inf")})
            continue
        parent_geometry = rect_geometry(parent)
        child_geometry = rect_geometry(rect)
        if not parent_geometry or not child_geometry:
            checks.append({"fillFor": fill_for, "invalidGeometry": True, "maxInternalPaddingPx": float("inf")})
            continue
        px, py, pw, ph = parent_geometry
        cx, cy, cw, ch = child_geometry
        offsets = {
            "left": cx - px,
            "top": cy - py,
            "right": (px + pw) - (cx + cw),
            "bottom": (py + ph) - (cy + ch),
        }
        axis = str(rect.get("dataFillAxis") or "all")
        required_edges = ["left", "top", "bottom"] if axis == "x-progress" else list(offsets)
        required_offsets = {edge: offsets[edge] for edge in required_edges}
        checks.append(
            {
                "fillFor": fill_for,
                "axis": axis,
                "requiredOffsets": required_offsets,
                "maxInternalPaddingPx": max(abs(value) for value in required_offsets.values()) if required_offsets else 0.0,
            }
        )
    return checks


def untagged_inset_rect_checks(
    rects: list[dict[str, Any]],
    *,
    min_area_ratio: float,
    min_size_px: float,
    min_padding_px: float,
) -> list[dict[str, Any]]:
    geometries = [(rect, geometry) for rect in rects if (geometry := rect_geometry(rect))]
    largest_area = max((rect_area(geometry) for _, geometry in geometries), default=0.0)
    checks: list[dict[str, Any]] = []
    for child, child_geometry in geometries:
        if child.get("dataFillFor") or child.get("dataBoxId") or child.get("dataZoneId"):
            continue
        if parse_opacity(child.get("fillOpacity")) <= 0.01:
            continue
        cx, cy, cw, ch = child_geometry
        child_area = rect_area(child_geometry)
        if child_area <= 0:
            continue
        best: dict[str, Any] | None = None
        best_area = float("inf")
        for parent, parent_geometry in geometries:
            if parent is child or parent.get("dataFillFor"):
                continue
            parent_index = parent.get("index")
            child_index = child.get("index")
            if isinstance(parent_index, int) and isinstance(child_index, int) and parent_index > child_index:
                continue
            if parse_color(parent.get("stroke")) is None and parse_color(parent.get("fill")) is None:
                continue
            px, py, pw, ph = parent_geometry
            parent_area = rect_area(parent_geometry)
            if largest_area > 0 and parent_area >= largest_area * 0.9:
                continue
            parent_aspect = max(pw / ph, ph / pw) if pw > 0 and ph > 0 else float("inf")
            if parent_aspect > 8.0:
                continue
            if parent_area <= child_area or parent_area >= best_area:
                continue
            offsets = {
                "left": cx - px,
                "top": cy - py,
                "right": (px + pw) - (cx + cw),
                "bottom": (py + ph) - (cy + ch),
            }
            if any(value <= min_padding_px for value in offsets.values()):
                continue
            area_ratio = child_area / parent_area
            size_signal = min(cw, ch) >= min_size_px and min(pw, ph) >= min_size_px * 2
            horizontal_padding_balance = min(offsets["left"], offsets["right"]) / max(offsets["left"], offsets["right"])
            vertical_padding_balance = min(offsets["top"], offsets["bottom"]) / max(offsets["top"], offsets["bottom"])
            balanced_padding = horizontal_padding_balance >= 0.45 and vertical_padding_balance >= 0.45
            if not balanced_padding:
                continue
            if area_ratio < min_area_ratio:
                continue
            best_area = parent_area
            best = {
                "parentRect": parent.get("index"),
                "childRect": child.get("index"),
                "requiredOffsets": offsets,
                "areaRatio": area_ratio,
                "sizeSignal": size_signal,
                "balancedPadding": balanced_padding,
                "horizontalPaddingBalance": horizontal_padding_balance,
                "verticalPaddingBalance": vertical_padding_balance,
                "maxInternalPaddingPx": max(abs(value) for value in offsets.values()),
            }
        if best:
            checks.append(best)
    return checks


def padded_module_interior_checks(
    rects: list[dict[str, Any]],
    *,
    min_child_count: int,
    min_area_ratio: float,
    min_offset_px: float,
    min_size_px: float,
) -> list[dict[str, Any]]:
    geometries = [(rect, geometry) for rect in rects if (geometry := rect_geometry(rect))]
    checks: list[dict[str, Any]] = []
    for parent, parent_geometry in geometries:
        if parent.get("dataFillFor"):
            continue
        if parent.get("dataPaddingExempt") == "zone-evidence-outline":
            continue
        is_module = str(parent.get("dataMasonryModule") or "").strip().lower() == "true"
        is_zone = bool(parent.get("dataZoneId")) or bool(parent.get("dataBoxId"))
        if not (is_module or is_zone):
            continue
        px, py, pw, ph = parent_geometry
        parent_area = rect_area(parent_geometry)
        if parent_area <= 0 or min(pw, ph) < min_size_px * 3:
            continue
        parent_index = parent.get("index")
        children: list[dict[str, Any]] = []
        child_area = 0.0
        max_padding = 0.0
        min_offsets = {"left": float("inf"), "top": float("inf"), "right": float("inf"), "bottom": float("inf")}
        for child, child_geometry in geometries:
            if child is parent:
                continue
            if child.get("dataFillFor") or str(child.get("dataMasonryModule") or "").strip().lower() == "true":
                continue
            if child.get("dataPaddingExempt") == "zone-evidence-outline":
                continue
            child_index = child.get("index")
            if isinstance(parent_index, int) and isinstance(child_index, int) and child_index <= parent_index:
                continue
            cx, cy, cw, ch = child_geometry
            if min(cw, ch) < min_size_px:
                continue
            offsets = {
                "left": cx - px,
                "top": cy - py,
                "right": (px + pw) - (cx + cw),
                "bottom": (py + ph) - (cy + ch),
            }
            if any(value < min_offset_px for value in offsets.values()):
                continue
            area = rect_area(child_geometry)
            if area <= 0:
                continue
            if str(child.get("dataSemanticGlyph") or "").strip().lower() == "true" and area / parent_area < 0.035:
                continue
            children.append(
                {
                    "rect": child.get("index"),
                    "offsets": {edge: round(value, 3) for edge, value in offsets.items()},
                    "area": round(area, 3),
                    "fill": child.get("fill"),
                    "stroke": child.get("stroke"),
                    "dataBoxId": child.get("dataBoxId"),
                    "dataZoneId": child.get("dataZoneId"),
                }
            )
            child_area += area
            max_padding = max(max_padding, max(abs(value) for value in offsets.values()))
            for edge, value in offsets.items():
                min_offsets[edge] = min(min_offsets[edge], value)
        area_ratio = child_area / parent_area if parent_area else 0.0
        if len(children) >= min_child_count and area_ratio >= min_area_ratio:
            checks.append(
                {
                    "parentRect": parent.get("index"),
                    "parentIsMasonryModule": is_module,
                    "parentZoneId": parent.get("dataZoneId"),
                    "childCount": len(children),
                    "childAreaRatio": round(area_ratio, 4),
                    "minOffsets": {edge: round(value, 3) for edge, value in min_offsets.items() if value < float("inf")},
                    "maxInternalPaddingPx": max_padding,
                    "children": children[:12],
                }
            )
    return checks


def hex_gray(rgb: tuple[int, int, int]) -> str | None:
    r, g, b = rgb
    if r == g == b:
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


def is_role_red(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r >= 100 and g <= 100 and b <= 130 and (r - g) >= 35


def gray_spread(gray_levels: set[str]) -> float:
    values = [int(color[1:3], 16) for color in gray_levels if re.fullmatch(r"#[0-9a-f]{6}", color)]
    if len(values) < 2:
        return 0.0
    return float(max(values) - min(values))


def analyze_texts(
    texts: list[dict[str, Any]],
    viewport_area: float,
    non_text_mark_count: int,
    forbidden_fragments: list[str],
) -> dict[str, Any]:
    text_area = 0.0
    largest_text_area = 0.0
    text_character_count = 0
    title_band_texts: list[dict[str, Any]] = []
    ellipsized_texts: list[dict[str, Any]] = []
    normalized_forbidden = [item.strip().lower() for item in forbidden_fragments if item.strip()]

    for item in texts:
        text = str(item.get("text") or "").strip()
        text_character_count += len(text)
        width = item.get("width")
        height = item.get("height")
        opacity = item.get("opacity")
        area = 0.0
        if isinstance(width, (int, float)) and isinstance(height, (int, float)):
            area = max(0.0, float(width)) * max(0.0, float(height))
            if isinstance(opacity, (int, float)):
                area *= max(0.0, min(1.0, float(opacity)))
        text_area += area
        largest_text_area = max(largest_text_area, area)

        lower_text = text.lower()
        y_value = item.get("y")
        is_forbidden_text = any(fragment and fragment in lower_text for fragment in normalized_forbidden)
        is_editorial_word = any(word in lower_text for word in ("draft", "checked date", "subtitle", "caption"))
        is_large_top_band = (
            isinstance(y_value, (int, float))
            and float(y_value) <= 72.0
            and isinstance(width, (int, float))
            and float(width) >= 260.0
            and len(text) >= 18
        )
        if is_forbidden_text or is_editorial_word or is_large_top_band:
            title_band_texts.append(
                {
                    "index": item.get("index"),
                    "text": text[:80],
                    "x": item.get("x"),
                    "y": item.get("y"),
                    "width": item.get("width"),
                    "height": item.get("height"),
                }
            )
        if text.endswith("...") or text.endswith("…"):
            ellipsized_texts.append(
                {
                    "index": item.get("index"),
                    "text": text[:80],
                    "x": item.get("x"),
                    "y": item.get("y"),
                    "width": item.get("width"),
                    "height": item.get("height"),
                }
            )

    text_element_count = len(texts)
    return {
        "textElementCount": text_element_count,
        "textCharacterCount": text_character_count,
        "textBBoxArea": round(text_area, 3),
        "largestTextBoxArea": round(largest_text_area, 3),
        "textBBoxAreaRatio": (text_area / viewport_area) if viewport_area > 0 else 0.0,
        "largestTextBoxAreaRatio": (largest_text_area / viewport_area) if viewport_area > 0 else 0.0,
        "nonTextMarkCount": non_text_mark_count,
        "markToTextRatio": non_text_mark_count / max(1, text_element_count),
        "titleBandTextCount": len(title_band_texts),
        "titleBandTexts": title_band_texts[:12],
        "ellipsizedTextCount": len(ellipsized_texts),
        "ellipsizedTexts": ellipsized_texts[:12],
    }


def analyze_sample(
    sample: dict[str, Any],
    grid: float,
    min_untagged_inset_area_ratio: float,
    min_untagged_inset_size_px: float,
    min_padded_module_child_count: int,
    min_padded_module_area_ratio: float,
    min_padded_module_offset_px: float,
    min_gray_level_area_ratio: float,
    viewport_area: float,
    forbidden_text_fragments: list[str],
) -> dict[str, Any]:
    rects = [rect for rect in sample.get("rects", []) if isinstance(rect, dict)]
    line_like = [line for line in sample.get("lineLike", []) if isinstance(line, dict)]
    texts = [text for text in sample.get("texts", []) if isinstance(text, dict)]
    edges: list[float] = []
    offgrid_edges: list[dict[str, Any]] = []
    rounded_rects: list[dict[str, Any]] = []
    gray_areas: dict[str, float] = {}
    total_rendered_rect_area = 0.0
    red_rect_area = 0.0
    zero_padding_checks = zero_padding_geometry_checks(rects)
    zero_padding_violations = [
        item
        for item in zero_padding_checks
        if float(item.get("maxInternalPaddingPx") or 0.0) > 0.5
        or item.get("missingParent")
        or item.get("invalidGeometry")
    ]
    untagged_inset_checks = untagged_inset_rect_checks(
        rects,
        min_area_ratio=min_untagged_inset_area_ratio,
        min_size_px=min_untagged_inset_size_px,
        min_padding_px=0.5,
    )
    padded_module_checks = padded_module_interior_checks(
        rects,
        min_child_count=min_padded_module_child_count,
        min_area_ratio=min_padded_module_area_ratio,
        min_offset_px=min_padded_module_offset_px,
        min_size_px=min_untagged_inset_size_px,
    )
    zone_rects = [rect for rect in rects if rect.get("dataZoneId")]
    zone_ids = sorted({str(rect.get("dataZoneId")) for rect in zone_rects if rect.get("dataZoneId")})
    zone_roles = sorted({str(rect.get("dataZoneRole")) for rect in zone_rects if rect.get("dataZoneRole")})

    def rect_data_values(rect: dict[str, Any], json_key: str, legacy_key: str) -> list[str]:
        raw_json = rect.get(json_key)
        if isinstance(raw_json, str) and raw_json.strip():
            try:
                decoded = json.loads(raw_json)
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, list):
                return [str(value).strip() for value in decoded if str(value).strip()]
        return [part.strip() for part in str(rect.get(legacy_key) or "").split("|") if part.strip()]

    source_anchors = sorted(
        {
            part
            for rect in zone_rects
            for part in rect_data_values(rect, "dataSourceAnchorJson", "dataSourceAnchor")
        }
    )
    semantic_bindings = sorted(
        {
            part
            for rect in zone_rects
            for part in rect_data_values(rect, "dataSemanticBindingJson", "dataSemanticBinding")
        }
    )
    masonry_rects = [
        rect
        for rect in rects
        if str(rect.get("dataMasonryModule") or "").strip().lower() == "true"
    ]
    semantic_glyph_rects = [
        rect
        for rect in rects
        if str(rect.get("dataSemanticGlyph") or "").strip().lower() == "true"
    ]
    masonry_sizes = sorted(
        {
            (
                round(float(rect.get("rawWidth") if rect.get("rawWidth") is not None else rect.get("width") or 0.0), 3),
                round(float(rect.get("rawHeight") if rect.get("rawHeight") is not None else rect.get("height") or 0.0), 3),
            )
            for rect in masonry_rects
        }
    )
    masonry_area = sum(
        max(0.0, float(rect.get("width") or 0.0)) * max(0.0, float(rect.get("height") or 0.0))
        for rect in masonry_rects
    )
    active_zone_ids = sorted(
        {
            str(rect.get("dataZoneId"))
            for rect in zone_rects
            if str(rect.get("dataZoneActive") or "").lower() == "true" and rect.get("dataZoneId")
        }
    )

    for rect in rects:
        x = rect.get("x")
        y = rect.get("y")
        width = rect.get("width")
        height = rect.get("height")
        raw_x = rect.get("rawX")
        raw_y = rect.get("rawY")
        raw_width = rect.get("rawWidth")
        raw_height = rect.get("rawHeight")
        rect_area_value = 0.0
        if rect.get("insideCameraLayer") and all(isinstance(value, (int, float)) for value in (raw_x, raw_y, raw_width, raw_height)):
            edge_x = float(raw_x)
            edge_y = float(raw_y)
            edge_width = float(raw_width)
            edge_height = float(raw_height)
        elif all(isinstance(value, (int, float)) for value in (x, y, width, height)):
            edge_x = float(x)
            edge_y = float(y)
            edge_width = float(width)
            edge_height = float(height)
        else:
            edge_x = edge_y = edge_width = edge_height = None
        if edge_x is not None:
            rect_edges = [edge_x, edge_x + edge_width, edge_y, edge_y + edge_height]
            edges.extend(rect_edges)
            for edge in rect_edges:
                if is_offgrid(edge, grid):
                    offgrid_edges.append({"rect": rect.get("index"), "edge": edge})
        if all(isinstance(value, (int, float)) for value in (x, y, width, height)):
            rect_area_value = max(0.0, float(width)) * max(0.0, float(height)) * max(0.0, parse_opacity(rect.get("fillOpacity")))
            total_rendered_rect_area += rect_area_value
        rx = float(rect.get("rx") or 0)
        ry = float(rect.get("ry") or 0)
        if abs(rx) > 0.001 or abs(ry) > 0.001:
            rounded_rects.append({"rect": rect.get("index"), "rx": rx, "ry": ry})
        if parse_opacity(rect.get("fillOpacity")) > 0.01:
            parsed_fill = parse_color(rect.get("fill"))
            if parsed_fill is not None and is_role_red(parsed_fill):
                red_rect_area += rect_area_value
            gray = hex_gray(parsed_fill or (-1, -2, -3))
            if gray is not None:
                gray_areas[gray] = gray_areas.get(gray, 0.0) + rect_area_value

    gray_levels = {
        color
        for color, area in gray_areas.items()
        if total_rendered_rect_area > 0 and area / total_rendered_rect_area >= min_gray_level_area_ratio
    }

    rounded_lines = []
    for item in line_like:
        cap = str(item.get("strokeLinecap") or "").strip().lower()
        join = str(item.get("strokeLinejoin") or "").strip().lower()
        if cap == "round" or join == "round":
            rounded_lines.append(
                {
                    "index": item.get("index"),
                    "tag": item.get("tag"),
                    "strokeLinecap": cap,
                    "strokeLinejoin": join,
                }
            )

    text_metrics = analyze_texts(
        texts,
        viewport_area=viewport_area,
        non_text_mark_count=len(rects) + len(line_like),
        forbidden_fragments=forbidden_text_fragments,
    )

    return {
        "sample": sample.get("sample"),
        "seconds": sample.get("seconds"),
        "stagePolicy": sample.get("stagePolicy"),
        "rectCount": len(rects),
        "lineLikeCount": len(line_like),
        "zoneElementCount": len(zone_rects),
        "zoneIdCount": len(zone_ids),
        "zoneRoleCount": len(zone_roles),
        "sourceAnchorCount": len(source_anchors),
        "semanticBindingCount": len(semantic_bindings),
        "semanticGlyphCount": len(semantic_glyph_rects),
        "masonryModuleCount": len(masonry_rects),
        "masonrySizeCount": len(masonry_sizes),
        "masonrySizes": [{"width": width, "height": height} for width, height in masonry_sizes[:12]],
        "masonryAreaRatio": (masonry_area / viewport_area) if viewport_area else 0.0,
        "activeZoneCount": len(active_zone_ids),
        "zoneIds": zone_ids,
        "sourceAnchors": source_anchors,
        "semanticBindings": semantic_bindings,
        "activeZoneIds": active_zone_ids[:12],
        **text_metrics,
        "edgeCount": len(edges),
        "offgridEdgeCount": len(offgrid_edges),
        "offgridRatio": (len(offgrid_edges) / len(edges)) if edges else 0.0,
        "sharedEdgeRatio": shared_edge_ratio(edges),
        "offgridEdges": offgrid_edges[:12],
        "roundedRectCount": len(rounded_rects),
        "roundedRects": rounded_rects[:12],
        "roundedLineSignalCount": len(rounded_lines),
        "roundedLineSignals": rounded_lines[:12],
        "grayLevels": sorted(gray_levels),
        "allGrayLevels": sorted(gray_areas),
        "grayLevelAreas": {color: round(area, 3) for color, area in sorted(gray_areas.items())},
        "totalRenderedRectArea": round(total_rendered_rect_area, 3),
        "redRectArea": round(red_rect_area, 3),
        "redRectAreaRatio": (red_rect_area / viewport_area) if viewport_area else 0.0,
        "minGrayLevelAreaRatio": min_gray_level_area_ratio,
        "grayLevelCount": len(gray_levels),
        "grayLuminanceSpread": gray_spread(gray_levels),
        "zeroPaddingGeometryCheckCount": len(zero_padding_checks),
        "zeroPaddingGeometryViolationCount": len(zero_padding_violations),
        "zeroPaddingGeometryViolations": zero_padding_violations[:12],
        "untaggedInsetRectCheckCount": len(untagged_inset_checks),
        "untaggedInsetRectViolationCount": len(untagged_inset_checks),
        "untaggedInsetRectViolations": untagged_inset_checks[:12],
        "paddedModuleInteriorCheckCount": len(padded_module_checks),
        "paddedModuleInteriorViolationCount": len(padded_module_checks),
        "paddedModuleInteriorViolations": padded_module_checks[:12],
        "maxRenderedInternalPaddingPx": max(
            (
                float(item.get("maxInternalPaddingPx") or 0.0)
                for item in [*zero_padding_checks, *untagged_inset_checks, *padded_module_checks]
            ),
            default=0.0,
        ),
    }


def build_findings(
    args: argparse.Namespace,
    analyzed: list[dict[str, Any]],
    *,
    masonry_required: bool = False,
    min_masonry_modules: int = 6,
    min_masonry_size_count: int = 4,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    total_edges = sum(int(item.get("edgeCount") or 0) for item in analyzed)
    total_offgrid = sum(int(item.get("offgridEdgeCount") or 0) for item in analyzed)
    total_rounded_rects = sum(int(item.get("roundedRectCount") or 0) for item in analyzed)
    total_rounded_lines = sum(int(item.get("roundedLineSignalCount") or 0) for item in analyzed)
    total_zero_padding_checks = sum(int(item.get("zeroPaddingGeometryCheckCount") or 0) for item in analyzed)
    total_zero_padding_violations = sum(int(item.get("zeroPaddingGeometryViolationCount") or 0) for item in analyzed)
    total_untagged_inset_checks = sum(int(item.get("untaggedInsetRectCheckCount") or 0) for item in analyzed)
    total_untagged_inset_violations = sum(int(item.get("untaggedInsetRectViolationCount") or 0) for item in analyzed)
    total_padded_module_checks = sum(int(item.get("paddedModuleInteriorCheckCount") or 0) for item in analyzed)
    total_padded_module_violations = sum(int(item.get("paddedModuleInteriorViolationCount") or 0) for item in analyzed)
    max_internal_padding = max((float(item.get("maxRenderedInternalPaddingPx") or 0.0) for item in analyzed), default=0.0)
    max_zone_elements = max((int(item.get("zoneElementCount") or 0) for item in analyzed), default=0)
    masonry_module_counts = [int(item.get("masonryModuleCount") or 0) for item in analyzed]
    max_masonry_modules = max(masonry_module_counts, default=0)
    min_masonry_modules_seen = min(masonry_module_counts, default=0)
    masonry_module_count_range = max_masonry_modules - min_masonry_modules_seen
    masonry_module_count_distinct = len(set(masonry_module_counts))
    masonry_module_count_nondecreasing = all(
        later >= earlier for earlier, later in zip(masonry_module_counts, masonry_module_counts[1:])
    )
    max_masonry_size_count = max((int(item.get("masonrySizeCount") or 0) for item in analyzed), default=0)
    max_masonry_area_ratio = max((float(item.get("masonryAreaRatio") or 0.0) for item in analyzed), default=0.0)
    red_area_ratios = [float(item.get("redRectAreaRatio") or 0.0) for item in analyzed]
    max_red_rect_area_ratio = max(red_area_ratios, default=0.0)
    max_gray_count = max((int(item.get("grayLevelCount") or 0) for item in analyzed), default=0)
    max_gray_spread = max((float(item.get("grayLuminanceSpread") or 0.0) for item in analyzed), default=0.0)
    active_gray_samples = [item for item in analyzed if int(item.get("rectCount") or 0) > 0]
    gray_counts = [int(item.get("grayLevelCount") or 0) for item in active_gray_samples]
    gray_spreads = [float(item.get("grayLuminanceSpread") or 0.0) for item in active_gray_samples]
    median_gray_count = float(statistics.median(gray_counts)) if gray_counts else 0.0
    median_gray_spread = float(statistics.median(gray_spreads)) if gray_spreads else 0.0
    gray_sample_passes = [
        item
        for item in active_gray_samples
        if int(item.get("grayLevelCount") or 0) >= args.min_gray_levels
        and float(item.get("grayLuminanceSpread") or 0.0) >= args.min_gray_luminance_spread
    ]
    gray_sample_pass_ratio = (len(gray_sample_passes) / len(active_gray_samples)) if active_gray_samples else 0.0
    min_shared_edge_ratio = min((float(item.get("sharedEdgeRatio") or 0.0) for item in analyzed if item.get("edgeCount")), default=0.0)
    offgrid_ratio = (total_offgrid / total_edges) if total_edges else 0.0
    final = analyzed[-1] if analyzed else {}
    final_gray_count = int(final.get("grayLevelCount") or 0)
    final_gray_spread = float(final.get("grayLuminanceSpread") or 0.0)
    text_area_ratios = [float(item.get("textBBoxAreaRatio") or 0.0) for item in analyzed]
    largest_text_ratios = [float(item.get("largestTextBoxAreaRatio") or 0.0) for item in analyzed]
    mark_to_text_ratios = [float(item.get("markToTextRatio") or 0.0) for item in analyzed]
    median_text_area_ratio = float(statistics.median(text_area_ratios)) if text_area_ratios else 0.0
    max_largest_text_box_area_ratio = max(largest_text_ratios, default=0.0)
    median_mark_to_text_ratio = float(statistics.median(mark_to_text_ratios)) if mark_to_text_ratios else 0.0
    max_text_element_count = max((int(item.get("textElementCount") or 0) for item in analyzed), default=0)
    max_text_character_count = max((int(item.get("textCharacterCount") or 0) for item in analyzed), default=0)
    title_band_text_count = sum(int(item.get("titleBandTextCount") or 0) for item in analyzed)
    ellipsized_text_count = sum(int(item.get("ellipsizedTextCount") or 0) for item in analyzed)

    if max_zone_elements < args.min_zone_elements:
        findings.append(
            {
                "code": "rendered-too-few-zone-elements",
                "message": f"Rendered frames expose at most {max_zone_elements} data-zone-id elements; expected at least {args.min_zone_elements}.",
                "samples": sorted(analyzed, key=lambda item: int(item.get("zoneElementCount") or 0))[:3],
            }
        )
    if masonry_required and max_masonry_modules < min_masonry_modules:
        findings.append(
            {
                "code": "rendered-missing-masonry-modules",
                "message": (
                    f"Rendered frames expose at most {max_masonry_modules} data-masonry-module rects; "
                    f"expected at least {min_masonry_modules}."
                ),
                "samples": sorted(analyzed, key=lambda item: int(item.get("masonryModuleCount") or 0))[:3],
            }
        )
    if masonry_required and max_masonry_size_count < min_masonry_size_count:
        findings.append(
            {
                "code": "rendered-weak-masonry-size-variety",
                "message": (
                    f"Rendered Masonry exposes at most {max_masonry_size_count} module sizes; "
                    f"expected at least {min_masonry_size_count}."
                ),
                "samples": sorted(analyzed, key=lambda item: int(item.get("masonrySizeCount") or 0))[:3],
            }
        )
    if masonry_required and max_masonry_area_ratio < 0.35:
        findings.append(
            {
                "code": "rendered-masonry-area-too-small",
                "message": f"Rendered Masonry area ratio {max_masonry_area_ratio:.3f} is below 0.350.",
                "samples": sorted(analyzed, key=lambda item: float(item.get("masonryAreaRatio") or 0.0))[:3],
            }
        )
    if masonry_required and masonry_module_count_distinct < 3:
        findings.append(
            {
                "code": "rendered-static-masonry-construction",
                "message": (
                    f"Rendered Masonry exposes only {masonry_module_count_distinct} distinct module counts "
                    "across sampled frames; expected visible construction over time."
                ),
                "moduleCounts": masonry_module_counts,
            }
        )
    if masonry_required and masonry_module_count_range < 4:
        findings.append(
            {
                "code": "rendered-weak-masonry-construction-growth",
                "message": (
                    f"Rendered Masonry module count changes by {masonry_module_count_range}; "
                    "expected at least 4 modules of construction growth."
                ),
                "moduleCounts": masonry_module_counts,
            }
        )
    if masonry_required and not masonry_module_count_nondecreasing:
        findings.append(
            {
                "code": "rendered-masonry-construction-regression",
                "message": "Rendered Masonry module count decreases across sampled construction frames.",
                "moduleCounts": masonry_module_counts,
            }
        )
    if masonry_required and max_text_element_count > 6:
        findings.append(
            {
                "code": "rendered-masonry-too-many-text-elements",
                "message": (
                    f"Rendered Masonry exposes {max_text_element_count} text elements; "
                    "expected no more than 6 so the wall is carried by marks, modules, and motion."
                ),
            }
        )
    if masonry_required and max_text_character_count > 80:
        findings.append(
            {
                "code": "rendered-masonry-too-many-text-characters",
                "message": (
                    f"Rendered Masonry exposes {max_text_character_count} text characters; "
                    "expected no more than 80 for low-text Metro output."
                ),
            }
        )
    if total_rounded_rects > args.max_rounded_rects:
        findings.append(
            {
                "code": "rendered-rounded-rects",
                "message": f"{total_rounded_rects} rendered rects have nonzero rx/ry; allowed {args.max_rounded_rects}.",
                "samples": [item for item in analyzed if item.get("roundedRectCount")][:3],
            }
        )
    if total_rounded_lines > args.max_rounded_line_signals:
        findings.append(
            {
                "code": "rendered-rounded-line-caps-or-joins",
                "message": f"{total_rounded_lines} rendered line/path cap or join signals are round; allowed {args.max_rounded_line_signals}.",
                "samples": [item for item in analyzed if item.get("roundedLineSignalCount")][:3],
            }
        )
    if offgrid_ratio > args.max_offgrid_ratio:
        findings.append(
            {
                "code": "rendered-offgrid-rect-edges",
                "message": f"Rendered off-grid edge ratio {offgrid_ratio:.4f} exceeds {args.max_offgrid_ratio:.4f}.",
                "samples": [item for item in analyzed if item.get("offgridEdgeCount")][:3],
            }
        )
    if min_shared_edge_ratio < args.min_shared_edge_ratio:
        findings.append(
            {
                "code": "rendered-weak-shared-edge-composition",
                "message": (
                    f"Minimum rendered shared-edge ratio {min_shared_edge_ratio:.4f} "
                    f"is below {args.min_shared_edge_ratio:.4f}."
                ),
                "samples": sorted(analyzed, key=lambda item: float(item.get("sharedEdgeRatio") or 0.0))[:3],
            }
        )
    if max_red_rect_area_ratio > args.max_red_rect_area_ratio:
        findings.append(
            {
                "code": "rendered-red-rect-area-too-high",
                "message": (
                    f"Rendered red rectangle area ratio {max_red_rect_area_ratio:.4f} exceeds "
                    f"{args.max_red_rect_area_ratio:.4f}; red should act as state, emphasis, or route, not a dominant surface."
                ),
                "samples": sorted(analyzed, key=lambda item: float(item.get("redRectAreaRatio") or 0.0), reverse=True)[:3],
            }
        )
    if max_gray_count < args.min_gray_levels:
        findings.append(
            {
                "code": "rendered-insufficient-gray-hierarchy",
                "message": f"Rendered frames expose at most {max_gray_count} gray levels; expected at least {args.min_gray_levels}.",
            }
        )
    if max_gray_spread < args.min_gray_luminance_spread:
        findings.append(
            {
                "code": "rendered-weak-gray-spread",
                "message": f"Rendered frame gray luminance spread {max_gray_spread:.1f} is below {args.min_gray_luminance_spread:.1f}.",
            }
        )
    if median_gray_count < args.min_gray_levels:
        findings.append(
            {
                "code": "rendered-median-insufficient-gray-hierarchy",
                "message": (
                    f"Median active rendered sample exposes {median_gray_count:.1f} gray levels; "
                    f"expected at least {args.min_gray_levels}."
                ),
            }
        )
    if median_gray_spread < args.min_gray_luminance_spread:
        findings.append(
            {
                "code": "rendered-median-weak-gray-spread",
                "message": (
                    f"Median active rendered sample gray luminance spread {median_gray_spread:.1f} "
                    f"is below {args.min_gray_luminance_spread:.1f}."
                ),
            }
        )
    if gray_sample_pass_ratio < args.min_gray_sample_pass_ratio:
        findings.append(
            {
                "code": "rendered-unstable-gray-hierarchy",
                "message": (
                    f"Only {gray_sample_pass_ratio:.3f} of active rendered samples meet gray hierarchy "
                    f"thresholds; expected at least {args.min_gray_sample_pass_ratio:.3f}."
                ),
                "sampleCount": len(active_gray_samples),
                "passingSampleCount": len(gray_sample_passes),
            }
        )
    if median_text_area_ratio > args.max_median_text_area_ratio:
        findings.append(
            {
                "code": "rendered-text-area-too-high",
                "message": (
                    f"Median rendered text area ratio {median_text_area_ratio:.4f} exceeds "
                    f"{args.max_median_text_area_ratio:.4f}; Metro videos should explain through visual structure."
                ),
                "samples": sorted(analyzed, key=lambda item: float(item.get("textBBoxAreaRatio") or 0.0), reverse=True)[:3],
            }
        )
    if max_largest_text_box_area_ratio > args.max_largest_text_box_area_ratio:
        findings.append(
            {
                "code": "rendered-dominant-text-box",
                "message": (
                    f"Largest rendered text box ratio {max_largest_text_box_area_ratio:.4f} exceeds "
                    f"{args.max_largest_text_box_area_ratio:.4f}."
                ),
                "samples": sorted(analyzed, key=lambda item: float(item.get("largestTextBoxAreaRatio") or 0.0), reverse=True)[:3],
            }
        )
    if median_mark_to_text_ratio < args.min_median_mark_to_text_ratio:
        findings.append(
            {
                "code": "weak-rendered-mark-to-text-density",
                "message": (
                    f"Median rendered mark-to-text ratio {median_mark_to_text_ratio:.3f} is below "
                    f"{args.min_median_mark_to_text_ratio:.3f}; add marks, zones, rails, edges, or state geometry instead of labels."
                ),
                "samples": sorted(analyzed, key=lambda item: float(item.get("markToTextRatio") or 0.0))[:3],
            }
        )
    if title_band_text_count > args.max_title_band_text_count:
        findings.append(
            {
                "code": "rendered-title-band-text",
                "message": f"{title_band_text_count} rendered title/date/editorial text instances were found; allowed {args.max_title_band_text_count}.",
                "samples": [item for item in analyzed if item.get("titleBandTextCount")][:3],
            }
        )
    if ellipsized_text_count > args.max_ellipsized_text_count:
        findings.append(
            {
                "code": "rendered-ellipsized-text",
                "message": f"{ellipsized_text_count} rendered text labels end with ellipsis; allowed {args.max_ellipsized_text_count}.",
                "samples": [item for item in analyzed if item.get("ellipsizedTextCount")][:3],
            }
        )
    if final_gray_count < args.min_final_gray_levels:
        findings.append(
            {
                "code": "rendered-final-insufficient-gray-hierarchy",
                "message": f"Final rendered sample exposes {final_gray_count} gray levels; expected at least {args.min_final_gray_levels}.",
            }
        )
    if final_gray_spread < args.min_final_gray_luminance_spread:
        findings.append(
            {
                "code": "rendered-final-weak-gray-spread",
                "message": (
                    f"Final rendered sample gray luminance spread {final_gray_spread:.1f} "
                    f"is below {args.min_final_gray_luminance_spread:.1f}."
                ),
            }
        )
    if args.require_zero_padding_policy:
        for item in analyzed:
            policy = item.get("stagePolicy") if isinstance(item.get("stagePolicy"), dict) else {}
            if policy.get("edgeStyle") != "square":
                findings.append(
                    {
                        "code": "rendered-stage-edge-policy-missing",
                        "message": f"Stage data-edge-style is {policy.get('edgeStyle')!r}, expected 'square'.",
                    }
                )
                break
            if policy.get("boxInteriorPolicy") != "zero" or str(policy.get("internalPaddingPx")) != "0":
                findings.append(
                    {
                        "code": "rendered-zero-padding-policy-missing",
                        "message": (
                            "Stage zero-padding policy is missing or inconsistent: "
                            f"boxInteriorPolicy={policy.get('boxInteriorPolicy')!r}, "
                            f"internalPaddingPx={policy.get('internalPaddingPx')!r}."
                        ),
                    }
                )
                break
        if total_zero_padding_violations:
            findings.append(
                {
                    "code": "rendered-internal-padding-geometry",
                    "message": (
                        f"{total_zero_padding_violations} rendered fill associations have internal padding "
                        "or invalid parent geometry; allowed 0."
                    ),
                    "maxRenderedInternalPaddingPx": max_internal_padding,
                    "samples": [item for item in analyzed if item.get("zeroPaddingGeometryViolationCount")][:3],
                }
            )
        if total_untagged_inset_violations > args.max_untagged_inset_rects:
            findings.append(
                {
                    "code": "rendered-untagged-inset-rect-padding",
                    "message": (
                        f"{total_untagged_inset_violations} untagged rendered rects look inset inside a parent box; "
                        f"allowed {args.max_untagged_inset_rects}."
                    ),
                    "samples": [item for item in analyzed if item.get("untaggedInsetRectViolationCount")][:3],
                }
            )
        if (
            masonry_required
            and max_masonry_modules > 0
            and total_zero_padding_checks == 0
            and total_untagged_inset_checks == 0
            and total_padded_module_checks == 0
        ):
            findings.append(
                {
                    "code": "rendered-padding-detector-no-coverage",
                    "message": (
                        "Rendered frames contain Masonry modules but no explicit or implicit padding geometry "
                        "checks ran. The zero-padding claim has no measured coverage."
                    ),
                    "maxMasonryModuleCount": max_masonry_modules,
                }
            )
        if total_padded_module_violations > args.max_padded_module_interiors:
            findings.append(
                {
                    "code": "rendered-padded-module-interiors",
                    "message": (
                        f"{total_padded_module_violations} module interiors contain inset child-rect groups; "
                        f"allowed {args.max_padded_module_interiors}. Content should be flush to module edges "
                        "or moved into adjacent flush lanes."
                    ),
                    "samples": [item for item in analyzed if item.get("paddedModuleInteriorViolationCount")][:3],
                }
            )
        if (total_zero_padding_checks or total_untagged_inset_checks or total_padded_module_checks) and max_internal_padding > args.max_rendered_internal_padding_px:
            findings.append(
                {
                    "code": "rendered-internal-padding-too-large",
                    "message": (
                        f"Maximum rendered internal padding {max_internal_padding:.2f}px exceeds "
                        f"{args.max_rendered_internal_padding_px:.2f}px."
                    ),
                }
            )
    return findings


def main() -> int:
    args = parse_args()
    html = args.html.resolve()
    if not html.exists():
        print(f"HTML file not found: {html}", file=sys.stderr)
        return 2

    config = resolve_config(args)
    times = sample_times(float(config["duration"]), args.samples)
    try:
        frames, browser_notes = sample_rendered_frames(
            html,
            times,
            config,
            args.selector,
            args.install_browser,
            args.launch_timeout_ms,
            args.navigation_timeout_ms,
        )
    except Exception as exc:
        report = {
            "passed": False,
            "html": args.html.as_posix(),
            "sourcePackage": args.source_package.as_posix() if args.source_package else None,
            "videoId": config["videoId"],
            "duration": config["duration"],
            "width": config["width"],
            "height": config["height"],
            "samplesRequested": args.samples,
            "sampleTimes": times,
            "findings": [
                {
                    "code": "rendered-frame-browser-failed",
                    "message": str(exc),
                }
            ],
            "browserFailed": True,
        }
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1
    viewport_area = float(config["width"]) * float(config["height"])
    forbidden_text_fragments = [
        str(config.get("title") or ""),
        str(config.get("checkedDate") or ""),
    ]
    masonry_layout = config.get("masonryLayout")
    masonry_layout = masonry_layout if isinstance(masonry_layout, dict) else {}
    masonry_required = masonry_layout.get("required") is True
    analyzed = [
        analyze_sample(
            frame,
            args.grid,
            args.min_untagged_inset_area_ratio,
            args.min_untagged_inset_size_px,
            args.min_padded_module_child_count,
            args.min_padded_module_area_ratio,
            args.min_padded_module_offset_px,
            args.min_gray_level_area_ratio,
            viewport_area,
            forbidden_text_fragments,
        )
        for frame in frames
    ]
    total_edges = sum(int(item.get("edgeCount") or 0) for item in analyzed)
    total_offgrid = sum(int(item.get("offgridEdgeCount") or 0) for item in analyzed)
    total_zero_padding_checks = sum(int(item.get("zeroPaddingGeometryCheckCount") or 0) for item in analyzed)
    total_zero_padding_violations = sum(int(item.get("zeroPaddingGeometryViolationCount") or 0) for item in analyzed)
    total_untagged_inset_checks = sum(int(item.get("untaggedInsetRectCheckCount") or 0) for item in analyzed)
    total_untagged_inset_violations = sum(int(item.get("untaggedInsetRectViolationCount") or 0) for item in analyzed)
    total_padded_module_checks = sum(int(item.get("paddedModuleInteriorCheckCount") or 0) for item in analyzed)
    total_padded_module_violations = sum(int(item.get("paddedModuleInteriorViolationCount") or 0) for item in analyzed)
    max_internal_padding = max((float(item.get("maxRenderedInternalPaddingPx") or 0.0) for item in analyzed), default=0.0)
    max_zone_elements = max((int(item.get("zoneElementCount") or 0) for item in analyzed), default=0)
    max_zone_ids = max((int(item.get("zoneIdCount") or 0) for item in analyzed), default=0)
    max_active_zones = max((int(item.get("activeZoneCount") or 0) for item in analyzed), default=0)
    zone_ids = sorted(
        {
            str(zone_id)
            for item in analyzed
            for zone_id in (item.get("zoneIds") if isinstance(item.get("zoneIds"), list) else [])
        }
    )
    source_anchors = sorted(
        {
            str(anchor)
            for item in analyzed
            for anchor in (item.get("sourceAnchors") if isinstance(item.get("sourceAnchors"), list) else [])
        }
    )
    semantic_bindings = sorted(
        {
            str(binding)
            for item in analyzed
            for binding in (item.get("semanticBindings") if isinstance(item.get("semanticBindings"), list) else [])
        }
    )
    max_gray_count = max((int(item.get("grayLevelCount") or 0) for item in analyzed), default=0)
    max_gray_spread = max((float(item.get("grayLuminanceSpread") or 0.0) for item in analyzed), default=0.0)
    active_gray_samples = [item for item in analyzed if int(item.get("rectCount") or 0) > 0]
    gray_counts = [int(item.get("grayLevelCount") or 0) for item in active_gray_samples]
    gray_spreads = [float(item.get("grayLuminanceSpread") or 0.0) for item in active_gray_samples]
    median_gray_count = float(statistics.median(gray_counts)) if gray_counts else 0.0
    median_gray_spread = float(statistics.median(gray_spreads)) if gray_spreads else 0.0
    gray_sample_pass_count = sum(
        1
        for item in active_gray_samples
        if int(item.get("grayLevelCount") or 0) >= args.min_gray_levels
        and float(item.get("grayLuminanceSpread") or 0.0) >= args.min_gray_luminance_spread
    )
    gray_sample_pass_ratio = (gray_sample_pass_count / len(active_gray_samples)) if active_gray_samples else 0.0
    min_shared_edge_ratio = min((float(item.get("sharedEdgeRatio") or 0.0) for item in analyzed if item.get("edgeCount")), default=0.0)
    final = analyzed[-1] if analyzed else {}
    text_area_ratios = [float(item.get("textBBoxAreaRatio") or 0.0) for item in analyzed]
    largest_text_ratios = [float(item.get("largestTextBoxAreaRatio") or 0.0) for item in analyzed]
    mark_to_text_ratios = [float(item.get("markToTextRatio") or 0.0) for item in analyzed]
    median_text_area_ratio = float(statistics.median(text_area_ratios)) if text_area_ratios else 0.0
    max_text_area_ratio = max(text_area_ratios, default=0.0)
    max_largest_text_box_area_ratio = max(largest_text_ratios, default=0.0)
    median_mark_to_text_ratio = float(statistics.median(mark_to_text_ratios)) if mark_to_text_ratios else 0.0
    min_mark_to_text_ratio = min(mark_to_text_ratios, default=0.0)
    max_text_element_count = max((int(item.get("textElementCount") or 0) for item in analyzed), default=0)
    max_text_character_count = max((int(item.get("textCharacterCount") or 0) for item in analyzed), default=0)
    title_band_text_count = sum(int(item.get("titleBandTextCount") or 0) for item in analyzed)
    ellipsized_text_count = sum(int(item.get("ellipsizedTextCount") or 0) for item in analyzed)
    masonry_module_counts = [int(item.get("masonryModuleCount") or 0) for item in analyzed]
    max_masonry_modules = max(masonry_module_counts, default=0)
    min_masonry_modules_seen = min(masonry_module_counts, default=0)
    masonry_module_count_range = max_masonry_modules - min_masonry_modules_seen
    masonry_module_count_distinct = len(set(masonry_module_counts))
    masonry_module_count_nondecreasing = all(
        later >= earlier for earlier, later in zip(masonry_module_counts, masonry_module_counts[1:])
    )
    max_masonry_size_count = max((int(item.get("masonrySizeCount") or 0) for item in analyzed), default=0)
    max_masonry_area_ratio = max((float(item.get("masonryAreaRatio") or 0.0) for item in analyzed), default=0.0)
    red_area_ratios = [float(item.get("redRectAreaRatio") or 0.0) for item in analyzed]
    max_red_rect_area_ratio = max(red_area_ratios, default=0.0)
    median_red_rect_area_ratio = float(statistics.median(red_area_ratios)) if red_area_ratios else 0.0
    semantic_glyph_counts = [int(item.get("semanticGlyphCount") or 0) for item in analyzed]
    max_semantic_glyph_count = max(semantic_glyph_counts, default=0)
    min_semantic_glyph_count = min(semantic_glyph_counts, default=0)
    semantic_glyph_count_distinct = len(set(semantic_glyph_counts))
    findings = build_findings(args, analyzed, masonry_required=masonry_required)
    report = {
        "passed": not findings,
        "html": args.html.as_posix(),
        "sourcePackage": args.source_package.as_posix() if args.source_package else None,
        "videoId": config["videoId"],
        "duration": config["duration"],
        "width": config["width"],
        "height": config["height"],
        "samplesRequested": args.samples,
        "sampleTimes": times,
        "grid": args.grid,
        "browserNotes": browser_notes,
        "rectEdgeCount": total_edges,
        "offgridEdgeCount": total_offgrid,
        "offgridRatio": (total_offgrid / total_edges) if total_edges else 0.0,
        "minSharedEdgeRatio": min_shared_edge_ratio,
        "roundedRectCount": sum(int(item.get("roundedRectCount") or 0) for item in analyzed),
        "roundedLineSignalCount": sum(int(item.get("roundedLineSignalCount") or 0) for item in analyzed),
        "zeroPaddingGeometryCheckCount": total_zero_padding_checks,
        "zeroPaddingGeometryViolationCount": total_zero_padding_violations,
        "untaggedInsetRectCheckCount": total_untagged_inset_checks,
        "untaggedInsetRectViolationCount": total_untagged_inset_violations,
        "paddedModuleInteriorCheckCount": total_padded_module_checks,
        "paddedModuleInteriorViolationCount": total_padded_module_violations,
        "maxUntaggedInsetRects": args.max_untagged_inset_rects,
        "minUntaggedInsetAreaRatio": args.min_untagged_inset_area_ratio,
        "minUntaggedInsetSizePx": args.min_untagged_inset_size_px,
        "maxRenderedInternalPaddingPx": max_internal_padding,
        "maxAllowedRenderedInternalPaddingPx": args.max_rendered_internal_padding_px,
        "maxZoneElementCount": max_zone_elements,
        "maxZoneIdCount": max_zone_ids,
        "maxActiveZoneCount": max_active_zones,
        "zoneIds": zone_ids,
        "sourceAnchors": source_anchors,
        "sourceAnchorCount": len(source_anchors),
        "semanticBindings": semantic_bindings,
        "semanticBindingCount": len(semantic_bindings),
        "maxSemanticGlyphCount": max_semantic_glyph_count,
        "minSemanticGlyphCount": min_semantic_glyph_count,
        "semanticGlyphCountDistinct": semantic_glyph_count_distinct,
        "semanticGlyphCounts": semantic_glyph_counts,
        "minZoneElements": args.min_zone_elements,
        "masonryRequired": masonry_required,
        "maxMasonryModuleCount": max_masonry_modules,
        "minMasonryModuleCount": min_masonry_modules_seen,
        "masonryModuleCountRange": masonry_module_count_range,
        "masonryModuleCountDistinct": masonry_module_count_distinct,
        "masonryModuleCountNondecreasing": masonry_module_count_nondecreasing,
        "masonryModuleCounts": masonry_module_counts,
        "maxMasonrySizeCount": max_masonry_size_count,
        "maxMasonryAreaRatio": max_masonry_area_ratio,
        "maxRedRectAreaRatio": max_red_rect_area_ratio,
        "medianRedRectAreaRatio": median_red_rect_area_ratio,
        "maxAllowedRedRectAreaRatio": args.max_red_rect_area_ratio,
        "minGrayLevelAreaRatio": args.min_gray_level_area_ratio,
        "maxGrayLevelCount": max_gray_count,
        "maxGrayLuminanceSpread": max_gray_spread,
        "medianGrayLevelCount": median_gray_count,
        "medianGrayLuminanceSpread": median_gray_spread,
        "activeGraySampleCount": len(active_gray_samples),
        "passingGraySampleCount": gray_sample_pass_count,
        "graySamplePassRatio": gray_sample_pass_ratio,
        "minGraySamplePassRatio": args.min_gray_sample_pass_ratio,
        "finalGrayLevelCount": int(final.get("grayLevelCount") or 0),
        "finalGrayLuminanceSpread": float(final.get("grayLuminanceSpread") or 0.0),
        "medianTextAreaRatio": median_text_area_ratio,
        "maxTextAreaRatio": max_text_area_ratio,
        "maxLargestTextBoxAreaRatio": max_largest_text_box_area_ratio,
        "medianMarkToTextRatio": median_mark_to_text_ratio,
        "minMarkToTextRatio": min_mark_to_text_ratio,
        "maxTextElementCount": max_text_element_count,
        "maxTextCharacterCount": max_text_character_count,
        "titleBandTextCount": title_band_text_count,
        "ellipsizedTextCount": ellipsized_text_count,
        "maxMedianTextAreaRatio": args.max_median_text_area_ratio,
        "maxLargestTextBoxAreaRatioAllowed": args.max_largest_text_box_area_ratio,
        "minMedianMarkToTextRatio": args.min_median_mark_to_text_ratio,
        "maxTitleBandTextCount": args.max_title_band_text_count,
        "maxEllipsizedTextCount": args.max_ellipsized_text_count,
        "samples": analyzed,
        "findings": findings,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
