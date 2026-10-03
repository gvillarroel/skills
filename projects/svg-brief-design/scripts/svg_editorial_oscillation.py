#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Version 6.3: repair the unsupported periodicity requirement in one task family."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import shutil
import sys

from svg_excellence import REPO, encode, read, sha, write
from art_direction_review import verified_decisions
import svg_technique_observer as previous
import svg_technique_review as technique
import svg_technique_score as scoring
import svg_curated_pairs as observer

ROOT = REPO / "evaluations/runs/svg-technique-v6.3"
CONFIG = REPO / "projects/svg-brief-design/evaluation/technique-v6.3"


def prepare():
    ROOT.mkdir(exist_ok=False); CONFIG.mkdir(exist_ok=False)
    previous.lock_check("observation-lock.json")
    source = previous.ROOT
    coordinator = copy.deepcopy(read(source / "coordinator-only.json"))
    affected = []
    for pair in coordinator["pairs"]:
        if pair["profile"] == "vintage-print-diagram":
            if "oscilación periódica" not in pair["brief"]: raise ValueError("Expected brief mismatch absent")
            pair["prior_brief"] = pair["brief"]
            pair["brief"] = pair["brief"].replace("oscilación periódica","oscilación")
            affected.append(pair["id"])
    if len(affected)!=5: raise ValueError("Expected three trials, one crop and one order control")
    write(ROOT / "coordinator-only.json",coordinator)
    for name in ["job.json","observer-prompt.txt","use-profiles.json","generator-introductions.json"]:
        shutil.copy2(previous.CONFIG / name,CONFIG / name)
    protocol = copy.deepcopy(read(previous.CONFIG / "protocol.json"))
    protocol.update(version="6.3.0",new_visual_calls=5,new_jev_calls=5,retained_jev_cases=31,retries=0)
    protocol["reason_for_revision"] = "The user describes an editorial vintage artifact. Dataset authors introduced 'periodic', but the source has visibly unequal cycle widths. Remove only that unsupported requirement from the five instances of this family; retain oscillation, axes, reference letters, print character, all SVGs, all other tasks and the exact v6.1 Jev questions. This is a changed task contract, not rescoring a failed answer under the same prompt. Retain the scientific precision mismatch in v6.2."
    protocol["scope"] = "Public post-feedback task-contract repair under the stated editorial interpretation. Not independent validation or proof that a mathematically irregular wave is an accurate periodic plot."
    protocol["visual_evidence"] = "Five fresh same-image observations with the corrected brief. Inherit 27 unchanged image records plus four unchanged textual controls and their first accepted native Jev results. Never retry accepted semantics."
    protocol["external_recovery"] = "At most one predeclared replacement among the five new observations, solely for a terminated stream with incomplete JSON and no accepted comparison. Zero Jev retries. Maximum six new visual attempts and five new Jev calls. Preserve originals and exact-input provenance."
    protocol["brief_repair"] = {"family":"vintage-print-diagram","old":"oscilación periódica","new":"oscilación","reason":"The brief should request the actual editorial subject without inventing constant-period data fidelity.","generator_instruction_replacement_required":True}
    write(CONFIG / "protocol.json",protocol)
    inherited = []
    for path in sorted((source / "inputs").glob("*.jsonl")):
        if path.stem in affected: continue
        verified_decisions(source / "native" / path.stem,path)
        target = ROOT / "inputs" / path.name
        target.parent.mkdir(exist_ok=True);shutil.copy2(path,target)
        shutil.copytree(source / "native" / path.stem,ROOT / "native" / path.stem)
        inherited.append({"id":path.stem,"source_input":path.relative_to(REPO).as_posix(),"source_native":(source / "native" / path.stem).relative_to(REPO).as_posix(),"input_sha256":sha(path.read_bytes())})
    write(ROOT / "inheritance.json",{"source_version":"6.2.0","retained_native_cases":inherited,"new_case_ids":affected,"source_results_sha256":sha((source / "results.json").read_bytes())})
    files = [Path(__file__),Path(scoring.__file__),Path(observer.__file__),Path(technique.__file__),Path(previous.__file__),ROOT / "coordinator-only.json",ROOT / "inheritance.json",source / "results.json",*CONFIG.glob("*"),*sorted((ROOT / "inputs").glob("*.jsonl"))]
    files.extend(Path(p[s+"_render"]) for p in coordinator["pairs"] if p["id"] in affected for s in ("A","B"))
    write(ROOT / "observation-lock.json",{"files":{p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in files}})
    print("Sealed five corrected-family calls; retained 31 unchanged Jev results.")


def check():
    for relative,expected in read(ROOT / "observation-lock.json")["files"].items():
        if sha((REPO / relative).read_bytes())!=expected: raise ValueError("Frozen input drift")


