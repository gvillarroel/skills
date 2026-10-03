#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Fail-closed compact-path launch of the unchanged population engine."""
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import run_procedural_population

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp3"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    assert mode in {"doctor", "dry-run", "run"}
    protocol = json.loads((ROOT / "protocol.json").read_text())
    assert all(row["passed"] for row in json.loads((ROOT / "path-length-probe.json").read_text())["rows"])
    assert protocol["maximum_expected_artifact_path_length"] <= 210
    for name, expected in protocol["runtime"]["helpers"].items():
        assert hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == expected, name
    for name, expected in protocol["templates"].items():
        assert hashlib.sha256((ROOT / "templates" / name).read_bytes()).hexdigest() == expected, name
    for key in ("agent_image", "source_agent_image", "verifier_image"):
        identity = protocol["runtime"][key]
        assert json.loads(subprocess.check_output(["docker", "image", "inspect", identity]))[0]["Id"] == identity
    argv = json.loads((ROOT / "generation-000-argv.json").read_text())
    if mode != "run":
        argv += ["--holdout-template", str(ROOT / "templates/validation.json"), "--" + mode]
    else:
        with (ROOT / "generation-000-started.json").open("x") as handle:
            json.dump({"started_at": datetime.now(timezone.utc).isoformat(), "argv": argv,
                       "protocol_sha256": hashlib.sha256((ROOT / "protocol.json").read_bytes()).hexdigest()}, handle, indent=2)
    sys.argv = ["population"] + argv
    print(json.dumps({"mode": mode, "started": True}), flush=True)
    with (ROOT / f"generation-000-{mode}.stdout.json").open("w") as output, (ROOT / f"generation-000-{mode}.stderr.txt").open("w") as error:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            result = run_procedural_population.main()
    print(json.dumps({"mode": mode, "exit_code": result}), flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
