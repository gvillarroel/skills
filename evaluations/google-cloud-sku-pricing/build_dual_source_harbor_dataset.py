#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build disjoint Harbor tasks for Parquet and BigQuery pricing workflows."""

from __future__ import annotations

from collections import Counter, defaultdict
import argparse
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
DATASET_ROOT = REPOSITORY_ROOT / "evaluations" / "datasets" / "google-cloud-sku-pricing-100"
CATALOG = DATASET_ROOT / "processed" / "catalog.sqlite"
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
DEFAULT_TASK_ROOT = (
    REPOSITORY_ROOT
    / "evaluations"
    / "runs"
    / "google-cloud-sku-pricing-dual-source-20260826-tasks"
)
DURABLE_MANIFEST = EVALUATION_DIR / "dual-source-harbor-manifest-20260826.json"
FRESH_SEED = 20260827

TASK_TOML = """version = "1.0"

[metadata]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 60.0
"""
TEST_SH_PARQUET = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_task.py"
"""
TEST_SH_SQL = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_bigquery_sql.py"
"""
PARQUET_INSTRUCTION = """Answer all ten questions in `questions.json` from the frozen
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
BIGQUERY_INSTRUCTION = """Generate the BigQuery Standard SQL requested in
`request.json` for the documented Google Cloud Billing pricing export.

Use the installed `google-cloud-sku-pricing` skill. Work only inside this task
workspace and the installed skill. Do not inspect ancestor repositories, prior
trials, evaluator tests, credentials, or network resources. Treat the installed
skill as read-only. Read
`/app/.agents/skills/google-cloud-sku-pricing/SKILL.md` first; it is the only
evaluated skill bundle.

