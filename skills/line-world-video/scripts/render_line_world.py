#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13", "resvg-py==0.5.0", "numpy>=2,<3"]
# ///
"""Audit and capture the same seekable scene used by native HyperFrames."""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import math
import os
import shutil
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import resvg_py
from color_audit import BROWSER_CHECK as COLOR_CHECK
from content_scan import source_presence, scan as scan_content

SVG_EXPORT = """() => {
 const source=document.getElementById('stage'), clone=source.cloneNode(true), originals=[source,...source.querySelectorAll('*')], copies=[clone,...clone.querySelectorAll('*')];
 const props=['fill','stroke','stroke-width','stroke-dasharray','stroke-dashoffset','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','font-size','font-weight','font-style','letter-spacing','text-anchor','dominant-baseline','display','visibility','vector-effect'];
 originals.forEach((e,i)=>{const cs=getComputedStyle(e);for(const p of props)copies[i].style.setProperty(p,cs.getPropertyValue(p));if(e.tagName==='text'||e.tagName==='tspan')copies[i].style.fontFamily='Space Grotesk';});
 clone.setAttribute('xmlns','http://www.w3.org/2000/svg');clone.setAttribute('width',innerWidth);clone.setAttribute('height',innerHeight);clone.style.width=innerWidth+'px';clone.style.height=innerHeight+'px';
 clone.querySelectorAll('style').forEach(e=>e.remove());
 const bg=document.createElementNS('http://www.w3.org/2000/svg','rect');bg.setAttribute('width','100%');bg.setAttribute('height','100%');bg.setAttribute('fill','#ffffff');clone.insertBefore(bg,clone.firstChild);
 return new XMLSerializer().serializeToString(clone);
}"""


