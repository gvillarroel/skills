#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the child-access gate and strict family preference order."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "artifacts" / "data"
OUTPUT = PROJECT / "artifacts" / "reviews" / "preference-ranking-validation.json"


def main() -> int:
    rows = json.loads((DATA / "ranked-places.json").read_text(encoding="utf-8"))
    all_rows = json.loads((DATA / "all-eligible-candidates.json").read_text(encoding="utf-8"))
    summary = json.loads((DATA / "category-summary.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["category_id"]].append(row)
        required = (
            "children_allowed",
            "child_access_level",
            "child_policy_basis",
            "cultural_priority_1_5",
            "international_experience_1_5",
            "affordability_1_5",
            "secondary_quality_1_5",
            "preference_key",
            "ranking_key",
        )
        missing = [field for field in required if row.get(field) in (None, "")]
        if missing:
            failures.append(f"{row['name']}: missing {', '.join(missing)}")
        if row.get("children_allowed") is not True:
            failures.append(f"{row['name']}: published without child access")
        for field in ("cultural_priority_1_5", "international_experience_1_5", "affordability_1_5", "secondary_quality_1_5"):
            value = float(row.get(field) or 0)
            if not 1 <= value <= 5:
                failures.append(f"{row['name']}: {field}={value} outside 1..5")

    summary_by_category = {row["category_id"]: row for row in summary}
    for category_id, category_rows in grouped.items():
        ordered = sorted(
            category_rows,
            key=lambda row: (
                -int(row["availability_priority"]),
                -float(row["cultural_priority_1_5"]),
                -float(row["international_experience_1_5"]),
                -float(row["affordability_1_5"]),
                -float(row["secondary_quality_1_5"]),
                float(row.get("distance_miles") if row.get("distance_miles") is not None else 9999),
                row["name"],
            ),
        )
        actual_ids = [row["id"] for row in sorted(category_rows, key=lambda row: int(row["rank"]))]
        expected_ids = [row["id"] for row in ordered]
        if actual_ids != expected_ids:
            failures.append(f"{category_id}: rows do not follow the strict preference order")
        expected_ranks = list(range(1, len(category_rows) + 1))
        actual_ranks = [int(row["rank"]) for row in sorted(category_rows, key=lambda row: int(row["rank"]))]
        if actual_ranks != expected_ranks:
            failures.append(f"{category_id}: ranks are not contiguous")
        pool = int(summary_by_category[category_id]["eligible_pool_size"])
        expected_count = min(50, pool) if pool >= 50 else math.ceil(pool * 0.5)
        if len(category_rows) != expected_count:
            failures.append(f"{category_id}: selected {len(category_rows)}, expected {expected_count}")

    false_positive_checks = [
        ("Indian Seats", "India"),
        ("Indian Mounds", "India"),
        ("Hindu Temple", "Jewish heritage"),
    ]
    for name_fragment, forbidden_tag in false_positive_checks:
        for row in all_rows:
            if name_fragment.lower() in row["name"].lower() and forbidden_tag in (row.get("nation_culture_tags") or []):
                failures.append(f"{row['name']}: false-positive tag {forbidden_tag}")
    for row in all_rows:
        if row["category_id"] == "shopping-markets-outlets" and "Cherokee Nation" in (row.get("nation_culture_tags") or []):
            failures.append(f"{row['name']}: shopping row incorrectly tagged Cherokee Nation")

    report = {
        "ok": not failures,
        "publishedRows": len(rows),
        "eligibleRows": len(all_rows),
        "categoryCounts": dict(Counter(row["category_id"] for row in rows)),
        "childrenAllowedRows": sum(1 for row in rows if row.get("children_allowed") is True),
        "conditionalChildAccessRows": sum(1 for row in rows if row.get("child_access_level") == "Children allowed with conditions"),
        "culturalRows": sum(1 for row in rows if float(row.get("cultural_priority_1_5") or 0) >= 4),
        "internationalRows": sum(1 for row in rows if float(row.get("international_experience_1_5") or 0) >= 4),
        "affordableRows": sum(1 for row in rows if float(row.get("affordability_1_5") or 0) >= 4),
        "failures": failures,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
