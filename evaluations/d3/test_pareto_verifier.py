#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for D3 Pareto bundle objectives."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from verify_pareto_task import bundle_profile, combine_rewards


POLICY = {
    "semanticWeight": 0.9,
    "bundleWeight": 0.1,
    "metrics": {
        "runtimeFileCount": {"bestAtOrBelow": 3, "zeroAtOrAbove": 13},
        "runtimeBytes": {"bestAtOrBelow": 100, "zeroAtOrAbove": 1100},
        "skillLines": {"bestAtOrBelow": 10, "zeroAtOrAbove": 110},
        "maxReferenceBytes": {"bestAtOrBelow": 50, "zeroAtOrAbove": 550},
        "orphanRootReferences": {"bestAtOrBelow": 0, "zeroAtOrAbove": 4},
    },
    "progressiveDisclosureWeights": {
        "skillLines": 0.5,
        "maxReferenceBytes": 0.25,
        "orphanRootReferences": 0.25,
    },
    "bundleEfficiencyWeights": {
        "runtimeFileCount": 0.45,
        "runtimeBytes": 0.2,
        "progressiveDisclosure": 0.35,
    },
}


def write_skill(root: Path, *, lines: int, orphan_count: int, filler_bytes: int) -> None:
    references = root / "references"
    references.mkdir(parents=True)
    names = [f"route-{index}.md" for index in range(orphan_count)]
    body = ["---", "name: d3", "description: Test D3 skill.", "---"]
    body.extend(f"Instruction {index}." for index in range(max(0, lines - len(body))))
    (root / "SKILL.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    for name in names:
        (references / name).write_text("x" * filler_bytes, encoding="utf-8")


class ParetoVerifierTests(unittest.TestCase):
    def test_smaller_routed_bundle_scores_higher(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bulky = root / "bulky"
            lean = root / "lean"
            write_skill(bulky, lines=100, orphan_count=4, filler_bytes=500)
            write_skill(lean, lines=10, orphan_count=0, filler_bytes=10)
            bulky_profile = bundle_profile(bulky, POLICY)
            lean_profile = bundle_profile(lean, POLICY)
            self.assertGreater(
                lean_profile["bundleEfficiency"], bulky_profile["bundleEfficiency"]
            )
            self.assertGreater(
                lean_profile["progressiveDisclosure"],
                bulky_profile["progressiveDisclosure"],
            )

    def test_acceptance_examples_are_excluded_from_runtime_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "d3"
            write_skill(root, lines=10, orphan_count=0, filler_bytes=10)
            example = root / "assets" / "examples" / "gallery" / "large.js"
            example.parent.mkdir(parents=True)
            example.write_text("x" * 10000, encoding="utf-8")
            profile = bundle_profile(root, POLICY)
            self.assertEqual(profile["runtimeFileCount"], 1)

    def test_combined_reward_preserves_semantic_priority(self) -> None:
        profile = {"bundleEfficiency": 1.0, "progressiveDisclosure": 1.0}
        passed = combine_rewards({"rewards": {"reward": 1.0}}, profile, POLICY)
        failed = combine_rewards({"rewards": {"reward": 0.0}}, profile, POLICY)
        self.assertEqual(passed["reward"], 1.0)
        self.assertEqual(failed["reward"], 0.1)
        self.assertGreater(passed["reward"], failed["reward"])


if __name__ == "__main__":
    unittest.main()
