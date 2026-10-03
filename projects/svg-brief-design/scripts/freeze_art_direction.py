#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Seal a passing development calibration and prepare native Harbor jobs."""
import shutil
from pathlib import Path
from svg_excellence import REPO,DEFAULT_FONTS,read,sha,write
from svg_art_direction import GENERATOR_INTRO
from prepare_excellence_harbor import wsl

ROOT=REPO/"evaluations/runs/svg-art-v4"
CONFIG=REPO/"projects/svg-brief-design/evaluation/art-direction-v4"


def main():
    results=read(ROOT/"results.json");audit=read(ROOT/"audit.json");pairs=read(ROOT/"pair-report.json")
    if not results["passed_single_artifact_checks"] or not audit["passed"] or not pairs["passed"]:
        raise ValueError("Development gates do not authorize activation")
    bundle=ROOT/"frozen/evaluator";(bundle/"scripts").mkdir(parents=True,exist_ok=False)
    scripts=REPO/"projects/svg-brief-design/scripts"
    for name in ["svg_art_direction.py","svg_excellence.py","diagnose_svg_layout.py","luna_svg_observer.py","evaluate_svg_jev.py","art_direction_review.py","harbor_svg_art_direction.py"]:
        shutil.copy2(scripts/name,bundle/"scripts"/name)
    for path in (REPO/"skills/jev-batch-decisions/scripts").glob("jev_*.py"):
        shutil.copy2(path,bundle/"scripts"/path.name)
    for name in ["job.json","rubric.json","visual-critic-prompt.txt"]:
        shutil.copy2(CONFIG/name,bundle/name)
    shutil.copytree(DEFAULT_FONTS,bundle/"fonts")
    write(bundle/"lock.json",{"version":"4.0.0","files":{p.relative_to(bundle).as_posix():sha(p.read_bytes()) for p in sorted(bundle.rglob("*")) if p.is_file()},"observed_models":audit["observed_models"],"calibration_checks":results["checks"],"pair_order_agreement":pairs["order_agreement"],"scope":"Development-calibrated art quality. No independent skill promotion.","results_sha256":sha((ROOT/"results.json").read_bytes())})
    source=REPO/"evaluations/runs/svgq2/ds";target=ROOT/"ds"
    shutil.copytree(source,target)
    for path in target.glob("*/instruction.md"):
        path.write_text(GENERATOR_INTRO+" "+path.read_text(encoding="utf-8"),encoding="utf-8",newline="\n")
    for path in target.glob("*/task.toml"):
        path.write_text(path.read_text().replace("technical-excellence-v3","professional-quality-v4").replace("timeout_sec = 360","timeout_sec = 600"),encoding="utf-8",newline="\n")
    for path in target.glob("*/tests/test.sh"):
        path.write_text('#!/bin/sh\necho "Use the frozen SvgArtDirectionVerifier." >&2\nexit 2\n',encoding="utf-8",newline="\n")
    verifier={"import_path":"harbor_svg_art_direction:SvgArtDirectionVerifier","kwargs":{"evaluator_bundle":wsl(bundle),"evaluator_lock_sha256":sha((bundle/"lock.json").read_bytes())}}
    future=read(REPO/"evaluations/runs/svgq2/future-job.json")
    future.update(job_name="future-professional-v4",jobs_dir=wsl(ROOT/"jobs"),verifier=verifier)
    future["datasets"][0]["path"]=wsl(target)
    write(ROOT/"future-job.json",future)
    baseline=read(REPO/"evaluations/runs/svgq2/future-baseline-job.json")
    baseline.update(job_name="future-baseline-professional-v4",jobs_dir=wsl(ROOT/"jobs"),verifier=verifier,datasets=future["datasets"])
    write(ROOT/"future-baseline-job.json",baseline)
    rows=read(ROOT/"prepared/coordinator-only.json");good=next(r for r in rows if r["name"]=="minimal-refined")
    probe=ROOT/"probe/hud"
    shutil.copytree(next(target.iterdir()),probe)
    brief=read(ROOT/"prepared/evidence"/(good["id"]+".json"))["request"]
    (probe/"instruction.md").write_text(GENERATOR_INTRO+" "+brief+"\n\nSave the self-contained editable SVG to `/logs/artifacts/deliverable/vector.svg`.\n",encoding="utf-8",newline="\n")
    (probe/"solution").mkdir()
    art=(ROOT/"prepared/artifacts"/(good["id"]+".svg")).read_text(encoding="utf-8")
    (probe/"solution/solve.sh").write_text("#!/bin/sh\nset -eu\nmkdir -p /logs/artifacts/deliverable\ncat > /logs/artifacts/deliverable/vector.svg <<'SVG_EOF'\n"+art+"\nSVG_EOF\n",encoding="utf-8",newline="\n")
    config=future|{"job_name":"native-art-v4-probe","n_attempts":1,"n_concurrent_trials":1,"agents":[{"name":"oracle"}],"datasets":[{"path":wsl(ROOT/"probe"),"task_names":["hud"]}]}
    write(ROOT/"probe-job.json",config)
    write(ROOT/"integration-lock.json",{"adapter_sha256":sha((scripts/"harbor_svg_art_direction.py").read_bytes()),"bundle_lock_sha256":sha((bundle/"lock.json").read_bytes()),"jobs":{name:sha((ROOT/name).read_bytes()) for name in ["future-job.json","future-baseline-job.json","probe-job.json"]}})
    print("Sealed calibrated art-direction evaluator and prepared native jobs.")


if __name__=="__main__":main()
