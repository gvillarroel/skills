#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Independently validate a portable desktop plugin against its published schemas."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

from jsonschema import Draft202012Validator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--complete", action="store_true", help="Also require packaged runtime and canonical skill files")
    args = parser.parse_args()
    plugin = args.plugin.resolve()
    output = args.output_dir.resolve()
    project = Path(__file__).resolve().parents[1]
    if not output.is_relative_to(project / "artifacts"):
        parser.error("Evidence must stay within this project's artifacts directory")
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    schema_records = []
    manifests = {}
    for name in ("plugin.json", "mcp.json"):
        data = json.loads((plugin / name).read_text(encoding="utf-8"))
        manifests[name] = data
        url = f"https://agent-plugins.org/schemas/1.0.0/{name.replace('.json', '.schema.json')}"
        with urlopen(url, timeout=25) as response:
            raw = response.read(1024 * 1024)
        schema = json.loads(raw)
        (output / name.replace(".json", ".schema.json")).write_bytes(raw)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: str(error.path))
        checks.append({"check": f"published-schema:{name}", "pass": not errors, "errors": [error.message for error in errors]})
        schema_records.append({"url": url, "sha256": hashlib.sha256(raw).hexdigest()})

    server = manifests["mcp.json"]["mcpServers"]["xy"]
    checks.extend([
        {"check": "local-stdio", "pass": server.get("type") == "stdio"},
        {"check": "plugin-relative-working-directory", "pass": server.get("cwd") == "./"},
        {"check": "stdio-desktop-flags", "pass": "--stdio" in server.get("args", []) and "--desktop" in server.get("args", [])},
        {"check": "canonical-root-skill", "pass": server.get("env", {}).get("XY_SKILL_DIR") == "skills/reflex-xy"},
        {"check": "no-literal-plugin-root", "pass": "${PLUGIN_ROOT}" not in json.dumps(server)},
        {"check": "local-executor-declared", "pass": manifests["plugin.json"].get("extensions", {}).get("com.openai", {}).get("requires_local_executor") is True},
    ])
    if args.complete:
        required = ["chatgpt/dist/server-bundled.js", "chatgpt/dist/widget.html", "chatgpt/dist/THIRD-PARTY-NOTICES.txt", "runtime/render.py", "runtime/presets.py", "runtime/capabilities.json", "skills/reflex-xy/SKILL.md", "skills/reflex-xy/references/interaction-design.md", ".codex-plugin/plugin.json", ".mcp.json"]
        checks.append({"check": "complete-runtime-files", "pass": all((plugin / name).is_file() for name in required), "missing": [name for name in required if not (plugin / name).is_file()]})
        bundle = json.loads((plugin / "bundle.json").read_text(encoding="utf-8"))
        mismatches = []
        for item in bundle["files"]:
            path = plugin / item["path"]
            if not path.resolve().is_relative_to(plugin) or not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                mismatches.append(item["path"])
        checks.append({"check": "release-inventory", "pass": not mismatches, "mismatches": mismatches})
        actual = {path.relative_to(plugin).as_posix() for path in plugin.rglob("*") if path.is_file()}
        expected = {item["path"] for item in bundle["files"]} | {"bundle.json"}
        checks.append({"check": "exact-package-file-set", "pass": actual == expected, "unexpected": sorted(actual - expected), "missing": sorted(expected - actual)})

    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "plugin": str(plugin), "schemas": schema_records, "checks": checks, "pass": all(check["pass"] for check in checks), "scope": "Manifest, launch declaration, and optional package identity only. This does not establish application installation or native inline painting."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pass": report["pass"], "checks": len(checks), "report": str(output / "report.json")}))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
