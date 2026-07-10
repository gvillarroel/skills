#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///
"""Validate an awsome-videos deterministic HTML renderer contract."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import extract_voiceover_cues  # noqa: E402


REQUIRED_FIELDS = [
    "activeBeat",
    "visualPattern",
    "visibleMechanismCount",
    "hookVisible",
    "sourceProofVisible",
    "transitionVisible",
    "warningVisible",
    "outputVisible",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a deterministic awsome-videos HTML renderer.")
    parser.add_argument("html", type=Path)
    parser.add_argument("--video-id")
    parser.add_argument("--duration", type=float, default=70.0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--brief", type=Path, help="Brief whose timed beat table should be sampled.")
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--composition-plan", type=Path)
    parser.add_argument(
        "--require-visual-ids",
        action="store_true",
        help="Require visible DOM asset/composition IDs to match renderer state and the visual contracts.",
    )
    parser.add_argument("--require-all-brief-beats", action="store_true")
    parser.add_argument("--brief-beat-sample-position", type=float, default=0.5)
    parser.add_argument("--times", nargs="*", type=float)
    parser.add_argument("--min-unique-beats", type=int, default=4)
    parser.add_argument("--min-screenshot-stddev", type=float, default=4.0)
    parser.add_argument("--min-screenshot-colors", type=int, default=32)
    parser.add_argument("--screenshot-dir", type=Path)
    parser.add_argument("--output", type=Path, help="Optional path to write the JSON report.")
    parser.add_argument("--install-browser", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def default_times(duration: float) -> list[float]:
    return [0.0, min(5.0, duration), duration * 0.28, duration * 0.55, duration * 0.78, max(0.0, duration - 0.25)]


def brief_beat_sample_times(brief: Path | None, duration: float, sample_position: float) -> dict[str, Any]:
    if brief is None:
        return {
            "briefBeatCount": 0,
            "expectedBriefBeats": [],
            "briefBeatRanges": [],
            "sampledBriefTimes": [],
            "failures": [],
        }
    if not brief.exists():
        return {
            "briefBeatCount": 0,
            "expectedBriefBeats": [],
            "briefBeatRanges": [],
            "sampledBriefTimes": [],
            "failures": [f"brief not found: {brief}"],
        }
    text = brief.read_text(encoding="utf-8")
    ranges = extract_voiceover_cues.extract_beat_ranges(text)
    failures: list[str] = []
    if not ranges:
        failures.append("brief has no timed beat ranges to sample")
    position = max(0.05, min(0.95, sample_position))
    times: list[float] = []
    for item in ranges:
        start = float(item["startSeconds"])
        end = float(item["endSeconds"])
        if end <= start:
            failures.append(f"brief beat {item.get('index')} has non-positive duration: {item.get('raw')}")
            continue
        at = start + ((end - start) * position)
        at = min(max(0.0, at), max(0.0, duration - 0.001), max(start, end - 0.001))
        times.append(round(at, 3))
    return {
        "briefBeatCount": len(ranges),
        "expectedBriefBeats": [item.get("index") for item in ranges],
        "briefBeatRanges": ranges,
        "sampledBriefTimes": times,
        "failures": failures,
    }


def beat_coverage(states: list[dict[str, Any]], expected_beats: list[Any]) -> dict[str, Any]:
    expected = [int(item) for item in expected_beats if isinstance(item, int)]
    sampled: set[int] = set()
    for sample in states:
        state = sample.get("state") or {}
        active = state.get("activeBeat") if isinstance(state, dict) else None
        try:
            sampled.add(int(active))
        except (TypeError, ValueError):
            continue
    missing = [beat for beat in expected if beat not in sampled]
    return {
        "briefBeatCoverageOk": bool(expected) and not missing,
        "expectedBriefBeats": expected,
        "sampledBriefBeats": sorted(sampled),
        "missingBriefBeats": missing,
    }


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_object(path: Path | None, label: str, failures: list[str]) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.is_file():
        failures.append(f"{label} missing: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"{label} root is not an object")
        return {}
    return data


def visual_expectations(
    asset_manifest: dict[str, Any],
    composition_plan: dict[str, Any],
    failures: list[str],
    asset_manifest_path: Path | None = None,
) -> dict[str, Any]:
    beat_assets: dict[int, set[str]] = {}
    all_assets: set[str] = set()
    asset_bindings: dict[str, dict[str, Any]] = {}
    project_root = asset_manifest_path.parent.parent.resolve() if asset_manifest_path is not None else None
    assets = asset_manifest.get("assets", [])
    if isinstance(assets, list):
        for item in assets:
            if not isinstance(item, dict):
                continue
            asset_id = str(item.get("id", "")).strip()
            if not asset_id:
                continue
            all_assets.add(asset_id)
            output = str(item.get("output", "")).strip()
            declared_sha256 = str(item.get("sha256", "")).strip()
            resolved_output: Path | None = None
            if project_root is not None:
                raw_path = Path(output)
                if not output or raw_path.is_absolute() or raw_path.drive:
                    failures.append(f"asset {asset_id} output must be project-root-relative")
                else:
                    candidate = (project_root / raw_path).resolve()
                    try:
                        candidate.relative_to(project_root)
                    except ValueError:
                        failures.append(f"asset {asset_id} output escapes the project root")
                    else:
                        resolved_output = candidate
                        if not candidate.is_file():
                            failures.append(f"asset {asset_id} output file is missing: {candidate}")
                        elif not re.fullmatch(r"[0-9a-f]{64}", declared_sha256):
                            failures.append(f"asset {asset_id} sha256 is missing or invalid")
                        elif sha256_file(candidate) != declared_sha256:
                            failures.append(f"asset {asset_id} output sha256 does not match the manifest")
            asset_bindings[asset_id] = {
                "output": Path(output).as_posix() if output else output,
                "sha256": declared_sha256,
                "resolvedOutput": str(resolved_output) if resolved_output is not None else None,
            }
            uses = item.get("uses", [])
            if not isinstance(uses, list):
                continue
            for use in uses:
                if not isinstance(use, dict):
                    continue
                match = re.fullmatch(r"b(\d+)", str(use.get("beatId", "")))
                if match:
                    beat_assets.setdefault(int(match.group(1)), set()).add(asset_id)

    beat_compositions: dict[int, str] = {}
    all_compositions: set[str] = set()
    composition_objects: dict[str, list[dict[str, Any]]] = {}
    scenes = composition_plan.get("scenes", [])
    if isinstance(scenes, list):
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            scene_id = str(scene.get("id", "")).strip()
            if not scene_id:
                continue
            all_compositions.add(scene_id)
            object_bounds = scene.get("objectBounds", [])
            if isinstance(object_bounds, list):
                composition_objects[scene_id] = [item for item in object_bounds if isinstance(item, dict)]
            beat_ids = scene.get("beatIds", [])
            if not isinstance(beat_ids, list):
                continue
            for beat_id in beat_ids:
                match = re.fullmatch(r"b(\d+)", str(beat_id))
                if match:
                    beat = int(match.group(1))
                    previous = beat_compositions.get(beat)
                    if previous and previous != scene_id:
                        failures.append(f"composition plan maps beat {beat} to multiple scenes")
                    beat_compositions[beat] = scene_id
    return {
        "beatAssets": beat_assets,
        "allAssetIds": all_assets,
        "assetBindings": asset_bindings,
        "beatCompositions": beat_compositions,
        "allCompositionIds": all_compositions,
        "compositionObjects": composition_objects,
    }


def validate_visible_asset_bindings(
    samples: list[dict[str, Any]],
    expected_bindings: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    failures: list[str] = []
    observed: set[str] = set()
    for sample in samples:
        at = sample.get("time")
        bindings = sample.get("visibleAssetBindings")
        if not isinstance(bindings, list):
            failures.append(f"state at {at} visibleAssetBindings is missing or not a list")
            continue
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                failures.append(f"state at {at} visibleAssetBindings[{index}] is not an object")
                continue
            asset_id = str(binding.get("id", "")).strip()
            expected = expected_bindings.get(asset_id)
            if expected is None:
                failures.append(f"state at {at} has no manifest binding for asset {asset_id or '<missing>'}")
                continue
            observed.add(asset_id)
            source = str(binding.get("source", "")).strip()
            normalized_source = Path(source).as_posix() if source else source
            if normalized_source != expected.get("output"):
                failures.append(
                    f"state at {at} asset {asset_id} data-asset-src does not match manifest output"
                )
            if binding.get("sha256") != expected.get("sha256"):
                failures.append(
                    f"state at {at} asset {asset_id} data-asset-sha256 does not match manifest sha256"
                )
            tag = str(binding.get("tag", "")).lower()
            direct_media_tags = {"img", "video", "object", "iframe"}
            resource_backed_tags = {"canvas", "svg"}
            if binding.get("bindingElementIsVisual") is not True:
                failures.append(
                    f"state at {at} asset {asset_id} data-asset-id must be carried by the visible media element"
                )
                continue
            resolved_output = expected.get("resolvedOutput")
            expected_uri = Path(str(resolved_output)).resolve().as_uri() if resolved_output else None
            raw_media_url = binding.get("mediaUrl")
            media_url = raw_media_url.strip() if isinstance(raw_media_url, str) else ""
            raw_resource_url = binding.get("resourceUrl")
            resource_url = raw_resource_url.strip() if isinstance(raw_resource_url, str) else ""
            if tag in direct_media_tags:
                if not media_url:
                    failures.append(f"state at {at} asset {asset_id} media element has no loaded URL")
                elif expected_uri and media_url != expected_uri:
                    failures.append(
                        f"state at {at} asset {asset_id} loaded URL does not match manifest output"
                    )
                if binding.get("mediaReady") is not True:
                    detail = str(binding.get("mediaError") or "media did not reach a decoded ready state")
                    failures.append(f"state at {at} asset {asset_id} is not a healthy loaded {tag}: {detail}")
            elif tag in resource_backed_tags:
                if not resource_url:
                    failures.append(
                        f"state at {at} asset {asset_id} inline {tag} needs data-asset-resource-src"
                    )
                elif expected_uri and resource_url != expected_uri:
                    failures.append(
                        f"state at {at} asset {asset_id} resource-loaded URL does not match manifest output"
                    )
                if binding.get("resourceLoaded") is not True:
                    failures.append(
                        f"state at {at} asset {asset_id} inline {tag} did not actually load its manifest resource"
                    )
            else:
                failures.append(
                    f"state at {at} asset {asset_id} uses unsupported binding element <{tag or 'unknown'}>"
                )
    missing = sorted(set(expected_bindings) - observed)
    if missing:
        failures.append("renderer never exposed manifest-bound asset metadata: " + ", ".join(missing))
    return {
        "ok": not failures,
        "failures": failures,
        "observedAssetIds": sorted(observed),
        "missingAssetIds": missing,
    }


def install_chromium() -> None:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def analyze_screenshot_bytes(
    data: bytes,
    *,
    min_stddev: float,
    min_colors: int,
) -> dict[str, Any]:
    failures: list[str] = []
    try:
        with Image.open(BytesIO(data)) as raw_image:
            image = raw_image.convert("RGB")
    except Exception as exc:
        return {"ok": False, "failures": [f"screenshot could not be opened: {exc}"]}

    width, height = image.size
    sample_width = min(320, width)
    sample_height = max(1, round(height * sample_width / max(width, 1)))
    sample = image.resize((sample_width, sample_height)).convert("RGB")
    luminance = sample.convert("L")
    stddev = float(ImageStat.Stat(luminance).stddev[0])
    if stddev < min_stddev:
        failures.append(f"screenshot luminance variation too low: {stddev:.2f} < {min_stddev:.2f}")
    colors = sample.getcolors(maxcolors=sample_width * sample_height + 1)
    color_count = len(colors) if colors is not None else sample_width * sample_height
    if color_count < min_colors:
        failures.append(f"screenshot color diversity too low: {color_count} < {min_colors}")

    return {
        "ok": not failures,
        "failures": failures,
        "width": width,
        "height": height,
        "sampleWidth": sample_width,
        "sampleHeight": sample_height,
        "luminanceStddev": stddev,
        "colorCount": color_count,
        "minLuminanceStddev": min_stddev,
        "minColorCount": min_colors,
    }


def sample_renderer(args: argparse.Namespace) -> dict[str, Any]:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    if not args.html.exists():
        return {"ok": False, "failures": [f"renderer not found: {args.html}"], "warnings": []}

    failures: list[str] = []
    warnings: list[str] = []
    asset_manifest_path = getattr(args, "asset_manifest", None)
    composition_plan_path = getattr(args, "composition_plan", None)
    require_visual_ids = bool(getattr(args, "require_visual_ids", False))
    if require_visual_ids and asset_manifest_path is None:
        failures.append("--require-visual-ids requires --asset-manifest")
    if require_visual_ids and composition_plan_path is None:
        failures.append("--require-visual-ids requires --composition-plan")
    asset_manifest = load_json_object(asset_manifest_path, "asset manifest", failures)
    composition_plan = load_json_object(composition_plan_path, "composition plan", failures)
    expectations = visual_expectations(
        asset_manifest,
        composition_plan,
        failures,
        asset_manifest_path if require_visual_ids else None,
    )
    brief_samples = brief_beat_sample_times(args.brief, args.duration, args.brief_beat_sample_position)
    failures.extend(str(failure) for failure in brief_samples.get("failures", []))
    times = list(args.times or default_times(args.duration))
    if args.brief:
        times.extend(float(item) for item in brief_samples.get("sampledBriefTimes", []))
    max_sample_time = max(0.0, args.duration - 0.001)
    times = sorted({round(max(0.0, min(max_sample_time, float(item))), 3) for item in times})
    states: list[dict[str, Any]] = []
    screenshots: list[str] = []
    screenshot_analyses: list[dict[str, Any]] = []
    browser = None
    try:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True, timeout=15_000)
            except PlaywrightError:
                if not args.install_browser:
                    raise
                install_chromium()
                browser = playwright.chromium.launch(headless=True, timeout=15_000)
            page = browser.new_page(viewport={"width": args.width, "height": args.height})
            page.add_init_script(
                """
                (() => {
                  const resourceLog = [];
                  const normalizeUrl = (value) => {
                    try {
                      if (value && typeof value === 'object' && 'url' in value) value = value.url;
                      return new URL(String(value || ''), document.baseURI).href;
                    } catch (_error) {
                      return null;
                    }
                  };
                  const record = (value, ok, kind, status = null) => {
                    const url = normalizeUrl(value);
                    if (url) resourceLog.push({ url, ok: Boolean(ok), kind, status });
                  };
                  Object.defineProperty(window, '__AWSOME_ASSET_RESOURCE_LOG', {
                    configurable: false,
                    enumerable: false,
                    writable: false,
                    value: resourceLog
                  });

                  const originalFetch = window.fetch;
                  if (typeof originalFetch === 'function') {
                    window.fetch = async function (...fetchArgs) {
                      try {
                        const response = await originalFetch.apply(this, fetchArgs);
                        record(response.url || fetchArgs[0], response.ok, 'fetch', response.status);
                        return response;
                      } catch (error) {
                        record(fetchArgs[0], false, 'fetch', null);
                        throw error;
                      }
                    };
                  }

                  const originalOpen = XMLHttpRequest.prototype.open;
                  const originalSend = XMLHttpRequest.prototype.send;
                  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
                    this.__awsomeResourceUrl = url;
                    return originalOpen.call(this, method, url, ...rest);
                  };
                  XMLHttpRequest.prototype.send = function (...sendArgs) {
                    this.addEventListener('loadend', () => {
                      const ok = (this.status >= 200 && this.status < 400) ||
                        (this.status === 0 && this.response != null);
                      record(this.responseURL || this.__awsomeResourceUrl, ok, 'xhr', this.status);
                    }, { once: true });
                    return originalSend.apply(this, sendArgs);
                  };

                  window.addEventListener('error', (event) => {
                    const target = event.target;
                    if (!target || !target.tagName) return;
                    const tag = target.tagName.toLowerCase();
                    if (!['img', 'video', 'object', 'iframe', 'script', 'link'].includes(tag)) return;
                    const value = target.currentSrc || target.src || target.data ||
                      target.getAttribute('src') || target.getAttribute('data') || target.getAttribute('href');
                    record(value, false, tag, null);
                  }, true);
                  window.addEventListener('load', (event) => {
                    const target = event.target;
                    if (!target || !target.tagName) return;
                    const tag = target.tagName.toLowerCase();
                    if (!['img', 'image', 'video', 'object', 'iframe', 'script', 'link'].includes(tag)) return;
                    const value = target.currentSrc || target.src || target.href || target.data ||
                      target.getAttribute('src') || target.getAttribute('href') || target.getAttribute('data');
                    record(value, true, tag, null);
                  }, true);
                })();
                window.AWSOME_VIDEO_TEST_MODE = true;
                """
            )
            page.goto(args.html.resolve().as_uri(), wait_until="load")
            has_function = page.evaluate("typeof window.renderConceptFrame === 'function'")
            if not has_function:
                failures.append("window.renderConceptFrame is not defined")
                return {"ok": False, "failures": failures, "warnings": warnings, "states": states}

            for index, at in enumerate(times):
                state = page.evaluate(
                    """async ([videoId, seconds, duration]) => {
                      const requestedVideoId = videoId || undefined;
                      const state = await Promise.resolve(
                        window.renderConceptFrame(requestedVideoId, seconds, { duration })
                      );
                      await new Promise((resolve) => setTimeout(resolve, 50));
                      const stage = document.querySelector("#stage");
                      const rect = stage ? stage.getBoundingClientRect() : null;
                      const isVisible = (element) => {
                        const style = getComputedStyle(element);
                        const bounds = element.getBoundingClientRect();
                        return style.display !== 'none' && style.visibility !== 'hidden' &&
                          Number(style.opacity || 1) > 0.01 && bounds.width > 1 && bounds.height > 1;
                      };
                      const visibleAssetElements = Array.from(document.querySelectorAll('[data-asset-id]')).filter(isVisible);
                      const visibleAssetIds = [...new Set(visibleAssetElements.map((element) => element.dataset.assetId).filter(Boolean))];
                      const successfulResourceUrls = new Set([
                        ...(window.__AWSOME_ASSET_RESOURCE_LOG || [])
                          .filter((item) => item && item.ok === true && item.url)
                          .map((item) => item.url)
                      ]);
                      const visibleAssetBindings = visibleAssetElements.map((element) => {
                        const tag = element.tagName.toLowerCase();
                        const directMediaTags = ['img', 'video', 'object', 'iframe'];
                        const resourceBackedTags = ['canvas', 'svg'];
                        const media = directMediaTags.includes(tag) ? element : null;
                        const rawMediaUrl = media
                          ? (media.currentSrc || media.src || media.data || media.getAttribute('src') || media.getAttribute('data'))
                          : null;
                        const rawResourceUrl = element.dataset.assetResourceSrc ||
                          element.dataset.assetLoadedSrc || null;
                        const mediaUrl = rawMediaUrl ? new URL(rawMediaUrl, document.baseURI).href : null;
                        const resourceUrl = rawResourceUrl ? new URL(rawResourceUrl, document.baseURI).href : null;
                        let mediaReady = null;
                        let mediaError = null;
                        if (tag === 'img') {
                          mediaReady = element.complete && element.naturalWidth > 0 && element.naturalHeight > 0;
                          mediaError = mediaReady ? null : 'image is incomplete or has no decoded dimensions';
                        } else if (tag === 'video') {
                          mediaReady = !element.error && element.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA &&
                            element.videoWidth > 0 && element.videoHeight > 0 &&
                            element.networkState !== HTMLMediaElement.NETWORK_NO_SOURCE;
                          mediaError = element.error
                            ? `video error code ${element.error.code}`
                            : (mediaReady ? null : `video is not decoded (readyState=${element.readyState}, networkState=${element.networkState})`);
                        } else if (tag === 'object') {
                          let objectDocument = null;
                          try { objectDocument = element.contentDocument || element.getSVGDocument?.() || null; } catch (_error) {}
                          mediaReady = Boolean(rawMediaUrl && objectDocument);
                          mediaError = mediaReady ? null : 'object resource did not expose a loaded document';
                        } else if (tag === 'iframe') {
                          let frameReady = false;
                          try {
                            frameReady = Boolean(
                              rawMediaUrl && element.contentDocument &&
                              element.contentDocument.readyState === 'complete' &&
                              element.contentWindow && element.contentWindow.location.href !== 'about:blank'
                            );
                          } catch (_error) {
                            frameReady = Boolean(rawMediaUrl);
                          }
                          mediaReady = frameReady;
                          mediaError = mediaReady ? null : 'iframe resource is not loaded';
                        }
                        const resourceLoaded = resourceUrl ? successfulResourceUrls.has(resourceUrl) : false;
                        return {
                          id: element.dataset.assetId || null,
                          source: element.dataset.assetSrc || null,
                          sha256: element.dataset.assetSha256 || null,
                          tag,
                          bindingElementIsVisual: directMediaTags.includes(tag) || resourceBackedTags.includes(tag),
                          mediaUrl,
                          mediaReady,
                          mediaError,
                          resourceUrl,
                          resourceLoaded,
                          resourceMode: directMediaTags.includes(tag)
                            ? 'direct-media'
                            : (resourceBackedTags.includes(tag) ? 'instrumented-resource' : 'none')
                        };
                      });
                      const brokenAssetIds = visibleAssetBindings
                        .filter((binding) => !binding.bindingElementIsVisual ||
                          (binding.resourceMode === 'direct-media' && binding.mediaReady !== true) ||
                          (binding.resourceMode === 'instrumented-resource' && binding.resourceLoaded !== true))
                        .map((binding) => binding.id)
                        .filter(Boolean);
                      const nonVisualAssetIds = visibleAssetElements
                        .filter((element) => !['img', 'video', 'canvas', 'svg', 'object', 'iframe'].includes(
                          element.tagName.toLowerCase()
                        ))
                        .map((element) => element.dataset.assetId)
                        .filter(Boolean);
                      const visibleCompositionIds = [...new Set(
                        Array.from(document.querySelectorAll('[data-composition-id]'))
                          .filter(isVisible)
                          .map((element) => element.dataset.compositionId)
                          .filter(Boolean)
                      )];
                      const visibleObjects = Array.from(document.querySelectorAll('[data-object-id]'))
                        .filter(isVisible)
                        .map((element) => {
                          const bounds = element.getBoundingClientRect();
                          return {
                            id: element.dataset.objectId,
                            role: element.dataset.role || null,
                            x: rect ? (bounds.left - rect.left) / rect.width : null,
                            y: rect ? (bounds.top - rect.top) / rect.height : null,
                            width: rect ? bounds.width / rect.width : null,
                            height: rect ? bounds.height / rect.height : null,
                            clipped: rect ? (
                              bounds.left < rect.left - 1 || bounds.top < rect.top - 1 ||
                              bounds.right > rect.right + 1 || bounds.bottom > rect.bottom + 1
                            ) : true
                          };
                        });
                      return {
                        state,
                        stage: rect ? { width: rect.width, height: rect.height } : null,
                        visibleTextLength: document.body.innerText.trim().length,
                        visibleNodeCount: document.querySelectorAll(".is-visible").length,
                        visibleAssetIds,
                        visibleAssetBindings,
                        visibleCompositionIds,
                        brokenAssetIds,
                        nonVisualAssetIds,
                        successfulResourceUrls: [...successfulResourceUrls],
                        resourceEvents: [...(window.__AWSOME_ASSET_RESOURCE_LOG || [])],
                        visibleObjects
                      };
                    }""",
                    [args.video_id, at, args.duration],
                )
                states.append({"time": at, **state})
                screenshot_path: str | None = None
                if args.screenshot_dir:
                    args.screenshot_dir.mkdir(parents=True, exist_ok=True)
                    shot = args.screenshot_dir / f"renderer-{index:02d}-{int(round(at * 1000)):06d}ms.png"
                    screenshot_path = str(shot)
                screenshot_data = page.screenshot(path=screenshot_path, full_page=False)
                analysis = analyze_screenshot_bytes(
                    screenshot_data,
                    min_stddev=args.min_screenshot_stddev,
                    min_colors=args.min_screenshot_colors,
                )
                analysis["time"] = at
                if screenshot_path:
                    analysis["path"] = screenshot_path
                    screenshots.append(screenshot_path)
                screenshot_analyses.append(analysis)
            if browser:
                browser.close()
    except Exception as exc:  # noqa: BLE001
        failures.append(f"renderer browser validation failed: {exc}")

    for sample in states:
        state = sample.get("state") or {}
        missing = [field for field in REQUIRED_FIELDS if field not in state]
        if missing:
            failures.append(f"state at {sample.get('time')} missing fields: {', '.join(missing)}")
        stage = sample.get("stage")
        if not stage:
            failures.append(f"state at {sample.get('time')} has no #stage element")
        elif stage.get("width", 0) < args.width * 0.85 or stage.get("height", 0) < args.height * 0.85:
            warnings.append(f"stage at {sample.get('time')} is smaller than expected viewport")
        if sample.get("visibleTextLength", 0) < 20:
            failures.append(f"state at {sample.get('time')} appears visually empty")
        if sample.get("visibleNodeCount", 0) < 2:
            warnings.append(f"state at {sample.get('time')} has few `.is-visible` mechanism nodes")
        if state.get("visibleMechanismCount", 0) < 1:
            failures.append(f"state at {sample.get('time')} reports no visible mechanism")

    for analysis in screenshot_analyses:
        for failure in analysis.get("failures", []):
            failures.append(f"screenshot at {analysis.get('time')} {failure}")

    observed_asset_ids: set[str] = set()
    observed_composition_ids: set[str] = set()
    observed_object_ids: dict[str, set[str]] = {}
    unknown_asset_ids: set[str] = set()
    unknown_composition_ids: set[str] = set()
    asset_binding_info: dict[str, Any] = {"ok": False, "failures": [], "observedAssetIds": [], "missingAssetIds": []}
    if require_visual_ids:
        expected_all_assets = set(expectations.get("allAssetIds", set()))
        expected_all_compositions = set(expectations.get("allCompositionIds", set()))
        beat_assets = expectations.get("beatAssets", {})
        beat_compositions = expectations.get("beatCompositions", {})
        composition_objects = expectations.get("compositionObjects", {})
        asset_binding_info = validate_visible_asset_bindings(
            states,
            expectations.get("assetBindings", {}),
        )
        failures.extend(asset_binding_info.get("failures", []))
        for sample in states:
            state = sample.get("state") or {}
            at = sample.get("time")
            visible_assets = {str(item) for item in sample.get("visibleAssetIds", []) if item}
            visible_compositions = {str(item) for item in sample.get("visibleCompositionIds", []) if item}
            claimed_assets_raw = state.get("activeAssetIds") if isinstance(state, dict) else None
            claimed_assets = (
                {str(item) for item in claimed_assets_raw if item}
                if isinstance(claimed_assets_raw, list)
                else set()
            )
            source_assets_raw = state.get("sourceProofAssetIds") if isinstance(state, dict) else None
            source_assets = (
                {str(item) for item in source_assets_raw if item}
                if isinstance(source_assets_raw, list)
                else set()
            )
            observed_asset_ids.update(visible_assets)
            observed_composition_ids.update(visible_compositions)
            unknown_asset_ids.update(visible_assets - expected_all_assets)
            unknown_composition_ids.update(visible_compositions - expected_all_compositions)
            if state.get("rendererMode") == "wireframe":
                failures.append(f"state at {at} is still the scaffold wireframe")
            if sample.get("brokenAssetIds"):
                failures.append(
                    f"state at {at} has unloaded visible assets: "
                    + ", ".join(str(item) for item in sample.get("brokenAssetIds", []))
                )
            if sample.get("nonVisualAssetIds"):
                failures.append(
                    f"state at {at} marks non-media placeholders as assets: "
                    + ", ".join(str(item) for item in sample.get("nonVisualAssetIds", []))
                )
            if not isinstance(claimed_assets_raw, list):
                failures.append(f"state at {at} activeAssetIds is missing or not a list")
            if claimed_assets - visible_assets:
                failures.append(
                    f"state at {at} claims assets not visibly marked in the DOM: "
                    + ", ".join(sorted(claimed_assets - visible_assets))
                )
            if visible_assets - claimed_assets:
                failures.append(
                    f"state at {at} has visible DOM assets omitted from activeAssetIds: "
                    + ", ".join(sorted(visible_assets - claimed_assets))
                )
            try:
                active_beat = int(state.get("activeBeat"))
            except (TypeError, ValueError):
                active_beat = None
            if active_beat is not None:
                expected_assets = set(beat_assets.get(active_beat, set()))
                if expected_assets and not expected_assets.intersection(visible_assets):
                    failures.append(
                        f"state at {at} beat {active_beat} shows none of its declared assets: "
                        + ", ".join(sorted(expected_assets))
                    )
                expected_composition = beat_compositions.get(active_beat)
                active_composition = state.get("activeCompositionId")
                if expected_composition and active_composition != expected_composition:
                    failures.append(
                        f"state at {at} beat {active_beat} composition mismatch: "
                        f"{active_composition!r} != {expected_composition!r}"
                    )
                if expected_composition and expected_composition not in visible_compositions:
                    failures.append(
                        f"state at {at} beat {active_beat} lacks visible data-composition-id={expected_composition}"
                    )
                if expected_composition:
                    declared_objects = {
                        str(item.get("id")): item
                        for item in composition_objects.get(expected_composition, [])
                        if isinstance(item, dict) and item.get("id")
                    }
                    visible_objects = [
                        item for item in sample.get("visibleObjects", []) if isinstance(item, dict) and item.get("id")
                    ]
                    observed_object_ids.setdefault(expected_composition, set()).update(
                        str(item.get("id")) for item in visible_objects
                    )
                    for visible_object in visible_objects:
                        object_id = str(visible_object.get("id"))
                        declared = declared_objects.get(object_id)
                        if declared is None:
                            failures.append(
                                f"state at {at} composition {expected_composition} exposes unknown object {object_id}"
                            )
                            continue
                        if visible_object.get("clipped") is True:
                            failures.append(f"state at {at} composition object {object_id} is clipped outside #stage")
                        if visible_object.get("role") == "focal":
                            area = float(visible_object.get("width") or 0) * float(visible_object.get("height") or 0)
                            if area < 0.05:
                                failures.append(
                                    f"state at {at} focal object {object_id} is too small: {area:.3f} < 0.050"
                                )
                        for field, tolerance in [("x", 0.15), ("y", 0.15), ("width", 0.20), ("height", 0.20)]:
                            expected_value = declared.get(field)
                            actual_value = visible_object.get(field)
                            if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                                if abs(float(expected_value) - float(actual_value)) > tolerance:
                                    failures.append(
                                        f"state at {at} object {object_id} {field} drifts from composition plan: "
                                        f"{float(actual_value):.3f} vs {float(expected_value):.3f}"
                                    )
            if state.get("sourceProofVisible"):
                if not source_assets:
                    failures.append(f"state at {at} reports sourceProofVisible without sourceProofAssetIds")
                elif not source_assets.issubset(visible_assets):
                    failures.append(
                        f"state at {at} sourceProofAssetIds are not all visibly loaded: "
                        + ", ".join(sorted(source_assets - visible_assets))
                    )

        missing_asset_ids = sorted(expected_all_assets - observed_asset_ids)
        missing_composition_ids = sorted(expected_all_compositions - observed_composition_ids)
        if missing_asset_ids:
            failures.append("renderer never visibly sampled declared assets: " + ", ".join(missing_asset_ids))
        if missing_composition_ids:
            failures.append(
                "renderer never visibly sampled declared compositions: " + ", ".join(missing_composition_ids)
            )
        if unknown_asset_ids:
            failures.append("renderer exposed unknown asset IDs: " + ", ".join(sorted(unknown_asset_ids)))
        if unknown_composition_ids:
            failures.append(
                "renderer exposed unknown composition IDs: " + ", ".join(sorted(unknown_composition_ids))
            )
        missing_object_ids: list[str] = []
        for composition_id, declared in composition_objects.items():
            declared_ids = {str(item.get("id")) for item in declared if isinstance(item, dict) and item.get("id")}
            for object_id in sorted(declared_ids - observed_object_ids.get(composition_id, set())):
                missing_object_ids.append(f"{composition_id}:{object_id}")
        if missing_object_ids:
            failures.append("renderer never sampled declared composition objects: " + ", ".join(missing_object_ids))
    else:
        expected_all_assets = set()
        expected_all_compositions = set()
        missing_asset_ids = []
        missing_composition_ids = []
        missing_object_ids = []

    unique_beats = sorted({sample.get("state", {}).get("activeBeat") for sample in states if sample.get("state")})
    if len(unique_beats) < args.min_unique_beats:
        failures.append(f"expected at least {args.min_unique_beats} unique active beats, found {len(unique_beats)}")
    coverage = beat_coverage(states, brief_samples.get("expectedBriefBeats", []))
    if args.require_all_brief_beats and coverage["missingBriefBeats"]:
        failures.append(
            "renderer missing activeBeat coverage for brief beats: "
            + ", ".join(str(item) for item in coverage["missingBriefBeats"])
        )
    if args.require_all_brief_beats and not coverage["expectedBriefBeats"]:
        failures.append("renderer beat coverage was required but no expected brief beats were found")
    if states:
        final_state = states[-1].get("state") or {}
        if not final_state.get("outputVisible"):
            failures.append("final sampled state did not report outputVisible")
        if not final_state.get("finalCallbackVisible"):
            failures.append("final sampled state did not report finalCallbackVisible")

    return {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "states": states,
        "uniqueBeats": unique_beats,
        "briefBeatCount": brief_samples.get("briefBeatCount", 0),
        "sampledBriefTimes": brief_samples.get("sampledBriefTimes", []),
        **coverage,
        "screenshots": screenshots,
        "screenshotAnalyses": screenshot_analyses,
        "visualContractRequired": require_visual_ids,
        "rendererSha256": sha256_file(args.html),
        "assetManifestSha256": sha256_file(asset_manifest_path),
        "compositionPlanSha256": sha256_file(composition_plan_path),
        "expectedAssetIds": sorted(expected_all_assets),
        "observedAssetIds": sorted(observed_asset_ids),
        "missingAssetIds": missing_asset_ids,
        "unknownAssetIds": sorted(unknown_asset_ids),
        "assetBindingCoverageOk": asset_binding_info.get("ok") is True,
        "assetBindingFailures": asset_binding_info.get("failures", []),
        "visualAssetCoverageOk": bool(expected_all_assets)
        and not missing_asset_ids
        and not unknown_asset_ids
        and asset_binding_info.get("ok") is True,
        "expectedCompositionIds": sorted(expected_all_compositions),
        "observedCompositionIds": sorted(observed_composition_ids),
        "missingCompositionIds": missing_composition_ids,
        "unknownCompositionIds": sorted(unknown_composition_ids),
        "compositionCoverageOk": bool(expected_all_compositions)
        and not missing_composition_ids
        and not unknown_composition_ids
        and not missing_object_ids,
        "missingCompositionObjectIds": missing_object_ids,
    }


def main() -> int:
    args = parse_args()
    result = sample_renderer(args)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos renderer: {len(result.get('states', []))} sampled states")
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    else:
        print("FAIL awsome-videos renderer")
        for failure in result["failures"]:
            print(f"- {failure}")
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
