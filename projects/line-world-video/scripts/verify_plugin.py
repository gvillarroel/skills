#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Validate portable schema and native Codex installation in a disposable home."""
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path
from jsonschema import Draft202012Validator

PROJECT = Path(__file__).resolve().parent.parent


def main():
    artifacts = PROJECT / "artifacts"
    version = json.loads((PROJECT / "package-spec.json").read_text())["version"]
    package = artifacts / "packages" / ("line-world-video-" + version)
    report_dir = artifacts / "host-checks" / ("release-" + version)
    report_dir.mkdir(parents=True, exist_ok=True)
    home = report_dir / ("codex-home-" + version)
    home.mkdir(exist_ok=True)
    env = {**os.environ, "CODEX_HOME": str(home)}
    schema_url = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    schema_bytes = urllib.request.urlopen(schema_url, timeout=30).read()
    (report_dir / "plugin.schema.json").write_bytes(schema_bytes)
    manifest = json.loads((package / "plugin/plugin.json").read_text())
    errors = [e.message for e in Draft202012Validator(json.loads(schema_bytes)).iter_errors(manifest)]
    commands = [["--version"], ["plugin", "marketplace", "add", str(package), "--json"], ["plugin", "list", "--available", "--marketplace", "line-world-local", "--json"], ["plugin", "add", "line-world-video@line-world-local", "--json"], ["plugin", "list", "--marketplace", "line-world-local", "--json"]]
    binary = shutil.which("codex.cmd") or shutil.which("codex")
    results = []
    for i, args in enumerate(commands):
        result = subprocess.run([binary, *args], cwd=package, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        (report_dir / f"command-{i}.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (report_dir / f"command-{i}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        results.append({"args": args, "exitCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            break
    installed = list(home.rglob("SKILL.md"))
    names = sorted({p.parent.name for p in installed})
    expected = sorted(json.loads((PROJECT/"package-spec.json").read_text())["skills"])
    report = {"ok": not errors and len(results) == len(commands) and all(r["exitCode"] == 0 for r in results) and names == expected, "schema": {"url": schema_url, "sha256": hashlib.sha256(schema_bytes).hexdigest(), "errors": errors}, "isolatedHome": str(home), "cachedSkillNames": names, "commands": results, "scope": "Native task-local catalog and installation check. No global host installation or desktop UI activation is claimed."}
    (report_dir / "plugin-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "schemaErrors": errors, "cachedSkillNames": names, "commandExits": [r["exitCode"] for r in results]}))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
