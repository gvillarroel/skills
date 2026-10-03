#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""One explicit post-failure development amendment for a terminated visual stream."""
import argparse
import json
from pathlib import Path
import sys

from svg_excellence import REPO, encode, read, sha, write
import svg_technique_observer as review
import svg_technique_review as technique
import svg_curated_pairs as observer

IDENTITY = "d97f5ab71e4b937b51b2"


def recover():
    root = review.ROOT
    review.lock_check("observation-lock.json")
    original = root / "observations" / IDENTITY
    receipt = read(original / "receipt.json")
    events = [json.loads(line) for line in (original / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    final = [e["message"] for e in events if e.get("type")=="message_end" and e.get("message",{}).get("role")=="assistant"][-1]
    if receipt["passed"] or (original / "comparison.json").exists() or final.get("stopReason")!="error" or final.get("errorMessage")!="terminated":
        raise ValueError("Not the independently evidenced terminated stream")
    partial = "\n".join(c.get("text","") for c in final.get("content",[]) if c.get("type")=="text")
    try:
        json.loads(partial)
    except json.JSONDecodeError:
        pass
    else:
        raise ValueError("Complete semantic result exists; do not repeat")
    files = {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    write(root / "external-observation-amendment.json",{
        "status":"post-failure exploratory-development protocol amendment",
        "original_budget":{"visual_calls":32,"retries":0},
        "amended_budget":{"visual_calls_max":33,"replacement_calls_max":1,"semantic_retries":0},
        "identity":IDENTITY,
        "reason":"Observed image stream stopped with errorMessage=terminated and incomplete JSON. No complete observation or judgment exists. Preserve the failed stream and make one exact-input replacement for the first evaluable observation. This exception was NOT preregistered; report the deviation.",
        "first_attempt_files":files,"replacement_path":"recovery/"+IDENTITY,
        "policy":"No second replacement, no repetition of successful observations, no change to images, prompt, model, thresholds or accepted semantics.",
    })
    pair = next(p for p in read(root / "coordinator-only.json")["pairs"] if p["id"]==IDENTITY)
    template = review.PROMPT + "\n\nUSE PROFILE:\n" + technique.PROFILES[pair["profile"]]
    replacement = root / "recovery" / IDENTITY
    observer.observe_pair(pair,replacement,template)
    if read(replacement / "input.json") != read(original / "input.json"):
        raise ValueError("Replacement input differs")
    for relative,expected in files.items():
        if sha((root / relative).read_bytes()) != expected: raise ValueError("Failed evidence changed")
    print("First complete observation recovered; original stream retained unchanged.")


def stage():
    root = review.ROOT
    review.lock_check("observation-lock.json")
    amendment = read(root / "external-observation-amendment.json")
    execution = read(root / "observation-execution.json")
    if [r["id"] for r in execution if r["status"]!="complete"] != [IDENTITY]:
        raise ValueError("The single permitted replacement does not cover all failures")
    for relative,expected in amendment["first_attempt_files"].items():
        if sha((root / relative).read_bytes()) != expected: raise ValueError("Original evidence drift")
    records = []; observation_files = []
    for pair in read(root / "coordinator-only.json")["pairs"]:
        directory = root / ("recovery" if pair["id"]==IDENTITY else "observations") / pair["id"]
        receipt = read(directory / "receipt.json")
        if not receipt["passed"] or not receipt["image_seen"] or receipt["image_sha256"]!=sha((directory / "image.png").read_bytes()):
            raise ValueError("Incomplete image evidence")
        records.append(technique.judge_record(pair["id"],pair["brief"],read(directory / "comparison.json"),pair["profile"]))
        observation_files.extend(directory / name for name in ["comparison.json","receipt.json","input.json","image.png","events.jsonl"])
    records.extend(r for r,_ in technique.semantic_controls())
    with (root / "records.jsonl").open("xb") as stream:
        for record in sorted(records,key=lambda r:r["id"]): stream.write(encode(record)+b"\n")
    sys.path.insert(0,str(REPO / "skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    for record in records:
        source = root / "inputs" / (record["id"]+".jsonl")
        source.parent.mkdir(exist_ok=True);source.write_bytes(encode(record)+b"\n")
        execute(review.CONFIG / "job.json",[source],root / "plans" / record["id"],dry_run=True)
    files = [Path(__file__),root / "external-observation-amendment.json",root / "observation-lock.json",root / "records.jsonl",*sorted((root / "inputs").glob("*.jsonl")),*observation_files]
    old = read(root / "observation-lock.json")["files"]
    write(root / "pre-inference-lock.json",{"files":old | {p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in files},"protocol_deviation":"One exact-input external replacement after a terminated incomplete stream; see preserved amendment."})
    print("Sealed 32 first-complete observations and four text controls; 33 visual attempts accounted for.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=["recover","stage"]);a=p.parse_args()
    {"recover":recover,"stage":stage}[a.mode]()
