#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify one D3 task and add candidate-bundle Pareto objectives."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import verify_task


EXCLUDED_PARTS = {".git", "__pycache__", "examples", "node_modules"}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def descending_score(value: int, best: int, zero: int) -> float:
    if zero <= best:
        raise ValueError("A bundle score requires zeroAtOrAbove > bestAtOrBelow")
    return clamp((zero - value) / (zero - best))


def runtime_files(skill_root: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_root.rglob("*")
        if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.parts)
    )


def root_reference_orphans(skill_root: Path) -> list[str]:
    references = skill_root / "references"
    root_files = sorted(references.glob("*.md")) if references.is_dir() else []
    markdown = [skill_root / "SKILL.md", *sorted(references.rglob("*.md"))]
    texts = {
        path: path.read_text(encoding="utf-8", errors="replace")
        for path in markdown
        if path.is_file()
    }
    orphans: list[str] = []
    for candidate in root_files:
        if not any(
            candidate.name in text
            for path, text in texts.items()
            if path != candidate
        ):
            orphans.append(candidate.name)
    return orphans


def bundle_profile(skill_root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    files = runtime_files(skill_root)
    skill_path = skill_root / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8", errors="replace")
    references = sorted((skill_root / "references").rglob("*.md"))
    file_count = len(files)
    byte_count = sum(path.stat().st_size for path in files)
    skill_lines = len(skill_text.splitlines())
    max_reference_bytes = max((path.stat().st_size for path in references), default=0)
    orphan_names = root_reference_orphans(skill_root)

    metrics = policy["metrics"]
    file_score = descending_score(
        file_count,
        int(metrics["runtimeFileCount"]["bestAtOrBelow"]),
        int(metrics["runtimeFileCount"]["zeroAtOrAbove"]),
    )
    byte_score = descending_score(
        byte_count,
        int(metrics["runtimeBytes"]["bestAtOrBelow"]),
        int(metrics["runtimeBytes"]["zeroAtOrAbove"]),
    )
    line_score = descending_score(
        skill_lines,
        int(metrics["skillLines"]["bestAtOrBelow"]),
        int(metrics["skillLines"]["zeroAtOrAbove"]),
    )
    reference_score = descending_score(
        max_reference_bytes,
        int(metrics["maxReferenceBytes"]["bestAtOrBelow"]),
        int(metrics["maxReferenceBytes"]["zeroAtOrAbove"]),
    )
    orphan_score = descending_score(
        len(orphan_names),
        int(metrics["orphanRootReferences"]["bestAtOrBelow"]),
        int(metrics["orphanRootReferences"]["zeroAtOrAbove"]),
    )

    progressive_weights = policy["progressiveDisclosureWeights"]
    progressive = (
        line_score * float(progressive_weights["skillLines"])
        + reference_score * float(progressive_weights["maxReferenceBytes"])
        + orphan_score * float(progressive_weights["orphanRootReferences"])
    )
    efficiency_weights = policy["bundleEfficiencyWeights"]
    efficiency = (
        file_score * float(efficiency_weights["runtimeFileCount"])
        + byte_score * float(efficiency_weights["runtimeBytes"])
        + progressive * float(efficiency_weights["progressiveDisclosure"])
    )

    findings: list[str] = []
    if "assets/examples" in skill_text.replace("\\", "/"):
        findings.append("SKILL.md routes normal use into acceptance examples")
    if re.search(r"skills/d3-(?:animated-svg|composition-evaluator|composition-recomposer|logo-design)", skill_text):
        findings.append("SKILL.md references a retired sibling D3 skill")

    return {
        "runtimeFileCount": file_count,
        "runtimeBytes": byte_count,
        "skillLines": skill_lines,
        "maxReferenceBytes": max_reference_bytes,
        "orphanRootReferenceCount": len(orphan_names),
        "orphanRootReferences": orphan_names,
        "componentScores": {
            "runtimeFileCount": round(file_score, 6),
            "runtimeBytes": round(byte_score, 6),
            "skillLines": round(line_score, 6),
            "maxReferenceBytes": round(reference_score, 6),
            "orphanRootReferences": round(orphan_score, 6),
        },
        "progressiveDisclosure": round(progressive, 6),
        "bundleEfficiency": round(efficiency, 6),
        "findings": findings,
    }


def combine_rewards(
    semantic_result: dict[str, Any], profile: dict[str, Any], policy: dict[str, Any]
) -> dict[str, Any]:
    rewards = dict(semantic_result["rewards"])
    semantic_reward = float(rewards["reward"])
    semantic_weight = float(policy["semanticWeight"])
    bundle_weight = float(policy["bundleWeight"])
    combined = (
        semantic_reward * semantic_weight
        + float(profile["bundleEfficiency"]) * bundle_weight
    )
    rewards.update(
        {
            "semantic_reward": semantic_reward,
            "bundle_efficiency": float(profile["bundleEfficiency"]),
            "progressive_disclosure": float(profile["progressiveDisclosure"]),
            "reward": round(combined, 6),
        }
    )
    return rewards


def main() -> int:
    workspace = Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    log_dir = Path(
        os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")
    ).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    contract = json.loads(
        (Path(__file__).with_name("contract.json")).read_text(encoding="utf-8")
    )
    if contract["route"] == "evaluation":
        semantic = verify_task.verify_evaluation(workspace, log_dir, contract)
    else:
        semantic = verify_task.verify_visual(workspace, log_dir, contract)

    skill_root = workspace / ".agents" / "skills" / "d3"
    profile = bundle_profile(skill_root, contract["bundleProfile"])
    rewards = combine_rewards(semantic, profile, contract["bundleProfile"])
    result = {
        "taskId": contract["taskId"],
        "route": contract["route"],
        "expectedColorset": contract["colorset"],
        **semantic,
        "rewards": rewards,
        "bundleProfile": profile,
    }
    diagnostics = {
        "status": "passed" if semantic["ok"] else "failed",
        "failure_domain": None if semantic["ok"] else "candidate",
        "terminal_outcome": "verified" if semantic["ok"] else "verifier_failed",
        "error_code": None if semantic["ok"] else "semantic_contract_failed",
    }
    (log_dir / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (log_dir / "bundle-profile.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (log_dir / "verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (log_dir / "reward.json").write_text(
        json.dumps(rewards, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if semantic["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
