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

from logo_svg import VARIANTS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", default="", help="Case-insensitive text matched against ID, title, and category")
    parser.add_argument("--provider", help="Exact provider name, such as AWS, GCP, Devicon, Simple Icons, Font Awesome Brands, or Ollama")
    parser.add_argument("--category")
    parser.add_argument("--id", help="Exact stable logo ID; no fuzzy substitution")
    parser.add_argument("--variant", choices=VARIANTS, default="color")
    parser.add_argument("--available-only", action="store_true", help="Hide records where the requested variant is unavailable")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest_path = Path(__file__).resolve().parents[1] / "assets" / "logos" / "logo_manifest.json"
    logos = json.loads(manifest_path.read_text(encoding="utf-8"))["logos"]
    variants = {item["id"]: item for item in json.loads((manifest_path.parent / "logo_variants.json").read_text(encoding="utf-8"))["logos"]}
    if args.id and args.id not in variants:
        parser.error(f"Unknown exact logo ID: {args.id}")
    needle = args.search.casefold()
    category = (args.category or "").casefold()
    matches = []
    for item in logos:
        if args.id and item["id"] != args.id:
            continue
        haystack = " ".join((item["id"], item["title"], item["category"])).casefold()
        if needle and needle not in haystack:
            continue
        if args.provider and item["provider"] != args.provider:
            continue
        if category and category not in item["category"].casefold():
            continue
        selection = variants[item["id"]]
        selected = selection["variants"].get(args.variant)
        if args.available_only and selected is None:
            continue
        matches.append(
            {
                "id": item["id"],
                "title": item["title"],
                "provider": item["provider"],
                "category": item["category"],
                "variant": args.variant,
                "available": selected is not None,
                "path": f"assets/logos/{selected['assetPath']}" if selected else None,
                "licenseId": selected["licenseId"] if selected else item["licenseId"],
                "paletteKind": selected["paletteKind"] if selected else None,
                "recolorable": bool(selected and selected["recolorable"]),
                "availableVariants": list(selection["variants"]),
                "unavailableVariants": selection["unavailable"],
                "reason": None if selected else selection["unavailable"].get(args.variant),
                "artworkStatus": item.get("artworkStatus", "pinned-source-artwork"),
            }
        )
    matches = matches[: max(0, args.limit)]
    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        for item in matches:
            print(
                f"{item['id']}\t{item['variant']}\t{item['licenseId']}\t{item['path'] or 'UNAVAILABLE: ' + str(item['reason'])}\tavailable={','.join(item['availableVariants'])}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
