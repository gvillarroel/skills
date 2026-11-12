#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch the two primary-source inputs pinned for this local interface study."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json", "gemini-catalog.json", "ec9da1b6f2d2fd375d1df902e3fd52f95b5e8be0c16c86db172f8f251f4c7218"),
    ("https://vega.github.io/schema/vega-lite/v5.json", "vega-lite-v5.schema.json", "1aeeda8aa44dcce60f6b6fb7d8b650487e3e389a8284a2040e590be9a4c7610e"),
]


def main():
    output = ROOT / "artifacts/data"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for url, name, expected in SOURCES:
        target = output / name
        if target.is_file():
            raw = target.read_bytes()
        else:
            with urlopen(url, timeout=30) as response:
                raw = response.read(8_000_001)
            if len(raw) > 8_000_000:
                raise ValueError("Source exceeds this study's bounded download profile.")
        json.loads(raw)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise ValueError(f"Primary-source digest changed for {name}; review the new source before updating this study's pin.")
        target.write_bytes(raw)
        records.append({"url": url, "file": name, "sha256": digest, "bytes": len(raw)})
    (output / "schema-sources.json").write_text(json.dumps({"verifiedAtUtc": datetime.now(timezone.utc).isoformat(), "sources": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "sources": len(records), "scope": "Pinned source bytes only; no host acceptance claim."}))


if __name__ == "__main__":
    main()
