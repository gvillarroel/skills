#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare reviewed knowledge censuses without substituting OCR for meaning."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

METRICS = ("named_records", "typed_relations", "temporal_anchors", "context_statements")


def validate(profile: dict, name: str) -> list[str]:
    if (not isinstance(profile, dict) or type(profile.get("schema_version")) is not int
        or profile.get("schema_version") != 1):
        raise ValueError(f"{name}: expected census schema version 1.")
    if profile.get("family") not in {"genealogy", "lineage", "timeline", "matrix"}:
        raise ValueError(f"{name}: unsupported reference family.")
    if profile.get("comparison_basis") != "same-full-poster-area":
        raise ValueError(f"{name}: use the same full poster area; resizing cannot increase the knowledge inventory.")
    if profile.get("counting_protocol") != "usefulcharts-knowledge-v1":
        raise ValueError(f"{name}: unsupported counting protocol.")
    if not isinstance(profile.get("counts"), dict) or set(profile["counts"]) != set(METRICS):
        raise ValueError(f"{name}: provide all four knowledge layers.")
    pending = []
    for metric in METRICS:
        value = profile["counts"][metric]
        if value is None:
            pending.append(f"{name}.{metric}: census incomplete")
            continue
        if (not isinstance(value, list) or len(value) != 2
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or not math.isfinite(v) or v < 0 or v != int(v) for v in value)
            or value[0] > value[1]):
            raise ValueError(f"{name}.{metric}: expected a nonnegative integer [lower, upper] interval.")
    if name == "reference" and profile["counts"]["named_records"] == [0, 0]:
        pending.append("reference: an empty subject cannot establish a dense-poster minimum")
    if profile.get("coverage") != "full-body":
        pending.append(f"{name}: full-body census required")
    if profile.get("method") not in {"manual-census", "svg-source-census"}:
        pending.append(f"{name}: OCR and pixel measurements are screening evidence only")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", str(profile.get("image_sha256", ""))):
        pending.append(f"{name}: identify the reviewed image by SHA-256")
    if not isinstance(profile.get("ledger"), str) or not profile["ledger"].strip():
        pending.append(f"{name}: provide a traceable census ledger")
    for review in ("census_review", "semantic_review", "legibility_review"):
        if profile.get(review) != "pass":
            pending.append(f"{name}.{review}: not passed")
    return pending


def compare(reference: dict, candidate: dict) -> dict:
    pending = validate(reference, "reference") + validate(candidate, "candidate")
    if reference["family"] != candidate["family"]:
        raise ValueError("Compare the same reference family; a sparse family cannot set another family's minimum.")
    checks = []
    for metric in METRICS:
        ref, cand = reference["counts"][metric], candidate["counts"][metric]
        if ref is None or cand is None:
            checks.append({"metric": metric, "status": "unknown"})
            continue
        needed, available = ref[1], cand[0]
        checks.append({
            "metric": metric, "reference_interval": ref, "candidate_interval": cand,
            "conservative_ratio": available/needed if needed else None,
            "shortfall": max(0, needed-available),
            "status": "pass" if available >= needed else "below-reference",
        })
    shortfall = any(check["status"] == "below-reference" for check in checks)
    status = "needs-evidence" if pending else "below-reference" if shortfall else "meets-measured-floor"
    return {
        "schema_version": 1, "status": status,
        "passes_measured_floor": status == "meets-measured-floor",
        "family": reference["family"], "minimum_ratio": 1,
        "checks": checks, "pending": pending,
        "reference_image_sha256": reference.get("image_sha256"),
        "candidate_image_sha256": candidate.get("image_sha256"),
        "scope": "Declared reviewed knowledge census only. Verify the ledger, source truth, actual image, spatial distribution and readability separately. This is not an aesthetic parity verdict.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--require-pass", action="store_true", help="Exit 1 when the completed comparison does not meet the measured floor.")
    args = parser.parse_args()
    try:
        if args.report.resolve() in {args.reference.resolve(), args.candidate.resolve()}:
            raise ValueError("The report must not overwrite a census input.")
        result = compare(json.loads(args.reference.read_text(encoding="utf-8-sig")),
                         json.loads(args.candidate.read_text(encoding="utf-8-sig")))
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(result))
        return 1 if args.require_pass and not result["passes_measured_floor"] else 0
    except (ValueError, OSError, TypeError) as error:
        print(f"Density comparison could not complete: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
