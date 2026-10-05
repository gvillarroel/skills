#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run retained standalone cohorts for this audit's composition consumers."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import sys

revision = sys.argv[1] if len(sys.argv) > 1 else "final"
case_filter = sys.argv[2] if len(sys.argv) > 2 else "all"
skill_filter = sys.argv[3] if len(sys.argv) > 3 else "all"
run_model = sys.argv[4] if len(sys.argv) > 4 else "openai-codex/gpt-5.6-luna"

root = Path(__file__).resolve().parents[3]
jobs = [
    ("echarts-animated-svg", "echarts", ["deliverables/workflow.static.svg", "deliverables/workflow.animated.svg", "deliverables/workflow-validation.json", "deliverables/layout-review.md"], ["deliverables/chart.static.svg", "deliverables/chart.animated.svg", "deliverables/chart-validation.json", "deliverables/layout-review.md"]),
    ("slidev-echarts", "slidev-echarts", ["deck/slides.md", "deck/components/SampleWorkflow.vue", "deck/package.json", "deliverables/layout-review.md"], ["deliverables/graph.svg", "deliverables/graph-option.json", "deliverables/layout-review.md"]),
    ("slidev-animejs", "slidev-animejs", ["deck/slides.md", "deck/components/OrderHandoff.vue", "deck/package.json", "deliverables/layout-review.md"], ["deck/slides.md", "deck/package.json", "deck/components/SvgAssetSlide.vue", "deliverables/layout-review.md"]),
    ("video", "video", ["source/scene-contract.json", "src/index.html", "deliverables/layout-review.md"], ["source/scene-contract.json", "src/index.html", "deliverables/layout-review.md"]),
    ("slidev-quality-audit", "slidev-audit", ["deck/slides.md", "deck/package.json", "deliverables/audit/quality-report.md", "deliverables/audit/quality-report.json", "deliverables/layout-review.md"], ["deck/slides.md", "deck/package.json", "deliverables/audit/quality-report.md", "deliverables/audit/quality-report.json", "deliverables/layout-review.md"]),
]
out = root / "projects/diagram-compactness/artifacts/reviews/root-cohorts"
out.mkdir(parents=True, exist_ok=True)

def run_skill(job):
    skill, prompt, natural_outputs, contract_outputs = job
    rows = []
    for case, suffix, outputs in [
        ("contract", "-contract", contract_outputs),
        ("natural-1", "", natural_outputs),
        ("natural-2", "", natural_outputs),
        ("natural-3", "", natural_outputs),
    ]:
        if case_filter != "all" and not case.startswith(case_filter):
            continue
        run_id = f"compact-{skill}-20261004-{revision}-{case}"
        cmd = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill,
               "--prompt-file", f"evaluations/pi-prompts/diagram-compactness-{prompt}{suffix}.md",
               "--model", run_model, "--thinking", "medium",
               "--mode", "json", "--strict", "--run-id", run_id]
        for path in outputs:
            cmd.extend(["--expect-output", path])
        result = subprocess.run(cmd, cwd=root, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        (out / f"{run_id}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        rows.append({"run": run_id, "returnCode": result.returncode, "command": cmd})
        (out / f"{skill}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(json.dumps(rows[-1]), flush=True)
    return rows

with ThreadPoolExecutor(max_workers=1) as pool:
    rows = list(pool.map(run_skill, [job for job in jobs if skill_filter in {"all", job[0]}]))
(out / "runs.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
