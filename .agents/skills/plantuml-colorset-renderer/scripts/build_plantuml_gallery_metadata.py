#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
from pathlib import Path

from plantuml_coverage import DEFAULT_MANIFEST, build_gallery_metadata, load_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic PlantUML gallery coverage metadata.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--colorset", choices=["colorset1", "colorset2"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    metadata = build_gallery_metadata(load_manifest(args.manifest), args.colorset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "itemCount": metadata["itemCount"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
