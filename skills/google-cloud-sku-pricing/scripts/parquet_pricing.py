#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==1.4.4", "pytz==2025.2"]
# ///
"""Query and calculate exact values from a Google Cloud pricing Parquet file."""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path
import sys
from typing import Any, Iterable

import duckdb


REQUIRED_COLUMNS = {
    "snapshot_id",
    "retrieved_at",
    "api_version",
    "pagination_complete",
    "service_id",
    "service_name",
    "sku_id",
    "sku_name",
    "geo_type",
    "regions",
    "product_taxonomy",
    "consumption_model_id",
    "consumption_model_description",
    "currency_code",
    "unit",
    "unit_description",
    "unit_quantity",
    "aggregation_level",
    "aggregation_interval",
    "tier_position",
    "tier_start",
    "list_price",
}


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def parse_decimal(value: Any, label: str) -> Decimal:
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{label} must be a decimal number: {value!r}") from error
    if not parsed.is_finite():
        raise ValueError(f"{label} must be finite: {value!r}")
    return parsed


def connect(path: Path) -> duckdb.DuckDBPyConnection:
    if not path.is_file():
        raise FileNotFoundError(f"Pricing Parquet file does not exist: {path}")
    connection = duckdb.connect(":memory:")
    try:
        connection.execute("SET TimeZone = 'UTC'")
        connection.read_parquet(str(path)).create_view("pricing")
        observed = {str(row[0]) for row in connection.execute("DESCRIBE pricing").fetchall()}
        missing = sorted(REQUIRED_COLUMNS - observed)
        if missing:
            raise ValueError(f"Pricing Parquet is missing columns: {', '.join(missing)}")
        row = connection.execute(
            "SELECT pagination_complete FROM pricing LIMIT 1"
        ).fetchone()
        if row is None:
            raise ValueError("Pricing Parquet contains no rows")
        if row[0] is not True:
            raise ValueError("Refusing to query a Parquet snapshot with incomplete pagination")
        return connection
    except Exception:
        connection.close()
        raise


