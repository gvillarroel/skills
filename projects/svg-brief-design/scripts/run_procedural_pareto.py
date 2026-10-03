#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Use the installed native Pareto engine with a stable Harbor event loop.

The optional execute mode runs one frozen native job through the same engine's
execute_job function. Completed jobs enter its unmodified --analyze-only path;
this allows independent proposal branches to finish at different times without
replaying already completed baseline attempts. This adapter never scores,
normalizes, ranks, or promotes candidates.
"""
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types

REPO = Path(__file__).resolve().parents[3]
ENGINE = Path("/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def wsl(path):
    return "/mnt/c/" + Path(path).resolve().as_posix()[3:]


def put(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)


def engine_module():
    spec = importlib.util.spec_from_file_location("svg_native_pareto", ENGINE)
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    return engine


def remote(root, mode, argument):
    os.environ["OPENROUTER_API_KEY"] = json.load(sys.stdin)["key"]
    os.environ["FOX_PI_AUTH"] = "/mnt/c/Users/villa/.pi/agent/auth.json"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(REPO / "evaluations/runs/svgq2/python-deps"))
    from evaluate_svg_jev import validate_bundle
    validate_bundle(root / "evaluator")
    protocol = read(root / "protocol.json")
    for name, expected in protocol["helper_sha256"].items():
        assert sha(Path(__file__).parent / name) == expected
    assert sha(__file__) == protocol["pareto_adapter_sha256"]
    engine = engine_module()
    assert sha(ENGINE) == protocol["pareto_engine_sha256"]
    log = root / f"pareto-{mode}-{argument}"
    with log.with_suffix(".stdout.txt").open("x") as output, log.with_suffix(".stderr.txt").open("x") as error:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            with asyncio.Runner() as runner:
                proxy = types.SimpleNamespace(**vars(asyncio))
                proxy.run = runner.run
                engine.asyncio = proxy
                if mode == "execute":
                    assert not (root / "validation-release-ready.json").exists()
                    assert argument in protocol["candidate_ids"]
                    template = root / "templates/development.json"
                    skill = root / f"inputs/{argument}/svg-brief-design"
                    config = engine.load_job_template(template)
                    assert config.n_attempts == protocol["development"]["attempts"]
                    assert config.n_concurrent_trials == 3 and config.retry.max_retries == 0
                    assert all(a.model_name == "openai-codex/gpt-6-luna" for a in config.agents)
                    engine.assert_self_contained_bundle(skill, "frozen execution candidate")
                    seal = read(root / f"input-{argument}.json")
                    assert engine.parse_skill_name(skill) == "svg-brief-design"
                    from harbor.skills import compute_skill_digest
                    assert compute_skill_digest(skill) == seal["harbor_digest"]
                    put(root / f"started-{argument}.json", {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "template_sha256": sha(template), "input_receipt_sha256": sha(root / f"input-{argument}.json"),
                        "generation_calls": protocol["development"]["cases"] * config.n_attempts,
                        "retries": 0, "native_entrypoint": str(ENGINE) + ":execute_job",
                    })
                    runner.run(engine.execute_job(template, skill, root / "jobs", argument))
                    assert compute_skill_digest(skill) == seal["harbor_digest"]
                else:
                    config = root / f"pareto-{argument}.json"
                    options = {"doctor": ["--doctor"], "dry-run": ["--dry-run"],
                               "analyze": ["--analyze-only"], "holdout": ["--phase", "holdout"]}
                    assert mode in options
                    if mode == "holdout":
                        assert read(root / "validation-release-ready.json")["passed"]
                    sys.argv = [str(ENGINE), str(config), *options[mode]]
                    engine.main()
    print(json.dumps({"mode": mode, "argument": argument, "completed": True}), flush=True)


def main():
    mode, study, argument = sys.argv[1:]
    assert study.startswith("svt") and study[3:].isdigit()
    assert argument.replace("-", "").isalnum()
    root = REPO / "evaluations/runs" / study
    if sys.platform != "win32":
        return remote(root, mode, argument)
    command = ["wsl", "-e", "/home/villa/.local/share/uv/tools/harbor/bin/python", "-B",
               wsl(__file__), mode, study, argument]
    result = subprocess.run(command, input=json.dumps({"key": os.environ["OPENROUTER_API_KEY"]}),
                            text=True, encoding="utf-8")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
