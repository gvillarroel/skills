#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a private, read-only case index; completion is not outcome verification."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile


MAX_RECORD_BYTES = 64 * 1024
MAX_RESULT_BYTES = 1024 * 1024
MAX_EVIDENCE_PER_AGENT = 10000
MAX_DATABASE_BYTES = 256 * 1024 * 1024
DEFAULT_SNAPSHOTS = Path(__file__).resolve().parents[2] / "artifacts" / "reviews" / ".case-index-snapshots"
HEX = re.compile(r"^[a-f0-9]{64}$")
AGENT = re.compile(r"^[a-z][a-z0-9-]{0,47}$")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value) -> str | None:
    return value if isinstance(value, str) and HEX.fullmatch(value) else None


def load_json(path: Path, maximum: int):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > maximum:
        raise ValueError("A required scoped JSON file is missing, linked or oversized.")
    return json.loads(path.read_text(encoding="utf-8"))


def plain(value, maximum=300):
    """Retain bounded identifiers only, never operational free text or results."""
    if not isinstance(value, str) or not value or len(value) > maximum:
        return None
    if any(ord(char) < 32 for char in value):
        return None
    if re.search(r"(?:Bearer\s|github_pat_|gh[pousr]_|sk-[A-Za-z0-9_-]{8,}|password\s*=|token\s*=)", value, re.I):
        return "[REDACTED]"
    return value


def integer(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def version(record: dict) -> dict:
    source = record.get("version")
    if not isinstance(source, dict):
        return {"hostDigest": None, "conversationDigest": None, "instructionsSha256": None,
                "provider": None, "model": None, "effort": None}
    host = source.get("hostVersion") if isinstance(source.get("hostVersion"), dict) else source
    conversation = source.get("conversationVersion") if isinstance(source.get("conversationVersion"), dict) else source
    provider = conversation.get("provider") if isinstance(conversation.get("provider"), dict) else {}
    selection = conversation.get("modelSelection") if isinstance(conversation.get("modelSelection"), dict) else {}
    selected = selection.get("selected") if isinstance(selection.get("selected"), dict) else {}
    selected_model = selected.get("model") if isinstance(selected.get("model"), dict) else {}
    return {
        "hostDigest": digest(host.get("digest")),
        "conversationDigest": digest(conversation.get("digest")),
        "instructionsSha256": digest(conversation.get("instructionsSha256")),
        "provider": plain(selected_model.get("provider") or provider.get("kind"), 100),
        "model": plain(selected_model.get("modelId") or provider.get("model"), 100),
        "effort": plain(selected.get("effort") or provider.get("effort"), 50),
    }


def file_observation(path: Path):
    if not path.exists():
        return None
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_DATABASE_BYTES:
        raise ValueError("State file is linked, unsupported or too large for a bounded review.")
    before = path.stat()
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            checksum.update(chunk)
    after = path.stat()
    identity = (before.st_size, before.st_mtime_ns, before.st_ino)
    if identity != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError("State changed while collecting a bounded snapshot; retry only when stable.")
    return {"identity": identity, "sha256": checksum.hexdigest()}


@contextmanager
def readonly_database(path: Path, snapshot_dir: Path = DEFAULT_SNAPSHOTS):
    if not path.is_file() or path.is_symlink():
        raise ValueError("A required state database does not exist or is linked; no database was created.")
    # Even mode=ro/query_only may update live WAL shared-memory reader marks.
    # Never open the source with SQLite: verify a stable DB+WAL copy first, then
    # read that private copy. Do not copy credentials or the mutable live SHM.
    wal = Path(str(path) + "-wal")
    journal = Path(str(path) + "-journal")
    if journal.exists():
        raise ValueError("Rollback-journal state needs an operator-provided consistent backup.")
    observations = [file_observation(item) for item in (path, wal)]
    snapshot_dir = snapshot_dir.resolve()
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="readonly-case-", dir=snapshot_dir) as temporary:
        target_root = Path(temporary).resolve()
        # Verify the exact recursively cleaned temporary directory remains in
        # the intended artifact location before TemporaryDirectory cleanup.
        if not target_root.is_relative_to(snapshot_dir):
            raise ValueError("Temporary snapshot path escaped the artifact directory.")
        target = target_root / path.name
        for original, observed in zip((path, wal), observations):
            if observed is not None:
                copied = target_root / original.name
                shutil.copyfile(original, copied)
                if file_observation(copied)["sha256"] != observed["sha256"]:
                    raise ValueError("State changed during the bounded snapshot copy.")
        if journal.exists() or observations != [file_observation(item) for item in (path, wal)]:
            raise ValueError("State changed during snapshot collection; no mixed snapshot is used.")
        connection = sqlite3.connect(target.as_uri() + "?mode=ro", uri=True, timeout=2)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA query_only=ON")
            connection.execute("BEGIN")
            yield connection
        finally:
            connection.close()


