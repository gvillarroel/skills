#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52", "pillow>=10"]
# ///
"""Inspect actual borderless chrome, text contrast and decoded pulse motion."""
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts"
PROVIDERS = ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search", "destockd-video-search")
SCAN = r'''() => {
 const borders=[...document.querySelectorAll('article,.cell,.node,#solids .tile')].filter(node=>{const s=getComputedStyle(node);return ['Top','Right','Bottom','Left'].some(side=>parseFloat(s['border'+side+'Width'])>0&&s['border'+side+'Style']!=='none')}).map(node=>node.id||node.className);
 const contrast=[];
 const lum=c=>{const v=c.match(/[\d.]+/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2]};
 for(const node of document.querySelectorAll('.node,#solids .tile')){const s=getComputedStyle(node);const L=lum(s.backgroundColor),black=(L+.05)/.05,white=1.05/(L+.05),expected=black>=white?'rgb(0, 0, 0)':'rgb(255, 255, 255)';if(s.color!==expected)contrast.push({fill:s.backgroundColor,text:s.color,expected})}
 const paperLabels=[...document.querySelectorAll('article h2,article h3,article p,.cell label')].filter(node=>{const s=getComputedStyle(node);return s.color!=='rgb(0, 0, 0)' && s.color!=='rgb(255, 255, 255)'}).map(node=>({tag:node.tagName,color:getComputedStyle(node).color}));
 return {borders,contrast,paperLabels,horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,solidCount:document.querySelectorAll('#solids .tile').length,overflowVisible:!!document.querySelector('.overflow:not([hidden])'),title:document.title};
}'''


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def latest_workspace(skill):
    candidates = []
    for path in (ROOT / "evaluations/runs").glob(f"20261003-solid-{skill}-support-*"):
        result = path / "evaluation-result.json"
        if result.is_file() and json.loads(result.read_text())["passed"]:
            candidates.append(path)
    if not candidates:
        raise RuntimeError(f"No passing support run for {skill}")
    return sorted(candidates)[-1] / "workspace"


def main():
    report = {"date": "2026-10-03", "states": [], "findings": [], "media": {}, "raster": []}
    screenshots = ART / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}/"
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            for width in (1440, 390):
                page = browser.new_page(viewport={"width": width, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(origin + "projects/solid-colorset-style/artifacts/previews/style-guide.html")
                for palette, count in (("cs1", 16), ("cs2", 36)):
                    page.locator("#" + palette).click()
                    state = page.evaluate(SCAN)
                    state.update(label=f"style-guide-{palette}-{width}", errors=errors.copy(), expectedCount=count)
                    if state["solidCount"] != count or state["overflowVisible"]:
                        report["findings"].append({"label": state["label"], "error": "Unexpected solid capacity or early overflow"})
                    report["states"].append(state)
                    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
                    page.screenshot(path=str(screenshots / (state["label"] + ".png")), full_page=True)
                page.locator("#overflow").click()
                state = page.evaluate(SCAN)
                state.update(label=f"style-guide-overflow-{width}", errors=errors.copy())
                if not state["overflowVisible"]:
                    report["findings"].append({"label": state["label"], "error": "Overflow control failed"})
                report["states"].append(state)
                page.close()
            for skill in PROVIDERS:
                workspace = latest_workspace(skill)
                path = (workspace / "preview.html").relative_to(ROOT).as_posix()
                for width in (1440, 390):
                    page = browser.new_page(viewport={"width": width, "height": 1000})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(origin + path, wait_until="networkidle")
                    for action in ("initial", "hover", "focus"):
                        if action != "initial":
                            getattr(page.locator("a[href]").first, action)()
                        state = page.evaluate(SCAN)
                        state.update(label=f"{skill}-{width}-{action}", errors=errors.copy(), artifact=path)
                        report["states"].append(state)
                    page.screenshot(path=str(screenshots / f"{skill}-{width}.png"), full_page=True)
                    page.close()
            browser.close()
    finally:
        server.shutdown()
    for state in report["states"]:
        for key in ("borders", "contrast", "paperLabels", "horizontalOverflow", "errors"):
            if state.get(key):
                report["findings"].append({"label": state["label"], "check": key, "value": state[key]})
    workspace = latest_workspace("animated-svg-to-gif")
    source = workspace / "pulse.animated.svg"
    if 'stroke="#333e48"' in source.read_text() or 'stroke-width="4"' in source.read_text():
        report["findings"].append({"artifact": str(source), "error": "Pulse retains decorative outline"})
    with Image.open(workspace / "pulse.gif") as gif:
        frames, durations = [], []
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append(sha256(gif.convert("RGB").tobytes()).hexdigest())
            durations.append(gif.info.get("duration", 0))
        report["media"] = {"width": gif.width, "height": gif.height, "frames": gif.n_frames, "durationMs": sum(durations), "distinctFrames": len(set(frames)), "sourceSha256": sha256(source.read_bytes()).hexdigest()}
        if gif.width != 360 or gif.n_frames < 20 or len(set(frames)) < 10 or sum(durations) != 2000:
            report["findings"].append({"error": "Decoded GIF contract failed", "media": report["media"]})
    palettes = json.loads((ROOT / "docs/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    for skill, filename, mode in (("pixel-art-image-video", "pixel.png", "colorset1"), ("pixel-art-image-video", "extended.webp", "colorset2"), ("one-bit-dither-svg", "regional.png", "colorset1"), ("one-bit-dither-svg", "extended.png", "colorset2")):
        artifact = latest_workspace(skill) / filename
        with Image.open(artifact) as picture:
            pixels = picture.convert("RGBA").tobytes()
            colors = {"#%02x%02x%02x" % tuple(pixels[index:index + 3]) for index in range(0, len(pixels), 4) if pixels[index + 3]}
            bad = sorted(colors - set(palettes[mode]["allowed"]))
            row = {"artifact": artifact.relative_to(ROOT).as_posix(), "colorset": mode, "size": list(picture.size), "colorCount": len(colors), "offPalette": bad, "sha256": sha256(artifact.read_bytes()).hexdigest()}
            report["raster"].append(row)
            if bad:
                report["findings"].append(row)
    report["passed"] = not report["findings"]
    target = ROOT / "evaluations/solid-colorset-style/support-browser-20261003.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "states": len(report["states"]), "rasterChecks": len(report["raster"]), "media": report["media"], "findings": report["findings"]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
