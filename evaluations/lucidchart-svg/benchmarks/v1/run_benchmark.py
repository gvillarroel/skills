#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze, run, or summarize the public Lucidchart SVG development benchmark.

Run from any directory. The repository Pi helper supplies isolation and strict gates.
Manual reviews must be evaluator-owned records beside, never inside, workspaces.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SKILL = "lucidchart-svg"
MODEL = "openai-codex/gpt-5.6-luna"
EXPECTED_PAYLOAD = "0e4d5c69add73792b268cb0890edbb48d39c573e1fdb9a908ba017ad50679f93"
CASES = {
    "contract": (1, 1, "contract-smoke", "validate_native_cases.py", ["input/contract.json", "out/contract/diagram.lucid", "out/contract/document.json", "out/contract/native-report.json", "out/contract/notes.md"]),
    "geometry": (3, 2, "naturalistic-forward", "validate_svg_cases.py", ["inputs/dispatch.svg", "outputs/dispatch/inspection.json", "outputs/dispatch/graph.json", "outputs/dispatch/mapping.json", "outputs/dispatch/diagram.lucid", "outputs/dispatch/document.json", "outputs/dispatch/fidelity.md"]),
    "relations": (3, 2, "generalization", "validate_svg_cases.py", ["source/release-route.svg", "deliver/release/inspection.json", "deliver/release/graph.json", "deliver/release/mapping.json", "deliver/release/native.lucid", "deliver/release/document.json", "deliver/release/changes.md"]),
    "asset": (3, 2, "naturalistic-forward", "validate_svg_cases.py", ["source/night-shift.svg", "ready/night-shift.svg", "review/inspection.json", "review/fidelity.md"]),
    "boundary": (1, 1, "boundary-recovery", "validate_boundaries.py", ["input/received.svg", "out/boundary/inspection.json", "out/boundary/notes.md"]),
    "ambiguity": (1, 1, "boundary-recovery", "validate_boundaries.py", ["source/sketch.svg", "out/ambiguity/inspection.json", "out/ambiguity/visual.svg", "out/ambiguity/notes.md"]),
    "semantic": (3, 2, "generalization", "validate_native_cases.py", ["out/semantic/graph.json", "out/semantic/diagram.lucid", "out/semantic/document.json", "out/semantic/native-report.json", "out/semantic/notes.md"]),
    "generated": (3, 2, "generalization", "validate_native_cases.py", ["out/generated/layout.json", "out/generated/diagram.lucid", "out/generated/document.json", "out/generated/layout-report.json", "out/generated/notes.md"]),
}
IGNORE = {"node_modules", ".git", ".cache", ".venv", "venv", "__pycache__", "dist", "output", "playwright-report", "test-results", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".tox", ".vite"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_snapshot() -> dict:
    bundle = ROOT / "skills" / SKILL
    files = {}
    for path in sorted(bundle.rglob("*")):
        relative = path.relative_to(bundle)
        if not path.is_file() or IGNORE.intersection(relative.parts) or path.suffix.lower() in {".pyc", ".pyo"} or relative.parts[:2] == ("assets", "examples"):
            continue
        files[relative.as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": digest(path)}
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"file_count": len(files), "sha256": hashlib.sha256(encoded).hexdigest(), "files": files}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def controls() -> list[Path]:
    return [Path(__file__).resolve(), HERE / "protocol.md", HERE / "run_performance.py"] + sorted(HERE.glob("validate_*.py")) + [ROOT / "evaluations" / "pi-prompts" / f"lucidchart-svg-benchmark-v1-{case}.md" for case in CASES]


def freeze(destination: Path, expected_payload: str) -> None:
    if destination.exists():
        raise ValueError("Manifest already exists; preserve its identity and use a new benchmark version")
    snapshot = runtime_snapshot()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_payload) or snapshot["file_count"] != 21 or snapshot["sha256"] != expected_payload:
        raise ValueError("Skill changed before freeze; declare a separate subject revision")
    paths = controls()
    if any(not path.is_file() for path in paths):
        raise ValueError("All prompts, validators and protocol must exist before freezing")
    manifest = {"schema_version": 1, "benchmark_id": "lucidchart-svg-v1", "visibility": "public-development", "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "subject": {"skill": SKILL, "profile": "runtime", "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), **snapshot},
                "model": MODEL, "thinking": "high", "model_exception": "Existing backlog exception after Spark account/provider rejection before tools; no gate is waived.",
                "controls": {path.relative_to(ROOT).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size} for path in paths},
                "cases": {case: {"repetitions": count, "required_joint_passes": threshold, "taxonomy": taxonomy, "validator": validator, "expected_outputs": outputs, "prompt": f"evaluations/pi-prompts/lucidchart-svg-benchmark-v1-{case}.md", "exact_command": case == "contract"} for case, (count, threshold, taxonomy, validator, outputs) in CASES.items()},
                "required_trials": 18, "live_service_coverage": "unverified", "is_holdout": False}
    save(destination, manifest)
    print(json.dumps({"frozen": str(destination), "trials": 18, "payload": snapshot["sha256"]}))


