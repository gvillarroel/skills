#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==1.4.4", "pytz==2025.2"]
# ///
"""Build and verify a sealed 60-question Google Cloud pricing Harbor dataset."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = Path(__file__).resolve().parent
RUNS_DIR = REPOSITORY_ROOT / "evaluations" / "runs"
DEFAULT_TASK_ROOT = RUNS_DIR / "google-cloud-sku-pricing-mixed-load-60-20260826-tasks"
DURABLE_MANIFEST = EVALUATION_DIR / "mixed-load-60-manifest-20260826.json"
DATASET_ID = "google-cloud-sku-pricing-mixed-load-60-20260826"
SNAPSHOT_ID = "gcp-pricing-636387a8dd1a10dc"
SEED_SEARCH_START = 20260830
SEED_CANDIDATE_COUNT = 12
TASK_COUNT = 6
QUESTIONS_PER_TASK = 10
QUESTION_COUNT = TASK_COUNT * QUESTIONS_PER_TASK

PARQUET = (
    REPOSITORY_ROOT
    / "projects"
    / "google-cloud-sku-pricing-parquet"
    / "artifacts"
    / "data"
    / "google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.parquet"
)
PARQUET_MANIFEST = (
    REPOSITORY_ROOT
    / "projects"
    / "google-cloud-sku-pricing-parquet"
    / "artifacts"
    / "manifests"
    / "google-cloud-public-prices-gcp-pricing-636387a8dd1a10dc.manifest.json"
)
CATALOG = (
    REPOSITORY_ROOT
    / "evaluations"
    / "datasets"
    / "google-cloud-sku-pricing-100"
    / "processed"
    / "catalog.sqlite"
)
PARQUET_HELPER_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "google-cloud-sku-pricing"
    / "scripts"
    / "parquet_pricing.py"
)

RELEASED_TASK_ROOTS = (
    RUNS_DIR / "google-cloud-sku-pricing-dual-source-20260826-tasks",
    RUNS_DIR / "google-cloud-sku-pricing-dual-source-20260826-holdout-v2-tasks",
    RUNS_DIR / "google-cloud-sku-pricing-dual-source-20260826-holdout-v3-tasks",
)

SKU_PATTERN = re.compile(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b")
FILTER_PATTERN = re.compile(
    r"service ID is `([^`]+)`, geographic region is `([^`]+)`, "
    r"and taxonomy contains exact category `([^`]+)`"
)
USAGE_PATTERN = re.compile(r"(?:exact usage|usage) `([^`]+)`")

TASK_TOML = """version = "1.0"

[metadata]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 60.0
"""

TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_task.py"
"""

INSTRUCTION = """Answer all ten questions in `questions.json` from the frozen
`catalog.parquet` file in this task workspace.

Use the installed `google-cloud-sku-pricing` skill. Work only inside this task
workspace and the installed skill. Do not inspect ancestor repositories, prior
trials, evaluator tests, credentials, or network resources. Treat the installed
skill as read-only. Read
`/app/.agents/skills/google-cloud-sku-pricing/SKILL.md` first; it is the only
evaluated skill bundle. Use its Parquet workflow and bundled helper.

Create exactly one non-empty output file named `answers.json` in the task
workspace. It must be valid JSON with this exact envelope:

```json
{
  "answers": [
    {"id": "the question id", "answer": {"only": "the requested fields"}}
  ]
}
```

Include every question exactly once and preserve the order from
`questions.json`. Do not add root fields, explanation, evidence, or unrequested
answer fields. Decimal values must be JSON strings in canonical plain-decimal
form: no exponent, no thousands separator, and no insignificant trailing zero.
Use exact decimal arithmetic and the supplied snapshot only.
"""

