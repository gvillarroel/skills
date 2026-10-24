#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0", "playwright==1.64.1"]
# ///
"""Independently check the declared native Sankey contrast contract without repairs."""
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"projects/reflex-xy/artifacts/sankey-contrast-pi"
PLAN=json.loads((OUT/"plan.json").read_text(encoding="utf-8"))
RUN=ROOT/"evaluations/runs"/PLAN["run_id"]
WORKSPACE=RUN/"workspace"
spec=importlib.util.spec_from_file_location("cap_utilities",Path(__file__).with_name("verify_errorbar_caps_pi.py"))
CAP=importlib.util.module_from_spec(spec);spec.loader.exec_module(CAP)
UTIL,BASE=CAP.UTIL,CAP.BASE
check,digest=UTIL.check,UTIL.digest
NAMES=["Intake","Review","Direct","Accepted","Returned"]
LABELS=["Fictional review flow","Synthetic flow totals",*NAMES]
PROBE=UTIL.CANONICAL_PROBE.replace("captured=[]",'''captured=[]
sankey_calls=[]
def serial(value):
    if hasattr(value,'tolist'): return serial(value.tolist())
    if isinstance(value,(tuple,list)): return [serial(v) for v in value]
    if isinstance(value,dict): return {str(k):serial(v) for k,v in value.items()}
    if value is None or isinstance(value,(str,int,float,bool)): return value
    return {'type':type(value).__name__}
for api in ('sankey','sankey_chart'):
    native=getattr(xy,api)
    def wrap(native=native,api=api):
        @functools.wraps(native)
        def called(*args,**kwargs):
            sankey_calls.append({'api':api,'links':serial(args[0] if args else kwargs.get('links')),'nodes':serial(kwargs.get('nodes')),'navigation':kwargs.get('navigation')})
            return native(*args,**kwargs)
        return called
    setattr(xy,api,wrap())
''').replace("json.dumps(captured,indent=2)","json.dumps({'charts':captured,'sankey_calls':sankey_calls},indent=2)")


def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")


def color(value):
    value=value.lower().strip()
    if re.fullmatch(r"#[a-f0-9]{8}",value):
        check(value[-2:] in ("00","ff"),"Unexpected authored translucency")
        return None if value[-2:]=="00" else value[:7]
    return UTIL.normalize_color(value)


def rgb(value):
    value=color(value)
    check(value and value.startswith("#") and len(value)==7,"Unresolved paint "+str(value))
    return tuple(int(value[i:i+2],16) for i in (1,3,5))


def luminance(channels):
    linear=[v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4 for v in channels]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))


def contrast(a,b):
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)


