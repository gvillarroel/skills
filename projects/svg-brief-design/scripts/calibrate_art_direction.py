#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Prepare, run and audit blinded development calibration of the SVG art judge."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import html
import json
from pathlib import Path
import statistics
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps
from svg_excellence import REPO, DEFAULT_FONTS, encode, host_path, make_evidence, read, sha, write
from svg_art_direction import DIMENSIONS, BANDS, QUALITY_CONTEXT, GENERATOR_INTRO, OBSERVATION_PROMPT, aggregate, judge_record, make_job, observe_art

ROOT = REPO / "evaluations/runs/svg-art-v4"
CONFIG = REPO / "projects/svg-brief-design/evaluation/art-direction-v4"


def prepare():
    ROOT.mkdir(parents=True, exist_ok=False)
    CONFIG.mkdir(parents=True, exist_ok=False)
    source = REPO / "evaluations/runs/svgq2/review-v3/summary.json"
    rows = [r for r in read(source)["records"] if r["candidate"] == "q"]
    assert len(rows) == 18
    protocol = {
        "version": "4.0.0", "scope": "Public evaluator development; no private cohort or skill promotion. Retrospective quality standard is broader than the original generation brief.",
        "hypothesis": "Explicit positive art-direction evidence distinguishes curated refinement from merely functional output without provenance or resemblance rewards.",
        "population": {"current_outputs": 18, "public_reference_artworks": 6, "reference_crop_controls": 6, "synthetic_controls": 4},
        "judges": {"visual_critic": "openai-codex/gpt-6-astra", "thinking": "high", "decision_maker": "typesafe/jev-1.13"},
        "retries": 0, "max_visual_calls": 34, "max_jev_calls": 60, "configuration_candidates": 1,
        "blinding": "Anonymous single-artifact critiques and judgments. Source labels, paths, file size, source path count, prior scores and target identities withheld. No artwork in the skill.",
        "primary_checks": {"reference_above_task_generated_mean_minimum": 5, "reference_mean_gap_minimum": 15, "generated_full_credit_maximum": 1, "crop_gap_minimum": 10, "crop_controls_passing_minimum": 5, "paired_order_agreement_minimum": 5},
        "synthetic_checks": {"refined_above_rough_minimum": 15, "minimal_refined_minimum": 75, "wrong_subject_maximum": 0, "invalid_svg_maximum": 0},
        "pairwise": "One fixed middle-by-trial-name generated output per task against its reference; both A/B orders, using the independently collected critiques, 12 calls. Diagnostic crosscheck, not independent human truth.",
        "frozen_input_report_sha256": sha(source.read_bytes()), "quality_context": QUALITY_CONTEXT,
        "known_limitations": ["Six previously visible task families; calibration is not a held-out generalization test.", "User supplied corpus-level preference; no per-artifact human labels or inter-rater reliability.", "Jev reads visual critique text, not pixels; changing critic and rubric is a combined intervention."]}
    write(CONFIG/"protocol.json", protocol)
    write(CONFIG/"job.json", make_job())
    write(CONFIG/"rubric.json", {"version": "4.0.0", "dimensions": {k:{"weight":v[0],"label":v[1],"definition":v[2]} for k,v in DIMENSIONS.items()}, "bands": BANDS, "brief_caps": {"wrong":0,"major_missing":49,"minor_gap":79,"fulfilled":100}, "overall_cap": "overall readiness band + 5, maximum 100", "pass_threshold": .8, "excellent_threshold": .9, "quality_context": QUALITY_CONTEXT, "generator_introduction": GENERATOR_INTRO})
    (CONFIG/"visual-critic-prompt.txt").write_text(OBSERVATION_PROMPT, encoding="utf-8")
    items, seen = [], set()
    for row in sorted(rows, key=lambda r:(r["task"],r["name"])):
        ev = read(REPO/"evaluations/runs/svgq2/current-bounded/evidence"/(row["id"]+".json"))
        items.append({"task":row["task"],"arm":"generated","name":row["name"],"path":row["artifact"],"data":Path(row["artifact"]).read_bytes(),"request":ev["request"],"contract":ev["request_contract"],"old_score":row["score_100"]})
        if row["task"] in seen:
            continue
        seen.add(row["task"])
        native = read(row["native_result"])
        reference = host_path(native["config"]["task"]["path"])/"tests/reference.svg"
        data = reference.read_bytes()
        items.append({"task":row["task"],"arm":"reference","name":row["task"],"path":str(reference),"data":data,"request":ev["request"],"contract":ev["request_contract"]})
        root = ET.fromstring(data)
        box = [float(x) for x in root.attrib["viewBox"].replace(","," ").split()]
        box[2] *= .68
        root.set("viewBox", " ".join(map(str, box)))
        cropped = ET.tostring(root, encoding="utf-8")
        items.append({"task":row["task"],"arm":"crop_control","name":row["task"]+"-crop","path":None,"data":cropped,"request":ev["request"],"contract":ev["request_contract"]})
    brief = "Create a compact black technological HUD bar with an elongated open center and three diagonal accents at the right. Keep the design restrained, angular, and fully visible."
    good = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 140"><path fill-rule="evenodd" d="M24 38H339L365 64V102H24L42 70Z M56 54L47 70L56 86H349V71L332 54Z"/><path d="M374 40L388 40L370 102H356Z M397 40H411L393 102H379Z M420 40H434L416 102H402Z"/></svg>'
    rough = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 140"><path fill-rule="evenodd" d="M24 18H345L355 70V103H24L60 70Z M40 29L65 76L43 85H346V75L312 29Z"/><path d="M370 28L392 44L370 120H355Z M392 10H411L404 99H375Z M429 48H451L416 115H414Z"/></svg>'
    for name, data in [("minimal-refined",good),("minimal-rough",rough),("wrong-subject",'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 140"><circle cx="240" cy="70" r="45"/></svg>'),("invalid",'<svg><broken')]:
        items.append({"task":"synthetic-hud","arm":"synthetic","name":name,"path":None,"data":data.encode(),"request":brief,"contract":{"required":["HUD bar","Open center","Three diagonal accents at right"]}})
    coordinator = []
    for item in items:
        identity = sha(("art-direction-4|"+item["arm"]+"|"+item["name"]).encode())[:20]
        out = ROOT/"prepared"
        artifact = out/"artifacts"/(identity+".svg"); artifact.parent.mkdir(parents=True,exist_ok=True); artifact.write_bytes(item["data"])
        evidence = make_evidence(item["data"],item["request"],item["contract"],DEFAULT_FONTS,out/"renders"/(identity+".png"))
        write(out/"evidence"/(identity+".json"),evidence)
        coordinator.append({k:v for k,v in item.items() if k not in {"data","request","contract"}}|{"id":identity,"artifact_sha256":sha(item["data"]),"artifact_valid":evidence["artifact_valid"]})
    write(ROOT/"prepared/coordinator-only.json", coordinator)
    write(ROOT/"pre-inference-lock.json", {"files":{str(p.relative_to(REPO)).replace("\\","/"):sha(p.read_bytes()) for p in [CONFIG/"protocol.json",CONFIG/"job.json",CONFIG/"rubric.json",CONFIG/"visual-critic-prompt.txt",Path(__file__).with_name("svg_art_direction.py"),Path(__file__),ROOT/"prepared/coordinator-only.json"]}, "evidence":{r["id"]:sha((ROOT/"prepared/evidence"/(r["id"]+".json")).read_bytes()) for r in coordinator}})
    print(json.dumps({"prepared":len(coordinator),"valid":sum(r["artifact_valid"] for r in coordinator)}))


