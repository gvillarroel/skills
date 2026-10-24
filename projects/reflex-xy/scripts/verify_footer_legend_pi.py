#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0", "playwright==1.64.1"]
# ///
"""Independently grade native Cartesian footer legends on the final frozen subject."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"projects/reflex-xy/artifacts/footer-legend-pi"
PLAN=json.loads((OUT/"plan.json").read_text(encoding="utf-8"))
RUN=ROOT/"evaluations/runs"/PLAN["run_id"]
WORKSPACE=RUN/"workspace"
spec=importlib.util.spec_from_file_location("cap_utilities",Path(__file__).with_name("verify_errorbar_caps_pi.py"))
CAP=importlib.util.module_from_spec(spec);spec.loader.exec_module(CAP)
UTIL,BASE=CAP.UTIL,CAP.BASE
check,digest=UTIL.check,UTIL.digest


def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")


def intersects(a,b):
    return a["x"]<b["x"]+b["width"] and b["x"]<a["x"]+a["width"] and a["y"]<b["y"]+b["height"] and b["y"]<a["y"]+a["height"]


def native_layout(path,screenshot,names,xlabel):
    root=ET.parse(path).getroot();width,height=float(root.get("width")),float(root.get("height"))
    clip=next(n for n in root.iter() if n.tag.rsplit("}",1)[-1]=="clipPath")
    rect=next(n for n in clip if n.tag.rsplit("}",1)[-1]=="rect")
    plot={k:float(rect.get(k)) for k in ("x","y","width","height")}
    with sync_playwright() as playwright:
        browser=BASE.launch_browser(playwright,None)
        context=browser.new_context(viewport={"width":int(width),"height":int(height)},device_scale_factor=1)
        page=context.new_page()
        page.set_content('<!doctype html><html><body style="margin:0">'+path.read_text(encoding="utf-8")+'</body></html>')
        page.evaluate("() => document.fonts.ready")
        texts=page.evaluate("""() => [...document.querySelectorAll('svg text')].map(n=>{const b=n.getBoundingClientRect();return {text:n.textContent.trim(),x:b.x,y:b.y,width:b.width,height:b.height,fill:getComputedStyle(n).fill};})""")
        marks=page.evaluate("""() => [...document.querySelectorAll('svg line,svg rect,svg path,svg circle')].map(n=>{const b=n.getBoundingClientRect(),s=getComputedStyle(n);return {tag:n.tagName,x:b.x,y:b.y,width:b.width,height:b.height,fill:s.fill,stroke:s.stroke};})""")
        page.screenshot(path=str(screenshot))
        context.close();browser.close()
    legends=[t for t in texts if t["text"] in names]
    check(len(legends)==len(names) and {t["text"] for t in legends}==set(names),"Native legend names are missing or duplicated")
    axis=next(t for t in texts if t["text"]==xlabel)
    notes=[t for t in texts if t["text"]=="Synthetic observations"]
    check(notes,"Native chart omits the synthetic note")
    series_keys=[]
    for label in legends:
        check(label["y"]>=plot["y"]+plot["height"]+2,"A legend overlaps the native data plot")
        check(label["y"]>=axis["y"]+axis["height"]+4,"A legend touches/overlaps the x-axis title")
        check(label["x"]>=1 and label["y"]>=1 and label["x"]+label["width"]<=width-1 and label["y"]+label["height"]<=height-1,"A native legend label is clipped outside the figure")
        check(not any(intersects(label,note) for note in notes),"A legend overlaps the synthetic note")
        keys=[m for m in marks if 0<m["width"]<=40 and m["x"]+m["width"]<=label["x"]+1 and 0<=label["x"]-m["x"]-m["width"]<=15 and label["y"]-3<=m["y"]+m["height"]/2<=label["y"]+label["height"]+3]
        check(keys,"A native legend name has no visible adjacent series key")
        series_keys.append({"label":label["text"],"candidates":keys})
    check(not any(intersects(a,b) for i,a in enumerate(legends) for b in legends[i+1:]),"Native legend names overlap one another")
    geometry=[{"tag":n.tag.rsplit("}",1)[-1],"attributes":{k:v for k,v in n.attrib.items() if k not in ("fill","stroke","color","id","clip-path")},"text":n.text} for n in root.iter() if n.tag.rsplit("}",1)[-1] not in ("defs","clipPath")]
    return {"plot":plot,"x_axis_title":axis,"legend_labels":legends,"series_keys":series_keys,"notes":notes,"figure_dimensions":[width,height],"legend_plot_gap_px":min(t["y"] for t in legends)-plot["y"]-plot["height"],"legend_axis_title_gap_px":min(t["y"] for t in legends)-axis["y"]-axis["height"],"geometry":geometry}


def canonical_data(charts,data):
    reports={}
    for family in ("trend","bars"):
        candidates=[c for c in charts if c["path"] and Path(c["path"]).stem==family]
        check(candidates,f"No actual captured chart exports for {family}")
        good=[]
        for chart in candidates:
            if family=="trend":
                actual=[list(zip(t.get("x",[]),t.get("y",[]))) for t in chart["traces"] if t["kind"]=="line"]
                expected=[list(zip(data["trend"]["x"],values)) for values in data["trend"]["values"]]
                check(sorted(actual)==sorted(expected),"Actual XY line paths do not preserve the twelve supplied vertices")
                good.append({"path":chart["path"],"series":2,"vertices":12})
            else:
                actual=Counter((round(float(x)),float(y)) for t in chart["traces"] if t["kind"]=="bar" for x,y in zip(t.get("x",[]),t.get("y",[])))
                expected=Counter((index,float(value)) for row in data["bars"]["values"] for index,value in enumerate(row))
                check(actual==expected,"Actual XY grouped bars change category or value")
                good.append({"path":chart["path"],"series":3,"bars":12})
        reports[family]=good
    return reports


def main():
    result={"run_id":PLAN["run_id"],"runtime_digest":PLAN["runtime_digest"],"checks":{},"findings":[]};checks=result["checks"]
    try:
        check((OUT/"harness-result.json").is_file(),"The final isolated attempt is still running")
        checks["original_outputs"]={p:{"bytes":(WORKSPACE/p).stat().st_size,"sha256":digest(WORKSPACE/p)} for p in PLAN["outputs"]}
        source=(WORKSPACE/"app.py").read_text(encoding="utf-8");meta=BASE.metadata(source)
        check("xy==0.0.8" in meta.get("dependencies",[]),"Missing pinned PEP 723 metadata")
        expected=json.loads(re.search(r"```json\s*(.*?)\s*```",(RUN/"prompt.md").read_text(encoding="utf-8"),re.S).group(1))
        replay=OUT/"replay-workspace";check(not replay.exists(),"Refusing to replace retained source replay")
        shutil.copytree(WORKSPACE,replay,ignore=shutil.ignore_patterns("results","__pycache__",".venv"))
        checks["source_replay"]=UTIL.command(["uv","run","--script","app.py"],replay)
        header='#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = '+json.dumps(meta.get("requires-python",">=3.11"))+'\n# dependencies = '+json.dumps(meta.get("dependencies",[]))+'\n# ///\n'
        profile=OUT/"record-probe.py";record_data=OUT/"record-data.json"
        profile.write_text(header+BASE.RUNTIME_PROBE,encoding="utf-8")
        checks["record_execution"]=UTIL.command(["uv","run","--script",str(profile),str(replay/"app.py"),str(record_data)],replay)
        observations=json.loads(record_data.read_text(encoding="utf-8"))
        values=[v for o in observations for v in BASE.nested_values(o["value"])]
        for family in ("trend","bars"):
            for field,value in expected[family].items():
                check(any(v==value for v in values),f"Editable source does not retain ordered {family}.{field}")
        checks["source_records"]={"trend_points":12,"bar_values":12,"series_names":5,"all_ordered_inputs_preserved":True}
        probe=OUT/"canonical-probe.py";data=OUT/"canonical-data.json"
        probe.write_text(header+UTIL.CANONICAL_PROBE,encoding="utf-8")
        checks["probe_execution"]=UTIL.command(["uv","run","--script",str(probe),str(replay/"app.py"),str(data)],replay)
        charts=json.loads(data.read_text(encoding="utf-8"));checks["actual_chart_data"]=canonical_data(charts,expected)
        native,browsers={},{}
        for family,title,xlabel,ylabel in (("trend","Trial endpoints","Observation","Response"),("bars","Regional plan","Region","Items")):
            native[family]={};browsers[family]={}
            labels=[title,xlabel,ylabel,"Synthetic observations",*expected[family]["series"]]
            if family=="bars":labels+=expected[family]["categories"]
            for suffix,palette in (("cs1","colorset1"),("cs2","colorset2")):
                svg=WORKSPACE/f"results/{suffix}/{family}.svg";html=svg.with_suffix(".html")
                paints=UTIL.svg_inspect(svg,palette,labels)
                layout=native_layout(svg,OUT/f"{family}-{suffix}-native.png",expected[family]["series"],xlabel)
                native[family][suffix]={"paint_audit":paints,"layout":layout}
                check(layout["geometry"]==native_layout(replay/f"results/{suffix}/{family}.svg",OUT/f"{family}-{suffix}-replay-native.png",expected[family]["series"],xlabel)["geometry"],"Source replay changes native data or footer layout")
                check(BASE.inspect_html(html)["scripts"]>0,"HTML lacks the embedded client runtime")
                browsers[family][suffix]={"desktop":CAP.browser_render(html,OUT/f"{family}-{suffix}-desktop.png",1280,800,labels),"mobile":CAP.browser_render(html,OUT/f"{family}-{suffix}-mobile.png",390,844,labels)}
            check(native[family]["cs1"]["layout"]["geometry"]==native[family]["cs2"]["layout"]["geometry"],"Palette variants change native geometry or labels")
            check(native[family]["cs1"]["paint_audit"]["paints"]!=native[family]["cs2"]["paint_audit"]["paints"],"Palette variants are visually identical")
        checks["native"]=native;checks["browser"]=browsers
        notes=(WORKSPACE/"notes.md").read_text(encoding="utf-8")
        check(all(any(t in notes.lower() for t in words) for words in (("fictional","synthetic"),("footer","below"),("offline","snapshot"))),"Notes omit the fictional/footer/offline contracts")
        checks["notes"]={"text":notes,"requires_manual_truthfulness_review":True}
        checks["original_outputs_unchanged"]={p:digest(WORKSPACE/p)==v["sha256"] for p,v in checks["original_outputs"].items()}
        check(all(checks["original_outputs_unchanged"].values()),"An original Pi output changed during independent grading")
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["artifact_passed"]=not result["findings"];result["manual_review_pending"]=True
    save("independent-check.json",result)
    print(json.dumps({"artifact_passed":result["artifact_passed"],"findings":result["findings"]},indent=2))


if __name__=="__main__":main()
