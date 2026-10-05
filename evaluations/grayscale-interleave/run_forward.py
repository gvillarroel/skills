#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run bounded frozen-payload palette-key cohorts; retain every dispatch."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import subprocess
import hashlib
import collect_acceptance

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="r1")
    parser.add_argument("--skills", nargs="*")
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--cases", default="cases.json")
    parser.add_argument("--family", choices=["all", "contract", "naturalistic"], default="all")
    args = parser.parse_args()
    cases = json.loads((HERE / args.cases).read_bytes())
    selected = [skill for skill in cases if (not args.skills or skill in args.skills) and skill not in args.exclude]
    logs = ROOT / "projects/grayscale-interleave/artifacts/reviews/forward"
    logs.mkdir(parents=True, exist_ok=True)
    if not 1 <= args.jobs <= 6:
        raise SystemExit("Use between one and six simultaneous lightweight cohorts.")
    families = [name for name in ("contract", "naturalistic") if args.family in ("all", name)]
    for skill in selected:
        if args.revision == "r4":
            config = cases[skill]
            if config["naturalistic"].get("caseFamily") != "gray-prefix" or config["naturalistic"].get("categoryCount") != 13:
                raise SystemExit("Revision r4 requires the frozen thirteen-category prefix cases.")
            current = collect_acceptance.digest(collect_acceptance.inventory(ROOT / "skills" / skill))
            if current != config["frozenNormalizedPayloadSha256"]:
                raise SystemExit(f"Runtime source changed after prefix freeze: {skill}")
            prompt = (HERE / config["naturalistic"]["prompt"]).read_text(encoding="utf-8")
            if hashlib.sha256(prompt.encode()).hexdigest() != config["naturalistic"]["promptSha256"]:
                raise SystemExit(f"Prefix prompt changed after freeze: {skill}")
        if (logs / f"{args.revision}-{skill}.json").exists():
            raise SystemExit(f"Preserve the previous dispatch summary; use a fresh revision: {skill}")
        for family in families:
            for repeat in range(1, cases[skill][family]["repetitions"] + 1):
                run_id = f"gray-20261005-{args.revision}-{skill}-{family}-{repeat}"
                if (ROOT / "evaluations/runs" / run_id).exists() or (logs / f"{run_id}.log").exists():
                    raise SystemExit(f"Preserve the previous attempt; use a fresh revision: {run_id}")

    def cohort(skill):
        rows = []
        for family in ("contract", "naturalistic"):
            if args.family != "all" and args.family != family:
                continue
            item = cases[skill][family]
            for repeat in range(1, item["repetitions"] + 1):
                run_id = f"gray-20261005-{args.revision}-{skill}-{family}-{repeat}"
                command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill,
                           "--prompt-file", str((HERE / item["prompt"]).relative_to(ROOT)),
                           "--model", cases[skill]["model"], "--thinking", "medium",
                           "--mode", "json", "--strict", "--run-id", run_id, "--timeout-seconds", "300"]
                if family == 'contract':
                    command.append('--require-exact-command-from-prompt')
                for output in item["outputs"]:
                    command.extend(["--expect-output", output])
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
                (logs / f"{run_id}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
                row = {"skill": skill, "family": family, "repeat": repeat, "runId": run_id,
                       "returnCode": result.returncode, "command": command}
                rows.append(row)
                (logs / f"{args.revision}-{skill}.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
                print(json.dumps({k: row[k] for k in ("skill", "family", "repeat", "returnCode")}), flush=True)
        return rows

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(cohort, selected))


if __name__ == "__main__":
    main()