def observe():
    check()
    write(ROOT / "observation-started.json",{"logical_calls":5,"external_replacements_max":1})
    ids = read(ROOT / "inheritance.json")["new_case_ids"]
    pairs = [p for p in read(ROOT / "coordinator-only.json")["pairs"] if p["id"] in ids]
    template = (CONFIG / "observer-prompt.txt").read_text(encoding="utf-8")+"\n\nUSE PROFILE:\n"+technique.PROFILES["vintage-print-diagram"]
    def one(pair):
        try:
            observer.observe_pair(pair,ROOT / "observations" / pair["id"],template)
            return {"id":pair["id"],"directory":"observations/"+pair["id"],"status":"complete"}
        except Exception as exc:
            return {"id":pair["id"],"status":"failed","error_type":type(exc).__name__}
    with ThreadPoolExecutor(max_workers=3) as pool: outcomes = list(pool.map(one,pairs))
    failures = [r for r in outcomes if r["status"]!="complete"]
    if len(failures)==1:
        row = failures[0]; directory = ROOT / "observations" / row["id"]
        receipt = read(directory / "receipt.json")
        events = [json.loads(line) for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        final = [e["message"] for e in events if e.get("type")=="message_end" and e.get("message",{}).get("role")=="assistant"][-1]
        text = "\n".join(x.get("text","") for x in final.get("content",[]) if x.get("type")=="text")
        incomplete = False
        try: json.loads(text)
        except json.JSONDecodeError: incomplete = True
        if not receipt["passed"] and not (directory / "comparison.json").exists() and final.get("stopReason")=="error" and final.get("errorMessage")=="terminated" and incomplete:
            replacement = ROOT / "recovery" / row["id"]
            write(ROOT / "external-recovery.json",{"id":row["id"],"reason":"Terminated stream with incomplete JSON; exact-input first-complete recovery","original_files":{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in directory.iterdir() if p.is_file()}})
            observer.observe_pair(next(p for p in pairs if p["id"]==row["id"]),replacement,template)
            if read(replacement / "input.json")!=read(directory / "input.json"): raise ValueError("Recovery input drift")
            row.update(status="complete",directory="recovery/"+row["id"],recovered=True)
    write(ROOT / "observation-execution.json",outcomes)
    if any(r["status"]!="complete" for r in outcomes): raise ValueError("Incomplete corrected-family evidence")
    print("Five corrected-family observations complete.")


def stage_and_score():
    check()
    outcomes = read(ROOT / "observation-execution.json")
    if len(outcomes)!=5 or any(r["status"]!="complete" for r in outcomes): raise ValueError("Incomplete observations")
    coordinator = read(ROOT / "coordinator-only.json")
    files = []; new_inputs = []
    for row in outcomes:
        pair = next(p for p in coordinator["pairs"] if p["id"]==row["id"])
        directory = ROOT / row["directory"]
        receipt = read(directory / "receipt.json")
        if not receipt["passed"] or receipt["image_sha256"]!=sha((directory / "image.png").read_bytes()): raise ValueError("Invalid visual receipt")
        record = technique.judge_record(row["id"],pair["brief"],read(directory / "comparison.json"),pair["profile"])
        source = ROOT / "inputs" / (row["id"]+".jsonl")
        source.write_bytes(encode(record)+b"\n");new_inputs.append(source)
        files.extend(directory / name for name in ["comparison.json","receipt.json","input.json","image.png","events.jsonl"])
    records = sorted((ROOT / "inputs").glob("*.jsonl"))
    if len(records)!=36: raise ValueError("Missing combined coverage")
    (ROOT / "records.jsonl").write_bytes(b"".join(p.read_bytes() for p in records))
    files.extend([ROOT / "observation-lock.json",ROOT / "records.jsonl",*records])
    old = read(ROOT / "observation-lock.json")["files"]
    write(ROOT / "pre-inference-lock.json",{"files":old | {p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in files}})
    sys.path.insert(0,str(REPO / "skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    from jev_transport import http_post
    from jev_contract import digest
    for source in new_inputs: execute(CONFIG / "job.json",[source],ROOT / "plans" / source.stem,dry_run=True)
    write(ROOT / "inference-started.json",{"new_calls":5,"retained_cases":31,"retries":0})
    def one(source):
        raw = ROOT / "raw" / source.stem;raw.mkdir(parents=True)
        def recorded(payload,key,timeout):
            status,headers,data = http_post(payload,key,timeout)
            if status==200: (raw / (digest(payload)+".json")).write_bytes(data)
            return status,headers,data
        execute(CONFIG / "job.json",[source],ROOT / "native" / source.stem,post=recorded)
    with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(one,new_inputs))
    scoring.ROOT = ROOT;scoring.CONFIG = CONFIG;scoring.report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument("mode",choices=["prepare","observe","score"]);args=parser.parse_args()
    {"prepare":prepare,"observe":observe,"score":stage_and_score}[args.mode]()