Create exactly one non-empty output file named `query.sql` in the task
workspace. Write plain executable SQL only: no Markdown fence, prose, sample
results, or additional files. Use the exact table and output-view placeholders
from `request.json`. Preserve all requested price, geography, model, tier, unit,
currency, SKU, and effective-time dimensions. Do not require live BigQuery
access and do not invent undocumented fields.
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_builder() -> Any:
    source = EVALUATION_DIR / "build_benchmark.py"
    spec = importlib.util.spec_from_file_location("pricing_benchmark_builder_v3", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load benchmark builder: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def historical_contract() -> tuple[set[str], set[str]]:
    prompts: set[str] = set()
    skus: set[str] = set()
    for benchmark in (
        DATASET_ROOT / "processed" / "benchmark.sqlite",
        DATASET_ROOT / "processed" / "v2" / "benchmark.sqlite",
    ):
        connection = sqlite3.connect(benchmark)
        connection.row_factory = sqlite3.Row
        try:
            for row in connection.execute("SELECT prompt, source_skus_json FROM questions"):
                prompts.add(str(row["prompt"]))
                skus.update(json.loads(row["source_skus_json"]))
        finally:
            connection.close()
    return prompts, skus


def fresh_batches() -> tuple[dict[str, list[Any]], dict[str, Any]]:
    builder = load_builder()
    old_prompts, old_skus = historical_contract()
    questions = builder.generate_questions(
        CATALOG,
        seed=FRESH_SEED,
        reserved_skus=old_skus,
    )
    selected_batches = {
        "parquet-train-01": [q for q in questions if q.batch_id == "train-01"],
        "parquet-train-02": [q for q in questions if q.batch_id == "train-02"],
        "parquet-validation-01": [q for q in questions if q.batch_id == "validation-01"],
        "parquet-holdout-01": [q for q in questions if q.batch_id == "holdout-01"],
    }
    for name, batch in selected_batches.items():
        if len(batch) != 10 or {question.family for question in batch} != set(builder.FAMILIES):
            raise RuntimeError(f"Fresh batch is incomplete: {name}")
    selected = [question for batch in selected_batches.values() for question in batch]
    new_prompts = {question.prompt for question in selected}
    new_skus = {sku for question in selected for sku in question.source_skus}
    if old_prompts & new_prompts:
        raise RuntimeError("Fresh Parquet tasks repeat a historical prompt")
    if old_skus & new_skus:
        raise RuntimeError("Fresh Parquet tasks reuse historical named-SKU provenance")
    split_skus: dict[str, set[str]] = defaultdict(set)
    for name, batch in selected_batches.items():
        split = "train" if "train" in name else "validation" if "validation" in name else "holdout"
        split_skus[split].update(sku for question in batch for sku in question.source_skus)
    if split_skus["train"] & split_skus["validation"]:
        raise RuntimeError("Fresh Parquet train and validation SKU provenance overlaps")
    if split_skus["train"] & split_skus["holdout"]:
        raise RuntimeError("Fresh Parquet train and holdout SKU provenance overlaps")
    if split_skus["validation"] & split_skus["holdout"]:
        raise RuntimeError("Fresh Parquet validation and holdout SKU provenance overlaps")
    metadata = {
        "seed": FRESH_SEED,
        "historicalPromptCount": len(old_prompts),
        "historicalNamedSkuCount": len(old_skus),
        "selectedQuestionCount": len(selected),
        "selectedNamedSkuCount": len(new_skus),
        "historicalPromptOverlapCount": 0,
        "historicalNamedSkuOverlapCount": 0,
        "crossSplitNamedSkuOverlapCount": 0,
        "questionContractSha256": hashlib.sha256(
            "\n".join(sorted(new_prompts)).encode("utf-8")
        ).hexdigest(),
    }
    return selected_batches, metadata


def common_contract(scenario: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "scenario": scenario,
        "requiredAll": [
            {
                "id": "pricing-table",
                "pattern": r"`PROJECT\.DATASET\.cloud_pricing_export`",
            },
            {
                "id": "latest-partition",
                "pattern": r"MAX\s*\(\s*DATE\s*\(\s*_PARTITIONTIME\s*\)\s*\)",
            },
            {
                "id": "effective-time",
                "pattern": r"\bpricing_as_of_time\b",
            },
            {
                "id": "latest-effective-time",
                "pattern": r"MAX\s*\(\s*pricing_as_of_time\s*\)",
            },
        ],
        "requiredAny": [],
        "requiredLiterals": [],
        "forbidden": [
            {"id": "binary-float", "pattern": r"\bFLOAT64\b"},
            {"id": "approximation", "pattern": r"\bAPPROX_[A-Z_]+\b"},
            {"id": "description-region-inference", "pattern": r"REGEXP_[A-Z_]+\s*\([^)]*sku\.description"},
        ],
    }


def bigquery_cases() -> list[dict[str, Any]]:
    regional = common_contract("regional-marginal-list-price")
    regional["requiredAll"] += [
        {"id": "regions", "pattern": r"UNNEST\s*\([^)]*geo_taxonomy\.regions"},
        {"id": "models", "pattern": r"UNNEST\s*\([^)]*consumption_model_prices"},
        {"id": "list-tiers", "pattern": r"UNNEST\s*\([^)]*list_price\.tiered_rates"},
        {"id": "eligible-tier", "pattern": r"start_usage_amount[^\n;]*<=\s*usage_amount"},
        {"id": "marginal-row", "pattern": r"ROW_NUMBER\s*\(\s*\)\s*OVER"},
        {"id": "descending-start", "pattern": r"ORDER\s+BY[^)]*start_usage_amount\s+DESC"},
        {"id": "safe-normalization", "pattern": r"SAFE_DIVIDE\s*\([^)]*usd_amount[^)]*pricing_unit_quantity"},
        {"id": "sku-output", "pattern": r"\bsku_id\b"},
        {"id": "region-output", "pattern": r"\bregion\b"},
        {"id": "unit-output", "pattern": r"\bpricing_unit_quantity\b"},
    ]
    regional["requiredLiterals"] = [
        "AAAA-BBBB-0001",
        "AAAA-BBBB-0002",
        "us-central1",
        "us-east1",
        "Default",
    ]

    progressive = common_contract("progressive-list-cost")
    progressive["requiredAll"] += [
        {"id": "models", "pattern": r"UNNEST\s*\([^)]*consumption_model_prices"},
        {"id": "list-tiers", "pattern": r"UNNEST\s*\([^)]*list_price\.tiered_rates"},
        {"id": "next-tier", "pattern": r"LEAD\s*\(\s*(?:[A-Za-z_][\w]*\.)?start_usage_amount"},
        {"id": "bounded-usage", "pattern": r"\bLEAST\s*\("},
        {"id": "open-final-tier", "pattern": r"\bCOALESCE\s*\("},
        {"id": "tier-sum", "pattern": r"\bSUM\s*\("},
        {"id": "unit-quantity", "pattern": r"\bpricing_unit_quantity\b"},
        {"id": "positive-segment", "pattern": r"usage_amount\s*>\s*(?:[A-Za-z_][\w]*\.)?start_usage_amount"},
    ]
    progressive["requiredAny"] += [
        {
            "id": "exact-division",
            "patterns": [
                r"SAFE_DIVIDE\s*\([^)]*pricing_unit_quantity",
                r"/\s*(?:[A-Za-z_][\w]*\.)?pricing_unit_quantity",
            ],
        }
    ]
    progressive["requiredLiterals"] = ["CCCC-DDDD-0003", "Default", "1500000"]

    flatten = common_contract("latest-normalized-pricing-view")
    flatten["requiredAll"] += [
        {
            "id": "create-view",
            "pattern": r"CREATE\s+OR\s+REPLACE\s+VIEW\s+`PROJECT\.DATASET\.normalized_cloud_pricing`",
        },
        {"id": "regions", "pattern": r"UNNEST\s*\([^)]*geo_taxonomy\.regions"},
        {"id": "global-sentinel", "pattern": r"geo_taxonomy\.type[^\n;]*GLOBAL"},
        {"id": "models", "pattern": r"UNNEST\s*\([^)]*consumption_model_prices"},
        {"id": "list-tiers", "pattern": r"UNNEST\s*\([^)]*list_price\.tiered_rates"},
        {"id": "service-id", "pattern": r"service\.id"},
        {"id": "sku-id", "pattern": r"sku\.id"},
        {"id": "taxonomy", "pattern": r"product_taxonomy"},
        {"id": "unit", "pattern": r"pricing_unit_quantity"},
        {"id": "usd", "pattern": r"usd_amount"},
    ]

    contract = common_contract("separate-list-and-contract-marginal-prices")
    contract["requiredAll"] += [
        {"id": "models", "pattern": r"UNNEST\s*\([^)]*consumption_model_prices"},
        {"id": "list-tiers", "pattern": r"UNNEST\s*\([^)]*list_price\.tiered_rates"},
        {"id": "contract-tiers", "pattern": r"UNNEST\s*\([^)]*billing_account_price\.tiered_rates"},
        {"id": "separate-branches", "pattern": r"\bUNION\s+ALL\b"},
        {"id": "list-label", "pattern": r"['\"][^'\"]*list[^'\"]*['\"]"},
        {"id": "contract-label", "pattern": r"['\"][^'\"]*contract[^'\"]*['\"]"},
        {"id": "marginal-row", "pattern": r"ROW_NUMBER\s*\(\s*\)\s*OVER"},
        {"id": "descending-start", "pattern": r"ORDER\s+BY[^)]*start_usage_amount\s+DESC"},
        {"id": "scope-output", "pattern": r"\bprice_scope\b"},
        {"id": "unit-output", "pattern": r"\bpricing_unit_quantity\b"},
    ]
    contract["requiredLiterals"] = [
        "EEEE-FFFF-0004",
        "EEEE-FFFF-0005",
        "Default",
        "250000",
    ]
    contract["forbidden"] += [
        {"id": "offset-tier-join", "pattern": r"\bWITH\s+OFFSET\b"},
    ]

    return [
        {
            "split": "train",
            "name": "bigquery-train-regional",
            "request": {
                "schema_version": 1,
                "scenario": regional["scenario"],
                "table": "`PROJECT.DATASET.cloud_pricing_export`",
                "requirements": [
                    "Use the latest ingestion partition and latest pricing_as_of_time.",
                    "Compare public list-price marginal tiers for explicit candidate SKUs AAAA-BBBB-0001 and AAAA-BBBB-0002 in us-central1 and us-east1 at usage_amount.",
                    "Use Default consumption model, preserve SKU and region, and normalize USD by pricing_unit_quantity without binary floats.",
                    "Rank only compatible unit and unit-quantity rows.",
                ],
            },
            "contract": regional,
        },
        {
            "split": "train",
            "name": "bigquery-train-progressive",
            "request": {
                "schema_version": 1,
                "scenario": progressive["scenario"],
                "table": "`PROJECT.DATASET.cloud_pricing_export`",
                "requirements": [
                    "Use the latest ingestion partition and latest pricing_as_of_time.",
                    "Calculate progressive public list cost for SKU CCCC-DDDD-0003, Default model, and exact NUMERIC usage 1500000.",
                    "Bound each tier at the next tier start, keep the last tier open to usage, divide by pricing_unit_quantity, and sum tier components.",
                ],
            },
            "contract": progressive,
        },
        {
            "split": "validation",
            "name": "bigquery-validation-view",
            "request": {
                "schema_version": 1,
                "scenario": flatten["scenario"],
                "table": "`PROJECT.DATASET.cloud_pricing_export`",
                "output_view": "`PROJECT.DATASET.normalized_cloud_pricing`",
                "requirements": [
                    "Create or replace the output view from the latest ingestion partition and latest pricing_as_of_time.",
                    "Flatten public consumption-model list tiers and geographic regions without dropping global SKUs.",
                    "Preserve effective time, service, SKU, taxonomy, geography, model, unit quantity, tier start, and USD amount.",
                ],
            },
            "contract": flatten,
        },
        {
            "split": "holdout",
            "name": "bigquery-holdout-contract",
            "request": {
                "schema_version": 1,
                "scenario": contract["scenario"],
                "table": "`PROJECT.DATASET.cloud_pricing_export`",
                "requirements": [
                    "Use the latest ingestion partition and latest pricing_as_of_time.",
                    "For explicit SKUs EEEE-FFFF-0004 and EEEE-FFFF-0005 at usage 250000 and Default model, return marginal public list and billing-account contract prices as separately labeled scopes.",
                    "Unnest list and contract tier arrays independently; never pair tiers by array offset.",
                    "Preserve SKU, model, price scope, tier start, pricing unit quantity, USD amount, and effective time.",
                ],
            },
            "contract": contract,
        },
    ]


def task_split(name: str) -> str:
    if "train" in name:
        return "train"
    if "validation" in name:
        return "validation"
    return "holdout"


def write_parquet_task(task_root: Path, name: str, questions: list[Any], verifier_source: Path) -> None:
    split = task_split(name)
    task = task_root / split / name
    environment = task / "environment"
    tests = task / "tests"
    environment.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PARQUET, environment / "catalog.parquet")
    visible = {
        "schema_version": 1,
        "dataset_id": "google-cloud-sku-pricing-dual-source-20260826",
        "snapshot_id": "gcp-pricing-636387a8dd1a10dc",
        "batch_id": name,
        "source_format": "parquet",
        "questions": [
            {"id": q.question_id, "family": q.family, "prompt": q.prompt}
            for q in questions
        ],
    }
    expected = {
        "answers": [{"id": q.question_id, "answer": q.answer} for q in questions]
    }
    write_json(environment / "questions.json", visible)
    write_json(tests / "expected.json", expected)
    shutil.copy2(verifier_source, tests / "verify_task.py")
    (tests / "test.sh").write_text(TEST_SH_PARQUET, encoding="utf-8", newline="\n")
    (task / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task / "instruction.md").write_text(
        PARQUET_INSTRUCTION, encoding="utf-8", newline="\n"
    )


