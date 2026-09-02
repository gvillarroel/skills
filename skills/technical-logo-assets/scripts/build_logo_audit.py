#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline browser contact sheet and exhaustive SVG paint/color audit."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from sync_normalized_logos import asset_directory, safe_asset_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Output HTML outside the skill bundle")
    parser.add_argument("--id", action="append", default=[], help="Representative stable ID; repeat to customize the contact sheet")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = args.output.resolve()
    if target.is_relative_to(root) or target.suffix.lower() != ".html":
        parser.error("Write an .html audit outside the read-only skill bundle")
    assets = asset_directory()
    manifest = json.loads((assets / "logo_manifest.json").read_text(encoding="utf-8"))
    catalog = json.loads((assets / "logo_variants.json").read_text(encoding="utf-8"))
    items = {item["id"]: item for item in manifest["logos"]}
    representatives = args.id or ["aws-compute-lambda", "gcp-compute-cloud-run", "devicon-python", "devicon-kubernetes",
        "devicon-docker", "code-assistant-opencode", "code-assistant-gemini-cli", "code-assistant-aider",
        "code-assistant-cline", "ai-provider-openai", "ai-provider-deepseek", "simpleicons-angular"]
    if set(representatives) - set(items):
        parser.error("Unknown representative logo ID")
    records = []
    for row in catalog["logos"]:
        item = items[row["id"]]
        for kind, variant in row["variants"].items():
            payload = safe_asset_path(assets, variant["assetPath"]).read_bytes()
            records.append({"id": row["id"], "variant": kind, "title": item["title"], "license": variant["licenseId"],
                            "svg": base64.b64encode(payload).decode("ascii")})
    data = {"records": records, "representatives": representatives, "kinds": catalog["variantKinds"],
            "coverage": catalog["coverage"], "availability": {row["id"]: row["unavailable"] for row in catalog["logos"] if row["id"] in representatives}}
    template = (root / "assets/logo-audit.html").read_text(encoding="utf-8")
    payload = template.replace("__LOGO_AUDIT_DATA__", json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "html": str(target), "selectableSvgCount": len(records), "contactSheetRows": len(representatives)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
