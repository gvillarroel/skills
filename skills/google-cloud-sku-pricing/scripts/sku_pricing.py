#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Query and calculate values from a normalized Google Cloud SKU catalog."""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any, Iterable


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def parse_decimal(value: str, label: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"{label} must be a decimal number: {value!r}") from error


def connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(f"Catalog database does not exist: {path}")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    required = {"metadata", "services", "skus", "sku_regions", "product_categories", "price_models", "price_tiers"}
    observed = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    missing = sorted(required - observed)
    if missing:
        connection.close()
        raise ValueError(f"Catalog database is missing tables: {', '.join(missing)}")
    return connection


def snapshot_metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return {
        row["key"]: row["value"]
        for row in connection.execute("SELECT key, value FROM metadata ORDER BY key")
    }


def resolve_model(
    connection: sqlite3.Connection,
    sku_id: str,
    model: str | None,
) -> sqlite3.Row:
    rows = list(
        connection.execute(
            """
            SELECT * FROM price_models
            WHERE sku_id = ?
            ORDER BY
              CASE WHEN lower(consumption_model_description) = 'default' THEN 0 ELSE 1 END,
              consumption_model_description,
              consumption_model_id
            """,
            (sku_id,),
        )
    )
    if not rows:
        raise ValueError(f"No public price models found for SKU {sku_id}")
    if model is None:
        return rows[0]
    folded = model.casefold()
    matches = [
        row
        for row in rows
        if row["consumption_model_id"].casefold() == folded
        or row["consumption_model_description"].casefold() == folded
    ]
    if len(matches) != 1:
        available = ", ".join(row["consumption_model_description"] for row in rows)
        raise ValueError(
            f"Consumption model {model!r} did not resolve uniquely for {sku_id}; "
            f"available: {available}"
        )
    return matches[0]


def tiers_for(
    connection: sqlite3.Connection,
    sku_id: str,
    model_id: str,
) -> list[tuple[Decimal, Decimal]]:
    rows = list(
        connection.execute(
            """
            SELECT start_amount, list_price
            FROM price_tiers
            WHERE sku_id = ? AND consumption_model_id = ?
            """,
            (sku_id, model_id),
        )
    )
    tiers = [
        (parse_decimal(row["start_amount"], "start_amount"), parse_decimal(row["list_price"], "list_price"))
        for row in rows
    ]
    tiers.sort(key=lambda item: item[0])
    if not tiers:
        raise ValueError(f"No tiers found for SKU {sku_id} and model {model_id}")
    return tiers


def applicable_tier(
    tiers: list[tuple[Decimal, Decimal]], usage: Decimal
) -> tuple[Decimal, Decimal]:
    eligible = [tier for tier in tiers if tier[0] <= usage]
    if not eligible:
        raise ValueError(
            f"Usage {decimal_text(usage)} precedes the first tier at "
            f"{decimal_text(tiers[0][0])}"
        )
    return eligible[-1]


def model_payload(model: sqlite3.Row) -> dict[str, str]:
    return {
        "consumption_model_id": model["consumption_model_id"],
        "consumption_model_description": model["consumption_model_description"],
        "currency": model["currency_code"],
        "unit": model["unit"],
        "unit_description": model["unit_description"],
        "pricing_unit_quantity": model["unit_quantity"],
        "aggregation_level": model["aggregation_level"],
        "aggregation_interval": model["aggregation_interval"],
    }


def describe(connection: sqlite3.Connection, sku_id: str) -> dict[str, Any]:
    sku = connection.execute(
        """
        SELECT skus.*, services.display_name AS service_name
        FROM skus JOIN services USING (service_id)
        WHERE sku_id = ?
        """,
        (sku_id,),
    ).fetchone()
    if sku is None:
        raise ValueError(f"Unknown SKU: {sku_id}")
    regions = [
        row["region"]
        for row in connection.execute(
            "SELECT region FROM sku_regions WHERE sku_id = ? ORDER BY region",
            (sku_id,),
        )
    ]
    categories = [
        row["category"]
        for row in connection.execute(
            "SELECT category FROM product_categories WHERE sku_id = ? ORDER BY position",
            (sku_id,),
        )
    ]
    models = [
        model_payload(row)
        for row in connection.execute(
            """
            SELECT * FROM price_models WHERE sku_id = ?
            ORDER BY consumption_model_description, consumption_model_id
            """,
            (sku_id,),
        )
    ]
    return {
        "sku_id": sku["sku_id"],
        "sku_description": sku["display_name"],
        "service_id": sku["service_id"],
        "service_name": sku["service_name"],
        "geo_type": sku["geo_type"],
        "regions": regions,
        "product_categories": categories,
        "models": models,
        "snapshot": snapshot_metadata(connection),
    }


