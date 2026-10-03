#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0", "numpy==2.2.6", "resvg-py==0.2.6", "scipy==1.16.2", "scikit-image==0.25.2", "defusedxml==0.7.1"]
# ///
"""Render completed-study outputs outside the skill; never recalculate fitness."""
from pathlib import Path
import argparse
import hashlib
import json
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--development-pool", action="store_true", help="Review all fully evaluated development candidates; never a promotion decision")
    args = parser.parse_args()
    run_root = args.study / "run-async-compatible"
    run = json.loads((run_root / "run.json").read_text())
    sys.path.insert(0, str(args.benchmark / "scripts"))
    from compare_svg_v1_1 import render
    candidate_hash = hashlib.sha256((run_root / "candidate-skill/SKILL.md").read_bytes()).hexdigest()
    baseline_hash = hashlib.sha256((run_root / "baseline-snapshot/skills/svg-brief-design/SKILL.md").read_bytes()).hexdigest()
    pool_hashes = [baseline_hash, candidate_hash]
    score_maps = {}
    if args.development_pool:
        candidates = json.loads((run_root / "gepa/candidates.json").read_text())
        pool_hashes = [hashlib.sha256(row["current_candidate"].encode()).hexdigest() for row in candidates]
        # Locally produced GEPA state, outside agent-writable environments.
        with (run_root / "gepa/gepa_state.bin").open("rb") as handle:
            state = pickle.load(handle)
        score_maps = dict(zip(pool_hashes, state["prog_candidate_val_subscores"]))
        evolution_tasks = json.loads((args.study / "evolution-async-compatible.json").read_text())["splits"]["evolution"]
        task_positions = {Path(path).name: index for index, path in enumerate(evolution_tasks)}
    rows = []
    for evaluation_path in sorted((run_root / "harbor-trials").glob("*/*/evaluation.json")):
        evaluation = json.loads(evaluation_path.read_text())
        if evaluation["skillProvenance"].get("status") == "candidate-rejected":
            continue
        phase = evaluation_path.parent.parent.name
        skill_hash = evaluation["skillProvenance"]["candidateSkillMdDigest"].removeprefix("sha256:")
        if skill_hash not in set(pool_hashes):
            continue
        result_path = next((evaluation_path.parent / "trials").glob("*/result.json"))
        trial = result_path.parent
        result = json.loads(result_path.read_text())
        if args.development_pool:
            if phase != "development":
                continue
            expected_score = score_maps[skill_hash][task_positions[result["task_name"]]]
            if abs(evaluation["reward"] - expected_score) > 1e-12:
                continue
        artifact = next(iter((trial / "artifacts").rglob("*.svg")), None)
        rows.append({"phase": phase, "task": result["task_name"], "hash": skill_hash, "artifact": artifact, "reward": evaluation.get("reward"), "native_result": str(result_path.relative_to(args.study))})
    out = args.study / ("review-development-pool" if args.development_pool else "review")
    out.mkdir(exist_ok=True)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 16)
    small = ImageFont.truetype(font_path, 13)
    title = ImageFont.truetype(font_path, 23)
    manifests = []
    for phase in ("development", "validation", "holdout"):
        phase_rows = [row for row in rows if row["phase"].startswith(phase)]
        if not phase_rows:
            continue
        names = sorted({row["task"] for row in phase_rows})
        repeats = 1 if phase == "development" else 3
        sides = tuple(pool_hashes) if args.development_pool else ((baseline_hash,) if candidate_hash == baseline_hash else (baseline_hash, candidate_hash))
        labels = ["Reference"] + [f"Baseline {i+1}" for i in range(repeats)]
        if args.development_pool:
            labels = ["Reference", "Original guide"] + [f"GEPA pool candidate {i}" for i in range(1, len(sides))]
        elif len(sides) == 2:
            labels += [f"Candidate {i+1}" for i in range(repeats)]
        cell_width, row_height = 280, 280
        sheet = Image.new("RGB", (cell_width * len(labels), 112 + row_height * len(names)), "#eef3f3")
        draw = ImageDraw.Draw(sheet)
        draw.text((20, 15), f"SVG Brief Design - {phase}", fill="#173a3d", font=title)
        note = "Exact full-set GEPA outputs; all fully evaluated candidates, including regressions." if args.development_pool else ("First observed output per task and side; selection uses the full GEPA record." if phase == "development" else "All three preregistered attempts per task and side; no best-output selection.")
        draw.text((20, 51), note, fill="#426165", font=small)
        for i, label in enumerate(labels):
            draw.text((i * cell_width + 18, 82), label, fill="#173a3d", font=font)
        for row_index, task in enumerate(names):
            y = 110 + row_index * row_height
            draw.rectangle((8, y, sheet.width - 8, y + row_height - 8), fill="white")
            draw.text((18, y + 8), task.split("--")[0], fill="#173a3d", font=font)
            reference = (args.benchmark / "datasets-v1.1/development" / task / "tests/reference.svg") if phase == "development" else (args.private / "validation-v1.1" / task / "tests/reference.svg")
            selected = []
            for wanted in sides:
                selected += [row for row in phase_rows if row["task"] == task and row["hash"] == wanted][:repeats]
            assert len(selected) == len(sides) * repeats, (phase, task, "missing review artifact")
            paths = [reference] + [row["artifact"] for row in selected]
            for column, path in enumerate(paths):
                if path is None:
                    continue
                try:
                    ink, _ = render(path.read_bytes())
                    picture = Image.fromarray(np.uint8((1 - ink) * 255)).convert("RGB")
                    picture.thumbnail((230, 215))
                    sheet.paste(picture, (column * cell_width + (cell_width - picture.width) // 2, y + 35))
                except Exception as error:
                    draw.text((column * cell_width + 18, y + 110), type(error).__name__, fill="#983131", font=small)
                if column:
                    score = selected[column - 1]["reward"]
                    label = "Unavailable" if score is None else f"Visual {score:.3f}"
                    draw.text((column * cell_width + 18, y + 249), label, fill="#426165", font=small)
            manifests.append({"phase": phase, "task": task, "attempts": [{key: value for key, value in row.items() if key != "artifact"} for row in selected]})
        sheet.save(out / f"{phase}.jpg", quality=95)
    (out / "manifest.json").write_text(json.dumps(manifests, indent=2))
    print(json.dumps({"rendered": [p.name for p in out.glob("*.jpg")], "source_run_complete": True, "scores_recomputed": False}))


if __name__ == "__main__":
    main()
