#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26,<2", "playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Cache real PDF page captures, compile a paper tour, audit and render exact clocks."""
from __future__ import annotations
import argparse, functools, hashlib, http.server, json, math, os, shutil
import subprocess, threading
from pathlib import Path
import pymupdf

RESOURCE = Path(__file__).resolve().parent.parent / "assets/paper-video"

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def finite(value):
    return not isinstance(value, bool) and isinstance(value, (int,float)) and math.isfinite(value)

def rect(value, bounds):
    if not isinstance(value, list) or len(value)!=4 or not all(map(finite,value)):
        raise ValueError("Regions must be four finite PDF-point coordinates.")
    x,y,r,b=value
    if x<0 or y<0 or r<=x or b<=y or r>bounds[0] or b>bounds[1]:
        raise ValueError("Region exceeds the original PDF page or has no area.")

def validate_camera(value):
    if not isinstance(value,dict): raise ValueError("Camera settings must be an object.")
    if value.get("mode","pan") not in ("pan","static"): raise ValueError("Use pan or static camera mode; per-cue zoom pulses are not supported.")
    ranges={"zoom":(1,2.5),"enterSeconds":(1.8,12),"travelSeconds":(1.4,12),"minTravelSeconds":(1.2,8),"minHoldSeconds":(.8,12),"safeInset":(24,150),"maxPanSpeed":(100,800)}
    for key,val in value.items():
        if key=="mode":continue
        if key not in ranges or not finite(val) or not ranges[key][0]<=val<=ranges[key][1]: raise ValueError("Invalid or abrupt camera setting: "+key)
    if (value.get('zoom',1.3)-1)*1.875/value.get('enterSeconds',2.6)>.35: raise ValueError("Slow the camera entry for this zoom factor.")

def validate(story, manifest):
    if not finite(story.get("fps",30)) or not 1<=story.get("fps",30)<=120:
        raise ValueError("Frame rate must be a finite number between 1 and 120.")
    if not story.get("source",{}).get("url") or not story["source"].get("license"):
        raise ValueError("Record the paper URL, version and reviewed reuse license.")
    if not story["source"].get("version") or not story.get("scenes"):
        raise ValueError("A pinned paper version and at least one scene are required.")
    pages={p["page"]:p for p in manifest["pages"]};ids=set()
    for s in story["scenes"]:
        if not s.get("id") or s["id"] in ids: raise ValueError("Scene IDs must be unique.")
        ids.add(s["id"])
        if s.get("layout") not in ("paper","table-side","table-stack"):
            raise ValueError("Unknown paper layout.")
        validate_camera(s.get("camera",{}))
        if s.get("emphasis","margin") not in ("margin","none"): raise ValueError("Use margin emphasis or none; ink must not frame through source content.")
        if s["page"] not in pages: raise ValueError("Capture each requested PDF page first.")
        if not finite(s.get("duration")) or s["duration"]<=1: raise ValueError("Scene duration must exceed one second.")
        bounds=pages[s["page"]]["size"];rect(s["view"],bounds)
        for r in s["targets"].values(): rect(r,bounds)
        for r in s.get("avoid",[]): rect(r,bounds)
        last=-1
        for c in s.get("cues",[]):
            if c.get("target") not in s["targets"]: raise ValueError("Focus target must identify a source region.")
            if not finite(c.get("at")) or c["at"]<last or c["at"]>=s["duration"]:
                raise ValueError("Cues must be ordered and remain inside the measured scene.")
            last=c["at"]
            if c.get("view"): rect(c["view"],bounds)
        if s.get("entry"):
            e=s["entry"]
            if e["page"] not in pages: raise ValueError("Capture the entry page first.")
            rect(e["view"],pages[e["page"]]["size"])
        last_cut=0
        for shot in s.get("shots",[]):
            validate_camera(shot.get("camera",{}))
            if not finite(shot.get("at")) or not last_cut<shot["at"]<s["duration"]:
                raise ValueError("Shot changes must be ordered inside the same native scene.")
            last_cut=shot["at"]
            if shot["page"] not in pages: raise ValueError("Capture each shot's original page first.")
            rect(shot["view"],pages[shot["page"]]["size"])
        cuts=[0]+[shot["at"] for shot in s.get("shots",[])]+[s["duration"]]
        if any(not any(a<=c["at"]<b for c in s.get("cues",[])) for a,b in zip(cuts,cuts[1:])):
            raise ValueError("Every paper shot needs a focus cue inside its interval.")
        if s.get("chart"):
            ch=s["chart"];cols=ch["columns"];rows=ch["rows"]
            if not cols or not rows or len({r["id"] for r in rows})!=len(rows):
                raise ValueError("Chart rows and columns need stable identities.")
            for row in rows:
                if len(row["values"])!=len(cols) or not all(finite(v) and 0<=v<=100 for v in row["values"]):
                    raise ValueError("Percentage charts need one exact 0-100 value per column.")
            for c in s.get("cues",[]):
                if not 0<=c.get("column",0)<len(cols): raise ValueError("Cue column is outside the table.")
    return story

