#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise readonly attribution and refusal of false verification passes."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("review-evidence.py")
SPEC = importlib.util.spec_from_file_location("review_evidence", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[2]
TEMP = ROOT / "artifacts" / "reviews" / "case-index-tests"


@contextmanager
def database(path):
    connection = sqlite3.connect(path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


class ReviewEvidenceTests(unittest.TestCase):
    def setUp(self):
        TEMP.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=TEMP)
        self.project = Path(self.temporary.name)
        (self.project / "prompts").mkdir()
        (self.project / "prompts/agent.md").write_text("Read only. Report observed facts.\n", encoding="utf-8")
        self.config = self.project / "config.json"
        self.config.write_text(json.dumps({"version": 1, "dataDir": "state", "provider": {"model": "gpt-6.1-sol"}, "agents": [{"id": "agent", "instructionsFile": "prompts/agent.md"}]}), encoding="utf-8")
        state = self.project / "state"
        state.mkdir()
        with database(state / "catalog.sqlite") as db:
            db.execute("CREATE TABLE jobs(id TEXT,agentId TEXT,status TEXT,conversationId INTEGER,submissionId INTEGER,result TEXT)")
            db.execute("INSERT INTO jobs VALUES ('job-1','agent','done',7,9,'observed result')")
        with database(state / "evidence.sqlite") as db:
            db.execute("CREATE TABLE evidence(id TEXT,at TEXT,agentId TEXT,kind TEXT,record TEXT)")
        self.source = {"hostVersion": {"digest": "a" * 64}, "conversationVersion": {"digest": "b" * 64, "instructionsSha256": "c" * 64, "provider": {"kind": "openai-codex", "model": "gpt-6.1-sol"}}}
        self.result_sha = hashlib.sha256(b"observed result").hexdigest()
        self.add("admission", "job.admitted")
        self.add("decision", "decision.recorded", details={"summary": "A public recommendation"}, submission=None, job=None)
        self.add("completion", "job.completed", details={"result": {"sha256": self.result_sha}})

    def tearDown(self):
        self.temporary.cleanup()

    def add(self, identity, kind, *, details=None, agent="agent", job="job-1", conversation=7, submission=9, source=None):
        record = {"id": identity, "at": "2026-10-25T12:00:00Z", "agentId": agent, "kind": kind,
                  "details": details or {}, "version": source or self.source}
        for key, value in (("jobId", job), ("conversationId", conversation), ("submissionId", submission)):
            if value is not None:
                record[key] = value
        with database(self.project / "state/evidence.sqlite") as db:
            db.execute("INSERT INTO evidence VALUES (?,?,?,?,?)", (identity, record["at"], agent, kind, json.dumps(record)))

    def receipt(self, identity="verified", **changes):
        details = {"status": "passed", "contractSha256": "d" * 64, "outputSha256": self.result_sha,
                   "evidenceIds": ["admission"], "checks": [{"id": "specific-outcome", "passed": True}]}
        details.update(changes.pop("details", {}))
        self.add(identity, "verification.completed", details=details, **changes)

    def case(self):
        return MODULE.build_index(self.config)["agents"][0]["cases"][0]

    def test_completion_alone_is_insufficient(self):
        case = self.case()
        self.assertEqual(case["status"], "done")
        self.assertEqual(case["outcomeVerification"]["status"], "not-recorded")
        self.assertEqual(case["disposition"], "insufficient")
        self.assertTrue(case["resultHashMatchesRecordedCompletion"])
        self.assertEqual(case["sourceVersion"]["model"], "gpt-6.1-sol")

    def test_wrong_agent_case_and_hash_do_not_become_passes(self):
        self.receipt("other-agent", agent="other")
        self.receipt("other-job", job="another-job")
        self.receipt("other-submission", submission=10)
        self.receipt("wrong-hash", details={"outputSha256": "f" * 64})
        self.receipt("empty-checks", details={"checks": []})
        self.receipt("wrong-source", source={"conversationVersion": {"digest": "f" * 64}})
        case = self.case()
        self.assertEqual(case["outcomeVerification"]["status"], "not-recorded")
        self.assertEqual(case["outcomeVerification"]["rejectedAttributionOrContractRecords"], 3)

    def test_bound_verification_is_a_historical_check_not_global_readiness(self):
        self.receipt()
        result = MODULE.build_index(self.config)
        case = result["agents"][0]["cases"][0]
        self.assertEqual(case["outcomeVerification"]["status"], "passed")
        self.assertEqual(case["disposition"], "requires-goal-review")
        self.assertEqual(result["agents"][0]["disposition"], "insufficient")

    def test_failed_check_is_retained(self):
        self.receipt(details={"status": "failed", "checks": [{"id": "specific-outcome", "passed": False}]})
        self.assertEqual(self.case()["outcomeVerification"]["status"], "failed")

    def test_unanswered_is_not_reclassified_from_model_response(self):
        with database(self.project / "state/catalog.sqlite") as db:
            db.execute("UPDATE jobs SET status='unanswered',result=NULL")
        self.add("response", "model.response", details={"publicSummary": "I succeeded."}, job=None, submission=None)
        case = self.case()
        self.assertEqual(case["status"], "unanswered")
        self.assertEqual(case["disposition"], "insufficient")

    def test_missing_database_is_not_created(self):
        path = self.project / "state/missing.sqlite"
        with self.assertRaises(ValueError):
            with MODULE.readonly_database(path):
                pass
        self.assertFalse(path.exists())

    def test_database_and_source_bytes_unchanged(self):
        def snapshot():
            return {str(path.relative_to(self.project)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.project.rglob("*") if path.is_file()}
        before = snapshot()
        MODULE.build_index(self.config)
        self.assertEqual(before, snapshot())
        with MODULE.readonly_database(self.project / "state/catalog.sqlite") as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute("DELETE FROM jobs")

    def test_job_limit_and_no_raw_result(self):
        with database(self.project / "state/catalog.sqlite") as db:
            db.execute("INSERT INTO jobs VALUES ('job-2','agent','failed',8,10,'private result must not be exported')")
        result = MODULE.build_index(self.config, 1)
        agent = result["agents"][0]
        self.assertEqual((agent["jobsIndexed"], agent["jobsOmitted"]), (1, 1))
        self.assertNotIn("private result must not be exported", json.dumps(result))
        self.assertNotIn("observed result", json.dumps(result))
        with self.assertRaises(ValueError):
            MODULE.build_index(self.config, 101)

    def test_human_control_completion_not_inferred(self):
        self.add("human", "human.submitted", job=None)
        self.add("human-response", "model.response", details={"publicSummary": "Done"}, job=None, submission=None)
        result = MODULE.build_index(self.config)["agents"][0]["unlinkedHumanSubmissions"]
        self.assertEqual(result["observedCount"], 1)
        self.assertEqual(result["status"], "not-inferred")

    def test_existing_wal_is_read_and_its_files_are_unchanged(self):
        path = self.project / "state/catalog.sqlite"
        writer = sqlite3.connect(path)
        try:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("INSERT INTO jobs VALUES ('wal-job','agent','unanswered',11,12,NULL)")
            writer.commit()
            files = [path, Path(str(path) + "-wal"), Path(str(path) + "-shm")]
            before = {str(item): item.read_bytes() for item in files}
            index = MODULE.build_index(self.config)
            self.assertEqual(index["agents"][0]["jobsTotal"], 2)
            self.assertEqual(before, {str(item): item.read_bytes() for item in files})
        finally:
            writer.close()

    def test_rollback_journal_is_refused_without_recovery(self):
        path = self.project / "state/catalog.sqlite"
        journal = Path(str(path) + "-journal")
        journal.write_bytes(b"retained rollback journal")
        before = journal.read_bytes()
        with self.assertRaises(ValueError):
            with MODULE.readonly_database(path):
                pass
        self.assertEqual(journal.read_bytes(), before)

    def test_concurrent_source_change_refuses_the_snapshot(self):
        path = self.project / "state/catalog.sqlite"
        original_copy = MODULE.shutil.copyfile

        def copy_then_writer(source, destination):
            result = original_copy(source, destination)
            if Path(source) == path:
                with database(path) as db:
                    db.execute("INSERT INTO jobs VALUES ('concurrent','agent','queued',NULL,NULL,NULL)")
            return result

        with patch.object(MODULE.shutil, "copyfile", side_effect=copy_then_writer):
            with self.assertRaises(ValueError):
                with MODULE.readonly_database(path):
                    self.fail("A changed source must not be admitted as a stable snapshot.")


if __name__ == "__main__":
    unittest.main()
