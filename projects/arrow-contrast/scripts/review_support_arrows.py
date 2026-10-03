#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52", "pillow>=11"]
# ///
"""Inspect authored Harbor direction glyphs and representative converted markers."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
from threading import Thread

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/arrow-contrast/artifacts/support"
OUT = ROOT / "evaluations/arrow-contrast/support-arrows-20261003.json"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(script, *arguments):
    command = ["uv", "run", "--script", script, *map(str, arguments)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    log = ART / (Path(script).stem + ".log")
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{script} failed; inspect {log.relative_to(ROOT)}")
    return {"command": command, "exitCode": result.returncode,
            "log": log.relative_to(ROOT).as_posix()}


def glyphs(page):
    return page.evaluate(r'''() => [...document.querySelectorAll('text')]
      .filter(n=>/[\u2190-\u2194]/u.test(n.textContent)).map(n=>{
        const s=getComputedStyle(n), r=n.getBoundingClientRect();
        let alpha=Number(s.fillOpacity), p=n;
        while(p instanceof Element){alpha*=Number(getComputedStyle(p).opacity);p=p.parentElement;}
        const c=s.fill.match(/[\d.]+/g).slice(0,3).map(Number);
        const composite=c.map(x=>x*alpha+255*(1-alpha));
        const linear=x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4;};
        const L=.2126*linear(composite[0])+.7152*linear(composite[1])+.0722*linear(composite[2]);
        const svg=document.documentElement.getBoundingClientRect();
        return {text:n.textContent,paint:s.fill,effectiveOpacity:alpha,backing:'#ffffff',
          contrast:1.05/(L+.05),bounds:{x:r.x,y:r.y,width:r.width,height:r.height},
          contained:r.left>=svg.left&&r.top>=svg.top&&r.right<=svg.right&&r.bottom<=svg.bottom};
      })''')


def marker_pixels(path):
    with Image.open(path) as image:
        image.seek(0)
        raster = image.convert("RGB")
        samples = []
        for y, foreground, backing in ((40, 0, 255), (120, 255, 0)):
            points = [(70, y), (270, y - 3), (270, y + 3), (277, y)]
            samples.append({"y": y, "shaftAndHeadPixels": [raster.getpixel(p) for p in points],
                            "expectedForeground": foreground,
                            "adjacentPixels": [raster.getpixel((270, y - 10)), raster.getpixel((270, y + 10))],
                            "expectedBacking": backing})
        passed = raster.size == (320, 160) and all(
            all(all(abs(c-row["expectedForeground"])<=16 for c in pixel) for pixel in row["shaftAndHeadPixels"])
            and all(all(abs(c-row["expectedBacking"])<=16 for c in pixel) for pixel in row["adjacentPixels"])
            for row in samples)
        return {"artifact": path.relative_to(ROOT).as_posix(), "size": raster.size,
                "passed": passed, "samples": samples,
                "scope": "Decoded interiors of both shafts and heads, plus adjacent backing; black on white and white on black."}


def main():
    ART.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("harbor_fixture", ROOT / "skills/harbor-author-evaluation-datasets/scripts/test_consolidate_harbor_reports.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    report = fixture.report()
    source = ART / "harbor-input.json"
    source.write_text(json.dumps(report) + "\n", encoding="utf-8")
    commands = [run("skills/harbor-author-evaluation-datasets/scripts/consolidate_harbor_reports.py",
                    source, "--output-dir", ART / "harbor", "--overwrite")]
    arrow = ART / "markers.svg"
    arrow.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="160" viewBox="0 0 320 160">
<defs><marker id="black" markerUnits="userSpaceOnUse" viewBox="0 0 12 12" markerWidth="12" markerHeight="12" refX="12" refY="6" orient="auto"><path d="M0 0L12 6L0 12Z" fill="#000000"/></marker>
<marker id="white" markerUnits="userSpaceOnUse" viewBox="0 0 12 12" markerWidth="12" markerHeight="12" refX="12" refY="6" orient="auto"><path d="M0 0L12 6L0 12Z" fill="#ffffff"/></marker></defs>
<rect width="320" height="160" fill="#ffffff"/><rect y="80" width="320" height="80" fill="#000000"/>
<path d="M40 40H280" stroke="#000000" stroke-width="4" fill="none" marker-end="url(#black)"/>
<path d="M40 120H280" stroke="#ffffff" stroke-width="4" fill="none" marker-end="url(#white)"/></svg>\n''', encoding="utf-8")
    commands.append(run("skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py", arrow,
                        "-o", ART / "markers.gif", "--fps", 6, "--width", 320,
                        "--duration", 1, "--scale", 1, "--background", "#ffffff", "--include-static"))
    commands.append(run("skills/one-bit-dither-svg/scripts/stylize_svg.py", arrow,
                        "-o", ART / "markers-one-bit.svg", "--mode", "original",
                        "--quality-profile", "detailed", "--render-width", 320, "--cell-size", 1,
                        "--preview-png", ART / "markers-one-bit.png", "--json-report", ART / "markers-one-bit.json"))
    commands.append(run("skills/one-bit-dither-svg/scripts/validate_stylized_svg.py",
                        ART / "markers-one-bit.svg", "--expect-mode", "original"))
    commands.append(run("skills/pixel-art-image-video/scripts/pixel_art.py", arrow,
                        "-o", ART / "markers-pixel.png", "--quality-profile", "detailed",
                        "--width", 320, "--height", 160, "--pixel-size", 1,
                        "--palette", "colorset1", "--json-report", ART / "markers-pixel.json"))
    commands.append(run("skills/pixel-art-image-video/scripts/validate_pixel_art.py",
                        ART / "markers-pixel.png", "--manifest", ART / "markers-pixel.json",
                        "--expect-pixel-size", 1, "--expect-palette-mode", "colorset1", "--expect-colorset", "colorset1"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    harbor = []
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            page = browser.new_page(viewport={"width": 1700, "height": 1100})
            for artifact in sorted((ART / "harbor").glob("*.svg")):
                page.goto(f"http://127.0.0.1:{server.server_port}/" + artifact.relative_to(ROOT).as_posix())
                harbor.append({"artifact": artifact.relative_to(ROOT).as_posix(), "glyphs": glyphs(page)})
            page.set_viewport_size({"width": 320, "height": 160})
            page.goto(f"http://127.0.0.1:{server.server_port}/" + arrow.relative_to(ROOT).as_posix())
            page.screenshot(path=str(ART / "markers-source.png"))
            browser.close()
    finally:
        server.shutdown()
    pixels = [marker_pixels(ART / name) for name in
              ("markers-source.png", "markers.gif", "markers-one-bit.png", "markers-pixel.png")]
    directions = [glyph for row in harbor for glyph in row["glyphs"]]
    passed = len(directions) == 2 and all(g["contrast"] >= 4.5 and g["contained"] for g in directions) and all(row["passed"] for row in pixels)
    result = {"date": "2026-10-03", "passed": passed, "commands": commands,
              "harbor": harbor, "decodedMarkers": pixels,
              "limits": "Representative conversion fixture only; converters preserve or intentionally restyle source imagery. This does not certify arbitrary source arrow geometry or lossy settings. No producer behavior changed in these support bundles."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "directionGlyphs": len(directions), "decodedStates": len(pixels)}, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
