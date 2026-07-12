#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.45.0"]
# ///
"""Preflight the demo's semantic renderer before a full 70-second encode.

This project-specific gate checks that each manifest-bound SVG exposes a
recognizable input/process/output contract, that the composition plan promotes
the SVG to a scene-primary focal object, and that the browser renderer exposes
the expected scene, asset, composition, and state IDs at every beat midpoint.
It complements, rather than replaces, the manual three-second silent test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any


SCENE_TIMES = {
    "s01": 2.5,
    "s02": 9.0,
    "s03": 17.5,
    "s04": 26.5,
    "s05": 36.0,
    "s06": 46.0,
    "s07": 56.0,
    "s08": 65.5,
}
REQUIRED_SVG_GROUPS = {"input", "process", "output", "active-state"}
REQUIRED_STATE_FIELDS = {
    "activeBeat",
    "sceneId",
    "activeSceneId",
    "activeCompositionId",
    "activeAssetIds",
    "sourceProofAssetIds",
    "visualPattern",
    "visibleMechanismCount",
    "hookVisible",
    "sourceProofVisible",
    "transitionVisible",
    "warningVisible",
    "outputVisible",
}
FORBIDDEN_RENDERER_TERMS = {
    "awsome_scaffold_wireframe": "scaffold marker",
    "proof inset": "detached proof-inset language",
    "megacanvas": "rejected abstract megacanvas implementation",
    "systems-flow": "generic systems-flow renderer branch",
}


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check semantic asset and browser-renderer contracts.")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--html", type=Path, default=Path("src/index.html"))
    parser.add_argument("--asset-manifest", type=Path, default=Path("source/asset-manifest.json"))
    parser.add_argument("--composition-plan", type=Path, default=Path("source/composition-plan.json"))
    parser.add_argument("--min-focal-area", type=float, default=0.45)
    parser.add_argument("--output", type=Path, default=Path("artifacts/reviews/semantic-renderer-preflight.json"))
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def resolve(project_root: Path, raw: Path, *, must_exist: bool = True) -> Path:
    root = project_root.resolve()
    path = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes project root: {raw}") from exc
    if must_exist and not path.is_file():
        raise FileNotFoundError(path)
    return path


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def inspect_svg(path: Path, asset_id: str, declared_sha: str) -> dict[str, Any]:
    failures: list[str] = []
    actual_sha = sha256_path(path)
    if actual_sha != declared_sha:
        failures.append("file SHA-256 does not match asset-manifest.json")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {"assetId": asset_id, "path": str(path), "ok": False, "failures": [f"invalid SVG XML: {exc}"]}
    if local_name(root.tag) != "svg":
        failures.append("root element is not <svg>")
    if root.get("id") != asset_id:
        failures.append(f"root id must equal {asset_id!r}")
    if root.get("data-asset-id") != asset_id:
        failures.append(f"root data-asset-id must equal {asset_id!r}")
    ids = {value for node in root.iter() if (value := node.get("id"))}
    missing_groups = sorted(REQUIRED_SVG_GROUPS - ids)
    if missing_groups:
        failures.append("missing semantic group IDs: " + ", ".join(missing_groups))
    title_nodes = [node for node in root.iter() if local_name(node.tag) == "title"]
    desc_nodes = [node for node in root.iter() if local_name(node.tag) == "desc"]
    visible_text = [
        " ".join("".join(node.itertext()).split())
        for node in root.iter()
        if local_name(node.tag) == "text" and " ".join("".join(node.itertext()).split())
    ]
    if not title_nodes or not desc_nodes:
        failures.append("SVG needs non-empty title and desc accessibility nodes")
    if len(visible_text) < 4:
        failures.append(f"SVG needs at least four functional visible labels; found {len(visible_text)}")
    return {
        "assetId": asset_id,
        "path": str(path),
        "ok": not failures,
        "sha256": actual_sha,
        "semanticGroupIds": sorted(REQUIRED_SVG_GROUPS & ids),
        "visibleTextCount": len(visible_text),
        "visibleTextSample": visible_text[:8],
        "failures": failures,
    }


def inspect_compositions(plan: dict[str, Any], min_focal_area: float) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    failures: list[str] = []
    scenes = plan.get("scenes")
    if not isinstance(scenes, list):
        return reports, ["composition plan scenes is not a list"]
    by_id = {str(scene.get("id")): scene for scene in scenes if isinstance(scene, dict)}
    for scene_id in SCENE_TIMES:
        scene = by_id.get(scene_id)
        if scene is None:
            failures.append(f"composition plan is missing {scene_id}")
            continue
        object_bounds = scene.get("objectBounds")
        bounds = {
            str(item.get("id")): item
            for item in object_bounds
            if isinstance(object_bounds, list) and isinstance(item, dict) and item.get("id")
        } if isinstance(object_bounds, list) else {}
        focal = bounds.get(f"{scene_id}-focal")
        support = bounds.get(f"{scene_id}-support")
        focal_area = None
        scene_failures: list[str] = []
        if not isinstance(focal, dict):
            scene_failures.append("missing focal object bounds")
        else:
            width, height = focal.get("width"), focal.get("height")
            if isinstance(width, (int, float)) and isinstance(height, (int, float)):
                focal_area = float(width) * float(height)
                if focal_area < min_focal_area:
                    scene_failures.append(
                        f"focal area {focal_area:.3f} is below semantic minimum {min_focal_area:.3f}"
                    )
            else:
                scene_failures.append("focal width/height is not numeric")
        if not isinstance(support, dict):
            scene_failures.append("missing support object bounds")
        reports.append({"sceneId": scene_id, "focalArea": focal_area, "ok": not scene_failures, "failures": scene_failures})
        failures.extend(f"{scene_id}: {finding}" for finding in scene_failures)
    return reports, failures


def inspect_browser(html: Path, min_focal_area: float) -> tuple[list[dict[str, Any]], list[str]]:
    from playwright.sync_api import sync_playwright

    samples: list[dict[str, Any]] = []
    failures: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, timeout=15_000)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(html.resolve().as_uri(), wait_until="load")
        for expected_beat, (scene_id, timestamp) in enumerate(SCENE_TIMES.items(), start=1):
            sample = page.evaluate(
                """async ([seconds, sceneId]) => {
                  const state = await Promise.resolve(
                    window.renderConceptFrame(undefined, seconds, { duration: 70 })
                  );
                  const pendingImages = [...document.querySelectorAll('img[data-asset-id]')];
                  await Promise.all(pendingImages.map((image) => {
                    if (image.complete && image.naturalWidth > 0 && image.naturalHeight > 0) {
                      return Promise.resolve();
                    }
                    return new Promise((resolve) => {
                      let settled = false;
                      const finish = () => {
                        if (settled) return;
                        settled = true;
                        resolve();
                      };
                      image.addEventListener('load', finish, { once: true });
                      image.addEventListener('error', finish, { once: true });
                      setTimeout(finish, 1500);
                    });
                  }));
                  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                  const stage = document.querySelector('#stage');
                  const stageBounds = stage.getBoundingClientRect();
                  const visible = (element) => {
                    const style = getComputedStyle(element);
                    const bounds = element.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' &&
                      Number(style.opacity || 1) > 0.01 && bounds.width > 1 && bounds.height > 1;
                  };
                  const assets = [...document.querySelectorAll('[data-asset-id]')].filter(visible);
                  const compositions = [...document.querySelectorAll('[data-composition-id]')]
                    .filter(visible).map((element) => element.dataset.compositionId).filter(Boolean);
                  const objects = [...document.querySelectorAll('[data-object-id]')].filter(visible).map((element) => {
                    const bounds = element.getBoundingClientRect();
                    return {
                      id: element.dataset.objectId,
                      role: element.dataset.role || null,
                      x: (bounds.left - stageBounds.left) / stageBounds.width,
                      y: (bounds.top - stageBounds.top) / stageBounds.height,
                      width: bounds.width / stageBounds.width,
                      height: bounds.height / stageBounds.height,
                      clipped: bounds.left < stageBounds.left - 1 || bounds.top < stageBounds.top - 1 ||
                        bounds.right > stageBounds.right + 1 || bounds.bottom > stageBounds.bottom + 1
                    };
                  });
                  return {
                    requestedSceneId: sceneId,
                    state,
                    visibleTextLength: document.body.innerText.trim().length,
                    assetIds: assets.map((element) => element.dataset.assetId),
                    assetHealthy: assets.every((element) => element.tagName.toLowerCase() === 'img' &&
                      element.complete && element.naturalWidth > 0 && element.naturalHeight > 0),
                    compositionIds: [...new Set(compositions)],
                    objects
                  };
                }""",
                [timestamp, scene_id],
            )
            state = sample.get("state") if isinstance(sample, dict) else None
            state = state if isinstance(state, dict) else {}
            sample_failures: list[str] = []
            missing_state = sorted(REQUIRED_STATE_FIELDS - set(state))
            if missing_state:
                sample_failures.append("missing renderer state fields: " + ", ".join(missing_state))
            if state.get("sceneId") != scene_id or state.get("activeSceneId") != scene_id:
                sample_failures.append(f"renderer did not activate {scene_id}")
            if state.get("activeBeat") != expected_beat:
                sample_failures.append(f"activeBeat is not {expected_beat}")
            active_assets = state.get("activeAssetIds")
            visible_assets = sample.get("assetIds") if isinstance(sample, dict) else []
            if not isinstance(active_assets, list) or active_assets != visible_assets or len(visible_assets) != 1:
                sample_failures.append("activeAssetIds must exactly match one visible manifest-bound image")
            if sample.get("assetHealthy") is not True:
                sample_failures.append("visible asset image is not decoded")
            if scene_id not in sample.get("compositionIds", []):
                sample_failures.append(f"visible composition marker {scene_id} is missing")
            if int(sample.get("visibleTextLength") or 0) < 20:
                sample_failures.append("renderer-native functional text is too thin")
            objects = sample.get("objects") if isinstance(sample, dict) else []
            focal = next((item for item in objects if item.get("id") == f"{scene_id}-focal"), None)
            support = next((item for item in objects if item.get("id") == f"{scene_id}-support"), None)
            focal_area = None
            if focal is None:
                sample_failures.append("visible focal object is missing")
            else:
                focal_area = float(focal.get("width") or 0) * float(focal.get("height") or 0)
                if focal_area < min_focal_area:
                    sample_failures.append(
                        f"visible focal area {focal_area:.3f} is below semantic minimum {min_focal_area:.3f}"
                    )
                if focal.get("clipped") is True:
                    sample_failures.append("visible focal object is clipped")
            if support is None:
                sample_failures.append("visible support object is missing")
            elif support.get("clipped") is True:
                sample_failures.append("visible support object is clipped")
            samples.append(
                {
                    "sceneId": scene_id,
                    "time": timestamp,
                    "focalArea": focal_area,
                    "visibleTextLength": sample.get("visibleTextLength"),
                    "state": state,
                    "ok": not sample_failures,
                    "failures": sample_failures,
                }
            )
            failures.extend(f"{scene_id}: {finding}" for finding in sample_failures)
        browser.close()
    return samples, failures


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    html = resolve(project_root, args.html)
    manifest_path = resolve(project_root, args.asset_manifest)
    composition_path = resolve(project_root, args.composition_plan)
    output = resolve(project_root, args.output, must_exist=False)
    manifest = read_json(manifest_path)
    composition = read_json(composition_path)
    failures: list[str] = []

    html_text = html.read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    for term, label in FORBIDDEN_RENDERER_TERMS.items():
        if term in lowered_html:
            failures.append(f"renderer contains {label}: {term}")
    if "window.renderconceptframe" not in lowered_html:
        failures.append("renderer does not expose window.renderConceptFrame")

    asset_reports: list[dict[str, Any]] = []
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        failures.append("asset manifest assets is not a list")
        assets = []
    seen_asset_ids: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict):
            failures.append("asset manifest contains a non-object asset")
            continue
        asset_id = str(asset.get("id", "")).strip()
        output_path = str(asset.get("output", "")).strip()
        declared_sha = str(asset.get("sha256", "")).strip()
        if not re.fullmatch(r"a\d{2}-[a-z0-9-]+", asset_id):
            failures.append(f"invalid semantic asset ID: {asset_id!r}")
            continue
        seen_asset_ids.add(asset_id)
        report = inspect_svg(resolve(project_root, Path(output_path)), asset_id, declared_sha)
        asset_reports.append(report)
        failures.extend(f"{asset_id}: {finding}" for finding in report.get("failures", []))
    if len(seen_asset_ids) != 8:
        failures.append(f"expected 8 semantic assets, found {len(seen_asset_ids)}")

    composition_reports, composition_failures = inspect_compositions(composition, args.min_focal_area)
    failures.extend(composition_failures)
    browser_samples: list[dict[str, Any]] = []
    if not args.skip_browser:
        browser_samples, browser_failures = inspect_browser(html, args.min_focal_area)
        failures.extend(browser_failures)

    result = {
        "ok": not failures,
        "projectRoot": str(project_root),
        "inputs": {
            "html": str(html),
            "htmlSha256": sha256_path(html),
            "assetManifest": str(manifest_path),
            "assetManifestSha256": sha256_path(manifest_path),
            "compositionPlan": str(composition_path),
            "compositionPlanSha256": sha256_path(composition_path),
        },
        "minimumFocalArea": args.min_focal_area,
        "assets": asset_reports,
        "compositions": composition_reports,
        "browserSamples": browser_samples,
        "manualReviewRequired": [
            "Run the three-second silent test for recognizable object, action, and result in every scene.",
            "Inspect overlays and transition objects at full resolution; geometry checks cannot prove semantic clearance.",
            "Review the final encoded video muted and at full speed before approval.",
        ],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Semantic renderer preflight {'passed' if result['ok'] else 'failed'}: {output}")
        for finding in failures:
            print(f"- {finding}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
