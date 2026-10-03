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
PROMPTS = ROOT / "evaluations/pi-prompts/custom-solid-style"
PROMPTS.mkdir(parents=True, exist_ok=True)
MODEL = "openai-codex/gpt-5.6-luna"
CASES = {
    "d3": {
        "contract": ('''Build the offline delivery flow by running this exact command, then inspect the resulting artifacts. Keep all files under this workspace and treat skills/d3/ as read-only. Do not inspect acceptance fixtures or other skills.

```powershell
uv run --script skills/d3/scripts/build_contract_artifact.py --kind flow --output flow.html --decision-output flow.json --title "Delivery stages" --description "Capture to release" --route flow --colorset colorset2 --pattern-id d3-delivery-stages --svg-id delivery --reason "Ordered transfers" --flow-node Capture --flow-node Review --flow-node Release --link "Capture->Review" --link "Review->Release" --link-value 8 --link-value 6
```
''', ["flow.html", "flow.json"]),
        "naturalistic": ('''Create an offline, editable D3 SVG diagram for a six-stage document workflow: Draft, Review, Revise, Approve, Publish, Archive, in that exact order, with directed transfers between adjacent stages of 12, 10, 8, 7 and 6 documents respectively. Use colorset2 and the skill's standard visual treatment. Save workflow.html and decision.json. Use a 1200 by 240 SVG with id workflow and pattern ID d3-document-workflow. Keep the labels readable and the link amounts visible. Treat skills/d3/ as read-only and do not inspect acceptance fixtures, other skills or outside context. Use the bundled production route and inspect the result; do not install or probe undeclared browser dependencies.
''', ["workflow.html", "decision.json"]),
    },
    "threejs-animated-3d": {
        "contract": ('''Create the standard offline orbit scene by running this exact command. Inspect the resulting HTML. Treat skills/threejs-animated-3d/ as read-only; keep outputs in this workspace and do not read examples or other skills.

```powershell
uv run --script skills/threejs-animated-3d/scripts/build_standalone_threejs.py orbit.html --colorset colorset1 --token-count 5
```
''', ["orbit.html"]),
        "naturalistic": ('''Build an offline, replayable 3D orbit study titled "Material roles" with eighteen orbiting token objects around the central hub. Use colorset2 and the normal visual treatment of the skill, white lighting, a white stage, compact controls and pointer drag. Save the exact standalone file roles.html. It must run without network access and expose the standard scene inspection API for material and light colors. Keep skills/threejs-animated-3d/ read-only. Do not read examples, other skills or outside context. Use the declared bundled builder and validator without new dependency probes.
''', ["roles.html"]),
    },
    "procedural-svg-animation": {
        "contract": ('''Build this eight-state sequencing pattern, then validate the output. Treat skills/procedural-svg-animation/ as read-only; do not read acceptance fixtures, other skills or outside context. Keep task files in this workspace.

```powershell
uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py procedural-svg-state-sequencer --output sequencer.svg --palette colorset2 --seed 31 --duration-ms 4000
```
''', ["sequencer.svg"]),
        "naturalistic": ('''Create a standalone animated SVG that explains an eight-state clock moving through states 1 to 8 and returning to the start every four seconds. Use the skill's standard colorset2 treatment at 960 by 600, deterministic seed 89. Save clock.svg with its normal in-document reduced-motion fallback, and save a directly static reduced-motion version as clock-static.svg. Use the same procedural pattern and geometry for both. Validate both. Treat skills/procedural-svg-animation/ as read-only; do not inspect example galleries, other skills or outside context. Keep all generated files under this workspace.
''', ["clock.svg", "clock-static.svg"]),
    },
    "svg-brief-design": {
        "contract": ('''Create the editable flow scaffold with this exact command. Inspect the SVG and recipe. Treat skills/svg-brief-design/ as read-only; do not read examples, other skills or outside context. Keep generated files in this workspace.

```powershell
uv run --script skills/svg-brief-design/scripts/scaffold.py init flow --recipe flow.json --output flow.svg --colorset colorset1
```
''', ["flow.json", "flow.svg"]),
        "naturalistic": ('''Draw an editable three-stage workflow with Harvest, Review and Release in that order, connected by right-pointing arrows. Use a canvas 860 by 300. Create two versions of exactly the same geometry: all boxes in maroon #9e1b32 and all boxes in yellow #f1c319, both with colorset2. Follow the skill's normal styling and retain readable labels. Save maroon.svg, yellow.svg, maroon.json and yellow.json as editable scaffold recipes and SVGs. Treat skills/svg-brief-design/ as read-only, do not inspect other skills or outside context, and keep all generated files in this workspace. Use the bundled scaffold route.
''', ["maroon.svg", "yellow.svg", "maroon.json", "yellow.json"]),
    },
    "vectorize-art-patterns": {
        "contract": ('''Vectorize the bundled public-domain Bailly source with this exact command. Inspect the SVG and report. Treat skills/vectorize-art-patterns/ as read-only and do not read acceptance fixtures or other skills. The bundled source manifest is the provenance authority. Keep outputs in this workspace.

```powershell
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py skills/vectorize-art-patterns/assets/base-images/bailly-beauties-fancy.jpg bailly.svg --mode organic --colors 12 --colorset colorset1 --max-dimension 320 --source-manifest skills/vectorize-art-patterns/assets/base-images/manifest.json --source-id bailly-beauties-fancy --report bailly.json
```
''', ["bailly.svg", "bailly.json"]),
        "naturalistic": ('''Create a compact editable vector reinterpretation of the bundled public-domain Bailly artwork bailly-beauties-fancy.jpg. Make paired colorset1 and colorset2 versions using identical source contours, twelve color layers, organic mode and a maximum source dimension of 320. Use the skill's standard styling and retain the bundled manifest provenance. Save artwork-cs1.svg, artwork-cs2.svg and their matching reports artwork-cs1.json and artwork-cs2.json. Check both derivatives and geometry parity. Treat skills/vectorize-art-patterns/ as read-only; read only the necessary bundled source image and manifest, instructions and machinery. Do not read acceptance galleries, other skills or outside context. Keep generated outputs in this workspace.
''', ["artwork-cs1.svg", "artwork-cs2.svg", "artwork-cs1.json", "artwork-cs2.json"]),
    },
}


