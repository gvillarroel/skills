#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the single prospectively declared contract after the cap-unit correction."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/reflex-xy/artifacts/errorbar-caps-pi"
RUN_ID = "20261024-reflex-xy-errorbar-caps-contract-sol-1"
FROZEN = "eaab7a3ee1f03faeb9b6cb0b215edecc64c2fa8d06ec37686022ac8914ae9d8d"
PROMPT = "evaluations/pi-prompts/reflex-xy-capabilities-errorbar-caps.md"
OUTPUTS = ["app.py", "notes.md", "results/cs1/errorbars.html",
           "results/cs1/errorbars.svg", "results/cs2/errorbars.html",
           "results/cs2/errorbars.svg"]


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "plan.json").exists() or (ROOT / "evaluations/runs" / RUN_ID).exists():
        raise RuntimeError("Refusing to rerun or replace the retained single attempt")
    spec = importlib.util.spec_from_file_location("harness", ROOT / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    snapshot_dir = OUT / "runtime-snapshot"
    harness.copy_skill_only(ROOT / "skills/reflex-xy", snapshot_dir, "runtime")
    snapshot = harness.snapshot_tree(snapshot_dir)
    digest = harness.snapshot_digest(snapshot)
    if digest != FROZEN or len(snapshot) != 18:
        raise RuntimeError(f"Runtime subject differs: {digest}, {len(snapshot)} files")
    write("runtime-freeze.json", {"digest": digest, "file_count": len(snapshot), "files": snapshot})
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", "reflex-xy",
               "--prompt-file", PROMPT, "--model", "openai-codex/gpt-5.6-sol",
               "--mode", "json", "--strict", "--run-id", RUN_ID,
               "--timeout-seconds", "900"]
    for output in OUTPUTS:
        command += ["--expect-output", output]
    write("plan.json", {"declared_at_utc": datetime.now(timezone.utc).isoformat(),
          "case": "corrected-native-errorbar-cap-units-contract", "attempts": 1,
          "run_id": RUN_ID, "runtime_digest": FROZEN, "runtime_files": 18,
          "prompt": PROMPT, "prompt_sha256": harness.sha256_file(ROOT / PROMPT),
          "model": "openai-codex/gpt-5.6-sol", "profile": "runtime", "mode": "json",
          "strict": True, "outputs": OUTPUTS, "command": command,
          "independent_checks": ["exact supplied centers and lower/upper boundaries",
          "six vertical shafts and twelve compact horizontal end caps in native SVG",
          "cap span <= 0.4 of the nearest observation gap; visible within plot",
          "small explicit native cap-size value relative to data-axis domain",
          "same geometry and labels across both canonical palettes, distinct measurement ink",
          "valid native SVG XML, offline HTML, source replay, desktop/mobile screenshot legibility",
          "strict model/tool/read-surface/payload integrity; independent trace review"],
          "threshold": "1/1 strict and independent artifact and manual geometry/screenshot pass",
          "policy": "Retain the single attempt; no rerolls, repairs, or waivers. Prior eight-attempt cohort remains historical. Skill status remains validating."})
    print(f"START {RUN_ID} frozen={digest}", flush=True)
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    (OUT / "harness.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (OUT / "harness.stderr.txt").write_text(result.stderr, encoding="utf-8")
    write("harness-result.json", {"run_id": RUN_ID, "command": command,
          "returncode": result.returncode, "elapsed_seconds": round(time.monotonic() - start, 2)})
    after_dir = OUT / "runtime-after"
    harness.copy_skill_only(ROOT / "skills/reflex-xy", after_dir, "runtime")
    write("runtime-freeze-check.json", harness.compare_snapshots(snapshot, harness.snapshot_tree(after_dir)))
    print(f"DONE {RUN_ID} exit={result.returncode}", flush=True)
