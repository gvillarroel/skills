#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import random
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample renderConceptFrame state from a generated HTML video without encoding frames.")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expect-state", action="append", default=[], help="Expected top-level render state value in KEY=VALUE form.")
    parser.add_argument("--expect-state-final", action="append", default=[], help="Expected final sampled top-level render state value in KEY=VALUE form.")
    parser.add_argument("--expect-state-contains", action="append", default=[], help="Expected item inside a top-level list render state value in KEY=VALUE form.")
    parser.add_argument("--expect-state-transition", action="append", default=[], help="Expected first-to-final top-level render state transition in KEY=FROM->TO form.")
    parser.add_argument("--expect-state-monotonic", action="append", default=[], help="Expected numeric state monotonicity in KEY=nondecreasing|nonincreasing|increasing|decreasing form.")
    parser.add_argument("--min-distinct-state", action="append", default=[], help="Minimum distinct top-level render state values in KEY=COUNT form.")
    return parser.parse_args()


def free_port() -> int:
    for _ in range(100):
        port = random.randint(49152, 65535)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    raise RuntimeError("Could not find a free high localhost port")


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


def parse_key_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Expected KEY=VALUE, got {raw!r}")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"Expected non-empty key in {raw!r}")
    return key, value.strip()


def parse_transition(raw: str) -> tuple[str, str, str]:
    key, value = parse_key_value(raw)
    if "->" not in value:
        raise ValueError(f"Expected KEY=FROM->TO, got {raw!r}")
    start, end = value.split("->", 1)
    start = start.strip()
    end = end.strip()
    if not start or not end:
        raise ValueError(f"Expected non-empty transition values in {raw!r}")
    return key, start, end


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def summarize_states(states: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[Any]] = {}
    for sample in states:
        state = sample.get("state")
        if not isinstance(state, dict):
            continue
        for key, value in state.items():
            buckets.setdefault(key, []).append(value)

    summary: dict[str, dict[str, Any]] = {}
    for key, values in buckets.items():
        distinct = sorted({canonical(value) for value in values})
        entry: dict[str, Any] = {
            "count": len(values),
            "distinctCount": len(distinct),
            "distinctValues": distinct[:12],
        }
        numeric_values = [float(value) for value in values if isinstance(value, (int, float, bool))]
        if numeric_values:
            entry["min"] = min(numeric_values)
            entry["max"] = max(numeric_values)
        summary[key] = entry
    return summary


def expected_value_candidates(expected: str) -> set[str]:
    candidates = {expected}
    try:
        candidates.add(canonical(json.loads(expected)))
    except json.JSONDecodeError:
        candidates.add(canonical(expected))
    lowered = expected.lower()
    if lowered == "true":
        candidates.add(canonical(True))
    elif lowered == "false":
        candidates.add(canonical(False))
    elif lowered == "null":
        candidates.add(canonical(None))
    return candidates


def value_matches_expected(value: Any, expected: str) -> bool:
    candidates = expected_value_candidates(expected)
    if canonical(value) in candidates:
        return True
    if isinstance(value, str) and value == expected:
        return True
    return False


def state_values(states: list[dict[str, Any]], key: str) -> list[Any]:
    values: list[Any] = []
    for sample in states:
        state = sample.get("state")
        if isinstance(state, dict) and key in state:
            values.append(state[key])
    return values


def numeric_values(values: list[Any]) -> list[float] | None:
    converted: list[float] = []
    for value in values:
        if not isinstance(value, (int, float, bool)):
            return None
        converted.append(float(value))
    return converted


def is_monotonic(values: list[float], mode: str) -> bool:
    pairs = zip(values, values[1:])
    if mode in {"nondecreasing", "non-decreasing"}:
        return all(left <= right for left, right in pairs)
    if mode in {"nonincreasing", "non-increasing"}:
        return all(left >= right for left, right in pairs)
    if mode == "increasing":
        return all(left < right for left, right in pairs)
    if mode == "decreasing":
        return all(left > right for left, right in pairs)
    raise ValueError(f"Unsupported monotonic mode {mode!r}")


