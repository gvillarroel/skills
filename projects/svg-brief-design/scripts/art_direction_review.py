#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Audit native Jev responses and crosscheck anonymous art-direction preferences."""
import argparse
import copy
import html
import json
from pathlib import Path
import sys

from svg_excellence import REPO, encode, read, sha, write
from svg_art_direction import DIMENSIONS, QUALITY_CONTEXT, judge_record

ROOT=REPO/"evaluations/runs/svg-art-v4"
CONFIG=REPO/"projects/svg-brief-design/evaluation/art-direction-v4"


def verified_decisions(native, records_path):
    sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
    from jev_contract import ENDPOINT, decision, digest, response_valid
    native=Path(native);records_path=Path(records_path)
    run=read(native/"run.json")
    if read(native/"report.json")["status"]!="complete" or run["sources"][0]["sha256"]!=sha(records_path.read_bytes()):
        raise ValueError("Native coverage or input digest failure")
    validated={};models=set()
    for line in (native/"map-jobs.jsonl").read_text(encoding="utf-8").splitlines():
        planned=json.loads(line);key=digest(dict(endpoint=ENDPOINT,payload=planned["request"]))
        checkpoint=read(native/"checkpoints"/(key+".json"))
        if checkpoint["request_hash"]!=key or checkpoint["response_hash"]!=digest(checkpoint["response"]):
            raise ValueError("Native checkpoint drift")
        response_valid(checkpoint["response"],planned["request"]["questions"],run["job"]["model"])
        models.add(checkpoint["response"]["model"])
        for name,(chunk,dimension) in planned["bindings"].items():
            validated[(chunk,dimension)]=decision(checkpoint["response"]["answers"][name],run["job"]["review"])
    result={}
    for line in (native/"decisions.jsonl").read_text(encoding="utf-8").splitlines():
        row=json.loads(line);identity=row["location"]["record_id"]
        if identity in result:raise ValueError("Duplicate native output")
        for dimension,value in row["decisions"].items():
            if value!=validated[(row["id"],dimension)]:raise ValueError("Normalized/native disagreement")
        result[identity]=row
    expected={json.loads(line)["id"] for line in records_path.read_text(encoding="utf-8").splitlines()}
    if set(result)!=expected:raise ValueError("Native coverage mismatch")
    return result,sorted(models)


def audit():
    lock=read(ROOT/"pre-inference-lock.json")
    for relative,expected in lock["files"].items():
        if sha((REPO/relative).read_bytes())!=expected:raise ValueError("Pre-inference file drift: "+relative)
    rows=read(ROOT/"prepared/coordinator-only.json")
    records={json.loads(line)["id"]:json.loads(line) for line in (ROOT/"records.jsonl").read_text(encoding="utf-8").splitlines()}
    for row in rows:
        ep=ROOT/"prepared/evidence"/(row["id"]+".json")
        if sha(ep.read_bytes())!=lock["evidence"][row["id"]]:raise ValueError("Evidence drift")
        if sha((ROOT/"prepared/artifacts"/(row["id"]+".svg")).read_bytes())!=row["artifact_sha256"]:raise ValueError("SVG drift")
        if row["path"] and sha(Path(row["path"]).read_bytes())!=row["artifact_sha256"]:raise ValueError("Original modified")
        if row["artifact_valid"]:
            observation=ROOT/"observations"/row["id"]
            rec=read(observation/"receipt.json")
            if not rec["passed"] or not rec["image_seen"] or rec["model"]!="gpt-6-astra":raise ValueError("Visual critic provenance failure")
            if rec["image_sha256"]!=sha((observation/"image.png").read_bytes()):raise ValueError("Visual evidence drift")
            if records[row["id"]]!=judge_record(read(ep),read(observation/"critique.json"),row["id"]):raise ValueError("Critique/input drift")
    decisions,models=verified_decisions(ROOT/"jev",ROOT/"records.jsonl")
    receipt={"passed":True,"items":len(rows),"model_decisions":len(decisions),"observed_models":models,"inputs_and_originals_unchanged":True}
    write(ROOT/"audit.json",receipt);print(json.dumps(receipt))


def pairs():
    records={json.loads(line)["id"]:json.loads(line) for line in (ROOT/"records.jsonl").read_text(encoding="utf-8").splitlines()}
    rows=read(ROOT/"prepared/coordinator-only.json")
    cases=[];private=[]
    for ref in sorted([r for r in rows if r["arm"]=="reference"],key=lambda r:r["task"]):
        gen=sorted([r for r in rows if r["task"]==ref["task"] and r["arm"]=="generated"],key=lambda r:r["name"])[1]
        for reverse in (False,True):
            first,second=(gen,ref) if reverse else (ref,gen)
            identity=sha(("art-v4-pair|"+ref["task"]+str(reverse)).encode())[:20]
            def compact(row):
                r=records[row["id"]]
                return {"visual_critique":r["visual_critique"]}
            cases.append({"id":identity,"brief":records[ref["id"]]["brief"],"A":compact(first),"B":compact(second)})
            private.append({"id":identity,"task":ref["task"],"A_id":first["id"],"B_id":second["id"],"reference_side":"B" if reverse else "A"})
    path=ROOT/"pairs.jsonl"
    with path.open("xb") as f:
        for r in sorted(cases,key=lambda r:r["id"]):f.write(encode(r)+b"\n")
    write(ROOT/"pairs-coordinator-only.json",private)
    job=read(CONFIG/"job.json")
    job["context"]=QUALITY_CONTEXT+" Compare the two anonymous drawings solely from the specific visual critique evidence. Neither is a target to imitate. Do not infer provenance, author, price or which is expected to win. Ignore order and verbosity. A simple design can beat a complex one. Weigh visible relationships and refinement rather than counting positive or negative adjectives."
    job["questions"]={"preferred":{"type":"choice","instructions":"Which drawing is the more resolved and professionally art-directed response to this brief, considering optical balance, silhouette, shape rhythm, junctions, hierarchy and coherent restraint?","criteria":{"A":"A has stronger professional visual quality on balance, for concrete visible reasons.","B":"B has stronger professional visual quality on balance, for concrete visible reasons.","tie":"Neither has a meaningful quality advantage; differences are reasonable stylistic alternatives.","unknown":"Available observations cannot support a meaningful comparison."}}}
    job["limits"]["chunk_chars"]=24000
    write(ROOT/"pair-job.json",job)
    sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    execute(ROOT/"pair-job.json",[path],ROOT/"jev-pairs")


