#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow==25.0.1"]
# ///
"""Download or convert Google Cloud Pricing API data to exact ZSTD Parquet."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Iterable, Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pyarrow as pa
import pyarrow.parquet as pq


API_ROOT = "https://cloudbilling.googleapis.com/v2beta"
DECIMAL_PRECISION = 38
DECIMAL_SCALE = 9
DECIMAL_TYPE = pa.decimal128(DECIMAL_PRECISION, DECIMAL_SCALE)
SCHEMA_VERSION = 1


def schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("snapshot_id", pa.string(), nullable=False),
            pa.field("retrieved_at", pa.timestamp("us", tz="UTC"), nullable=False),
            pa.field("api_version", pa.string(), nullable=False),
            pa.field("pagination_complete", pa.bool_(), nullable=False),
            pa.field("service_id", pa.string(), nullable=False),
            pa.field("service_name", pa.string(), nullable=False),
            pa.field("sku_id", pa.string(), nullable=False),
            pa.field("sku_name", pa.string(), nullable=False),
            pa.field("geo_type", pa.string(), nullable=False),
            pa.field(
                "regions",
                pa.list_(pa.field("element", pa.string())),
                nullable=False,
            ),
            pa.field(
                "product_taxonomy",
                pa.list_(pa.field("element", pa.string())),
                nullable=False,
            ),
            pa.field("price_resource_name", pa.string(), nullable=False),
            pa.field("consumption_model_id", pa.string(), nullable=False),
            pa.field("consumption_model_description", pa.string(), nullable=False),
            pa.field("currency_code", pa.string(), nullable=False),
            pa.field("unit", pa.string(), nullable=False),
            pa.field("unit_description", pa.string(), nullable=False),
            pa.field("unit_quantity", DECIMAL_TYPE, nullable=False),
            pa.field("aggregation_level", pa.string(), nullable=False),
            pa.field("aggregation_interval", pa.string(), nullable=False),
            pa.field("tier_position", pa.int32(), nullable=False),
            pa.field("tier_start", DECIMAL_TYPE, nullable=False),
            pa.field("list_price", DECIMAL_TYPE, nullable=False),
        ]
    )


def json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_rows(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON in {path} at line {line_number}") from error
            if not isinstance(row, dict):
                raise ValueError(f"Expected an object in {path} at line {line_number}")
            yield row


def resource_id(value: str) -> str:
    return value.rstrip("/").rsplit("/", 1)[-1] if value else ""


def exact_decimal(value: Any, label: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label} is not an exact decimal: {value!r}") from error
    if not number.is_finite():
        raise ValueError(f"{label} must be finite: {value!r}")
    number = Decimal(0) if number == 0 else number.normalize()
    exponent = number.as_tuple().exponent
    fractional_digits = max(0, -exponent)
    integer_digits = max(
        1,
        len(number.as_tuple().digits) + exponent
        if exponent >= 0
        else len(number.as_tuple().digits) - fractional_digits,
    )
    if fractional_digits > DECIMAL_SCALE or integer_digits > DECIMAL_PRECISION - DECIMAL_SCALE:
        raise ValueError(
            f"{label}={value!r} does not fit DECIMAL({DECIMAL_PRECISION},{DECIMAL_SCALE})"
        )
    return number


def money_decimal(money: dict[str, Any]) -> Decimal:
    units = exact_decimal(money.get("units", 0), "Money.units")
    nanos = exact_decimal(money.get("nanos", 0), "Money.nanos")
    value = units + nanos / Decimal(1_000_000_000)
    return exact_decimal(value, "Money value")


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
        for row in ((taxonomy.get("multiRegionalMetadata") or {}).get("regions") or []):
            if isinstance(row, dict) and row.get("region"):
                regions.add(str(row["region"]))
    return geo_type, sorted(regions)


def taxonomy_categories(sku: dict[str, Any]) -> list[str]:
    rows = ((sku.get("productTaxonomy") or {}).get("taxonomyCategories") or [])
    return [str(row["category"]) for row in rows if isinstance(row, dict) and row.get("category")]


def parse_retrieved_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_raw_manifest(raw_dir: Path, currency: str) -> dict[str, Any]:
    manifest_path = raw_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Raw snapshot manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Raw snapshot manifest must be a JSON object")
    required = {
        "apiVersion",
        "currencyCode",
        "paginationComplete",
        "retrievalCompletedAt",
        "snapshotId",
        "sources",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError(f"Raw snapshot manifest is missing: {', '.join(missing)}")
    if str(manifest["currencyCode"]).upper() != currency.upper():
        raise ValueError(
            f"Manifest currency {manifest['currencyCode']} does not match requested {currency}"
        )
    if manifest["paginationComplete"] is not True:
        raise ValueError("Refusing to export a snapshot with incomplete pagination")
    return manifest


def verify_raw_sources(raw_dir: Path, manifest: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    required_collections = {"services", "skus", "prices"}
    for source in manifest.get("sources") or []:
        if not isinstance(source, dict):
            raise ValueError("Raw manifest contains a non-object source")
        collection = str(source.get("collection", ""))
        file_name = str(source.get("file", ""))
        expected = str(source.get("sha256", ""))
        path = raw_dir / file_name
        if not collection or not file_name or not expected or not path.is_file():
            raise ValueError(f"Incomplete raw source entry for collection {collection!r}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {path.name}: expected {expected}, got {actual}")
        observed[collection] = actual
    missing = sorted(required_collections - set(observed))
    if missing:
        raise ValueError(f"Raw snapshot is missing collections: {', '.join(missing)}")
    return observed


def gcloud_access_token(executable: str | None, env_name: str) -> str:
    environment_token = os.environ.get(env_name, "").strip()
    if environment_token:
        return environment_token
    resolved = executable or shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not resolved:
        raise RuntimeError(
            f"No OAuth token in {env_name} and gcloud was not found; configure one without passing secrets on the command line"
        )
    completed = subprocess.run(
        [resolved, "auth", "print-access-token"],
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
    endpoint: str,
    collection_key: str,
    destination: Path,
    page_size: int,
    headers: dict[str, str],
    api_key: str,
    extra_parameters: dict[str, str] | None = None,
) -> dict[str, Any]:
    count = 0
    pages = 0
    page_token = ""
    with destination.open("wb") as output:
        while True:
            parameters = {"pageSize": str(page_size), **(extra_parameters or {})}
            if page_token:
                parameters["pageToken"] = page_token
            if api_key:
                parameters["key"] = api_key
            request = Request(
                f"{API_ROOT}/{endpoint}?{urlencode(parameters)}",
                headers=headers,
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
                        raise RuntimeError(
                            f"Pricing API request for {endpoint} failed with HTTP {error.code}"
                        ) from error
                except URLError as error:
                    if attempt == 5:
                        raise RuntimeError(
                            f"Pricing API request for {endpoint} failed after retries"
                        ) from error
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


def download_snapshot(
    destination: Path,
    currency: str,
    page_size: int,
    api_key_env: str,
    access_token_env: str,
    gcloud: str | None,
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    occupied = [path for path in destination.iterdir() if path.name != ".gitkeep"]
    if occupied:
        raise FileExistsError(
            f"Download directory is not empty: {destination}; use a new directory to preserve snapshot provenance"
        )
    api_key = os.environ.get(api_key_env, "").strip()
    headers = {
        "Accept": "application/json",
        "User-Agent": "google-cloud-sku-pricing-parquet/1",
    }
    auth_mode = "api-key"
    if not api_key:
        token = gcloud_access_token(gcloud, access_token_env)
        headers["Authorization"] = f"Bearer {token}"
        auth_mode = "oauth"
    started = datetime.now(timezone.utc).isoformat()
    sources = [
        fetch_collection(
            endpoint="services",
            collection_key="services",
            destination=destination / "services.jsonl",
            page_size=page_size,
            headers=headers,
            api_key=api_key,
        ),
        fetch_collection(
            endpoint="skus",
            collection_key="skus",
            destination=destination / "skus.jsonl",
            page_size=page_size,
            headers=headers,
            api_key=api_key,
        ),
        fetch_collection(
            endpoint="skus/-/prices",
            collection_key="prices",
            destination=destination / f"prices-{currency.casefold()}.jsonl",
            page_size=page_size,
            headers=headers,
            api_key=api_key,
            extra_parameters={"currencyCode": currency},
        ),
    ]
    digest = hashlib.sha256(
        "".join(source["sha256"] for source in sources).encode("ascii")
    ).hexdigest()
    manifest = {
        "schemaVersion": 1,
        "apiVersion": "v2beta",
        "currencyCode": currency,
        "pageSize": page_size,
        "retrievalStartedAt": started,
        "retrievalCompletedAt": datetime.now(timezone.utc).isoformat(),
        "paginationComplete": True,
        "snapshotId": f"gcp-pricing-{digest[:16]}",
        "authenticationMode": auth_mode,
        "sources": sources,
    }
    write_json(destination / "manifest.json", manifest)
    return manifest


def service_lookup(raw_dir: Path) -> dict[str, str]:
    services: dict[str, str] = {}
    for row in raw_rows(raw_dir / "services.jsonl"):
        service_id = str(row.get("serviceId") or resource_id(str(row.get("name", ""))))
        if service_id:
            services[service_id] = str(row.get("displayName") or service_id)
    return services


def sku_lookup(raw_dir: Path, services: dict[str, str]) -> dict[str, dict[str, Any]]:
    skus: dict[str, dict[str, Any]] = {}
    for row in raw_rows(raw_dir / "skus.jsonl"):
        sku_id = str(row.get("skuId") or resource_id(str(row.get("name", ""))))
        service_id = resource_id(str(row.get("service", "")))
        if not sku_id or service_id not in services:
            continue
        geo_type, regions = normalize_geo(row)
        skus[sku_id] = {
            "service_id": service_id,
            "service_name": services[service_id],
            "sku_name": str(row.get("displayName") or sku_id),
            "geo_type": geo_type,
            "regions": regions,
            "product_taxonomy": taxonomy_categories(row),
        }
    return skus


def price_rows(
    raw_dir: Path,
    manifest: dict[str, Any],
    skus: dict[str, dict[str, Any]],
    metrics: Counter[str],
) -> Iterator[dict[str, Any]]:
    currency = str(manifest["currencyCode"])
    retrieved_at = parse_retrieved_at(str(manifest["retrievalCompletedAt"]))
    prices_path = raw_dir / f"prices-{currency.casefold()}.jsonl"
    for price in raw_rows(prices_path):
        name = str(price.get("name", ""))
        parts = name.split("/")
        sku_id = parts[1] if len(parts) >= 3 and parts[0] == "skus" else ""
        sku = skus.get(sku_id)
        if sku is None:
            metrics["rejected_price_resources"] += 1
            continue
        metrics["price_resources"] += 1
        for model in price.get("skuPrices") or []:
            if not isinstance(model, dict) or str(model.get("valueType", "")).casefold() != "rate":
                metrics["rejected_non_rate_models"] += 1
                continue
            rate = model.get("rate") or {}
            unit_info = rate.get("unitInfo") or {}
            aggregation = rate.get("aggregationInfo") or {}
            model_id = resource_id(str(model.get("consumptionModel", "")))
            tiers = rate.get("tiers") or []
            unit = str(unit_info.get("unit", ""))
            unit_quantity = exact_decimal(
                ((unit_info.get("unitQuantity") or {}).get("value", "1")),
                "unit quantity",
            )
            if not model_id or not unit or not tiers or unit_quantity == 0:
                metrics["rejected_incomplete_models"] += 1
                continue
            inserted = 0
            for position, tier in enumerate(tiers):
                if not isinstance(tier, dict) or not isinstance(tier.get("listPrice"), dict):
                    metrics["rejected_incomplete_tiers"] += 1
                    continue
                money = tier["listPrice"]
                row_currency = str(money.get("currencyCode") or price.get("currencyCode") or currency)
                yield {
                    "snapshot_id": str(manifest["snapshotId"]),
                    "retrieved_at": retrieved_at,
                    "api_version": str(manifest["apiVersion"]),
                    "pagination_complete": True,
                    **sku,
                    "sku_id": sku_id,
                    "price_resource_name": name,
                    "consumption_model_id": model_id,
                    "consumption_model_description": str(
                        model.get("consumptionModelDescription") or model_id
                    ),
                    "currency_code": row_currency,
                    "unit": unit,
                    "unit_description": str(unit_info.get("unitDescription", "")),
                    "unit_quantity": unit_quantity,
                    "aggregation_level": str(aggregation.get("level", "")),
                    "aggregation_interval": str(aggregation.get("interval", "")),
                    "tier_position": position,
                    "tier_start": exact_decimal(
                        ((tier.get("startAmount") or {}).get("value", "0")),
                        "tier start",
                    ),
                    "list_price": money_decimal(money),
                }
                inserted += 1
                metrics["price_tiers"] += 1
            if inserted:
                metrics["price_models"] += 1


def batches(rows: Iterable[dict[str, Any]], batch_size: int) -> Iterator[list[dict[str, Any]]]:
    batch: list[dict[str, Any]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def export_parquet(
    raw_dir: Path,
    output: Path,
    manifest_output: Path,
    currency: str,
    compression_level: int,
    row_group_size: int,
    batch_size: int,
    overwrite: bool,
) -> dict[str, Any]:
    raw_dir = raw_dir.resolve()
    output = output.resolve()
    manifest_output = manifest_output.resolve()
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output}")
    if manifest_output.exists() and not overwrite:
        raise FileExistsError(f"Manifest output already exists: {manifest_output}")
    raw_manifest = load_raw_manifest(raw_dir, currency)
    verified_sources = verify_raw_sources(raw_dir, raw_manifest)
    services = service_lookup(raw_dir)
    skus = sku_lookup(raw_dir, services)
    if not services or not skus:
        raise ValueError("Raw snapshot did not contain usable services and SKUs")

    maximum_level = pa.Codec.maximum_compression_level("zstd")
    if compression_level < pa.Codec.minimum_compression_level("zstd") or compression_level > maximum_level:
        raise ValueError(
            f"ZSTD compression level must be between {pa.Codec.minimum_compression_level('zstd')} and {maximum_level}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".partial")
    if temporary.exists():
        temporary.unlink()
    metrics: Counter[str] = Counter()
    metadata = {
        b"google_cloud_pricing.schema_version": str(SCHEMA_VERSION).encode("ascii"),
        b"google_cloud_pricing.snapshot_id": str(raw_manifest["snapshotId"]).encode("utf-8"),
        b"google_cloud_pricing.retrieved_at": str(raw_manifest["retrievalCompletedAt"]).encode("utf-8"),
        b"google_cloud_pricing.api_version": str(raw_manifest["apiVersion"]).encode("utf-8"),
        b"google_cloud_pricing.currency_code": str(raw_manifest["currencyCode"]).encode("utf-8"),
        b"google_cloud_pricing.pagination_complete": b"true",
        b"google_cloud_pricing.source": b"Google Cloud Pricing API",
    }
    output_schema = schema().with_metadata(metadata)
    writer = pq.ParquetWriter(
        temporary,
        output_schema,
        version="2.6",
        compression="zstd",
        compression_level=compression_level,
        use_dictionary=True,
        write_statistics=True,
        data_page_version="2.0",
        write_page_index=True,
        use_compliant_nested_type=True,
    )
    try:
        for batch in batches(price_rows(raw_dir, raw_manifest, skus, metrics), batch_size):
            table = pa.Table.from_pylist(batch, schema=output_schema)
            writer.write_table(table, row_group_size=row_group_size)
    except Exception:
        writer.close()
        if temporary.exists():
            temporary.unlink()
        raise
    writer.close()
    if metrics["price_tiers"] == 0:
        temporary.unlink(missing_ok=True)
        raise ValueError("No price tiers were written")
    temporary.replace(output)

    parquet_file = pq.ParquetFile(output)
    if parquet_file.metadata.num_rows != metrics["price_tiers"]:
        raise RuntimeError("Parquet row count does not match normalized tier count")
    if not parquet_file.schema_arrow.equals(output_schema, check_metadata=True):
        raise RuntimeError("Parquet schema or metadata changed during write")
    output_digest = sha256_file(output)
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "artifactType": "google-cloud-pricing-api-tier-parquet",
        "source": {
            "apiVersion": raw_manifest["apiVersion"],
            "currencyCode": raw_manifest["currencyCode"],
            "paginationComplete": raw_manifest["paginationComplete"],
            "retrievalCompletedAt": raw_manifest["retrievalCompletedAt"],
            "snapshotId": raw_manifest["snapshotId"],
            "verifiedSourceSha256": verified_sources,
        },
        "normalization": {
            "services": len(services),
            "skus": len(skus),
            **dict(sorted(metrics.items())),
        },
        "parquet": {
            "file": output.name,
            "bytes": output.stat().st_size,
            "sha256": output_digest,
            "rows": parquet_file.metadata.num_rows,
            "rowGroups": parquet_file.metadata.num_row_groups,
            "compression": "ZSTD",
            "compressionLevel": compression_level,
            "zstdMaximumCompressionLevel": maximum_level,
            "decimalType": f"DECIMAL({DECIMAL_PRECISION},{DECIMAL_SCALE})",
            "schema": str(parquet_file.schema_arrow.remove_metadata()),
        },
    }
    write_json(manifest_output, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--raw-dir", type=Path, help="Complete Pricing API JSONL snapshot")
    source.add_argument(
        "--download-dir",
        type=Path,
        help="New empty directory in which to download a complete API snapshot",
    )
    parser.add_argument("--output", required=True, type=Path, help="Destination .parquet file")
    parser.add_argument("--manifest-output", type=Path, help="Destination artifact manifest JSON")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--page-size", type=int, default=5000)
    parser.add_argument("--api-key-env", default="GOOGLE_CLOUD_API_KEY")
    parser.add_argument("--access-token-env", default="GOOGLE_OAUTH_ACCESS_TOKEN")
    parser.add_argument("--gcloud", help="Optional gcloud executable path")
    parser.add_argument(
        "--compression-level",
        type=int,
        default=pa.Codec.maximum_compression_level("zstd"),
        help="ZSTD level; defaults to the maximum supported by bundled Arrow",
    )
    parser.add_argument("--row-group-size", type=int, default=65536)
    parser.add_argument("--batch-size", type=int, default=65536)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.page_size <= 0 or args.row_group_size <= 0 or args.batch_size <= 0:
            raise ValueError("Page, row-group, and batch sizes must be positive")
        currency = args.currency.upper()
        if args.download_dir is not None:
            raw_dir = args.download_dir.resolve()
            download_snapshot(
                raw_dir,
                currency,
                args.page_size,
                args.api_key_env,
                args.access_token_env,
                args.gcloud,
            )
        else:
            raw_dir = args.raw_dir.resolve()
        manifest_output = (
            args.manifest_output.resolve()
            if args.manifest_output
            else args.output.resolve().with_suffix(".manifest.json")
        )
        result = export_parquet(
            raw_dir,
            args.output,
            manifest_output,
            currency,
            args.compression_level,
            args.row_group_size,
            args.batch_size,
            args.overwrite,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
