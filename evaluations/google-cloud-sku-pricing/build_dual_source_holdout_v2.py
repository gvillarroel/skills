#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a fresh dual-source holdout after the first Harbor gate was released."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = Path(__file__).resolve().parent
DEFAULT_TASK_ROOT = (
    REPOSITORY_ROOT
    / "evaluations"
    / "runs"
    / "google-cloud-sku-pricing-dual-source-20260826-holdout-v2-tasks"
)
DURABLE_MANIFEST = EVALUATION_DIR / "dual-source-holdout-v2-manifest-20260826.json"
FRESH_SEED = 20260828


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DUAL = load_module(
    "pricing_dual_source_builder_v2",
    EVALUATION_DIR / "build_dual_source_harbor_dataset.py",
)
BASE = DUAL.load_builder()


def new_account_region_case() -> dict[str, Any]:
    contract = DUAL.common_contract("regional-contract-price-in-account-currency")
    contract["requiredAll"] += [
        {"id": "regions", "pattern": r"UNNEST\s*\([^)]*geo_taxonomy\.regions"},
        {"id": "models", "pattern": r"UNNEST\s*\([^)]*consumption_model_prices"},
        {
            "id": "contract-tiers",
            "pattern": r"UNNEST\s*\([^)]*billing_account_price\.tiered_rates",
        },
        {
            "id": "eligible-tier",
            "pattern": r"start_usage_amount[^\n;]*<=\s*usage_amount",
        },
        {"id": "marginal-row", "pattern": r"ROW_NUMBER\s*\(\s*\)\s*OVER"},
        {
            "id": "descending-start",
            "pattern": r"ORDER\s+BY[^)]*start_usage_amount\s+DESC",
        },
        {
            "id": "account-currency-amount",
            "pattern": r"\baccount_currency_amount\b",
        },
        {
            "id": "account-currency-code",
            "pattern": r"\baccount_currency_code\b",
        },
        {
            "id": "safe-normalization",
            "pattern": r"SAFE_DIVIDE\s*\([^)]*account_currency_amount[^)]*pricing_unit_quantity",
        },
        {"id": "sku-output", "pattern": r"\bsku_id\b"},
        {"id": "region-output", "pattern": r"\bregion\b"},
        {"id": "unit-output", "pattern": r"\bpricing_unit_quantity\b"},
    ]
    contract["requiredLiterals"] = [
        "GGGG-HHHH-0006",
        "GGGG-HHHH-0007",
        "asia-northeast1",
        "northamerica-northeast1",
        "Default",
        "750000",
    ]
    contract["forbidden"] += [
        {
            "id": "public-list-tier-source",
            "pattern": r"UNNEST\s*\([^)]*list_price\.tiered_rates",
        },
        {"id": "offset-tier-join", "pattern": r"\bWITH\s+OFFSET\b"},
    ]
    return {
        "split": "holdout",
        "name": "bigquery-holdout-v2-account-region",
        "request": {
            "schema_version": 1,
            "scenario": contract["scenario"],
            "table": "`PROJECT.DATASET.cloud_pricing_export`",
            "requirements": [
                "Use the latest ingestion partition and latest pricing_as_of_time.",
                "For explicit SKUs GGGG-HHHH-0006 and GGGG-HHHH-0007 in asia-northeast1 and northamerica-northeast1 at exact NUMERIC usage 750000, return the Default consumption-model marginal billing-account contract price.",
                "Use only billing_account_price tiers, return account_currency_amount with account_currency_code, and normalize by pricing_unit_quantity using exact NUMERIC arithmetic.",
                "Preserve SKU, region, model, tier start, unit, unit quantity, account currency, normalized rate, and effective time.",
            ],
        },
        "contract": contract,
    }