def pair_report():
    judgments,models=verified_decisions(ROOT/"jev-pairs",ROOT/"pairs.jsonl")
    outcomes=[]
    for pair in read(ROOT/"pairs-coordinator-only.json"):
        raw=judgments[pair["id"]]["decisions"]["preferred"]["raw"]
        preferred=raw["choice"]
        outcomes.append(pair|{"choice":preferred,"winner_id":pair.get(preferred+"_id"),"reference_wins":preferred==pair["reference_side"],"confidence":raw["confidence"]})
    by_task={task:[r for r in outcomes if r["task"]==task] for task in sorted({r["task"] for r in outcomes})}
    agreement=sum(rs[0]["winner_id"] is not None and rs[0]["winner_id"]==rs[1]["winner_id"] for rs in by_task.values())
    value={"order_agreement":agreement,"pairs":6,"reference_wins_both_orders":sum(all(r["reference_wins"] for r in rs) for rs in by_task.values()),"passed":agreement>=5,"outcomes":outcomes,"observed_models":models}
    write(ROOT/"pair-report.json",value);print(json.dumps(value,indent=2))


def gallery():
    data=read(ROOT/"results.json");rows=data["records"];out=ROOT/"review";out.mkdir(exist_ok=False)
    names={"004":"Android head","011":"Circular frame","019":"HUD bar","020":"Industrial label","024":"Periodic graph","030":"Space insignia"}
    sections=[]
    for family in data["families"]:
        task=family["task"];group=[r for r in rows if r["task"]==task and r["arm"] in {"reference","generated"}]
        group.sort(key=lambda r:(r["arm"]!="reference",r["name"]))
        cards=[]
        for r in group:
            identity=r["id"];label="Purchased reference" if r["arm"]=="reference" else "Luna + current skill"
            note=r["critique"]["overall"]
            old="" if "old_score" not in r else f'<small>Previous rubric: {r["old_score"]:g}/100</small>'
            dims="".join(f'<li>{spec[1]}: <b>{r["bands"][key]}</b></li>' for key,spec in DIMENSIONS.items())
            cards.append(f'<article><header><b>{label}</b><strong>{r["score_100"]:g} / 100</strong>{old}</header><a href="../prepared/artifacts/{identity}.svg" target="_blank"><img src="../prepared/renders/{identity}.png" alt="{label} {names[task.split("--")[0][-3:]]}"></a><div class="body"><p><b>Works:</b> {html.escape(note["works"])}</p><p><b>Limits:</b> {html.escape(note["holds_back"])}</p><p><b>Next edit:</b> {html.escape(note["highest_impact_edit"])}</p><details><summary>Design dimensions and full critique</summary><ul>{dims}</ul><pre>{html.escape(json.dumps(r["critique"],ensure_ascii=False,indent=2))}</pre></details></div></article>')
        sections.append(f'<section><h2>{names[task.split("--")[0][-3:]]}</h2><p>Reference {family["reference"]:g}; generated mean {family["generated_mean"]:.2f}; gap {family["gap"]:.2f} points.</p><div class="grid">{"".join(cards)}</div></section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG art-direction calibration</title><style>*{box-sizing:border-box}body{font:15px/1.5 system-ui,sans-serif;background:#eef1f5;color:#152238;margin:0}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:36px;line-height:1.15}h2{margin-top:48px}p{max-width:100ch}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #dce2eb;border-radius:12px;overflow:hidden}header,.body{padding:18px}header b,header strong,small{display:block}strong{font-size:28px;color:#145e54}img{display:block;width:100%;height:270px;object-fit:contain;padding:16px;background:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}summary{cursor:pointer}li{font-size:13px}small{color:#66758a}.notice{background:white;padding:18px;border-left:4px solid #8297ae}@media(max-width:1150px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.grid{grid-template-columns:1fr}main{padding:16px}}</style><main><h1>Professional quality: references and generated SVGs</h1><p>Jev assigns six art-direction bands using anonymous visual critiques from GPT-6 Astra and deterministic SVG facts. Labels are revealed here only after scoring. Each original is compared with all three existing current-skill outputs.</p><p class="notice">Local evaluation material. Purchased artwork stays outside the skill. These are development calibration results, not an independent skill-improvement claim. Historical outputs were generated before the broader professional-quality introduction. The new score is not directly comparable with the previous technical rubric.</p>'''+"".join(sections)+"</main></html>"
    (out/"index.html").write_text(page,encoding="utf-8")
    print(out/"index.html")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=["audit","pairs","pair-report","gallery"]);a=p.parse_args()
    {"audit":audit,"pairs":pairs,"pair-report":pair_report,"gallery":gallery}[a.mode]()