def rate(
    connection: sqlite3.Connection,
    sku_id: str,
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    model = resolve_model(connection, sku_id, model_name)
    tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
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
    connection: sqlite3.Connection,
    sku_id: str,
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    if usage < 0:
        raise ValueError("usage must be non-negative")
    model = resolve_model(connection, sku_id, model_name)
    tiers = tiers_for(connection, sku_id, model["consumption_model_id"])
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
    connection: sqlite3.Connection,
    service: str | None,
    region: str | None,
    category: str | None,
) -> dict[str, Any]:
    clauses: list[str] = []
    parameters: list[str] = []
    if service:
        clauses.append("(lower(s.service_id) = lower(?) OR lower(s.display_name) = lower(?))")
        parameters.extend([service, service])
    if region:
        clauses.append(
            "EXISTS (SELECT 1 FROM sku_regions r WHERE r.sku_id = k.sku_id AND lower(r.region) = lower(?))"
        )
        parameters.append(region)
    if category:
        clauses.append(
            "EXISTS (SELECT 1 FROM product_categories c WHERE c.sku_id = k.sku_id AND lower(c.category) = lower(?))"
        )
        parameters.append(category)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    row = connection.execute(
        "SELECT COUNT(DISTINCT k.sku_id) AS value FROM skus k JOIN services s USING (service_id)" + where,
        parameters,
    ).fetchone()
    return {
        "count": int(row["value"]),
        "service": service,
        "region": region,
        "category": category,
        "snapshot": snapshot_metadata(connection),
    }


def compare(
    connection: sqlite3.Connection,
    sku_ids: Iterable[str],
    model_name: str | None,
    usage: Decimal,
) -> dict[str, Any]:
    rows = [rate(connection, sku_id, model_name, usage) for sku_id in sku_ids]
    if len(rows) < 2:
        raise ValueError("compare requires at least two SKU IDs")
    compatibility = {
        (row["currency"], row["unit"], row["pricing_unit_quantity"], row["consumption_model_description"])
        for row in rows
    }
    if len(compatibility) != 1:
        raise ValueError("Compared SKUs do not share currency, unit, quantity, and consumption model")
    ranked = sorted(
        rows,
        key=lambda row: (parse_decimal(row["price_per_base_unit"], "price_per_base_unit"), row["sku_id"]),
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
    parser.add_argument("--db", required=True, type=Path, help="Normalized catalog SQLite database")
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

    count_parser = subparsers.add_parser("count", help="Count distinct SKUs matching catalog filters")
    count_parser.add_argument("--service")
    count_parser.add_argument("--region")
    count_parser.add_argument("--category")

    compare_parser = subparsers.add_parser("compare", help="Compare compatible marginal SKU rates")
    compare_parser.add_argument("--sku-id", action="append", required=True)
    compare_parser.add_argument("--model")
    compare_parser.add_argument("--usage", required=True)

    cheapest_parser = subparsers.add_parser("cheapest", help="Alias for compare with an explicit cheapest result")
    cheapest_parser.add_argument("--sku-id", action="append", required=True)
    cheapest_parser.add_argument("--model")
    cheapest_parser.add_argument("--usage", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        connection = connect(args.db.resolve())
        with connection:
            if args.command == "describe":
                payload = describe(connection, args.sku_id)
            elif args.command == "rate":
                payload = rate(connection, args.sku_id, args.model, parse_decimal(args.usage, "usage"))
            elif args.command == "cost":
                payload = progressive_cost(connection, args.sku_id, args.model, parse_decimal(args.usage, "usage"))
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
    except (FileNotFoundError, ValueError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