def rows_as_dicts(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    columns = [str(item[0]) for item in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def row_as_dict(cursor: duckdb.DuckDBPyConnection) -> dict[str, Any] | None:
    rows = rows_as_dicts(cursor)
    return rows[0] if rows else None


def snapshot_metadata(connection: duckdb.DuckDBPyConnection) -> dict[str, str]:
    row = row_as_dict(
        connection.execute(
            """
            SELECT snapshot_id, retrieved_at, api_version, currency_code,
                   pagination_complete
            FROM pricing
            LIMIT 1
            """
        )
    )
    assert row is not None
    retrieved = row["retrieved_at"]
    return {
        "snapshot_id": str(row["snapshot_id"]),
        "retrieved_at": retrieved.isoformat() if hasattr(retrieved, "isoformat") else str(retrieved),
        "api_version": str(row["api_version"]),
        "currency_code": str(row["currency_code"]),
        "pagination_complete": "true" if row["pagination_complete"] else "false",
        "source_format": "parquet",
    }


def models_for(connection: duckdb.DuckDBPyConnection, sku_id: str) -> list[dict[str, Any]]:
    return rows_as_dicts(
        connection.execute(
            """
            SELECT DISTINCT
              consumption_model_id,
              consumption_model_description,
              currency_code,
              unit,
              unit_description,
              unit_quantity,
              aggregation_level,
              aggregation_interval
            FROM pricing
            WHERE sku_id = ?
            ORDER BY consumption_model_description, consumption_model_id
            """,
            [sku_id],
        )
    )


def resolve_model(
    connection: duckdb.DuckDBPyConnection,
    sku_id: str,
    model: str | None,
) -> dict[str, Any]:
    rows = models_for(connection, sku_id)
    if not rows:
        raise ValueError(f"No public price models found for SKU {sku_id}")
    if model is None:
        defaults = [
            row
            for row in rows
            if str(row["consumption_model_description"]).casefold() == "default"
        ]
        return defaults[0] if defaults else rows[0]
    folded = model.casefold()
    matches = [
        row
        for row in rows
        if str(row["consumption_model_id"]).casefold() == folded
        or str(row["consumption_model_description"]).casefold() == folded
    ]
    if len(matches) != 1:
        available = ", ".join(str(row["consumption_model_description"]) for row in rows)
        raise ValueError(
            f"Consumption model {model!r} did not resolve uniquely for {sku_id}; available: {available}"
        )
    return matches[0]


def tiers_for(
    connection: duckdb.DuckDBPyConnection,
    sku_id: str,
    model_id: str,
) -> list[tuple[Decimal, Decimal]]:
    rows = connection.execute(
        """
        SELECT tier_start, list_price
        FROM pricing
        WHERE sku_id = ? AND consumption_model_id = ?
        ORDER BY tier_start, tier_position
        """,
        [sku_id, model_id],
    ).fetchall()
    tiers = [
        (parse_decimal(row[0], "tier_start"), parse_decimal(row[1], "list_price"))
        for row in rows
    ]
    if not tiers:
        raise ValueError(f"No tiers found for SKU {sku_id} and model {model_id}")
    return tiers


def applicable_tier(
    tiers: list[tuple[Decimal, Decimal]], usage: Decimal
) -> tuple[Decimal, Decimal]:
    eligible = [tier for tier in tiers if tier[0] <= usage]
    if not eligible:
        raise ValueError(
            f"Usage {decimal_text(usage)} precedes the first tier at {decimal_text(tiers[0][0])}"
        )
    return eligible[-1]


def model_payload(model: dict[str, Any]) -> dict[str, str]:
    return {
        "consumption_model_id": str(model["consumption_model_id"]),
        "consumption_model_description": str(model["consumption_model_description"]),
        "currency": str(model["currency_code"]),
        "unit": str(model["unit"]),
        "unit_description": str(model["unit_description"]),
        "pricing_unit_quantity": decimal_text(
            parse_decimal(model["unit_quantity"], "unit_quantity")
        ),
        "aggregation_level": str(model["aggregation_level"]),
        "aggregation_interval": str(model["aggregation_interval"]),
    }


def describe(connection: duckdb.DuckDBPyConnection, sku_id: str) -> dict[str, Any]:
    sku = row_as_dict(
        connection.execute(
            """
            SELECT sku_id, sku_name, service_id, service_name, geo_type,
                   regions, product_taxonomy
            FROM pricing
            WHERE sku_id = ?
            LIMIT 1
            """,
            [sku_id],
        )
    )
    if sku is None:
        raise ValueError(f"Unknown SKU: {sku_id}")
    models = [model_payload(row) for row in models_for(connection, sku_id)]
    return {
        "sku_id": str(sku["sku_id"]),
        "sku_description": str(sku["sku_name"]),
        "service_id": str(sku["service_id"]),
        "service_name": str(sku["service_name"]),
        "geo_type": str(sku["geo_type"]),
        "regions": list(sku["regions"] or []),
        "product_categories": list(sku["product_taxonomy"] or []),
        "models": models,
        "snapshot": snapshot_metadata(connection),
    }


def rate(
    connection: duckdb.DuckDBPyConnection,
    sku_id: str,
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    model = resolve_model(connection, sku_id, model_name)
    tiers = tiers_for(connection, sku_id, str(model["consumption_model_id"]))
    start, price = applicable_tier(tiers, usage)
    unit_quantity = parse_decimal(model["unit_quantity"], "unit_quantity")
    with localcontext() as context:
        context.prec = 50
        normalized = price / unit_quantity
    return {
        "sku_id": sku_id,
        **model_payload(model),
        "usage": decimal_text(usage),
        "tier_start": decimal_text(start),
        "price_per_pricing_unit": decimal_text(price),
        "price_per_base_unit": decimal_text(normalized),
        "snapshot": snapshot_metadata(connection),
    }


def progressive_cost(
    connection: duckdb.DuckDBPyConnection,
    sku_id: str,
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    if usage < 0:
        raise ValueError("usage must be non-negative")
    model = resolve_model(connection, sku_id, model_name)
    tiers = tiers_for(connection, sku_id, str(model["consumption_model_id"]))
    unit_quantity = parse_decimal(model["unit_quantity"], "unit_quantity")
    components: list[dict[str, str]] = []
    total = Decimal(0)
    with localcontext() as context:
        context.prec = 50
        for index, (start, price) in enumerate(tiers):
            if usage <= start:
                break
            next_start = tiers[index + 1][0] if index + 1 < len(tiers) else usage
            quantity = min(usage, next_start) - start
            if quantity <= 0:
                continue
            component_cost = quantity / unit_quantity * price
            total += component_cost
            components.append(
                {
                    "tier_start": decimal_text(start),
                    "quantity": decimal_text(quantity),
                    "price_per_pricing_unit": decimal_text(price),
                    "cost": decimal_text(component_cost),
                }
            )
    return {
        "sku_id": sku_id,
        **model_payload(model),
        "usage": decimal_text(usage),
        "total_cost": decimal_text(total),
        "components": components,
        "snapshot": snapshot_metadata(connection),
    }


def count_skus(
    connection: duckdb.DuckDBPyConnection,
    service: str | None,
    region: str | None,
    category: str | None,
) -> dict[str, Any]:
    clauses: list[str] = []
    parameters: list[str] = []
    if service:
        clauses.append("(lower(service_id) = lower(?) OR lower(service_name) = lower(?))")
        parameters.extend([service, service])
    if region:
        clauses.append(
            "EXISTS (SELECT 1 FROM UNNEST(regions) AS r(value) WHERE lower(value) = lower(?))"
        )
        parameters.append(region)
    if category:
        clauses.append(
            "EXISTS (SELECT 1 FROM UNNEST(product_taxonomy) AS c(value) WHERE lower(value) = lower(?))"
        )
        parameters.append(category)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    row = connection.execute(
        "SELECT COUNT(DISTINCT sku_id) FROM pricing" + where,
        parameters,
    ).fetchone()
    assert row is not None
    return {
        "count": int(row[0]),
        "service": service,
        "region": region,
        "category": category,
        "snapshot": snapshot_metadata(connection),
    }


def compare(
    connection: duckdb.DuckDBPyConnection,
    sku_ids: Iterable[str],
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    rows = [rate(connection, sku_id, model_name, usage) for sku_id in sku_ids]
    if len(rows) < 2:
        raise ValueError("compare requires at least two SKU IDs")
    compatibility = {
        (
            row["currency"],
            row["unit"],
            row["pricing_unit_quantity"],
            row["consumption_model_description"],
        )
        for row in rows
    }
    if len(compatibility) != 1:
        raise ValueError(
            "Compared SKUs do not share currency, unit, quantity, and consumption model"
        )
    ranked = sorted(
        rows,
        key=lambda row: (
            parse_decimal(row["price_per_base_unit"], "price_per_base_unit"),
            row["sku_id"],
        ),
    )
    low = parse_decimal(ranked[0]["price_per_base_unit"], "price_per_base_unit")
    high = parse_decimal(ranked[-1]["price_per_base_unit"], "price_per_base_unit")
    return {
        "usage": decimal_text(usage),
        "cheapest_sku_id": ranked[0]["sku_id"],
        "difference_per_base_unit": decimal_text(high - low),
        "ranked": [
            {
                "sku_id": row["sku_id"],
                "tier_start": row["tier_start"],
                "price_per_base_unit": row["price_per_base_unit"],
            }
            for row in ranked
        ],
        "currency": rows[0]["currency"],
        "unit": rows[0]["unit"],
        "snapshot": snapshot_metadata(connection),
    }


def output(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", required=True, type=Path, help="Pricing tier Parquet file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    describe_parser = subparsers.add_parser("describe", help="Describe one SKU")
    describe_parser.add_argument("--sku-id", required=True)

    rate_parser = subparsers.add_parser("rate", help="Return the marginal tier rate at a usage amount")
    rate_parser.add_argument("--sku-id", required=True)
    rate_parser.add_argument("--model")
    rate_parser.add_argument("--usage", required=True)

    cost_parser = subparsers.add_parser("cost", help="Calculate a progressive tiered cost")
    cost_parser.add_argument("--sku-id", required=True)
    cost_parser.add_argument("--model")
    cost_parser.add_argument("--usage", required=True)

    count_parser = subparsers.add_parser("count", help="Count distinct priced SKUs matching filters")
    count_parser.add_argument("--service")
    count_parser.add_argument("--region")
    count_parser.add_argument("--category")

    compare_parser = subparsers.add_parser("compare", help="Compare compatible marginal SKU rates")
    compare_parser.add_argument("--sku-id", action="append", required=True)
    compare_parser.add_argument("--model")
    compare_parser.add_argument("--usage", required=True)

    cheapest_parser = subparsers.add_parser("cheapest", help="Alias for compare with a cheapest result")
    cheapest_parser.add_argument("--sku-id", action="append", required=True)
    cheapest_parser.add_argument("--model")
    cheapest_parser.add_argument("--usage", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    connection: duckdb.DuckDBPyConnection | None = None
    try:
        connection = connect(args.parquet.resolve())
        if args.command == "describe":
            payload = describe(connection, args.sku_id)
        elif args.command == "rate":
            payload = rate(
                connection,
                args.sku_id,
                args.model,
                parse_decimal(args.usage, "usage"),
            )
        elif args.command == "cost":
            payload = progressive_cost(
                connection,
                args.sku_id,
                args.model,
                parse_decimal(args.usage, "usage"),
            )
        elif args.command == "count":
            payload = count_skus(connection, args.service, args.region, args.category)
        else:
            payload = compare(
                connection,
                args.sku_id,
                args.model,
                parse_decimal(args.usage, "usage"),
            )
        output(payload)
        return 0
    except (FileNotFoundError, ValueError, duckdb.Error) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    sys.exit(main())
