#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unforced metadata routing control, separate from the forced isolated harness."""
import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("harness", root / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec); spec.loader.exec_module(harness)
    names = ["hyperframes-explainer", "video", "asciinema-real-command-video", "manim-svg-video",
             "compose-synchronized-svg", "d3", "svg-brief-design"]
    descriptions = {name: re.search(r"^description: (.+)$", (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1) for name in names}
    cases = [
        ("tank", "Create a minimal HyperFrames film where opening a valve changes tank fill, rate and history together; colorset1 and almost no text.", "hyperframes-explainer"),
        ("cause", "Make a code-authored educational video with one controlling event and synchronized mechanism, measurements and trajectory; keep text sparse.", "hyperframes-explainer"),
        ("preview", "Build an interactive preview and MP4 of a vehicle's speed and accumulated distance, with a shared seekable clock and direct labels.", "hyperframes-explainer"),
        ("palette", "Use HyperFrames to explain conserved exchange with minimal labels, trying colorset1 before colorset2.", "hyperframes-explainer"),
        ("media", "Combine my photos, two existing video clips, a spoken soundtrack and subtitles into a multi-scene MP4.", "video"),
        ("tui", "Record an authentic execution of my installed terminal program and export the recording as video.", "asciinema-real-command-video"),
        ("manim", "Sequence these six existing SVG files using Manim and encode the result to MP4.", "manim-svg-video"),
        ("world", "Build a giant standalone SVG composition with linked diagrams, shared state and semantic zoom; no movie needed.", "compose-synchronized-svg"),
        ("chart", "Create one D3 scatter plot from this CSV with linked tooltip interaction.", "d3"),
        ("emblem", "Design an original decorative SVG botanical emblem with negative space.", "svg-brief-design"),
        ("prose", "Rewrite a paragraph to be more concise.", "none"),
        ("code", "Fix a Python function that mishandles an empty list.", "none"),
    ]
    run = root / "evaluations/runs" / args.run_id
    work = run / "workspace"; work.mkdir(parents=True, exist_ok=False)
    prompt = ("Select one primary skill from these descriptions for each request, or the string none. "
              "This is routing only; do not perform the requested tasks or read a skill. "
              "Use the write tool to create out/routing.json as an object mapping request IDs to skill names. "
              "Write only inside this workspace.\n\nDescriptions:\n" + json.dumps(descriptions, indent=2)
              + "\n\nRequests:\n" + json.dumps([{"id": key, "request": request} for key, request, _ in cases], indent=2))
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    command = [*harness.pi_command_prefix(), "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high", "--mode", "json",
               "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session",
               "--print", "Read ../prompt.md first, then carry out its routing-only request."]
    result = subprocess.run(command, cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    (run / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    (run / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    harness.write_json(run / "command.json", command)
    output = work / "out/routing.json"
    actual = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    checks = [{"id": key, "expected": expected, "actual": actual.get(key), "ok": actual.get(key) == expected} for key, _, expected in cases]
    summary = {"ok": result.returncode == 0 and all(c["ok"] for c in checks), "passed": sum(c["ok"] for c in checks),
               "total": len(checks), "model": "openai-codex/gpt-5.6-luna", "checks": checks,
               "scope": "Unforced metadata-only selection. This does not prove native app discovery."}
    harness.write_json(run / "result.json", summary)
    print(json.dumps(summary)); return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
