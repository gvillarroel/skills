#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0", "playwright==1.64.1"]
# ///
"""Independently grade the one corrected native error-bar contract; never repair it."""
from __future__ import annotations
import ast
import argparse
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/reflex-xy/artifacts/errorbar-caps-pi"
PLAN = json.loads((OUT / "plan.json").read_text(encoding="utf-8"))
RUN = ROOT / "evaluations/runs" / PLAN["run_id"]
WORKSPACE = RUN / "workspace"
spec = importlib.util.spec_from_file_location("atlas_utilities", Path(__file__).with_name("verify_atlas_pi.py"))
UTIL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(UTIL)
BASE = UTIL.BASE
check, digest = UTIL.check, UTIL.digest
LABELS = ["Capped measurement ranges", "Observation position", "Response (units)", "Fictional supplied ranges"]
PROBE = UTIL.CANONICAL_PROBE.replace("captured=[]", """captured=[]
errorbar_calls=[]
native_errorbar=xy.errorbar
@functools.wraps(native_errorbar)
def captured_errorbar(*args,**kwargs):
    errorbar_calls.append({'cap_size':kwargs.get('cap_size'),'has_yerr':'yerr' in kwargs})
    return native_errorbar(*args,**kwargs)
xy.errorbar=captured_errorbar
""").replace("json.dumps(captured,indent=2)", "json.dumps({'charts':captured,'errorbar_calls':errorbar_calls},indent=2)")


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def affine(values, pixels):
    avg = sum(values) / len(values)
    center = sum(pixels) / len(pixels)
    slope = sum((x-avg)*(y-center) for x,y in zip(values,pixels)) / sum((x-avg)**2 for x in values)
    offset = center - slope * avg
    error = max(abs(offset+slope*x-y) for x,y in zip(values,pixels))
    check(error <= 0.035, f"Native coordinates do not match supplied values: maximum error {error}px")
    return {"scale": slope, "offset": offset, "max_pixel_error": error}


def native_geometry(path, rows):
    root = ET.parse(path).getroot()
    ns = {"s":"http://www.w3.org/2000/svg"}
    groups = root.findall(".//s:g[@clip-path]", ns)
    check(groups, "Native SVG has no clipped mark group")
    segments, centers = [], []
    for group in groups:
        for node in group.iter():
            tag = node.tag.rsplit("}",1)[-1]
            if tag == "line":
                segment = [float(node.get(k)) for k in ("x1","y1","x2","y2")]
                if math.dist(segment[:2],segment[2:]) > 0.01:
                    segments.append(segment)
            elif tag == "circle":
                centers.append([float(node.get("cx")),float(node.get("cy")),float(node.get("r"))])
    # Native errorbar exports use explicit SVG line primitives; this contract
    # deliberately verifies the actual renderer output rather than source text.
    shafts = sorted([s for s in segments if abs(s[0]-s[2])<0.01 and abs(s[1]-s[3])>0.01])
    caps = [s for s in segments if abs(s[1]-s[3])<0.01 and abs(s[0]-s[2])>0.01]
    check(len(shafts)==6, f"Expected six vertical native shafts, found {len(shafts)}")
    check(len(caps)==12, f"Expected twelve horizontal native caps, found {len(caps)}")
    check(len(segments)==18, f"Unexpected additional native mark segments: {len(segments)}")
    check(len(centers)==6, f"Expected six visible native center circles, found {len(centers)}")
    centers.sort()
    xs = [s[0] for s in shafts]
    gap = min(b-a for a,b in zip(xs,xs[1:]))
    check(gap>0, "Observation positions overlap")
    cap_ratios = []
    y_values, y_pixels = [], []
    for shaft, center, row in zip(shafts,centers,rows):
        x,ya,_,yb = shaft
        top,bottom = sorted([ya,yb])
        check(abs(center[0]-x)<=0.02 and top<center[1]<bottom, "A center is misplaced relative to its range")
        matching = [s for s in caps if abs((s[0]+s[2])/2-x)<=0.02 and min(abs(s[1]-top),abs(s[1]-bottom))<=0.02]
        check(len(matching)==2, "A shaft lacks its two centered end caps")
        for cap in matching:
            span=abs(cap[2]-cap[0]); ratio=span/gap
            check(span>=2 and ratio<=0.4, f"Cap span {span:.3f}px/{gap:.3f}px={ratio:.4f} is not compact and visible")
            cap_ratios.append(ratio)
        y_values += [row["lower"],row["center"],row["upper"]]
        y_pixels += [bottom,center[1],top]
    x_transform=affine([r["position"] for r in rows],xs)
    y_transform=affine(y_values,y_pixels)
    check(x_transform["scale"]>0 and y_transform["scale"]<0, "Native scale orientation is wrong")
    clip = root.find(".//s:clipPath/s:rect",ns)
    plot=[float(clip.get(k)) for k in ("x","y","width","height")]
    left,top,width,height=plot
    all_points=[p for s in segments for p in (s[:2],s[2:])] + [c[:2] for c in centers]
    check(all(left+1<=x<=left+width-1 and top+1<=y<=top+height-1 for x,y in all_points), "A native range/cap is clipped at the plot boundary")
    geometric={"plot":plot,"segments":segments,"centers":centers,"dimensions":[root.get("width"),root.get("height")]}
    return {"shafts":6,"caps":12,"centers":6,"nearest_x_gap_px":gap,"max_cap_gap_ratio":max(cap_ratios),
            "x_transform":x_transform,"y_transform":y_transform,"geometry":geometric}