def prepare(pdf, project, pages, dpi):
    if not 120<=dpi<=450: raise ValueError("Use capture resolution between 120 and 450 DPI.")
    project.mkdir(parents=True, exist_ok=True);assets=project/"pages";assets.mkdir(exist_ok=True)
    target=project/"source.pdf"
    if pdf.resolve()!=target.resolve(): shutil.copyfile(pdf,target)
    sha=digest(target);previous=read(project/"paper.json") if (project/"paper.json").exists() else {}
    cached={p["page"]:p for p in previous.get("pages",[])} if previous.get("pdfSha256")==sha and previous.get("dpi")==dpi else {}
    result=[];reused=0
    with pymupdf.open(target) as doc:
        for n in sorted(set(pages)):
            if not 1<=n<=len(doc): raise ValueError("Page number is outside the PDF.")
            page=doc[n-1];image=assets/f"page-{n:03}.png"
            if n in cached and image.exists() and digest(image)==cached[n]["sha256"]:
                result.append(cached[n]);reused+=1;continue
            page.get_pixmap(dpi=dpi,alpha=False).save(image)
            words=[[round(v,3) for v in w[:4]]+[w[4]] for w in page.get_text("words")]
            result.append({"page":n,"size":[page.rect.width,page.rect.height],"image":image.relative_to(project).as_posix(),"sha256":digest(image),"words":words})
    manifest={"schemaVersion":1,"pdfSha256":sha,"dpi":dpi,"pages":result}
    write(project/"paper.json",manifest)
    return {"ok":True,"pages":len(result),"reused":reused,"pdfSha256":sha}

def build(project, story_path):
    story=validate(read(story_path),read(project/"paper.json"))
    for name in ("index.html","paper-motion.js","paper.js"):
        shutil.copyfile(RESOURCE/name,project/name)
    (project/"story.js").write_text("window.PAPER_STORY="+json.dumps(story,ensure_ascii=False)+";\nwindow.PAPER_PAGES="+(project/"paper.json").read_text(encoding="utf-8")+";\n",encoding="utf-8")
    if story_path.resolve()!=(project/"story.json").resolve(): write(project/"story.json",story)
    cursor=0;timing=[]
    for s in story["scenes"]:
        frames=math.ceil(s["duration"]*story.get("fps",30)-1e-7)
        duration=frames/story.get("fps",30)
        timing.append({"id":s["id"],"start":cursor,"end":cursor+duration,"duration":duration,"frames":frames})
        cursor+=duration
    write(project/"timing.json",{"clock":"scene-local seconds; measured voice alignment must be recorded separately","duration":cursor,"scenes":timing})
    write(project/"attribution.json",story["source"])
    return {"ok":True,"scenes":len(timing),"duration":cursor,"project":str(project)}

