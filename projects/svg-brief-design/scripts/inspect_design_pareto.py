#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Reuse the native Pareto audit and frozen guards for the design study."""
import json
from pathlib import Path
import sys

import inspect_pareto_study as native_audit
from seal_technique_evolution import org, sha

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svt7"
native_audit.ROOT = ROOT


def guide_reads(arm):
    """Count observed guide reads, without extracting model reasoning."""
    counts = {}
    for path in sorted((ROOT / f"jobs/{arm}").glob("*/agent/pi.txt")):
        calls = []
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "tool_execution_start":
                calls.append(json.dumps(event.get("args", {})))
        counts[path.parent.parent.name] = {
            name: any(name in call for call in calls)
            for name in ["contour-counterform.md", "print-optical-finish.md"]
        }
    result = {"arm": arm, "trials": counts,
              "reads": {name: sum(row[name] for row in counts.values())
                        for name in ["contour-counterform.md", "print-optical-finish.md"]}}
    native_audit.put(ROOT / f"guide-reads-{arm}.json", result)
    print(json.dumps({"arm": arm, "guide_reads": result["reads"]}))


def close_empty_frontier(generation):
    """Close only a completed empty-frontier study; never release or install."""
    archive_path = ROOT / f"pareto/development/generation-{generation:03d}/pareto-archive.json"
    selection_path = ROOT / f"selection-g{generation}.json"
    archive = native_audit.read(archive_path)
    selection = native_audit.read(selection_path)
    assert not archive["archive"] and selection["selected"] is None
    assert not (ROOT / "pareto/holdout").exists()
    assert not (ROOT / "validation-release-ready.json").exists()
    repo = Path(__file__).resolve().parents[3]
    baseline_files = native_audit.read(ROOT / "input-b.json")["files"]
    for bundle in [ROOT / "inputs/b/svg-brief-design", repo / "skills/svg-brief-design", repo / ".agents/skills/svg-brief-design"]:
        assert {p.relative_to(bundle).as_posix(): sha(p) for p in sorted(bundle.rglob("*")) if p.is_file()} == baseline_files
    rows = []
    for record in archive["candidateResults"]:
        arm = record["candidateId"]
        audit = native_audit.read(ROOT / f"audit-{arm}.json")
        trials = native_audit.collect(ROOT / f"jobs/{arm}", 18)
        scored = [t for t in trials if not t["exception"] and t["reward"].get("artifact_valid") == 1 and t["overall"] is not None and "technique_quality" in t["reward"]]
        rows.append({"candidate": arm, "trials": len(trials), "jev_scored": len(scored),
                     "errors": audit["errors"], "provider_failures": len(audit["critic_provider_failures"]),
                     "observed_model": audit["observed_generator_aliases"],
                     "native_diagnostic_mean": record["summary"]["meanReward"],
                     "qualified": record["qualification"]["passed"], "harbor_digest": record["skillDigest"]})
    result = {"status": "no-qualified-pareto-candidate", "installed": False,
              "method": "harbor-reflective-pareto-search", "new_generator_calls": sum(r["trials"] for r in rows),
              "model": "openai-codex/gpt-6-luna", "thinking": "medium", "evaluator": "Jev 6.3 unchanged", "retries": 0,
              "candidates": rows, "generation": generation, "native_archive_sha256": sha(archive_path),
              "selection_sha256": sha(selection_path), "protocol_sha256": sha(ROOT / "protocol.json"),
              "research_sha256": native_audit.read(ROOT / "freeze-receipt.json")["research_sha256"],
              "private_gate_opened": False, "reserved_cohort_consumed": False, "reserved_family_count": 2,
              "canonical_and_local_unchanged": True,
              "unaffected_family_guards": {arm: value["unaffected_family_visual_guard"] for arm, value in selection["candidates"].items()},
              "limitation": "Native means include preserved execution-failure zeros. They are not pure visual grades. No qualified parent exists for a further generation. Private reserve remains unopened.",
              "cost": None}
    decision_path = ROOT / "final-decision.json"
    if decision_path.exists():
        # Permit continuation after a pre-ledger local report failure only when
        # the complete decision is byte-semantically unchanged.
        assert native_audit.read(decision_path) == result
    else:
        native_audit.put(decision_path, result)
    evidence = [("native-pareto", "evolution-report", "development", archive_path),
                ("selection", "decision", "development", selection_path),
                ("final-decision", "decision", "decision", ROOT / "final-decision.json"),
                ("reference-audit", "other", "diagnostic", ROOT / "public-reference-check.json"),
                ("contour-review", "other", "development", ROOT / "public-visual-review-g0.json"),
                ("print-review", "other", "development", ROOT / "public-print-review-g0.json")]
    for row in rows:
        arm = row["candidate"]
        evidence.extend([(f"job-{arm}", "native-job", "development", ROOT / f"jobs/{arm}"),
                         (f"input-{arm}", "candidate", "lineage", ROOT / f"inputs/{arm}/svg-brief-design")])
    for identity, kind, role, path in evidence:
        org("record-evidence", ROOT / "study", "--stage-id", "evolve", "--evidence-id", identity,
            "--kind", kind, "--role", role, "--visibility", "private", "--path", path)
    org("transition", ROOT / "study", "--stage-id", "evolve", "--status", "completed")
    org("transition", ROOT / "study", "--stage-id", "validate", "--status", "stopped",
        "--note", "Empty qualified Pareto frontier; no eligible parent or finalist. Unconsumed reserve preserved, canonical skill unchanged.")
    org("verify", ROOT / "study")
    destination = repo / "evaluations/svg-brief-design/design-craft-pareto-20260926.json"
    native_audit.put(destination, result)
    print(json.dumps({"closed": True, "attempts": result["new_generator_calls"], "installed": False, "private_gate_opened": False, "result": str(destination)}))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "status":
        native_audit.status()
    elif mode == "audit":
        native_audit.audit(sys.argv[2])
        guide_reads(sys.argv[2])
    elif mode == "decide":
        native_audit.decide(int(sys.argv[2]))
    elif mode == "close-empty":
        close_empty_frontier(int(sys.argv[2]))
    else:
        raise SystemExit("Unknown mode")