def exact_case(record: dict, agent: str, job: sqlite3.Row) -> bool:
    return (record.get("agentId") == agent and record.get("jobId") == job["id"]
            and integer(record.get("conversationId")) == integer(job["conversationId"])
            and integer(record.get("submissionId")) == integer(job["submissionId"])
            and integer(job["conversationId"]) is not None and integer(job["submissionId"]) is not None)


def event_records(connection: sqlite3.Connection, agent: str):
    rows = connection.execute(
        "SELECT rowid,record FROM evidence WHERE agentId=? AND length(CAST(record AS BLOB))<=? ORDER BY rowid DESC LIMIT ?",
        (agent, MAX_RECORD_BYTES, MAX_EVIDENCE_PER_AGENT),
    ).fetchall()
    result = []
    invalid = 0
    for row in rows:
        try:
            record = json.loads(row["record"])
            if not isinstance(record, dict) or record.get("agentId") != agent or not isinstance(record.get("details"), dict):
                raise ValueError("Invalid record attribution")
            if not plain(record.get("id"), 100):
                raise ValueError("Invalid record identity")
            result.append((row["rowid"], record))
        except (ValueError, TypeError):
            invalid += 1
    return result, invalid


def observed_verification(records, agent: str, job: sqlite3.Row, admission: dict | None,
                          result_sha: str | None):
    accepted = []
    rejected = 0
    if admission is None:
        admission = {}
    for _, record in records:
        if record.get("kind") != "verification.completed" or not exact_case(record, agent, job):
            continue
        details = record["details"]
        status = details.get("status")
        checks = details.get("checks")
        source = version(record)
        original = version(admission)
        valid = (status in {"passed", "failed", "inconclusive", "unconfigured"}
                 and isinstance(details.get("evidenceIds"), list) and admission.get("id") in details["evidenceIds"]
                 and digest(details.get("contractSha256")) is not None
                 and result_sha is not None and details.get("outputSha256") == result_sha
                 and original["conversationDigest"] is not None
                 and source == original and isinstance(checks, list) and len(checks) <= 32
                 and all(isinstance(check, dict) and plain(check.get("id"), 100)
                         and isinstance(check.get("passed"), bool) for check in checks))
        if status in {"passed", "failed"}:
            valid = valid and isinstance(checks, list) and 0 < len(checks) <= 32
            if valid:
                valid = all(isinstance(check, dict) and plain(check.get("id"), 100)
                            and isinstance(check.get("passed"), bool) for check in checks)
            if valid and status == "passed":
                valid = all(check["passed"] for check in checks)
            if valid and status == "failed":
                valid = any(not check["passed"] for check in checks)
        if not valid:
            rejected += 1
            continue
        accepted.append({
            "evidenceId": plain(record.get("id"), 100), "at": plain(record.get("at"), 50),
            "status": status, "contractSha256": details["contractSha256"],
            "outputSha256": result_sha,
            "checks": [{"id": plain(check.get("id"), 100), "passed": check.get("passed")} for check in (checks or [])][:32],
        })
    return {"status": accepted[0]["status"] if accepted else "not-recorded",
            "receipts": accepted[:10], "rejectedAttributionOrContractRecords": rejected,
            "scope": "Historical configured checks only; not an independent general-quality judgment."}


