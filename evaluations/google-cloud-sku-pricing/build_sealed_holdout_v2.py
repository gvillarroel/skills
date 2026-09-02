#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replace a contaminated holdout with 20 fresh, SKU-disjoint questions."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BASE_DATASET = REPOSITORY_ROOT / "evaluations" / "datasets" / "google-cloud-sku-pricing-100"
BASE_PROCESSED = BASE_DATASET / "processed"
REVISION_DIR = BASE_PROCESSED / "v2"
DEFAULT_TASK_ROOT = (
    REPOSITORY_ROOT
    / "evaluations"
    / "runs"
    / "google-cloud-sku-pricing-100-holdout-v2-tasks"
)
HOLDOUT_SEED = 20260826


def load_builder() -> Any:
    source = Path(__file__).with_name("build_benchmark.py")
    spec = importlib.util.spec_from_file_location("pricing_benchmark_builder", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load benchmark builder: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def index_from_batch(split: str, batch_id: str) -> int:
    number = int(batch_id.rsplit("-", 1)[1])
    if split == "train":
        return number - 1
    if split == "validation":
        return number + 5
    return number + 7


def load_original_questions(builder: Any, benchmark: Path) -> tuple[list[Any], set[str], set[str]]:
    connection = sqlite3.connect(benchmark)
    connection.row_factory = sqlite3.Row
    questions: list[Any] = []
    reserved_skus: set[str] = set()
    prompts: set[str] = set()
    try:
        rows = list(
            connection.execute(
                """
                SELECT question_id, family, split, batch_id, prompt,
                       expected_json, source_skus_json
                FROM questions ORDER BY question_id
                """
            )
        )
        for row in rows:
            source_skus = tuple(json.loads(row["source_skus_json"]))
            reserved_skus.update(source_skus)
            prompts.add(row["prompt"])
            if row["split"] in {"train", "validation"}:
                questions.append(
                    builder.Question(
                        row["question_id"],
                        row["family"],
                        index_from_batch(row["split"], row["batch_id"]),
                        row["prompt"],
                        json.loads(row["expected_json"]),
                        source_skus,
                    )
                )
    finally:
        connection.close()
    if len(questions) != 80:
        raise RuntimeError(f"Expected 80 preserved train/validation questions, found {len(questions)}")
    return questions, reserved_skus, prompts


def build_revision(task_root: Path) -> dict[str, Any]:
    builder = load_builder()
    catalog_source = BASE_PROCESSED / "catalog.sqlite"
    benchmark_source = BASE_PROCESSED / "benchmark.sqlite"
    base_manifest = json.loads((BASE_PROCESSED / "manifest.json").read_text(encoding="utf-8"))
    preserved, reserved_skus, old_prompts = load_original_questions(builder, benchmark_source)
    fresh_pool = builder.generate_questions(
        catalog_source,
        seed=HOLDOUT_SEED,
        reserved_skus=reserved_skus,
    )
    fresh_holdout = [question for question in fresh_pool if question.split == "holdout"]
    if len(fresh_holdout) != 20:
        raise RuntimeError(f"Expected 20 fresh holdout questions, found {len(fresh_holdout)}")
    fresh_source_skus = {
        sku_id for question in fresh_holdout for sku_id in question.source_skus
    }
    overlap = reserved_skus & fresh_source_skus
    if overlap:
        raise RuntimeError(f"Fresh holdout reuses v1 SKU provenance: {sorted(overlap)}")
    repeated_prompts = old_prompts & {question.prompt for question in fresh_holdout}
    if repeated_prompts:
        raise RuntimeError(f"Fresh holdout repeats {len(repeated_prompts)} v1 prompts")

    combined = [*preserved, *fresh_holdout]
    split_counts = Counter(question.split for question in combined)
    family_counts = Counter(question.family for question in combined)
    if split_counts != Counter(train=60, validation=20, holdout=20):
        raise RuntimeError(f"Invalid revised split counts: {dict(split_counts)}")
    if family_counts != Counter({family: 10 for family in builder.FAMILIES}):
        raise RuntimeError(f"Invalid revised family counts: {dict(family_counts)}")

    REVISION_DIR.mkdir(parents=True, exist_ok=True)
    catalog_revision = REVISION_DIR / "catalog.sqlite"
    shutil.copy2(catalog_source, catalog_revision)
    benchmark_revision = builder.write_benchmark_database(
        REVISION_DIR, base_manifest["snapshotId"], combined
    )
    connection = sqlite3.connect(benchmark_revision)
    try:
        with connection:
            connection.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("holdout_revision", "v2"),
            )
            connection.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("holdout_seed", str(HOLDOUT_SEED)),
            )
    finally:
        connection.close()
    instruction_hashes = builder.write_tasks(
        task_root,
        REPOSITORY_ROOT,
        catalog_revision,
        base_manifest["snapshotId"],
        combined,
    )
    holdout_contract_hash = hashlib.sha256(
        b"".join(
            builder.json_bytes(
                {
                    "id": question.question_id,
                    "family": question.family,
                    "prompt": question.prompt,
                }
            )
            for question in sorted(fresh_holdout, key=lambda item: item.question_id)
        )
    ).hexdigest()
    manifest = {
        "schemaVersion": 1,
        "datasetId": "google-cloud-sku-pricing-100-holdout-v2",
        "baseDatasetId": builder.DATASET_ID,
        "snapshotId": base_manifest["snapshotId"],
        "catalogSha256": sha256_file(catalog_revision),
        "benchmarkSha256": sha256_file(benchmark_revision),
        "questionCount": len(combined),
        "splitCounts": dict(sorted(split_counts.items())),
        "familyCounts": dict(sorted(family_counts.items())),
        "preservedTrainValidationQuestions": 80,
        "freshHoldoutQuestions": 20,
        "holdoutSeed": HOLDOUT_SEED,
        "reservedV1SkuCount": len(reserved_skus),
        "freshHoldoutNamedSkuCount": len(fresh_source_skus),
        "v1SkuOverlapCount": 0,
        "v1PromptOverlapCount": 0,
        "holdoutContractSha256": holdout_contract_hash,
        "canonicalAnswersStoredInManifest": False,
        "reason": "Replace holdout prompts exposed to a reflection model in rejected run v4.",
        "taskInstructionSha256": instruction_hashes,
    }
    write_json(REVISION_DIR / "manifest.json", manifest)
    return verify_existing(task_root)


