#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2", "numpy>=2,<3"]
# ///
"""Review encoded scenes, cue travel and SVG reading geometry in one cached pass."""
from __future__ import annotations

import argparse
import functools
import hashlib
import html
import http.server
import json
import math
import os
import re
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from content_scan import scan as scan_content

SKILL = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def run(args, **kwargs):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", **kwargs)
    if p.returncode:
        raise ValueError((p.stderr or p.stdout)[-1800:])
    return p.stdout, p.stderr


def plan(story, timing, cues, fps, frame_count):
    identifiers = [s["id"] for s in story["scenes"]]
    if not identifiers or len(identifiers) != len(set(identifiers)) or any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) or len(value)>64 for value in identifiers):
        raise ValueError("Provide unique lowercase hyphen-case scene IDs, at most 64 characters each.")
    measured = {s["id"]: s for s in timing["scenes"]} if timing else {}
    cue_map = {s["id"]: s.get("cues", []) for s in (cues or {}).get("scenes", [])}
    scenes = []; samples = []; cursor = 0
    for index, scene in enumerate(story["scenes"]):
        observed = measured.get(scene["id"])
        if timing and observed is None:
            raise ValueError("Timing is missing scene " + scene["id"])
        duration = float(observed.get("sceneSeconds", observed.get("duration", 0))) if observed else float(scene["clipSeconds"])
        start = float(observed.get("start", cursor)) if observed else cursor
        if not math.isfinite(duration) or duration <= 0 or start < cursor - .01:
            raise ValueError("Scene timing must be finite, positive and ordered.")
        local = cue_map.get(scene["id"], [])
        entry = {"id": scene["id"], "index": index, "start": start, "duration": duration, "sourceDuration": float(scene.get("clipSeconds", duration)), "cues": local}
        scenes.append(entry)
        times = [(0, "join"), (.15, "opening"), (.45, "opening"), (.8, "opening"), (min(1.1, duration / 2), "early-reading"), (duration*.25, "reading"), (duration*.5, "reading"), (duration*.75, "reading"), (max(0, duration-1/fps), "end")]
        for cue in local:
            at = float(cue["at"]); travel = float(cue.get("travelSeconds", .28))
            if not 0 <= at <= duration + 1/fps:
                raise ValueError("Cue outside measured scene: " + scene["id"])
            times.extend([(max(0, at-travel), "travel-start:"+cue["target"]), (max(0, at-travel/2), "travel-mid:"+cue["target"]), (at, "cue:"+cue["target"])])
        seen = set()
        for t, kind in sorted(times):
            if not 0 <= t < duration:
                continue
            frame = max(0, min(frame_count-1, round((start+t)*fps)))
            if frame in seen:
                continue
            seen.add(frame); samples.append({"scene": scene["id"], "frame": frame, "seconds": frame/fps, "localSeconds": round(t, 6), "kind": kind})
        cursor = start + duration
    if abs(cursor-frame_count/fps) > max(.15, 3/fps):
        raise ValueError("The measured timeline does not cover the encoded movie.")
    samples.append({"scene": scenes[-1]["id"], "frame": frame_count-1, "seconds": (frame_count-1)/fps, "localSeconds": scenes[-1]["duration"]-1/fps, "kind": "encoded-last-frame"})
    return scenes, samples


