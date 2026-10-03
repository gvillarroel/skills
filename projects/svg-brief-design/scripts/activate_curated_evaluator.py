#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Activate only the calibrated bundle that passed the native identity control."""
import hashlib
import json
from pathlib import Path
import shutil

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO/"evaluations/runs/svg-art-v5"


def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def new(path,value):
    with path.open("x",encoding="utf-8") as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write("\n")


def main():
    result=read(ROOT/"results.json")
    if not result["passed"] or result["version"]!="5.2.0":raise ValueError("Uncalibrated evaluator")
    bundle=ROOT/"frozen/evaluator";lock=read(bundle/"lock.json")
    for path,expected in lock["files"].items():
        if sha(bundle/path)!=expected:raise ValueError("Frozen bundle changed")
    job=ROOT/"jobs/native-curated-v5.2-probe";native=read(job/"result.json")
    if native["stats"]["n_completed_trials"]!=1 or native["stats"]["n_errored_trials"] or native["stats"]["n_retries"]:raise ValueError("Native control did not pass")
    trial=next(job.glob("hud__*/verifier"));metrics=read(trial/"metrics.json")
    if metrics["score_interval_100"]!=[90,90] or metrics["review_recommended"]:raise ValueError("Identical visible artwork did not earn clear parity")
    if sha(trial/"candidate.png")!=sha(trial/"anchor.png"):raise ValueError("The intended visible-identity control differs")
    source=REPO/"skills/svg-brief-design";frozen=REPO/"evaluations/runs/svp3/inputs/q/svg-brief-design";installed=REPO/".agents/skills/svg-brief-design"
    skill_files={p.relative_to(frozen).as_posix():sha(p) for p in frozen.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    for relative,expected in skill_files.items():
        if sha(source/relative)!=expected or sha(installed/relative)!=expected:raise ValueError("Skill payload drift")
    active=REPO/"projects/svg-brief-design/evaluation/active-evaluator.json"
    prior=REPO/"projects/svg-brief-design/evaluation/art-direction-v5.2/previous-active-v3.json"
    if prior.exists():raise ValueError("Activation already recorded")
    shutil.copy2(active,prior)
    value={
        "version":"5.2.0","status":"active-development-calibration","primary_reward":"curated_design_quality",
        "reward_range":[0,1],"display_range":[0,100],"pass_threshold":.9,
        "pass_meaning":"Conservative weighted artistic merit reaches the curated anchor's quality level. This is not a universal quality measurement or independent skill promotion.",
        "anchor_level":90,"anchor_level_is_scale_convention":True,
        "evaluator_bundle":bundle.relative_to(REPO).as_posix(),"lock_sha256":sha(bundle/"lock.json"),
        "judge_model":"typesafe/jev-1.13","observed_judge_model":"typesafe/jev-1.13-20260917",
        "visual_observer_model":"openai-codex/gpt-6-astra","visual_observer_thinking":"high",
        "reference_similarity_used":False,"quality_anchor_used":True,
        "anchor_access":"Host verifier only. Purchased SVGs never enter skill payload or generator environment.",
        "harbor":{"import_path":"harbor_svg_curated:SvgCuratedVerifier","future_job":"evaluations/runs/svg-art-v5/future-job.json","future_baseline_job":"evaluations/runs/svg-art-v5/future-baseline-job.json","rewardKey":"curated_design_quality","requiredRewards":{"artifact_valid":1.0},"passThreshold":.9},
        "uncertainty":"Unknown artistic dimensions retain the full 50–100 point interval; reward is the lower bound, not an imputed grade. Unknown candidate subject yields no reward. Overall preference and confidence remain separate diagnostics.",
        "promotion_gate":"Do not automatically promote from this development score. Review any selected candidate with unresolved dimensions or global preference; require a disjoint untouched evaluation under the same task contract.",
        "scope":"Six public development families, 18 current outputs, curated anchors and controls; no baseline comparison under this new metric, no private cohort opened.",
        "report":"evaluations/svg-brief-design/art-direction-20260926.md",
    }
    active.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    new(ROOT/"activation.json",{"active_config_sha256":sha(active),"evaluator_lock_sha256":sha(bundle/"lock.json"),"native_result_sha256":sha(job/"result.json"),"unchanged_skill_files":skill_files,"previous_config_sha256":sha(prior),"visible_identity_control":True})
    reports=[REPO/"evaluations/runs/svg-art-v4/jev/report.json",REPO/"evaluations/runs/svg-art-v4/jev-pairs/report.json",ROOT/"judgments/jev/report.json",ROOT/"scoring-v5.1/jev-effective/report.json",trial/"jev/report.json"]
    costs=[read(p)["metrics"] for p in reports]
    receipt_paths=[* (REPO/"evaluations/runs/svg-art-v4/observations").glob("*/receipt.json"),*(ROOT/"observations").glob("*/receipt.json"),*(ROOT/"recovery").glob("*/receipt.json"),trial/"critic/receipt.json"]
    receipts=[read(p) for p in receipt_paths]
    accounting={"jev_http_attempts":sum(m["http_attempts"] for m in costs),"jev_accepted_calls":sum(m["accepted_calls"] for m in costs),"jev_reported_cost_usd":sum(m["reported_cost_usd"] for m in costs),"jev_reported_input_tokens":sum(m["reported_input_tokens"] for m in costs),"jev_reported_output_tokens":sum(m["reported_output_tokens"] for m in costs),"visual_observer_attempts":len(receipts),"visual_observer_completed":sum(r["passed"] for r in receipts),"visual_observer_reported_total_tokens":sum((r.get("usage") or {}).get("totalTokens",0) for r in receipts),"visual_observer_cost_usd":None,"cost_note":"Jev transport reports provider cost. Observer runs use the signed-in Codex account; zero cost fields do not establish zero economic cost. The terminated stream reports zero tokens despite partial text, so observer token accounting is incomplete.","deduplication":"The v5.1 effective report includes its two cached accepted calls and one rejected original call; the failed source report is not summed again."}
    new(ROOT/"accounting.json",accounting)
    compact={k:v for k,v in result.items() if k!="records"}|{"accounting":accounting,"skill_changed":False,"native_probe_reward":.9,"active_config_sha256":sha(active),"evaluator_lock_sha256":sha(bundle/"lock.json")}
    new(REPO/"evaluations/svg-brief-design/art-direction-20260926.json",compact)
    print(json.dumps({"activated":"5.2.0","skill_files_unchanged":len(skill_files),"accounting":accounting},indent=2))


if __name__=="__main__":main()
