#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Execute the installed native population engine with sealed study inputs."""
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt1"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):
    with Path(p).open("x",encoding="utf-8") as f: json.dump(v,f,indent=2)
def wsl(p): return "/mnt/c/"+Path(p).resolve().as_posix()[3:]


def main():
    mode = sys.argv[1]
    assert mode in {"doctor","dry-run","run","analyze","gate"}
    if sys.platform=="win32":
        target = ROOT / "inputs/c/svg-brief-design"
        if not target.exists(): shutil.copytree(ROOT / "sealed-c/candidate/skills/svg-brief-design",target)
        argv = ["--job-template",wsl(ROOT / "templates/development.json"),"--candidate","b="+wsl(ROOT / "inputs/b/svg-brief-design"),"--candidate","c="+wsl(target),"--baseline","b","--generation","0","--reward-key","technique_quality","--pass-threshold","0","--minimum-development-pass-rate","1","--required-reward","artifact_valid=1","--minimum-holdout-gain",".02","--allow-task-regressions","--output",wsl(ROOT)]
        path = ROOT / "generation-000-argv.json"
        if not path.exists(): write(path,argv)
        else: assert read(path)==argv
        process = subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python",wsl(Path(__file__)),mode],input=json.dumps({"key":os.environ["OPENROUTER_API_KEY"]}),text=True,encoding="utf-8")
        raise SystemExit(process.returncode)
    os.environ["OPENROUTER_API_KEY"] = json.load(sys.stdin)["key"]
    os.environ["FOX_PI_AUTH"] = "/mnt/c/Users/villa/.pi/agent/auth.json"
    os.environ["PYTHONDONTWRITEBYTECODE"]="1";sys.dont_write_bytecode=True
    sys.path.insert(0,str(REPO / "evaluations/runs/svgq2/python-deps"))
    protocol = read(ROOT / "protocol.json")
    for name,expected in protocol["template_sha256"].items(): assert sha(ROOT / "templates" / name)==expected
    for name,expected in protocol["helper_sha256"].items(): assert sha(Path(__file__).parent / name)==expected
    from evaluate_svg_jev import validate_bundle
    validate_bundle(ROOT / "evaluator")
    argv = read(ROOT / "generation-000-argv.json")
    if mode in {"doctor","dry-run"}:
        argv += ["--holdout-template",str(ROOT / "templates/validation.json"),"--"+mode]
    elif mode in {"analyze","gate"}:
        argv += ["--analyze-only"]
        for candidate in ["b","c"]:
            job=ROOT / f"generation-000/candidates/{candidate}/harbor-jobs/harbor-pop-g000-{candidate}"
            argv += ["--job",candidate+"="+str(job)]
        if mode=="gate":
            assert read(ROOT / "validation-release-ready.json")["passed"]
            argv += ["--holdout-template",str(ROOT / "templates/validation.json")]
    if mode in {"run","gate"}:
        write(ROOT / (mode+"-started.json"),{"at":datetime.now(timezone.utc).isoformat(),"argv":argv,"protocol_sha256":sha(ROOT / "protocol.json"),"entrypoint_sha256":sha(__file__)})
    import run_procedural_population
    sys.argv=["population"]+argv
    with (ROOT / (mode+".stdout.txt")).open("x") as out,(ROOT / (mode+".stderr.txt")).open("x") as err:
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=run_procedural_population.main()
    print(json.dumps({"mode":mode,"exit_code":code,"log":str(ROOT / (mode+".stdout.txt"))}),flush=True)
    return code


if __name__=="__main__": raise SystemExit(main())
