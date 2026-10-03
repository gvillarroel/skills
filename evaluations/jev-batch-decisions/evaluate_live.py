#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate synthetic multi-document cases and independently score real Jev runs."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_case(root, name, job, inputs, execute):
    jobpath = root / "jobs" / (name + ".json")
    save(jobpath, job)
    output = root / "runs" / name
    report = execute(jobpath, inputs, output)
    decisions = rows(output / "decisions.jsonl")
    chunks = rows(output / "chunks.jsonl")
    plan = read(output / "plan.json")
    assert report["status"] == "complete" and len(decisions) == len(chunks) == plan["total_units"]
    assert len({x["id"] for x in decisions}) == len(decisions)
    assert {x["id"] for x in decisions} == {x["id"] for x in chunks}
    assert plan["max_map_request_bytes"] <= job.get("limits", {}).get("max_request_bytes", 24000)
    for source in plan["sources"]:
        path = Path(source["path"])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
        if path.suffix == ".md":
            pieces = [x for x in chunks if x["source_id"] == source["source_id"]]
            assert "".join(x["text"] for x in pieces) == path.read_text(encoding="utf-8")
    return report, decisions, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, default=Path("skills/jev-batch-decisions"))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str((args.skill / "scripts").resolve()))
    from jev_batch import execute

    fixtures = read(args.skill / "assets/examples/tickets.json")["cases"]
    template = read(args.skill / "assets/templates/job.json")
    template["questions"]["category"]["criteria"]["sales"] = "Pre-purchase questions, plan comparisons and quotations."
    template["questions"]["urgency"] = dict(type="score", instructions="Rate current operational impact, not emotional tone or words such as urgent.",
        criteria=["No current impact; informational or future planning request.",
                  "Minor inconvenience; normal work continues.",
                  "One user is blocked or has a billing issue; no widespread outage.",
                  "Important work blocked for a whole team.",
                  "Complete production outage for all customers, without a workaround."])
    template["reducers"]["urgency"] = "max"
    template["limits"].update(max_requests=300, chunk_chars=3000)
    input_dir = root / "inputs"
    input_dir.mkdir()
    ticket_file = input_dir / "support.csv"
    expected = []
    with ticket_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "message"])
        writer.writeheader()
        for repetition in range(3):
            for case in fixtures:
                writer.writerow(dict(id=f"{case['id']}-{repetition}", message=case["text"] + f"\nReference number: {repetition+100}."))
                expected.append(case)

    summary = {"date": "2026-09-18", "model": template["model"], "cases": [], "all_passed": True}
    outputs = {}
    for name, batch, concurrency in (("support-batch-parallel", 4, 4), ("support-single-sequential", 1, 1), ("support-batch-sequential", 4, 1)):
        job = copy.deepcopy(template)
        job["limits"].update(batch_items=batch, concurrency=concurrency)
        report, decisions, output = run_case(root, name, job, [ticket_file], execute)
        checks = []
        for row, golden in zip(decisions, expected):
            raw = row["decisions"]
            checks.append(dict(id=row["id"], category=raw["category"]["raw"]["choice"] == golden["category"],
                               refund=raw["refund"]["value"] == golden["refund"],
                               urgency=abs(raw["urgency"]["raw"]["score"]-golden["urgency"]) <= 0.65))
        passed = all(all(x[k] for k in ("category", "refund", "urgency")) for x in checks)
        result = dict(name=name, passed=passed, records=len(decisions), checks=checks, report=report)
        summary["cases"].append(result)
        outputs[name] = decisions
        print(json.dumps(dict(case=name, passed=passed, calls=report["metrics"]["http_attempts"], seconds=report["elapsed_seconds"])), flush=True)
        before = (output/"decisions.jsonl").read_bytes()
        resumed = execute(root/"jobs"/(name+".json"), [ticket_file], output, resume=True)
        assert resumed["metrics"]["http_attempts"] == report["metrics"]["http_attempts"]
        assert before == (output/"decisions.jsonl").read_bytes()
        result["resume_no_new_calls"] = True
        save(root/"evaluation.json", summary)

    reference = outputs["support-single-sequential"]
    agreement = []
    for name in ("support-batch-parallel", "support-batch-sequential"):
        values = outputs[name]
        agreement.append(dict(name=name, category_matches=sum(a["decisions"]["category"]["raw"]["choice"] == b["decisions"]["category"]["raw"]["choice"] for a,b in zip(values, reference)),
                              refund_matches=sum(a["decisions"]["refund"]["value"] == b["decisions"]["refund"]["value"] for a,b in zip(values, reference)), total=len(reference)))
    summary["batch_controls"] = agreement

    # One document alone exceeds a normal 32K context on ordinary English tokenization.
    # Actual token accounting is retained; byte size is never called a token count.
    doc_inputs = []
    for doc in range(4):
        paragraphs = []
        for section in range(660 if doc == 0 else 36):
            paragraph = (f"Operations journal {doc}, entry {section}. All work described in this entry is routine completed maintenance. "
                         "The equipment inventory lists spare cables, archived manuals, storage racks and completed inspection forms. "
                         "The routine checks are finished, production is operating normally, and no unresolved production incident is reported here. ")
            if doc in (0, 3) and section == (617 if doc == 0 else 28):
                paragraph = (f"Operations journal {doc}, entry {section}. A current production incident remains unresolved. "
                             "The payment gateway is unavailable and the on-call team has not restored it. "
                             "This entry explicitly reports an unresolved production incident, and subsequent routine entries do not resolve it.")
            paragraphs.append(paragraph)
        path = input_dir/f"operations-{doc}.md"
        path.write_text("\n\n".join(paragraphs), encoding="utf-8")
        doc_inputs.append(path)
    evidence = dict(version=1, model=template["model"], context="Each fragment is independent evidence. Routine maintenance does not imply an incident. A subsequent routine entry does not resolve an earlier explicit incident.",
                    questions={"incident": dict(type="noul", instructions="Does this fragment explicitly report at least one currently unresolved production incident?",
                                criteria={"true": "Explicit current unresolved production incident.", "false": "Only routine maintenance, normal operation, resolved incidents, or no such evidence."})},
                    reducers={"incident": "any"}, limits=dict(chunk_chars=2400, batch_items=4, concurrency=4, max_requests=200))
    report, decisions, output = run_case(root, "long-document-screening", evidence, doc_inputs, execute)
    aggregates = read(output/"aggregates.json")["groups"]
    assertions = [aggregates[f"s{i+1:04d}"]["incident"]["value"] == (i in (0,3)) for i in range(4)]
    result = dict(name="long-document-screening", passed=all(assertions), documents=4,
                  bytes=sum(p.stat().st_size for p in doc_inputs), largest_document_bytes=doc_inputs[0].stat().st_size,
                  source_checks=assertions, report=report)
    summary["cases"].append(result)
    print(json.dumps(dict(case=result["name"], passed=result["passed"], units=len(decisions))), flush=True)
    save(root/"evaluation.json", summary)

    # Independent complete-record score use case, including unequal final batch size.
    impact_file = input_dir / "service-impact.jsonl"
    impact_texts = ["No users are currently affected. All systems are healthy.",
                    "Exactly one user cannot use the application; all other users can work.",
                    "A whole team cannot do their work; other teams are unaffected.",
                    "The entire service is unavailable for every user."]
    impacts = [(i*3)%4 for i in range(25)]
    impact_file.write_text("\n".join(json.dumps(dict(id=f"incident-{i}", text=impact_texts[value])) for i,value in enumerate(impacts)), encoding="utf-8")
    rubric = dict(type="score", instructions="Rate only the current explicitly stated impact.", criteria=["No users affected", "One user affected", "A whole team affected", "Every user affected"])
    impact_job = dict(version=1, questions={"impact": rubric}, reducers={"impact": "mean"}, limits=dict(batch_items=4, concurrency=4))
    report, decisions, output = run_case(root, "incident-rubric-mean", impact_job, [impact_file], execute)
    score_checks = [abs(row["decisions"]["impact"]["raw"]["score"]-value) <= 0.35 for row,value in zip(decisions, impacts)]
    measured_mean = read(output/"aggregates.json")["groups"]["all"]["impact"]["value"]
    result = dict(name="incident-rubric-mean", passed=all(score_checks) and measured_mean is not None and abs(measured_mean-statistics.mean(impacts))<=0.15,
                  records=25, score_matches=sum(score_checks), expected_mean=statistics.mean(impacts), observed_mean=measured_mean, report=report)
    summary["cases"].append(result)
    print(json.dumps(dict(case=result["name"], passed=result["passed"], observed_mean=measured_mean)), flush=True)

    # Five documents require recursive typed decisions, with a late minority blocker.
    release_files = []
    for doc in range(5):
        paragraphs = []
        for section in range(9):
            condition = "Release is blocked by an unresolved critical defect." if doc == 4 and section == 7 else "Release is explicitly clear: all required checks passed and there are no blockers."
            paragraphs.append(f"Module {doc}, checklist section {section}. {condition} " +
                              "The checklist covers the current release of this module. The accompanying inventory describes configured storage, routine labels, tracked owners and test environments. " +
                              "Use the stated release status for this section; inventory details do not change that status.")
        path = input_dir/f"release-{doc}.md"
        path.write_text("\n\n".join(paragraphs), encoding="utf-8")
        release_files.append(path)
    choices = dict(blocked="An explicit unresolved blocker exists.", clear="Explicitly clear with all required checks passed.", unknown="Insufficient evidence, unknown or null status.")
    rule = "If any child release value is blocked, the aggregate is blocked. Otherwise any unknown or null makes it unknown. Otherwise all children are clear and the aggregate is clear. Apply identically at every level."
    tree_job = dict(version=1, context="Judge current release status only from the fragment's explicit statement.",
                    questions={"release": dict(type="choice", instructions="What release status is explicitly stated in this fragment?", criteria=choices)},
                    limits=dict(chunk_chars=650, batch_items=4, concurrency=4, max_requests=120),
                    reduce=dict(context=rule, fan_in=3, max_levels=8, questions={"release": dict(type="choice", instructions="Combine all child release values according to the exact aggregation rule.", criteria=choices)}))
    report, decisions, output = run_case(root, "recursive-release-review", tree_job, release_files, execute)
    final = read(output/"final.json")
    nodes = rows(output/"reduce-nodes.jsonl")
    known_ids = {x["id"] for x in decisions}
    for node in nodes:
        assert set(node["children"]) <= known_ids
        known_ids.add(node["id"])
    result = dict(name="recursive-release-review", passed=final["decisions"]["release"]["value"] == "blocked" and final["leaf_count"]==len(decisions) and final["level"] >= 3,
                  documents=5, reduce_nodes=len(nodes), levels=final["level"], final=final["decisions"], report=report)
    summary["cases"].append(result)
    print(json.dumps(dict(case=result["name"], passed=result["passed"], levels=final["level"])), flush=True)

    summary["all_passed"] = all(c["passed"] for c in summary["cases"])
    summary["total_reported_cost_usd"] = sum(c["report"]["metrics"]["reported_cost_usd"] for c in summary["cases"])
    summary["total_http_attempts"] = sum(c["report"]["metrics"]["http_attempts"] for c in summary["cases"])
    summary["total_reported_input_tokens"] = sum(c["report"]["metrics"]["reported_input_tokens"] for c in summary["cases"])
    save(root/"evaluation.json", summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ("cases", "batch_controls")}), flush=True)
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
