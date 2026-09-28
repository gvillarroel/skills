#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check source-specific routing from metadata without forcing any skill."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main():
    root = Path.cwd()
    run = root / "evaluations/runs/free-resources-routing-20260927-luna-1"
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    names = ["polyhaven-asset-search", "ambientcg-material-search", "pexels-media-search", "iconify-icon-search", "kenney-asset-search", "destockd-video-search", "technical-logo-assets"]
    metadata = {}
    for name in names:
        header = (root / "skills" / name / "SKILL.md").read_text(encoding="utf8").split("---", 2)[1]
        metadata[name] = next(x.split(":", 1)[1].strip() for x in header.splitlines() if x.startswith("description:"))
    cases = [
        ("Find free sunset lighting environments on Poly Haven.", names[0]),
        ("From the Poly Haven options, download option 2 with its model textures.", names[0]),
        ("Busca materiales de hormigon en ambientCG y muestra opciones.", names[1]),
        ("Download the selected ambientCG material as a 4K PNG package.", names[1]),
        ("Find vertical Pexels photos of forests.", names[2]),
        ("Download the Pexels video option 3 at the available 1080p rendition.", names[2]),
        ("Find matching cart and settings icons from Iconify.", names[3]),
        ("Download the selected Iconify SVG in blue at 32 pixels high.", names[3]),
        ("Find free Kenney 3D nature packs and show previews.", names[4]),
        ("Extract the chosen sprite from the Kenney pack we selected.", names[4]),
        ("Find archival clips of old computers on Destockd.", names[5]),
        ("Build a verified SVG catalog of cloud vendor logos.", names[6]),
        ("Buy a premium texture from a paid marketplace.", "none"),
        ("Generate an original illustration of a fox.", "none"),
        ("Explain what roughness means in a PBR material.", "none"),
    ]
    questions = {f"q{i}": text for i, (text, _) in enumerate(cases, 1)}
    expected = {f"q{i}": answer for i, (_, answer) in enumerate(cases, 1)}
    prompt = "Choose the single best skill for each request using only these descriptions. Use 'none' when no skill applies. Do not execute the tasks or read skill files. Write routing.json as a JSON mapping of request IDs to skill names.\n\nDescriptions:\n" + json.dumps(metadata, indent=2) + "\n\nRequests:\n" + json.dumps(questions, indent=2)
    (run / "prompt.md").write_text(prompt, encoding="utf8")
    spec = importlib.util.spec_from_file_location("harness", root / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec); spec.loader.exec_module(harness)
    command = [*harness.pi_command_prefix(), "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high", "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session", "--print", "Read ../prompt.md first and complete the metadata-only routing task."]
    with (run / "events.jsonl").open("w", encoding="utf8") as out, (run / "stderr.txt").open("w", encoding="utf8") as err:
        result = subprocess.run(command, cwd=workspace, stdout=out, stderr=err, timeout=240)
    actual = json.loads((workspace / "routing.json").read_text(encoding="utf8")) if (workspace / "routing.json").exists() else {}
    observed = harness.collect_observed_models(run / "events.jsonl")
    correct = sum(actual.get(k) == v for k, v in expected.items())
    report = {"passed": correct == len(cases) and result.returncode == 0 and observed == [{"provider": "openai-codex", "model": "gpt-5.6-luna"}],
              "correct": correct, "total": len(cases), "expected": expected, "actual": actual, "observed_models": observed,
              "metadata_only": True, "forced_skill": False, "scope": "Classification control, not native Codex discovery evidence.", "command": command}
    (run / "routing-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__": raise SystemExit(main())
