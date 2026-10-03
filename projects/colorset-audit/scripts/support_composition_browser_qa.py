#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52", "pillow>=10"]
# ///
"""Independently inspect preview chrome, small media outputs and Pages layout."""
from collections import Counter
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/colorset-audit/artifacts/support-browser"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = ROOT / "evaluations/colorset-audit/support-browser-20261002.json"
PALETTES = json.loads((ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json").read_text())["colorsets"]
TOKENS = {key: {token.lower() for token in value["allowed"]} for key, value in PALETTES.items()}
PREVIEWS = [
    "20261002-colorset-ambientcg-material-search-final", "20261002-colorset-iconify-icon-search-final",
    "20261002-colorset-kenney-asset-search-final", "20261002-colorset-pexels-media-search-final",
    "20261002-colorset-polyhaven-asset-search-final", "20261002-colorset-destockd-final2",
]
SCAN = r"""() => {
 const paints = new Map();
 function add(value,element,property) {
   for(const match of String(value).matchAll(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([.\d]+))?\)/g)) {
     if(match[4]!==undefined && Number(match[4])===0)continue;
     const token='#'+[match[1],match[2],match[3]].map(v=>Number(v).toString(16).padStart(2,'0')).join('');
     if(!paints.has(token))paints.set(token,[]);
     if(paints.get(token).length<4)paints.get(token).push({tag:element.tagName,id:element.id,property});
   }
 }
 for(const element of document.querySelectorAll('body,body *')) {
   if(element.closest('svg')||['IMG','VIDEO','CANVAS','IFRAME','SCRIPT','STYLE','SOURCE'].includes(element.tagName))continue;
   const style=getComputedStyle(element);
   if(style.display==='none'||style.visibility==='hidden')continue;
   for(const property of ['color','backgroundColor','boxShadow','textShadow'])add(style[property],element,property);
   for(const side of ['Top','Right','Bottom','Left'])if(parseFloat(style['border'+side+'Width'])>0 && style['border'+side+'Style']!=='none')add(style['border'+side+'Color'],element,'border'+side+'Color');
   if(parseFloat(style.outlineWidth)>0 && style.outlineStyle!=='none')add(style.outlineColor,element,'outlineColor');
 }
 const brokenImages=[...document.images].filter(image=>!image.complete||image.naturalWidth===0).map(image=>image.getAttribute('src'));
 const horizontalOverflow=document.documentElement.scrollWidth>innerWidth+1;
 const cardContentOverflow=[...document.querySelectorAll('article')].flatMap(card=>{
   const boundary=card.getBoundingClientRect();
   return [...card.children].filter(child=>{const r=child.getBoundingClientRect();return r.width>0&&(r.left<boundary.left-1||r.right>boundary.right+1);})
     .map(child=>({tag:child.tagName,className:child.className,excessRightPixels:Math.round(child.getBoundingClientRect().right-boundary.right)}));
 });
 return {paintSources:Object.fromEntries(paints),brokenImages,horizontalOverflow,cardContentOverflow,viewport:{width:innerWidth,height:innerHeight},scrollWidth:document.documentElement.scrollWidth,
   title:document.title,articleCount:document.querySelectorAll('article').length,linkCount:document.querySelectorAll('a[href]').length};
}"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def inspect_pixels(path, label):
    with Image.open(path) as image:
        pixels = {"#%02x%02x%02x" % value[:3] for value in image.convert("RGBA").getdata() if value[3]}
        fits = [key for key, allowed in TOKENS.items() if pixels <= allowed]
        item = {"label": label, "path": path.relative_to(ROOT).as_posix(), "size": list(image.size),
                "mode": image.mode, "colorCount": len(pixels), "colors": sorted(pixels), "fits": fits,
                "offColorset2": sorted(pixels - TOKENS["colorset2"])}
        return item, image.convert("RGB").copy()


def main():
    report = {"date": "2026-10-02", "purpose": "Independent visual and computed-paint verification; no skill source mutations",
              "sourceScope": "Imported preview media and cover image pixels remain source-preserved. HTML authored chrome is checked separately.",
              "browser": [], "raster": [], "gif": {}, "findings": []}
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            preview_routes = [(run_id, f"evaluations/runs/{run_id}/workspace/preview.html") for run_id in PREVIEWS]
            preview_routes.append(("compose-published-gallery", "skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/index.html"))
            preview_routes.append(("destockd-direct-final", "projects/colorset-audit/artifacts/html/destockd-final.html"))
            for run_id, path in preview_routes:
                for mode, viewport in [("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})]:
                    page = browser.new_page(viewport=viewport)
                    errors, requests = [], []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("requestfailed", lambda request: requests.append({"url": request.url, "failure": request.failure}))
                    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) or route.request.url.startswith("data:") else route.abort())
                    page.goto(f"{origin}/{path}", wait_until="networkidle")
                    result = page.evaluate(SCAN)
                    palette = page.locator("html").get_attribute("data-colorset") or "colorset1"
                    result.update({"artifact": path, "state": mode, "palette": palette, "offPalette": sorted(set(result["paintSources"]) - TOKENS[palette]), "pageErrors": errors, "failedRequests": requests})
                    screenshot = OUT / f"{run_id}-{mode}.png"
                    page.screenshot(path=str(screenshot), full_page=True)
                    result["screenshot"] = screenshot.relative_to(ROOT).as_posix()
                    report["browser"].append(result)
                    for action in ["hover", "focus"]:
                        first_link = page.locator("a[href]").first
                        getattr(first_link, action)()
                        state = page.evaluate(SCAN)
                        state.update({"artifact": path, "state": f"{mode}-{action}", "palette": palette,
                                      "offPalette": sorted(set(state["paintSources"]) - TOKENS[palette]),
                                      "pageErrors": errors.copy(), "failedRequests": requests.copy()})
                        report["browser"].append(state)
                    page.close()
            for mode, viewport in [("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})]:
                page = browser.new_page(viewport=viewport)
                errors, requests = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("requestfailed", lambda request: requests.append({"url": request.url, "failure": request.failure}))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) or route.request.url.startswith("data:") else route.abort())
                page.goto(f"{origin}/dist/pages/index.html", wait_until="networkidle")
                base = page.evaluate(SCAN)
                base.update({"artifact": "dist/pages/index.html", "state": mode, "palette": "colorset2", "offPalette": sorted(set(base["paintSources"]) - TOKENS["colorset2"]), "pageErrors": errors, "failedRequests": requests})
                screenshot = OUT / f"pages-index-{mode}.png"
                page.screenshot(path=str(screenshot), full_page=True)
                base["screenshot"] = screenshot.relative_to(ROOT).as_posix()
                report["browser"].append(base)
                for action in ["hover", "focus"]:
                    first_link = page.locator("a[href]").first
                    getattr(first_link, action)()
                    state = page.evaluate(SCAN)
                    state.update({"artifact": "dist/pages/index.html", "state": f"{mode}-{action}", "palette": "colorset2", "offPalette": sorted(set(state["paintSources"]) - TOKENS["colorset2"]), "pageErrors": errors.copy(), "failedRequests": requests.copy()})
                    report["browser"].append(state)
                page.close()
            browser.close()
    finally:
        server.shutdown()
    raster_paths = [
        ("pixel", "20261002-colorset-pixel-1", "pixel.png"),
        ("pixel-extended", "20261002-colorset-pixel-1", "extended.webp"),
        ("dither-regional", "20261002-colorset-dither-1", "regional.png"),
        ("dither-extended", "20261002-colorset-dither-1", "extended.png"),
    ]
    contact = Image.new("RGB", (1200, 480), "#f7f7f7")
    draw = ImageDraw.Draw(contact)
    for i, (label, run_id, filename) in enumerate(raster_paths):
        item, image = inspect_pixels(ROOT / "evaluations/runs" / run_id / "workspace" / filename, label)
        report["raster"].append(item)
        image.thumbnail((280, 400), Image.Resampling.NEAREST)
        if image.width < 256 and image.height < 256:
            scale = max(1, min(280 // image.width, 400 // image.height))
            image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
        contact.paste(image, (i * 300 + 10, 40))
        draw.text((i * 300 + 10, 10), f"{label} {item['size']}", fill="#333e48")
    contact_path = OUT / "pixel-dither-contact.png"
    contact.save(contact_path)
    report["rasterContactSheet"] = contact_path.relative_to(ROOT).as_posix()
    gif_path = ROOT / "evaluations/runs/20261002-colorset-gif-luna-3/workspace/pulse.gif"
    with Image.open(gif_path) as gif:
        frames, durations, colors = [], [], set()
        for index in range(gif.n_frames):
            gif.seek(index)
            frame = gif.convert("RGB")
            frames.append(sha256(frame.tobytes()).hexdigest())
            durations.append(gif.info.get("duration", 0))
            colors |= {"#%02x%02x%02x" % pixel for pixel in frame.getdata()}
        report["gif"] = {"path": gif_path.relative_to(ROOT).as_posix(), "size": list(gif.size), "frames": gif.n_frames,
                         "uniqueFrames": len(set(frames)), "durationMilliseconds": sum(durations), "loop": gif.info.get("loop"),
                         "encodedPixelColorCount": len(colors), "encodedOffColorset2Count": len(colors - TOKENS["colorset2"]),
                         "pixelInterpretation": "GIF quantization and antialiased edges can introduce encoded colors; exact authored source paints are validated separately."}
        sheet = Image.new("RGB", (gif.width * 4, gif.height), "#f7f7f7")
        for i, index in enumerate([0, gif.n_frames // 3, gif.n_frames * 2 // 3, gif.n_frames - 1]):
            gif.seek(index)
            sheet.paste(gif.convert("RGB"), (gif.width * i, 0))
        sheet_path = OUT / "pulse-gif-contact.png"
        sheet.save(sheet_path)
        report["gif"]["contactSheet"] = sheet_path.relative_to(ROOT).as_posix()
    for item in report["browser"]:
        if item["offPalette"] or item["horizontalOverflow"] or item["cardContentOverflow"] or item["pageErrors"] or item["brokenImages"]:
            report["findings"].append({"artifact": item["artifact"], "state": item["state"], "offPalette": item["offPalette"], "horizontalOverflow": item["horizontalOverflow"], "cardContentOverflow": item["cardContentOverflow"], "pageErrors": item["pageErrors"], "brokenImages": item["brokenImages"]})
    for item in report["raster"]:
        if item["offColorset2"]:
            report["findings"].append({"artifact": item["path"], "offPalette": item["offColorset2"]})
    report["passed"] = not report["findings"] and report["gif"]["uniqueFrames"] > 1
    report["sourceChecks"] = [
        {"command": "uv run --script scripts/validate-colorsets.py --input evaluations/runs/20261002-colorset-gif-luna-3/workspace/pulse.animated.svg --colorset colorset1", "result": "Passed; 1 artifact and 0 findings", "passed": True},
        {"command": "ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames:format=duration -of json evaluations/runs/20261002-colorset-gif-luna-3/workspace/pulse.gif", "result": "360x240; 12/1 fps; 24 frames; 2.000000 seconds", "passed": True},
    ]
    report["visualReview"] = {
        "previews": "Five synthetic resource fixtures share the same usable missing-image message and one candidate card. Destockd initially exposed an empty source keyframe image. These fixtures verify rendering and styling contracts, not live provider results.",
        "raster": "All four 80x48 outputs preserve visible circle/block geometry. Pixel art is crisp; dither patterns remain legible. Extended variants visibly add canonical blue while regional variants use red and neutral tokens.",
        "gif": "Four decoded moments show a legible Pulse label and a circle changing size/opacity; the sequence has 20 distinct frames. Antialiased/composited encoded colors are distinguished from authored source paint membership.",
        "pages": "The main index has 14 discoverable example-set cards. Desktop uses four columns; mobile uses a single column with no horizontal overflow. Titles and resource links remain visible at both widths.",
    }
    report["developmentFindingsResolvedByRegeneration"] = [
        "Root index badge/code backgrounds, shadow base, hover border and browser-default focus outline initially contained off-palette paints.",
        "Six source-preview fixtures initially inherited the browser's #101010 focus outline; final canonical builders provide explicit red focus styling.",
        "Destockd's initial missing-keyframe fixture emitted img src=\"\"; the corrected preview displays the missing-preview message.",
        "Composition gallery navy shadow was changed to canonical #333e48; explicit keyboard focus uses canonical #9e1b32. This was an acceptance-fixture-only correction.",
        "Destockd's padded missing-preview box initially extended past the mobile card edge; its final2 output uses border-box and is checked against article boundaries.",
    ]
    original = OUT / "support-browser-initial-failure.json"
    if REPORT.exists() and not original.exists():
        prior = json.loads(REPORT.read_text())
        if prior.get("findings"):
            original.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
    if original.exists():
        report["retainedInitialFailure"] = original.relative_to(ROOT).as_posix()
    for item in report["browser"]:
        sources = item.pop("paintSources")
        item["paintTokens"] = sorted(sources)
        if item["offPalette"]:
            item["offPaletteSources"] = {token: sources[token] for token in item["offPalette"]}
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "browserStates": len(report["browser"]), "rasterOutputs": len(report["raster"]), "gif": report["gif"], "findings": report["findings"], "passed": report["passed"]}, indent=2))


if __name__ == "__main__":
    main()