def extract(video, video_sha, samples, output, previous):
    records = previous.get("frames", {}) if previous.get("videoSha256") == video_sha else {}
    wanted = sorted(set(s["frame"] for s in samples))
    missing = [n for n in wanted if str(n) not in records or not (output/records[str(n)]["path"]).is_file() or sha(output/records[str(n)]["path"]) != records[str(n)]["sha256"]]
    decoded = previous.get("decoded") if previous.get("videoSha256") == video_sha else None
    if missing or decoded is None:
        # Including the final requested frame forces decoding through the movie tail.
        chosen = sorted(set(missing or [wanted[-1]]))
        if decoded is None:
            chosen = sorted(set([*chosen, wanted[-1]]))
        def expression(numbers):
            if len(numbers) == 1:
                return "eq(n\\,"+str(numbers[0])+")"
            middle = len(numbers)//2
            return "("+expression(numbers[:middle])+"+"+expression(numbers[middle:])+")"
        expr = expression(chosen)
        batch = output / ("capture-"+video_sha[:12]); batch.mkdir(exist_ok=True)
        vf = "scale=640:-2,signalstats,metadata=mode=print:file=frame-stats.txt,select="+expr
        _, errors = run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-an", "-sn", "-vf", vf, "-fps_mode", "vfr", "-q:v", "3", str(batch / "%06d.jpg")], cwd=batch)
        minima = []; maxima = []
        for line in (batch / "frame-stats.txt").read_text(encoding="utf-8").splitlines():
            if line.startswith("lavfi.signalstats.YMIN="):
                minima.append(float(line.split("=")[1]))
            if line.startswith("lavfi.signalstats.YMAX="):
                maxima.append(float(line.split("=")[1]))
        decoded = {"frames": len(minima), "whiteFrames": [i for i, v in enumerate(minima) if v >= 235], "blackFrames": [i for i, v in enumerate(maxima) if v <= 24], "decoderErrors": errors.strip()}
        frames = output / "frames"; frames.mkdir(exist_ok=True)
        for i, n in enumerate(chosen, 1):
            source = batch / f"{i:06d}.jpg"
            target = frames / f"{video_sha[:12]}-{n:06d}.jpg"
            if not source.is_file():
                raise ValueError("Missing encoded sample frame " + str(n))
            target.write_bytes(source.read_bytes())
            records[str(n)] = {"path": target.relative_to(output).as_posix(), "sha256": sha(target)}
    for sample in samples:
        sample["image"] = records[str(sample["frame"])]["path"]
    return records, decoded, len(wanted)-len(missing), len(missing)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def browser_path():
    roots = Path(os.environ.get("LOCALAPPDATA", str(Path.home()/".cache"))) / "ms-playwright"
    paths = sorted(roots.glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"), reverse=True)
    options = [os.environ.get("LINE_WORLD_BROWSER", ""), *paths, "C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/chromium"]
    return next((str(p) for p in options if str(p) and Path(p).is_file()), None)


def source_review(document, scenes, clock, fps, width, height, output, extra):
    from playwright.sync_api import sync_playwright
    extensions = {".html", ".js", ".css", ".json", ".csv", ".tsv", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ttf", ".woff", ".woff2"}
    files = sorted(p for p in document.parent.rglob("*") if p.is_file() and p.suffix.lower() in extensions and not p.resolve().is_relative_to(output))
    fingerprint = key({"files": [(p.relative_to(document.parent).as_posix(), sha(p)) for p in files], "extra": [(str(p), sha(p)) for p in extra], "runtime": sha(SKILL/"assets/runtime/visual-review.js"), "focus": sha(SKILL/"assets/runtime/focus.js"), "script": sha(Path(__file__)), "scenes": scenes, "clock": clock, "fps": fps, "size": [width, height]})
    cache = output / ("source-"+fingerprint+".json")
    if cache.is_file():
        result = read(cache); result["reused"] = True; return result
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(document.parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    result = {"sourceSha256": fingerprint, "reused": False, "clock": clock, "trajectoryFps": fps, "scenes": [], "browserErrors": []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.on("pageerror", lambda e: result["browserErrors"].append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{document.name}")
            page.evaluate("async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready}")
            page.add_script_tag(path=str(SKILL/"assets/runtime/focus.js")); page.add_script_tag(path=str(SKILL/"assets/runtime/visual-review.js"))
            for scene in scenes:
                record = page.evaluate("""({scene,clock,fps})=>{
                  const stage=document.querySelector('#stage')||document.querySelector('svg');if(!stage)throw Error('A rendered SVG stage is required.');
                  const render=t=>clock==='scene-local'?window.renderClip(scene.index,t):window.renderAt(scene.start+t);
                  if(clock==='scene-local'&&typeof window.renderClip!=='function')throw Error('Scene-local review requires renderClip(index, seconds).');
                  const count=Math.ceil(scene.sourceDuration*fps),found=new Map(),readings=[],emptyIntervals=[];let previousCamera=null,minAnchors=Infinity;
                  for(let frame=0;frame<count;frame++){
                    const seconds=frame/fps,state=render(seconds)||window.snapshot?.(),camera=JSON.stringify(state?.camera||null),moving=previousCamera!==null&&camera!==previousCamera;previousCamera=camera;
                    const coverage=LineWorldVisualReview.content(stage);minAnchors=Math.min(minAnchors,coverage.visibleAnchors);if(coverage.empty){const last=emptyIntervals.at(-1);if(last&&last.lastFrame===frame-1){last.end=(frame+1)/fps;last.lastFrame=frame;last.frames++;}else emptyIntervals.push({start:seconds,end:(frame+1)/fps,firstFrame:frame,lastFrame:frame,frames:1});}
                    const test=LineWorldVisualReview.guide(stage);
                    const seen=new Set();for(const issue of test.issues){const id=issue.kind+'|'+issue.target;if(seen.has(id))continue;seen.add(id);let item=found.get(id);if(!item){item={...issue,firstSeconds:seconds,lastSeconds:seconds,frames:0,inCameraMotion:0,intervals:[],lastFrame:-2};found.set(id,item)}if(item.lastFrame!==frame-1)item.intervals.push({start:seconds,end:seconds});else item.intervals.at(-1).end=seconds;item.lastFrame=frame;item.lastSeconds=seconds;item.frames++;if(moving)item.inCameraMotion++;}
                  }
                  const points=[scene.sourceDuration*.25,scene.sourceDuration*.5,scene.sourceDuration*.75,...scene.cues.map(c=>Math.min(scene.sourceDuration-1/fps,c.at+.25))];
                  for(const seconds of [...new Set(points.map(t=>Math.round(t*fps)/fps))]){render(seconds);readings.push({seconds,...LineWorldVisualReview.reading(stage)});}
                  render(0);const first=window.snapshot?.();render(scene.sourceDuration-1/fps);const end=window.snapshot?.();render(scene.sourceDuration*.4);render(scene.sourceDuration-1/fps);const repeated=window.snapshot?.();
                  return{id:scene.id,start:scene.start,duration:scene.duration,trajectoryFrames:count,content:{minimumVisibleAnchors:minAnchors,emptyIntervals},guideIssues:[...found.values()].map(({lastFrame,...rest})=>rest),readingSamples:readings,repeatSeek:JSON.stringify(end)===JSON.stringify(repeated),firstPose:first,lastPose:end};
                }""", {"scene": scene, "clock": clock, "fps": fps})
                grouped = {}
                for reading in record["readingSamples"]:
                    for issue in reading["issues"]:
                        identity = key(issue)
                        if identity not in grouped:
                            grouped[identity] = {**issue, "firstSeconds": reading["seconds"], "lastSeconds": reading["seconds"], "samples": 0}
                        grouped[identity]["lastSeconds"] = reading["seconds"]; grouped[identity]["samples"] += 1
                record["readingIssues"] = list(grouped.values())
                result["scenes"].append(record)
            browser.close()
        save(cache, result)
    finally:
        server.shutdown(); server.server_close()
    return result


def gallery(report, output, video):
    font = ImageFont.load_default(size=18)
    movie = Path(os.path.relpath(video, output)).as_posix()
    cards = []
    for scene in report["scenes"]:
        samples = [s for s in report["samples"] if s["scene"] == scene["id"]]
        rows = math.ceil(len(samples)/3)
        sheet = Image.new("RGB", (1200, rows*250), "white"); draw = ImageDraw.Draw(sheet)
        blocks = []
        for i, sample in enumerate(samples):
            thumb = Image.open(output/sample["image"]).convert("RGB"); thumb.thumbnail((400, 225))
            x, y = i%3*400, i//3*250; sheet.paste(thumb, (x, y))
            caption = f'{sample["seconds"]:.3f}s · {sample["kind"]}'
            draw.text((x+8, y+225), caption[:43], fill="#333e48", font=font)
            blocks.append(f'<button class="frame" data-time="{sample["seconds"]}" title="{html.escape(caption)}"><img loading="lazy" src="{sample["image"]}"><span>{html.escape(caption)}</span></button>')
        target = output / (scene["id"]+".jpg"); sheet.save(target, quality=92)
        cards.append('<section><h2>'+html.escape(scene["id"])+f'</h2><a href="{target.name}">Contact sheet</a><div class="frames">'+"".join(blocks)+"</div></section>")
    body = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Video visual review</title><style>body{margin:0;background:#f8f8f8;color:#333e48;font:16px Arial}header{padding:18px 24px;background:white}video{width:min(900px,100%);display:block;margin:auto}main{padding:20px}.frames{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}.frame{background:white;color:#333e48;border:1px solid #cfcfcf;padding:0;cursor:pointer;text-align:left}.frame img{width:100%;display:block}.frame span{display:block;padding:8px}a{color:#9e1b32}section{margin-bottom:32px}button:focus{outline:2px solid #9e1b32}</style><header><h1>Visual review</h1><p>Inspect each reading state, cue and pan. Click a frame to seek the original movie. Diagnostic labels belong to this review page.</p><p><a href="report.json">Machine report</a> · Manual review: pending until an operator records findings.</p><video controls preload="metadata" src="MOVIE"></video></header><main>CARDS</main><script>const v=document.querySelector('video');document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{v.currentTime=+b.dataset.time;v.scrollIntoView({block:'center'})});</script></html>'''
    status = 'recorded for this exact movie/source' if report['manualReview']=='recorded' else 'pending until an operator records findings'
    body = body.replace('pending until an operator records findings', status)
    (output/"index.html").write_text(body.replace("MOVIE", html.escape(movie)).replace("CARDS", "".join(cards)), encoding="utf-8")


def manual_review(path, video_sha, source, scenes):
    if path is None:
        return 'pending'
    record = read(path)
    if record.get('videoSha256') != video_sha or record.get('sourceSha256') != (source['sourceSha256'] if source else None):
        raise ValueError('The visual review record belongs to different movie/source bytes.')
    reviewed = record.get('scenes', [])
    if sorted(s.get('id','') for s in reviewed) != sorted(s['id'] for s in scenes) or any(s.get('reviewed') is not True or not s.get('notes') for s in reviewed):
        raise ValueError('Record explicit visual notes for every current scene.')
    return 'recorded'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, required=True); p.add_argument("--story", type=Path, required=True); p.add_argument("--timing", type=Path); p.add_argument("--cues", type=Path); p.add_argument("--html", type=Path); p.add_argument("--clock", choices=["global", "scene-local"], default="global"); p.add_argument("--trajectory-fps", type=float, default=30); p.add_argument("--input", type=Path, action="append", default=[]); p.add_argument("--manual-review", type=Path); p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(); output = args.output.resolve()
    if output.is_relative_to(SKILL): p.error("Keep generated review files outside the skill.")
    if args.html and args.html.resolve().parent.is_relative_to(output): p.error("Use a separate review directory that does not contain the authored HTML.")
    if not math.isfinite(args.trajectory_fps) or not 1 <= args.trajectory_fps <= 60: p.error("Trajectory FPS must be between 1 and 60.")
    output.mkdir(parents=True, exist_ok=True)
    try:
        video = args.video.resolve(); probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)])[0]); stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        numerator, denominator = map(int, stream["r_frame_rate"].split("/")); fps = numerator/denominator
        frames = int(stream["nb_frames"]); story = read(args.story); scenes, samples = plan(story, read(args.timing) if args.timing else None, read(args.cues) if args.cues else None, fps, frames)
        video_sha = sha(video); cache_file = output/"cache.json"; old = read(cache_file) if cache_file.is_file() else {}
        content = scan_content(video, cache=output/'content-scan.json', video_sha=video_sha)
        source = source_review(args.html.resolve(), scenes, args.clock, args.trajectory_fps, stream["width"], stream["height"], output, [p.resolve() for p in args.input]) if args.html else None
        extra=[(content['lowestInkFrame']['frame'],'lowest-content')]
        for interval in content['intervals']:
            extra.extend((n,'insufficient-content') for n in [interval['firstFrame'],(interval['firstFrame']+interval['lastFrame'])//2,interval['lastFrame']])
        if source:
            for s,measured in zip(source['scenes'],scenes):
                for interval in s['content']['emptyIntervals']:
                    extra.append((min(frames-1,round((measured['start']+interval['start'])*fps)),'missing-source-anchor'))
        for number,kind in extra:
            scene=next((s for s in scenes if s['start']<=number/fps<s['start']+s['duration']),scenes[-1])
            if not any(s['scene']==scene['id'] and s['frame']==number for s in samples):samples.append({'scene':scene['id'],'frame':number,'seconds':number/fps,'localSeconds':max(0,number/fps-scene['start']),'kind':kind})
        samples.sort(key=lambda s:s['frame'])
        frame_records, decoded, reused, captured = extract(video, video_sha, samples, output, old)
        failures = []
        if not content['ok']: failures.append('encoded-insufficient-content')
        if decoded["frames"] != frames or decoded["whiteFrames"] or decoded["blackFrames"] or decoded["decoderErrors"]: failures.append("encoded-decode-or-blank-frames")
        if source:
            if source["browserErrors"]: failures.append("source-browser-errors")
            for scene in source["scenes"]:
                if scene['content']['emptyIntervals']: failures.append(scene['id']+':no-content-anchor')
                if scene["guideIssues"] or not scene["repeatSeek"]: failures.append(scene["id"]+":guide-or-seek")
                if any(i.get("severity") != "advisory" for r in scene["readingSamples"] for i in r["issues"]): failures.append(scene["id"]+":reading-clearance")
        manual = manual_review(args.manual_review, video_sha, source, scenes)
        report = {"ok": not failures, "manualReview": manual, "deliveryReady": not failures and manual=='recorded', "videoSha256": video_sha, "video": str(video), "scenes": scenes, "samples": samples, "encoded": decoded, "content":content, "source": source, "failures": failures, "cache": {"reusedFrames": reused, "capturedFrames": captured}, "scope": "Actual encoded frame/decode samples and optional authored SVG geometry. Source trajectory sampling is separate from encoded-pixel or speech verification. Operator visual decisions remain explicit."}
        save(output/"report.json", report); gallery(report, output, video)
        save(output/"findings.json", [{"id": s["id"], "emptySourceIntervals": s['content']['emptyIntervals'], "emptyEncodedIntervals":[v for v in content['intervals'] if v['start']<s['start']+s['duration'] and v['end']>s['start']], "guideIssues": s["guideIssues"], "readingIssues": s["readingIssues"], "repeatSeek": s["repeatSeek"]} for s in source["scenes"]] if source else [{'id':'encoded','emptyEncodedIntervals':content['intervals']}])
        save(cache_file, {"videoSha256": video_sha, "frames": frame_records, "decoded": decoded})
        summary = {"ok": report["ok"], "manualReview": manual, "deliveryReady": report['deliveryReady'], "scenes": len(scenes), "encodedSamples": len(samples), "decodedFrames": decoded["frames"], "guideFrames": sum(s["trajectoryFrames"] for s in source["scenes"]) if source else 0, "guideEvents": sum(len(s["guideIssues"]) for s in source["scenes"]) if source else 0, "advisories": sum(len(s["readingIssues"]) for s in source["scenes"]) if source else 0, "cache": report["cache"], "sourceReused": source["reused"] if source else None, "report": str(output/"report.json"), "findings": str(output/"findings.json"), "gallery": str(output/"index.html"), "failures": failures}
        summary.update({'contentFrames':content['frames'],'insufficientContentFrames':content['insufficientFrames'],'emptySourceIntervals':sum(len(s['content']['emptyIntervals']) for s in source['scenes']) if source else None,'contentReused':content['reused']})
        save(output/"summary.json", summary); print(json.dumps(summary)); return 0 if report["ok"] else 2
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)})); return 2


if __name__ == "__main__":
    raise SystemExit(main())
