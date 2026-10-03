#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Audit, report and display the curated-art calibration without score tuning."""
import html
import json
from pathlib import Path
import statistics
from svg_excellence import REPO,read,sha,write
from svg_curated_pairs import ROOT,PREVIOUS,CONFIG,DIMENSIONS,pair_board,ART_CONTEXT
from curated_quality_v52 import aggregate
from art_direction_review import verified_decisions
from recover_curated_observer import observation_path


def main():
    for relative,expected in read(ROOT/"bounds-lock.json")["files"].items():
        if sha((REPO/relative).read_bytes())!=expected:raise ValueError("Bounded reward contract changed: "+relative)
    scoring=ROOT/"scoring-v5.1"
    for relative,expected in read(scoring/"pre-inference-lock.json")["files"].items():
        if sha((REPO/relative).read_bytes())!=expected:raise ValueError("Revised frozen input changed: "+relative)
    for relative,expected in read(ROOT/"pre-inference-lock.json")["files"].items():
        if sha((REPO/relative).read_bytes())!=expected:raise ValueError("Frozen input changed: "+relative)
    source={r["id"]:r for r in read(PREVIOUS/"prepared/coordinator-only.json")}
    for r in source.values():
        if sha((PREVIOUS/"prepared/artifacts"/(r["id"]+".svg")).read_bytes())!=r["artifact_sha256"]:raise ValueError("Source artifact drift")
        if r["path"] and sha(Path(r["path"]).read_bytes())!=r["artifact_sha256"]:raise ValueError("Original artifact modified")
    native,models=verified_decisions(scoring/"jev-effective",scoring/"records.jsonl")
    inputs={json.loads(line)["id"]:json.loads(line) for line in (scoring/"records.jsonl").read_text(encoding="utf-8").splitlines()}
    rows=[]
    for pair in read(ROOT/"pairs-coordinator-only.json"):
        obs=observation_path(pair["id"]);receipt=read(obs/"receipt.json")
        expected_image=sha(pair_board(pair["A_render"],pair["B_render"]))
        if not receipt["passed"] or not receipt["image_seen"] or receipt["image_sha256"]!=expected_image or sha((obs/"image.png").read_bytes())!=expected_image:raise ValueError("Paired visual provenance failure")
        expected_prompt=(CONFIG/"visual-pair-prompt.txt").read_text(encoding="utf-8")+"\n\nArt direction:\n"+ART_CONTEXT+"\n\nBrief:\n"+pair["brief"]
        observed_input=read(obs/"input.json")
        if observed_input!={"prompt":expected_prompt,"image_sha256":expected_image,"A_sha256":pair["A_sha256"],"B_sha256":pair["B_sha256"]} or receipt["prompt_sha256"]!=sha(expected_prompt.encode()):raise ValueError("Visual prompt or side binding changed")
        comparison=read(obs/"comparison.json")
        if inputs[pair["id"]]["comparison"]!=comparison:raise ValueError("Comparison text changed")
        result=aggregate(native[pair["id"]]["decisions"],pair["candidate_side"])
        ref_side="B" if pair["candidate_side"]=="A" else "A"
        rows.append(pair|result|{"reference_preferred":result["choices"]["overall"].startswith(ref_side+"_"),"comparison":comparison})
    generated=[r for r in rows if r["kind"]=="generated"]
    if any(r["score_100"] is None for r in rows):raise ValueError("A comparison is unresolved; preserve judgments without activating")
    families=[]
    for task in sorted({r["task"] for r in generated}):
        group=[r for r in generated if r["task"]==task]
        families.append({"task":task,"anchor_level":90,"generated_mean":statistics.mean(r["score_100"] for r in group),"generated_mean_upper":statistics.mean(r["score_interval_100"][1] for r in group),"scores":[r["score_interval_100"] for r in group],"reference_preferred":sum(r["reference_preferred"] for r in group)})
    by_id={r["candidate_id"]:r for r in generated}
    stability=[{"task":r["task"],"score":by_id[r["candidate_id"]]["score_interval_100"],"reversed_score":r["score_interval_100"],"difference":max(abs(a-b) for a in r["score_interval_100"] for b in by_id[r["candidate_id"]]["score_interval_100"]),"same_overall_preference":r["reference_preferred"]==by_id[r["candidate_id"]]["reference_preferred"]} for r in rows if r["kind"]=="order_control"]
    synthetic={source[r["candidate_id"]]["name"]:r["score_100"] for r in rows if r["kind"]=="synthetic"}
    mean=statistics.mean(r["score_100"] for r in generated)
    upper=statistics.mean(r["score_interval_100"][1] for r in generated)
    checks={"all_34_artifacts_accounted":len(rows)==32 and len(source)==34,"reference_above_5_of_6_task_means":sum(f["generated_mean_upper"]<90 for f in families)>=5,"anchor_gap_15":90-upper>=15,"crop_sensitivity":sum(r["score_interval_100"][1]<80 for r in rows if r["kind"]=="crop_control")>=5,"order_stability":sum(r["difference"]<=10 for r in stability)>=5,"rough_control":synthetic["minimal-rough"]<75,"wrong_subject":synthetic["wrong-subject"]==0,"invalid_gate":not next(r["artifact_valid"] for r in source.values() if r["name"]=="invalid")}
    result={"version":"5.2.0","passed":all(checks.values()),"checks":checks,"generated_mean":mean,"generated_mean_interval":[mean,upper],"anchor_level":90,"anchor_level_is_scale_convention":True,"reference_preferred_of_18":sum(r["reference_preferred"] for r in generated),"overall_unresolved_of_18":sum(r["overall_preference_unresolved"] for r in generated),"bounded_generated_items":sum(r["point_score_100"] is None for r in generated),"families":families,"stability":stability,"synthetic":synthetic,"records":rows,"observed_models":models,"source_hashes_unchanged":True}
    write(ROOT/"results.json",result)
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
    gallery(result,source)