def inspect_page(project, page_number, max_chars=5000):
    if isinstance(max_chars,bool) or not isinstance(max_chars,int) or max_chars<=0:
        raise ValueError("Inspection needs a positive character budget.")
    requested=max_chars;max_chars=min(max_chars,12000)
    with pymupdf.open(project/"source.pdf") as doc:
        if not 1<=page_number<=len(doc): raise ValueError("Page number is outside the PDF.")
        page=doc[page_number-1];remaining=max_chars;blocks=[]
        for block in page.get_text("blocks"):
            if remaining<=0: break
            value=block[4][:remaining];remaining-=len(value)
            blocks.append({"rect":[round(v,3) for v in block[:4]],"text":value})
        return {"page":page_number,"size":[page.rect.width,page.rect.height],"blocks":blocks,"requestedMaxChars":requested,"maxChars":max_chars,"truncated":len(page.get_text())>max_chars,"textScope":"Extractable PDF text, not OCR of embedded figures."}

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def run_browser(project, output, report_path, scenes, render, poster=None, poster_scene=None, poster_at=None):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    report_path.parent.mkdir(parents=True,exist_ok=True)
    shots=report_path.parent/(report_path.stem+"-frames");shots.mkdir(exist_ok=True)
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Quiet,directory=str(project)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    report={"ok":False,"renderer":"Isolated browser capture of original PDF pages","nativeVids":False,"textCoverage":"Extractable PDF words plus manually annotated focus bodies; embedded raster labels require visual review.","scenes":[],"errors":[]}
    story=read(project/"story.json");fps=story.get("fps",30)
    cache=Path(os.environ.get("LOCALAPPDATA",""))/"ms-playwright"
    bins=sorted(cache.glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"),key=lambda p:int(p.parts[-3].split("-")[-1]),reverse=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=str(bins[0]) if bins else None,headless=True)
            page=browser.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1)
            page.on("pageerror",lambda e:report["errors"].append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_port}/index.html?capture=1")
            page.evaluate("async()=>await window.ready")
            for i,s in enumerate(story["scenes"]):
                if scenes and s["id"] not in scenes: continue
                checks=[];times=sorted(set([0,.4,.8,1.2,s["duration"]-1/fps]+[c["at"]+min(.9,(s["duration"]-c["at"])/2) for c in s["cues"]]+[c["at"] for c in s["cues"]]+[c["at"]-.16 for c in s["cues"] if c["at"]>.2]))
                for t in times:
                    state=page.evaluate("([i,t])=>renderClip(i,t)",[i,t]);checks.append(state)
                    page.screenshot(path=str(shots/f"{i+1:02}-{t:06.2f}.png"))
                for t in (s["duration"]-1/fps,1,s["duration"]-1/fps):
                    state=page.evaluate("([i,t])=>renderClip(i,t)",[i,t])
                    if t==s["duration"]-1/fps:
                        if "last" in locals() and last!=state: raise ValueError("Repeated seeking changed a scene.")
                        last=state
                del last
                trajectory=page.evaluate("""([i,fps])=>{let failures=[],frames=Math.ceil(PAPER_STORY.scenes[i].duration*fps-1e-7),previous=null,maxScaleRate=0,maxTranslationSpeed=0,zoomOutFrames=0;for(let n=0;n<frames;n++){let s=renderClip(i,n/fps);if(s.issues.length)failures.push({frame:n,issues:s.issues});if(previous&&previous.shot===s.shot&&!s.cover&&!previous.cover){let dk=(s.camera.k-previous.camera.k)*fps;maxScaleRate=Math.max(maxScaleRate,Math.abs(dk));maxTranslationSpeed=Math.max(maxTranslationSpeed,Math.hypot(s.camera.x-previous.camera.x,s.camera.y-previous.camera.y)*fps);if(dk<-.001)zoomOutFrames++}previous=s}return{frames,failures,maxScaleRate,maxTranslationSpeed,zoomOutFrames}}""",[i,fps])
                if trajectory['zoomOutFrames']:trajectory['failures'].append({'kind':'repeated-zoom-out','frames':trajectory['zoomOutFrames']})
                if trajectory['maxScaleRate']>.37:trajectory['failures'].append({'kind':'abrupt-scale-change','rate':trajectory['maxScaleRate']})
                if trajectory['maxTranslationSpeed']>820:trajectory['failures'].append({'kind':'abrupt-camera-translation','pixelsPerSecond':trajectory['maxTranslationSpeed']})
                item={"id":s["id"],"frames":math.ceil(s["duration"]*fps-1e-7),"samples":len(checks),"trajectoryFrames":trajectory["frames"],"motion":{k:trajectory[k] for k in ('maxScaleRate','maxTranslationSpeed','zoomOutFrames')},"findings":[v for c in checks for v in c["issues"]]+trajectory["failures"]}
                report["scenes"].append(item)
                if render:
                    output.mkdir(parents=True,exist_ok=True);video=output/f"{i+1:02}-{s['id']}.mp4"
                    command=["ffmpeg","-y","-v","error","-f","image2pipe","-vcodec","mjpeg","-framerate",str(fps),"-i","pipe:0","-frames:v",str(item["frames"]),"-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(video)]
                    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                    previous=None;frame=None;captures=0
                    try:
                        for n in range(item["frames"]):
                            state=page.evaluate("([i,t])=>renderClip(i,t)",[i,n/fps])
                            if state["issues"]: raise ValueError(str(state["issues"]))
                            key=json.dumps(state,sort_keys=True)
                            if key!=previous:
                                frame=page.screenshot(type="jpeg",quality=97);previous=key;captures+=1
                            proc.stdin.write(frame)
                    finally: proc.stdin.close()
                    error=proc.stderr.read().decode();code=proc.wait()
                    if code: raise ValueError(error)
                    item.update(video=str(video),sha256=digest(video),capturedFrames=captures)
                    print(json.dumps({"rendered":s["id"],"frames":item["frames"],"captured":captures}),flush=True)
            if poster:
                indices=[i for i,s in enumerate(story["scenes"]) if s["id"]==(poster_scene or story["scenes"][-1]["id"])]
                if not indices: raise ValueError("Poster scene must be a known stable ID.")
                i=indices[0];at=poster_at if poster_at is not None else story["scenes"][i]["duration"]/2
                if not finite(at) or not 0<=at<story["scenes"][i]["duration"]: raise ValueError("Poster time must remain inside its scene.")
                state=page.evaluate("([i,t])=>renderClip(i,t)",[i,at]);poster.parent.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(poster));report["poster"]={"path":str(poster),"scene":story["scenes"][i]["id"],"seconds":at,"state":state}
            browser.close()
        report["ok"]=not report["errors"] and all(not s["findings"] for s in report["scenes"])
        files=sorted(shots.glob("*.png"));columns=4;rows=math.ceil(len(files)/columns)
        sheet=Image.new("RGB",(480*columns,270*rows),"white")
        for i,p in enumerate(files):
            with Image.open(p) as im:sheet.paste(im.resize((480,270)),((i%columns)*480,(i//columns)*270))
        sheet.save(report_path.parent/(report_path.stem+"-contact.jpg"),quality=90)
    except Exception as e: report["errors"].append(str(e))
    finally: server.shutdown();server.server_close()
    write(report_path,report)
    return {"ok":report["ok"],"report":str(report_path),"errors":report["errors"],"findings":sum(len(s["findings"]) for s in report["scenes"])}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("prepare");a.add_argument("--pdf",type=Path,required=True);a.add_argument("--pages",required=True);a.add_argument("--dpi",type=int,default=300)
    a=sub.add_parser("locate");a.add_argument("--page",type=int,required=True);a.add_argument("--text",required=True)
    a=sub.add_parser("inspect");a.add_argument("--page",type=int,required=True);a.add_argument("--max-chars",type=int,default=5000,help="Requested text budget, capped at 12000 characters without failing.")
    a=sub.add_parser("build");a.add_argument("--story",type=Path,required=True)
    for name in ("audit","render"):
        a=sub.add_parser(name);a.add_argument("--report",type=Path,required=True);a.add_argument("--output",type=Path,default=Path("clips"));a.add_argument("--scene",action="append");a.add_argument("--poster",type=Path);a.add_argument("--poster-scene");a.add_argument("--poster-at",type=float)
    for a in sub.choices.values(): a.add_argument("--project",type=Path,required=True)
    a=p.parse_args();project=a.project.resolve()
    try:
        if project.is_relative_to(Path(__file__).resolve().parent.parent):
            raise ValueError("Keep generated projects outside the read-only skill bundle.")
        if a.command=="prepare":result=prepare(a.pdf,project,[int(v) for v in a.pages.split(",")],a.dpi)
        elif a.command=="build":result=build(project,a.story)
        elif a.command=="locate":
            with pymupdf.open(project/"source.pdf") as doc: result={"page":a.page,"matches":[list(r) for r in doc[a.page-1].search_for(a.text)]}
        elif a.command=="inspect":result=inspect_page(project,a.page,a.max_chars)
        else:result=run_browser(project,a.output.resolve(),a.report.resolve(),a.scene,a.command=="render",a.poster,a.poster_scene,a.poster_at)
        print(json.dumps(result,ensure_ascii=True));return 0 if result.get("ok",True) else 2
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({"ok":False,"error":str(e)}));return 2

if __name__=="__main__":raise SystemExit(main())
