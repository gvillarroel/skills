#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check package-evaluator acceptance/rejection with tiny independent archives."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = root / "projects/desktop-plugin-ui/artifacts/plugin-pocs/package-verifier-selftests" / args.run_id
    if not output.resolve().is_relative_to(root):
        parser.error("Unsafe output path")
    output.mkdir(parents=True, exist_ok=False)
    plugin = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "name": "evaluator-fixture", "version": "1.0.0"}
    config = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": {"fixture": {"type": "stdio", "command": "node", "args": ["${PLUGIN_ROOT}/dist/server.js"], "cwd": "${PLUGIN_ROOT}"}}}
    manifest = {"manifest_version": "0.3", "name": "evaluator-fixture", "version": "1.0.0", "description": "Package evaluator fixture", "author": {"name": "Evaluation"}, "server": {"type": "node", "entry_point": "dist/server.js", "mcp_config": {"command": "node", "args": ["${__dirname}/dist/server.js"]}}}
    cases = []

    def run(name: str, kind: str, entries: dict[str, object], expected: bool) -> None:
        fixture = output / name
        fixture.mkdir()
        archive = fixture / "fixture.zip"
        with zipfile.ZipFile(archive, "w") as package:
            for member, data in entries.items():
                package.writestr(member, json.dumps(data) if not isinstance(data, str) else data)
        command = ["uv", "run", "--script", str(root / "projects/desktop-plugin-ui/scripts/inspect-mcp-poc-package.py"), "--poc", str(fixture), "--kind", kind, "--archive", str(archive), "--output", str(fixture / "review")]
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=240)
        report_path = fixture / "review/package-review.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
        actual = result.returncode == 0 and report.get("passed") is True
        cases.append({"name": name, "passed": actual == expected and bool(report), "expected_acceptance": expected, "actual_acceptance": actual, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})

    run("valid-portable", "portable", {"plugin.json": plugin, "mcp.json": config, "dist/server.js": "// fixture\n"}, True)
    invalid = json.loads(json.dumps(config))
    del invalid["mcpServers"]["fixture"]["type"]
    run("missing-portable-transport", "portable", {"plugin.json": plugin, "mcp.json": invalid, "dist/server.js": "// fixture\n"}, False)
    run("unsafe-archive-path", "portable", {"../escape.txt": "must not extract", "plugin.json": plugin, "mcp.json": config}, False)
    run("valid-mcpb", "claude-desktop", {"manifest.json": manifest, "dist/server.js": "// fixture\n"}, True)
    escape_files = list(output.rglob("escape.txt"))
    cases.append({"name": "unsafe-member-never-extracted", "passed": not escape_files, "actual": [str(path) for path in escape_files]})
    report = {"passed": all(item["passed"] for item in cases), "checks": cases, "scope": "Independent package evaluator selftests; not runtime plugin acceptance."}
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(cases), "failed": [item["name"] for item in cases if not item["passed"]], "output": str(output / "result.json")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