def verify_existing(task_root: Path) -> dict[str, Any]:
    builder = load_builder()
    manifest = json.loads((REVISION_DIR / "manifest.json").read_text(encoding="utf-8"))
    catalog = REVISION_DIR / "catalog.sqlite"
    benchmark = REVISION_DIR / "benchmark.sqlite"
    findings: list[str] = []
    if not catalog.is_file() or sha256_file(catalog) != manifest["catalogSha256"]:
        findings.append("catalog-hash")
    if not benchmark.is_file() or sha256_file(benchmark) != manifest["benchmarkSha256"]:
        findings.append("benchmark-hash")
    connection = sqlite3.connect(benchmark)
    connection.row_factory = sqlite3.Row
    try:
        rows = list(connection.execute("SELECT family, split, prompt, source_skus_json FROM questions"))
    finally:
        connection.close()
    if len(rows) != 100:
        findings.append("question-count")
    if Counter(row["split"] for row in rows) != Counter(train=60, validation=20, holdout=20):
        findings.append("split-counts")
    base_connection = sqlite3.connect(BASE_PROCESSED / "benchmark.sqlite")
    base_connection.row_factory = sqlite3.Row
    try:
        old_rows = list(base_connection.execute("SELECT prompt, source_skus_json FROM questions"))
    finally:
        base_connection.close()
    old_prompts = {row["prompt"] for row in old_rows}
    old_skus = {sku for row in old_rows for sku in json.loads(row["source_skus_json"])}
    new_holdout = [row for row in rows if row["split"] == "holdout"]
    new_prompts = {row["prompt"] for row in new_holdout}
    new_skus = {sku for row in new_holdout for sku in json.loads(row["source_skus_json"])}
    if old_prompts & new_prompts:
        findings.append("v1-prompt-overlap")
    if old_skus & new_skus:
        findings.append("v1-sku-overlap")
    expected_catalog_hash = sha256_file(catalog) if catalog.is_file() else ""
    task_count = 0
    for split, expected_batches in (("train", 6), ("validation", 2), ("holdout", 2)):
        directories = sorted(path for path in (task_root / split).glob("*") if path.is_dir())
        if len(directories) != expected_batches:
            findings.append(f"task-batches:{split}")
        for task_dir in directories:
            task_count += 1
            visible = json.loads(
                (task_dir / "environment" / "questions.json").read_text(encoding="utf-8")
            )
            expected = json.loads(
                (task_dir / "tests" / "expected.json").read_text(encoding="utf-8")
            )
            if len(visible.get("questions", [])) != 10 or len(expected.get("answers", [])) != 10:
                findings.append(f"task-count:{split}/{task_dir.name}")
            if sha256_file(task_dir / "environment" / "catalog.sqlite") != expected_catalog_hash:
                findings.append(f"task-catalog:{split}/{task_dir.name}")
    if task_count != 10:
        findings.append("task-total")
    result = {
        "ok": not findings,
        "datasetId": manifest["datasetId"],
        "snapshotId": manifest["snapshotId"],
        "questionCount": len(rows),
        "taskCount": task_count,
        "freshHoldoutQuestions": len(new_holdout),
        "v1SkuOverlapCount": len(old_skus & new_skus),
        "v1PromptOverlapCount": len(old_prompts & new_prompts),
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
    task_root = args.task_root.resolve()
    result = verify_existing(task_root) if args.verify_existing else build_revision(task_root)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

