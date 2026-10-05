#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently review the four frozen R2 primary-logo forwards."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXPECTED_RUNTIME = "1c61ccd9693630dc686eb408cba1736fe83fbf0ff70449a44e2894b779ef2450"
REQUIRED = ("deliverables/logo.html", "deliverables/validation.json", "deliverables/native.json", "deliverables/small-logo.png")
EXPECTED_CONFIGURATION = {"selectedColorset": "colorset1", "initialPattern": "d3-logo-type-orbit", "initialBrand": "ATLAS", "initialTagline": "Signals in motion", "standalone": True}
IDS = ["gray-20261005-logo-r2-d3-contract-1", *[f"gray-20261005-logo-r2-d3-naturalistic-{index}" for index in range(1, 4)]]
REVIEW = ROOT / "projects/grayscale-interleave/artifacts/reviews/primary-logo"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def png_dimensions(path: Path) -> list[int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Invalid PNG header: {path}")
    return list(struct.unpack(">II", header[16:24]))


def command(arguments: list[str], destination: Path) -> int:
    result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    destination.write_text(result.stdout + result.stderr, encoding="utf-8")
    return result.returncode


def runtime_snapshot(harness: dict) -> dict:
    source = ROOT / "skills/d3"
    snapshot = {}
    for current, directories, files in os.walk(source):
        current = Path(current)
        directories[:] = [name for name in directories if name not in harness["COPY_IGNORE"]
                          and (current / name).relative_to(source) not in harness["RUNTIME_EXCLUDED_DIRS"]]
        for name in files:
            path = current / name
            if name not in harness["COPY_IGNORE"] and path.suffix.lower() not in harness["SNAPSHOT_IGNORED_SUFFIXES"]:
                snapshot[path.relative_to(source).as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": digest(path)}
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true", help="Run current static and native helpers serially without changing trial artifacts")
    parser.add_argument("--manual-review", type=Path, help="Hash-bound manual PNG verdicts after visual inspection")
    args = parser.parse_args()
    REVIEW.mkdir(parents=True, exist_ok=True)
    harness = runpy.run_path(str(ROOT / "scripts/run-pi-skill-eval.py"))
    current_snapshot = runtime_snapshot(harness)
    current_runtime = harness["snapshot_digest"](current_snapshot)
    current_matches = current_runtime == EXPECTED_RUNTIME and len(current_snapshot) == 296
    manual = load(args.manual_review.resolve()) if args.manual_review else {}
    rows = []
    for run_id in IDS:
        run = ROOT / "evaluations/runs" / run_id
        workspace = run / "workspace"
        manifest = load(run / "run-manifest.json")
        result = load(run / "evaluation-result.json")
        artifacts = load(run / "artifact-check.json")
        events = load(run / "event-check.json")
        copied = harness["snapshot_tree"](workspace / "skills/d3")
        copied_digest = harness["snapshot_digest"](copied)
        prompt_path = ROOT / "evaluations/pi-prompts" / ("colorset1-gray-order-d3-logo-contract-20261005.md" if "-contract-" in run_id else "colorset1-gray-order-d3-logo-natural-20261005.md")
        prompt_digest = hashlib.sha256(prompt_path.read_text(encoding="utf-8").encode()).hexdigest()
        copied_prompt_digest = hashlib.sha256((run / "prompt.md").read_text(encoding="utf-8").encode()).hexdigest()
        frozen = manifest["skill"]["payloadSha256"] == copied_digest == EXPECTED_RUNTIME and len(copied) == manifest["skill"]["fileCount"] == 296
        prompt_matches = prompt_digest == copied_prompt_digest == manifest["prompt"]["sha256"]
        model_matches = manifest["pi"]["model"] == "openai-codex/gpt-5.6-luna" and events["observedModels"] == [{"provider": "openai-codex", "model": "gpt-5.6-luna"}]
        read_paths = sorted({call["path"] for call in events["calls"] if call.get("path")})
        allowed_reads = {"../prompt.md", "skills/d3/SKILL.md", "skills/d3/references/logo-studio.md", *REQUIRED}
        read_surface_pass = set(read_paths) <= allowed_reads
        strict = result["passed"] and result["returnCode"] == result["piExitCode"] == 0 and not result["timedOut"] and all(result["gates"].get(gate) is True for gate in ("artifacts", "events", "skillIntegrity"))
        strict = bool(strict and events["passed"] and model_matches and manifest["eventPolicy"]["strict"] and ("-contract-" not in run_id or manifest["eventPolicy"]["requireExactCommandFromPrompt"]))
        artifact_rows = []
        artifact_matches = artifacts["passed"] and artifacts["expectedOutputCount"] == 4 and not artifacts["missingOutputs"]
        for relative in REQUIRED:
            path = (workspace / relative).resolve()
            record = next(item for item in artifacts["outputs"] if item["path"] == relative)
            ok = path.is_relative_to(workspace.resolve()) and path.is_file() and digest(path) == record["sha256"] and path.stat().st_size == record["sizeBytes"]
            artifact_matches = artifact_matches and ok
            artifact_rows.append({"path": relative, "sha256": digest(path), "sizeBytes": path.stat().st_size, "matchesHarness": ok})
        authored_static = load(workspace / "deliverables/validation.json")
        authored_native = load(workspace / "deliverables/native.json")
        authored_reports_pass = authored_static["ok"] and authored_static["engineRegistryParity"] and not authored_static["findings"] and authored_native["clean"] and not authored_native["findings"] and not any(authored_native["browser"].values())
        authored_reports_pass = authored_reports_pass and all(authored_static.get(key) == value for key, value in EXPECTED_CONFIGURATION.items())
        small = authored_native["smallLogo"]
        authored_reports_pass = authored_reports_pass and png_dimensions(workspace / "deliverables/small-logo.png") == [96, 64] and small["wordmarkText"] == "ATLAS" and small["accessibleTaglinePreserved"] and small["configuredTagline"] == "Signals in motion"
        case = REVIEW / run_id
        case.mkdir(exist_ok=True)
        static_command = ["uv", "run", "--script", "skills/d3/scripts/validate_logo_artifact.py", str(workspace / "deliverables/logo.html"), "--require-colorset", "colorset1", "--json-report", str(case / "independent-static.json")]
        native_command = ["uv", "run", "--script", "skills/d3/scripts/verify_logo_gallery.py", str(workspace / "deliverables/logo.html"), "--small-only", "--json-report", str(case / "independent-native.json"), "--small-logo-screenshot", str(case / "independent-small.png")]
        if args.capture:
            static_code = command(static_command, case / "static.log")
            native_code = command(native_command, case / "native.log")
            (case / "commands.json").write_text(json.dumps({"static": {"command": static_command, "returnCode": static_code}, "native": {"command": native_command, "returnCode": native_code}}, indent=2) + "\n", encoding="utf-8")
        independent = load(case / "commands.json")
        independent_static = load(case / "independent-static.json")
        independent_native = load(case / "independent-native.json")
        independent_pass = independent["static"]["returnCode"] == independent["native"]["returnCode"] == 0 and independent_static["ok"] and independent_static["engineRegistryParity"] and not independent_static["findings"] and independent_native["clean"] and not independent_native["findings"] and not any(independent_native["browser"].values()) and png_dimensions(case / "independent-small.png") == [96, 64]
        independent_pass = independent_pass and all(independent_static.get(key) == value for key, value in EXPECTED_CONFIGURATION.items())
        manual_record = manual.get(run_id, {})
        manual_pass = manual_record.get("passed") is True and manual_record.get("authoredPngSha256") == digest(workspace / "deliverables/small-logo.png") and manual_record.get("independentPngSha256") == digest(case / "independent-small.png")
        raw = {name: digest(run / name) for name in ("events.jsonl", "run-manifest.json", "evaluation-result.json", "event-check.json", "artifact-check.json", "skill-integrity-check.json", "prompt.md")}
        row = {"runId": run_id, "family": "contract" if "-contract-" in run_id else "naturalistic", "durationSeconds": result["durationSeconds"], "strictPassed": strict, "frozenRuntimeMatches": frozen, "promptMatches": prompt_matches, "promptTextSha256": prompt_digest, "copiedRuntimeSha256": copied_digest, "rawFileSha256": raw, "readPaths": read_paths, "readSurfacePassed": read_surface_pass, "outputs": artifact_rows, "artifactsMatch": artifact_matches, "authoredReportsPassed": bool(authored_reports_pass), "independentNativePassed": bool(independent_pass), "independentEvidence": {name: {"path": (case / name).relative_to(ROOT).as_posix(), "sha256": digest(case / name)} for name in ("commands.json", "independent-static.json", "independent-native.json", "independent-small.png")}, "manualPngReview": manual_record, "manualPngReviewPassed": manual_pass, "eventFindings": events["findings"]}
        row["jointPassed"] = bool(strict and frozen and current_matches and prompt_matches and read_surface_pass and artifact_matches and authored_reports_pass and independent_pass and manual_pass)
        row["verifiedInitialConfiguration"] = {key: independent_static.get(key) for key in EXPECTED_CONFIGURATION}
        rows.append(row)
        print(json.dumps({key: row[key] for key in ("runId", "strictPassed", "independentNativePassed", "manualPngReviewPassed", "jointPassed")}), flush=True)
    contract_pass = rows[0]["jointPassed"]
    natural_count = sum(row["jointPassed"] for row in rows[1:])
    development = []
    for index in (2, 3):
        run_id = f"gray-20261005-logo-r1-d3-naturalistic-{index}"
        run = ROOT / "evaluations/runs" / run_id
        previous_result = load(run / "evaluation-result.json")
        development.append({"runId": run_id, "accepted": False, "returnCode": previous_result["returnCode"], "piExitCode": previous_result["piExitCode"], "timedOut": previous_result["timedOut"], "durationSeconds": previous_result["durationSeconds"], "rawFileSha256": {name: digest(run / name) for name in ("events.jsonl", "evaluation-result.json", "run-manifest.json", "prompt.md")}})
    report = {"scope": "D3 primary logo builder and Type Orbit native compact check", "runtimeSha256": EXPECTED_RUNTIME, "runtimeFileCount": 296, "currentRuntimeSha256": current_runtime, "currentRuntimeMatches": current_matches, "model": "openai-codex/gpt-5.6-luna", "accepted": contract_pass and natural_count >= 2, "contractJointPassed": contract_pass, "naturalisticJointPassed": natural_count, "naturalisticRepetitions": 3, "runs": rows, "manualReviewFile": str(args.manual_review) if args.manual_review else None, "preservedDevelopmentFailures": development, "failureDisposition": "R2 naturalistic-1 remains strict FAIL after an unnecessary plain-Python Pillow import; later recovery and native success do not count as acceptance."}
    target = ROOT / "evaluations/grayscale-interleave/primary-logo-validation.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("accepted", "contractJointPassed", "naturalisticJointPassed")}), flush=True)
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
