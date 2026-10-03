#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Seal passing curated-art calibration and stage host-only anchors for Harbor."""
import shutil
from pathlib import Path
from svg_excellence import REPO,DEFAULT_FONTS,read,sha,write
from svg_curated_pairs import ROOT,PREVIOUS,CONFIG,INTRO
from prepare_excellence_harbor import wsl
CONFIG=REPO/"projects/svg-brief-design/evaluation/art-direction-v5.2"


def main():
    results=read(ROOT/"results.json")
    if not results["passed"]:raise ValueError("Calibration failed; do not activate")
    bundle=ROOT/"frozen/evaluator";(bundle/"scripts").mkdir(parents=True,exist_ok=False)
    script_root=REPO/"projects/svg-brief-design/scripts"
    for name in ["svg_curated_pairs.py","curated_quality_v52.py","svg_art_direction.py","svg_excellence.py","diagnose_svg_layout.py","luna_svg_observer.py","evaluate_svg_jev.py","art_direction_review.py","harbor_svg_curated.py"]:
        shutil.copy2(script_root/name,bundle/"scripts"/name)
    for path in (REPO/"skills/jev-batch-decisions/scripts").glob("jev_*.py"):
        shutil.copy2(path,bundle/"scripts"/path.name)
    for name in ["job.json","protocol.json","visual-pair-prompt.txt"]:shutil.copy2(CONFIG/name,bundle/name)
    shutil.copytree(DEFAULT_FONTS,bundle/"fonts")
    source=read(PREVIOUS/"prepared/coordinator-only.json")
    anchors={}
    for row in source:
        if row["arm"]!="reference" and row["name"]!="minimal-refined":continue
        file="anchors/"+row["artifact_sha256"]+".svg"
        target=bundle/file;target.parent.mkdir(exist_ok=True);target.write_bytes((PREVIOUS/"prepared/artifacts"/(row["id"]+".svg")).read_bytes())
        anchors[row["task"]]={"file":file,"sha256":row["artifact_sha256"]}
    write(bundle/"anchor-registry.json",anchors)
    write(bundle/"lock.json",{"version":"5.2.0","files":{p.relative_to(bundle).as_posix():sha(p.read_bytes()) for p in sorted(bundle.rglob("*")) if p.is_file()},"observed_models":results["observed_models"],"checks":results["checks"],"results_sha256":sha((ROOT/"results.json").read_bytes()),"scope":"Curated-art development calibration; no independent skill promotion.","anchor_boundary":"Purchased SVGs stay in this ignored host-only evaluator bundle; never in skill payload, agent mounts, or public publication."})
    ds=ROOT/"ds";shutil.copytree(REPO/"evaluations/runs/svgq2/ds",ds)
    for folder in ds.iterdir():
        path=folder/"instruction.md";path.write_text(INTRO+" "+path.read_text(encoding="utf-8"),encoding="utf-8",newline="\n")
        (folder/"tests/test.sh").write_text('#!/bin/sh\necho "Use the frozen host-only SvgCuratedVerifier." >&2\nexit 2\n',encoding="utf-8",newline="\n")
        path=folder/"task.toml";path.write_text(path.read_text().replace("technical-excellence-v3","curated-design-v5.2").replace("timeout_sec = 360","timeout_sec = 600"),encoding="utf-8",newline="\n")
        path=folder/"tests/request-contract.json";contract=read(path)
        if "full_marks" in contract:contract["brief_fulfillment"]=contract.pop("full_marks")
        contract["quality_target"]="Brief fulfillment alone does not establish curated design quality. Evaluate six artistic dimensions against the anonymous quality anchor."
        path.write_text(__import__("json").dumps(contract,indent=2),encoding="utf-8")
        write(folder/"tests/quality-anchor.json",anchors[folder.name])
    verifier={"import_path":"harbor_svg_curated:SvgCuratedVerifier","kwargs":{"evaluator_bundle":wsl(bundle),"evaluator_lock_sha256":sha((bundle/"lock.json").read_bytes())}}
    future=read(REPO/"evaluations/runs/svgq2/future-job.json");future.update(job_name="future-curated-v5.2",jobs_dir=wsl(ROOT/"jobs"),verifier=verifier);future["datasets"][0]["path"]=wsl(ds)
    write(ROOT/"future-job.json",future)
    base=read(REPO/"evaluations/runs/svgq2/future-baseline-job.json");base.update(job_name="future-baseline-curated-v5.2",jobs_dir=wsl(ROOT/"jobs"),verifier=verifier,datasets=future["datasets"]);write(ROOT/"future-baseline-job.json",base)
    probe=ROOT/"probe/hud";shutil.copytree(sorted(ds.iterdir())[0],probe)
    good=next(row for row in source if row["name"]=="minimal-refined")
    request=read(PREVIOUS/"prepared/evidence"/(good["id"]+".json"))["request"]
    (probe/"instruction.md").write_text(INTRO+" "+request+"\n\nSave the editable, self-contained SVG to `/logs/artifacts/deliverable/vector.svg`.\n",encoding="utf-8",newline="\n")
    (probe/"tests/quality-anchor.json").write_text(__import__("json").dumps(anchors["synthetic-hud"],indent=2),encoding="utf-8")
    (probe/"tests/request-contract.json").write_text(__import__("json").dumps({"brief":request,"subject":"synthetic horizontal HUD bar","format":"editable self-contained SVG"},indent=2),encoding="utf-8")
    art=(PREVIOUS/"prepared/artifacts"/(good["id"]+".svg")).read_text(encoding="utf-8").replace('</svg>','<metadata>Visible-artwork identity control.</metadata></svg>')
    (probe/"solution").mkdir()
    (probe/"solution/solve.sh").write_text("#!/bin/sh\nset -eu\nmkdir -p /logs/artifacts/deliverable\ncat > /logs/artifacts/deliverable/vector.svg <<'SVG_EOF'\n"+art+"\nSVG_EOF\n",encoding="utf-8",newline="\n")
    job=future|{"job_name":"native-curated-v5.2-probe","n_attempts":1,"n_concurrent_trials":1,"agents":[{"name":"oracle"}],"datasets":[{"path":wsl(ROOT/"probe"),"task_names":["hud"]}]}
    write(ROOT/"probe-job.json",job)
    write(ROOT/"integration-lock.json",{"adapter_sha256":sha((script_root/"harbor_svg_curated.py").read_bytes()),"jobs":{name:sha((ROOT/name).read_bytes()) for name in ["future-job.json","future-baseline-job.json","probe-job.json"]},"probe_calls":{"observer":1,"jev":1},"scope":"Additional native wiring and visible-identity control, after the development calibration; not new skill generation."})
    print("Frozen curated-art evaluator, isolated quality anchors and new Harbor tasks.")


if __name__=="__main__":main()
