#!/usr/bin/env python3
"""Independent Harbor verifier for authentic terminal-video artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import shutil
from typing import Any


ANSI_RE = re.compile(
    r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\)|[PX^_].*?\x1b\\)",
    re.DOTALL,
)


def read_json(path: Path, findings: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append(f"{label} missing or invalid: {error}")
        return {}
    if not isinstance(value, dict):
        findings.append(f"{label} must contain one JSON object")
        return {}
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def asciicast_text(path: Path, findings: list[str]) -> tuple[str, dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as error:
        findings.append(f"cast is unreadable: {error}")
        return "", {}
    if not lines:
        findings.append("cast is empty")
        return "", {}
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as error:
        findings.append(f"cast header is invalid: {error}")
        return "", {}
    output: list[str] = []
    for index, line in enumerate(lines[1:], start=2):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            findings.append(f"cast event line {index} is invalid JSON")
            continue
        if isinstance(event, list) and len(event) >= 3 and event[1] == "o":
            output.append(str(event[2]))
    return ANSI_RE.sub("", "".join(output)), header if isinstance(header, dict) else {}


def probe_video(path: Path, findings: list[str]) -> dict[str, Any]:
    executable = media_command("ffprobe")
    command = [
        executable,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,pix_fmt,width,height,avg_frame_rate,nb_frames:format=duration",
        "-of",
        "json",
        media_input_path(path, executable),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        findings.append(f"ffprobe failed to start: {error}")
        return {}
    if completed.returncode != 0:
        findings.append(f"ffprobe exited {completed.returncode}: {completed.stderr.strip()}")
        return {}
    try:
        payload = json.loads(completed.stdout)
        stream = payload["streams"][0]
        duration = float(payload["format"]["duration"])
        numerator, denominator = str(stream["avg_frame_rate"]).split("/", 1)
        frame_rate = float(numerator) / float(denominator)
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
        findings.append(f"ffprobe output is incomplete: {error}")
        return {}
    return {
        "codec_name": stream.get("codec_name"),
        "pix_fmt": stream.get("pix_fmt"),
        "width": int(stream.get("width") or 0),
        "height": int(stream.get("height") or 0),
        "avg_frame_rate": frame_rate,
        "nb_frames": int(stream.get("nb_frames") or 0),
        "duration_seconds": duration,
    }


def frame_sample(path: Path, *, final: bool) -> dict[str, Any]:
    executable = media_command("ffmpeg")
    command = [executable, "-v", "error"]
    if final:
        command.extend(["-sseof", "-0.1"])
    command.extend(
        [
            "-i",
            media_input_path(path, executable),
            "-frames:v",
            "1",
            "-pix_fmt",
            "gray",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    try:
        completed = subprocess.run(command, capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"ok": False, "error": str(error)}
    payload = completed.stdout
    if completed.returncode != 0 or not payload:
        return {
            "ok": False,
            "error": completed.stderr.decode("utf-8", errors="replace")[-500:],
        }
    minimum = min(payload)
    maximum = max(payload)
    mean = sum(payload) / len(payload)
    return {
        "ok": len(set(payload)) >= 4 and maximum - minimum >= 20 and 1.0 < mean < 254.0,
        "byte_count": len(payload),
        "minimum": minimum,
        "maximum": maximum,
        "mean": round(mean, 3),
    }


def nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def executable_basename(value: Any) -> str:
    return str(value or "").replace("\\", "/").rsplit("/", 1)[-1].casefold()


def media_command(name: str) -> str:
    """Resolve native Unix or Windows-interoperability media commands."""
    for candidate in (name, f"{name}.exe"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return name


def media_input_path(path: Path | str, executable: str) -> str:
    """Translate a WSL mount path only for a Windows media executable."""

    value = str(path)
    if executable_basename(executable).endswith(".exe"):
        normalized = value.replace("\\", "/")
        match = re.fullmatch(r"/mnt/([A-Za-z])(?:/(.*))?", normalized)
        if match:
            suffix = (match.group(2) or "").replace("/", "\\")
            return f"{match.group(1).upper()}:\\{suffix}"
    return value


def target_only_presentation_ok(
    manifest: dict[str, Any], validation_checks: set[str]
) -> bool:
    presentation = (
        manifest.get("presentation")
        if isinstance(manifest.get("presentation"), dict)
        else {}
    )
    if not (
        presentation.get("start_at") == "tui-ready"
        and float(presentation.get("trim_leading_seconds") or 0.0) > 0.0
        and float(presentation.get("trim_trailing_seconds") or 0.0) > 0.0
        and float(presentation.get("final_hold_seconds") or 0.0) > 0.0
    ):
        return False
    end_at = presentation.get("end_at")
    if end_at == "tui-exit":
        return float(presentation.get("terminal_restore_seconds") or 0.0) > 0.0
    if end_at == "before-final-key":
        return bool(
            float(presentation.get("final_key_marker_seconds") or 0.0)
            > float(presentation.get("trim_leading_seconds") or 0.0)
            and {
                "before-final-key-marker",
                "before-final-key-presentation",
            }.issubset(validation_checks)
        )
    return False


def select_workspace(contract: dict[str, Any]) -> Path:
    """Prefer a preserved app workspace; use collected artifacts as fallback."""

    candidates: list[Path] = [
        Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    ]
    artifact_dir = os.environ.get("HARBOR_ARTIFACT_DIR")
    if artifact_dir:
        candidates.append(Path(artifact_dir).resolve())

    def available_file_count(candidate: Path) -> int:
        return sum(
            1
            for relative in contract["requiredFiles"]
            if (candidate / relative).is_file()
            and (candidate / relative).stat().st_size > 0
        )

    return max(candidates, key=available_file_count)


def runtime_exit_ok(
    mode: str,
    runtime: dict[str, Any],
    target: dict[str, Any],
    prompt_count: int,
) -> bool:
    if mode == "tui":
        return target.get("final_exit_code") == 0
    steps = runtime.get("steps") if isinstance(runtime.get("steps"), list) else []
    return bool(
        len(steps) == prompt_count
        and all(
            step.get("status") == "passed"
            and step.get("exit_code") in (step.get("expected_exit_codes") or [])
            for step in steps
        )
    )


def effective_validation_checks(validation: dict[str, Any]) -> set[str]:
    checks = set(validation.get("checks") or [])
    if "exit-codes" in checks:
        checks.add("target-exit")
    if float(nested(validation, "presentation", "source_cast_duration_seconds") or 0.0) > 0:
        checks.add("real-time-duration")
    if (
        nested(validation, "presentation", "start_at") == "tui-ready"
        and "before-final-key-presentation" in checks
    ):
        # Older validator builds fully verified the ready-marker trim for this
        # presentation mode but omitted its descriptive check label.
        checks.add("tui-ready-presentation")
    return checks


def verify_complexity_contract(
    contract: dict[str, Any],
    plan: dict[str, Any],
    runtime: dict[str, Any],
    manifest: dict[str, Any],
    findings: list[str],
) -> tuple[bool, dict[str, Any]]:
    """Verify optional long-form and interaction-sequence requirements.

    Version-one contracts omit these fields and therefore remain valid. New
    complex cohorts can independently require authentic source duration,
    explicit dwell time, and exact prompt/text/key sequences.
    """

    plan_steps = plan.get("steps") if isinstance(plan.get("steps"), list) else []
    runtime_steps = (
        runtime.get("steps") if isinstance(runtime.get("steps"), list) else []
    )
    prompts: list[str] = []
    text_actions: list[str] = []
    key_actions: list[str] = []
    action_types: list[str] = []
    pause_seconds = 0.0
    pause_action_count = 0
    runtime_matches_plan = len(runtime_steps) == len(plan_steps)

    for step_index, planned_step in enumerate(plan_steps):
        observed_step = runtime_steps[step_index] if step_index < len(runtime_steps) else {}
        if "prompt" in planned_step:
            prompt = str(planned_step.get("prompt") or "")
            prompts.append(prompt)
            if observed_step.get("prompt_sha256") != sha256_text(prompt):
                runtime_matches_plan = False
            continue

        planned_actions = (
            planned_step.get("actions")
            if isinstance(planned_step.get("actions"), list)
            else []
        )
        observed_actions = (
            observed_step.get("actions")
            if isinstance(observed_step.get("actions"), list)
            else []
        )
        if len(observed_actions) != len(planned_actions):
            runtime_matches_plan = False
        for action_index, planned_action in enumerate(planned_actions):
            action_type = str(planned_action.get("type") or "")
            action_types.append(action_type)
            observed_action = (
                observed_actions[action_index]
                if action_index < len(observed_actions)
                and isinstance(observed_actions[action_index], dict)
                else {}
            )
            if observed_action.get("type") != action_type:
                runtime_matches_plan = False
            if action_type == "text":
                text_value = str(planned_action.get("text") or "")
                text_actions.append(text_value)
                if observed_action.get("text_sha256") != sha256_text(text_value):
                    runtime_matches_plan = False
            elif action_type == "key":
                key_value = str(planned_action.get("key") or "")
                key_actions.append(key_value)
                if observed_action.get("key") != key_value:
                    runtime_matches_plan = False
            elif action_type == "pause":
                seconds = float(planned_action.get("seconds") or 0.0)
                pause_seconds += seconds
                pause_action_count += 1
                try:
                    observed_seconds = float(observed_action.get("seconds"))
                except (TypeError, ValueError):
                    observed_seconds = -1.0
                if not math.isclose(
                    observed_seconds, seconds, rel_tol=0.0, abs_tol=0.001
                ):
                    runtime_matches_plan = False

    requirements = {
        "requiredPromptSequence": contract.get("requiredPromptSequence") or [],
        "requiredTextSequence": contract.get("requiredTextSequence") or [],
        "requiredKeySequence": contract.get("requiredKeySequence") or [],
        "minActionCount": int(contract.get("minActionCount") or 0),
        "minPauseActionCount": int(contract.get("minPauseActionCount") or 0),
        "minPlannedPauseSeconds": float(contract.get("minPlannedPauseSeconds") or 0.0),
        "minSourceDurationSeconds": float(contract.get("minSourceDurationSeconds") or 0.0),
    }
    source_duration = float(
        nested(manifest, "presentation", "source_cast_duration_seconds")
        or nested(manifest, "recording", "duration_seconds")
        or 0.0
    )
    checks = {
        "runtimeMatchesPlan": runtime_matches_plan,
        "promptSequence": prompts == requirements["requiredPromptSequence"]
        if requirements["requiredPromptSequence"]
        else True,
        "textSequence": text_actions == requirements["requiredTextSequence"]
        if requirements["requiredTextSequence"]
        else True,
        "keySequence": key_actions == requirements["requiredKeySequence"]
        if requirements["requiredKeySequence"]
        else True,
        "actionCount": len(action_types) >= requirements["minActionCount"],
        "pauseActionCount": pause_action_count
        >= requirements["minPauseActionCount"],
        "plannedPauseSeconds": pause_seconds
        >= requirements["minPlannedPauseSeconds"],
        "sourceDuration": source_duration
        >= requirements["minSourceDurationSeconds"],
    }
    for name, passed in checks.items():
        if not passed:
            findings.append(f"complex interaction requirement failed: {name}")
    evidence = {
        "requirements": requirements,
        "observed": {
            "prompts": prompts,
            "textSequence": text_actions,
            "keySequence": key_actions,
            "actionTypes": action_types,
            "actionCount": len(action_types),
            "pauseActionCount": pause_action_count,
            "plannedPauseSeconds": round(pause_seconds, 3),
            "sourceDurationSeconds": source_duration,
        },
        "checks": checks,
    }
    return all(checks.values()), evidence


def verify() -> dict[str, Any]:
    contract_path = Path(
        os.environ.get(
            "HARBOR_CONTRACT_PATH", Path(__file__).with_name("contract.json")
        )
    ).resolve()
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    workspace = select_workspace(contract)
    log_dir = Path(
        os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")
    ).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    findings: list[str] = []

    required_paths = [workspace / item for item in contract["requiredFiles"]]
    artifacts_ok = True
    for path in required_paths:
        if not path.is_file() or path.stat().st_size <= 0:
            findings.append(f"required artifact missing or empty: {path.relative_to(workspace)}")
            artifacts_ok = False

    plan_path = workspace / "source" / "session-plan.json"
    cast_path = workspace / "deliverables" / "session.cast"
    mp4_path = workspace / "deliverables" / "session.mp4"
    manifest_path = workspace / "deliverables" / "session.manifest.json"
    runtime_path = workspace / "deliverables" / "session.manifest.runtime.json"
    validation_path = workspace / "deliverables" / "validation.json"

    plan = read_json(plan_path, findings, "plan") if plan_path.is_file() else {}
    manifest = read_json(manifest_path, findings, "manifest") if manifest_path.is_file() else {}
    runtime = read_json(runtime_path, findings, "runtime report") if runtime_path.is_file() else {}
    validation = (
        read_json(validation_path, findings, "independent validation")
        if validation_path.is_file()
        else {}
    )
    cast_text, cast_header = (
        asciicast_text(cast_path, findings) if cast_path.is_file() else ("", {})
    )
    evidence_text = "\n".join(
        [cast_text, json.dumps(runtime, ensure_ascii=False), json.dumps(plan, ensure_ascii=False)]
    ).casefold()

    plan_mode = "tui" if isinstance(plan.get("interaction"), dict) else "argv"
    plan_steps = plan.get("steps") if isinstance(plan.get("steps"), list) else []
    plan_ok = bool(
        plan
        and plan.get("schema_version") == 1
        and plan_mode == contract["mode"]
        and len(plan_steps) == contract["promptCount"]
        and nested(plan, "target", "name") == contract["targetName"]
        and int(nested(plan, "render", "fps") or 0) == contract["fps"]
    )
    if not plan_ok:
        findings.append("session plan does not match the disclosed task contract")

    target = manifest.get("target") if isinstance(manifest.get("target"), dict) else {}
    executable_names = {item.casefold() for item in contract["executableNames"]}
    target_ok = bool(
        target.get("name") == contract["targetName"]
        and executable_basename(target.get("resolved_executable")) in executable_names
        and runtime_exit_ok(
            contract["mode"], runtime, target, contract["promptCount"]
        )
        and target.get("version_exit_code") == 0
        and str(target.get("version_output") or "").strip()
    )
    if not target_ok:
        findings.append("resolved target identity, version, or final exit status is incorrect")

    validation_checks = effective_validation_checks(validation)
    required_checks = set(contract["requiredChecks"])
    validation_exit_ok = runtime_exit_ok(
        contract["mode"], runtime, validation.get("target") or {}, contract["promptCount"]
    )
    validation_ok = bool(
        validation.get("status") == "passed"
        and validation.get("prompt_count") == contract["promptCount"]
        and validation_exit_ok
        and required_checks.issubset(validation_checks)
    )
    if not validation_ok:
        findings.append("independent validation status or required checks are incomplete")

    provenance_ok = artifacts_ok and bool(manifest)
    artifact_map = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}
    for key, path in (
        ("plan", plan_path),
        ("cast", cast_path),
        ("mp4", mp4_path),
        ("runtime_report", runtime_path),
    ):
        record = artifact_map.get(key) if isinstance(artifact_map.get(key), dict) else {}
        if not path.is_file() or record.get("sha256") != sha256_file(path):
            findings.append(f"manifest SHA-256 mismatch: {key}")
            provenance_ok = False
    if nested(manifest, "recording", "input_event_count") != 0:
        findings.append("Asciinema input capture was not zero")
        provenance_ok = False
    if cast_header.get("version") not in {2, 3}:
        findings.append("asciicast header version is unsupported")
        provenance_ok = False

    probe = probe_video(mp4_path, findings) if mp4_path.is_file() else {}
    duration = float(probe.get("duration_seconds") or 0.0)
    media_ok = bool(
        probe
        and probe.get("codec_name") == "h264"
        and probe.get("pix_fmt") == "yuv420p"
        and probe.get("width", 0) > 0
        and probe.get("height", 0) > 0
        and probe.get("width", 0) % 2 == 0
        and probe.get("height", 0) % 2 == 0
        and math.isclose(
            float(probe.get("avg_frame_rate") or 0.0),
            float(contract["fps"]),
            rel_tol=0.0,
            abs_tol=0.01,
        )
        and probe.get("nb_frames", 0) > 0
        and contract["minDurationSeconds"] <= duration <= contract["maxDurationSeconds"]
    )
    if not media_ok:
        findings.append("H.264/yuv420p media contract, timing, or frame rate failed")

    first_frame = frame_sample(mp4_path, final=False) if mp4_path.is_file() else {"ok": False}
    last_frame = frame_sample(mp4_path, final=True) if mp4_path.is_file() else {"ok": False}
    visual_ok = bool(first_frame.get("ok") and last_frame.get("ok"))
    if not visual_ok:
        findings.append("first or final video frame is blank or invalid")

    presentation_ok = True
    if contract["requireTargetOnly"]:
        presentation_ok = target_only_presentation_ok(manifest, validation_checks)
        if not presentation_ok:
            findings.append("target-only TUI presentation evidence is incomplete")

    interaction_ok = True
    if contract["mode"] == "tui":
        runtime_steps = runtime.get("steps") if isinstance(runtime.get("steps"), list) else []
        interaction_ok = bool(
            runtime.get("status") == "passed"
            and runtime.get("mode") == "tui"
            and len(runtime_steps) == contract["promptCount"]
            and nested(runtime, "interaction", "target_status", "exit_code") == 0
            and all(step.get("status") == "passed" for step in runtime_steps)
        )
        if not interaction_ok:
            findings.append("real TUI step/process evidence is incomplete")

    complexity_ok, complexity_evidence = verify_complexity_contract(
        contract, plan, runtime, manifest, findings
    )

    output_ok = True
    for term in contract["requiredCastTerms"]:
        if term.casefold() not in evidence_text:
            findings.append(f"required real terminal evidence is missing: {term}")
            output_ok = False
    for group in contract["anyCastTermGroups"]:
        if not any(term.casefold() in evidence_text for term in group):
            findings.append(f"none of the allowed terminal outcomes appeared: {group}")
            output_ok = False

    rewards = {
        "reward": 1.0
        if all(
            (
                artifacts_ok,
                plan_ok,
                target_ok,
                validation_ok,
                provenance_ok,
                media_ok,
                visual_ok,
                presentation_ok,
                interaction_ok,
                complexity_ok,
                output_ok,
            )
        )
        else 0.0,
        "artifacts": 1.0 if artifacts_ok else 0.0,
        "plan": 1.0 if plan_ok else 0.0,
        "target": 1.0 if target_ok else 0.0,
        "validation": 1.0 if validation_ok else 0.0,
        "provenance": 1.0 if provenance_ok else 0.0,
        "media": 1.0 if media_ok else 0.0,
        "visual": 1.0 if visual_ok else 0.0,
        "presentation": 1.0 if presentation_ok else 0.0,
        "interaction": 1.0 if interaction_ok else 0.0,
        "complexity": 1.0 if complexity_ok else 0.0,
        "output": 1.0 if output_ok else 0.0,
    }
    return {
        "taskId": contract["taskId"],
        "split": contract["split"],
        "caseType": contract["caseType"],
        "ok": rewards["reward"] == 1.0,
        "rewards": rewards,
        "findings": findings,
        "videoProbe": probe,
        "firstFrame": first_frame,
        "lastFrame": last_frame,
        "target": target,
        "validationChecks": sorted(validation_checks),
        "complexityEvidence": complexity_evidence,
        "authorizedMutation": contract["authorizedMutation"],
    }


def main() -> int:
    result = verify()
    log_dir = Path(
        os.environ.get("HARBOR_VERIFIER_LOG_DIR", Path.cwd() / ".harbor-verifier")
    ).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (log_dir / "reward.json").write_text(
        json.dumps(result["rewards"], sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