def capture(page, project, method):
    if method == "browser":
        return page.screenshot(type="png", timeout=10000)
    svg = page.evaluate(SVG_EXPORT)
    return resvg_py.svg_to_bytes(svg_string=svg, font_files=[str(project / "assets/fonts/space-grotesk.ttf")], skip_system_fonts=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def browser_path():
    cache = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache"))) / "ms-playwright"
    cached = sorted(cache.glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"), key=lambda p: int(p.parts[-3].split("-")[-1]), reverse=True)
    paths = [os.environ.get("LINE_WORLD_BROWSER"), *map(str, cached), "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "/usr/bin/google-chrome", "/usr/bin/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    return next((p for p in paths if p and Path(p).is_file()), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--benchmark-capture", action="store_true", help="Compare a small sample of both capture methods without encoding a movie.")
    parser.add_argument("--benchmark-frames", type=int, default=6)
    parser.add_argument("--capture", choices=("svg", "browser"), default="browser", help="Default to direct browser capture; use svg explicitly for the computed SVG/resvg route.")
    args = parser.parse_args()
    project, report_path = args.project.resolve(), args.report.resolve()
    if args.benchmark_capture:
        from capture_benchmark import benchmark
        return benchmark(project,report_path,args.benchmark_frames)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    images = report_path.parent / (report_path.stem + "-frames")
    images.mkdir(parents=True, exist_ok=True)
    story = json.loads((project / "story.json").read_text(encoding="utf-8-sig"))
    if story.get("mode") == "atlas":
        from atlas_audit import main_atlas
        return main_atlas(args)
    timing = json.loads((project / "timing.json").read_text(encoding="utf-8"))
    palettes = json.loads((project / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))
    allowed = set(palettes["colorsets"][story["palette"]]["allowed"])
    report = {"ok": False, "renderer": "Playwright computed SVG + resvg" if args.capture == "svg" else "Playwright screenshots", "nativeHyperFrames": False, "findings": [], "samples": [], "audio": "silent", "palette": story["palette"]}
    handler = functools.partial(QuietHandler, directory=str(project))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True, args=["--allow-file-access-from-files", "--disable-gpu"])
            page = browser.new_page(viewport={"width": story["width"], "height": story["height"]}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/index.html", wait_until="networkidle")
            page.evaluate("async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready;}")
            page.wait_for_function("typeof window.renderAt === 'function'")
            report['contentSource']=source_presence(page,timing['duration'],story['fps'])
            if not report['contentSource']['ok']:report['findings'].append({'issue':'No explanatory object is visible.','intervals':report['contentSource']['emptyIntervals']})
            samples = set()
            for beat in timing["beats"]:
                samples.add(round(beat["start"] + beat["duration"] / 2, 4))
                samples.add(round(beat["start"] + min(1.35, beat["duration"] / 2), 4))
                samples.add(round(beat["end"] - .15, 4))
            samples.add(timing["duration"] - 1 / story["fps"])
            for focus in timing["focusWindows"]:
                samples.add(round((focus["start"] + focus["end"]) / 2, 4))
            checks = r"""() => {
              const svg=document.getElementById('stage'), paints=new Set(), issues=[];
              const normal=s=>{const m=s.match(/^rgb\((\d+), (\d+), (\d+)\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):s};
              for(const e of svg.querySelectorAll('*')){const cs=getComputedStyle(e);for(const p of ['fill','stroke']){const v=normal(cs[p]);if(v&&v!=='none')paints.add(v)}
                if(e.tagName==='text'&&+cs.opacity>.95){const r=e.getBoundingClientRect();if(r.width&&r.height&&r.x>=0&&r.y>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&parseFloat(cs.fontSize)*Math.abs(e.getCTM().a)>=19){if(r.width>innerWidth*.94)issues.push('Overwide visible label: '+e.textContent)}}}
              const records=[...document.querySelectorAll('.table-row')].map(e=>{
                const id=e.dataset.rowId,pair=[...document.querySelectorAll('.pair')].find(p=>p.dataset.rowId===id);
                return {id,before:+e.querySelector('.before-value').textContent,after:+e.querySelector('.after-value').textContent,
                  chartValue:+pair.querySelector('.chart-value').textContent,beforeWidth:+pair.querySelector('.before-bar').getAttribute('width'),afterWidth:+pair.querySelector('.after-bar').getAttribute('width')};});
              const state=window.snapshot(), selected=[...document.querySelectorAll('.table-row')].find(e=>e.dataset.rowId===state.selectedRowId);
              const guide=document.querySelector('#attention-dot circle:last-child');
              if(normal(getComputedStyle(guide).fill)!=='#9e1b32'||state.guideColor!=='#9e1b32')issues.push('Guide differs from primary red.');
              if(!Number.isFinite(state.guideRadius)||Math.abs(+guide.getAttribute('r')-state.guideRadius)>1e-8||state.guideRadius<STORY.attention.travelRadius-1e-8||state.guideRadius>STORY.attention.emitRadius+1e-8)issues.push('Guide radius violates its attention contract.');
              const expectedContext=STORY.presentation?.contextLabels?.[state.beat]||'';
              if(document.querySelector('#context-label')?.textContent!==expectedContext)issues.push('Visible context differs from the explicit request.');
              if(document.querySelector('.world-headline,#conclusion'))issues.push('An automatic heading or closing slogan is present.');
              const selectedHistory=[...document.querySelectorAll('.history-path')].find(e=>e.dataset.rowId===state.selectedRowId);
              for(const node of document.querySelectorAll('#producer-diagram .node')){
                const circle=node.querySelector('circle'),label=node.querySelector('.label');if(circle&&label){const a=circle.getBoundingClientRect(),b=label.getBoundingClientRect();if(b.width>a.width*.98||b.height>a.height*.98)issues.push('Producer label exceeds its circle: '+label.textContent.trim());}}
              return {state,records,focusPaint:normal(getComputedStyle(selected.querySelector('.row-label')).fill),historyPaint:normal(getComputedStyle(selectedHistory).stroke),paints:[...paints],issues,svgCount:document.querySelectorAll('svg').length,d3Version:d3.version};
            }"""
            for seconds in sorted(samples):
                page.evaluate("t=>renderAt(t)", seconds)
                result = page.evaluate(checks)
                color=page.evaluate(COLOR_CHECK)
                result['colorPriority']=color
                if not color['ok']:
                    report['findings'].append({'time':seconds,'issue':'Large dark neutral blocks violate the red/gray-first style.','marks':color['darkBlocks']})
                bad = sorted(set(result["paints"]) - allowed)
                if bad:
                    report["findings"].append({"time": seconds, "unsupportedPaint": bad})
                report["findings"].extend({"time": seconds, "issue": v} for v in result["issues"])
                state = result["state"]
                units = []
                for actual, expected in zip(result["records"], story["rows"]):
                    if any(actual[key] != expected[key] for key in ("id", "before", "after")) or actual["chartValue"] != expected["after"]:
                        report["findings"].append({"time": seconds, "issue": "Visible table or chart values differ from source data."})
                    if state["beat"] == "compare" and seconds >= next(b["start"] for b in timing["beats"] if b["id"] == "compare") + 2:
                        for key in ("before", "after"):
                            if expected[key] > 0:
                                units.append(actual[key + "Width"] / expected[key])
                            elif abs(actual[key + "Width"]) > 1e-6:
                                report["findings"].append({"time": seconds, "issue": "A zero value has a nonzero plotted length."})
                if units and max(units) - min(units) > 1e-5:
                    report["findings"].append({"time": seconds, "issue": "Paired data marks do not use one truthful shared scale."})
                if state["beat"] in ("compare", "history") and result["focusPaint"] != "#9e1b32":
                    report["findings"].append({"time": seconds, "issue": "Selected table row lacks its visible focus paint."})
                if state["beat"] == "history" and result["historyPaint"] != "#9e1b32":
                    report["findings"].append({"time": seconds, "issue": "Selected history lacks its visible focus paint."})
                for focus in timing["focusWindows"]:
                    if focus["start"] <= seconds < focus["end"]:
                        if state["selectedRowId"] != focus["rowId"] or state["before"] != focus["before"] or state["after"] != focus["after"]:
                            report["findings"].append({"time": seconds, "issue": "Table/chart focus disagrees with source values."})
                before = page.locator("#stage").evaluate("e=>e.outerHTML")
                page.evaluate("renderAt(0)")
                page.evaluate("t=>renderAt(t)", seconds)
                if page.locator("#stage").evaluate("e=>e.outerHTML") != before:
                    report["findings"].append({"time": seconds, "issue": "Repeated seek is not deterministic."})
                file = images / f"frame-{seconds:07.3f}.png"
                file.write_bytes(capture(page, project, args.capture))
                report["samples"].append({"time": seconds, "path": str(file), "state": state})
            report["findings"].extend({"browserError": v} for v in errors)
            report["d3Version"] = page.evaluate("d3.version")
            if not args.audit_only and not report["findings"]:
                if not args.output:
                    raise ValueError("--output is required unless --audit-only is used.")
                output = args.output.resolve()
                output.parent.mkdir(parents=True, exist_ok=True)
                count = round(timing["duration"] * story["fps"])
                command = ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-vcodec", "png", "-framerate", str(story["fps"]), "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    for i in range(count):
                        page.evaluate("t=>renderAt(t)", i / story["fps"])
                        process.stdin.write(capture(page, project, args.capture))
                        if i % max(1, story["fps"] * 5) == 0:
                            print(f"Captured {i}/{count} frames", flush=True)
                    process.stdin.close()
                    stderr = process.stderr.read().decode("utf-8", errors="replace")
                    code = process.wait()
                    if code:
                        raise RuntimeError(stderr)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(output)], text=True))
                video = next(s for s in probe["streams"] if s["codec_type"] == "video")
                report["media"] = {"path": str(output), "width": video["width"], "height": video["height"], "fps": video["r_frame_rate"], "frames": int(video["nb_read_frames"]), "duration": float(probe["format"]["duration"]), "codec": video["codec_name"]}
                report['contentEncoded']=scan_content(output,cache=report_path.with_name(report_path.stem+'-content.json'))
                if not report['contentEncoded']['ok']:report['findings'].append({'issue':'Encoded movie has insufficient-content frames.','intervals':report['contentEncoded']['intervals']})
                if (video["width"], video["height"], int(video["nb_read_frames"])) != (story["width"], story["height"], count) or abs(float(probe["format"]["duration"]) - timing["duration"]) > 1 / story["fps"]:
                    report["findings"].append({"issue": "Encoded dimensions, duration or frame count differs from the story."})
            browser.close()
        thumb_w, thumb_h = 480, 270
        sheet = Image.new("RGB", (thumb_w * 3, (thumb_h + 34) * math.ceil(len(report["samples"]) / 3)), "white")
        painter = ImageDraw.Draw(sheet)
        for i, item in enumerate(report["samples"]):
            x, y = (i % 3) * thumb_w, (i // 3) * (thumb_h + 34)
            with Image.open(item["path"]) as im:
                sheet.paste(im.resize((thumb_w, thumb_h)), (x, y))
            painter.text((x + 12, y + thumb_h + 8), f'{item["time"]:.2f}s  |  {item["state"]["beat"]}', fill="#333e48")
        contact = report_path.parent / f"{report_path.stem}-contact-sheet.jpg"
        sheet.save(contact, quality=93)
        report["contactSheet"] = str(contact)
        report["ok"] = not report["findings"]
    except Exception as exc:
        report["findings"].append({"error": str(exc)})
    finally:
        server.shutdown()
        server.server_close()
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "report": str(report_path), "findings": report["findings"]}, ensure_ascii=False))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