def observe(ids=None):
    rows = [r for r in read(ROOT/"prepared/coordinator-only.json") if r["artifact_valid"] and (not ids or r["id"] in ids)]
    pending = [r for r in rows if not (ROOT/"observations"/r["id"]).exists()]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(observe_art,read(ROOT/"prepared/evidence"/(r["id"]+".json")),ROOT/"prepared/renders"/(r["id"]+".png"),ROOT/"observations"/r["id"]):r for r in pending}
        for future in as_completed(futures):
            row = futures[future]
            try:
                future.result();print("Observed "+row["id"],flush=True)
            except Exception as exc:
                print("Failed "+row["id"]+": "+str(exc),flush=True)
    print(json.dumps({"requested":len(rows),"completed":sum((ROOT/"observations"/r["id"]/"critique.json").exists() for r in rows)}))


def execute_score():
    rows=read(ROOT/"prepared/coordinator-only.json")
    records=[]
    for row in rows:
        if row["artifact_valid"]:
            observation = ROOT/"observations"/row["id"]
            receipt=read(observation/"receipt.json")
            assert receipt["passed"] and receipt["artifact_sha256"]==row["artifact_sha256"]
            records.append(judge_record(read(ROOT/"prepared/evidence"/(row["id"]+".json")),read(observation/"critique.json"),row["id"]))
    path=ROOT/"records.jsonl"
    with path.open("xb") as f:
        for r in sorted(records,key=lambda r:r["id"]): f.write(encode(r)+b"\n")
    sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    execute(CONFIG/"job.json",[path],ROOT/"jev")


