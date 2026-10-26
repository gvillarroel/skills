#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Curator mechanics/negative controls with fake native results, never models."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("curator_gate_tested", Path(__file__).with_name("run-curator-gate.py"))
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def setUp(self):
        parent = gate.ARTIFACTS / "gate-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent, prefix="fixture-")
        self.root = Path(self.temp.name)
        self.project = self.root / "live"
        self.project.mkdir()
        actual = Path("C:/Users/villa/dev/.pi/durable/repo-custodian")
        for name in gate.driver.ALLOWED:
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((actual / name).read_bytes())
        self.area = self.root / "study"
        self.controls = self.area / "evaluation-controls"
        self.controls.mkdir(parents=True)
        self.development = self.area / "artifacts/development-run"
        self.development.mkdir(parents=True)
        self.output = self.area / "artifacts/curator-gates"
        cfg = {"provider": {"model": "gpt-6.1-sol", "thinkingLevel": "medium", "catalogFile": "models.json"}}
        gate.write(self.project / "config.evo10.json", cfg)
        gate.write(self.project / "models.json", {"mechanicsOnly": True})
        prefix = "evaluation/evo10/"
        self.dev_case = prefix + "development/decision-cases.json"
        helpers = [prefix + name for name in ("decision-grader.ts", "evaluation-settings.json", "worker-benchmark.py", "worker-fixtures.json")]
        for name in [prefix + "verifier.mjs", *helpers]:
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Mechanics fixture only: " + name, encoding="utf-8")
        for split in ("development", "validation", "holdout"):
            gate.write(self.project / (prefix + split + "/decision-cases.json"), {"mechanicsOnly": True, "split": split})
        (self.controls / "protocol.md").write_text("Frozen fixture protocol.\n", encoding="utf-8")
        self.commitments = {
            "development": {"sha256": gate.sha(self.project / self.dev_case)},
            "validationCommitment": {"sha256": gate.sha(self.project / (prefix + "validation/decision-cases.json")), "cases": 4},
            "holdoutCommitment": {"sha256": gate.sha(self.project / (prefix + "holdout/decision-cases.json")), "cases": 4},
            "evaluatorFiles": {"protocol.md": gate.sha(self.controls / "protocol.md")},
            "selection": {"decisionWeight": 0.5, "workerReceiptWeight": 0.5, "minimumPairedImprovement": 0.01,
                          "tieBreak": ["candidate-score-descending", "patch-digest-lexicographic"]},
        }
        gate.write(self.controls / "benchmark-commitments.json", self.commitments)
        gate.write(self.area / "artifacts/driver-freeze.json", {"driverSha256": gate.sha(gate.DRIVER_PATH)})
        self.request = gate.seal({
            "version": 1, "kind": "request", "id": "custodian-evo10-development-20261025", "agentId": "repo-custodian",
            "goal": "Mechanics-only gate fixture; no model quality claim.",
            "allowedPaths": list(gate.driver.ALLOWED), "minimumImprovement": 0.01, "timeoutMs": 360000,
            "verifierPath": prefix + "verifier.mjs", "fixturePaths": ["config.evo10.json", *helpers, self.dev_case],
            "configDigest": gate.sha(self.project / "config.evo10.json"), "evidence": [{"id": "fixture-observation"}],
            "source": [{"path": name, "sha256": gate.sha(self.project / name), "bytes": (self.project / name).stat().st_size} for name in [*gate.driver.ALLOWED, "models.json"]],
        })
        self.request["frozenVerifier"] = [{"path": name, "sha256": gate.sha(self.project / name), "bytes": (self.project / name).stat().st_size}
                                          for name in [self.request["verifierPath"], *self.request["fixturePaths"]]]
        self.request = gate.seal(self.request)
        gate.write(self.area / "artifacts/development-request.json", self.request)
        self.args = SimpleNamespace(command="freeze", project=self.project, config="config.evo10.json",
                                    request_file=self.area / "artifacts/development-request.json",
                                    development_dir=self.development, commitments=self.controls / "benchmark-commitments.json",
                                    output_dir=self.output, authorize_open=False)
        self.calls = []
        self.pass_gate = True
        self.make_attempts()

    def tearDown(self):
        self.temp.cleanup()

    def verification(self, score):
        return {"passed": True, "score": score, "cases": [{"id": "fixture-case", "passed": True, "score": score}],
                "decisionScore": score, "workerScore": score}

    def evaluation(self, proposal, request, score):
        return gate.seal({"proposalId": proposal["id"], "proposalDigest": proposal["digest"], "requestDigest": request["digest"],
                          "source": request["source"], "frozenVerifier": request["frozenVerifier"],
                          "baseline": {"verification": self.verification(0.2)},
                          "candidate": {"verification": self.verification(score)}, "passed": score - 0.2 + 2.220446049250313e-16 >= 0.01})

    def make_attempts(self, tied=False):
        events, finished = [], []
        source = {item["path"]: item["sha256"] for item in self.request["source"]}
        for slot in range(1, 11):
            folder = self.development / "iterations" / f"i{slot:02}"
            folder.mkdir(parents=True, exist_ok=True)
            content = (self.project / gate.driver.ALLOWED[0]).read_text() + f"\nMechanics-only candidate {slot}.\n"
            changes = [{"path": gate.driver.ALLOWED[0], "beforeHash": source[gate.driver.ALLOWED[0]], "content": content}]
            candidate = {"requestId": self.request["id"], "evidenceIds": ["fixture-observation"], "hypothesis": "Fixture",
                         "decision": "Fixture", "expectedBenefit": "Test guards only", "regressionRisks": [], "changes": changes}
            proposal = gate.seal({**candidate, "id": f"fixture-proposal-{slot}", "requestDigest": self.request["digest"]})
            score = 0.4 if tied else round(0.3 + slot * 0.01, 6)
            evaluated = self.evaluation(proposal, self.request, score)
            gate.write(folder / "candidate.json", candidate, exclusive=False)
            gate.write(folder / "proposal.json", proposal, exclusive=False)
            gate.write(folder / "evaluation.json", evaluated, exclusive=False)
            start = {"event": "started", "slot": slot, "baselineRequestDigest": self.request["digest"], "maximumStartedSlots": 10}
            done = {"event": "finished", "slot": slot, "qualified": True, "candidateScore": score,
                    "patchDigest": gate.driver.patch_digest(changes), "candidatePath": str((folder / "candidate.json").resolve()),
                    "proposalId": proposal["id"], "evaluationDigest": evaluated["digest"]}
            events.extend([start, done]); finished.append(done)
        (self.development / "development-ledger.jsonl").write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
        best = sorted(finished, key=lambda item: (-item["candidateScore"], item["patchDigest"]))[0]
        gate.write(self.development / "development-summary.json",
                   {"startedSlots": 10, "finishedSlots": 10, "completedRequestedSlots": True, "iterations": finished, "best": best}, exclusive=False)

    def native(self, args, project, config, directory, action, *extra):
        self.assertTrue((directory / "released.json").is_file(), "Release marker must precede every native call")
        self.calls.append((args.command, action))
        if action == "request":
            body = gate.read(extra[1])
            result = gate.seal({**self.request, **body, "evidence": [{"id": "new-gate-evidence"}],
                               "frozenVerifier": [{"path": name, "sha256": gate.sha(project / name), "bytes": (project / name).stat().st_size}
                                                  for name in [body["verifierPath"], *body["fixturePaths"]]]})
        elif action == "propose":
            body = gate.read(extra[3])
            request = gate.sealed(directory / "request.json")
            result = gate.seal({**body, "id": "native-" + args.command, "requestDigest": request["digest"]})
        else:
            result = self.evaluation(gate.sealed(directory / "propose.json"), gate.sealed(directory / "request.json"), 0.5 if self.pass_gate else 0.2)
        gate.write(directory / (action + ".json"), result)
        return result

    def freeze(self):
        return gate.freeze_selection(self.args)

    def open(self, stage="validation", authorized=True):
        self.args.command, self.args.authorize_open = stage, authorized
        with patch.object(gate, "native", self.native):
            return gate.open_gate(self.args)

    def test_freeze_ten_and_highest_native_score(self):
        result = self.freeze()
        self.assertEqual(result["phase"], "finalist-frozen")
        self.assertEqual(gate.sealed(self.output / "selection.json")["winner"]["slot"], 10)
        self.assertEqual(self.calls, [])

    def test_tie_uses_patch_digest_only(self):
        self.make_attempts(tied=True)
        summary = gate.read(self.development / "development-summary.json")
        self.freeze()
        self.assertEqual(gate.sealed(self.output / "selection.json")["winner"]["patchDigest"], summary["best"]["patchDigest"])

    def test_incomplete_duplicate_or_active_slots_cannot_freeze(self):
        ledger = self.development / "development-ledger.jsonl"
        data = ledger.read_text().splitlines()
        ledger.write_text("\n".join(data[:-2]) + "\n")
        with self.assertRaises(ValueError): self.freeze()
        ledger.write_text("\n".join(data) + "\n")
        (self.development / "development-driver.lock").write_text("active")
        with self.assertRaises(ValueError): self.freeze()
        self.assertFalse((self.output / "selection.json").exists())

    def test_summary_cannot_choose_lower_score(self):
        path = self.development / "development-summary.json"
        value = gate.read(path); value["best"] = value["iterations"][0]
        gate.write(path, value, exclusive=False)
        with self.assertRaises(ValueError): self.freeze()

    def test_native_evaluation_or_candidate_drift_refused(self):
        path = self.development / "iterations/i10/evaluation.json"
        value = gate.read(path); value["passed"] = False
        gate.write(path, value, exclusive=False)
        with self.assertRaises(ValueError): self.freeze()

    def test_explicit_authorization_required_without_marker(self):
        self.freeze()
        result = self.open(authorized=False)
        self.assertFalse(result["released"])
        self.assertEqual(self.calls, [])
        self.assertFalse((self.output / "validation/released.json").exists())

    def test_one_way_validation_and_holdout_keep_exact_patch(self):
        self.freeze(); selected = gate.sealed(self.output / "selection.json")["winner"]
        result = self.open()
        self.assertTrue(result["passed"])
        self.assertFalse(result["qualifiedForSeparatePromotionReview"])
        final = self.open("holdout")
        self.assertTrue(final["qualifiedForSeparatePromotionReview"])
        self.assertEqual(final["patchDigest"], selected["patchDigest"])
        self.assertEqual(len(self.calls), 6)
        with self.assertRaises(FileExistsError): self.open("holdout")
        self.assertEqual(len(self.calls), 6)
        for stage in ("validation", "holdout"):
            request = gate.sealed(self.output / stage / "request.json")
            proposal = gate.sealed(self.output / stage / "propose.json")
            self.assertEqual(gate.driver.patch_digest(proposal["changes"]), selected["patchDigest"])
            self.assertEqual(proposal["evidenceIds"], ["new-gate-evidence"])
            self.assertNotIn(self.dev_case, request["fixturePaths"])

    def test_holdout_without_passed_validation_refused(self):
        self.freeze()
        with self.assertRaises(FileNotFoundError): self.open("holdout")
        self.assertEqual(self.calls, [])
        self.assertFalse((self.output / "holdout/released.json").exists())

    def test_failed_validation_is_terminal_and_blocks_holdout(self):
        self.freeze(); self.pass_gate = False
        result = self.open(); self.assertFalse(result["passed"])
        with self.assertRaises(FileExistsError): self.open()
        with self.assertRaises(ValueError): self.open("holdout")
        self.assertEqual(len(self.calls), 3)

    def test_interrupted_gate_consumes_release_before_call(self):
        self.freeze(); self.args.command = "validation"; self.args.authorize_open = True
        def fail(*args, **kwargs):
            self.assertTrue((self.output / "validation/released.json").is_file())
            raise RuntimeError("Mechanics-only simulated interruption")
        with patch.object(gate, "native", fail):
            with self.assertRaises(RuntimeError): gate.open_gate(self.args)
        self.assertTrue(gate.sealed(self.output / "validation/failure.json")["releaseConsumed"])
        with self.assertRaises(FileExistsError): self.open()
        self.assertEqual(self.calls, [])

    def test_finalist_bytes_and_live_source_cannot_drift(self):
        self.freeze()
        candidate = self.development / "iterations/i10/candidate.json"
        candidate.write_bytes(candidate.read_bytes() + b"\n")
        with self.assertRaises(ValueError): self.open()
        self.assertEqual(self.calls, [])

    def test_reserved_case_hash_change_refuses_before_release(self):
        self.freeze()
        case = self.project / "evaluation/evo10/validation/decision-cases.json"
        case.write_text("Changed reserved fixture")
        with self.assertRaises(ValueError): self.open()
        self.assertFalse((self.output / "validation/released.json").exists())

    def test_live_config_change_refuses_before_release(self):
        self.freeze()
        (self.project / "config.evo10.json").write_text("{}")
        with self.assertRaises(ValueError): self.open()
        self.assertFalse((self.output / "validation/released.json").exists())

    def test_duplicate_semantic_cases_are_not_independent(self):
        path = self.project / "evaluation/evo10/validation/decision-cases.json"
        path.write_bytes((self.project / self.dev_case).read_bytes())
        self.commitments["validationCommitment"]["sha256"] = gate.sha(path)
        gate.write(self.args.commitments, self.commitments, exclusive=False)
        self.freeze()
        with self.assertRaises(ValueError): self.open()
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
