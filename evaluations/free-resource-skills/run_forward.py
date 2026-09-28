#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run independent strict skill trials and preserve every attempt."""
import argparse
import concurrent.futures
import json
import subprocess
from pathlib import Path

SOURCES = {
    "polyhaven": ("polyhaven-asset-search", "deck.jpg", "sunset.hdr"),
    "ambientcg": ("ambientcg-material-search", "wood.zip", "brick.zip"),
    "pexels": ("pexels-media-search", "access.json", None),
    "iconify": ("iconify-icon-search", "house.svg", "search.svg"),
    "kenney": ("kenney-asset-search", "patterns.zip", "nature.zip"),
}


def trial(task):
    source, case, repetition, model, suffix = task
    skill, contract, generalization = SOURCES[source]
    outputs = []
    if case == "contract":
        outputs = ["artifacts/" + contract, "artifacts/review.md"]
        if source != "pexels": outputs.append("artifacts/" + contract + ".json")
    elif case == "naturalistic":
        outputs = (["artifacts/access.json", "artifacts/next-step.md"] if source == "pexels" else
                   ["artifacts/options.json", "artifacts/options.html", "artifacts/shortlist.md"])
    elif case == "generalization":
        outputs = ["artifacts/options.json", "artifacts/options.html", "artifacts/" + generalization,
                   "artifacts/" + generalization + ".json", "artifacts/review.md"]
        if source == "kenney": outputs.append("artifacts/license-only/extraction.json")
    elif case == "boundary":
        outputs = ["artifacts/reply.md"]
    run_id = f"free-{source}-{case}-20260927-{suffix}-{repetition}"
    argv = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill, "--prompt-file",
            f"evaluations/pi-prompts/free-resources-{source}-{case}.md", "--mode", "json", "--strict",
            "--model", model, "--run-id", run_id, "--timeout-seconds", "600"]
    for output in outputs: argv += ["--expect-output", output]
    if case == "contract": argv.append("--require-exact-command-from-prompt")
    r = subprocess.run(argv, capture_output=True, text=True, encoding="utf8", errors="replace")
    run = Path("evaluations/runs") / run_id
    run.mkdir(parents=True, exist_ok=True)
    (run / "launcher.stdout.txt").write_text(r.stdout, encoding="utf8")
    (run / "launcher.stderr.txt").write_text(r.stderr, encoding="utf8")
    result = {"run_id": run_id, "returncode": r.returncode, "command": argv, "required_outputs": outputs}
    print(json.dumps(result), flush=True)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", choices=["contract", "naturalistic", "generalization", "boundary"], required=True)
    p.add_argument("--source", choices=list(SOURCES), action="append")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--model", default="openai-codex/gpt-5.6-luna")
    p.add_argument("--suffix", default="luna")
    p.add_argument("--workers", type=int, default=2)
    a = p.parse_args()
    tasks = [(s, a.case, n, a.model, a.suffix) for s in (a.source or SOURCES) for n in range(1, a.repeat + 1)
             if not (a.case == "generalization" and s == "pexels")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        results = list(pool.map(trial, tasks))
    raise SystemExit(int(any(r["returncode"] for r in results)))


if __name__ == "__main__": main()