def build_case(agent: str, job: sqlite3.Row, records) -> dict:
    matching = [(row, record) for row, record in records if exact_case(record, agent, job)]
    admissions = [(row, record) for row, record in matching if record.get("kind") == "job.admitted"]
    completions = [(row, record) for row, record in matching if record.get("kind") == "job.completed"]
    admission = admissions[0][1] if admissions else None
    completion = completions[0][1] if completions else None
    actual_sha = sha(job["boundedResult"].encode("utf-8")) if isinstance(job["boundedResult"], str) else None
    recorded_sha = digest(completion["details"].get("result", {}).get("sha256")) if completion and isinstance(completion["details"].get("result"), dict) else None
    result_sha = actual_sha if actual_sha is not None and actual_sha == recorded_sha else None
    source = version(admission or {})
    gaps = []
    if not admission:
        gaps.append("No exact agent/job/conversation/submission admission in the bounded evidence window.")
    if job["status"] != "done":
        gaps.append("Task is not recorded as completed; its failure or unanswered status is retained.")
    if not completion or result_sha is None:
        gaps.append("No attributable completion with a matching bounded result hash.")
    if source["conversationDigest"] is None:
        gaps.append("Original conversation source version is unknown.")
    checks = observed_verification(records, agent, job, admission, result_sha)
    if checks["status"] not in {"passed", "failed"}:
        gaps.append("No matching substantive outcome-verification receipt; completion is not a quality pass.")
    low = admissions[0][0] if admissions else None
    high = completions[0][0] if completions else None
    related = [(row, record) for row, record in records
               if record.get("conversationId") == job["conversationId"] and low is not None and high is not None and low <= row <= high]
    # Conversation-window references describe context, not proof that each tool
    # or public decision belongs to a particular submission in an overlapping chat.
    decision_ids = [plain(record.get("id"), 100) for _, record in related if record.get("kind") == "decision.recorded"][:20]
    terminal = [plain(record.get("id"), 100) for _, record in matching
                if record.get("kind") in {"job.completed", "job.unanswered", "job.interrupted"}][:20]
    return {
        "jobId": plain(job["id"]), "agentId": agent, "status": plain(job["status"], 50),
        "conversationId": integer(job["conversationId"]), "submissionId": integer(job["submissionId"]),
        "admissionEvidenceIds": [plain(record.get("id"), 100) for _, record in admissions][:20],
        "terminalEvidenceIds": terminal, "sourceVersion": source,
        "resultSha256": result_sha, "resultHashMatchesRecordedCompletion": result_sha is not None,
        "conversationWindowDecisionIds": decision_ids,
        "conversationWindowToolCounts": {kind: sum(record.get("kind") == kind for _, record in related)
                                        for kind in ("tool.started", "tool.completed", "tool.failed")},
        "outcomeVerification": checks,
        "disposition": "requires-goal-review" if not gaps else "insufficient",
        "missingObservations": gaps,
        "limitations": "Observed database attribution only. This does not grade reasoning, correctness, causality or generalization.",
    }


