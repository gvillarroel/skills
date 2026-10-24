#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the single prospectively declared contract after the Sankey contrast correction."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/reflex-xy/artifacts/sankey-contrast-pi"
RUN_ID = "20261024-reflex-xy-sankey-contrast-contract-sol-1"
FROZEN = "fc516b8295be4db1319006310e08181d3a9e3d36716b5ac3268e95c7c3151eb7"
PROMPT = "evaluations/pi-prompts/reflex-xy-capabilities-sankey-contrast.md"
OUTPUTS = ["app.py", "notes.md", "results/cs1/flows.html", "results/cs1/flows.svg",
           "results/cs2/flows.html", "results/cs2/flows.svg"]


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
          "case": "corrected-native-sankey-label-contrast-contract", "attempts": 1,
          "run_id": RUN_ID, "runtime_digest": FROZEN, "runtime_files": 18,
          "prompt": PROMPT, "prompt_sha256": harness.sha256_file(ROOT / PROMPT),
          "model": "openai-codex/gpt-5.6-sol", "profile": "runtime", "mode": "json",
          "strict": True, "outputs": OUTPUTS, "command": command,
          "independent_checks": ["all supplied node identities and ordered weighted links preserved",
          "actual native Sankey family used; five native node labels retained",
          "proportional five-link geometry; identical paired native geometry",
          "canonical dark authored nodes/ribbon endpoints and readable contrasting labels",
          "native label/background contrast and HTML/SVG screenshot legibility",
          "valid native SVG XML, local offline HTML, editable pinned source replay",
          "truthful derived ribbon-color and offline callback limitations",
          "strict model/tool/read-surface/payload integrity; independent trace review"],
          "threshold": "1/1 strict and independent artifact and manual native/HTML contrast pass",
          "policy": "Retain the single attempt; no rerolls, repairs, or waivers. Earlier eight-attempt and cap cohorts remain historical. Skill status remains validating."})
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
