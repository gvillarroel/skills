#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""One affirmative independent review of a predeclared two-family pilot.

The prior three-family authoring attempt failed before any candidate generation.
Reuse its exact randomly sampled inventory, not a favorable replacement seed.
This is an append-only change of the pilot's coverage claim, never a passing
reinterpretation of the earlier rejection. No candidate outputs are supplied.
"""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

import prepare_technique_evolution as preparation
from svg_art_direction import PROGRAM, IMAGE, IMAGE_ID
from svg_excellence import read, write, sha


def main():
    base = Path(__file__).resolve().parents[3] / "evaluations/runs"
    previous, root = base / "svt5", base / "svt6"
    assert not read(previous / "curation-status.json")["passed"]
    root.mkdir()
    private = root / "private"
    private.mkdir()
    old = previous / "private"
    for pattern in ["pool*", "dev-*.png", "seed.json", "curator-board.png"]:
        for source in old.glob(pattern):
            shutil.copy2(source, private / source.name)
    prior = read(old / "curator-input.json")
    prompt = prior["prompt"]
    replacements = {
        "exactly three": "exactly two", "THREE DIFFERENT": "TWO DIFFERENT",
        "If three cannot": "If two cannot", "another chosen drawing": "the other chosen drawing",
    }
    for source, target in replacements.items():
        prompt = prompt.replace(source, target)
    prompt += "\nThis is a newly declared TWO-family feasibility pilot. The previous three-group requirement failed before any candidate was generated. Review the SAME source inventory affirmatively; do not inherit a pass from that rejection. Require exactly TWO distinct suitable source groups and construction families under ALL unchanged exclusion, purpose-profile, natural brief and alternative-validity conditions. If that is not established, reject. No extra source resampling or further curator call is permitted for this authoring version."
    png = (private / "curator-board.png").read_bytes()
    write(root / "authoring-commitment.json", {
        "created_at": datetime.now(timezone.utc).isoformat(), "version": "two-family-feasibility-pilot",
        "previous_authoring": str(previous), "previous_status_sha256": sha((previous / "curation-status.json").read_bytes()),
        "inventory_sha256": sha((private / "pool.json").read_bytes()), "same_inventory": True,
        "curator_calls_cap": 1, "required_families": 2, "required_source_packs": 2,
        "candidate_generation_calls_before_review": 0,
        "limitations": "Two independent groups can support a bounded pilot gate only, not broad professional generalization. No change of evaluator, purpose profiles, source exclusions, or accepted outcome after observing a candidate.",
    })
    write(private / "curator-input.json", {"prompt": prompt, "image_sha256": sha(png)})
    docker = ["wsl", "-e", "docker"]
    assert json.loads(subprocess.check_output(docker + ["image", "inspect", IMAGE]))[0]["Id"] == IMAGE_ID
    auth = {"openai-codex": read(Path("C:/Users/villa/.pi/agent/auth.json"))["openai-codex"]}
    result = subprocess.run(docker + ["run", "--rm", "-i", "--network", "bridge", IMAGE, "python3", "-c", PROGRAM],
        input=json.dumps({"auth": auth, "model": "gpt-6-astra", "prompt": prompt, "image": base64.b64encode(png).decode()}),
        capture_output=True, text=True, encoding="utf-8", timeout=390)
    (private / "curator-events.jsonl").write_text(result.stdout, encoding="utf-8")
    (private / "curator-stderr.txt").write_text(result.stderr, encoding="utf-8")
    events = [json.loads(x) for x in result.stdout.splitlines() if x.startswith("{")]
    assert not any(e.get("type") == "tool_execution_start" for e in events)
    messages = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
    assert result.returncode == 0 and messages and all(m.get("model") == "gpt-6-astra" for m in messages)
    assert messages[-1].get("stopReason") not in {"error", "aborted"}
    answer = "\n".join(x["text"] for x in messages[-1]["content"] if x.get("type") == "text").strip()
    if answer.startswith("```json"):
        answer = answer[7:-3].strip()
    review = json.loads(answer)
    write(private / "curation.json", review)
    write(root / "curation-status.json", {"passed": review["passed"], "selected_count": len(review["selected"]),
        "review_sha256": sha((private / "curation.json").read_bytes()), "model": "gpt-6-astra", "usage": messages[-1].get("usage")})
    if review["passed"]:
        preparation.ROOT = root
        preparation.materialize(expected_families=2)
    else:
        print(json.dumps({"passed": False, "selected_count": 0, "candidate_inference_authorized": False}))


if __name__ == "__main__":
    main()
