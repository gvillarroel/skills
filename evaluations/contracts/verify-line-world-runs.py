#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently grade the frozen V2 outputs and summarize exact runtime reads."""
import json
import importlib.util
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="v2", choices=("v2", "v3", "clean"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("harness", ROOT / "scripts/run-pi-skill-eval.py")
    harness_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness_module)
    current_payload = harness_module.snapshot_tree(ROOT / "skills/line-world-video")
    results = []
    ids = ["contract-sol-1", "boundary-sol-1", *[f"naturalistic-sol-{i}" for i in (1, 2, 3)], *[f"generalization-sol-{i}" for i in (1, 2, 3)]]
    for case in ids:
        run = ROOT / "evaluations/runs" / ("20261114-line-world-" + args.version + "-" + case)
        work = run / "workspace"
        harness = read(run / "evaluation-result.json")
        trace = subprocess.run(["uv", "run", "--script", str(ROOT / "scripts/summarize-pi-json-events.py"), str(run / "events.jsonl"), "--output", str(run / "read-surface.json"), "--require-model", "gpt-6.1-sol", "--fail-on-invalid-json", "--fail-on-tool-error", "--require-tool-call", "--require-read", "../prompt.md", "--forbid-read-regex", r"(?i)(?:^|[\\/])assets[\\/]examples(?:[\\/]|$)"], capture_output=True, text=True)
        checks = {"strictHarness": harness["passed"], "trace": trace.returncode == 0, "currentPayloadMatches": harness_module.snapshot_tree(work / "skills/line-world-video") == current_payload}
        prefix = "lab-film" if case.startswith("generalization") else "boundary-film" if case.startswith("boundary") else "film"
        story, timing = read(work / prefix / "story.json"), read(work / prefix / "timing.json")
        if args.version == "clean":
            checks["titlesRequireAnExplicitRequest"] = not story.get("presentation", {}).get("contextLabels", {})
        beats = timing["beats"]
        checks["contiguous"] = beats[0]["start"] == 0 and all(a["end"] == b["start"] for a, b in zip(beats, beats[1:])) and beats[-1]["end"] == timing["duration"]
        checks["focusData"] = {f["rowId"]: (f["before"], f["after"]) for f in timing["focusWindows"]} == {r["id"]: (r["before"], r["after"]) for r in story["rows"]}
        if case.startswith("contract"):
            checks["contract"] = timing["duration"] == 56 and len(story["rows"]) == 4 and story["palette"] == "colorset1" and read(work / "check.json")["pass"]
        elif case.startswith("boundary"):
            report = read(work / "boundary-report.json")
            checks["invalidInputsRejected"] = len(report["cases"]) == 4 and all(c["rejected"] and (c.get("timingManifestUnchanged") is True or (c.get("timingUnchangedAfterValidation") is True and c.get("timingUnchangedAfterBuild") is True)) for c in report["cases"]) and report["validStoryRestored"] and report["pass"]
        else:
            audit = read(work / ("lab-review" if prefix == "lab-film" else "review") / "audit.json")
            checks["actualBrowserAudit"] = audit["ok"] and not audit["findings"] and len(audit["samples"]) >= 16 and audit["d3Version"] == "7.9.0" and all(Path(s["path"]).is_file() for s in audit["samples"])
            if prefix == "lab-film":
                expected = [("alpha", "Alpha", 9, 6, [9, 8, 7, 6]), ("beta", "Beta", 7, 4, [7, 6, 5, 4]), ("gamma", "Gamma", 12, 8, [12, 11, 9, 8])]
                checks["newData"] = [(r["id"], r["label"], r["before"], r["after"], r["trend"]) for r in story["rows"]] == expected
                checks["newTiming"] = timing["duration"] == 35 and [b["duration"] for b in beats] == [3, 3, 2, 11, 7, 5, 4]
                checks["newUnits"] = story["unit"] == "hours" and story["palette"] == "colorset2" and bool(story["paletteReason"])
            else:
                checks["requestedRetime"] = timing["duration"] == 60 and story["timing"]["compare"] == 18 and story["palette"] == "colorset1"
        result = {"case": case, "ok": all(checks.values()), "checks": checks}
        results.append(result)
        (run / "independent-check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    report = {"ok": all(r["ok"] for r in results), "passed": sum(r["ok"] for r in results), "total": len(results), "model": "openai-codex/gpt-6.1-sol", "results": results}
    target = ROOT / "evaluations/line-world-video" / (args.version + "-results.json")
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
