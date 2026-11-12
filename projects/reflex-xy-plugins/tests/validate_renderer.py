#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0"]
# ///
"""Exercise the public XY JSON CLI with real native exports and hostile inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from artifact_contract import inspect_html, inspect_png, inspect_svg, require


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", type=Path, required=True)
    parser.add_argument("--skill-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--palettes", type=Path, required=True)
    parser.add_argument("--presets", default="line,scatter,bar,sankey,pie,heatmap")
    parser.add_argument("--python", type=Path, help="Use an installed XY environment rather than uv")
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    palettes = json.loads(args.palettes.read_text(encoding="utf-8"))["colorsets"]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["UV_CACHE_DIR"] = str(args.output_dir / "uv-cache")
    all_results = []

    def run(name: str, spec: dict, valid: bool = True, raw: str | None = None) -> dict:
        output = args.output_dir / name
        command = [str(args.python), str(args.renderer.resolve())] if args.python else ["uv", "run", "--script", str(args.renderer.resolve())]
        command += ["--output-dir", str(output)]
        if args.skill_dir:
            command += ["--skill-dir", str(args.skill_dir.resolve())]
        request = raw if raw is not None else json.dumps(spec, ensure_ascii=True, allow_nan=False)
        started = time.monotonic()
        done = subprocess.run(command, cwd=args.output_dir, input=request, encoding="utf-8",
                              capture_output=True, env=env, timeout=180)
        record = {"case": name, "valid": valid, "returncode": done.returncode,
                  "seconds": round(time.monotonic() - started, 3),
                  "stdout": done.stdout[-4000:], "stderr": done.stderr[-2000:]}
        try:
            if valid:
                require(done.returncode == 0, f"Renderer failed for {name}: {done.stderr}")
                result = json.loads(done.stdout)
                require(result["schema_version"] == 1, "Unexpected response schema version")
                require(result["palette"] == spec["colorset"], "Result palette does not match request")
                require(result["width"] >= 320 and result["height"] >= 240, "Invalid result dimensions")
                palette = palettes[spec["colorset"]]
                paths = {}
                for key in ["html", "svg", "png", "source", "spec"]:
                    relative = Path(result["files"][key])
                    require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe result artifact path")
                    path = (output / relative).resolve()
                    require(path.is_relative_to(output) and path.is_file() and path.stat().st_size, f"Missing artifact {key}")
                    paths[key] = path
                # Some native chart families use interpolated/alpha paint. The
                # independent report keeps all observed paint rather than
                # silently classifying it as exact-palette output.
                record["svg"] = inspect_svg(paths["svg"], set(palette["allowed"]), allow_derived=True)
                record["png"] = inspect_png(paths["png"], palette["roles"]["background"])
                record["html"] = inspect_html(paths["html"])
                require(paths["svg"].stat().st_size == result["svg_bytes"], "SVG byte count mismatch")
                require(paths["png"].stat().st_size == result["png_bytes"], "PNG byte count mismatch")
                stored_spec = json.loads(paths["spec"].read_text(encoding="utf-8"))
                require(stored_spec.get("colorset") == spec["colorset"], "Saved spec changed requested palette")
                if "data" in spec:
                    require(stored_spec.get("data") == spec["data"], "Saved spec changed supplied measurements")
                record["artifact_hashes"] = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}
                record["response"] = result
            else:
                require(done.returncode == 2, f"Invalid input was not rejected with exit 2: {name}")
                require(not done.stdout.strip(), "Invalid input emitted success data on stdout")
                error = json.loads(done.stderr)
                require(isinstance(error.get("error"), dict) and error["error"].get("code") and error["error"].get("message"), "Missing structured error")
                record["error"] = error
                require(not output.exists() or not any(output.glob("chart.*")), "Invalid input left partial success artifacts")
            record["passed"] = True
        except Exception as error:
            record["passed"] = False
            record["failure"] = f"{type(error).__name__}: {error}"
        all_results.append(record)
        print(json.dumps({key: record[key] for key in ["case", "passed", "returncode", "seconds"]}), flush=True)
        return record

    for preset in args.presets.split(","):
        for colorset in palettes:
            run(f"{preset}-{colorset}", {"preset": preset, "colorset": colorset,
                                       "title": f"Native {preset} / {colorset}"})
    # Same input rows exercise the generic channel API rather than relying only
    # on the adapter's pre-authored gallery data.
    for colorset in palettes:
        run(f"generic-mixed-{colorset}", {
            "version": 1, "factory": "chart", "colorset": colorset,
            "title": "Independent measurements", "width": 720, "height": 460,
            "data": {"elapsed": [0, 2, 5, 9, 14], "reading": [4, 7, 3, 11, 8]},
            "marks": [{"kind": "line", "args": ["elapsed", "reading"], "kwargs": {}},
                      {"kind": "scatter", "args": ["elapsed", "reading"], "kwargs": {}}],
            "components": [{"kind": "x_axis", "args": [], "kwargs": {"label": "Elapsed time (s)"}},
                           {"kind": "y_axis", "args": [], "kwargs": {"label": "Measured response"}}]
        })
    run("literal-untrusted-title", {"preset": "scatter", "colorset": "colorset1",
        "title": '</script><img src="https://invalid.example/" onerror="globalThis.__xyInjected=true">'})
    invalid = [
        ("unknown-preset", {"preset": "__import__('os').system('echo injected')", "colorset": "colorset1"}),
        ("unknown-palette", {"preset": "line", "colorset": "colorset3"}),
        ("oversize-dimensions", {"preset": "line", "colorset": "colorset1", "width": 100000}),
        ("arbitrary-output-path", {"preset": "line", "colorset": "colorset1", "output_dir": "../../outside"}),
        ("external-data-url", {"preset": "line", "colorset": "colorset1", "data": "https://invalid.example/rows.csv"}),
        ("code-field", {"preset": "line", "colorset": "colorset1", "code": "import os"}),
        ("dunder-factory", {"version": 1, "factory": "__getattribute__", "colorset": "colorset1", "marks": []}),
        ("unknown-mark", {"version": 1, "factory": "chart", "colorset": "colorset1", "marks": [{"kind": "eval", "args": ["1+1"], "kwargs": {}}]}),
        ("infinite-number", {}, '{"preset":"scatter","colorset":"colorset1","data":{"x":[1],"y":[NaN]}}'),
        ("malformed-json", {}, '{"preset":'),
        ("boolean-version", {"version": True, "factory": "chart", "colorset": "colorset1", "marks": []}),
        ("unequal-line-arrays", {"version": 1, "factory": "chart", "colorset": "colorset1",
            "marks": [{"kind": "line", "args": [[1, 2, 3], [4, 5]], "kwargs": {}}]}),
        ("empty-pie", {"version": 1, "factory": "pie_chart", "colorset": "colorset1", "args": [[]]}),
        ("huge-integer", {}, '{"preset":"line","colorset":"colorset1","data":{"x":[1],"y":[' + '9' * 500 + ']}}'),
        ("unexpected-theme-args", {"version": 1, "factory": "chart", "colorset": "colorset1",
            "marks": [{"kind": "line", "args": [[1, 2], [4, 5]], "kwargs": {}}],
            "components": [{"kind": "theme", "args": ["unexpected"], "kwargs": {}}]}),
    ]
    for entry in invalid:
        run(entry[0], entry[1], False, entry[2] if len(entry) == 3 else None)
    report = {"passed": all(item["passed"] for item in all_results),
              "cases": len(all_results), "passed_cases": sum(item["passed"] for item in all_results),
              "results": all_results, "renderer": str(args.renderer.resolve())}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["passed", "cases", "passed_cases"]}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
