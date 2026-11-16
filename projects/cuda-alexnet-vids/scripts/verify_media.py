#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3", "Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Verify circular assets, graph interaction and actual exported portrait pixels."""
import argparse
import json
import os
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--video", type=Path); args = parser.parse_args()
    media = ROOT / "artifacts/media"
    manifest = json.loads((media / "manifest.json").read_text(encoding="utf-8"))
    checks = []
    for asset in manifest["assets"]:
        with Image.open(media / asset["png"]) as image:
            rgba = image.convert("RGBA")
            checks.append({"id": asset["id"], "size": list(image.size), "transparentCorners": all(rgba.getpixel(xy)[3] == 0 for xy in [(0, 0), (511, 0), (0, 511), (511, 511)]), "vectorArtwork": asset["vectorArtwork"]})
    with sync_playwright() as pw:
        paths = sorted((Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright").glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"), reverse=True)
        browser = pw.chromium.launch(executable_path=str(paths[0]) if paths else None, headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 760})
        errors = []; page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto((media / "graph-preview.html").as_uri()); page.wait_for_selector("g.node image")
        page.evaluate("async()=>await Promise.all([...document.querySelectorAll('g.node image')].map(e=>new Promise((ok,bad)=>{const i=new Image();i.onload=ok;i.onerror=bad;i.src=e.getAttribute('href')})))")
        before = page.locator('[data-asset-id="ian-buck"]').get_attribute("transform")
        box = page.locator('[data-asset-id="ian-buck"] image').bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); page.mouse.down(); page.mouse.move(box["x"] + box["width"] / 2 + 50, box["y"] + box["height"] / 2 + 20, steps=5); page.mouse.up()
        after = page.locator('[data-asset-id="ian-buck"]').get_attribute("transform")
        graph = {"nodes": page.locator("g.node").count(), "edges": page.locator("g.edge").count(), "dragChangesPosition": before != after, "browserErrors": errors}
        page.screenshot(path=str(ROOT / "artifacts/screenshots/media-graph.png")); browser.close()
    report = {"ok": all(c["transparentCorners"] and c["size"] == [512, 512] for c in checks) and next(c["vectorArtwork"] for c in checks if c["id"] == "nvidia") and graph["nodes"] == 7 and graph["edges"] == 4 and graph["dragChangesPosition"] and not errors, "assets": checks, "graph": graph}
    if args.video:
        observed = json.loads((ROOT / "artifacts/data/final-native-observed.json").read_text(encoding="utf-8"))["scenes"]
        starts = []; cursor = 0
        for scene in observed:
            starts.append(cursor); cursor += scene["sceneSeconds"]
        geometry = json.loads((ROOT / 'artifacts/reviews/render.json').read_text(encoding='utf-8'))['scenes']
        crops = [(i, m['id'], round(m['x']), round(m['y']), round(m['width'])) for i,s in enumerate(geometry) for m in s.get('media',[])]
        if len(crops)!=7:
            raise ValueError('The actual browser render must provide all seven media regions.')
        portraits = []
        for scene, identity, x, y, size in crops:
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(starts[scene] + 10), "-i", str(args.video.resolve()), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"])
            actual = np.frombuffer(raw, dtype=np.uint8).reshape(1080, 1920, 3)[y:y+size, x:x+size].astype(float)
            local = np.asarray(Image.open(ROOT / f"artifacts/screenshots/{scene+1:02d}-reading.png").convert("RGB"))[y:y+size, x:x+size].astype(float)
            yy, xx = np.ogrid[:size, :size]; mask = (xx - size/2)**2 + (yy - size/2)**2 < (size*.44)**2
            a = actual[mask].ravel(); b = local[mask].ravel()
            mae = float(np.abs(a-b).mean()); rho = float(np.corrcoef(a, b)[0, 1])
            portraits.append({"id": identity, "meanAbsoluteRgbError": mae, "pixelCorrelation": rho, "passed": mae < 12 and rho > .97})
        report["nativeMedia"] = portraits; report["ok"] = report["ok"] and all(p["passed"] for p in portraits)
    (ROOT / "artifacts/reviews/media.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report)); return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
