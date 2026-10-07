#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure local script scaling with one warm-up and three verified fresh runs.

Timings include uv/process startup. This is not live Lucid service performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = ROOT / "skills" / "lucidchart-svg"
REPETITIONS = 3


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(family: str, count: int, directory: Path) -> tuple[Path, bytes]:
    directory.mkdir(parents=True, exist_ok=False)
    source = directory / ("source.svg" if family == "inspect" else "input.json")
    if family == "inspect":
        body = ''.join(f'<g data-node-id="n{i}"><rect x="{i % 50 * 130}" y="{i // 50 * 70}" width="110" height="50" fill="#ffffff" stroke="#222222"/><text x="{i % 50 * 130 + 8}" y="{i // 50 * 70 + 30}">Item {i}</text></g>' for i in range(count))
        source.write_bytes(f'<svg xmlns="http://www.w3.org/2000/svg" width="6500" height="7000" viewBox="0 0 6500 7000">{body}</svg>\n'.encode("utf-8"))
    elif family == "native":
        graph = {"title": f"Native chain {count}", "nodes": [{"id": f"n{i}", "type": "rectangle", "label": f"Item {i}", "x": i % 40 * 150, "y": i // 40 * 80, "width": 120, "height": 50} for i in range(count)],
                 "edges": [{"id": f"e{i}", "source": f"n{i}", "target": f"n{i+1}"} for i in range(count - 1)]}
        write_json(source, graph)
    else:
        values = [{"id": f"person-{i}", "parent": "" if i == 0 else "person-0", "name": f"Person {i}"} for i in range(count)]
        value = {"graph": {"title": f"Hierarchy {count}", "infinite_canvas": True, "nodes": []}, "collections": [{"id": "people", "values": values}],
                 "layouts": [{"id": "org", "type": "orgChart", "collectionId": "people", "idField": "id", "foreignKeyField": "parent", "nameField": "name", "position": {"x": 100, "y": 100}}]}
        write_json(source, value)
    return source, source.read_bytes()


def measure(family: str, count: int, directory: Path) -> dict:
    source, original = fixture(family, count, directory)
    records = []
    package_hashes = []
    for repetition in range(REPETITIONS + 1):
        output = directory / f"run-{repetition}"
        output.mkdir()
        report = output / "report.json"
        script = {"inspect": "inspect_svg.py", "native": "build_native.py", "generated": "build_generated.py"}[family]
        args = ["uv", "run", "--script", str(BUNDLE / "scripts" / script)]
        if family == "inspect":
            args += ["inspect", str(source), "--report", str(report)]
        else:
            args += [str(source), "--output", str(output / "diagram.lucid"), "--document-json", str(output / "document.json"), "--report", str(report)]
        started = time.perf_counter()
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        seconds = time.perf_counter() - started
        if result.returncode:
            raise RuntimeError(f"{family}/{count}: helper failed ({result.returncode}): {result.stderr}")
        if source.read_bytes() != original:
            raise ValueError("Performance helper modified input")
        value = json.loads(report.read_text(encoding="utf-8"))
        if family == "inspect":
            if value["vector_element_count"] != count * 2 or len(value["labels"]) != count or value["sha256"] != hashlib.sha256(original).hexdigest() or value["ready_for_upload"] is not True:
                raise ValueError("Inspection workload count/identity mismatch")
            size = report.stat().st_size
        else:
            document_bytes = (output / "document.json").read_bytes()
            document = json.loads(document_bytes)
            with zipfile.ZipFile(output / "diagram.lucid") as package:
                if package.namelist() != ["document.json"] or package.read("document.json") != document_bytes or package.testzip() is not None:
                    raise ValueError("Compiled ZIP/document mismatch")
            page = document["pages"][0]
            if family == "native":
                if len(page["shapes"]) != count or len(page["lines"]) != count - 1:
                    raise ValueError("Native workload cardinality mismatch")
            else:
                if len(page["dataBackedShapes"]) != 1 or page.get("settings", {}).get("infiniteCanvas") is not True:
                    raise ValueError("Generated workload page/layout mismatch")
                if value.get("totals", {}).get("orgChart") != count or value["generated_layouts"][0].get("item_count") != count or len(document["collections"][0]["values"]) != count:
                    raise ValueError("Generated workload item count mismatch")
            package_hashes.append(sha(output / "diagram.lucid"))
            size = len(document_bytes)
        records.append({"repetition": repetition, "warmup": repetition == 0, "seconds": round(seconds, 6), "output_bytes": size, "exit_code": 0, "command": args})
    if package_hashes and len(set(package_hashes)) != 1:
        raise ValueError("Packages are nondeterministic across identical workload repetitions")
    measured = [item["seconds"] for item in records if not item["warmup"]]
    return {"family": family, "items": count, "passed": True, "measured_repetitions": REPETITIONS, "median_seconds": statistics.median(measured), "minimum_seconds": min(measured), "maximum_seconds": max(measured),
            "median_items_per_second": round(count / statistics.median(measured), 2), "source_sha256": sha(source), "source_bytes": len(original), "package_sha256": package_hashes[0] if package_hashes else None, "records": records}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to((ROOT / "evaluations" / "runs").resolve()):
        parser.error("Use an unused output path under evaluations/runs")
    work = output.parent / "performance-workspace"
    if work.exists():
        parser.error("Performance workspace already exists; use a fresh output directory")
    results = []
    for family, counts in (("inspect", (100, 1000, 5000)), ("native", (10, 100, 1000)), ("generated", (100, 1000, 4000))):
        for count in counts:
            try:
                result = measure(family, count, work / f"{family}-{count}")
            except (ValueError, RuntimeError, OSError, KeyError, zipfile.BadZipFile) as error:
                failure = {"family": family, "items": count, "passed": False, "error": str(error)}
                results.append(failure)
                write_json(output, {"schema_version": 1, "complete": False, "workloads": results, "failure": failure})
                print(json.dumps(failure), flush=True)
                raise SystemExit(1)
            results.append(result)
            print(json.dumps({key: result[key] for key in ("family", "items", "median_seconds", "passed")}), flush=True)
            write_json(output, {"schema_version": 1, "platform": platform.platform(), "python_version": platform.python_version(), "processor": platform.processor(), "timing_scope": "Local helper CLI, including uv/process startup; one warm-up and three fresh measured runs. No live Lucid performance claim.", "complete": len(results) == 9, "workloads": results})


if __name__ == "__main__":
    main()
