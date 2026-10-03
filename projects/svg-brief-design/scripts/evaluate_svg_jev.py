#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Trusted Harbor verifier entrypoint: judge one SVG using a sealed expert bundle."""
import argparse
from pathlib import Path
import re
import sys

from svg_excellence import aggregate, collect, encode, judge_record, make_evidence, read, sha, write


def validate_bundle(bundle):
    bundle = Path(bundle).resolve()
    lock = read(bundle/"lock.json")
    for relative, expected in lock["files"].items():
        path = (bundle/relative).resolve()
        if not path.is_relative_to(bundle) or not path.is_file() or sha(path.read_bytes()) != expected:
            raise ValueError("Frozen evaluator file mismatch: " + relative)
    return lock


def evaluate(bundle, artifact, request_path, contract_path, output):
    bundle, artifact, output = Path(bundle), Path(artifact), Path(output)
    lock = validate_bundle(bundle)
    rubric = read(bundle/"rubric.json")
    request = Path(request_path).read_text(encoding="utf-8")
    declared = re.search(r"`(/logs/artifacts/[^`]+\.svg)`", request)
    if declared and artifact.as_posix() != declared.group(1):
        raise ValueError("Verifier was configured for a different delivery path")
    output.mkdir(parents=True, exist_ok=True)
    if any((output/name).exists() for name in ("reward.json", "metrics.json", "prepared", "jev")):
        raise ValueError("Preserve the existing verification; use a new run")
    if artifact.exists():
        evidence = make_evidence(artifact.read_bytes(), request, read(contract_path), bundle/"fonts", output/"render.png")
    else:
        evidence = {"artifact_valid": False, "hard_failure": "The exact requested SVG file is missing", "artifact_sha256": None}
    write(output/"evidence.json", evidence)
    if not evidence["artifact_valid"]:
        result = aggregate(evidence, {}, rubric)
    else:
        prepared = output/"prepared"
        identity = sha(encode({"request": request, "artifact": evidence["artifact_sha256"]}))[:20]
        evidence_path = prepared/"evidence"/(identity+".json")
        write(evidence_path, evidence)
        (prepared/"records.jsonl").write_bytes(encode(judge_record(evidence, identity))+b"\n")
        write(prepared/"manifest.json", {"records_sha256": sha((prepared/"records.jsonl").read_bytes()),
              "items": [{"id": identity, "artifact_valid": True, "evidence_sha256": sha(evidence_path.read_bytes())}]})
        sys.path.insert(0, str(bundle/"scripts"))
        from jev_batch import execute
        execute(bundle/"job.json", [prepared/"records.jsonl"], output/"jev")
        completed = collect(prepared, output/"jev", output/"judgments.json", bundle/"rubric.json")
        if completed["observed_models"] != lock["observed_models"]:
            raise ValueError("Jev served a different model version; recalibration is required")
        result = completed["results"][0]
    validate_bundle(bundle)
    write(output/"metrics.json", result | {"evaluator_lock_sha256": sha((bundle/"lock.json").read_bytes()),
           "verifier_version": rubric["version"], "reference_similarity_used": False})
    if result["technical_excellence"] is None:
        raise ValueError("Jev abstained; no numeric reward is fabricated")
    write(output/"reward.json", {"technical_excellence": result["technical_excellence"],
          "artifact_valid": float(evidence["artifact_valid"])})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(args.bundle, args.artifact, args.request, args.contract, args.out)
        print(encode({key: result[key] for key in ("status", "score_100")} ).decode())
    except Exception as exc:
        print("Verification did not produce a reward: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
