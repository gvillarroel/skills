#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run: uv run --script evaluations/contracts/summarize-hyperframes-composer.py --output <summary.json>."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def main():
    parser = argparse.ArgumentParser(description="Retain every composer development and release attempt.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    runs, groups = [], {}
    for folder in sorted((ROOT / "evaluations/runs").glob("20261002-hyperframes-composer-*-luna6-*")):
        manifest, strict = read(folder / "run-manifest.json"), read(folder / "evaluation-result.json")
        if manifest is None or strict is None:
            continue
        events = read(folder / "event-check.json") or {}
        independent, manual = read(folder / "independent.json"), read(folder / "manual.json")
        case = next(kind for kind in ["contract", "boundary", "reference", "vehicle", "inlet"]
                    if f"-{kind}-" in folder.name)
        cohort = "release-v3" if "-v3-" in folder.name else "development-v2"
        observed = events.get("observedModels", [])
        confirmed_model = observed == [{"provider": "openai-codex", "model": "gpt-6-luna"}]
        joint = bool(strict["passed"] and confirmed_model and independent and independent["ok"]
                     and manual and manual.get("ok"))
        if joint:
            classification = "pass"
        elif not strict["passed"]:
            classification = "agent-workflow" if not strict["gates"].get("events") else "agent-output"
        elif independent and not independent["ok"]:
            classification = "visual-semantic" if case == "inlet" else "independent-contract"
        elif manual and not manual.get("ok"):
            classification = "visual-semantic"
        else:
            classification = "review-pending"
        run = {"id": folder.name, "cohort": cohort, "case": case, "payload": manifest["skill"],
               "requestedModel": manifest["pi"]["model"], "observedModels": observed,
               "thinking": manifest["pi"]["thinking"], "strict": strict,
               "failureClassification": classification, "toolFindings": events.get("findings", []),
               "readPaths": sorted({call["path"] for call in events.get("calls", [])
                                    if call.get("path") is not None}),
               "independent": None if independent is None else
                   {"ok": independent["ok"], "findings": independent.get("findings", [])},
               "manual": manual, "jointPass": joint,
               "evidenceDirectory": folder.relative_to(ROOT).as_posix()}
        runs.append(run)
        key = (cohort, case, manifest["skill"]["payloadSha256"])
        group = groups.setdefault(key, {"cohort": cohort, "case": case, "payloadSha256": key[2],
                                       "runs": [], "strictPasses": 0, "independentPasses": 0,
                                       "manualPasses": 0, "jointPasses": 0})
        group["runs"].append(folder.name)
        group["strictPasses"] += int(strict["passed"])
        group["independentPasses"] += int(bool(independent and independent["ok"]))
        group["manualPasses"] += int(bool(manual and manual.get("ok")))
        group["jointPasses"] += int(joint)

    for group in groups.values():
        required = 1 if group["case"] in ["contract", "boundary"] else 2
        expected = 1 if group["case"] in ["contract", "boundary"] else 3
        group["thresholdPassed"] = len(group["runs"]) == expected and group["jointPasses"] >= required
    release = [group for group in groups.values() if group["cohort"] == "release-v3"]
    qualified = len(release) == 5 and len({group["payloadSha256"] for group in release}) == 1 \
        and all(group["thresholdPassed"] for group in release)
    report = {"schemaVersion": 1, "date": "2026-10-02", "skill": "hyperframes-explainer",
              "modelPolicy": "Develop with observed gpt-6.1-sol; forward-test with observed gpt-6-luna.",
              "attempts": len(runs), "releaseQualified": qualified,
              "cohorts": list(groups.values()), "runs": runs,
              "evidencePolicy": "Keep failures; require joint strict, independent and manual success on one frozen runtime bundle."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "attempts": len(runs), "releaseQualified": qualified,
                      "cohorts": list(groups.values())}))


if __name__ == "__main__":
    main()
