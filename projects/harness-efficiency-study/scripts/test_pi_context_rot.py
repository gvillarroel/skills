#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic tests for the offline Pi context-rot simulator."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
SOURCE_DIR = PROJECT_ROOT / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import pi_context_rot as model

COST_BUNDLE = (
    REPOSITORY_ROOT
    / "evaluations"
    / "harness-efficiency-study"
    / "20260904"
    / "pi-cost-elasticity"
)
EVIDENCE_CSV = PROJECT_ROOT / "source" / "context-rot-evidence-20260904.csv"


class ContextRotUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.study = model.build_study(COST_BUNDLE, EVIDENCE_CSV, monte_carlo_tasks=0)
        cls.aggregates = {
            (row["parameter_set_id"], row["model"], row["strategy_id"]): row
            for row in cls.study["aggregates"]
        }

    def test_fixed_100k_excess_auc_primary_oracle(self) -> None:
        prompts = list(range(40_000, 800_001, 20_000))
        self.assertEqual(len(prompts), 39)
        self.assertAlmostEqual(
            model.normalized_excess_auc(prompts, 200_000),
            31.0 / 13.0,
            places=14,
        )
        # The fixed 100k denominator makes onset sensitivities comparable.
        self.assertAlmostEqual(
            model.normalized_excess_auc([200_000, 300_000], 200_000),
            0.5,
            places=15,
        )

    def test_cost_bundle_yields_exact_compaction_positions(self) -> None:
        rows = [
            row
            for row in self.study["trajectories"]
            if row["model"] == "luna"
            and row["strategy_id"] == "cap_200k_uncached"
            and float(row["onset_tokens"]) == 200_000.0
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            json.loads(rows[0]["compaction_positions_json"]), [9, 18, 27, 36]
        )
        self.assertEqual(rows[0]["main_call_count"], 39)

    def test_uniform_evidence_fidelity_oracles(self) -> None:
        positions = [9, 18, 27, 36]
        self.assertEqual(model.effective_evidence_fidelity(39, positions, 1.0), 1.0)
        f = 0.95
        expected = (9 * f**4 + 9 * f**3 + 9 * f**2 + 9 * f + 3) / 39
        self.assertAlmostEqual(
            model.effective_evidence_fidelity(39, positions, f, "uniform"),
            expected,
            places=15,
        )
        self.assertAlmostEqual(expected, 0.8902418269230765, places=15)

    def test_evidence_profiles_have_expected_order(self) -> None:
        positions = [9, 18, 27, 36]
        front = model.effective_evidence_fidelity(39, positions, 0.9, "front_loaded")
        uniform = model.effective_evidence_fidelity(39, positions, 0.9, "uniform")
        back = model.effective_evidence_fidelity(39, positions, 0.9, "back_loaded")
        self.assertLess(front, uniform)
        self.assertLess(uniform, back)

    def test_null_and_monotonic_quality_controls(self) -> None:
        p0 = 0.8
        self.assertAlmostEqual(
            model.single_attempt_probability(p0, 0.0, 99.0, 1.0), p0, places=15
        )
        low_beta = model.single_attempt_probability(p0, 0.25, 2.0, 1.0)
        high_beta = model.single_attempt_probability(p0, 1.0, 2.0, 1.0)
        lower_fidelity = model.single_attempt_probability(p0, 0.25, 2.0, 0.9)
        self.assertLess(high_beta, low_beta)
        self.assertLess(lower_fidelity, low_beta)

    def test_exact_capped_retry_formulas_and_cost(self) -> None:
        completion, attempts = model.capped_retry_metrics(0.8, 3)
        self.assertAlmostEqual(completion, 0.992, places=15)
        self.assertAlmostEqual(attempts, 1.24, places=15)
        self.assertAlmostEqual(2.0 * attempts / completion, 2.5, places=15)
        self.assertEqual(model.capped_retry_metrics(0.0, 3), (0.0, 3.0))
        self.assertEqual(model.capped_retry_metrics(1.0, 3), (1.0, 1.0))

    def test_primary_luna_numerical_oracle(self) -> None:
        grow = self.aggregates[(model.PRIMARY_PARAMETER_ID, "luna", "grow_to_800k")]
        compact = self.aggregates[
            (model.PRIMARY_PARAMETER_ID, "luna", "cap_200k_uncached")
        ]
        self.assertAlmostEqual(float(grow["normalized_excess_auc"]), 31 / 13, places=14)
        self.assertAlmostEqual(
            float(grow["completion_probability"]), 0.9214844732483582, places=14
        )
        self.assertAlmostEqual(
            float(grow["expected_attempts"]), 1.499785645530507, places=14
        )
        self.assertAlmostEqual(
            float(grow["provider_cost_per_successful_session_usd"]),
            1.6607781434499127,
            places=14,
        )
        self.assertAlmostEqual(
            float(compact["effective_evidence_fidelity"]),
            0.8902418269230765,
            places=14,
        )
        self.assertAlmostEqual(
            float(compact["completion_probability"]), 0.9672265155858337, places=14
        )
        self.assertAlmostEqual(
            float(compact["provider_cost_per_successful_session_usd"]),
            0.8156465591590609,
            places=14,
        )

    def test_scale_rows_are_algebraic_not_materialized_sessions(self) -> None:
        rows = [
            row
            for row in self.study["scales"]
            if row["parameter_set_id"] == model.PRIMARY_PARAMETER_ID
            and row["model"] == "luna"
            and row["strategy_id"] == "cap_200k_uncached"
            and row["assigned_sessions"] == 1_000_000
        ]
        self.assertEqual(len(rows), 1)
        aggregate = self.aggregates[
            (model.PRIMARY_PARAMETER_ID, "luna", "cap_200k_uncached")
        ]
        self.assertAlmostEqual(
            rows[0]["expected_completed_sessions"],
            1_000_000 * float(aggregate["completion_probability"]),
            places=8,
        )
        self.assertAlmostEqual(
            rows[0]["expected_provider_spend_usd"],
            1_000_000 * float(aggregate["provider_cost_per_assigned_session_usd"]),
            places=8,
        )

    def test_evidence_blanks_are_retained_and_ineligible(self) -> None:
        base = next(
            row
            for row in self.study["evidence_curves"]
            if row["evidence_id"] == "nolima-gpt41-base"
        )
        self.assertFalse(base["anchor_eligible"])
        self.assertIsNone(base["reference_evidence_id"])
        self.assertIsNone(base["retention"])
        paired = next(
            row
            for row in self.study["evidence_curves"]
            if row["evidence_id"] == "chroma-gpt41-paired-difference"
        )
        self.assertFalse(paired["anchor_eligible"])
        self.assertIsNone(paired["retention"])

    def test_evidence_anchor_policy_and_no_extrapolation(self) -> None:
        nolima_1k = next(
            row
            for row in self.study["evidence_curves"]
            if row["evidence_id"] == "nolima-gpt41-1k"
        )
        chroma_focused = next(
            row
            for row in self.study["evidence_curves"]
            if row["evidence_id"] == "chroma-gpt41-focused"
        )
        self.assertTrue(nolima_1k["anchor_eligible"])
        self.assertEqual(nolima_1k["retention"], 1.0)
        self.assertTrue(chroma_focused["anchor_eligible"])
        chroma_50 = next(
            row
            for row in self.study["evidence_onsets"]
            if row["series_id"] == "chroma-gpt41-longmemeval-reanalysis"
            and row["retention_threshold"] == 0.5
        )
        self.assertEqual(chroma_50["threshold_status"], "unidentifiable")
        self.assertIsNone(chroma_50["interpolated_context_tokens"])

    def test_log2_interpolation_hand_oracle(self) -> None:
        def row(evidence_id: str, context: str, score: str) -> dict[str, str]:
            result = {column: "" for column in model.EVIDENCE_INPUT_COLUMNS}
            result.update(
                {
                    "evidence_id": evidence_id,
                    "series_id": "hand-series",
                    "study": "hand",
                    "model": "hand",
                    "task": "hand",
                    "metric": "accuracy",
                    "context_tokens": context,
                    "score": score,
                    "score_unit": "proportion",
                    "evidence_status": "source-reported",
                    "numeric_precision": "exact",
                }
            )
            return result

        _curves, onsets = model.build_evidence_tables(
            [row("hand-low", "100", "1"), row("hand-high", "400", "0")]
        )
        threshold = next(item for item in onsets if item["retention_threshold"] == 0.5)
        self.assertEqual(threshold["threshold_status"], "interpolated")
        self.assertAlmostEqual(
            threshold["interpolated_context_tokens"], 200.0, places=12
        )

    def test_primary_decision_boundaries_are_identified(self) -> None:
        self.assertEqual(len(self.study["fidelity_boundaries"]), 6)
        for row in self.study["fidelity_boundaries"]:
            self.assertIn(
                row["minimum_fidelity_cost_status"],
                {"already_satisfied_at_lower_bound", "identified_by_bisection"},
            )
            self.assertEqual(
                row["minimum_fidelity_completion_slo_status"], "identified_by_bisection"
            )
            self.assertIn(
                row["minimum_beta_cost_status"],
                {"already_satisfied_at_lower_bound", "identified_by_bisection"},
            )
            self.assertGreaterEqual(row["minimum_fidelity_completion_slo"], 0.0)
            self.assertLessEqual(row["minimum_fidelity_completion_slo"], 1.0)
        luna_uncached = next(
            row
            for row in self.study["fidelity_boundaries"]
            if row["model"] == "luna"
            and row["comparison_strategy_id"] == "cap_200k_uncached"
        )
        self.assertAlmostEqual(
            luna_uncached["minimum_fidelity_cost_per_success_not_above_grow"],
            0.227542712636023,
            places=11,
        )
        self.assertAlmostEqual(
            luna_uncached["minimum_fidelity_completion_slo"],
            0.839632455535138,
            places=11,
        )
        self.assertEqual(
            luna_uncached["minimum_beta_at_f095_cost_per_success_not_above_grow"], 0.0
        )

    def test_monte_carlo_sentinel_is_seed_repeatable(self) -> None:
        first = model._monte_carlo_rows(
            self.study["aggregates"],
            self.study["strata"],
            2_000,
            model.MONTE_CARLO_SEED,
        )
        second = model._monte_carlo_rows(
            self.study["aggregates"],
            self.study["strata"],
            2_000,
            model.MONTE_CARLO_SEED,
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 6)
        self.assertTrue(all(row["task_count"] == 2_000 for row in first))

    def test_bundle_is_deterministic_and_self_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            model.write_bundle(first, self.study)
            model.write_bundle(second, self.study)
            self.assertEqual(
                (first / "checksums.sha256").read_bytes(),
                (second / "checksums.sha256").read_bytes(),
            )
            manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["execution_mode"], "offline-statistical-simulation"
            )
            self.assertFalse(manifest["real_pi_or_copilot_or_model_calls"])
            self.assertEqual(
                manifest["input_files"]["pi-context-rot-spec-20260904.json"]["sha256"],
                hashlib.sha256(
                    (
                        PROJECT_ROOT / "source" / "pi-context-rot-spec-20260904.json"
                    ).read_bytes()
                ).hexdigest(),
            )
            checksum_lines = (
                (first / "checksums.sha256").read_text(encoding="utf-8").splitlines()
            )
            self.assertNotIn(
                "checksums.sha256", {line.split("  ", 1)[1] for line in checksum_lines}
            )
            for line in checksum_lines:
                expected, filename = line.split("  ", 1)
                actual = hashlib.sha256((first / filename).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)
            self.assertNotIn(
                b"\r\n",
                gzip.decompress(
                    (first / "quality-aggregate-results.csv.gz").read_bytes()
                ),
            )

    def test_large_tables_use_canonical_deterministic_gzip(self) -> None:
        logical_hashes = {
            "break-even.csv.gz": "0537d6bcfb01988db9acd09a96512091930b27da78978004159e6343c43cfaba",
            "quality-aggregate-results.csv.gz": "1f1d2c4fcc497e006e5f62bb5e984a59fabac19aa08d7e5b8b26cb483f8321bb",
            "quality-contrast-results.csv.gz": "28c13cc48a22e78855207417b20ab23c9ac2928bd66bc63e426e2c92a02e3ac4",
            "quality-stratum-results.csv.gz": "6099963164a54e8068ae2ab0fda4a68af8413db8d161e05a7c9b413780e461d4",
            "scale-results.csv.gz": "cead36aeac832b76d080d3fc623a4f639eef98037d9e987a7cdf36f5d5bde199",
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            model.write_bundle(output, self.study)
            manifest = json.loads((output / "manifest.json").read_text("utf-8"))
            self.assertEqual(set(model.GZIP_ARTIFACTS), set(logical_hashes))
            for filename, expected_hash in logical_hashes.items():
                stored = (output / filename).read_bytes()
                self.assertEqual(stored[:3], b"\x1f\x8b\x08")
                self.assertEqual(stored[3], 0)
                self.assertEqual(int.from_bytes(stored[4:8], "little"), 0)
                self.assertEqual(stored[8], 2)
                self.assertEqual(stored[9], 255)
                logical = gzip.decompress(stored)
                self.assertNotIn(b"\r\n", logical)
                self.assertEqual(hashlib.sha256(logical).hexdigest(), expected_hash)
                metadata = manifest["artifacts"][filename]
                self.assertEqual(metadata["uncompressed_sha256"], expected_hash)
                self.assertEqual(metadata["uncompressed_bytes"], len(logical))
                self.assertEqual(metadata["compression"]["format"], "gzip")
                self.assertEqual(metadata["compression"]["level"], 9)
                self.assertEqual(metadata["compression"]["mtime"], 0)
                self.assertEqual(metadata["compression"]["original_filename"], "")
                self.assertFalse((output / filename.removesuffix(".gz")).exists())

    def test_every_csv_has_declared_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            model.write_bundle(output, self.study)
            dictionary = json.loads(
                (output / "data-dictionary.json").read_text(encoding="utf-8")
            )
            for filename, table in dictionary["tables"].items():
                path = output / filename
                with (
                    gzip.open(path, "rt", encoding="utf-8", newline="")
                    if path.suffix == ".gz"
                    else path.open("r", encoding="utf-8", newline="")
                ) as handle:
                    header = next(csv.reader(handle))
                self.assertEqual(
                    header, [column["name"] for column in table["columns"]]
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