def report():
    native=read(ROOT/"jev/report.json")
    assert native["status"]=="complete"
    ds={x["location"]["record_id"]:x for x in [json.loads(line) for line in (ROOT/"jev/decisions.jsonl").read_text(encoding="utf-8").splitlines()]}
    rows=read(ROOT/"prepared/coordinator-only.json")
    results=[r|aggregate(ds[r["id"]]["decisions"] if r["artifact_valid"] else {},r["artifact_valid"]) for r in rows]
    for r in results:
        if r["artifact_valid"]:r["critique"]=read(ROOT/"observations"/r["id"]/"critique.json")
    summary={}
    for arm in ("reference","generated","crop_control"):
        values=[r["score_100"] for r in results if r["arm"]==arm and r["score_100"] is not None]
        summary[arm]={"n":len(values),"mean":statistics.mean(values),"min":min(values),"max":max(values)}
    families=[]
    for ref in [r for r in results if r["arm"]=="reference"]:
        gen=[r["score_100"] for r in results if r["task"]==ref["task"] and r["arm"]=="generated"]
        crop=next(r for r in results if r["task"]==ref["task"] and r["arm"]=="crop_control")
        families.append({"task":ref["task"],"reference":ref["score_100"],"generated_mean":statistics.mean(gen),"generated":gen,"crop":crop["score_100"],"gap":ref["score_100"]-statistics.mean(gen),"crop_gap":ref["score_100"]-crop["score_100"]})
    synthetic={r["name"]:r["score_100"] for r in results if r["arm"]=="synthetic"}
    checks={"coverage":all(r["score_100"] is not None for r in results),"reference_higher_5_of_6":sum(x["gap"]>0 for x in families)>=5,"reference_mean_gap_15":summary["reference"]["mean"]-summary["generated"]["mean"]>=15,"ceiling":sum(r["score_100"]==100 for r in results if r["arm"]=="generated")<=1,"crop_sensitivity":sum(x["crop_gap"]>=10 for x in families)>=5,"minimal_refined":synthetic["minimal-refined"]>=75,"refinement_gap":synthetic["minimal-refined"]-synthetic["minimal-rough"]>=15,"wrong_subject":synthetic["wrong-subject"]==0,"invalid":synthetic["invalid"]==0}
    write(ROOT/"results.json",{"summary":summary,"families":families,"synthetic":synthetic,"checks":checks,"passed_single_artifact_checks":all(checks.values()),"records":results,"jev_report":native})
    print(json.dumps({"summary":summary,"families":families,"synthetic":synthetic,"checks":checks},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=["prepare","observe","score","report"]);p.add_argument("--ids",nargs="*");a=p.parse_args()
    {"prepare":prepare,"observe":lambda:observe(a.ids),"score":execute_score,"report":report}[a.mode]()
