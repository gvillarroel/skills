#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Use the preregistered single external-envelope replacement; retain all valid answers."""
import shutil
import sys
import svg_technique_review as review
from svg_excellence import REPO,read,sha,write


def main():
    root=review.ROOT;original=root/"jev";report=read(original/"report.json")
    if report["status"]!="failed" or report["error"]!="Choice is not a highest-probability option." or report["metrics"]["http_attempts"]!=6 or report["metrics"]["accepted_calls"]!=5:
        raise ValueError("Not the documented single response contract failure")
    prior={p.relative_to(original).as_posix():sha(p.read_bytes()) for p in original.rglob("*") if p.is_file()}
    write(root/"external-recovery.json",{"classification":"Provider choice disagrees with maximum probability, violating https://docs.typesafe.ai/primitives/choice#response-structure and the existing typed contract. The rejected envelope produced no accepted score.","policy":"Single replacement already declared before inference; five accepted checkpoints are reused and 30 previously unstarted cases execute once. No accepted semantic result is repeated.","max_new_http_calls":31,"max_total_http_calls":37,"original_files":prior})
    effective=root/"jev-effective";shutil.copytree(original,effective)
    sys.path.insert(0,str(REPO/"skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    from jev_contract import digest
    from jev_transport import http_post
    calls=0
    def recorded(payload,key,timeout):
        nonlocal calls
        calls+=1
        if calls>31:raise ValueError("Single recovery allowance exhausted")
        status,headers,data=http_post(payload,key,timeout)
        if status==200:
            with (effective/("provider-response-"+digest(payload)+".json")).open("xb") as f:f.write(data)
        return status,headers,data
    execute(review.CONFIG/"job.json",[root/"records.jsonl"],effective,resume=True,post=recorded)
    for relative,digest in prior.items():
        if sha((original/relative).read_bytes())!=digest:raise ValueError("Original failed evidence changed")
    write(root/"report-source.json",{"effective_directory":"jev-effective","original_failed_directory":"jev","same_job_and_input":True,"source_report_sha256":sha((effective/"report.json").read_bytes())})
    verified=review.verified_decisions
    def effective_decisions(native,records):
        if native!=original:raise ValueError("Unexpected report source")
        return verified(effective,records)
    # Only redirect the native artifact directory; the frozen scoring and gates stay unchanged.
    review.verified_decisions=effective_decisions
    review.report()


if __name__=="__main__":main()
