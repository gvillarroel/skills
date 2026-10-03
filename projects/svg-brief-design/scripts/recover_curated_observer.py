#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Preserve one interrupted stream and admit its first complete comparison only."""
import argparse
import json
import sys
from svg_excellence import REPO, read, sha, write, encode
from svg_curated_pairs import ROOT, CONFIG, ART_CONTEXT, observe_pair, validate

CASE = "d97f5ab71e4b937b51b2"


def observation_path(identity):
    if identity != CASE:
        return ROOT / "observations" / identity
    manifest = read(ROOT / "recovery-manifest.json")
    recovery = ROOT / manifest["effective_directory"]
    original = ROOT / "observations" / identity
    for name, digest in manifest["original_files"].items():
        if sha((original / name).read_bytes()) != digest:
            raise ValueError("Original interrupted evidence changed")
    for name, digest in manifest["effective_files"].items():
        if sha((recovery / name).read_bytes()) != digest:
            raise ValueError("Recovered evidence changed")
    return recovery


def recover():
    original = ROOT / "observations" / CASE
    if (original / "comparison.json").exists():
        raise ValueError("A complete semantic result must never be rerun")
    receipt = read(original / "receipt.json")
    events = [json.loads(x) for x in (original / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    messages = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
    if len(messages) != 1 or receipt["passed"] or messages[0].get("stopReason") != "error" or messages[0].get("errorMessage") != "terminated":
        raise ValueError("Not the single documented interrupted provider stream")
    partial = "".join(c.get("text", "") for c in messages[0].get("content", []) if c.get("type") == "text")
    try:
        json.loads(partial)
    except json.JSONDecodeError:
        pass
    else:
        raise ValueError("Complete JSON exists; do not repeat semantic evaluation")
    for path, digest in read(ROOT / "pre-inference-lock.json")["files"].items():
        if sha((REPO / path).read_bytes()) != digest:
            raise ValueError("Frozen calibration inputs changed")
    evidence = {p.name: sha(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    write(ROOT / "external-recovery-amendment.json", {
        "version": 1, "case": CASE, "original_files": evidence,
        "classification": "Provider stream stopped with error 'terminated' midway through an unterminated JSON string. Partial semantic text is retained; no complete comparison or score exists.",
        "scope": "One additional observer call, same prompt, images, model and container. No completed semantic evaluation may be repeated. This is Pi observer recovery, not a native Harbor recovery claim.",
        "selection": "First complete evaluable result, independent of quality or preference.",
        "additional_observer_calls": 1, "additional_jev_calls": 0,
        "partial_text_chars": len(partial), "original_budget": 32,
    })
    pair = next(p for p in read(ROOT / "pairs-coordinator-only.json") if p["id"] == CASE)
    target = ROOT / "recovery" / CASE
    observe_pair(pair, target)
    recovered = read(target / "receipt.json")
    for field in ("image_sha256", "prompt_sha256", "model", "image_id"):
        if recovered[field] != receipt[field]:
            raise ValueError("Recovery input drift: " + field)
    write(ROOT / "recovery-manifest.json", {
        "case": CASE, "original_files": evidence,
        "effective_directory": target.relative_to(ROOT).as_posix(),
        "effective_files": {p.name: sha(p.read_bytes()) for p in target.iterdir() if p.is_file()},
        "amendment_sha256": sha((ROOT / "external-recovery-amendment.json").read_bytes()),
        "selection": "First complete evaluable result; no outcome-based selection.",
    })
    print("Recovered one interrupted comparison; original failure retained.")


def score():
    out = ROOT / "judgments"
    rows = read(ROOT / "pairs-coordinator-only.json")
    records = []
    for pair in rows:
        obs = observation_path(pair["id"])
        receipt = read(obs / "receipt.json")
        if not receipt["passed"] or not receipt["image_seen"]:
            raise ValueError("Incomplete observation")
        records.append({"id": pair["id"], "brief": pair["brief"], "art_direction": ART_CONTEXT, "comparison": validate(read(obs / "comparison.json"))})
    out.mkdir(exist_ok=False)
    with (out / "records.jsonl").open("xb") as file:
        for record in sorted(records, key=lambda r: r["id"]):
            file.write(encode(record) + b"\n")
    write(out / "effective-inputs.json", {pair["id"]: {"directory": observation_path(pair["id"]).relative_to(ROOT).as_posix(), "comparison_sha256": sha((observation_path(pair["id"]) / "comparison.json").read_bytes())} for pair in rows})
    sys.path.insert(0, str(REPO / "skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    execute(CONFIG / "job.json", [out / "records.jsonl"], out / "jev")
    print("Completed first Jev decisions for all 32 effective comparisons.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["recover", "score"])
    args = parser.parse_args()
    {"recover": recover, "score": score}[args.mode]()
