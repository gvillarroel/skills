#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit frozen SVG jobs and apply declared guards to native Pareto records.

Native Harbor/Pareto remain authoritative for rewards, case means, qualification,
and archive membership. This report does not rescore outputs or repair trials.
"""
import json
from pathlib import Path
import statistics
import sys

from inspect_technique_evolution import collect, describe, sha

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt6"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def put(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def status():
    result = {}
    for job in sorted((ROOT / "jobs").glob("*")):
        if not job.is_dir():
            continue
        rows = collect(job)
        result[job.name] = {"completed": len(rows), "errors": sum(bool(r["exception"]) for r in rows),
            "finished": bool(read(job / "result.json").get("finished_at")) if (job / "result.json").exists() else False}
    print(json.dumps(result))


def audit(arm):
    rows = collect(ROOT / f"jobs/{arm}", 18)
    observed, failures, critic_failures = set(), [], []
    information_reads = proof_calls = 0
    for row in rows:
        trace = ROOT / f"jobs/{arm}" / row["trial"] / "agent/pi.txt"
        commands = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
                observed.add(event["message"].get("model"))
            if event.get("type") == "tool_execution_start":
                commands.append(json.dumps(event.get("args", {})))
            if event.get("type") == "tool_execution_end" and event.get("isError"):
                messages = event.get("result", {}).get("content", [])
                text = "\n".join(m.get("text", "") for m in messages if m.get("type") == "text")
                failures.append({"trial": row["trial"], "tool": event.get("toolName"), "message": text[:2000]})
        information_reads += any("information-editing.md" in c for c in commands)
        proof_calls += any("scripts/proof_svg.py" in c for c in commands)
        critic_events = trace.parent.parent / "verifier/critic/events.jsonl"
        if critic_events.exists():
            for line in critic_events.read_text(encoding="utf-8").splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                message = event.get("message", {})
                if event.get("type") == "message_end" and message.get("role") == "assistant" and message.get("stopReason") in {"error", "aborted"}:
                    critic_failures.append({"trial": row["trial"], "model": message.get("model"),
                        "message": str(message.get("errorMessage", ""))[:1000], "event_file_sha256": sha(critic_events)})
    assert observed == {"gpt-6-luna"}, observed
    assert all(r["input_isolated"] for r in rows)
    assert all(r["skill_unchanged"] for r in rows if not r["exception"])
    seal = read(ROOT / f"input-{arm}.json")
    skill = ROOT / f"inputs/{arm}/svg-brief-design"
    assert seal["files"] == {p.relative_to(skill).as_posix(): sha(p) for p in sorted(skill.rglob("*")) if p.is_file()}
    result = {"arm": arm, "trials": 18, "observed_generator_aliases": sorted(observed),
        "input_isolation_and_integrity": all(r["input_isolated"] and r["skill_unchanged"] for r in rows),
        "input_isolated_trials": sum(r["input_isolated"] for r in rows),
        "skill_integrity_receipts": sum(r["skill_unchanged"] for r in rows),
        "errors": sum(bool(r["exception"]) for r in rows),
        "error_types": [{"trial": r["trial"], "type": r["exception"]["exception_type"], "message": r["exception"]["exception_message"][:500]} for r in rows if r["exception"]],
        "tool_failures": failures, "critic_provider_failures": critic_failures,
        "information_guide_reads": information_reads, "proof_helper_calls": proof_calls,
        "preview_reads": sum(r["preview_reads"] > 0 for r in rows), "scaffold_calls": sum(r["scaffold_used"] for r in rows)}
    put(ROOT / f"audit-{arm}.json", result)
    print(json.dumps(result))


def decide(generation):
    path = ROOT / f"pareto/development/generation-{generation:03d}/pareto-archive.json"
    native = read(path)
    assert native["promotionEligibleProfile"]
    records = {r["candidateId"]: r for r in native["candidateResults"]}
    assert all(r["promotionEligibleProvenance"] for r in records.values())
    baseline = records["b"]
    baseline_cases = {c["taskName"]: c for c in baseline["cases"]}
    complete = {t["taskName"] for t in baseline["trials"]}
    complete -= {t["taskName"] for t in baseline["trials"] if not t["qualificationPassed"]}
    # An error is attributable only after its saved concrete tool output matches
    # an ordinary agent-side command/argument/artifact mistake. No external error
    # is silently interpreted as zero here; native records remain unchanged.
    audit_b = read(ROOT / "audit-b.json")
    known = ["Cannot build scaffold:", "Cannot render SVG: SVG renders empty", "command not found",
             "must have required properties content", "must have required properties path, content", "ENOENT: no such file or directory, access '/harbor/skills/svg-brief-design/references/",
             "ls: cannot access '/logs/artifacts/", "SyntaxError:", "NameError:", "IndentationError:"]
    attributable = all(any(text in failure["message"] for text in known) for failure in audit_b["tool_failures"])
    failures_have_outputs = {t["trialName"] for t in baseline["trials"] if t["error"]} <= {f["trial"] for f in audit_b["tool_failures"]}
    baseline_usable = baseline["evaluable"] and attributable and failures_have_outputs and len(complete) >= 3
    archive_ids = {a["candidateId"] for a in native["archive"]}
    conclusions = {}
    rows_b = collect(ROOT / "jobs/b", 18)
    for arm, record in records.items():
        if arm == "b":
            continue
        cases = {c["taskName"]: c for c in record["cases"]}
        all_numeric = all(isinstance(c["meanReward"], (int, float)) and isinstance(baseline_cases[k]["meanReward"], (int,float)) for k,c in cases.items())
        families = {k: {"baseline": baseline_cases[k]["meanReward"], "candidate": c["meanReward"],
                       "delta": c["meanReward"] - baseline_cases[k]["meanReward"] if all_numeric else None} for k,c in cases.items()}
        rows_c = collect(ROOT / f"jobs/{arm}", 18)
        guard = describe([r for r in rows_b if r["task"] in complete], [r for r in rows_c if r["task"] in complete])
        deltas = [f["delta"] for f in families.values()] if all_numeric else []
        gain = statistics.mean(deltas) if deltas else None
        eligible = bool(baseline_usable and arm in archive_ids and record["qualification"]["passed"] and
                        gain is not None and gain >= .02 and min(deltas) >= -.08 and guard["passed"])
        conclusions[arm] = {"native_mean": record["summary"]["meanReward"], "archive_member": arm in archive_ids,
            "native_qualified": record["qualification"]["passed"], "baseline_usable": baseline_usable,
            "native_mean_gain": gain, "families": families, "unaffected_family_visual_guard": guard, "eligible": eligible}
        destination = ROOT / f"decision-{arm}.json"
        if not destination.exists():
            put(destination, {"comparison": {"families": families, "passed": eligible}, "trial_audit": {"b": rows_b, arm: rows_c},
                "native_archive": str(path), "native_archive_sha256": sha(path),
                "note": "Native error-derived zeros remain execution failures; they are not invented Jev judgments. Guard uses all completely valid baseline families."})
    eligible = [arm for arm, c in conclusions.items() if c["eligible"]]
    eligible.sort(key=lambda arm: (-records[arm]["summary"]["meanReward"], records[arm]["skillLines"], arm))
    result = {"native_archive": str(path), "native_archive_sha256": sha(path), "generation": generation,
              "baseline_complete_families": len(complete), "baseline_usable": baseline_usable,
              "candidates": conclusions, "selected": eligible[0] if eligible else None, "validation_opened": False}
    put(ROOT / f"selection-g{generation}.json", result)
    print(json.dumps({"generation": generation, "archive": sorted(archive_ids), "selected": result["selected"],
        "candidates": {arm: {k:v for k,v in c.items() if k not in {"families", "unaffected_family_visual_guard"}} for arm,c in conclusions.items()}}, indent=2))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "status": status()
    elif mode == "audit": audit(sys.argv[2])
    elif mode == "decide": decide(int(sys.argv[2]))
    else: raise SystemExit("Unknown mode")
