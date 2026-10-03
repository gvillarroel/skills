#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0", "numpy==2.2.6", "resvg-py==0.2.6", "scipy==1.16.2", "scikit-image==0.25.2", "defusedxml==0.7.1"]
# ///
"""Render explicit, matched development minibatch trials without rescoring."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_trial(study, index):
    dev = study / "run-async-compatible/harbor-trials/development"
    matches = list(dev.glob(f"{index:05d}-*/evaluation.json"))
    if len(matches) != 1:
        raise ValueError(f"Expected one development evaluation for index {index}")
    evaluation_path = matches[0]
    evaluation = json.loads(evaluation_path.read_text())
    provenance = evaluation["skillProvenance"]
    assert evaluation["evaluable"] and not evaluation["error"]
    assert provenance["verified"] and provenance["contentStableAfterTrial"]
    assert provenance["status"] == "verified"
    result_paths = list((evaluation_path.parent / "trials").glob("*/result.json"))
    assert len(result_paths) == 1
    result_path = result_paths[0]
    result = json.loads(result_path.read_text())
    assert result["exception_info"] is None
    assert result["task_name"] == evaluation["taskName"]
    assert result["agent_info"]["model_info"] == {"name": "gpt-6-luna", "provider": "openai-codex"}
    rewards = result["verifier_result"]["rewards"]
    assert rewards["artifact_valid"] == 1
    assert evaluation["reward"] == rewards["visual_similarity"]
    artifacts = list((result_path.parent / "artifacts").rglob("*.svg"))
    assert len(artifacts) == 1
    skill_path = evaluation_path.parent / "skills/svg-brief-design/SKILL.md"
    skill_hash = sha(skill_path)
    assert "sha256:" + skill_hash == provenance["candidateSkillMdDigest"]
    return {
        "index": index, "task": result["task_name"], "task_checksum": result["task_checksum"],
        "reward": rewards["visual_similarity"], "artifact_valid": rewards["artifact_valid"],
        "skill_md_sha256": skill_hash, "skill_bundle_digest": provenance["stagedDigest"],
        "provenance_verified": True, "model": "openai-codex/gpt-6-luna",
        "started_at": result["started_at"], "finished_at": result["finished_at"],
        "evaluation_path": str(evaluation_path.relative_to(study)), "evaluation_sha256": sha(evaluation_path),
        "native_result_path": str(result_path.relative_to(study)), "native_result_sha256": sha(result_path),
        "svg_path": str(artifacts[0].relative_to(study)), "svg_sha256": sha(artifacts[0]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--baseline-indices", type=int, nargs="+", required=True)
    parser.add_argument("--candidate-indices", type=int, nargs="+", required=True)
    parser.add_argument("--expected-baseline-sum", type=float, required=True)
    parser.add_argument("--expected-candidate-sum", type=float, required=True)
    args = parser.parse_args()
    study = args.study.resolve()
    run_path = study / "run-async-compatible/run.json"
    run = json.loads(run_path.read_text())
    assert run["generatedAt"] and run["source"] == "harbor-gepa"
    assert len(set(args.baseline_indices + args.candidate_indices)) == len(args.baseline_indices + args.candidate_indices)
    assert 1 <= len(args.baseline_indices) == len(args.candidate_indices) <= 12
    baseline = [read_trial(study, index) for index in args.baseline_indices]
    candidate = [read_trial(study, index) for index in args.candidate_indices]
    assert len({row["skill_md_sha256"] for row in baseline}) == 1
    assert len({row["skill_md_sha256"] for row in candidate}) == 1
    assert baseline[0]["skill_md_sha256"] != candidate[0]["skill_md_sha256"]
    original_hash = sha(study / "run-async-compatible/baseline-snapshot/skills/svg-brief-design/SKILL.md")
    assert baseline[0]["skill_md_sha256"] == original_hash
    assert len({row["task"] for row in baseline}) == len(baseline)
    assert {row["task"] for row in baseline} == {row["task"] for row in candidate}
    baseline_sum = sum(row["reward"] for row in baseline)
    candidate_sum = sum(row["reward"] for row in candidate)
    assert math.isclose(baseline_sum, args.expected_baseline_sum, abs_tol=1e-12, rel_tol=0)
    assert math.isclose(candidate_sum, args.expected_candidate_sum, abs_tol=1e-12, rel_tol=0)
    pairs = []
    for original in baseline:
        proposed = next(row for row in candidate if row["task"] == original["task"])
        assert original["task_checksum"] == proposed["task_checksum"]
        reference = args.benchmark / "datasets-v1.1/development" / original["task"] / "tests/reference.svg"
        pairs.append({"task": original["task"], "baseline": original, "candidate": proposed,
                      "delta": proposed["reward"] - original["reward"],
                      "reference_path": str(reference.relative_to(args.benchmark)), "reference_sha256": sha(reference)})
    sys.path.insert(0, str(args.benchmark / "scripts"))
    from compare_svg_v1_1 import render

    font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    heading = ImageFont.truetype(font_file, 24)
    text = ImageFont.truetype(font_file, 17)
    small = ImageFont.truetype(font_file, 14)
    cell, row_height, top = 360, 340, 146
    sheet = Image.new("RGB", (cell * 3, top + row_height * len(pairs)), "#edf3f3")
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 16), "SVG Brief Design: exact matched development minibatch", fill="#173a3d", font=heading)
    trial_note = f"Original trials {','.join(map(str, args.baseline_indices))} versus candidate {','.join(map(str, args.candidate_indices))}. Native rewards; no best-output selection."
    draw.text((20, 51), trial_note, fill="#426165", font=small)
    draw.text((20, 76), f"Mean original {baseline_sum/len(pairs):.6f} | candidate {candidate_sum/len(pairs):.6f} | candidate minus original {(candidate_sum-baseline_sum)/len(pairs):+.6f}", fill="#173a3d", font=text)
    labels = ["Reference", "Original: contemporaneous minibatch", "Rejected additive candidate"]
    for column, label in enumerate(labels):
        draw.text((column * cell + 18, 113), label, fill="#173a3d", font=text)
    for index, pair in enumerate(pairs):
        y = top + index * row_height
        draw.rectangle((8, y, sheet.width-8, y+row_height-8), fill="white")
        draw.text((18, y + 8), pair["task"].split("--")[0], fill="#173a3d", font=text)
        inputs = [args.benchmark / pair["reference_path"], study / pair["baseline"]["svg_path"], study / pair["candidate"]["svg_path"]]
        for column, source in enumerate(inputs):
            ink, _ = render(source.read_bytes())
            picture = Image.fromarray(np.uint8((1 - ink) * 255)).convert("RGB")
            picture = picture.resize((256, 256), Image.Resampling.LANCZOS)
            sheet.paste(picture, (column * cell + (cell - picture.width)//2, y + 37))
            if column:
                row = pair["baseline" if column == 1 else "candidate"]
                draw.text((column * cell + 18, y + 304), f"Trial {row['index']:02d} | visual {row['reward']:.6f}", fill="#426165", font=small)
    out = study / "review-minibatch"
    out.mkdir(exist_ok=False)
    sheet.save(out / "comparison.jpg", quality=95)
    summary = {"pair_count": len(pairs), "baseline_sum": baseline_sum, "candidate_sum": candidate_sum,
               "baseline_mean": baseline_sum / len(pairs), "candidate_mean": candidate_sum / len(pairs),
               "mean_delta": (candidate_sum-baseline_sum)/len(pairs)}
    manifest = {"schema_version": 1, "kind": "exact_matched_development_minibatch_review", "scores_recomputed": False,
                "selection": "Explicit native evaluation indices, verified against the recorded minibatch sums; no output selection by quality.",
                "limitations": "Three development tasks, one output per side; not full-set or private evidence. Rendered foreground is normalized for visual comparison.",
                "source_run_sha256": sha(run_path), "helper_sha256": sha(Path(__file__)),
                "verifier_script_sha256": sha(args.benchmark / "scripts/compare_svg_v1_1.py"),
                "gallery_sha256": sha(out / "comparison.jpg"), "summary": summary, "pairs": pairs}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(out), "summary": summary, "scores_recomputed": False}))


if __name__ == "__main__":
    main()
