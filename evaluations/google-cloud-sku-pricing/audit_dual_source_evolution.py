#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit the three Google Cloud pricing Harbor gates without changing them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = Path(__file__).resolve().parent
RUN_ROOTS = {
    "v1": REPOSITORY_ROOT
    / "evaluations/runs/google-cloud-sku-pricing-dual-source-evolution-20260826-v1",
    "v2": REPOSITORY_ROOT
    / "evaluations/runs/google-cloud-sku-pricing-dual-source-evolution-20260826-v2",
    "v3": REPOSITORY_ROOT
    / "evaluations/runs/google-cloud-sku-pricing-dual-source-evolution-20260826-v3",
}
MANIFESTS = [
    EVALUATION_DIR / "dual-source-harbor-manifest-20260826.json",
    EVALUATION_DIR / "dual-source-holdout-v2-manifest-20260826.json",
    EVALUATION_DIR / "dual-source-holdout-v3-manifest-20260826.json",
]
PARQUET = (
    REPOSITORY_ROOT
    / "projects/google-cloud-sku-pricing-parquet/artifacts/data/"
    "google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.parquet"
)
PARQUET_SHA256 = "20275538572f0b9c19e2efceaa98127385edb28ba0942097fe029ecb3aebf5c0"
SKU_PATTERN = re.compile(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_sql_writes(pi_path: Path) -> list[str]:
    queries: list[str] = []
    with pi_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "turn_end":
                continue
            for part in event.get("message", {}).get("content", []):
                if part.get("type") != "toolCall" or part.get("name") != "write":
                    continue
                arguments = part.get("arguments", {})
                if str(arguments.get("path", "")).lower().endswith(".sql"):
                    queries.append(str(arguments.get("content", "")))
    return queries


def v3_eligibility_is_semantic(sql: str) -> bool:
    """Accept direct exact usage or an exact NUMERIC parameter bound to it."""
    direct = re.search(
        r"start_usage_amount[\s\S]{0,160}<=\s*(?:"
        r"(?:NUMERIC\s*)?'?640000'?|"
        r"CAST\s*\(\s*640000\s+AS\s+NUMERIC\s*\)"
        r")",
        sql,
        flags=re.IGNORECASE,
    )
    parameter_use = re.search(
        r"start_usage_amount[\s\S]{0,160}<=\s*(?:params\.)?usage_amount",
        sql,
        flags=re.IGNORECASE,
    )
    parameter_value = re.search(
        r"NUMERIC\s*'640000'\s+AS\s+usage_amount",
        sql,
        flags=re.IGNORECASE,
    )
    return bool(direct or (parameter_use and parameter_value))


def reflection_findings(run_root: Path, holdout_tokens: set[str]) -> dict[str, Any]:
    reflection_root = run_root / "reflection-calls"
    files = sorted(path for path in reflection_root.rglob("*") if path.is_file())
    leaked: dict[str, list[str]] = {}
    tool_event_count = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = sorted(token for token in holdout_tokens if token in text)
        if hits:
            leaked[str(path.relative_to(run_root))] = hits
        if path.name == "events.jsonl":
            for line in text.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") in {"tool_execution_start", "tool_execution_end"}:
                    tool_event_count += 1
                for part in event.get("message", {}).get("content", []):
                    if isinstance(part, dict) and part.get("type") == "toolCall":
                        tool_event_count += 1
    return {
        "fileCount": len(files),
        "leakedTokens": leaked,
        "toolEventCount": tool_event_count,
        "ok": not leaked and tool_event_count == 0,
    }


def main() -> int:
    findings: list[str] = []
    runs: dict[str, Any] = {}
    for version, root in RUN_ROOTS.items():
        run = load_json(root / "run.json")
        trials = {
            variant: list(run.get("holdoutTrials", {}).get(variant, []))
            for variant in ("baseline", "candidate")
        }
        all_trials = [trial for variant in trials.values() for trial in variant]
        provenance_ok = all(
            trial.get("skillProvenance", {}).get("verified") is True
            and trial.get("skillProvenance", {}).get("sourceUnchanged") is True
            and trial.get("skillProvenance", {}).get("contentStableAfterTrial") is True
            for trial in all_trials
        )
        baseline_errors = [
            trial.get("error") for trial in trials["baseline"] if trial.get("error")
        ]
        candidate_errors = [
            trial.get("error") for trial in trials["candidate"] if trial.get("error")
        ]
        known_external_candidate_errors = all(
            "Invalid argument" in error and "harbor_pi_wrapper.py check" in error
            for error in candidate_errors
        )
        if not provenance_ok:
            findings.append(f"{version}:provenance")
        if baseline_errors:
            findings.append(f"{version}:baseline-errors")
        if candidate_errors and not known_external_candidate_errors:
            findings.append(f"{version}:unknown-candidate-error")
        runs[version] = {
            "baselineDigest": run.get("baselineDigest"),
            "candidateDigest": run.get("candidateDigest"),
            "metricCalls": run.get("gepa", {}).get("metricCalls"),
            "bestValidationScore": run.get("gepa", {}).get("bestValidationScore"),
            "holdout": run.get("holdout"),
            "baselineTrialCount": len(trials["baseline"]),
            "candidateTrialCount": len(trials["candidate"]),
            "provenanceVerified": provenance_ok,
            "baselineErrors": baseline_errors,
            "candidateExternalErrorCount": len(candidate_errors),
            "candidateErrorsKnownExternal": known_external_candidate_errors,
        }

    v3_run = load_json(RUN_ROOTS["v3"] / "run.json")
    v3_baseline = v3_run["holdoutTrials"]["baseline"]
    parquet_rewards = [
        float(trial["reward"])
        for trial in v3_baseline
        if trial["taskName"].startswith("parquet-")
    ]
    if parquet_rewards != [1.0, 1.0]:
        findings.append("v3:parquet-baseline-not-exact")

    bq_trials = [
        trial
        for trial in v3_baseline
        if trial["taskName"].startswith("bigquery-")
    ]
    bq_audit: list[dict[str, Any]] = []
    for trial in bq_trials:
        verifier = json.loads(trial["verifierOutput"])
        artifact = Path(trial["artifactDirectory"])
        pi_paths = list(artifact.rglob("agent/pi.txt"))
        queries = extract_sql_writes(pi_paths[0]) if len(pi_paths) == 1 else []
        only_brittle_check_failed = (
            verifier.get("failedChecks") == ["eligible-tier"]
            and verifier.get("passedChecks") == 30
            and verifier.get("totalChecks") == 31
        )
        semantic_eligibility = len(queries) == 1 and v3_eligibility_is_semantic(queries[0])
        recovered = only_brittle_check_failed and semantic_eligibility
        if not recovered:
            findings.append(f"v3:bigquery-semantic-audit:{artifact.name}")
        bq_audit.append(
            {
                "artifactDirectory": str(artifact),
                "rawReward": trial["reward"],
                "rawFailedChecks": verifier.get("failedChecks", []),
                "queryCount": len(queries),
                "semanticEligibilityVerified": semantic_eligibility,
                "auditedChecksPassed": 31 if recovered else verifier.get("passedChecks"),
                "auditedChecksTotal": 31,
            }
        )

    v3_task_root = (
        REPOSITORY_ROOT
        / "evaluations/runs/google-cloud-sku-pricing-dual-source-20260826-holdout-v3-tasks/holdout"
    )
    bq_request = load_json(
        v3_task_root
        / "bigquery-holdout-v3-account-region/environment/request.json"
    )
    parquet_questions = load_json(
        v3_task_root / "parquet-holdout-v3-01/environment/questions.json"
    )
    holdout_tokens = {
        *SKU_PATTERN.findall(json.dumps(bq_request)),
        *SKU_PATTERN.findall(json.dumps(parquet_questions)),
        "europe-west10",
        "us-west8",
        "regional-contract-price-v3",
    }
    reflection = reflection_findings(RUN_ROOTS["v3"], holdout_tokens)
    if not reflection["ok"]:
        findings.append("v3:reflection-leakage-or-tools")

    parquet_hash = sha256_file(PARQUET)
    if parquet_hash != PARQUET_SHA256:
        findings.append("parquet:digest")

    current_skill_md = sha256_file(
        REPOSITORY_ROOT / "skills/google-cloud-sku-pricing/SKILL.md"
    )
    v3_skill_digests = {
        trial["skillProvenance"]["candidateSkillMdDigest"].removeprefix("sha256:")
        for variant in ("baseline", "candidate")
        for trial in v3_run["holdoutTrials"][variant]
    }
    if v3_skill_digests != {current_skill_md}:
        findings.append("v3:current-skill-md-digest")

    manifest_release = {
        path.name: load_json(path).get("holdoutReleased") for path in MANIFESTS
    }
    if not all(manifest_release.values()):
        findings.append("manifest:holdout-not-released")

    result = {
        "schemaVersion": 1,
        "ok": not findings,
        "findings": findings,
        "runs": runs,
        "v3": {
            "baselineParquetRewards": parquet_rewards,
            "baselineBigQuerySemanticAudit": bq_audit,
            "reflectionIsolation": reflection,
            "currentSkillMdSha256": current_skill_md,
        },
        "parquet": {
            "path": str(PARQUET),
            "bytes": PARQUET.stat().st_size,
            "sha256": parquet_hash,
        },
        "manifestHoldoutReleased": manifest_release,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