def build_index(config_path: Path, limit: int = 100, snapshot_dir: Path = DEFAULT_SNAPSHOTS) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("Use --limit from 1 to 100 jobs per agent.")
    config_path = config_path.resolve(strict=True)
    config = load_json(config_path, 256 * 1024)
    if config.get("version") != 1 or not isinstance(config.get("dataDir"), str) or not isinstance(config.get("agents"), list):
        raise ValueError("Expected a version-1 project config with dataDir and agents.")
    project = config_path.parent
    state = (project / config["dataDir"]).resolve()
    agents = config["agents"]
    ids = [agent.get("id") for agent in agents if isinstance(agent, dict)]
    if not ids or len(ids) != len(agents) or len(set(ids)) != len(ids) or any(not isinstance(agent, str) or not AGENT.fullmatch(agent) for agent in ids):
        raise ValueError("Expected unique configured agent identities.")
    results = []
    with readonly_database(state / "catalog.sqlite", snapshot_dir) as catalog, readonly_database(state / "evidence.sqlite", snapshot_dir) as evidence:
        for agent in agents:
            agent_id = agent["id"]
            prompt_sha = None
            if agent.get("instructionsFile") is not None:
                path = project / str(agent["instructionsFile"])
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(project / "prompts") or path.is_symlink() or not resolved.is_file() or resolved.stat().st_size > 128 * 1024:
                    raise ValueError("A configured prompt is outside the scoped prompts directory, linked or oversized.")
                prompt_sha = sha(resolved.read_bytes())
            elif isinstance(agent.get("instructions"), str):
                prompt_sha = sha(agent["instructions"].encode("utf-8"))
            rows, invalid = event_records(evidence, agent_id)
            counts = {}
            for row in evidence.execute("SELECT kind,COUNT(*) AS n FROM evidence WHERE agentId=? GROUP BY kind", (agent_id,)):
                kind = row["kind"] if isinstance(row["kind"], str) and re.fullmatch(r"[a-z][a-z0-9_.-]{0,99}", row["kind"]) else "invalid-kind"
                counts[kind] = counts.get(kind, 0) + row["n"]
            jobs = catalog.execute(
                "SELECT id,status,conversationId,submissionId,CASE WHEN length(CAST(result AS BLOB))<=? THEN result END AS boundedResult FROM jobs WHERE agentId=? ORDER BY rowid DESC LIMIT ?",
                (MAX_RESULT_BYTES, agent_id, limit),
            ).fetchall()
            total = catalog.execute("SELECT COUNT(*) FROM jobs WHERE agentId=?", (agent_id,)).fetchone()[0]
            cases = [build_case(agent_id, job, rows) for job in jobs]
            results.append({
                "agentId": agent_id, "configuredPromptSha256": prompt_sha,
                "configuredModel": plain(config.get("provider", {}).get("model"), 100),
                "evidenceCounts": counts, "evidenceWindow": {"loaded": len(rows), "maximum": MAX_EVIDENCE_PER_AGENT, "invalidOrMismatchedLoadedRecords": invalid, "maximumRecordBytes": MAX_RECORD_BYTES},
                "jobsTotal": total, "jobsIndexed": len(cases), "jobsOmitted": max(0, total - len(cases)),
                "unlinkedHumanSubmissions": {"observedCount": counts.get("human.submitted", 0), "status": "not-inferred", "reason": "Model responses do not establish terminal completion or verification of a human control submission."},
                "cases": cases, "disposition": "insufficient",
                "nextStep": "Review the specific improvement goal, complete case coverage, actual outcome criteria and version confounders before considering evolution.",
            })
    return {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
            "scope": "Private read-only case inventory; no automatic quality or readiness gate.",
            "consistency": "Private stable DB+WAL copies are source-hash/stat checked before and after copying. SQLite opens only those copies, avoiding live SHM reader-mark writes. The databases are not an atomic cross-database snapshot; drain or use an operator-provided consistent backup for release decisions.",
            "agents": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    try:
        config_path = args.config.resolve(strict=True)
        config = load_json(config_path, 256 * 1024)
        state = (config_path.parent / config["dataDir"]).resolve()
        output = args.output.resolve()
        if "artifacts" not in output.parts or output.suffix != ".json" or output == config_path or output.is_relative_to(state) or output.is_relative_to(config_path.parent / "src") or output.is_relative_to(config_path.parent / "prompts"):
            raise ValueError("Write the private JSON review under artifacts, outside live state, source, prompts and config.")
        output.parent.mkdir(parents=True, exist_ok=True)
        result = build_index(args.config, args.limit, output.parent / ".case-index-snapshots")
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"indexed": True, "agents": len(result["agents"]), "jobs": sum(agent["jobsIndexed"] for agent in result["agents"]), "qualityPassClaimed": False}))
        return 0
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error):
        print("Evidence review failed: check scoped config, readonly state, schema and output path. No service was started and no quality pass is claimed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
