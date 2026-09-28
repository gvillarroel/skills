#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a bounded metadata routing control without forcing any skill."""

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("pi_harness", root / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    if not harness.SAFE_RUN_ID_RE.fullmatch(args.run_id):
        parser.error("Invalid run ID.")
    run = root / "evaluations/runs" / args.run_id
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    metadata = {}
    for name in ("destockd-video-search", "video", "pixel-art-image-video"):
        header = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        metadata[name] = next(line.split(":", 1)[1].strip() for line in header.splitlines() if line.startswith("description:"))
    questions = {
        "q1": "Find Destockd archival shots of a factory and show a preview shortlist.",
        "q2": "From the Destockd list you just showed, download option 3.",
        "q3": "Browse Destockd's animation collection and find similar shots to this clip.",
        "q4": "Busco un video en Destockd de ordenadores antiguos; muéstrame opciones.",
        "q5": "Find the full-film source linked from a Destockd shot page.",
        "q6": "Compose these local SVG scenes and narration into a three-scene MP4.",
        "q7": "Convert my local video to crisp retro pixel art.",
        "q8": "Download the YouTube video at this URL.",
        "q9": "Find modern commercial footage on Shutterstock, using only that provider.",
        "q10": "Explain the meaning of the word archival in one sentence.",
    }
    expected = {**{f"q{i}": "destockd-video-search" for i in range(1, 6)},
                "q6": "video", "q7": "pixel-art-image-video", "q8": "none", "q9": "none", "q10": "none"}
    prompt = ("Choose the single best skill for each request using only these descriptions. Use 'none' if none applies. "
              "Do not perform the requests or read any skill files. Write routing.json in the workspace as a JSON mapping "
              "of question IDs to exact skill names.\n\nDescriptions:\n" + json.dumps(metadata, indent=2)
              + "\n\nRequests:\n" + json.dumps(questions, ensure_ascii=False, indent=2))
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    command = [*harness.pi_command_prefix(), "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high",
               "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates",
               "--no-themes", "--no-session", "--print", "Read ../prompt.md first and complete its metadata-only classification."]
    with (run / "events.jsonl").open("w", encoding="utf-8") as out, (run / "stderr.txt").open("w", encoding="utf-8") as err:
        completed = subprocess.run(command, cwd=workspace, stdout=out, stderr=err, timeout=240)
    output = workspace / "routing.json"
    actual = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    observed = harness.collect_observed_models(run / "events.jsonl")
    correct = sum(actual.get(key) == value for key, value in expected.items())
    report = {"passed": correct == len(expected) and completed.returncode == 0
              and observed == [{"provider": "openai-codex", "model": "gpt-5.6-luna"}],
              "correct": correct, "total": len(expected), "expected": expected, "actual": actual,
              "observed_models": observed, "forced_skill": False, "metadata_only": True,
              "scope": "Classification control, not a native Codex discovery measurement.", "command": command}
    (run / "routing-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