def evaluate(skill, kind, repetition):
    prompt, artifacts = CASES[skill][kind]
    prompt = prompt.replace("```powershell", "```bash")
    prompt_path = PROMPTS / f"{skill}-{kind}.md"
    prompt_path.write_text(prompt, encoding="utf-8", newline="\n")
    run_id = f"custom-solid-{skill}-{kind}-20261003-luna-{repetition}"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill, "--prompt-file", str(prompt_path.relative_to(ROOT)), "--model", MODEL, "--mode", "json", "--strict", "--run-id", run_id, "--timeout-seconds", "600"]
    if kind == "contract":
        command.append("--require-exact-command-from-prompt")
    for artifact in artifacts:
        command.extend(["--expect-output", artifact])
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = ROOT / "projects/custom-solid-style/artifacts/data" / f"{run_id}.log"
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
    parser.add_argument("--naturalistic-repetitions", type=int, default=3)
    parser.add_argument("--start-repetition", type=int, default=1)
    parser.add_argument("--result-file", default="pi-results.json")
    args = parser.parse_args()
    kinds = (("contract", 1),) if args.contract_only else (("contract", 1), ("naturalistic", args.naturalistic_repetitions))
    work = [(skill, kind, repetition) for skill in args.skills for kind, repetitions in kinds for repetition in range(args.start_repetition, args.start_repetition + repetitions)]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed(pool.submit(evaluate, *item) for item in work):
            results.append(future.result())
            (ROOT / "projects/custom-solid-style/artifacts/data" / args.result_file).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"strictPasses": sum(item["exitCode"] == 0 for item in results), "attempts": len(results)}))
