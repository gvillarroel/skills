#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Audit actual placement replay, editable policies, explanations, and exports."""

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright
from audit_pixels import audit as audit_pixels


def audit(path, screenshot=None):
    base=audit_pixels(path,screenshot)
    checks,errors,network=[],[],[]
    def check(name,condition):checks.append({"check":name,"ok":bool(condition)})
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":1400,"height":1100},reduced_motion="reduce")
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.on("request",lambda request:network.append(request.url) if request.url.startswith(("http:","https:")) else None)
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.goto(path.resolve().as_uri())
        page.wait_for_function("document.documentElement.dataset.ready === 'true'")
        data=json.loads(page.locator("#hierarchy-data").text_content())
        snapshot=lambda:page.evaluate("hierarchyDecisions.snapshot()")
        start=snapshot();count=len(data["nodes"]);width=data["pixels"]["cellPixels"]
        def step(value):page.locator("#decision-step").evaluate("(el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));}",value)
        def painted():return page.locator("#art").evaluate("c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=4)if(d[i]!==16||d[i+1]!==21||d[i+2]!==31)n++;return n;}")
        check("complete-decision-log",len(start["decisions"])==count and {r["node"] for r in start["decisions"]}==set(range(count)))
        placed=set();priority_ok=True;parent_ok=True;score_ok=True
        config=start["config"];dim=next(d for d in data["dimensions"] if d["key"]==config["priority"]["key"])
        for index,record in enumerate(start["decisions"]):
            node=data["nodes"][record["node"]]
            if index:
                eligible=[n for n in data["nodes"] if n["id"] not in placed and n["parentId"] in placed]
                if config["eligibility"]=="generation":
                    depth=min(n["depth"] for n in eligible);eligible=[n for n in eligible if n["depth"]==depth]
                def rank(n):
                    value=n["values"][dim["key"]]
                    score=0 if value is None else config["priority"]["order"].index(value) if dim["type"]=="categorical" else value*(-1 if config["priority"]["direction"]=="descending" else 1)
                    return value is None,score,n["id"]
                priority_ok &= node["id"]==min(eligible,key=rank)["id"] and record["eligible"]==len(eligible)
                parent_ok &= node["parentId"] in placed
                score_ok &= math.isclose(record["score"],sum(config["weights"][k]*v for k,v in record["terms"].items()),abs_tol=1e-12) and all(a["score"]<=record["score"] for a in record["alternatives"])
            placed.add(node["id"])
        check("priority-and-eligibility-oracle",priority_ok)
        check("parents-always-first",parent_ok)
        check("recorded-weighted-scores",score_ok)
        step(1);check("root-only-playback",snapshot()["step"]==1 and painted()==width**2)
        if count>1:
            page.locator("#decision-next").click();check("one-placement-per-next",snapshot()["step"]==2 and painted()==2*width**2)
            page.locator("#decision-back").click();check("one-placement-per-back",snapshot()["step"]==1 and painted()==width**2)
            page.locator("#decision-play").click()
            page.wait_for_function("hierarchyDecisions.snapshot().step > 1")
            if page.locator("#decision-play").inner_text()=="Pause":page.locator("#decision-play").click()
            check("play-reveals-actual-cells",painted()==snapshot()["step"]*width**2)
        step(max(1,count//2));partial=snapshot()["step"]
        check("scrub-is-exact-prefix",painted()==partial*width**2)
        if screenshot:page.screenshot(path=str(screenshot.with_name(screenshot.stem+".growth.png")),full_page=True)
        with page.expect_download() as event:page.locator("#export-svg").click()
        svg=ET.fromstring(Path(event.value.path()).read_bytes());metadata=json.loads(svg.find("{http://www.w3.org/2000/svg}metadata").text)
        check("partial-export-keeps-decision-context",metadata["layout"]["visibleRecords"]==partial and metadata["layout"]["config"]==config and len(metadata["layout"]["decisions"])==count)
        for lens in range(len(data["dimensions"])):page.locator("#lenses button").nth(lens).click()
        check("color-lenses-preserve-decisions-and-replay",snapshot()=={**start,"step":partial})
        if count>1:
            step(1)
            target=data["nodes"][start["decisions"][-1]["node"]]["id"]
            page.locator("#info").click();page.locator("#search").fill(target)
            page.locator("#results button").filter(has_text=target).first.click()
            check("search-reveals-future-record",snapshot()["step"]==count and page.evaluate("hierarchyPixels.snapshot().state.selected")==target)
            page.locator("#reset").click();page.locator("#close").click()
        page.locator("#decision-finish").click();check("show-all-restores-complete-map",painted()==count*width**2)
        page.locator("#decision-rules").click()
        check("explanation-outside-image",page.locator("#decision-explanation table tr").count()==5 and page.locator("#art").text_content()=="")
        with page.expect_download() as event:page.locator("#decision-export").click()
        exported=json.loads(Path(event.value.path()).read_text(encoding="utf-8"))
        check("downloaded-log-matches-rendered-decisions",exported["decisions"]==start["decisions"] and exported["config"]==config and len(exported["records"])==count)
        alternate=next((d for d in data["dimensions"] if d["key"]!=config["priority"]["key"]),None)
        if alternate:
            page.locator("#priority-key").select_option(alternate["key"])
            page.locator("#compose-apply").click()
            page.wait_for_function("key=>hierarchyDecisions.snapshot().config.priority.key===key",arg=alternate["key"])
            check("editable-priority-recomposes",len(snapshot()["decisions"])==count and painted()==count*width**2)
        page.locator("#weight-affinity").evaluate("el=>{el.value=0;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        page.locator("#compose-apply").click()
        page.wait_for_function("hierarchyDecisions.snapshot().config.weights.affinity === 0")
        check("editable-spatial-weights",snapshot()["config"]["weights"]["affinity"]==0)
        page.locator("#compose-restore").click();check("restore-is-deterministic",snapshot()==start)
        if screenshot:page.screenshot(path=str(screenshot.with_name(screenshot.stem+".rules.png")),full_page=True)
        check("offline-decision-engine",not network)
        check("no-decision-browser-errors",not errors)
        browser.close()
    return {"ok":base["ok"] and all(c["ok"] for c in checks),"nodes":count,"decisions":count,"pixelChecks":len(base["checks"]),"checks":checks,"pixelAudit":base,"errors":errors}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html",type=Path)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--screenshot",type=Path)
    args=parser.parse_args()
    try:result=audit(args.html,args.screenshot)
    except Exception as error:result={"ok":False,"error":str(error)}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in {"checks","pixelAudit"}}|{"failed":[c for c in result.get("checks",[]) if not c["ok"]]}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
