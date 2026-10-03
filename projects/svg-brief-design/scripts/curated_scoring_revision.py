#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Freeze one uniform Jev question clarification; preserve failed v5 judgments."""
import copy
import json
import sys
from svg_excellence import REPO, read, sha, write
from svg_curated_pairs import ROOT, CONFIG, DIMENSIONS, aggregate
from art_direction_review import verified_decisions

REVISION=REPO/"projects/svg-brief-design/evaluation/art-direction-v5.1"


def main():
    decisions,models=verified_decisions(ROOT/"judgments/jev",ROOT/"judgments/records.jsonl")
    rows=[p|aggregate(decisions[p["id"]]["decisions"],p["candidate_side"]) for p in read(ROOT/"pairs-coordinator-only.json")]
    write(ROOT/"v5-failed-results.json",{"version":"5.0.0","passed":False,"reason":"One generated item abstained in shape rhythm despite interpretable evidence, and the wrong-subject control was classified as merely incomplete. No promotion or activation.","records":rows,"observed_models":models})
    REVISION.mkdir(exist_ok=False)
    job=copy.deepcopy(read(CONFIG/"job.json"))
    for key in [*DIMENSIONS,"overall"]:
        question=job["questions"][key]
        question["instructions"]+=" Different credible design approaches with no supported superiority are parity. A contrast need not identify a defect or winner to establish parity. Reserve unknown for missing, contradictory or uninterpretable evidence that prevents a comparison."
        question["criteria"]["unknown"]="The evidence is absent, contradictory or uninterpretable, preventing a comparison. This does not mean equal merit or two different legitimate styles; those are parity."
    for key in ["brief_A","brief_B"]:
        question=job["questions"][key]
        question["instructions"]+=" First establish whether the requested subject is present at all. A neutral elementary mark or an unrelated subject does not become the requested subject by sharing its color or general simplicity. Distinguish absence of the subject from an identifiable instance missing one essential part."
        question["criteria"]["major_missing"]="The requested subject is identifiable, but at least one essential part is missing."
        question["criteria"]["wrong"]="The requested subject is absent or replaced by an unrelated subject or a neutral elementary mark; matching color or cleanliness cannot satisfy the subject."
    write(REVISION/"job.json",job)
    protocol=read(CONFIG/"protocol.json")|{"version":"5.1.0","new_visual_calls":0,"maximum_jev_calls":32,"previous":"v5 preserved as failed. Clarify unknown versus parity and absent subject versus incomplete subject, uniformly for all records. No weights, score mapping, quality target or acceptance checks change.","visual_evidence_root":"evaluations/runs/svg-art-v5","input_records_sha256":sha((ROOT/"judgments/records.jsonl").read_bytes())}
    write(REVISION/"protocol.json",protocol)
    out=ROOT/"scoring-v5.1";out.mkdir(exist_ok=False)
    (out/"records.jsonl").write_bytes((ROOT/"judgments/records.jsonl").read_bytes())
    write(out/"pre-inference-lock.json",{"files":{p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in [Path(__file__),REVISION/"job.json",REVISION/"protocol.json",out/"records.jsonl"]},"prior_visual_lock_sha256":sha((ROOT/"pre-inference-lock.json").read_bytes()),"recovery_manifest_sha256":sha((ROOT/"recovery-manifest.json").read_bytes())})
    sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    execute(REVISION/"job.json",[out/"records.jsonl"],out/"jev")
    print("Completed uniform v5.1 Jev clarification on all 32 preserved comparisons.")


if __name__=="__main__":
    from pathlib import Path
    main()