def browser_render(path, screenshot, width, height, expected, native=False):
    with sync_playwright() as playwright:
        browser=BASE.launch_browser(playwright,None)
        context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
        requests,errors=[],[]
        def route_request(route):
            if route.request.url.startswith(("https://","http://")):
                requests.append(route.request.url); route.abort()
            else:
                route.continue_()
        context.route("**/*",route_request)
        page=context.new_page()
        page.on("pageerror",lambda e:errors.append(str(e)))
        if native:
            # Chromium's full-page capture can stall on a standalone SVG image
            # document. Embed the original, unchanged native XML in an empty
            # local HTML document solely for screenshot capture.
            page.goto("about:blank")
            page.set_content('<!doctype html><html><body style="margin:0">'+path.read_text(encoding="utf-8")+'</body></html>')
        else:
            page.goto(path.resolve().as_uri(),wait_until="load",timeout=60000)
        page.wait_for_function("() => document.querySelector('svg,canvas') !== null",timeout=30000)
        page.wait_for_timeout(900)
        text=" ".join((page.locator("svg").text_content() if native else page.locator("body").inner_text()).split())
        for label in expected:
            check(label in text,f"{path.name} lacks visible text {label!r}")
        measurements=page.evaluate("""() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,
            canvases:[...document.querySelectorAll('canvas')].map(c=>({width:c.width,height:c.height}))})""")
        page.screenshot(path=str(screenshot),full_page=True)
        if width==390:
            page.screenshot(path=str(screenshot.with_stem(screenshot.stem+"-viewport")),full_page=False)
        check(not requests,"Local HTML attempted remote requests")
        check(not errors,"Local browser JavaScript errors: "+str(errors))
        context.close();browser.close()
    return {"screenshot":str(screenshot),"requests":requests,"javascript_errors":errors,
            "measurements":measurements,"image":BASE.inspect_png(screenshot),"text":text}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume-evaluator",action="store_true",help="Continue artifact inspection after the retained SVG DOM evaluator error, without rerunning Pi or source.")
    args=parser.parse_args()
    result={"run_id":PLAN["run_id"],"runtime_digest":PLAN["runtime_digest"],"checks":{},"findings":[]}
    checks=result["checks"]
    try:
        check((OUT/"harness-result.json").is_file(),"The single Pi attempt is still running")
        checks["original_outputs"]={p:{"bytes":(WORKSPACE/p).stat().st_size,"sha256":digest(WORKSPACE/p)} for p in PLAN["outputs"]}
        check(all(v["bytes"] for v in checks["original_outputs"].values()),"An exact output is empty")
        rows=BASE.prompt_records((RUN/"prompt.md").read_text(encoding="utf-8"),"generalization")
        source=(WORKSPACE/"app.py").read_text(encoding="utf-8")
        meta=BASE.metadata(source); tree=ast.parse(source)
        check("xy==0.0.8" in meta.get("dependencies",[]),"Missing xy==0.0.8 PEP 723 pin")
        check(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="errorbar" for n in ast.walk(tree)),"No native XY errorbar call")
        replay=OUT/"replay-workspace"
        probe=OUT/"canonical-cap-probe.py";data=OUT/"canonical-cap-data.json"
        if args.resume_evaluator:
            prior=json.loads((OUT/"independent-check.json").read_text(encoding="utf-8"))
            check(len(prior["findings"])==1 and any(t in prior["findings"][0] for t in ("Node is not an HTMLElement","Page.screenshot: Timeout")),"Only the known evaluator SVG DOM/capture errors permit continuation")
            version=1 if not (OUT/"independent-check.evaluator-v1.json").exists() else 2
            retained=OUT/f"independent-check.evaluator-v{version}.json"
            check(not retained.exists(),"Refusing to replace a retained evaluator report")
            shutil.copy2(OUT/"independent-check.json",retained)
            for key in ("source_replay","records","probe_execution"):
                checks[key]=prior["checks"][key]
            checks["evaluator_continuation"]={"reason":"SVGElement needs text_content; Chromium full-page SVG-document capture stalls, so embed unchanged native XML in local HTML for capture. No task artifact defect.", "prior_reports":[f.name for f in sorted(OUT.glob('independent-check.evaluator-v*.json'))],"pi_relaunched":False,"source_rerun_again":False,"task_outputs_repaired":False}
        else:
            check(not replay.exists(),"Refusing to replace retained source replay evidence")
            shutil.copytree(WORKSPACE,replay,ignore=shutil.ignore_patterns("results","__pycache__",".venv"))
            checks["source_replay"]=UTIL.command(["uv","run","--script","app.py"],replay)
            checks["records"]=BASE.inspect_runtime_records("uv",replay,meta,rows,OUT/"records-check.json")
            header='#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = '+json.dumps(meta.get("requires-python",">=3.11"))+'\n# dependencies = '+json.dumps(meta.get("dependencies",[]))+'\n# ///\n'
            probe.write_text(header+PROBE,encoding="utf-8")
            checks["probe_execution"]=UTIL.command(["uv","run","--script",str(probe),str(replay/"app.py"),str(data)],replay)
        captured=json.loads(data.read_text(encoding="utf-8"));calls=captured["errorbar_calls"]
        check(len(calls)>=2 and all(c["has_yerr"] and isinstance(c["cap_size"],(float,int)) and 0<c["cap_size"]<=0.2 for c in calls),"Native cap-size calls are absent or not small relative to unit observation spacing")
        checks["native_errorbar_calls"]=calls
        checks["canonical_exports"]=captured["charts"]
        geometries,native,browsers={},{},{}
        for suffix,palette in (("cs1","colorset1"),("cs2","colorset2")):
            svg=WORKSPACE/f"results/{suffix}/errorbars.svg";html=svg.with_suffix(".html")
            native[suffix]=UTIL.svg_inspect(svg,palette,LABELS[:3])
            geometries[suffix]=native_geometry(svg,rows)
            check(geometries[suffix]["geometry"]==native_geometry(replay/f"results/{suffix}/errorbars.svg",rows)["geometry"],"Source replay changes native geometry")
            check(BASE.inspect_html(html)["scripts"]>0,"HTML lacks its embedded runtime")
            browsers[suffix]={"desktop":browser_render(html,OUT/f"{suffix}-desktop.png",1280,760,LABELS),
                "mobile":browser_render(html,OUT/f"{suffix}-mobile.png",390,844,LABELS),
                "native_svg":browser_render(svg,OUT/f"{suffix}-native.png",int(native[suffix]["dimensions"][0]),int(native[suffix]["dimensions"][1]),LABELS[:3],True)}
        check(geometries["cs1"]["geometry"]==geometries["cs2"]["geometry"],"Palette variants change the native chart geometry")
        check(native["cs1"]["paints"]!=native["cs2"]["paints"],"The two treatments have identical ink")
        checks["native_geometry"]=geometries;checks["native_svg"]=native;checks["browser"]=browsers
        notes=(WORKSPACE/"notes.md").read_text(encoding="utf-8")
        check(all(term in notes.lower() for term in ("cap","unit","fictional","supplied")),"Notes omit units or supplied fictional boundary meaning")
        checks["notes"]={"text":notes,"requires_manual_truthfulness_review":True}
        checks["original_outputs_unchanged"]={p:digest(WORKSPACE/p)==v["sha256"] for p,v in checks["original_outputs"].items()}
        check(all(checks["original_outputs_unchanged"].values()),"Evaluator altered original Pi artifacts")
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["artifact_passed"]=not result["findings"]
    result["manual_review_pending"]=True
    save("independent-check.json",result)
    print(json.dumps({"artifact_passed":result["artifact_passed"],"findings":result["findings"]},indent=2))


if __name__=="__main__":
    main()
