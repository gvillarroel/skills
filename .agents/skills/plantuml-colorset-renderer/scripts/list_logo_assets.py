#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search the bundled normalized technical-logo manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", default="", help="Case-insensitive text matched against ID, title, and category")
    parser.add_argument("--provider", help="Exact provider name, such as AWS, GCP, Devicon, or Simple Icons")
    parser.add_argument("--category")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest_path = Path(__file__).resolve().parents[1] / "assets" / "logos" / "logo_manifest.json"
    logos = json.loads(manifest_path.read_text(encoding="utf-8"))["logos"]
    needle = args.search.casefold()
    category = (args.category or "").casefold()
    matches = []
    for item in logos:
        haystack = " ".join((item["id"], item["title"], item["category"])).casefold()
        if needle and needle not in haystack:
            continue
        if args.provider and item["provider"] != args.provider:
            continue
        if category and category not in item["category"].casefold():
            continue
        matches.append(
            {
                "id": item["id"],
                "title": item["title"],
                "provider": item["provider"],
                "category": item["category"],
                "path": f"assets/logos/{item['assetPath']}",
                "licenseId": item["licenseId"],
            }
        )
    matches = matches[: max(0, args.limit)]
    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        for item in matches:
            print(
                f"{item['id']}\t{item['provider']}\t{item['category']}\t{item['title']}\t{item['licenseId']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