def fresh_parquet_batch() -> tuple[list[Any], dict[str, Any]]:
    historical_prompts, historical_skus = DUAL.historical_contract()
    previous_batches, _ = DUAL.fresh_batches()
    previous_questions = [
        question for batch in previous_batches.values() for question in batch
    ]
    previous_prompts = {question.prompt for question in previous_questions}
    previous_skus = {
        sku for question in previous_questions for sku in question.source_skus
    }
    reserved_skus = historical_skus | previous_skus
    questions = BASE.generate_questions(
        DUAL.CATALOG,
        seed=FRESH_SEED,
        reserved_skus=reserved_skus,
    )
    holdout = [question for question in questions if question.batch_id == "holdout-01"]
    if len(holdout) != 10 or {question.family for question in holdout} != set(BASE.FAMILIES):
        raise RuntimeError("Fresh v2 Parquet holdout is incomplete")
    prompts = {question.prompt for question in holdout}
    skus = {sku for question in holdout for sku in question.source_skus}
    all_old_prompts = historical_prompts | previous_prompts
    if all_old_prompts & prompts:
        raise RuntimeError("Fresh v2 Parquet holdout repeats a released prompt")
    if reserved_skus & skus:
        raise RuntimeError("Fresh v2 Parquet holdout reuses released named-SKU provenance")
    metadata = {
        "seed": FRESH_SEED,
        "questionCount": len(holdout),
        "namedSkuCount": len(skus),
        "releasedPromptCount": len(all_old_prompts),
        "releasedNamedSkuCount": len(reserved_skus),
        "releasedPromptOverlapCount": 0,
        "releasedNamedSkuOverlapCount": 0,
        "questionContractSha256": hashlib.sha256(
            "\n".join(sorted(prompts)).encode("utf-8")
        ).hexdigest(),
    }
    return holdout, metadata


def build(task_root: Path) -> dict[str, Any]:
    expected_parent = (REPOSITORY_ROOT / "evaluations" / "runs").resolve()
    resolved = task_root.resolve()
    if resolved == expected_parent or expected_parent not in resolved.parents:
        raise ValueError(f"Task root must be below {expected_parent}")
    if resolved.exists():
        shutil.rmtree(resolved)
    batch, metadata = fresh_parquet_batch()
    DUAL.write_parquet_task(
        resolved,
        "parquet-holdout-v2-01",
        batch,
        EVALUATION_DIR / "verify_task.py",
    )
    case = new_account_region_case()
    DUAL.write_bigquery_task(
        resolved,
        case,
        EVALUATION_DIR / "verify_bigquery_sql.py",
    )
    manifest = {
        "schemaVersion": 1,
        "datasetId": "google-cloud-sku-pricing-dual-source-holdout-v2-20260826",
        "snapshotId": "gcp-pricing-636387a8dd1a10dc",
        "taskCount": 2,
        "modeTaskCounts": {"parquet": 1, "bigquery": 1},
        "parquet": {
            "sha256": DUAL.sha256_file(DUAL.PARQUET),
            "bytes": DUAL.PARQUET.stat().st_size,
        },
        "freshParquetQuestions": metadata,
        "bigQueryScenario": case["request"]["scenario"],
        "canonicalAnswersStoredInManifest": False,
        "reason": "Fresh holdout after the first dual-source gate was released and one transferable exact-copy instruction was added.",
        "holdoutReleased": False,
    }
    DUAL.write_json(DURABLE_MANIFEST, manifest)
    return verify(resolved)


def verify(task_root: Path) -> dict[str, Any]:
    manifest = json.loads(DURABLE_MANIFEST.read_text(encoding="utf-8"))
    findings: list[str] = []
    holdout = task_root / "holdout"
    tasks = sorted(path for path in holdout.glob("*") if path.is_dir())
    if len(tasks) != 2:
        findings.append("task-count")
    parquet_tasks = [path for path in tasks if path.name.startswith("parquet-")]
    bigquery_tasks = [path for path in tasks if path.name.startswith("bigquery-")]
    if len(parquet_tasks) != 1 or len(bigquery_tasks) != 1:
        findings.append("mode-balance")
    if parquet_tasks:
        task = parquet_tasks[0]
        questions = json.loads(
            (task / "environment" / "questions.json").read_text(encoding="utf-8")
        )
        expected = json.loads(
            (task / "tests" / "expected.json").read_text(encoding="utf-8")
        )
        if len(questions.get("questions", [])) != 10 or len(expected.get("answers", [])) != 10:
            findings.append("parquet-question-count")
        if DUAL.sha256_file(task / "environment" / "catalog.parquet") != manifest["parquet"]["sha256"]:
            findings.append("parquet-hash")
    if bigquery_tasks:
        task = bigquery_tasks[0]
        request = json.loads(
            (task / "environment" / "request.json").read_text(encoding="utf-8")
        )
        contract = json.loads(
            (task / "tests" / "contract.json").read_text(encoding="utf-8")
        )
        if request.get("scenario") != contract.get("scenario"):
            findings.append("bigquery-scenario")
    result = {
        "ok": not findings,
        "datasetId": manifest["datasetId"],
        "taskCount": len(tasks),
        "modeTaskCounts": {
            "parquet": len(parquet_tasks),
            "bigquery": len(bigquery_tasks),
        },
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
    root = args.task_root.resolve()
    result = verify(root) if args.verify_existing else build(root)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
