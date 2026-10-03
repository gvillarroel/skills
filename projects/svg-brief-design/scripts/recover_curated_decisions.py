#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Resume only an invalid provider envelope and unstarted decisions, preserving caches."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO/"evaluations/runs/svg-art-v5/scoring-v5.1"
sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
from jev_batch import execute
from jev_contract import encode,digest
from jev_transport import http_post


def main():
    original=ROOT/"jev";report=json.loads((original/"report.json").read_text())
    if report["status"]!="failed" or report["error"]!="Choice is not a highest-probability option." or report["metrics"]["http_attempts"]!=3 or report["metrics"]["accepted_calls"]!=2:
        raise ValueError("Not the documented provider contract failure")
    files={p.relative_to(original).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in original.rglob("*") if p.is_file()}
    amendment={"version":1,"classification":"HTTP 200 decision envelope rejected by the existing typed-contract validator; selected choice disagrees with reported maximum probability. No score from the rejected response is accepted.","preserve":"Two accepted checkpoints and all prior artifacts. First valid response only; no semantic-result retries.","original_files":files,"additional_call_allowance":1,"total_call_limit":33,"new_http_call_limit":30}
    with (ROOT/"provider-recovery-amendment.json").open("xb") as f:f.write(encode(amendment)+b"\n")
    effective=ROOT/"jev-effective";shutil.copytree(original,effective)
    calls=0
    def recorded_post(payload,key,timeout):
        nonlocal calls
        calls+=1
        if calls>30:raise ValueError("One external replacement plus 29 unstarted calls exhausted")
        status,headers,data=http_post(payload,key,timeout)
        if status==200:
            path=effective/("provider-response-"+digest(payload)+".json")
            with path.open("xb") as f:f.write(data)
        return status,headers,data
    execute(REPO/"projects/svg-brief-design/evaluation/art-direction-v5.1/job.json",[ROOT/"records.jsonl"],effective,resume=True,post=recorded_post)
    for path,expected in files.items():
        if hashlib.sha256((original/path).read_bytes()).hexdigest()!=expected:raise ValueError("Original evidence drift")
    print("Completed unchanged Jev job with two cached answers, one invalid-envelope replacement and 29 first calls.")


if __name__=="__main__":main()
