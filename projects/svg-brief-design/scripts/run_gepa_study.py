#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "gepa==0.1.2"]
# ///
"""Use the installed Harbor/GEPA engine with Pi reflection and text-only feedback."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from luna_text_call import call_luna
from gepa_async_bridge import AsyncEvaluatorBridge

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svg-brief-design-gepa-20260925"
ENGINE = Path("/mnt/c/Users/villa/.codex/skills/harbor-evolve-skill/scripts/evolve_skill_with_harbor.py")
EXECUTION = "async-compatible"
FORBIDDEN = re.compile(r'<(?:svg|path|image|polygon|polyline|rect|circle|ellipse|line|g|defs|use)\b|data:image|base64,|vector-\d{3}|p\d{2}-s\d{3}|Fox Rockett|\bd\s*=\s*["\']\s*[Mm]\s*\d|https?://[^\s)>]+\.(?:svg|png|jpe?g|webp)(?:\?|\b)', re.I)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def load_engine():
    spec = importlib.util.spec_from_file_location("svg_gepa_native_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sanitized_development_feedback(trials_directory, agent_name):
    if "development" not in Path(trials_directory).parts:
        raise ValueError("Private feedback cannot enter the reflection adapter")
    trial_dirs = [p.parent for p in Path(trials_directory).glob("*/result.json")]
    if len(trial_dirs) != 1:
        raise ValueError("Expected exactly one terminal development trial")
    trial = trial_dirs[0]
    config = json.loads((trial / "config.json").read_text())
    result = json.loads((trial / "result.json").read_text())
    request = (Path(config["task"]["path"]) / "instruction.md").read_text()
    metrics_path = trial / "verifier/metrics.json"
    metrics = json.loads(metrics_path.read_text()) if metrics_path.is_file() else {}
    allowed_metrics = {key: value for key, value in metrics.items() if key in {
        "artifact_valid", "visual_similarity", "shape_similarity", "style_similarity",
        "chamfer_similarity", "foreground_ssim", "soft_iou", "style_components", "semantic_review_required",
    }}
    artifacts = []
    for path in sorted((trial / "artifacts").rglob("*.svg")):
        try:
            root = ET.fromstring(path.read_bytes())
            elements = Counter(element.tag.rsplit("}", 1)[-1] for element in root.iter())
            actual_text = ["".join(e.itertext()).strip()[:100] for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "text"]
            artifacts.append({"element_counts": dict(elements), "readable_text_elements": actual_text})
        except ET.ParseError:
            artifacts.append({"parse_error": True})
    log = trial / "agent/pi.txt"
    tool_counts = Counter()
    if log.is_file():
        for line in log.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "tool_execution_start":
                tool_counts[event.get("toolName", "unknown")] += 1
    # Only prose requests, scalar verifier evidence, and element counts cross
    # into reflection. No source SVG, path attributes, images, or raw trajectory.
    feedback = {
        "agentTrajectory": json.dumps({"tool_counts": dict(tool_counts), "native_error": bool(result.get("exception_info")), "raw_trajectory_withheld": True}),
        "agentOutput": json.dumps({"general_user_request": request, "generated_structure": artifacts, "svg_source_withheld": True}, ensure_ascii=False),
        "verifierOutput": json.dumps(allowed_metrics),
    }
    write_json(Path(trials_directory).parent / "reflection-feedback.json", {
        "native_result_sha256": digest(trial / "result.json"),
        "metrics_sha256": digest(metrics_path) if metrics_path.is_file() else None,
        "phase": "development", "feedback": feedback, "reference_artwork_shared": False,
    })
    return feedback


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--doctor", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("FOX_PI_AUTH", "/mnt/c/Users/villa/.pi/agent/auth.json")
    module = load_engine()
    config_path = STUDY / f"evolution-{EXECUTION}.json"
    config = module.normalize_config(config_path, None)
    if args.dry_run or args.doctor:
        plan = module.doctor(config) if args.doctor else module.public_plan(config)
        name = "doctor" if args.doctor else "dry-run"
        write_json(STUDY / (EXECUTION + "-" + name + ".json"), plan)
        print(json.dumps({"mode": name, "passed": True, "split_counts": {key: len(value) for key, value in config["splits"].items()}, "missing_env": plan.get("missingRequiredEnv"), "checks": plan.get("checks")}))
        return

    for mode_name in ("dry-run", "doctor"):
        if not (STUDY / (EXECUTION + "-" + mode_name + ".json")).is_file():
            raise ValueError("Run both read-only planning checks before inference")
    protocol = json.loads((STUDY / "protocol.json").read_text())
    for raw_root, expected in protocol["task_files"].items():
        root = Path(raw_root)
        observed = {path.relative_to(root).as_posix(): digest(path) for path in root.rglob("*") if path.is_file()}
        if observed != expected:
            raise ValueError("Task bytes changed since preregistration")
    source = config["baselineSkill"]
    if {p.relative_to(source).as_posix(): digest(p) for p in source.rglob("*") if p.is_file()} != protocol["baseline_files"]:
        raise ValueError("Baseline changed since preregistration")
    original_validation = module.validate_candidate
    metadata = module.parse_skill_frontmatter(config["baselineText"])

    def validate_guidance(text, expected_name):
        original_validation(text, expected_name)
        if module.parse_skill_frontmatter(text) != metadata:
            raise ValueError("The skill frontmatter is frozen in this study")
        if FORBIDDEN.search(text):
            raise ValueError("Candidate contains forbidden artwork, geometry, asset link, or task identifier")
        if len(text.encode()) > 14000 or len(text.splitlines()) > 150:
            raise ValueError("Keep transferable guidance below 150 lines and 14 KB")

    calls = 0

    def reflection(prompt):
        nonlocal calls
        calls += 1
        if calls > protocol["budgets"]["gepa_proposals"]:
            raise ValueError("Declared reflection call cap exhausted")
        if isinstance(prompt, str):
            text = prompt
        else:
            text = "\n\n".join(str(message["role"]) + ":\n" + str(message["content"]) for message in prompt)
        prefix = (
            "You are the reflection component of a skill optimizer. Return the requested complete SKILL.md in one fenced Markdown block. "
            "Preserve its name and description exactly. Write concise English instructions only. Do not include SVG markup, code examples, "
            "path coordinates, task IDs, asset links, reference silhouettes, fixed specimen counts, or memorized task solutions. "
            "Treat all case feedback as evidence to generalize. The skill may cite its existing references/svg-mechanics.md.\n\n"
        )
        evidence_dir = STUDY / "reflection" / f"call-{calls:03d}"
        response, receipt = call_luna(prefix + text, evidence_dir)
        (evidence_dir / "prompt.txt").write_text(prefix + text, encoding="utf-8")
        print(json.dumps({"reflection_call": calls, "model": receipt["model"], "tokens": receipt.get("usage", {}).get("totalTokens")}), flush=True)
        return response

    module.validate_candidate = validate_guidance
    module.collect_trial_evidence = sanitized_development_feedback
    config["gepa"]["reflectionModel"] = reflection
    # GEPA 0.1.2 rejects a custom template together with objective/background.
    # Its standard template retains both declared fields and the callable LM.
    module.REFLECTION_PROMPT = None
    write_json(STUDY / f"{EXECUTION}-execution-seal.json", {
        "created_at": datetime.now(timezone.utc).isoformat(), "config_sha256": digest(config_path),
        "protocol_sha256": digest(STUDY / "protocol.json"), "engine_sha256": digest(ENGINE),
        "adapter_sha256": digest(Path(__file__).with_name("pi_svg_skill_sse.py")),
        "reflection_bridge_sha256": digest(Path(__file__).with_name("luna_text_call.py")),
        "async_bridge_sha256": digest(Path(__file__).with_name("gepa_async_bridge.py")),
        "wrapper_sha256": digest(Path(__file__)),
        "extensions": ["GEPA supported callable reflection through Pi", "stricter text-only candidate validation", "sanitized development-only feedback", "GEPA 0.1.2 standard reflection template with declared objective/background", "Synchronous callback bridges to one stable Harbor asyncio loop"],
        "reward_or_gate_changes": False,
    })
    bridge = AsyncEvaluatorBridge(module.gepa_evaluator)
    module.gepa_evaluator = bridge
    try:
        run = module.run_evolution(config)
        print(json.dumps({"completed": True, "promoted": run["holdout"]["promoted"], "validation_passed": run["validation"]["passed"], "metric_calls": run["gepa"]["metricCalls"], "reflection_calls": calls, "report": str(config["outputDirectory"] / "report.md")}), flush=True)
    except Exception as error:
        write_json(STUDY / f"{EXECUTION}-execution-failure.json", {"exception": type(error).__name__, "message": str(error)[:2000], "reflection_calls": calls, "raw_trials_preserved": True, "automatic_retry": False})
        raise
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