def verify(manifest: dict) -> None:
    if runtime_snapshot()["sha256"] != manifest["subject"]["sha256"]:
        raise ValueError("Frozen subject payload changed")
    for relative, record in manifest["controls"].items():
        if digest(ROOT / relative) != record["sha256"]:
            raise ValueError(f"Frozen benchmark control changed: {relative}")


def command(args: list[str]) -> dict:
    started = time.monotonic()
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": args, "exit_code": result.returncode, "elapsed_seconds": round(time.monotonic() - started, 3), "stdout": result.stdout, "stderr": result.stderr}


def evaluate(manifest: dict, prefix: str, case: str, repetition: int) -> dict:
    spec = manifest["cases"][case]
    run_id = f"{prefix}-{case}-luna-{repetition}"
    run_dir = ROOT / "evaluations" / "runs" / run_id
    if run_dir.exists():
        raise ValueError(f"Refusing to reuse an existing trial: {run_id}")
    args = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", SKILL, "--prompt-file", spec["prompt"], "--model", manifest["model"], "--thinking", manifest["thinking"], "--mode", "json", "--strict", "--run-id", run_id]
    for path in spec["expected_outputs"]:
        args += ["--expect-output", path]
    if spec["exact_command"]:
        args.append("--require-exact-command-from-prompt")
    result = {"case": case, "repetition": repetition, "run_id": run_id, "harness": command(args)}
    result["independent"] = command(["uv", "run", "--script", str(HERE / spec["validator"]), case, str(run_dir / "workspace"), "--report", str(run_dir / "independent-benchmark.json")])
    result["read_surface"] = command(["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run_dir / "events.jsonl"), "--require-model", manifest["model"].split("/", 1)[1], "--require-tool-call", "--require-read", "../prompt.md", "--require-read", f"skills/{SKILL}/SKILL.md", "--fail-on-invalid-json", "--fail-on-tool-error", "--output", str(run_dir / "benchmark-read-surface.json")])
    copied = run_dir / "run-manifest.json"
    result["payload_matches"] = copied.is_file() and load(copied)["skill"]["payloadSha256"] == manifest["subject"]["sha256"]
    result["machine_passed"] = result["payload_matches"] and all(result[key]["exit_code"] == 0 for key in ("harness", "independent", "read_surface"))
    result["manual_review_pending"] = True
    save(run_dir / "benchmark-result.json", result)
    print(json.dumps({key: result[key] for key in ("case", "run_id", "machine_passed", "payload_matches")}), flush=True)
    return result


def run(manifest: dict, prefix: str, jobs: int, destination: Path) -> None:
    verify(manifest)
    if destination.exists() or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,100}", prefix):
        raise ValueError("Use a new safe run prefix and unused aggregate path")
    inventory = [(case, repetition) for case, spec in manifest["cases"].items() for repetition in range(1, spec["repetitions"] + 1)]
    if any((ROOT / "evaluations" / "runs" / f"{prefix}-{case}-luna-{repetition}").exists() for case, repetition in inventory):
        raise ValueError("A planned trial directory exists; use a fresh prefix")
    completed = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        tasks = {pool.submit(evaluate, manifest, prefix, case, repetition): (case, repetition) for case, repetition in inventory}
        for future in as_completed(tasks):
            case, repetition = tasks[future]
            try:
                record = future.result()
            except Exception as error:
                record = {"case": case, "repetition": repetition, "run_id": f"{prefix}-{case}-luna-{repetition}",
                          "machine_passed": False, "payload_matches": False, "manual_review_pending": True,
                          "failure_class": "harness-or-infrastructure", "error": f"{type(error).__name__}: {error}"}
                save(ROOT / "evaluations" / "runs" / record["run_id"] / "benchmark-result.json", record)
                print(json.dumps(record), flush=True)
            completed.append(record)
            save(destination, {"benchmark_id": manifest["benchmark_id"], "run_prefix": prefix, "planned_trials": manifest["required_trials"], "completed_trials": len(completed), "results": sorted(completed, key=lambda item: (item["case"], item["repetition"]))})
    verify(manifest)
    if not all(record["machine_passed"] for record in completed):
        raise SystemExit(1)


def summarize(manifest: dict, source: Path, destination: Path) -> None:
    verify(manifest)
    aggregate = load(source)
    if aggregate.get("benchmark_id") != manifest["benchmark_id"] or aggregate.get("planned_trials") != manifest["required_trials"]:
        raise ValueError("Cohort does not match the frozen benchmark")
    identities = set()
    for record in aggregate["results"]:
        case, repetition = record["case"], record["repetition"]
        if case not in manifest["cases"] or type(repetition) is not int or not 1 <= repetition <= manifest["cases"][case]["repetitions"]:
            raise ValueError("Unexpected cohort case/repetition")
        expected = f"{aggregate['run_prefix']}-{case}-luna-{repetition}"
        if record["run_id"] != expected or expected in identities:
            raise ValueError("Duplicate or mismatched cohort trial")
        identities.add(expected)
    results, durations, usage = [], [], []
    for record in aggregate["results"]:
        run_dir = ROOT / "evaluations" / "runs" / record["run_id"]
        manual_path = run_dir / "manual-benchmark-review.json"
        manual = load(manual_path) if manual_path.is_file() else {}
        reviewed = all(manual.get(key) is True for key in ("passed", "read_surface_passed", "commands_passed", "artifact_review_passed", "narrative_review_passed")) and manual.get("run_id") == record["run_id"] and manual.get("case") == record["case"]
        result = {"case": record["case"], "run_id": record["run_id"], "machine_passed": record["machine_passed"], "manual_review_completed": bool(manual), "manual_passed": reviewed, "joint_passed": record["machine_passed"] and reviewed, "manual_findings": manual.get("findings", [])}
        evaluation = load(run_dir / "evaluation-result.json") if (run_dir / "evaluation-result.json").is_file() else {}
        reads = load(run_dir / "benchmark-read-surface.json") if (run_dir / "benchmark-read-surface.json").is_file() else {}
        result["pi_duration_seconds"] = evaluation.get("durationSeconds")
        result["reported_token_usage"] = reads.get("usageTotals")
        if isinstance(result["pi_duration_seconds"], (int, float)):
            durations.append(result["pi_duration_seconds"])
        if isinstance(result["reported_token_usage"], dict) and "totalTokens" in result["reported_token_usage"]:
            usage.append(result["reported_token_usage"])
        results.append(result)
    by_case = {}
    for case, spec in manifest["cases"].items():
        records = [item for item in results if item["case"] == case]
        passed = sum(item["joint_passed"] for item in records)
        by_case[case] = {"planned": spec["repetitions"], "completed": len(records), "joint_passes": passed, "required_joint_passes": spec["required_joint_passes"], "threshold_met": len(records) == spec["repetitions"] and passed >= spec["required_joint_passes"]}
    token_values = {key: [value[key] for value in usage if type(value.get(key)) in (int, float)] for key in ("input", "output", "cacheRead", "cacheWrite", "totalTokens")}
    save(destination, {"benchmark_id": manifest["benchmark_id"], "subject_payload": manifest["subject"]["sha256"], "model": manifest["model"], "planned_trials": manifest["required_trials"], "completed_trials": len(results), "joint_passes": sum(item["joint_passed"] for item in results), "case_thresholds_met": all(value["threshold_met"] for value in by_case.values()), "cases": by_case, "results": results,
                       "resources": {"duration_observed_trials": len(durations), "duration_median_seconds": statistics.median(durations) if durations else None, "duration_min_seconds": min(durations) if durations else None, "duration_max_seconds": max(durations) if durations else None, "token_observed_trials": len(usage), "reported_token_totals": {key: sum(values) if values else None for key, values in token_values.items()}, "token_field_observed_trials": {key: len(values) for key, values in token_values.items()}, "reported_cost_usd": None, "timing_note": "Pi wall times with up to four concurrent local trials; observational, no no-skill baseline or isolated-latency claim."}, "visibility": "public-development", "is_holdout": False, "live_lucid_acceptance": "unverified"})
    print(json.dumps({"summary": str(destination), "joint_passes": sum(item["joint_passed"] for item in results), "completed": len(results)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("identity", "freeze", "run", "summarize"))
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest.json")
    parser.add_argument("--subject-sha256", default=EXPECTED_PAYLOAD, help="Explicit exact raw payload for a new manifest; never alters an existing freeze")
    parser.add_argument("--run-prefix", default="20261007-lucid-benchmark-v1")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--runs", type=Path)
    args = parser.parse_args()
    if args.action == "identity":
        snapshot = runtime_snapshot()
        print(json.dumps({"profile": "runtime", "file_count": snapshot["file_count"], "sha256": snapshot["sha256"]}))
        return
    if args.action == "freeze":
        freeze(args.manifest.resolve(), args.subject_sha256)
        return
    if args.output is None or not args.output.resolve().is_relative_to((ROOT / "evaluations" / "runs").resolve()):
        parser.error("--output must be under ignored evaluations/runs")
    manifest = load(args.manifest.resolve())
    if args.action == "run":
        run(manifest, args.run_prefix, args.jobs, args.output.resolve())
    else:
        if args.runs is None:
            parser.error("summarize requires --runs")
        summarize(manifest, args.runs.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
