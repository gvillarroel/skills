#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Enumerate an illustrative rare-shock sampling distribution; never run targets."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    scripts = args.skill.resolve() / "scripts"
    sys.path.insert(0, str(scripts))
    from analyze_simulation_hypotheses import analyze_point
    from run_simulation_experiment import normalize_spec
    from validate_simulation_bundle import audit_point_result

    if args.output_dir.exists():
        parser.error("output directory already exists; use a fresh destination")
    spec = json.loads((args.skill / "assets/templates/experiment.json").read_text("utf-8"))
    spec["replications"] = 32
    hypothesis = spec["hypotheses"][0]
    hypothesis["analysis"]["intervalLevel"] = 0.95
    if (hypothesis["analysis"]["primaryDesignPointIds"] != ["typical-demand"]
            or hypothesis["analysis"]["challengeDesignPointIds"] != ["low-demand"]):
        raise RuntimeError("the template family changed; review this frozen audit protocol")
    hypothesis["practicalThreshold"]["value"] = 0.005
    hypothesis["analysis"]["outcomeBounds"]["baseline"]["high"] = 0
    spec = normalize_spec(spec)
    normal_spec = copy.deepcopy(spec)
    normal_spec["hypotheses"][0]["analysis"].update(intervalMethod="normal-approximation-bonferroni")
    normal_spec["hypotheses"][0]["analysis"].pop("outcomeBounds")
    normal_spec = normalize_spec(normal_spec)
    n = spec["replications"]
    probabilities = (0.495, 0.495, 0.01)
    support = (0, 0.001, 1)
    truth = math.fsum(p*x for p, x in zip(probabilities, support))
    rows = []
    for shocks in range(n+1):
        for small in range(n-shocks+1):
            zero = n - shocks - small
            mass = (math.comb(n, shocks) * math.comb(n-shocks, small)
                    * probabilities[0]**zero * probabilities[1]**small * probabilities[2]**shocks)
            values = [0]*zero + [0.001]*small + [1]*shocks
            outcomes, seeds = [], {}
            for arm, sample in (("baseline-stock", [0]*n), ("higher-stock", values)):
                for index, value in enumerate(sample):
                    identity = f"{arm}-{index}"
                    outcomes.append({
                        "run_id": identity, "coupling_id": f"pair-{index}",
                        "scenario_id": arm, "design_point_id": "typical-demand",
                        "outcome_name": "fill_rate", "value": str(value),
                    })
                    seeds[identity] = index
            record = {"zero_count": zero, "small_count": small, "shock_count": shocks, "sample_probability": mass}
            for label, used_spec in (("normal", normal_spec), ("bounded", spec)):
                arguments = (used_spec, used_spec["hypotheses"][0], "typical-demand", "primary", outcomes, seeds)
                result = analyze_point(*arguments)
                audit = audit_point_result(*arguments, "mean-difference-v3")
                if result != audit:
                    raise RuntimeError("independent interval recomputation differs")
                record.update({
                    f"{label}_low": result["interval"]["low"],
                    f"{label}_high": result["interval"]["high"],
                    f"{label}_covers_mean": result["interval"]["low"] <= truth <= result["interval"]["high"],
                    f"{label}_status": result["status"],
                })
            rows.append(record)
    if not math.isclose(math.fsum(row["sample_probability"] for row in rows), 1, abs_tol=1e-14):
        raise RuntimeError("enumerated sampling mass is not one")
    aggregate = {}
    for label in ("normal", "bounded"):
        aggregate[label] = {
            "mean_interval_coverage": math.fsum(r["sample_probability"] for r in rows if r[f"{label}_covers_mean"]),
            "erroneous_challenge_probability": math.fsum(r["sample_probability"] for r in rows if r[f"{label}_status"] == "challenges"),
            "inconclusive_probability": math.fsum(r["sample_probability"] for r in rows if r[f"{label}_status"] == "inconclusive"),
        }
    if aggregate["normal"]["erroneous_challenge_probability"] < 0.72:
        raise RuntimeError("normal-method development counterexample no longer reproduces")
    if aggregate["bounded"]["mean_interval_coverage"] < 0.975:
        raise RuntimeError("bounded method misses its conditional marginal guarantee")
    summary = {
        "review": "simulation-methodology-20260906", "source_type": "simulated",
        "execution": "exact finite-distribution enumeration; no target or inference calls",
        "scope": "one point in a predeclared two-point family; a development counterexample, not empirical calibration",
        "outcome_interpretation": "a hypothetical bounded loss in unit 1; template names are test plumbing, not inventory evidence",
        "distribution": [{"value": x, "probability": p} for p, x in zip(probabilities, support)],
        "baseline": 0, "true_mean_contrast": truth, "threshold": 0.005,
        "replications": n, "family_size": 2, "family_level": 0.95, "marginal_level": 0.975,
        "count_vectors": len(rows), "independent_recomputations": len(rows)*2,
        "results": aggregate,
        "code_sha256": {
            "audit": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            **{name: hashlib.sha256((scripts/name).read_bytes()).hexdigest() for name in (
                "analyze_simulation_hypotheses.py", "validate_simulation_bundle.py", "run_simulation_experiment.py",
            )},
        },
        "template_sha256": hashlib.sha256((args.skill / "assets/templates/experiment.json").read_bytes()).hexdigest(),
    }
    args.output_dir.mkdir(parents=True)
    with (args.output_dir / "sampling-distribution.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "coverage-audit.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
