#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Independently extract and inspect a generated Desktop MCP PoC archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
from urllib.request import urlopen
import zipfile

from jsonschema import Draft202012Validator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--poc", type=Path, required=True)
    parser.add_argument("--kind", choices=("claude-desktop", "chatgpt-desktop", "portable"), required=True)
    parser.add_argument("--archive", type=Path, help="Override the host-specific default archive path for another portable package")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mcpb-version", default="2.1.2")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    if not output.is_relative_to(root / "projects/desktop-plugin-ui/artifacts"):
        parser.error("Evaluator output must remain inside the owning project's artifacts")
    output.mkdir(parents=True, exist_ok=False)
    checks: list[dict] = []

    def check(name: str, passed: bool, **detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), **detail})

    archive = args.archive.resolve() if args.archive else args.poc.resolve() / "releases" / ("queue-review.mcpb" if args.kind == "claude-desktop" else "queue-review-chatgpt.zip")
    extracted = output / "extracted"
    extracted.mkdir()
    inventory = []
    try:
        with zipfile.ZipFile(archive) as package:
            entries = package.infolist()
            names = [entry.filename.replace("\\", "/") for entry in entries]
            check("archive-unique-members", len(set(names)) == len(names))
            invalid = []
            for entry, name in zip(entries, names):
                relative = PurePosixPath(name)
                if relative.is_absolute() or ".." in relative.parts or ":" in name or stat.S_ISLNK(entry.external_attr >> 16):
                    invalid.append(name)
                if not entry.is_dir():
                    inventory.append({"path": name, "bytes": entry.file_size, "sha256": hashlib.sha256(package.read(entry)).hexdigest()})
            check("archive-safe-members", not invalid, invalid=invalid)
            dependencies = [name for name in names if {"node_modules", ".git", ".env", "npm-cache", "__pycache__"} & set(PurePosixPath(name).parts)]
            check("archive-no-dependency-cache-secret-tree", not dependencies, unexpected=dependencies)
            if invalid:
                raise ValueError("Unsafe archive members were refused before extraction")
            package.extractall(extracted)
        check("archive-extracts", True, archive=str(archive), sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    except Exception as error:
        check("archive-extracts", False, error=str(error))

    manifest_names = ["manifest.json"] if args.kind == "claude-desktop" else ["plugin.json", "mcp.json"]
    manifests = {}
    for name in manifest_names:
        try:
            data = json.loads((extracted / name).read_text(encoding="utf-8-sig"))
            manifests[name] = data
            check("archive-root-manifest:" + name, True)
            if args.kind != "claude-desktop":
                url = "https://agent-plugins.org/schemas/1.0.0/" + name.replace(".json", ".schema.json")
                with urlopen(url, timeout=25) as response:
                    raw = response.read(1024 * 1024)
                schema = json.loads(raw)
                (output / name.replace(".json", ".schema.json")).write_bytes(raw)
                errors = [error.message for error in Draft202012Validator(schema).iter_errors(data)]
                check("primary-schema:" + name, not errors, errors=errors, url=url, schema_sha256=hashlib.sha256(raw).hexdigest())
        except Exception as error:
            check("manifest:" + name, False, error=str(error))

    if args.kind == "claude-desktop" and "manifest.json" in manifests:
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if npm:
            cache = output / "npm-cache"
            command = [npm, "exec", "--cache", str(cache), "--yes", "--package", "@anthropic-ai/mcpb@" + args.mcpb_version, "--", "mcpb", "validate", str(extracted / "manifest.json")]
            result = subprocess.run(command, cwd=extracted, capture_output=True, text=True, encoding="utf-8", timeout=180)
            (output / "mcpb-stdout.txt").write_text(result.stdout, encoding="utf-8")
            (output / "mcpb-stderr.txt").write_text(result.stderr, encoding="utf-8")
            check("official-mcpb-cli-schema", result.returncode == 0, exit_code=result.returncode, command=command)
        else:
            check("official-mcpb-cli-schema", False, error="npm unavailable in evaluator")

    launch = None
    try:
        if args.kind == "claude-desktop":
            manifest = manifests["manifest.json"]
            config = manifest["server"]["mcp_config"]
            entry = manifest["server"]["entry_point"]
            check("mcpb-entry-point-exists", (extracted / entry).is_file())
        else:
            servers = manifests["mcp.json"]["mcpServers"]
            check("one-local-server", len(servers) == 1)
            config = next(iter(servers.values()))
            check("portable-stdio-transport", config.get("type") == "stdio")

        def substitute(value: str) -> str:
            return value.replace("${PLUGIN_ROOT}", str(extracted)).replace("${__dirname}", str(extracted))

        command = config.get("command")
        check("node-runtime-launch", command in ("node", "node.exe"))
        arguments = [substitute(str(value)) for value in config.get("args", [])]
        cwd = Path(substitute(config.get("cwd", str(extracted))))
        if not cwd.is_absolute():
            cwd = extracted / cwd
        cwd = cwd.resolve()
        check("contained-working-directory", cwd.is_relative_to(extracted) and cwd.is_dir(), actual=str(cwd))
        environment = {key: substitute(value) for key, value in config.get("env", {}).items()}
        unresolved = [value for value in [*arguments, str(cwd), *environment.values()] if "${" in value]
        check("declared-path-substitution-complete", not unresolved, unresolved=unresolved)
        check("runtime-launch-arguments-present", bool(arguments))
        launch = {"command": command, "args": arguments, "cwd": str(cwd), "env": environment}
    except Exception as error:
        check("runtime-launch-declaration", False, error=str(error))

    report = {"passed": all(item["passed"] for item in checks), "kind": args.kind, "poc": str(args.poc.resolve()), "checks": checks, "launch": launch, "extracted": str(extracted), "inventory": inventory, "scope": "Independent archive/schema/declared launch checks only; protocol, browser fixture and actual host paint are separate."}
    (output / "package-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(checks), "failed": [item["name"] for item in checks if not item["passed"]], "report": str(output / "package-review.json")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
