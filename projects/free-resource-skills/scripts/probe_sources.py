#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Capture bounded public metadata for the five source integrations."""
import concurrent.futures
import json
from pathlib import Path
from urllib.request import Request, urlopen

TARGETS = {
    "polyhaven-schema.json": "https://api.polyhaven.com/api-docs/swagger.json",
    "polyhaven-assets.json": "https://api.polyhaven.com/assets?t=textures",
    "polyhaven-files.json": "https://api.polyhaven.com/files/wood_floor_deck",
    "ambient-docs.html": "https://docs.ambientcg.com/api/v3/",
    "ambient-search.json": "https://ambientcg.com/api/v2/full_json?q=wood&limit=3&include=downloadData",
    "iconify-search.json": "https://api.iconify.design/search?query=home&prefix=lucide&limit=5",
    "iconify-collection.json": "https://api.iconify.design/collection?prefix=lucide&info=1",
    "kenney-search.html": "https://kenney.nl/assets?q=pattern",
    "kenney-pack.html": "https://kenney.nl/assets/pattern-pack",
}

def capture(pair):
    name, url = pair
    dest = Path("projects/free-resource-skills/artifacts/data") / name
    try:
        with urlopen(Request(url, headers={"User-Agent": "FreeResourceSkillsResearch/1.0"}), timeout=35) as r:
            raw = r.read(15_000_000)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        value = json.loads(raw) if name.endswith(".json") else None
        return {"name": name, "bytes": len(raw), "keys": list(value)[:12] if isinstance(value, dict) else None}
    except Exception as exc:
        return {"name": name, "error": str(exc)}

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(capture, TARGETS.items()):
            print(json.dumps(result))