DIVERSITY_MINIMUMS = {
    "distinctServiceCount": 24,
    "distinctCategoryCount": 16,
    "distinctRegionCount": 16,
    "distinctUnitCount": 6,
    "distinctPositiveUsageCount": 8,
    "loadBandCount": 4,
    "minimumDistinctServicesPerTask": 5,
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DUAL = load_module(
    "pricing_dual_source_for_mixed_load_60",
    EVALUATION_DIR / "build_dual_source_harbor_dataset.py",
)
BASE = DUAL.load_builder()
BASE_TEST = load_module(
    "pricing_benchmark_test_for_mixed_load_60",
    EVALUATION_DIR / "test_benchmark.py",
)
PARQUET_HELPER = load_module(
    "pricing_parquet_helper_for_mixed_load_60",
    PARQUET_HELPER_PATH,
)
VERIFIER = load_module(
    "pricing_verifier_for_mixed_load_60",
    EVALUATION_DIR / "verify_task.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def released_contract() -> tuple[set[str], set[str]]:
    prompts, skus = DUAL.historical_contract()
    prior_batches, _ = DUAL.fresh_batches()
    for batch in prior_batches.values():
        for question in batch:
            prompts.add(question.prompt)
            skus.update(question.source_skus)

    for root in RELEASED_TASK_ROOTS:
        if not root.is_dir():
            continue
        for path in root.glob("*/*/environment/questions.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for question in payload.get("questions", []):
                prompt = question.get("prompt")
                if isinstance(prompt, str):
                    prompts.add(prompt)
                    skus.update(SKU_PATTERN.findall(prompt))
    return prompts, skus


def load_band(value: Decimal) -> str:
    if value == 0:
        return "zero"
    if value < 1:
        return "positive-below-1"
    if value < 1_000:
        return "1-to-999"
    if value < 1_000_000:
        return "1k-to-999k"
    if value < 1_000_000_000:
        return "1m-to-999m"
    return "1b-or-more"


def batches_for(questions: Iterable[Any]) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = {}
    family_order = {family: index for index, family in enumerate(BASE.FAMILIES)}
    for index in range(TASK_COUNT):
        name = f"parquet-mixed-load-{index + 1:02d}"
        batch = sorted(
            (question for question in questions if question.index == index),
            key=lambda question: family_order[question.family],
        )
        result[name] = batch
    return result


def diversity_metrics(questions: list[Any]) -> dict[str, Any]:
    source_skus = sorted({sku for question in questions for sku in question.source_skus})
    service_ids: set[str] = set()
    service_names: set[str] = set()
    categories: set[str] = set()
    regions: set[str] = set()
    units: set[str] = set()
    geo_types: set[str] = set()
    services_by_sku: dict[str, str] = {}

    connection = sqlite3.connect(CATALOG)
    connection.row_factory = sqlite3.Row
    try:
        for sku_id in source_skus:
            row = connection.execute(
                """
                SELECT k.service_id, s.display_name AS service_name, k.geo_type
                FROM skus k JOIN services s USING (service_id)
                WHERE k.sku_id = ?
                """,
                (sku_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"Missing source SKU in normalized catalog: {sku_id}")
            service_ids.add(str(row["service_id"]))
            service_names.add(str(row["service_name"]))
            geo_types.add(str(row["geo_type"]))
            services_by_sku[sku_id] = str(row["service_id"])
            categories.update(
                str(item[0])
                for item in connection.execute(
                    "SELECT category FROM product_categories WHERE sku_id = ?",
                    (sku_id,),
                )
            )
            regions.update(
                str(item[0])
                for item in connection.execute(
                    "SELECT region FROM sku_regions WHERE sku_id = ?",
                    (sku_id,),
                )
            )
            units.update(
                str(item[0])
                for item in connection.execute(
                    """
                    SELECT DISTINCT unit FROM price_models
                    WHERE sku_id = ? AND lower(consumption_model_description) = 'default'
                    """,
                    (sku_id,),
                )
            )

        filtered_services: dict[str, str] = {}
        for question in questions:
            if question.family != "filtered_count":
                continue
            match = FILTER_PATTERN.search(question.prompt)
            if match is None:
                raise RuntimeError(f"Unable to parse filtered-count prompt: {question.prompt}")
            service_id, region, category = match.groups()
            row = connection.execute(
                "SELECT display_name FROM services WHERE service_id = ?",
                (service_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"Missing filtered-count service: {service_id}")
            service_ids.add(service_id)
            service_names.add(str(row[0]))
            filtered_services[question.question_id] = service_id
            regions.add(region)
            categories.add(category)
    finally:
        connection.close()

    usage_values: list[Decimal] = []
    usage_by_family: Counter[str] = Counter()
    for question in questions:
        match = USAGE_PATTERN.search(question.prompt)
        if match is None:
            continue
        usage_values.append(Decimal(match.group(1)))
        usage_by_family[question.family] += 1

    task_service_counts: dict[str, int] = {}
    for name, batch in batches_for(questions).items():
        ids = {
            services_by_sku[sku]
            for question in batch
            for sku in question.source_skus
        }
        for question in batch:
            if question.family == "filtered_count":
                match = FILTER_PATTERN.search(question.prompt)
                if match:
                    ids.add(match.group(1))
        task_service_counts[name] = len(ids)

    family_counts = Counter(question.family for question in questions)
    membership_counts = Counter(
        "present" if question.answer.get("present") is True else "absent"
        for question in questions
        if question.family == "region_membership"
    )
    positive_usage = sorted({value for value in usage_values if value > 0})
    bands = sorted({load_band(value) for value in usage_values})
    return {
        "questionCount": len(questions),
        "namedSkuCount": len(source_skus),
        "distinctServiceCount": len(service_ids),
        "distinctServiceNameCount": len(service_names),
        "serviceNames": sorted(service_names),
        "distinctCategoryCount": len(categories),
        "categories": sorted(categories),
        "distinctRegionCount": len(regions),
        "regions": sorted(regions),
        "distinctUnitCount": len(units),
        "units": sorted(units),
        "geoTypes": sorted(geo_types),
        "numericUsageQuestionCount": len(usage_values),
        "zeroUsageQuestionCount": sum(value == 0 for value in usage_values),
        "positiveUsageQuestionCount": sum(value > 0 for value in usage_values),
        "distinctPositiveUsageCount": len(positive_usage),
        "positiveUsageValues": [BASE.decimal_text(value) for value in positive_usage],
        "loadBands": bands,
        "loadBandCount": len(bands),
        "usageFamilyCounts": dict(sorted(usage_by_family.items())),
        "familyCounts": dict(sorted(family_counts.items())),
        "regionMembershipOutcomeCounts": dict(sorted(membership_counts.items())),
        "distinctServicesPerTask": task_service_counts,
        "minimumDistinctServicesPerTask": min(task_service_counts.values()),
    }


def meets_diversity_minimums(metrics: dict[str, Any]) -> bool:
    return all(metrics[key] >= minimum for key, minimum in DIVERSITY_MINIMUMS.items())


def candidate_score(metrics: dict[str, Any]) -> tuple[int, ...]:
    return (
        metrics["distinctServiceCount"],
        metrics["distinctRegionCount"],
        metrics["distinctCategoryCount"],
        metrics["distinctUnitCount"],
        metrics["distinctPositiveUsageCount"],
        metrics["minimumDistinctServicesPerTask"],
    )


def select_questions() -> tuple[list[Any], dict[str, Any]]:
    released_prompts, released_skus = released_contract()
    candidates: list[tuple[tuple[int, ...], int, list[Any], dict[str, Any]]] = []
    rejected: list[dict[str, Any]] = []
    for offset in range(SEED_CANDIDATE_COUNT):
        seed = SEED_SEARCH_START + offset
        generated = BASE.generate_questions(CATALOG, seed=seed, reserved_skus=released_skus)
        selected = [question for question in generated if question.index < TASK_COUNT]
        prompts = {question.prompt for question in selected}
        skus = {sku for question in selected for sku in question.source_skus}
        if released_prompts & prompts or released_skus & skus:
            raise RuntimeError(f"Seed {seed} overlaps released pricing evidence")
        metrics = diversity_metrics(selected)
        if meets_diversity_minimums(metrics):
            candidates.append((candidate_score(metrics), seed, selected, metrics))
        else:
            rejected.append({"seed": seed, "score": list(candidate_score(metrics))})
    if not candidates:
        raise RuntimeError(
            "No candidate seed met the diversity minimums: "
            + json.dumps({"minimums": DIVERSITY_MINIMUMS, "rejected": rejected})
        )
    candidates.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    score, seed, selected, metrics = candidates[0]
    selection = {
        "seedSearchStart": SEED_SEARCH_START,
        "seedCandidateCount": SEED_CANDIDATE_COUNT,
        "eligibleSeedCount": len(candidates),
        "selectedSeed": seed,
        "selectedScore": list(score),
        "diversityMinimums": DIVERSITY_MINIMUMS,
        "releasedPromptCount": len(released_prompts),
        "releasedNamedSkuCount": len(released_skus),
        "releasedPromptOverlapCount": 0,
        "releasedNamedSkuOverlapCount": 0,
    }
    return selected, {"selection": selection, "diversity": metrics}


def cross_check_answers(questions: list[Any]) -> dict[str, Any]:
    original_helper = BASE_TEST.HELPER
    BASE_TEST.HELPER = PARQUET_HELPER
    connection = PARQUET_HELPER.connect(PARQUET)
    mismatches: list[str] = []
    try:
        for question in questions:
            actual = BASE_TEST.helper_answer(connection, question.family, question.prompt)
            if actual != question.answer:
                mismatches.append(question.question_id)
    finally:
        connection.close()
        BASE_TEST.HELPER = original_helper
    if mismatches:
        raise RuntimeError(f"SQLite and Parquet canonical answers differ: {mismatches}")
    expected = {
        "answers": [
            {"id": question.question_id, "answer": question.answer}
            for question in questions
        ]
    }
    verifier_result = VERIFIER.score(expected, expected)
    if verifier_result["reward"] != 1.0 or not verifier_result["ok"]:
        raise RuntimeError("Canonical answers do not receive full verifier credit")
    return {
        "generationOracle": "normalized SQLite catalog derived from the complete public Pricing API snapshot",
        "independentOracle": "verified Parquet helper over the complete ZSTD snapshot",
        "exactMatchCount": len(questions),
        "exactMismatchCount": 0,
        "canonicalSelfVerifierReward": 1.0,
    }


def question_contract(questions: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": question.question_id,
            "family": question.family,
            "batch": f"parquet-mixed-load-{question.index + 1:02d}",
            "prompt": question.prompt,
        }
        for question in sorted(questions, key=lambda item: item.question_id)
    ]


def answer_contract(questions: list[Any]) -> list[dict[str, Any]]:
    return [
        {"id": question.question_id, "answer": question.answer}
        for question in sorted(questions, key=lambda item: item.question_id)
    ]


def write_task(root: Path, name: str, questions: list[Any]) -> dict[str, Any]:
    task = root / "holdout" / name
    environment = task / "environment"
    tests = task / "tests"
    environment.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PARQUET, environment / "catalog.parquet")
    visible = {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "snapshot_id": SNAPSHOT_ID,
        "batch_id": name,
        "source_format": "parquet",
        "questions": [
            {"id": question.question_id, "family": question.family, "prompt": question.prompt}
            for question in questions
        ],
    }
    expected = {
        "answers": [
            {"id": question.question_id, "answer": question.answer}
            for question in questions
        ]
    }
    write_json(environment / "questions.json", visible)
    write_json(tests / "expected.json", expected)
    shutil.copy2(EVALUATION_DIR / "verify_task.py", tests / "verify_task.py")
    (tests / "test.sh").write_text(TEST_SH, encoding="utf-8", newline="\n")
    (task / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task / "instruction.md").write_text(INSTRUCTION, encoding="utf-8", newline="\n")
    return {
        "name": name,
        "questionCount": len(questions),
        "questionSha256": sha256_file(environment / "questions.json"),
        "expectedSha256": sha256_file(tests / "expected.json"),
        "instructionSha256": sha256_file(task / "instruction.md"),
    }


def validate_inputs() -> dict[str, Any]:
    missing = [path for path in (CATALOG, PARQUET, PARQUET_MANIFEST) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Required pricing artifacts are missing: {missing}")
    source_manifest = json.loads(PARQUET_MANIFEST.read_text(encoding="utf-8"))
    parquet = source_manifest.get("parquet", {})
    source = source_manifest.get("source", {})
    actual_hash = sha256_file(PARQUET)
    if parquet.get("sha256") != actual_hash:
        raise RuntimeError("Parquet SHA-256 does not match its verified manifest")
    if source.get("paginationComplete") is not True:
        raise RuntimeError("Pricing API pagination is not complete")
    if source.get("snapshotId") != SNAPSHOT_ID:
        raise RuntimeError("Unexpected pricing snapshot ID")
    return source_manifest


def build(task_root: Path) -> dict[str, Any]:
    source_manifest = validate_inputs()
    resolved = task_root.resolve()
    if resolved == RUNS_DIR.resolve() or RUNS_DIR.resolve() not in resolved.parents:
        raise ValueError(f"Task root must be below {RUNS_DIR.resolve()}")
    if resolved.exists():
        shutil.rmtree(resolved)

    questions, evidence = select_questions()
    if len(questions) != QUESTION_COUNT:
        raise RuntimeError(f"Expected {QUESTION_COUNT} selected questions, got {len(questions)}")
    family_counts = Counter(question.family for question in questions)
    expected_family_counts = Counter({family: TASK_COUNT for family in BASE.FAMILIES})
    if family_counts != expected_family_counts:
        raise RuntimeError(f"Invalid family distribution: {dict(family_counts)}")
    batches = batches_for(questions)
    for name, batch in batches.items():
        if len(batch) != QUESTIONS_PER_TASK or {q.family for q in batch} != set(BASE.FAMILIES):
            raise RuntimeError(f"Task {name} does not contain one question from every family")

    oracle = cross_check_answers(questions)
    task_evidence = [write_task(resolved, name, batch) for name, batch in batches.items()]
    manifest = {
        "schemaVersion": 1,
        "datasetId": DATASET_ID,
        "snapshotId": SNAPSHOT_ID,
        "taskCount": TASK_COUNT,
        "questionsPerTask": QUESTIONS_PER_TASK,
        "questionCount": QUESTION_COUNT,
        "familyCounts": dict(sorted(family_counts.items())),
        "source": {
            "apiVersion": source_manifest["source"]["apiVersion"],
            "currencyCode": source_manifest["source"]["currencyCode"],
            "paginationComplete": source_manifest["source"]["paginationComplete"],
            "retrievalCompletedAt": source_manifest["source"]["retrievalCompletedAt"],
            "parquetSha256": source_manifest["parquet"]["sha256"],
            "parquetBytes": source_manifest["parquet"]["bytes"],
            "parquetRows": source_manifest["parquet"]["rows"],
            "compression": source_manifest["parquet"]["compression"],
            "compressionLevel": source_manifest["parquet"]["compressionLevel"],
            "decimalType": source_manifest["parquet"]["decimalType"],
        },
        "selection": evidence["selection"],
        "diversity": evidence["diversity"],
        "canonicalAnswerValidation": oracle,
        "questionContractSha256": sha256_json(question_contract(questions)),
        "canonicalAnswerContractSha256": sha256_json(answer_contract(questions)),
        "tasks": task_evidence,
        "canonicalAnswersStoredInManifest": False,
        "evaluationSealed": True,
        "evaluationReleased": True,
        "releaseEvidence": {
            "releasedOn": "2026-08-26",
            "jobName": "google-cloud-sku-pricing-mixed-load-60-luna-20260826-v2",
            "jobId": "6924467e-0fda-40fe-820d-ca34ecfe9a22",
            "completedTrials": 6,
            "passedTrials": 6,
            "evaluatedQuestions": 60,
            "correctQuestions": 60,
            "reward": 1.0,
            "format": 1.0,
            "errors": 0,
            "retries": 0,
            "resultSha256": "04a936b851754b2b56051828b9ce421cf9c603291b9daeee226703b122ea1bd9",
            "reportJson": "reports/mixed-load-60-luna-20260826-v2/final-report.json",
            "reportJsonSha256": "7a5c898a936b2f7614a29981691a1e9f0c50e7bb18af40b679213d46bb048320",
        },
        "requestedRuntime": {
            "harness": "Harbor 0.18.0",
            "agent": "Pi 0.84.2",
            "model": "openai-codex/gpt-5.6-luna",
        },
    }
    write_json(DURABLE_MANIFEST, manifest)
    return verify(resolved)


def verify(task_root: Path) -> dict[str, Any]:
    validate_inputs()
    if not DURABLE_MANIFEST.is_file():
        raise FileNotFoundError(f"Dataset manifest is missing: {DURABLE_MANIFEST}")
    manifest = json.loads(DURABLE_MANIFEST.read_text(encoding="utf-8"))
    findings: list[str] = []
    tasks = sorted(path for path in (task_root / "holdout").glob("*") if path.is_dir())
    if len(tasks) != TASK_COUNT:
        findings.append("task-count")

    question_rows: list[dict[str, Any]] = []
    answer_rows: list[dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    oracle_matches = 0
    original_helper = BASE_TEST.HELPER
    BASE_TEST.HELPER = PARQUET_HELPER
    connection = PARQUET_HELPER.connect(PARQUET)
    try:
        for task in tasks:
            questions_path = task / "environment" / "questions.json"
            expected_path = task / "tests" / "expected.json"
            task_parquet = task / "environment" / "catalog.parquet"
            required = (
                questions_path,
                expected_path,
                task_parquet,
                task / "tests" / "verify_task.py",
                task / "tests" / "test.sh",
                task / "task.toml",
                task / "instruction.md",
            )
            if any(not path.is_file() for path in required):
                findings.append(f"{task.name}:missing-file")
                continue
            if sha256_file(task_parquet) != manifest["source"]["parquetSha256"]:
                findings.append(f"{task.name}:parquet-hash")
            visible = json.loads(questions_path.read_text(encoding="utf-8"))
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            questions = visible.get("questions", [])
            answers = expected.get("answers", [])
            if len(questions) != QUESTIONS_PER_TASK or len(answers) != QUESTIONS_PER_TASK:
                findings.append(f"{task.name}:question-count")
                continue
            if [row.get("id") for row in questions] != [row.get("id") for row in answers]:
                findings.append(f"{task.name}:answer-order")
            if {row.get("family") for row in questions} != set(BASE.FAMILIES):
                findings.append(f"{task.name}:family-coverage")
            self_score = VERIFIER.score(expected, expected)
            if not self_score["ok"] or self_score["reward"] != 1.0:
                findings.append(f"{task.name}:self-verifier")
            expected_by_id = {row["id"]: row["answer"] for row in answers}
            for row in questions:
                question_id = row["id"]
                family_counts[row["family"]] += 1
                question_rows.append(
                    {
                        "id": question_id,
                        "family": row["family"],
                        "batch": task.name,
                        "prompt": row["prompt"],
                    }
                )
                answer_rows.append({"id": question_id, "answer": expected_by_id[question_id]})
                actual = BASE_TEST.helper_answer(connection, row["family"], row["prompt"])
                if actual == expected_by_id[question_id]:
                    oracle_matches += 1
                else:
                    findings.append(f"{question_id}:oracle-mismatch")
            if (task / "environment" / "expected.json").exists():
                findings.append(f"{task.name}:answer-leak")
            if (task / "environment" / "answers.json").exists():
                findings.append(f"{task.name}:preexisting-agent-output")
    finally:
        connection.close()
        BASE_TEST.HELPER = original_helper

    ids = [row["id"] for row in question_rows]
    if len(ids) != len(set(ids)):
        findings.append("duplicate-question-id")
    if len(ids) != QUESTION_COUNT:
        findings.append("question-count")
    if family_counts != Counter({family: TASK_COUNT for family in BASE.FAMILIES}):
        findings.append("family-distribution")
    if sha256_json(sorted(question_rows, key=lambda row: row["id"])) != manifest.get(
        "questionContractSha256"
    ):
        findings.append("question-contract-hash")
    if sha256_json(sorted(answer_rows, key=lambda row: row["id"])) != manifest.get(
        "canonicalAnswerContractSha256"
    ):
        findings.append("answer-contract-hash")
    if manifest.get("canonicalAnswersStoredInManifest") is not False:
        findings.append("manifest-answer-sealing")
    if manifest.get("evaluationSealed") is not True:
        findings.append("evaluation-seal")

    result = {
        "ok": not findings,
        "datasetId": manifest.get("datasetId"),
        "taskCount": len(tasks),
        "questionCount": len(question_rows),
        "familyCounts": dict(sorted(family_counts.items())),
        "independentOracleExactMatchCount": oracle_matches,
        "independentOracleExactMismatchCount": len(question_rows) - oracle_matches,
        "questionContractSha256": manifest.get("questionContractSha256"),
        "canonicalAnswerContractSha256": manifest.get("canonicalAnswerContractSha256"),
        "findings": findings,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--verify-existing", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = verify(args.task_root.resolve()) if args.verify_existing else build(args.task_root)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