def native_geometry(path,palette,expected):
    root=ET.parse(path).getroot();paints=Counter()
    for node in root.iter():
        for name in ("fill","stroke","stop-color"):
            if node.get(name) and (paint:=color(node.get(name))): paints[paint]+=1
    check(not set(paints)-set(UTIL.PALETTES[palette]["allowed"]),"Noncanonical authored SVG/gradient-endpoint paint")
    paths=[n for n in root.iter() if n.tag.rsplit("}",1)[-1]=="path"]
    def x_span(node):
        values=[float(v) for v in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",node.get("d"))]
        check(len(values)==16,"Unexpected native Sankey path topology")
        return abs(values[6]-values[0])
    # Equal endpoint colors are exported as constant fills, so classify by
    # native face span rather than requiring a gradient URL.
    ribbons=[n for n in paths if x_span(n)>float(root.get("width"))*.1]
    nodes=[n for n in paths if x_span(n)<=float(root.get("width"))*.1]
    check(len(ribbons)==5 and len(nodes)==5,f"Expected five native ribbons and nodes, got {len(ribbons)}, {len(nodes)}")
    stops=[n for n in root.iter() if n.tag.rsplit("}",1)[-1]=="stop"]
    check(all(contrast(rgb(n.get("fill")),(255,255,255))>=4.5 for n in nodes),"A node is not sufficiently dark for high-contrast white labeling")
    check(all(contrast(rgb(n.get("stop-color")),(255,255,255))>=4.5 for n in stops),"A ribbon endpoint is not a canonical dark fill")
    check(all(n.get("fill","").startswith("url(") or contrast(rgb(n.get("fill")),(255,255,255))>=4.5 for n in ribbons),"A flat ribbon is not a canonical dark fill")
    heights=[]
    for node in ribbons:
        values=[float(v) for v in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",node.get("d"))]
        check(len(values)==16,"Unexpected native Sankey ribbon path topology")
        source,target=abs(values[1]-values[15]),abs(values[7]-values[9])
        check(abs(source-target)<=.025,"Link width differs between source and target")
        heights.append(source)
    quantities=[link["value"] for link in expected]
    sorted_heights,sorted_values=sorted(heights),sorted(quantities)
    scale=sum(h*v for h,v in zip(sorted_heights,sorted_values))/sum(v*v for v in sorted_values)
    error=max(abs(h-scale*v) for h,v in zip(sorted_heights,sorted_values))
    check(error<=.025,f"Native ribbon widths are not proportional: {error}px")
    text=" ".join(" ".join(n.itertext()) for n in root.iter() if n.tag.rsplit("}",1)[-1]=="text")
    check(all(label in text for label in [LABELS[0],*NAMES]),"A native node label/title is missing")
    geometry={"dimensions":[root.get("width"),root.get("height")],"paths":[n.get("d") for n in paths],
              "labels":[{k:v for k,v in n.attrib.items() if k not in ("fill","stroke")} | {"text":"".join(n.itertext())} for n in root.iter() if n.tag.rsplit("}",1)[-1]=="text"]}
    return {"nodes":5,"ribbons":5,"link_heights_px":heights,"scale_px_per_item":scale,"max_proportional_width_error_px":error,"paints":dict(paints),"geometry":geometry}


def native_contrast(path,suffix):
    root=ET.parse(path).getroot();width,height=int(root.get("width")),int(root.get("height"))
    with sync_playwright() as playwright:
        browser=BASE.launch_browser(playwright,None)
        context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
        page=context.new_page()
        page.set_content('<!doctype html><html><body style="margin:0">'+path.read_text(encoding="utf-8")+'</body></html>')
        page.evaluate("() => document.fonts.ready")
        labels=page.evaluate("""names => [...document.querySelectorAll('svg text')].filter(n=>names.includes(n.textContent.trim())).map(n=>{
            const b=n.getBoundingClientRect();return {text:n.textContent.trim(),fill:getComputedStyle(n).fill,x:b.x,y:b.y,width:b.width,height:b.height};})""",NAMES)
        check(len(labels)==5,"Native SVG does not expose five node-name text elements")
        page.screenshot(path=str(OUT/f"{suffix}-native.png"))
        page.evaluate("names => [...document.querySelectorAll('svg text')].filter(n=>names.includes(n.textContent.trim())).forEach(n=>n.style.opacity='0')",NAMES)
        backdrop=OUT/f"{suffix}-native-label-backdrop.png"
        page.screenshot(path=str(backdrop))
        context.close();browser.close()
    image=Image.open(backdrop).convert("RGB")
    for label in labels:
        bounds=[math.ceil(label["x"]),math.ceil(label["y"]),math.floor(label["x"]+label["width"]),math.floor(label["y"]+label["height"])]
        check(bounds[0]>=0 and bounds[1]>=0 and bounds[2]<=width and bounds[3]<=height,"A native node label clips outside the viewport")
        foreground=rgb(label["fill"])
        ratios=[contrast(foreground,image.getpixel((x,y))) for y in range(bounds[1],bounds[3]) for x in range(bounds[0],bounds[2])]
        check(ratios,"A native label has zero visible extent")
        label["background_contrast_min"]=min(ratios)
        label["background_contrast_coverage_4_5"]=sum(v>=4.5 for v in ratios)/len(ratios)
        check(label["background_contrast_coverage_4_5"]>=.99,f"Label {label['text']} lacks readable actual-background contrast across its native bounds")
    return {"labels":labels,"screenshot":str(OUT/f"{suffix}-native.png"),"background_screenshot":str(backdrop),"method":"Hide only node text in browser; sample unchanged SVG backdrop across each original label's bounds; require >=99% contrast >=4.5."}


def main():
    result={"run_id":PLAN["run_id"],"runtime_digest":PLAN["runtime_digest"],"checks":{},"findings":[]};checks=result["checks"]
    try:
        check((OUT/"harness-result.json").is_file(),"The single Pi attempt is still running")
        checks["original_outputs"]={p:{"bytes":(WORKSPACE/p).stat().st_size,"sha256":digest(WORKSPACE/p)} for p in PLAN["outputs"]}
        source=(WORKSPACE/"app.py").read_text(encoding="utf-8");meta=BASE.metadata(source)
        check("xy==0.0.8" in meta.get("dependencies",[]),"Missing xy==0.0.8 metadata pin")
        expected=json.loads(re.search(r"```json\s*(.*?)\s*```",(RUN/"prompt.md").read_text(encoding="utf-8"),re.S).group(1))
        replay=OUT/"replay-workspace";check(not replay.exists(),"Refusing to replace retained source replay")
        shutil.copytree(WORKSPACE,replay,ignore=shutil.ignore_patterns("results","__pycache__",".venv"))
        checks["source_replay"]=UTIL.command(["uv","run","--script","app.py"],replay)
        checks["records"]=BASE.inspect_runtime_records("uv",replay,meta,expected["links"],OUT/"records-check.json")
        header='#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = '+json.dumps(meta.get("requires-python",">=3.11"))+'\n# dependencies = '+json.dumps(meta.get("dependencies",[]))+'\n# ///\n'
        probe=OUT/"native-sankey-probe.py";data=OUT/"native-sankey-data.json"
        probe.write_text(header+PROBE,encoding="utf-8")
        checks["probe_execution"]=UTIL.command(["uv","run","--script",str(probe),str(replay/"app.py"),str(data)],replay)
        observed=json.loads(data.read_text(encoding="utf-8"));calls=observed["sankey_calls"]
        triples=[[r["source"],r["target"],r["value"]] for r in expected["links"]]
        valid=[c for c in calls if c["links"]==triples and c["nodes"]==expected["nodes"]]
        check(len(valid)>=2,"The native Sankey calls do not retain every ordered link/node")
        check(any(c["api"]=="sankey_chart" and c["navigation"] is False for c in calls),"Fixed Sankey navigation was not disabled")
        checks["native_calls"]=calls;checks["canonical_exports"]=observed["charts"]
        native,browsers,contrasts={},{},{}
        for suffix,palette in (("cs1","colorset1"),("cs2","colorset2")):
            svg=WORKSPACE/f"results/{suffix}/flows.svg";html=svg.with_suffix(".html")
            native[suffix]=native_geometry(svg,palette,expected["links"])
            check(native[suffix]["geometry"]==native_geometry(replay/f"results/{suffix}/flows.svg",palette,expected["links"])["geometry"],"Source replay changed native layout/data")
            contrasts[suffix]=native_contrast(svg,suffix)
            check(BASE.inspect_html(html)["scripts"]>0,"HTML lacks the embedded runtime")
            browsers[suffix]={"desktop":CAP.browser_render(html,OUT/f"{suffix}-desktop.png",1280,760,LABELS),"mobile":CAP.browser_render(html,OUT/f"{suffix}-mobile.png",390,844,LABELS)}
        check(native["cs1"]["geometry"]==native["cs2"]["geometry"],"Palette variants change native geometry/labels")
        check(native["cs1"]["paints"]!=native["cs2"]["paints"],"Palette variants are visually identical")
        checks["native"]=native;checks["contrast"]=contrasts;checks["browser"]=browsers
        notes=(WORKSPACE/"notes.md").read_text(encoding="utf-8")
        check(all(any(t in notes.lower() for t in options) for options in (("fictional","synthetic"),("gradient","interpolat"),("contrast","white text","white label"),("offline","snapshot"))),"Notes omit fictional/contrast/derived/offline meaning")
        checks["notes"]={"text":notes,"requires_manual_truthfulness_review":True}
        checks["original_outputs_unchanged"]={p:digest(WORKSPACE/p)==v["sha256"] for p,v in checks["original_outputs"].items()}
        check(all(checks["original_outputs_unchanged"].values()),"An original Pi output changed during evaluation")
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["artifact_passed"]=not result["findings"];result["manual_review_pending"]=True
    save("independent-check.json",result)
    print(json.dumps({"artifact_passed":result["artifact_passed"],"findings":result["findings"]},indent=2))


if __name__=="__main__": main()