def write_bigquery_task(task_root: Path, case: dict[str, Any], verifier_source: Path) -> None:
    task = task_root / case["split"] / case["name"]
    environment = task / "environment"
    tests = task / "tests"
    environment.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)
    write_json(environment / "request.json", case["request"])
    write_json(tests / "contract.json", case["contract"])
    shutil.copy2(verifier_source, tests / "verify_bigquery_sql.py")
    (tests / "test.sh").write_text(TEST_SH_SQL, encoding="utf-8", newline="\n")
    (task / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task / "instruction.md").write_text(
        BIGQUERY_INSTRUCTION, encoding="utf-8", newline="\n"
    )


def build(task_root: Path) -> dict[str, Any]:
    if not CATALOG.is_file() or not PARQUET.is_file() or not PARQUET_MANIFEST.is_file():
        raise FileNotFoundError("Generate the catalog, Parquet, and artifact manifest first")
    expected_parent = (REPOSITORY_ROOT / "evaluations" / "runs").resolve()
    resolved_root = task_root.resolve()
    if resolved_root == expected_parent or expected_parent not in resolved_root.parents:
        raise ValueError(f"Task root must be below {expected_parent}")
    if resolved_root.exists():
        shutil.rmtree(resolved_root)
    batches, fresh_metadata = fresh_batches()
    for name, questions in batches.items():
        write_parquet_task(resolved_root, name, questions, EVALUATION_DIR / "verify_task.py")
    cases = bigquery_cases()
    for case in cases:
        write_bigquery_task(resolved_root, case, EVALUATION_DIR / "verify_bigquery_sql.py")
    parquet_manifest = json.loads(PARQUET_MANIFEST.read_text(encoding="utf-8"))
    manifest = {
        "schemaVersion": 1,
        "datasetId": "google-cloud-sku-pricing-dual-source-20260826",
        "snapshotId": "gcp-pricing-636387a8dd1a10dc",
        "taskCount": 8,
        "splitTaskCounts": {"train": 4, "validation": 2, "holdout": 2},
        "modeTaskCounts": {"parquet": 4, "bigquery": 4},
        "parquet": {
            "sha256": sha256_file(PARQUET),
            "bytes": PARQUET.stat().st_size,
            "rows": parquet_manifest["parquet"]["rows"],
            "compression": parquet_manifest["parquet"]["compression"],
            "compressionLevel": parquet_manifest["parquet"]["compressionLevel"],
        },
        "freshParquetQuestions": fresh_metadata,
        "bigQueryScenarios": [
            {"split": case["split"], "name": case["name"], "scenario": case["request"]["scenario"]}
            for case in cases
        ],
        "canonicalAnswersStoredInManifest": False,
        "holdoutReleased": False,
    }
    write_json(DURABLE_MANIFEST, manifest)
    return verify(task_root)


