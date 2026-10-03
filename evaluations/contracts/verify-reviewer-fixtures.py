#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify synthetic baseline, legitimate change, and independently triggered regressions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixtures", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    fixture_data = json.loads(args.fixtures.read_text(encoding="utf-8"))
    results = []
    for key, fixture in fixture_data.items():
        for variant in ("baseline", "legitimate", "regression"):
            root = (args.output / key / variant).resolve()
            files = dict(fixture["files"])
            if variant != "baseline":
                files.update(fixture[variant])
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            temporary = root / "temporary"
            temporary.mkdir(exist_ok=True)
            import os
            environment = dict(os.environ, TEMP=str(temporary), TMP=str(temporary), PYTHONDONTWRITEBYTECODE="1")
            unit = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"], cwd=root, env=environment, capture_output=True, text=True)
            expected_unit = 1 if key == "tenant" and variant == "regression" else 0
            passed = (unit.returncode != 0) if expected_unit else (unit.returncode == 0)
            path_escape = None
            if key == "export":
                spec = importlib.util.spec_from_file_location(f"export_{variant}", root / "src/export.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                export_root = root / "temporary" / "out"
                try:
                    module.export_text(export_root, "../out-sibling/report.txt", "synthetic")
                    path_escape = True
                except ValueError:
                    path_escape = False
                passed = passed and (path_escape == (variant == "regression"))
            results.append({"fixture": key, "variant": variant, "passed": passed, "unit_exit": unit.returncode, "sibling_path_escape": path_escape, "unit_output": unit.stderr.strip()})
    report = {"passed": all(item["passed"] for item in results), "results": results}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "fixture-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