def gallery(result,source):
    out=ROOT/"review-v5.2";out.mkdir(exist_ok=False)
    names={"004":"Android head","011":"Circular ornament","019":"HUD bar","020":"Industrial label","024":"Vintage oscillation","030":"Space insignia"}
    sections=[]
    for family in result["families"]:
        group=[r for r in result["records"] if r["kind"]=="generated" and r["task"]==family["task"]]
        cards=[]
        for i,r in enumerate(group,1):
            candidate=source[r["candidate_id"]];anchor=source[r["B_id"] if r["candidate_side"]=="A" else r["A_id"]]
            for label,item in [("candidate",candidate),("anchor",anchor)]:
                (out/f'{r["id"]}-{label}.svg').write_bytes((PREVIOUS/"prepared/artifacts"/(item["id"]+".svg")).read_bytes())
                (out/f'{r["id"]}-{label}.png').write_bytes((PREVIOUS/"prepared/renders"/(item["id"]+".png")).read_bytes())
            image=(observation_path(r["id"])/"image.png").read_bytes();(out/(r["id"]+"-blind.png")).write_bytes(image)
            dimensions="".join(f'<li><b>{spec[1]}:</b> {html.escape(r["comparison"]["dimensions"][key]["contrast"])}</li>' for key,spec in DIMENSIONS.items())
            low,high=r["score_interval_100"];score=f"{low:g}" if low==high else f"{low:g}–{high:g} (unresolved dimensions)"
            verdict="Reference preferred" if r["reference_preferred"] else "Global preference unresolved" if r["overall_preference_unresolved"] else "Comparable overall quality" if r["choices"]["overall"]=="parity" else "Generated drawing preferred"
            cards.append(f'<article id="{r["id"]}"><header><h3>Generated attempt {i}: {score} / 100</h3><p>Previous technical rubric: {candidate["old_score"]:g}. Curated anchor level: 90 by convention. <b>{verdict}.</b></p></header><div class="pair"><figure><a href="{r["id"]}-anchor.svg" target="_blank"><img src="{r["id"]}-anchor.png" alt="Purchased quality anchor"></a><figcaption>Purchased quality anchor</figcaption></figure><figure><a href="{r["id"]}-candidate.svg" target="_blank"><img src="{r["id"]}-candidate.png" alt="Current skill output"></a><figcaption>Luna + current skill</figcaption></figure></div><div class="body"><p>{html.escape(r["comparison"]["overall_contrast"])}</p><p class="muted">In the blind critique, candidate = {r["candidate_side"]}. Labels above were revealed after judgment.</p><details><summary>Concrete design contrasts and raw blind view</summary><ul>{dimensions}</ul><a href="{r["id"]}-blind.png">View exact anonymous evidence board</a><pre>{html.escape(json.dumps(r["choices"],indent=2))}</pre></details></div></article>')
        sections.append(f'<section><h2>{names[family["task"].split("--")[0][-3:]]}</h2><p>Generated mean interval {family["generated_mean"]:.2f}–{family["generated_mean_upper"]:.2f}; original preferred in {family["reference_preferred"]}/3 comparisons.</p>{"".join(cards)}</section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Curated SVG art direction</title><style>*{box-sizing:border-box}body{margin:0;background:#eef1f5;color:#192536;font:16px/1.5 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:30px 22px}h1{font-size:38px;line-height:1.15}h2{margin-top:46px}h3{margin:0}article{background:white;border-radius:14px;border:1px solid #dce2eb;margin:20px 0;overflow:hidden}header,.body{padding:20px 26px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px;padding:0 24px}figure{margin:0}img{display:block;width:100%;height:360px;object-fit:contain}figcaption{text-align:center;color:#5d6e83;font-size:14px}a{color:#1554a0}summary{cursor:pointer}.notice{padding:18px;background:#fff;border-left:4px solid #7189a5}.muted{font-size:13px;color:#64758a}pre{white-space:pre-wrap;overflow-wrap:anywhere}li{margin:12px 0}@media(max-width:650px){.pair{grid-template-columns:1fr}img{height:290px}main{padding:18px 12px}}</style><main><h1>Art direction: curated references and current outputs</h1><p class="notice">The score measures artistic merit relative to a curated quality anchor, not geometric similarity. Matching the anchor's quality level is defined as 90; this is a scale convention, not a separately measured absolute score for purchased artwork. The critic sees anonymous A/B pairs; Jev makes the final typed judgments. This is public development calibration, not independent validation of skill improvement.</p>'''+f'<p>Mean current score: <b>{result["generated_mean"]:.2f}</b>. Original preferred in <b>{result["reference_preferred_of_18"]}/18</b> direct comparisons. <a href="../results.json">Full scores and checks</a></p>'+"".join(sections)+"</main></html>"
    page=page.replace(f'Mean current score: <b>{result["generated_mean"]:.2f}</b>.',f'Mean current quality interval: <b>{result["generated_mean_interval"][0]:.2f}–{result["generated_mean_interval"][1]:.2f}</b>. The optimization reward uses the lower bound, preserving the uncertainty.')
    page=page.replace('direct comparisons.',f'direct comparisons; {result["overall_unresolved_of_18"]} global preferences remain unresolved. Click an image to open its editable SVG.')
    (out/"index.html").write_text(page,encoding="utf-8")


if __name__=="__main__":main()