def verify(task_root: Path) -> dict[str, Any]:
    manifest = json.loads(DURABLE_MANIFEST.read_text(encoding="utf-8"))
    findings: list[str] = []
    observed: Counter[str] = Counter()
    modes: Counter[str] = Counter()
    for split, expected_count in (("train", 4), ("validation", 2), ("holdout", 2)):
        tasks = sorted(path for path in (task_root / split).glob("*") if path.is_dir())
        if len(tasks) != expected_count:
            findings.append(f"task-count:{split}")
        for task in tasks:
            observed[split] += 1
            required = [task / "task.toml", task / "instruction.md", task / "tests" / "test.sh"]
            if not all(path.is_file() for path in required):
                findings.append(f"task-files:{split}/{task.name}")
                continue
            if task.name.startswith("parquet-"):
                modes["parquet"] += 1
                questions = json.loads((task / "environment" / "questions.json").read_text(encoding="utf-8"))
                expected = json.loads((task / "tests" / "expected.json").read_text(encoding="utf-8"))
                if len(questions.get("questions", [])) != 10 or len(expected.get("answers", [])) != 10:
                    findings.append(f"parquet-question-count:{split}/{task.name}")
                if sha256_file(task / "environment" / "catalog.parquet") != manifest["parquet"]["sha256"]:
                    findings.append(f"parquet-hash:{split}/{task.name}")
                visible_text = (task / "environment" / "questions.json").read_text(encoding="utf-8")
                if re.search(r'"answer"\s*:', visible_text):
                    findings.append(f"visible-answer:{split}/{task.name}")
            elif task.name.startswith("bigquery-"):
                modes["bigquery"] += 1
                request = json.loads((task / "environment" / "request.json").read_text(encoding="utf-8"))
                contract = json.loads((task / "tests" / "contract.json").read_text(encoding="utf-8"))
                if request.get("scenario") != contract.get("scenario"):
                    findings.append(f"scenario:{split}/{task.name}")
                if (task / "environment" / "query.sql").exists():
                    findings.append(f"visible-solution:{split}/{task.name}")
            else:
                findings.append(f"unknown-mode:{split}/{task.name}")
    if observed != Counter(train=4, validation=2, holdout=2):
        findings.append("split-distribution")
    if modes != Counter(parquet=4, bigquery=4):
        findings.append("mode-distribution")
    for split in ("train", "validation", "holdout"):
        split_tasks = [path.name for path in (task_root / split).glob("*") if path.is_dir()]
        if not any(name.startswith("parquet-") for name in split_tasks) or not any(
            name.startswith("bigquery-") for name in split_tasks
        ):
            findings.append(f"mode-balance:{split}")
    result = {
        "ok": not findings,
        "datasetId": manifest["datasetId"],
        "taskCount": sum(observed.values()),
        "splitTaskCounts": dict(sorted(observed.items())),
        "modeTaskCounts": dict(sorted(modes.items())),
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
    result = verify(task_root) if args.verify_existing else build(task_root)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
