#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run vector-logo release checks with temporary files kept inside this project."""

from __future__ import annotations

import argparse
import importlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository", action="store_true")
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if not output.is_relative_to(root / "projects/plantuml-colorset-renderer/artifacts"):
        parser.error("Keep generated validation evidence in this project's artifacts directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent / "test-temporary"
    temporary.mkdir(exist_ok=True)
    tempfile.tempdir = str(temporary)
    environment = {**os.environ, "TMP": str(temporary), "TEMP": str(temporary), "TMPDIR": str(temporary),
                   "UV_CACHE_DIR": str(output.parent / "uv-cache"), "PYTHONDONTWRITEBYTECODE": "1"}
    sys.path.insert(0, str(root / "skills/plantuml-colorset-renderer/scripts"))
    checks = []
    original_cwd = Path.cwd()
    os.chdir(temporary)
    try:
        for module_name in ("test_logo_variants", "test_logo_assets", "test_plantuml_coverage"):
            start = time.monotonic()
            module = importlib.import_module(module_name)
            stream = io.StringIO()
            result = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromModule(module))
            record = {"name": module_name, "ok": result.wasSuccessful(), "tests": result.testsRun,
                      "elapsedSeconds": round(time.monotonic()-start, 2), "output": stream.getvalue()}
            checks.append(record)
            print(json.dumps({key: value for key, value in record.items() if key != "output"}), flush=True)
            if not result.wasSuccessful():
                print(stream.getvalue(), flush=True)
    finally:
        os.chdir(original_cwd)
    if args.repository:
        for name in ("validate-pattern-ids.py", "validate-skills.py", "test-skill-independence.py", "check-repo-payload.py", "test-pi-eval-harness.py"):
            command = ["uv", "run", "--script", "scripts/" + name]
            result = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            record = {"name": name, "command": command, "ok": result.returncode == 0, "exitCode": result.returncode,
                      "output": result.stdout + result.stderr}
            checks.append(record)
            print(json.dumps({"name": name, "ok": record["ok"], "output": record["output"][-6000:]}), flush=True)
    payload = {"ok": all(check["ok"] for check in checks), "checks": checks}
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["ok"], "report": str(output)}), flush=True)
    return int(not payload["ok"])


if __name__ == "__main__":
    raise SystemExit(main())
