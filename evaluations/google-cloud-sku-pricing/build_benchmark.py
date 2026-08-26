#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch, normalize, and freeze the 100-question SKU pricing benchmark."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import sqlite3
import subprocess
import sys
import time
from typing import Any, Iterable, Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DATASET_ID = "google-cloud-sku-pricing-100"
SEED = 20260825
API_ROOT = "https://cloudbilling.googleapis.com/v2beta"
FAMILIES = (
    "geography",
    "sku_identity",
    "model_inventory",
    "list_rate",
    "normalized_rate",
    "marginal_tier",
    "progressive_cost",
    "region_membership",
    "filtered_count",
    "compatible_comparison",
)
TASK_TOML = """version = \"1.0\"

[metadata]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 60.0
"""
TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 \"$(dirname \"$0\")/verify_task.py\"
"""
INSTRUCTION = """Answer all ten questions in `questions.json` from the frozen
`catalog.sqlite` database in this task workspace.

Use the installed `google-cloud-sku-pricing` skill. Work only inside this task
workspace and the installed skill. Do not inspect ancestor repositories, prior
trials, evaluator tests, credentials, or network resources. Treat the installed
skill as read-only. Read
`/app/.agents/skills/google-cloud-sku-pricing/SKILL.md` first; it is the only
evaluated skill bundle.

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


@dataclass(frozen=True)
class Question:
    question_id: str
    family: str
    index: int
    prompt: str
    answer: dict[str, Any]
    source_skus: tuple[str, ...]

    @property
    def split(self) -> str:
        if self.index < 6:
            return "train"
        if self.index < 8:
            return "validation"
        return "holdout"

    @property
    def batch_number(self) -> int:
        if self.split == "train":
            return self.index + 1
        if self.split == "validation":
            return self.index - 5
        return self.index - 7

    @property
    def batch_id(self) -> str:
        return f"{self.split}-{self.batch_number:02d}"


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def money_decimal(value: dict[str, Any]) -> Decimal:
    units = Decimal(str(value.get("units", "0")))
    nanos = Decimal(str(value.get("nanos", "0")))
    with localcontext() as context:
        context.prec = 50
        return units + nanos / Decimal(1_000_000_000)


def resource_id(value: str) -> str:
    return value.rstrip("/").split("/")[-1]


