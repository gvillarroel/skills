#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for candidate-bound D3 Harbor job configs."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from build_harbor_dataset import write_job_config


class CandidateJobConfigTests(unittest.TestCase):
    def test_binds_agent_and_environment_to_same_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_root = root / "run"
            repo_root = root / "repo"
            candidate = root / "selected" / "d3"
            output = run_root / "configs" / "candidate-job.yaml"
            (run_root / "development").mkdir(parents=True)
            candidate.mkdir(parents=True)
            (candidate / "SKILL.md").write_text("---\nname: d3\ndescription: Test.\n---\n", encoding="utf-8")

            write_job_config(
                run_root,
                repo_root,
                "development",
                "candidate-development",
                3,
                4,
                "gpt-5.3-codex-spark",
                skill_source=candidate,
                config_path=output,
                job_name="candidate-development",
            )

            config = output.read_text(encoding="utf-8")
            candidate_text = candidate.resolve().as_posix()
            self.assertEqual(config.count(candidate_text), 2)
            self.assertTrue(output.is_file())
            self.assertIn((run_root / "development").as_posix(), config)
            self.assertNotIn((repo_root / "skills" / "d3").as_posix(), config)

    def test_can_bind_candidate_only_through_agent_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_root = root / "run"
            repo_root = root / "repo"
            candidate = root / "selected" / "d3"
            output = run_root / "candidate-job.yaml"
            jobs_dir = root / "evidence" / "jobs"
            (run_root / "validation").mkdir(parents=True)
            candidate.mkdir(parents=True)
            (candidate / "SKILL.md").write_text("---\nname: d3\ndescription: Test.\n---\n", encoding="utf-8")

            write_job_config(
                run_root,
                repo_root,
                "validation",
                "candidate-validation",
                2,
                4,
                "gpt-5.3-codex-spark",
                skill_source=candidate,
                config_path=output,
                job_name="candidate-validation",
                prime_environment_skill=False,
                jobs_dir=jobs_dir,
            )

            config = output.read_text(encoding="utf-8")
            candidate_text = candidate.resolve().as_posix()
            self.assertEqual(config.count(candidate_text), 1)
            self.assertNotIn("skill_source_dir:", config)
            self.assertIn((run_root / "validation").as_posix(), config)
            self.assertIn(jobs_dir.resolve().as_posix(), config)


if __name__ == "__main__":
    unittest.main()
