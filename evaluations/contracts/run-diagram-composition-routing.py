#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unforced, metadata-only routing control with evaluator-owned expected choices."""

import importlib.util
import argparse
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("eval_harness", root / "scripts" / "run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec); spec.loader.exec_module(harness)
    names = ["diagram-composition", "compose-synchronized-svg", "mermaid", "iconify-icon-search",
             "technical-logo-assets", "svg-brief-design", "d3"]
    descriptions = {n: re.search(r"^description: (.+)$", (root / "skills" / n / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1) for n in names}
    cases = [
        ("compact", "Explain a complex system with three related diagram types in a compact grid, using shared symbols.", "diagram-composition"),
        ("portrait", "Divide a complex idea into a taxonomy, cycle, and comparison and fit them into one readable portrait figure.", "diagram-composition"),
        ("sequence", "Create one Mermaid sequence diagram for a login handshake.", "mermaid"),
        ("brand", "Export the exact GitHub Copilot SVG logo with its provenance.", "technical-logo-assets"),
        ("pictograms", "Find a consistent set of Lucide house, search, and cloud pictograms.", "iconify-icon-search"),
        ("world", "Create a 24-module navigable SVG world with shared live values, semantic zoom, and coordinated focus.", "compose-synchronized-svg"),
        ("ornament", "Draw an original decorative botanical SVG emblem with deliberate negative space.", "svg-brief-design"),
        ("bug", "Fix a Python function that incorrectly handles empty strings.", "none"),
        ("spans", "Make two explanations on the left and a synthesis spanning both rows on the right; choose forms and SVG icons.", "diagram-composition"),
        ("bar", "Create a single D3 bar chart with a shared numerical scale.", "d3"),
        ("prose", "Shorten this prose paragraph to fifty words.", "none"),
        ("er", "Render a Mermaid ER diagram containing customers, orders, and cardinalities.", "mermaid")]
    run = root / "evaluations" / "runs" / args.run_id
    work = run / "workspace"; work.mkdir(parents=True, exist_ok=False)
    prompt = ("Choose one primary skill per request from the supplied descriptions, or none. "
              "This is routing only; do not execute the requested tasks or read any skill. "
              "Use the write tool to create the exact path out/routing.json, not routing.json. "
              "Write an object mapping request IDs to chosen skill name strings. Use the literal string none for no suitable skill; do not use null. "
              "Keep all output inside this workspace.\n\nDescriptions:\n" + json.dumps(descriptions, indent=2)
              + "\n\nRequests:\n" + json.dumps([{ "id": k, "request": q} for k, q, _ in cases], indent=2))
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    command = [*harness.pi_command_prefix(), "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high",
        "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates",
        "--no-themes", "--no-session", "--print", "Read ../prompt.md first, then carry out its routing-only request."]
    result = subprocess.run(command, cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    (run / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    (run / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    (run / "command.json").write_text(json.dumps(command, indent=2), encoding="utf-8")
    output = work / "out" / "routing.json"
    actual = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    checks = [{"id": k, "expected": expected, "actual": actual.get(k), "ok": actual.get(k) == expected} for k, _, expected in cases]
    summary = {"ok": all(c["ok"] for c in checks), "passed": sum(c["ok"] for c in checks), "total": len(checks), "checks": checks,
               "scope": "Metadata-only unforced selection; not native app discovery."}
    (run / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    raise SystemExit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