def build_findings(summary: dict[str, dict[str, Any]], states: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "severity": "error", "message": message})

    for raw in args.expect_state:
        key, expected = parse_key_value(raw)
        entry = summary.get(key)
        if entry is None:
            add("missing-state-key", f"Expected render state key {key!r}, but it was not returned.")
            continue
        values = set(str(value) for value in entry.get("distinctValues", []))
        if not expected_value_candidates(expected).intersection(values):
            add("unexpected-state-value", f"Expected render state {key}={expected!r}, got {sorted(values)}.")

    for raw in args.expect_state_contains:
        key, expected = parse_key_value(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected render state key {key!r}, but it was not returned.")
            continue
        matched = False
        for value in values:
            if isinstance(value, list) and any(value_matches_expected(item, expected) for item in value):
                matched = True
                break
            if isinstance(value, str) and expected in value:
                matched = True
                break
        if not matched:
            examples = [canonical(value) for value in values[:3]]
            add("missing-contained-state-value", f"Expected render state key {key!r} to contain {expected!r}, got {examples}.")

    for raw in args.expect_state_final:
        key, expected = parse_key_value(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected final render state key {key!r}, but it was not returned.")
            continue
        actual = values[-1]
        if not value_matches_expected(actual, expected):
            add("unexpected-final-state-value", f"Expected final render state {key}={expected!r}, got {canonical(actual)}.")

    for raw in args.expect_state_transition:
        key, start, end = parse_transition(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected transition render state key {key!r}, but it was not returned.")
            continue
        actual_start = values[0]
        actual_end = values[-1]
        if not value_matches_expected(actual_start, start):
            add("unexpected-initial-state-value", f"Expected initial render state {key}={start!r}, got {canonical(actual_start)}.")
        if not value_matches_expected(actual_end, end):
            add("unexpected-final-state-value", f"Expected final render state {key}={end!r}, got {canonical(actual_end)}.")

    for raw in args.expect_state_monotonic:
        key, mode = parse_key_value(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected monotonic render state key {key!r}, but it was not returned.")
            continue
        numbers = numeric_values(values)
        if numbers is None:
            add("non-numeric-state-value", f"Expected numeric render state key {key!r} for monotonic check, got {[canonical(value) for value in values[:6]]}.")
            continue
        if not is_monotonic(numbers, mode):
            add("state-not-monotonic", f"Expected render state key {key!r} to be {mode}, got {numbers[:12]}.")

    for raw in args.min_distinct_state:
        key, raw_count = parse_key_value(raw)
        try:
            required = int(raw_count)
        except ValueError as exc:
            raise ValueError(f"Expected integer count in {raw!r}") from exc
        entry = summary.get(key)
        if entry is None:
            add("missing-state-key", f"Expected render state key {key!r}, but it was not returned.")
            continue
        actual = int(entry.get("distinctCount", 0))
        if actual < required:
            add("state-not-changing", f"Expected at least {required} distinct values for state key {key!r}, got {actual}.")
    return findings


def sample_times(duration: float, samples: int) -> list[float]:
    if samples <= 0:
        raise ValueError("--samples must be positive")
    if samples == 1:
        return [0.0]
    tail = max(0.0, duration - min(0.25, duration / 20))
    return [round(tail * idx / (samples - 1), 3) for idx in range(samples)]


def goto_with_retry(page: Any, url: str, attempts: int = 4) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=10_000)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.25 * (attempt + 1))
    if last_error is not None:
        raise last_error


def write_manifest(args: argparse.Namespace, manifest: dict[str, Any]) -> None:
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def sample_with_node_stub(html: Path, times: list[float], video_id: str) -> list[dict[str, Any]]:
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        for candidate in (
            Path(r"C:\Program Files\nodejs\node.exe"),
            Path(r"C:\Program Files (x86)\nodejs\node.exe"),
            Path("/usr/bin/node"),
            Path("/usr/local/bin/node"),
        ):
            if candidate.exists():
                node = str(candidate)
                break
    if not node:
        raise RuntimeError("node executable was not found on PATH.")

    driver = r"""
import fs from "node:fs";

const htmlPath = process.argv[2];
const times = JSON.parse(process.argv[3]);
const videoId = process.argv[4];
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((match) => match[1]).join("\n");
if (!scripts.trim()) {
  throw new Error("No inline script tags found in HTML.");
}

function findById(node, id) {
  if (!node) return null;
  if (node.attributes?.id === id) return node;
  for (const child of node.children || []) {
    const found = findById(child, id);
    if (found) return found;
  }
  return null;
}

function makeNode(name = "node") {
  return {
    nodeName: name,
    children: [],
    attributes: {},
    dataset: {},
    style: {},
    classList: { add() {}, remove() {}, toggle() {} },
    setAttribute(key, value) {
      const stringValue = String(value);
      this.attributes[key] = stringValue;
      if (key === "id") this.id = stringValue;
      if (key.startsWith("data-")) {
        const datasetKey = key
          .slice(5)
          .replace(/-([a-z])/g, (_match, letter) => letter.toUpperCase());
        this.dataset[datasetKey] = stringValue;
      }
    },
    getAttribute(key) { return Object.prototype.hasOwnProperty.call(this.attributes, key) ? this.attributes[key] : null; },
    appendChild(child) { this.children.push(child); return child; },
    append(...children) { this.children.push(...children); },
    replaceChildren(...children) { this.children = [...children]; },
    querySelector(selector) {
      if (typeof selector === "string" && selector.startsWith("#")) {
        return findById(this, selector.slice(1));
      }
      return null;
    },
    remove() {},
    get textContent() { return this._textContent || ""; },
    set textContent(value) { this._textContent = String(value); },
  };
}

const stage = makeNode("svg");
const documentStub = {
  body: makeNode("body"),
  documentElement: makeNode("html"),
  fonts: { ready: Promise.resolve() },
  getElementById(id) { return id === "stage" ? stage : makeNode("div"); },
  querySelector() { return null; },
  createElement(name) { return makeNode(name); },
  createElementNS(_ns, name) { return makeNode(name); },
};

globalThis.window = { document: documentStub };
globalThis.document = documentStub;
Object.defineProperty(globalThis, "navigator", {
  value: { userAgent: "node-render-state" },
  configurable: true,
});
globalThis.performance = { now: () => Date.now() };
globalThis.requestAnimationFrame = () => 0;
globalThis.cancelAnimationFrame = () => {};

globalThis.eval(scripts);
if (typeof window.renderConceptFrame !== "function") {
  throw new Error("window.renderConceptFrame is not defined after evaluating HTML script.");
}

const states = times.map((seconds, index) => ({
  sample: index,
  seconds,
  state: window.renderConceptFrame(videoId, Number(seconds), { capture: true }),
}));
console.log(JSON.stringify(states));
process.exit(0);
"""
    with tempfile.TemporaryDirectory() as tmp:
        driver_path = Path(tmp) / "render_state_probe.mjs"
        driver_path.write_text(driver, encoding="utf-8")
        result = subprocess.run(
            [node, str(driver_path), str(html), json.dumps(times), video_id],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    if result.returncode != 0:
        tail = "\n".join(part for part in [result.stdout[-1200:], result.stderr[-1200:]] if part)
        raise RuntimeError(f"Node render-state probe exited {result.returncode}: {tail}")
    try:
        states = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Node render-state probe returned invalid JSON: {result.stdout[-1200:]}") from exc
    if not isinstance(states, list):
        raise RuntimeError("Node render-state probe did not return a JSON list.")
    return states


def sample_with_playwright(html: Path, times: list[float], video_id: str, width: int, height: int) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(f"Playwright import failed: {exc}") from exc

    states: list[dict[str, Any]] = []
    with serve_directory(html.parent) as base_url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(timeout=15_000)
            try:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.set_default_timeout(10_000)
                page.set_default_navigation_timeout(10_000)
                goto_with_retry(page, f"{base_url}/{html.name}")
                page.wait_for_function("() => typeof window.renderConceptFrame === 'function'", timeout=10_000)
                for idx, seconds in enumerate(times):
                    state = page.evaluate(
                        """async ({ videoId, seconds }) => {
                            return window.renderConceptFrame(videoId, seconds, { capture: true });
                        }""",
                        {"videoId": video_id, "seconds": seconds},
                    )
                    states.append({"sample": idx, "seconds": seconds, "state": state})
            finally:
                browser.close()
    return states


def main() -> int:
    args = parse_args()
    html = args.html.resolve()
    if not html.exists():
        print(f"HTML file not found: {html}", file=sys.stderr)
        return 2

    times = sample_times(args.duration, args.samples)
    states: list[dict[str, Any]] = []
    sampling_method = "node-stub"
    node_probe_error: str | None = None
    try:
        try:
            states = sample_with_node_stub(html, times, args.video_id)
        except Exception as node_exc:
            node_probe_error = str(node_exc)
            sampling_method = "playwright"
            try:
                states = sample_with_playwright(html, times, args.video_id, args.width, args.height)
            except Exception as browser_exc:
                raise RuntimeError(f"Node probe failed: {node_exc}; Playwright probe failed: {browser_exc}") from browser_exc
    except Exception as exc:
        summary = summarize_states(states)
        manifest = {
            "html": args.html.as_posix(),
            "videoId": args.video_id,
            "durationSeconds": args.duration,
            "samples": len(times),
            "sampleTimes": times,
            "samplingMethod": sampling_method,
            "nodeProbeError": node_probe_error,
            "stateSummary": summary,
            "findings": [{
                "code": "render-state-sampling-failed",
                "severity": "error",
                "message": str(exc),
            }],
            "passed": False,
            "statesSample": states[:3] + states[-3:] if len(states) > 6 else states,
        }
        write_manifest(args, manifest)
        return 1

    summary = summarize_states(states)
    findings = build_findings(summary, states, args)
    manifest = {
        "html": args.html.as_posix(),
        "videoId": args.video_id,
        "durationSeconds": args.duration,
        "samples": len(times),
        "sampleTimes": times,
        "samplingMethod": sampling_method,
        "nodeProbeError": node_probe_error,
        "stateSummary": summary,
        "findings": findings,
        "passed": not findings,
        "statesSample": states[:3] + states[-3:] if len(states) > 6 else states,
    }
    write_manifest(args, manifest)
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
