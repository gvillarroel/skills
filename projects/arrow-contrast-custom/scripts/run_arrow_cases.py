#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run and retain isolated contract and naturalistic style cases per bundle."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROMPTS = ROOT / "evaluations/pi-prompts/arrow-contrast-custom"
PROMPTS.mkdir(parents=True, exist_ok=True)
MODEL = "openai-codex/gpt-5.6-luna"
CASES = {
 "d3": {"naturalistic": ("""Create two offline, editable process engineering diagrams from the skill's normal P&ID control-loop route: pid-cs1.html using colorset1 and pid-cs2.html using colorset2. Keep the established equipment, valves, instrument bubbles, process paths and signal semantics. Directional shafts and complete arrow tips must remain readable against their actual local backings, with small external tip gutters and opaque borderless category fills. Use the owning bundled builder and inspect both files. Treat skills/d3/ as read-only, do not read acceptance fixtures, sibling skills or outside context, and keep all generated files in this workspace. Do not install or probe undeclared dependencies.
""", ["pid-cs1.html", "pid-cs2.html"])},
 "threejs-animated-3d": {"naturalistic": ("""Build a standalone offline 3D direction study titled "Directed flow" with twenty cone-and-cylinder arrow glyphs above a pale plane. Use the skill's vector-field scene route, colorset2, compact controls, replay and pointer orbit. Preserve actual cone/cylinder geometry and physical lighting for the surrounding plane; the arrows must keep readable 3:1 direction paint through the delivery views and reduced-motion state without outline meshes. Save field.html exactly. Run the declared bundled validator and inspect the result. Treat skills/threejs-animated-3d/ as read-only; do not read example galleries, sibling skills or outside context. Keep all task files in this workspace and use bundled machinery without package/dependency probes.
""", ["field.html"])},
 "svg-brief-design": {"naturalistic": ("""Create an editable three-stage flow with Intake, Review and Release, connected by right-pointing arrows. Produce paired versions using colorset2: yellow boxes #f1c319 on a white presentation, and the same yellow boxes over a full-canvas dark #1c1c1c rectangular underlay. Use a canvas 860 by 300. Keep the boxes solid and borderless and their labels readable. The actual shafts and open arrow tips must contrast with their local backings and remain outside the boxes. Save light.svg, dark.svg, light.json and dark.json exactly as scaffold recipes and outputs; inspect both. Treat skills/svg-brief-design/ as read-only, do not read acceptance fixtures, sibling skills or outside context, and keep all generated files in this workspace. Use the bundled scaffold route.
""", ["light.svg", "dark.svg", "light.json", "dark.json"])},
 "procedural-svg-animation": {"naturalistic": ("""Create a standalone procedural SVG vector field using the skill's established analytic line-glyph pattern: preserve the 9 by 15 sample geometry and its vector-derived orientation/length. Use colorset2 at 960 by 600 with deterministic seed 89 and a four-second emphasis cycle. Keep the existing bare lines; do not invent arrowheads or change the vector computation. Direction ink must be readable against the pale surface at full emphasis. Save field.svg and a directly static reduced-motion version field-static.svg using the same geometry and palette. Validate and inspect both. Treat skills/procedural-svg-animation/ as read-only; do not inspect acceptance fixtures, sibling skills or outside context, and keep generated files in this workspace. Use bundled machinery without undeclared dependency probes.
""", ["field.svg", "field-static.svg"])}
}


def evaluate(skill, kind, repetition):
    prompt, artifacts = CASES[skill][kind]
    prompt = prompt.replace("```powershell", "```bash")
    prompt_path = PROMPTS / f"{skill}-{kind}.md"
    prompt_path.write_text(prompt, encoding="utf-8", newline="\n")
    run_id = f"custom-arrow-{skill}-{kind}-20261003-luna-{repetition}"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill, "--prompt-file", str(prompt_path.relative_to(ROOT)), "--model", MODEL, "--mode", "json", "--strict", "--run-id", run_id, "--timeout-seconds", "600"]
    if kind == "contract":
        command.append("--require-exact-command-from-prompt")
    for artifact in artifacts:
        command.extend(["--expect-output", artifact])
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = ROOT / "projects/arrow-contrast-custom/artifacts/data" / f"{run_id}.log"
    log.write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")
    result = {"skill": skill, "case": kind, "repetition": repetition, "runId": run_id, "exitCode": completed.returncode, "command": command}
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills", nargs="*", choices=CASES, default=list(CASES))
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--naturalistic-repetitions", type=int, default=1)
    parser.add_argument("--start-repetition", type=int, default=1)
    parser.add_argument("--result-file", default="pi-results.json")
    args = parser.parse_args()
    kinds = (("naturalistic", args.naturalistic_repetitions),)
    work = [(skill, kind, repetition) for skill in args.skills for kind, repetitions in kinds for repetition in range(args.start_repetition, args.start_repetition + repetitions)]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed(pool.submit(evaluate, *item) for item in work):
            results.append(future.result())
            (ROOT / "projects/arrow-contrast-custom/artifacts/data" / args.result_file).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"strictPasses": sum(item["exitCode"] == 0 for item in results), "attempts": len(results)}))
