#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Capture two installed Codex cores without inference or global configuration writes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npm-codex", type=Path, required=True)
    parser.add_argument("--desktop-codex", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if (out / "inventory.json").exists():
        parser.error("Choose a fresh output directory; previous evidence is preserved.")
    out.mkdir(parents=True, exist_ok=True)
    commands = {
        "version": ["--version"],
        "help": ["--help"],
        "exec-help": ["exec", "--help"],
        "app-server-help": ["app-server", "--help"],
        "mcp-help": ["mcp", "--help"],
        "plugin-help": ["plugin", "--help"],
        "feature-defaults": ["features", "list"],
    }
    report = {"capturedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "scope": "Installed executable help, isolated default feature flags and generated protocol schemas",
              "modelTurnsStarted": 0, "globalConfigurationWrites": False, "cores": []}
    for label, executable in (("npm", args.npm_codex), ("desktop-bundled", args.desktop_codex)):
        executable = executable.resolve(strict=True)
        folder = out / label
        folder.mkdir()
        isolated_home = folder / "isolated-home"
        isolated_home.mkdir()
        env = dict(os.environ, CODEX_HOME=str(isolated_home))
        core = {"label": label, "executable": str(executable),
                "sha256": hashlib.sha256(executable.read_bytes()).hexdigest(), "commands": {}}
        for name, command_args in commands.items():
            completed = subprocess.run([str(executable), *command_args], cwd=folder, env=env,
                                       capture_output=True, text=True, encoding="utf-8", timeout=40)
            (folder / (name + ".stdout.txt")).write_text(completed.stdout, encoding="utf-8")
            (folder / (name + ".stderr.txt")).write_text(completed.stderr, encoding="utf-8")
            core["commands"][name] = {"argv": command_args, "exitCode": completed.returncode}
            if name == "version":
                core["version"] = completed.stdout.strip()
        schema = folder / "schema"
        command_args = ["app-server", "generate-json-schema", "--experimental", "--out", str(schema)]
        completed = subprocess.run([str(executable), *command_args], cwd=folder, env=env,
                                   capture_output=True, text=True, encoding="utf-8", timeout=60)
        (folder / "schema.stdout.txt").write_text(completed.stdout, encoding="utf-8")
        (folder / "schema.stderr.txt").write_text(completed.stderr, encoding="utf-8")
        core["commands"]["schema"] = {"argv": command_args, "exitCode": completed.returncode,
                                        "jsonFileCount": len(list(schema.rglob("*.json")))}
        report["cores"].append(core)
    (out / "inventory.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all(command["exitCode"] == 0 for core in report["cores"] for command in core["commands"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