def raw_rows(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from error
            if not isinstance(value, dict):
                raise ValueError(f"Expected an object at {path}:{line_number}")
            yield value


def gcloud_access_token(explicit: Path | None) -> str:
    configured = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN")
    if configured:
        return configured
    candidates = [
        str(explicit) if explicit else "",
        shutil.which("gcloud.cmd") or "",
        shutil.which("gcloud") or "",
        str(
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / "gcloud.cmd"
        ),
    ]
    executable = next((candidate for candidate in candidates if candidate and Path(candidate).exists()), None)
    if executable is None:
        raise RuntimeError("gcloud is unavailable and GOOGLE_OAUTH_ACCESS_TOKEN is unset")
    completed = subprocess.run(
        [executable, "auth", "print-access-token"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    token = completed.stdout.strip()
    if completed.returncode != 0 or not token:
        raise RuntimeError("gcloud could not provide an OAuth access token")
    return token


def fetch_collection(
    *,
    token: str,
    endpoint: str,
    collection_key: str,
    destination: Path,
    page_size: int,
    extra_parameters: dict[str, str] | None = None,
) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    pages = 0
    page_token = ""
    with destination.open("wb") as output:
        while True:
            parameters = {"pageSize": str(page_size), **(extra_parameters or {})}
            if page_token:
                parameters["pageToken"] = page_token
            url = f"{API_ROOT}/{endpoint}?{urlencode(parameters)}"
            request = Request(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "User-Agent": "google-cloud-sku-pricing-benchmark/1",
                },
            )
            payload: dict[str, Any] | None = None
            for attempt in range(6):
                try:
                    with urlopen(request, timeout=120) as response:
                        decoded = json.loads(response.read().decode("utf-8"))
                    if not isinstance(decoded, dict):
                        raise RuntimeError(f"Unexpected API payload for {endpoint}")
                    payload = decoded
                    break
                except HTTPError as error:
                    if error.code not in {429, 500, 502, 503, 504} or attempt == 5:
                        raise RuntimeError(f"Pricing API request failed with HTTP {error.code}") from error
                except URLError as error:
                    if attempt == 5:
                        raise RuntimeError("Pricing API request failed after retries") from error
                time.sleep(min(2**attempt, 16))
            assert payload is not None
            rows = payload.get(collection_key, [])
            if not isinstance(rows, list):
                raise RuntimeError(f"Pricing API field {collection_key!r} is not an array")
            for row in rows:
                if not isinstance(row, dict):
                    raise RuntimeError(f"Pricing API {collection_key} contains a non-object")
                output.write(json_bytes(row))
                count += 1
            pages += 1
            page_token = str(payload.get("nextPageToken", ""))
            print(f"Fetched {collection_key}: page {pages}, rows {count}", flush=True)
            if not page_token:
                break
    return {
        "endpoint": f"{API_ROOT}/{endpoint}",
        "collection": collection_key,
        "pages": pages,
        "rows": count,
        "sha256": sha256_file(destination),
        "file": destination.name,
    }


def fetch_snapshot(raw_dir: Path, currency: str, page_size: int, gcloud: Path | None) -> dict[str, Any]:
    token = gcloud_access_token(gcloud)
    retrieval_started = datetime.now(timezone.utc).isoformat()
    sources = [
        fetch_collection(
            token=token,
            endpoint="services",
            collection_key="services",
            destination=raw_dir / "services.jsonl",
            page_size=page_size,
        ),
        fetch_collection(
            token=token,
            endpoint="skus",
            collection_key="skus",
            destination=raw_dir / "skus.jsonl",
            page_size=page_size,
        ),
        fetch_collection(
            token=token,
            endpoint="skus/-/prices",
            collection_key="prices",
            destination=raw_dir / f"prices-{currency.casefold()}.jsonl",
            page_size=page_size,
            extra_parameters={"currencyCode": currency},
        ),
    ]
    digest = hashlib.sha256("".join(source["sha256"] for source in sources).encode("ascii")).hexdigest()
    manifest = {
        "schemaVersion": 1,
        "datasetId": DATASET_ID,
        "apiVersion": "v2beta",
        "currencyCode": currency,
        "pageSize": page_size,
        "retrievalStartedAt": retrieval_started,
        "retrievalCompletedAt": datetime.now(timezone.utc).isoformat(),
        "paginationComplete": True,
        "snapshotId": f"gcp-pricing-{digest[:16]}",
        "sources": sources,
    }
    write_json(raw_dir / "manifest.json", manifest)
    return manifest


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE services (
  service_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  display_name TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE skus (
  sku_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  display_name TEXT NOT NULL,
  service_id TEXT NOT NULL REFERENCES services(service_id),
  geo_type TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE sku_regions (
  sku_id TEXT NOT NULL REFERENCES skus(sku_id),
  region TEXT NOT NULL,
  PRIMARY KEY (sku_id, region)
) WITHOUT ROWID;
CREATE TABLE product_categories (
  sku_id TEXT NOT NULL REFERENCES skus(sku_id),
  position INTEGER NOT NULL,
  category TEXT NOT NULL,
  PRIMARY KEY (sku_id, position)
) WITHOUT ROWID;
CREATE TABLE price_models (
  sku_id TEXT NOT NULL REFERENCES skus(sku_id),
  consumption_model_id TEXT NOT NULL,
  consumption_model_description TEXT NOT NULL,
  currency_code TEXT NOT NULL,
  unit TEXT NOT NULL,
  unit_description TEXT NOT NULL,
  unit_quantity TEXT NOT NULL,
  aggregation_level TEXT NOT NULL,
  aggregation_interval TEXT NOT NULL,
  PRIMARY KEY (sku_id, consumption_model_id)
) WITHOUT ROWID;
CREATE TABLE price_tiers (
  sku_id TEXT NOT NULL,
  consumption_model_id TEXT NOT NULL,
  position INTEGER NOT NULL,
  start_amount TEXT NOT NULL,
  list_price TEXT NOT NULL,
  PRIMARY KEY (sku_id, consumption_model_id, position),
  FOREIGN KEY (sku_id, consumption_model_id)
    REFERENCES price_models(sku_id, consumption_model_id)
) WITHOUT ROWID;
CREATE INDEX idx_sku_service ON skus(service_id);
CREATE INDEX idx_regions_region ON sku_regions(region, sku_id);
CREATE INDEX idx_categories_category ON product_categories(category, sku_id);
CREATE INDEX idx_models_description ON price_models(consumption_model_description, sku_id);
CREATE INDEX idx_tiers_lookup ON price_tiers(sku_id, consumption_model_id, position);
"""


def normalize_geo(sku: dict[str, Any]) -> tuple[str, list[str]]:
    taxonomy = sku.get("geoTaxonomy") or {}
    api_type = str(taxonomy.get("type", "TYPE_UNSPECIFIED"))
    geo_type = api_type.removeprefix("TYPE_")
    regions: set[str] = set()
    if geo_type == "REGIONAL":
        region = (((taxonomy.get("regionalMetadata") or {}).get("region") or {}).get("region"))
        if region:
            regions.add(str(region))
    elif geo_type == "MULTI_REGIONAL":
        rows = ((taxonomy.get("multiRegionalMetadata") or {}).get("regions") or [])
        for row in rows:
            if isinstance(row, dict) and row.get("region"):
                regions.add(str(row["region"]))
    return geo_type, sorted(regions)


def normalize_catalog(
    raw_dir: Path,
    processed_dir: Path,
    raw_manifest: dict[str, Any],
) -> tuple[Path, dict[str, int]]:
    database = processed_dir / "catalog.sqlite"
    processed_dir.mkdir(parents=True, exist_ok=True)
    if database.exists():
        database.unlink()
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA journal_mode = OFF")
    connection.execute("PRAGMA synchronous = OFF")
    connection.executescript(SCHEMA_SQL)
    metrics: Counter[str] = Counter()
    try:
        with connection:
            metadata = {
                "dataset_id": DATASET_ID,
                "snapshot_id": str(raw_manifest["snapshotId"]),
                "api_version": str(raw_manifest["apiVersion"]),
                "currency_code": str(raw_manifest["currencyCode"]),
                "retrieved_at": str(raw_manifest["retrievalCompletedAt"]),
                "pagination_complete": "true",
            }
            connection.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)", sorted(metadata.items())
            )
            for service in raw_rows(raw_dir / "services.jsonl"):
                service_id = str(service.get("serviceId") or resource_id(str(service.get("name", ""))))
                if not service_id:
                    metrics["rejected_services"] += 1
                    continue
                connection.execute(
                    "INSERT OR REPLACE INTO services(service_id, name, display_name) VALUES (?, ?, ?)",
                    (service_id, str(service.get("name", "")), str(service.get("displayName", service_id))),
                )
                metrics["services"] += 1

            service_ids = {row[0] for row in connection.execute("SELECT service_id FROM services")}
            for sku in raw_rows(raw_dir / "skus.jsonl"):
                sku_id = str(sku.get("skuId") or resource_id(str(sku.get("name", ""))))
                service_id = resource_id(str(sku.get("service", "")))
                if not sku_id or service_id not in service_ids:
                    metrics["rejected_skus"] += 1
                    continue
                geo_type, regions = normalize_geo(sku)
                connection.execute(
                    """
                    INSERT OR REPLACE INTO skus(sku_id, name, display_name, service_id, geo_type)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        sku_id,
                        str(sku.get("name", "")),
                        str(sku.get("displayName", sku_id)),
                        service_id,
                        geo_type,
                    ),
                )
                for region in regions:
                    connection.execute(
                        "INSERT OR IGNORE INTO sku_regions(sku_id, region) VALUES (?, ?)",
                        (sku_id, region),
                    )
                    metrics["sku_regions"] += 1
                categories = ((sku.get("productTaxonomy") or {}).get("taxonomyCategories") or [])
                for position, category in enumerate(categories):
                    if isinstance(category, dict) and category.get("category"):
                        connection.execute(
                            "INSERT OR REPLACE INTO product_categories(sku_id, position, category) VALUES (?, ?, ?)",
                            (sku_id, position, str(category["category"])),
                        )
                        metrics["product_categories"] += 1
                metrics["skus"] += 1

            sku_ids = {row[0] for row in connection.execute("SELECT sku_id FROM skus")}
            prices_path = raw_dir / f"prices-{str(raw_manifest['currencyCode']).casefold()}.jsonl"
            for price in raw_rows(prices_path):
                name_parts = str(price.get("name", "")).split("/")
                sku_id = name_parts[1] if len(name_parts) >= 3 and name_parts[0] == "skus" else ""
                if sku_id not in sku_ids:
                    metrics["rejected_prices"] += 1
                    continue
                for model in price.get("skuPrices") or []:
                    if not isinstance(model, dict) or str(model.get("valueType", "")).casefold() != "rate":
                        metrics["rejected_non_rate_models"] += 1
                        continue
                    rate = model.get("rate") or {}
                    unit_info = rate.get("unitInfo") or {}
                    aggregation = rate.get("aggregationInfo") or {}
                    model_id = resource_id(str(model.get("consumptionModel", "")))
                    unit_quantity = str(((unit_info.get("unitQuantity") or {}).get("value", "1")))
                    tiers = rate.get("tiers") or []
                    if not model_id or not unit_info.get("unit") or not tiers or Decimal(unit_quantity) == 0:
                        metrics["rejected_incomplete_models"] += 1
                        continue
                    first_money = (tiers[0].get("listPrice") or {}) if isinstance(tiers[0], dict) else {}
                    currency_code = str(first_money.get("currencyCode") or price.get("currencyCode") or "")
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO price_models(
                          sku_id, consumption_model_id, consumption_model_description,
                          currency_code, unit, unit_description, unit_quantity,
                          aggregation_level, aggregation_interval
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            sku_id,
                            model_id,
                            str(model.get("consumptionModelDescription", model_id)),
                            currency_code,
                            str(unit_info.get("unit", "")),
                            str(unit_info.get("unitDescription", "")),
                            decimal_text(Decimal(unit_quantity)),
                            str(aggregation.get("level", "")),
                            str(aggregation.get("interval", "")),
                        ),
                    )
                    connection.execute(
                        "DELETE FROM price_tiers WHERE sku_id = ? AND consumption_model_id = ?",
                        (sku_id, model_id),
                    )
                    inserted_tiers = 0
                    for position, tier in enumerate(tiers):
                        if not isinstance(tier, dict) or not isinstance(tier.get("listPrice"), dict):
                            continue
                        start = Decimal(str(((tier.get("startAmount") or {}).get("value", "0"))))
                        amount = money_decimal(tier["listPrice"])
                        connection.execute(
                            """
                            INSERT INTO price_tiers(
                              sku_id, consumption_model_id, position, start_amount, list_price
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                sku_id,
                                model_id,
                                position,
                                decimal_text(start),
                                decimal_text(amount),
                            ),
                        )
                        inserted_tiers += 1
                        metrics["price_tiers"] += 1
                    if inserted_tiers:
                        metrics["price_models"] += 1
            connection.execute("ANALYZE")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Catalog integrity check failed: {integrity}")
    finally:
        connection.close()
    return database, dict(metrics)


def model_for(connection: sqlite3.Connection, sku_id: str) -> sqlite3.Row:
    row = connection.execute(
        """
        SELECT * FROM price_models
        WHERE sku_id = ? AND lower(consumption_model_description) = 'default'
        ORDER BY consumption_model_id LIMIT 1
        """,
        (sku_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"SKU {sku_id} has no Default price model")
    return row


def tiers_for(connection: sqlite3.Connection, sku_id: str, model_id: str) -> list[tuple[Decimal, Decimal]]:
    tiers = [
        (Decimal(row["start_amount"]), Decimal(row["list_price"]))
        for row in connection.execute(
            """
            SELECT start_amount, list_price FROM price_tiers
            WHERE sku_id = ? AND consumption_model_id = ? ORDER BY position
            """,
            (sku_id, model_id),
        )
    ]
    tiers.sort(key=lambda item: item[0])
    return tiers


def tier_at(tiers: list[tuple[Decimal, Decimal]], usage: Decimal) -> tuple[Decimal, Decimal]:
    eligible = [tier for tier in tiers if tier[0] <= usage]
    if not eligible:
        raise ValueError("Usage precedes the first price tier")
    return eligible[-1]


def progressive_total(
    tiers: list[tuple[Decimal, Decimal]], usage: Decimal, unit_quantity: Decimal
) -> Decimal:
    total = Decimal(0)
    with localcontext() as context:
        context.prec = 50
        for index, (start, price) in enumerate(tiers):
            if usage <= start:
                break
            end = tiers[index + 1][0] if index + 1 < len(tiers) else usage
            quantity = min(usage, end) - start
            if quantity > 0:
                total += quantity / unit_quantity * price
    return total


def shuffled(rows: Iterable[Any], rng: random.Random) -> list[Any]:
    values = list(rows)
    rng.shuffle(values)
    return values


def question_id(family: str, index: int) -> str:
    return f"gcp-{family.replace('_', '-')}-{index + 1:02d}"


def generate_questions(
    database: Path,
    *,
    seed: int = SEED,
    reserved_skus: Iterable[str] = (),
) -> list[Question]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    rng = random.Random(seed)
    used_skus: set[str] = set(reserved_skus)
    questions: list[Question] = []

    def add(family: str, index: int, prompt: str, answer: dict[str, Any], skus: Iterable[str] = ()) -> None:
        source = tuple(skus)
        duplicate = used_skus.intersection(source)
        if duplicate:
            raise RuntimeError(f"Benchmark SKU reuse detected: {sorted(duplicate)}")
        used_skus.update(source)
        questions.append(Question(question_id(family, index), family, index, prompt, answer, source))

    try:
        # Geography deliberately balances global, regional, and multi-regional rows.
        geo_sequence = ["GLOBAL", "REGIONAL", "MULTI_REGIONAL", "REGIONAL", "MULTI_REGIONAL"] * 2
        geo_buckets: dict[str, list[sqlite3.Row]] = {}
        for geo_type in set(geo_sequence):
            geo_buckets[geo_type] = shuffled(
                connection.execute(
                    """
                    SELECT DISTINCT k.sku_id, k.geo_type
                    FROM skus k JOIN price_models m USING (sku_id)
                    WHERE k.geo_type = ? AND lower(m.consumption_model_description) = 'default'
                    ORDER BY k.sku_id
                    """,
                    (geo_type,),
                ),
                rng,
            )
        for index, geo_type in enumerate(geo_sequence):
            row = next(row for row in geo_buckets[geo_type] if row["sku_id"] not in used_skus)
            sku_id = row["sku_id"]
            regions = [
                item[0]
                for item in connection.execute(
                    "SELECT region FROM sku_regions WHERE sku_id = ? ORDER BY region", (sku_id,)
                )
            ]
            add(
                "geography",
                index,
                f"For SKU `{sku_id}`, return exactly `geo_type` and `regions`. Use `GLOBAL`, "
                "`REGIONAL`, or `MULTI_REGIONAL`; sort regions alphabetically and use an empty array for global.",
                {"geo_type": geo_type, "regions": regions},
                [sku_id],
            )

        priced_skus = shuffled(
            (
                row[0]
                for row in connection.execute(
                    """
                    SELECT DISTINCT k.sku_id FROM skus k JOIN price_models m USING (sku_id)
                    WHERE lower(m.consumption_model_description) = 'default' ORDER BY k.sku_id
                    """
                )
            ),
            rng,
        )
        identity_skus = [sku for sku in priced_skus if sku not in used_skus][:10]
        if len(identity_skus) != 10:
            raise RuntimeError("Insufficient priced SKUs for identity questions")
        for index, sku_id in enumerate(identity_skus):
            row = connection.execute(
                """
                SELECT k.display_name AS sku_description, s.display_name AS service_name
                FROM skus k JOIN services s USING (service_id) WHERE k.sku_id = ?
                """,
                (sku_id,),
            ).fetchone()
            add(
                "sku_identity",
                index,
                f"For SKU `{sku_id}`, return exactly its `sku_description` and `service_name` as stored in the snapshot.",
                {"sku_description": row["sku_description"], "service_name": row["service_name"]},
                [sku_id],
            )

        inventory_skus = shuffled(
            (
                row[0]
                for row in connection.execute(
                    """
                    SELECT sku_id FROM price_models GROUP BY sku_id HAVING COUNT(*) >= 2 ORDER BY sku_id
                    """
                )
                if row[0] not in used_skus
            ),
            rng,
        )[:10]
        if len(inventory_skus) != 10:
            raise RuntimeError("Insufficient multi-model SKUs for inventory questions")
        for index, sku_id in enumerate(inventory_skus):
            models = [
                {
                    "consumption_model_id": row["consumption_model_id"],
                    "consumption_model_description": row["consumption_model_description"],
                }
                for row in connection.execute(
                    """
                    SELECT consumption_model_id, consumption_model_description FROM price_models
                    WHERE sku_id = ? ORDER BY consumption_model_description, consumption_model_id
                    """,
                    (sku_id,),
                )
            ]
            add(
                "model_inventory",
                index,
                f"For SKU `{sku_id}`, return exactly `model_count` and `models`. Each model must contain "
                "`consumption_model_id` and `consumption_model_description`; sort by description, then ID.",
                {"model_count": len(models), "models": models},
                [sku_id],
            )

        rate_skus = [sku for sku in priced_skus if sku not in used_skus][:10]
        if len(rate_skus) != 10:
            raise RuntimeError("Insufficient SKUs for list-rate questions")
        for index, sku_id in enumerate(rate_skus):
            model = model_for(connection, sku_id)
            tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
            usage = tiers[0][0]
            start, price = tier_at(tiers, usage)
            add(
                "list_rate",
                index,
                f"For SKU `{sku_id}` using consumption model `Default` at usage `{decimal_text(usage)}`, "
                "return exactly `currency`, `unit`, `pricing_unit_quantity`, `tier_start`, and "
                "`price_per_pricing_unit`.",
                {
                    "currency": model["currency_code"],
                    "unit": model["unit"],
                    "pricing_unit_quantity": model["unit_quantity"],
                    "tier_start": decimal_text(start),
                    "price_per_pricing_unit": decimal_text(price),
                },
                [sku_id],
            )

        normalized_candidates = shuffled(
            (
                row[0]
                for row in connection.execute(
                    """
                    SELECT DISTINCT m.sku_id FROM price_models m JOIN price_tiers t
                      ON t.sku_id = m.sku_id AND t.consumption_model_id = m.consumption_model_id
                    WHERE lower(m.consumption_model_description) = 'default'
                      AND m.unit_quantity NOT IN ('0', '1') AND t.list_price != '0'
                    ORDER BY m.sku_id
                    """
                )
                if row[0] not in used_skus
            ),
            rng,
        )
        if len(normalized_candidates) < 10:
            normalized_candidates.extend(
                sku for sku in priced_skus if sku not in used_skus and sku not in normalized_candidates
            )
        normalized_skus = normalized_candidates[:10]
        if len(normalized_skus) != 10:
            raise RuntimeError("Insufficient SKUs for normalized-rate questions")
        for index, sku_id in enumerate(normalized_skus):
            model = model_for(connection, sku_id)
            tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
            usage = tiers[0][0]
            start, price = tier_at(tiers, usage)
            with localcontext() as context:
                context.prec = 50
                normalized = price / Decimal(model["unit_quantity"])
            add(
                "normalized_rate",
                index,
                f"For SKU `{sku_id}`, model `Default`, and usage `{decimal_text(usage)}`, normalize the "
                "applicable list price to one base unit. Return exactly `currency`, `unit`, `tier_start`, "
                "and `price_per_base_unit`.",
                {
                    "currency": model["currency_code"],
                    "unit": model["unit"],
                    "tier_start": decimal_text(start),
                    "price_per_base_unit": decimal_text(normalized),
                },
                [sku_id],
            )

        multi_tier = shuffled(
            (
                row[0]
                for row in connection.execute(
                    """
                    SELECT m.sku_id FROM price_models m JOIN price_tiers t
                      ON t.sku_id = m.sku_id AND t.consumption_model_id = m.consumption_model_id
                    WHERE lower(m.consumption_model_description) = 'default'
                    GROUP BY m.sku_id, m.consumption_model_id HAVING COUNT(*) >= 2
                    ORDER BY m.sku_id
                    """
                )
                if row[0] not in used_skus
            ),
            rng,
        )
        marginal_skus = multi_tier[:10]
        cost_skus = multi_tier[10:20]
        if len(marginal_skus) != 10 or len(cost_skus) != 10:
            raise RuntimeError(f"Need 20 unused multi-tier SKUs, found {len(multi_tier)}")
        for index, sku_id in enumerate(marginal_skus):
            model = model_for(connection, sku_id)
            tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
            usage = tiers[min(1 + index % (len(tiers) - 1), len(tiers) - 1)][0]
            start, price = tier_at(tiers, usage)
            add(
                "marginal_tier",
                index,
                f"For SKU `{sku_id}` using model `Default` at exact usage `{decimal_text(usage)}`, return "
                "exactly the applicable marginal `tier_start`, `price_per_pricing_unit`, and `currency`.",
                {
                    "tier_start": decimal_text(start),
                    "price_per_pricing_unit": decimal_text(price),
                    "currency": model["currency_code"],
                },
                [sku_id],
            )
        for index, sku_id in enumerate(cost_skus):
            model = model_for(connection, sku_id)
            tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
            unit_quantity = Decimal(model["unit_quantity"])
            usage = tiers[1][0] + unit_quantity * Decimal(index + 2)
            total = progressive_total(tiers, usage, unit_quantity)
            add(
                "progressive_cost",
                index,
                f"For SKU `{sku_id}` with model `Default`, calculate progressive tiered list cost for "
                f"usage `{decimal_text(usage)}`. Return exactly `currency` and `total_cost`; do not use "
                "the final marginal rate for all usage.",
                {"currency": model["currency_code"], "total_cost": decimal_text(total)},
                [sku_id],
            )

        all_regions = [row[0] for row in connection.execute("SELECT DISTINCT region FROM sku_regions ORDER BY region")]
        membership_candidates = shuffled(
            (
                row[0]
                for row in connection.execute(
                    """
                    SELECT DISTINCT k.sku_id FROM skus k JOIN sku_regions r USING (sku_id)
                    JOIN price_models m USING (sku_id)
                    WHERE lower(m.consumption_model_description) = 'default' ORDER BY k.sku_id
                    """
                )
                if row[0] not in used_skus
            ),
            rng,
        )[:10]
        if len(membership_candidates) != 10:
            raise RuntimeError("Insufficient regional SKUs for membership questions")
        for index, sku_id in enumerate(membership_candidates):
            regions = [
                row[0]
                for row in connection.execute(
                    "SELECT region FROM sku_regions WHERE sku_id = ? ORDER BY region", (sku_id,)
                )
            ]
            if index % 2 == 0:
                region = regions[index % len(regions)]
                present = True
            else:
                region = next(candidate for candidate in all_regions if candidate not in regions)
                present = False
            add(
                "region_membership",
                index,
                f"Does SKU `{sku_id}` explicitly include region `{region}` in its geographic metadata? "
                "Return exactly `region` and boolean `present`.",
                {"region": region, "present": present},
                [sku_id],
            )

        count_rows = shuffled(
            connection.execute(
                """
                SELECT k.service_id, r.region, c.category, COUNT(DISTINCT k.sku_id) AS sku_count
                FROM skus k JOIN sku_regions r USING (sku_id)
                JOIN product_categories c USING (sku_id)
                JOIN price_models m USING (sku_id)
                WHERE lower(m.consumption_model_description) = 'default'
                GROUP BY k.service_id, r.region, c.category
                HAVING COUNT(DISTINCT k.sku_id) BETWEEN 2 AND 200
                ORDER BY k.service_id, r.region, c.category
                """
            ),
            rng,
        )
        selected_filters: list[sqlite3.Row] = []
        seen_filter_dimensions: set[tuple[str, str, str]] = set()
        for row in count_rows:
            key = (row["service_id"], row["region"], row["category"])
            if key not in seen_filter_dimensions:
                selected_filters.append(row)
                seen_filter_dimensions.add(key)
            if len(selected_filters) == 10:
                break
        if len(selected_filters) != 10:
            raise RuntimeError("Insufficient non-trivial filtered count combinations")
        for index, row in enumerate(selected_filters):
            add(
                "filtered_count",
                index,
                f"Count distinct SKUs whose service ID is `{row['service_id']}`, geographic region is "
                f"`{row['region']}`, and taxonomy contains exact category `{row['category']}`. Return "
                "exactly integer `count`.",
                {"count": int(row["sku_count"])},
            )

        comparison_groups: dict[tuple[str, str, str, str], list[tuple[str, Decimal]]] = defaultdict(list)
        for row in connection.execute(
            """
            SELECT k.sku_id, k.service_id, m.currency_code, m.unit, m.unit_quantity,
                   m.consumption_model_id
            FROM skus k JOIN price_models m USING (sku_id)
            WHERE lower(m.consumption_model_description) = 'default'
            ORDER BY k.sku_id
            """
        ):
            sku_id = row["sku_id"]
            if sku_id in used_skus:
                continue
            tiers = tiers_for(connection, sku_id, row["consumption_model_id"])
            try:
                _, price = tier_at(tiers, Decimal(0))
            except ValueError:
                continue
            with localcontext() as context:
                context.prec = 50
                base_rate = price / Decimal(row["unit_quantity"])
            key = (row["service_id"], row["currency_code"], row["unit"], row["unit_quantity"])
            comparison_groups[key].append((sku_id, base_rate))

        candidate_triples: list[tuple[tuple[str, str, str, str], list[tuple[str, Decimal]]]] = []
        for key, values in sorted(comparison_groups.items()):
            rng.shuffle(values)
            for offset in range(0, len(values) - 2, 3):
                triple = values[offset : offset + 3]
                if len({value for _, value in triple}) >= 2:
                    candidate_triples.append((key, triple))
        rng.shuffle(candidate_triples)
        selected_triples: list[tuple[tuple[str, str, str, str], list[tuple[str, Decimal]]]] = []
        reserved: set[str] = set()
        for key, triple in candidate_triples:
            sku_ids = {sku_id for sku_id, _ in triple}
            if reserved.isdisjoint(sku_ids):
                selected_triples.append((key, triple))
                reserved.update(sku_ids)
            if len(selected_triples) == 10:
                break
        if len(selected_triples) != 10:
            raise RuntimeError(f"Insufficient compatible comparison triples: {len(selected_triples)}")
        for index, (key, triple) in enumerate(selected_triples):
            _, currency, unit, _ = key
            ranked = sorted(triple, key=lambda item: (item[1], item[0]))
            sku_ids = [sku_id for sku_id, _ in triple]
            difference = ranked[-1][1] - ranked[0][1]
            add(
                "compatible_comparison",
                index,
                "Compare the compatible SKUs "
                + ", ".join(f"`{sku_id}`" for sku_id in sku_ids)
                + " using model `Default` at usage `0`. Rank normalized base-unit list rates. Return "
                "exactly `cheapest_sku_id`, `difference_per_base_unit` (highest minus lowest), "
                "`ranked_sku_ids` (ascending rate, then SKU ID), `currency`, and `unit`.",
                {
                    "cheapest_sku_id": ranked[0][0],
                    "difference_per_base_unit": decimal_text(difference),
                    "ranked_sku_ids": [sku_id for sku_id, _ in ranked],
                    "currency": currency,
                    "unit": unit,
                },
                sku_ids,
            )
    finally:
        connection.close()

    family_counts = Counter(question.family for question in questions)
    if len(questions) != 100 or family_counts != Counter({family: 10 for family in FAMILIES}):
        raise RuntimeError(f"Invalid question distribution: {dict(family_counts)}")
    split_skus: dict[str, set[str]] = defaultdict(set)
    for question in questions:
        split_skus[question.split].update(question.source_skus)
    if split_skus["train"] & split_skus["validation"]:
        raise RuntimeError("Train and validation SKU provenance overlaps")
    if split_skus["train"] & split_skus["holdout"]:
        raise RuntimeError("Train and holdout SKU provenance overlaps")
    if split_skus["validation"] & split_skus["holdout"]:
        raise RuntimeError("Validation and holdout SKU provenance overlaps")
    return questions


BENCHMARK_SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE questions (
  question_id TEXT PRIMARY KEY,
  family TEXT NOT NULL,
  split TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  prompt TEXT NOT NULL,
  expected_json TEXT NOT NULL,
  source_skus_json TEXT NOT NULL
) WITHOUT ROWID;
CREATE INDEX idx_questions_split ON questions(split, batch_id, family);
"""


def write_benchmark_database(
    processed_dir: Path, snapshot_id: str, questions: list[Question]
) -> Path:
    path = processed_dir / "benchmark.sqlite"
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.executescript(BENCHMARK_SCHEMA)
        with connection:
            metadata = {
                "dataset_id": DATASET_ID,
                "snapshot_id": snapshot_id,
                "seed": str(SEED),
                "question_count": str(len(questions)),
            }
            connection.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)", sorted(metadata.items())
            )
            connection.executemany(
                """
                INSERT INTO questions(
                  question_id, family, split, batch_id, prompt, expected_json, source_skus_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        question.question_id,
                        question.family,
                        question.split,
                        question.batch_id,
                        question.prompt,
                        json.dumps(question.answer, sort_keys=True, ensure_ascii=False),
                        json.dumps(question.source_skus, sort_keys=True),
                    )
                    for question in questions
                ],
            )
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Benchmark integrity check failed: {integrity}")
    finally:
        connection.close()
    return path


def safe_generated_root(path: Path, repository_root: Path) -> Path:
    resolved = path.resolve()
    expected_parent = (repository_root / "evaluations" / "runs").resolve()
    if resolved == expected_parent or expected_parent not in resolved.parents:
        raise ValueError(f"Generated task root must be below {expected_parent}: {resolved}")
    return resolved


def write_tasks(
    task_root: Path,
    repository_root: Path,
    catalog_database: Path,
    snapshot_id: str,
    questions: list[Question],
) -> dict[str, str]:
    task_root = safe_generated_root(task_root, repository_root)
    if task_root.exists():
        shutil.rmtree(task_root)
    verifier_source = Path(__file__).with_name("verify_task.py")
    instruction_hashes: dict[str, str] = {}
    batches: dict[tuple[str, str], list[Question]] = defaultdict(list)
    for question in questions:
        batches[(question.split, question.batch_id)].append(question)
    for (split, batch_id), batch in sorted(batches.items()):
        if len(batch) != 10 or {question.family for question in batch} != set(FAMILIES):
            raise RuntimeError(f"Batch {batch_id} does not contain one question per family")
        batch.sort(key=lambda question: FAMILIES.index(question.family))
        task_dir = task_root / split / batch_id
        environment_dir = task_dir / "environment"
        tests_dir = task_dir / "tests"
        environment_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(catalog_database, environment_dir / "catalog.sqlite")
        visible = {
            "schema_version": 1,
            "dataset_id": DATASET_ID,
            "snapshot_id": snapshot_id,
            "batch_id": batch_id,
            "questions": [
                {"id": question.question_id, "family": question.family, "prompt": question.prompt}
                for question in batch
            ],
        }
        expected = {
            "answers": [
                {"id": question.question_id, "answer": question.answer} for question in batch
            ]
        }
        write_json(environment_dir / "questions.json", visible)
        write_json(tests_dir / "expected.json", expected)
        shutil.copy2(verifier_source, tests_dir / "verify_task.py")
        (tests_dir / "test.sh").write_text(TEST_SH, encoding="utf-8", newline="\n")
        (task_dir / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
        (task_dir / "instruction.md").write_text(INSTRUCTION, encoding="utf-8", newline="\n")
        instruction_hashes[f"{split}/{batch_id}"] = hashlib.sha256(INSTRUCTION.encode("utf-8")).hexdigest()
    return instruction_hashes


def table_counts(database: Path) -> dict[str, int]:
    connection = sqlite3.connect(database)
    try:
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name != 'sqlite_stat1' ORDER BY name"
            )
        ]
        return {table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]) for table in tables}
    finally:
        connection.close()


def build_manifest(
    raw_manifest: dict[str, Any],
    catalog: Path,
    benchmark: Path,
    questions: list[Question],
    instruction_hashes: dict[str, str],
) -> dict[str, Any]:
    family_counts = Counter(question.family for question in questions)
    split_counts = Counter(question.split for question in questions)
    batch_counts = Counter((question.split, question.batch_id) for question in questions)
    question_contract_hash = hashlib.sha256(
        b"".join(
            json_bytes(
                {
                    "id": question.question_id,
                    "family": question.family,
                    "split": question.split,
                    "batch": question.batch_id,
                    "prompt": question.prompt,
                }
            )
            for question in sorted(questions, key=lambda item: item.question_id)
        )
    ).hexdigest()
    return {
        "schemaVersion": 1,
        "datasetId": DATASET_ID,
        "snapshotId": raw_manifest["snapshotId"],
        "retrievalCompletedAt": raw_manifest["retrievalCompletedAt"],
        "apiVersion": raw_manifest["apiVersion"],
        "currencyCode": raw_manifest["currencyCode"],
        "paginationComplete": raw_manifest["paginationComplete"],
        "rawSources": raw_manifest["sources"],
        "catalog": {
            "file": "catalog.sqlite",
            "sha256": sha256_file(catalog),
            "tables": table_counts(catalog),
        },
        "benchmark": {
            "file": "benchmark.sqlite",
            "sha256": sha256_file(benchmark),
            "questionCount": len(questions),
            "familyCounts": dict(sorted(family_counts.items())),
            "splitCounts": dict(sorted(split_counts.items())),
            "batchCounts": {
                split: len({batch for observed_split, batch in batch_counts if observed_split == split})
                for split in ("train", "validation", "holdout")
            },
            "questionContractSha256": question_contract_hash,
            "canonicalAnswersStoredInManifest": False,
            "seed": SEED,
        },
        "taskInstructionSha256": instruction_hashes,
    }


def verify_existing(dataset_root: Path, task_root: Path, repository_root: Path) -> dict[str, Any]:
    processed_dir = dataset_root / "processed"
    manifest_path = processed_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = processed_dir / "catalog.sqlite"
    benchmark = processed_dir / "benchmark.sqlite"
    findings: list[str] = []
    for path, expected_hash in (
        (catalog, manifest["catalog"]["sha256"]),
        (benchmark, manifest["benchmark"]["sha256"]),
    ):
        if not path.is_file():
            findings.append(f"missing:{path.name}")
        elif sha256_file(path) != expected_hash:
            findings.append(f"hash:{path.name}")
    if catalog.is_file():
        connection = sqlite3.connect(catalog)
        try:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                findings.append("integrity:catalog.sqlite")
        finally:
            connection.close()
    if benchmark.is_file():
        connection = sqlite3.connect(benchmark)
        connection.row_factory = sqlite3.Row
        try:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                findings.append("integrity:benchmark.sqlite")
            rows = list(connection.execute("SELECT family, split, batch_id FROM questions"))
            if len(rows) != 100:
                findings.append("question-count")
            if Counter(row["family"] for row in rows) != Counter({family: 10 for family in FAMILIES}):
                findings.append("family-distribution")
            if Counter(row["split"] for row in rows) != Counter(train=60, validation=20, holdout=20):
                findings.append("split-distribution")
        finally:
            connection.close()
    safe_task_root = safe_generated_root(task_root, repository_root)
    copied_catalog_hash = sha256_file(catalog) if catalog.is_file() else ""
    task_count = 0
    for split, expected_batches in (("train", 6), ("validation", 2), ("holdout", 2)):
        split_dir = safe_task_root / split
        batch_dirs = sorted(path for path in split_dir.glob("*") if path.is_dir()) if split_dir.is_dir() else []
        if len(batch_dirs) != expected_batches:
            findings.append(f"batches:{split}")
        for task_dir in batch_dirs:
            task_count += 1
            visible_path = task_dir / "environment" / "questions.json"
            task_catalog = task_dir / "environment" / "catalog.sqlite"
            expected_path = task_dir / "tests" / "expected.json"
            try:
                visible = json.loads(visible_path.read_text(encoding="utf-8"))
                expected = json.loads(expected_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                findings.append(f"task-json:{split}/{task_dir.name}")
                continue
            if "answer" in json.dumps(visible, sort_keys=True).casefold():
                findings.append(f"visible-answer-leak:{split}/{task_dir.name}")
            if len(visible.get("questions", [])) != 10 or len(expected.get("answers", [])) != 10:
                findings.append(f"task-question-count:{split}/{task_dir.name}")
            if not task_catalog.is_file() or sha256_file(task_catalog) != copied_catalog_hash:
                findings.append(f"task-catalog:{split}/{task_dir.name}")
    if task_count != 10:
        findings.append("task-count")
    result = {
        "ok": not findings,
        "datasetId": DATASET_ID,
        "snapshotId": manifest.get("snapshotId"),
        "taskCount": task_count,
        "questionCount": manifest.get("benchmark", {}).get("questionCount"),
        "findings": findings,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    repository_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=repository_root / "evaluations" / "datasets" / DATASET_ID,
    )
    parser.add_argument(
        "--task-root",
        type=Path,
        default=repository_root / "evaluations" / "runs" / f"{DATASET_ID}-tasks",
    )
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--page-size", type=int, default=5000)
    parser.add_argument("--gcloud", type=Path)
    parser.add_argument("--fetch-live", action="store_true")
    parser.add_argument("--verify-existing", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repository_root = Path(__file__).resolve().parents[2]
    dataset_root = args.dataset_root.resolve()
    task_root = args.task_root.resolve()
    if args.verify_existing:
        result = verify_existing(dataset_root, task_root, repository_root)
        return 0 if result["ok"] else 1
    raw_dir = dataset_root / "raw"
    processed_dir = dataset_root / "processed"
    if args.fetch_live:
        raw_manifest = fetch_snapshot(raw_dir, args.currency, args.page_size, args.gcloud)
    else:
        manifest_path = raw_dir / "manifest.json"
        if not manifest_path.is_file():
            raise SystemExit("No raw snapshot exists; run with --fetch-live")
        raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog, normalization_metrics = normalize_catalog(raw_dir, processed_dir, raw_manifest)
    questions = generate_questions(catalog)
    benchmark = write_benchmark_database(processed_dir, raw_manifest["snapshotId"], questions)
    instruction_hashes = write_tasks(
        task_root, repository_root, catalog, raw_manifest["snapshotId"], questions
    )
    manifest = build_manifest(raw_manifest, catalog, benchmark, questions, instruction_hashes)
    manifest["normalizationMetrics"] = normalization_metrics
    write_json(processed_dir / "manifest.json", manifest)
    result = verify_existing(dataset_root, task_root, repository_root)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
