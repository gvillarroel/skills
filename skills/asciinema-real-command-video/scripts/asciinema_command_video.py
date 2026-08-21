#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record real prompt-driven CLI sessions with Asciinema and render verified MP4s."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
MARKER_NAMESPACE = "ARCV"
SKILL_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_WORKING_DIRECTORY_TOKEN = "{windows_working_directory}"
SUBST_DRIVE_LETTERS = "ZYXWVUTSRQPONMLKJIHGFED"
NATIVE_WSLPATH = Path("/usr/bin/wslpath")
NATIVE_WSL_GIT = Path("/usr/bin/git")

TOP_LEVEL_FIELDS = {
    "schema_version",
    "title",
    "working_directory",
    "declared_scope",
    "target",
    "terminal",
    "render",
    "steps",
    "interaction",
    "tui_sessions",
}
TOP_LEVEL_REQUIRED_FIELDS = {
    "schema_version",
    "title",
    "working_directory",
    "declared_scope",
    "terminal",
    "render",
}
TARGET_FIELDS = {"name", "executable", "version_args"}
TUI_SESSION_FIELDS = {"id", "target", "interaction", "steps"}
TERMINAL_FIELDS = {"cols", "rows"}
RENDER_FIELDS = {
    "theme",
    "font_size",
    "line_height",
    "fps",
    "speed",
    "idle_time_limit",
    "last_frame_duration",
    "start_at",
    "end_at",
}
RENDER_REQUIRED_FIELDS = RENDER_FIELDS - {"start_at", "end_at"}
TUI_READY_PRESENTATION_MARGIN_SECONDS = 0.15
TUI_EXIT_PRESENTATION_MARGIN_SECONDS = 0.1
ARGV_STEP_FIELDS = {
    "id",
    "prompt",
    "args",
    "timeout_seconds",
    "pause_after_seconds",
    "expected_exit_codes",
}
TUI_STEP_COMMON_FIELDS = {
    "id",
    "timeout_seconds",
    "pause_after_seconds",
    "completion",
}
TUI_PROMPT_STEP_FIELDS = TUI_STEP_COMMON_FIELDS | {"prompt"}
TUI_ACTION_STEP_FIELDS = TUI_STEP_COMMON_FIELDS | {"actions"}
TUI_ACTION_TYPES = {"text", "key", "pause"}
TUI_TEXT_ACTION_FIELDS = {"type", "text"}
TUI_KEY_ACTION_FIELDS = {"type", "key"}
TUI_PAUSE_ACTION_FIELDS = {"type", "seconds"}
TUI_NAMED_KEYS = {
    "Enter",
    "Escape",
    "Tab",
    "BSpace",
    "Space",
    "Up",
    "Down",
    "Left",
    "Right",
    "Home",
    "End",
    "PageUp",
    "PageDown",
}
TUI_INTERACTION_FIELDS = {
    "mode",
    "launch_args",
    "typing_interval_seconds",
    "pre_submit_pause_seconds",
    "startup_timeout_seconds",
    "ready_pattern",
    "busy_pattern",
    "settle_seconds",
    "shutdown_mode",
    "exit_text",
    "exit_timeout_seconds",
    "expected_exit_codes",
}
TUI_INTERACTION_REQUIRED_FIELDS = TUI_INTERACTION_FIELDS - {"shutdown_mode", "exit_text"}

SENSITIVE_PATTERNS = (
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:password|passwd|api[ _-]?key|access[ _-]?token|secret)\b\s*[:=]\s*[\"']?[^\s\"']{8,}"
    ),
)

PINNED_TOOL_ASSETS: dict[tuple[str, str], dict[str, dict[str, Any]]] = {
    ("linux", "x86_64"): {
        "asciinema": {
            "version": "3.2.1",
            "url": "https://github.com/asciinema/asciinema/releases/download/v3.2.1/asciinema-x86_64-unknown-linux-gnu",
            "sha256": "1b405bbda565b33c3c4718de67fedc3535580603c0694b1ff3fb04f363430a20",
            "size": 7_983_848,
        },
        "agg": {
            "version": "1.9.0",
            "url": "https://github.com/asciinema/agg/releases/download/v1.9.0/agg-x86_64-unknown-linux-gnu",
            "sha256": "f111e315cd71056b116302342553dd765b7297579ed511f111d0cedb442aeda6",
            "size": 15_904_064,
        },
    },
    ("linux", "aarch64"): {
        "asciinema": {
            "version": "3.2.1",
            "url": "https://github.com/asciinema/asciinema/releases/download/v3.2.1/asciinema-aarch64-unknown-linux-gnu",
            "sha256": "b516a6d896844c0ffbc96e0a55afe4cbcc79216abde0fc64fdda4e39bee421ea",
            "size": 7_138_888,
        },
        "agg": {
            "version": "1.9.0",
            "url": "https://github.com/asciinema/agg/releases/download/v1.9.0/agg-aarch64-unknown-linux-gnu",
            "sha256": "2b4be407b97e00e1c313a41d154ced8fa3d02c560c8f47a0db4950a2576444c9",
            "size": 13_797_992,
        },
    },
    ("darwin", "x86_64"): {
        "asciinema": {
            "version": "3.2.1",
            "url": "https://github.com/asciinema/asciinema/releases/download/v3.2.1/asciinema-x86_64-apple-darwin",
            "sha256": "1b388af0e1566ab19deea663b0ce64730ad46ade2825fadd43cc88f0bd28140a",
            "size": 7_411_548,
        },
        "agg": {
            "version": "1.9.0",
            "url": "https://github.com/asciinema/agg/releases/download/v1.9.0/agg-x86_64-apple-darwin",
            "sha256": "1462150b611d231d2950d10a676303eaeb1019ff330735882aaae09b52e2e1c1",
            "size": 15_075_896,
        },
    },
    ("darwin", "aarch64"): {
        "asciinema": {
            "version": "3.2.1",
            "url": "https://github.com/asciinema/asciinema/releases/download/v3.2.1/asciinema-aarch64-apple-darwin",
            "sha256": "1f0c76da7855601df93e5dccdf69b7c683b81beff1411e38b3802de1f5fc7a1c",
            "size": 6_845_888,
        },
        "agg": {
            "version": "1.9.0",
            "url": "https://github.com/asciinema/agg/releases/download/v1.9.0/agg-aarch64-apple-darwin",
            "sha256": "742b2b6230529b72f310acb835e9479496000f2eabc97b0993cabe1d7fe70171",
            "size": 13_754_592,
        },
    },
}


class CommandVideoError(RuntimeError):
    """Raised when a plan, command, recording, or artifact violates the contract."""


@dataclass(frozen=True)
class LoadedPlan:
    path: Path
    data: dict[str, Any]
    sha256: str
    working_directory: Path


@dataclass(frozen=True)
class PreflightContext:
    env: dict[str, str]
    tools_dir: Path | None
    asciinema: Path
    agg: Path
    tmux: Path | None
    ffmpeg: Path
    ffprobe: Path
    target: Path
    targets: list[Path]
    pty_allocator: Path | None
    toolchain: dict[str, Any]
    terminal_control: dict[str, Any]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256_bytes(encoded)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CommandVideoError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except CommandVideoError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise CommandVideoError(f"Could not read JSON from {path}: {exc}") from exc


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def require_exact_fields(
    value: Any,
    *,
    label: str,
    allowed: set[str],
    required: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CommandVideoError(f"{label} must be a JSON object")
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CommandVideoError(f"{label} has unknown fields: {', '.join(unknown)}")
    missing = sorted((required or allowed) - set(value))
    if missing:
        raise CommandVideoError(f"{label} is missing fields: {', '.join(missing)}")
    return value


def require_string(value: Any, *, label: str, maximum: int = 10_000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CommandVideoError(f"{label} must be a non-empty string")
    if len(value) > maximum:
        raise CommandVideoError(f"{label} exceeds {maximum} characters")
    if "\x00" in value or "\x1b" in value:
        raise CommandVideoError(f"{label} contains a forbidden control character")
    return value


def require_number(
    value: Any, *, label: str, minimum: float, maximum: float, integer: bool = False
) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CommandVideoError(f"{label} must be a number")
    if integer and not isinstance(value, int):
        raise CommandVideoError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise CommandVideoError(f"{label} must be between {minimum} and {maximum}")
    return value


def validate_prompt_safety(prompt: str, *, label: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(prompt):
            raise CommandVideoError(
                f"{label} appears to contain a credential or secret; redact it before recording"
            )


def normalize_working_directory(plan_path: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = plan_path.parent / candidate
    candidate = candidate.resolve()
    if not candidate.is_dir():
        raise CommandVideoError(f"working_directory does not exist: {candidate}")
    return candidate


def validate_exit_codes(value: Any, *, label: str) -> list[int]:
    if not isinstance(value, list) or not value:
        raise CommandVideoError(f"{label} must be a non-empty list")
    if len(set(value)) != len(value):
        raise CommandVideoError(f"{label} contains duplicates")
    for code in value:
        if isinstance(code, bool) or not isinstance(code, int) or not -255 <= code <= 255:
            raise CommandVideoError(f"{label} values must be integers from -255 to 255")
    return value


def tui_shutdown_mode(plan: LoadedPlan | Mapping[str, Any]) -> str:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    interaction = data.get("interaction", {})
    if not isinstance(interaction, Mapping):
        return "exit-text"
    return str(interaction.get("shutdown_mode", "exit-text"))


def final_tui_shutdown_mode(plan: LoadedPlan | Mapping[str, Any]) -> str:
    sessions = plan_tui_sessions(plan)
    if sessions:
        return tui_shutdown_mode(sessions[-1])
    return tui_shutdown_mode(plan)


def tui_step_completion(step: Mapping[str, Any]) -> str:
    return str(step.get("completion", "ready"))


def tui_step_input_sha256(step: Mapping[str, Any]) -> str:
    if "prompt" in step:
        return sha256_text(str(step["prompt"]))
    return sha256_json(step.get("actions", []))


def is_tui_mode(mode: str) -> bool:
    return mode in {"tui", "tui-sequence"}


def plan_tui_sessions(
    plan: LoadedPlan | Mapping[str, Any],
) -> list[dict[str, Any]]:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    declared = data.get("tui_sessions")
    if isinstance(declared, list):
        return [dict(session) for session in declared if isinstance(session, Mapping)]
    interaction = data.get("interaction")
    if isinstance(interaction, Mapping) and interaction.get("mode") == "tui":
        return [
            {
                "id": "primary",
                "target": data["target"],
                "interaction": interaction,
                "steps": data["steps"],
            }
        ]
    return []


def plan_steps(plan: LoadedPlan | Mapping[str, Any]) -> list[dict[str, Any]]:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    sessions = plan_tui_sessions(data)
    if sessions:
        return [dict(step) for session in sessions for step in session["steps"]]
    steps = data.get("steps", [])
    return [dict(step) for step in steps if isinstance(step, Mapping)]


def plan_targets(plan: LoadedPlan | Mapping[str, Any]) -> list[dict[str, Any]]:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    sessions = plan_tui_sessions(data)
    if sessions:
        return [dict(session["target"]) for session in sessions]
    target = data.get("target")
    return [dict(target)] if isinstance(target, Mapping) else []


def loaded_tui_session(plan: LoadedPlan, session: Mapping[str, Any]) -> LoadedPlan:
    data = {
        key: value
        for key, value in plan.data.items()
        if key not in {"tui_sessions", "target", "interaction", "steps"}
    }
    data.update(
        {
            "target": session["target"],
            "interaction": session["interaction"],
            "steps": session["steps"],
        }
    )
    return LoadedPlan(
        path=plan.path,
        data=data,
        sha256=plan.sha256,
        working_directory=plan.working_directory,
    )


def select_tui_session_plan(
    plan: LoadedPlan, session_id: str | None
) -> tuple[str, LoadedPlan]:
    sessions = plan_tui_sessions(plan)
    if not sessions:
        raise CommandVideoError("The plan does not declare a TUI session")
    if plan_mode(plan) == "tui-sequence":
        if session_id is None:
            raise CommandVideoError("A TUI sequence target requires --session-id")
        matches = [session for session in sessions if session["id"] == session_id]
        if len(matches) != 1:
            raise CommandVideoError(f"Unknown TUI session id: {session_id}")
        return session_id, loaded_tui_session(plan, matches[0])
    if session_id not in {None, "primary"}:
        raise CommandVideoError("A single-target TUI plan only accepts session id 'primary'")
    return "primary", loaded_tui_session(plan, sessions[0])


def validate_tui_key(key: Any, *, label: str) -> str:
    key_value = require_string(key, label=label, maximum=32)
    if len(key_value) == 1 and key_value.isprintable() and not key_value.isspace():
        return key_value
    if key_value in TUI_NAMED_KEYS or re.fullmatch(r"C-[a-z]", key_value):
        return key_value
    raise CommandVideoError(
        f"{label} must be one printable character, a supported named key, or C-a through C-z"
    )


def validate_tui_actions(value: Any, *, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not 1 <= len(value) <= 64:
        raise CommandVideoError(f"{label} must contain between 1 and 64 actions")
    actions: list[dict[str, Any]] = []
    for index, raw_action in enumerate(value):
        action_label = f"{label}[{index}]"
        if not isinstance(raw_action, dict):
            raise CommandVideoError(f"{action_label} must be a JSON object")
        action_type = require_string(
            raw_action.get("type"), label=f"{action_label}.type", maximum=20
        )
        if action_type not in TUI_ACTION_TYPES:
            raise CommandVideoError(
                f"{action_label}.type must be 'text', 'key', or 'pause'"
            )
        if action_type == "text":
            action = require_exact_fields(
                raw_action,
                label=action_label,
                allowed=TUI_TEXT_ACTION_FIELDS,
                required=TUI_TEXT_ACTION_FIELDS,
            )
            text_value = require_string(
                action["text"], label=f"{action_label}.text", maximum=100_000
            )
            if "\n" in text_value or "\r" in text_value:
                raise CommandVideoError(f"{action_label}.text must be single-line")
            validate_prompt_safety(text_value, label=f"{action_label}.text")
        elif action_type == "key":
            action = require_exact_fields(
                raw_action,
                label=action_label,
                allowed=TUI_KEY_ACTION_FIELDS,
                required=TUI_KEY_ACTION_FIELDS,
            )
            validate_tui_key(action["key"], label=f"{action_label}.key")
        else:
            action = require_exact_fields(
                raw_action,
                label=action_label,
                allowed=TUI_PAUSE_ACTION_FIELDS,
                required=TUI_PAUSE_ACTION_FIELDS,
            )
            require_number(
                action["seconds"],
                label=f"{action_label}.seconds",
                minimum=0.05,
                maximum=30.0,
            )
        actions.append(action)
    return actions


def plan_mode(plan: LoadedPlan | Mapping[str, Any]) -> str:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    if isinstance(data.get("tui_sessions"), list):
        return "tui-sequence"
    interaction = data.get("interaction")
    return "tui" if isinstance(interaction, dict) and interaction.get("mode") == "tui" else "argv"


def render_start_at(plan: LoadedPlan | Mapping[str, Any]) -> str:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    render = data.get("render", {})
    return str(render.get("start_at", "recording")) if isinstance(render, Mapping) else "recording"


def render_end_at(plan: LoadedPlan | Mapping[str, Any]) -> str:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    render = data.get("render", {})
    return str(render.get("end_at", "target-exit")) if isinstance(render, Mapping) else "target-exit"


def tui_ready_presentation_lead_seconds(plan: LoadedPlan | Mapping[str, Any]) -> float:
    data = plan.data if isinstance(plan, LoadedPlan) else plan
    sessions = plan_tui_sessions(data)
    interaction = sessions[0]["interaction"] if sessions else data.get("interaction", {})
    if not isinstance(interaction, Mapping):
        raise CommandVideoError("TUI-ready presentation requires an interaction object")
    settle_seconds = float(interaction.get("settle_seconds", 0.0))
    return min(0.75, settle_seconds) + TUI_READY_PRESENTATION_MARGIN_SECONDS


def validate_plan_data(plan_path: Path, data: Any) -> LoadedPlan:
    plan = require_exact_fields(
        data,
        label="plan",
        allowed=TOP_LEVEL_FIELDS,
        required=TOP_LEVEL_REQUIRED_FIELDS,
    )
    if plan["schema_version"] != SCHEMA_VERSION:
        raise CommandVideoError(
            f"schema_version must be {SCHEMA_VERSION}, got {plan['schema_version']!r}"
        )
    require_string(plan["title"], label="title", maximum=200)
    working_value = require_string(
        plan["working_directory"], label="working_directory", maximum=4096
    )
    require_string(plan["declared_scope"], label="declared_scope", maximum=2000)

    if "tui_sessions" in plan:
        conflicting = sorted(set(plan) & {"target", "interaction", "steps"})
        if conflicting:
            raise CommandVideoError(
                "tui_sessions cannot be combined with top-level " + ", ".join(conflicting)
            )
        sessions = plan["tui_sessions"]
        if not isinstance(sessions, list) or not 2 <= len(sessions) <= 8:
            raise CommandVideoError("tui_sessions must contain between 2 and 8 TUI sessions")
        seen_session_ids: set[str] = set()
        seen_step_ids: set[str] = set()
        executable_identities: set[str] = set()
        for session_index, raw_session in enumerate(sessions):
            session_label = f"tui_sessions[{session_index}]"
            session = require_exact_fields(
                raw_session,
                label=session_label,
                allowed=TUI_SESSION_FIELDS,
                required=TUI_SESSION_FIELDS,
            )
            session_id = require_string(
                session["id"], label=f"{session_label}.id", maximum=63
            )
            if not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", session_id
            ):
                raise CommandVideoError(
                    f"{session_label}.id must be lowercase hyphen-case"
                )
            if session_id in seen_session_ids:
                raise CommandVideoError(f"Duplicate TUI session id: {session_id}")
            seen_session_ids.add(session_id)
            if not isinstance(session.get("target"), dict):
                raise CommandVideoError(f"{session_label}.target must be a JSON object")
            executable_identity = str(session["target"].get("executable", "")).casefold()
            if executable_identity:
                executable_identities.add(executable_identity)
            session_steps = session.get("steps")
            if isinstance(session_steps, list):
                for raw_step in session_steps:
                    if not isinstance(raw_step, dict):
                        continue
                    step_id = raw_step.get("id")
                    if isinstance(step_id, str):
                        if step_id in seen_step_ids:
                            raise CommandVideoError(
                                f"Duplicate step id across TUI sessions: {step_id}"
                            )
                        seen_step_ids.add(step_id)

            session_render = dict(plan["render"]) if isinstance(plan.get("render"), dict) else plan.get("render")
            if (
                isinstance(session_render, dict)
                and session_index < len(sessions) - 1
                and session_render.get("end_at", "target-exit") == "before-final-key"
            ):
                session_render["end_at"] = "target-exit"
            synthetic = {
                "schema_version": plan["schema_version"],
                "title": f"{plan['title']} — {session_id}",
                "working_directory": plan["working_directory"],
                "declared_scope": plan["declared_scope"],
                "target": session["target"],
                "terminal": plan["terminal"],
                "render": session_render,
                "steps": session["steps"],
                "interaction": session["interaction"],
            }
            validate_plan_data(plan_path, synthetic)
        if len(executable_identities) < 2:
            raise CommandVideoError(
                "tui_sessions must declare at least two distinct target executables"
            )
        resolved_plan_path = plan_path.resolve()
        working_directory = normalize_working_directory(
            resolved_plan_path, working_value
        )
        return LoadedPlan(
            path=resolved_plan_path,
            data=plan,
            sha256=sha256_file(resolved_plan_path),
            working_directory=working_directory,
        )

    missing_legacy = sorted({"target", "steps"} - set(plan))
    if missing_legacy:
        raise CommandVideoError(
            "Single-target plans are missing fields: " + ", ".join(missing_legacy)
        )

    target = require_exact_fields(
        plan["target"], label="target", allowed=TARGET_FIELDS, required=TARGET_FIELDS
    )
    require_string(target["name"], label="target.name", maximum=200)
    require_string(target["executable"], label="target.executable", maximum=4096)
    version_args = target["version_args"]
    if not isinstance(version_args, list) or not version_args:
        raise CommandVideoError("target.version_args must be a non-empty argv array")
    for index, item in enumerate(version_args):
        require_string(item, label=f"target.version_args[{index}]", maximum=4096)
        if "{prompt}" in item or "{run_id}" in item:
            raise CommandVideoError("target.version_args cannot contain placeholders")

    terminal = require_exact_fields(
        plan["terminal"],
        label="terminal",
        allowed=TERMINAL_FIELDS,
        required=TERMINAL_FIELDS,
    )
    require_number(terminal["cols"], label="terminal.cols", minimum=40, maximum=240, integer=True)
    require_number(terminal["rows"], label="terminal.rows", minimum=10, maximum=100, integer=True)

    render = require_exact_fields(
        plan["render"],
        label="render",
        allowed=RENDER_FIELDS,
        required=RENDER_REQUIRED_FIELDS,
    )
    require_string(render["theme"], label="render.theme", maximum=1000)
    require_number(render["font_size"], label="render.font_size", minimum=8, maximum=40, integer=True)
    require_number(render["line_height"], label="render.line_height", minimum=1.0, maximum=2.5)
    require_number(render["fps"], label="render.fps", minimum=1, maximum=60, integer=True)
    require_number(render["speed"], label="render.speed", minimum=0.1, maximum=10.0)
    if render["idle_time_limit"] is not None:
        require_number(
            render["idle_time_limit"],
            label="render.idle_time_limit",
            minimum=0.1,
            maximum=60.0,
        )
    require_number(
        render["last_frame_duration"],
        label="render.last_frame_duration",
        minimum=0.0,
        maximum=30.0,
    )
    start_at = render.get("start_at", "recording")
    if start_at not in {"recording", "tui-ready"}:
        raise CommandVideoError("render.start_at must be 'recording' or 'tui-ready'")
    end_at = render.get("end_at", "target-exit")
    if end_at not in {"target-exit", "before-final-key"}:
        raise CommandVideoError(
            "render.end_at must be 'target-exit' or 'before-final-key'"
        )

    mode = "argv"
    interaction = plan.get("interaction")
    if interaction is not None:
        interaction = require_exact_fields(
            interaction,
            label="interaction",
            allowed=TUI_INTERACTION_FIELDS,
            required=TUI_INTERACTION_REQUIRED_FIELDS,
        )
        if interaction["mode"] != "tui":
            raise CommandVideoError("interaction.mode must be 'tui'")
        mode = "tui"
        launch_args = interaction["launch_args"]
        if not isinstance(launch_args, list) or len(launch_args) > 128:
            raise CommandVideoError("interaction.launch_args must be an argv array with at most 128 items")
        for index, item in enumerate(launch_args):
            if not isinstance(item, str) or "\x00" in item or "\n" in item or "\r" in item:
                raise CommandVideoError(
                    f"interaction.launch_args[{index}] must be a single-line string"
                )
            if "{prompt}" in item:
                raise CommandVideoError(
                    "interaction.launch_args cannot contain {prompt}; TUI prompts are typed"
                )
        if any(WINDOWS_WORKING_DIRECTORY_TOKEN in item for item in launch_args):
            executable_name = str(target["executable"]).lower()
            if not executable_name.endswith(".exe"):
                raise CommandVideoError(
                    f"{WINDOWS_WORKING_DIRECTORY_TOKEN} is only valid for a native Windows .exe target"
                )
        require_number(
            interaction["typing_interval_seconds"],
            label="interaction.typing_interval_seconds",
            minimum=0.005,
            maximum=1.0,
        )
        require_number(
            interaction["pre_submit_pause_seconds"],
            label="interaction.pre_submit_pause_seconds",
            minimum=0.0,
            maximum=10.0,
        )
        require_number(
            interaction["startup_timeout_seconds"],
            label="interaction.startup_timeout_seconds",
            minimum=1,
            maximum=600,
            integer=True,
        )
        ready_pattern = require_string(
            interaction["ready_pattern"], label="interaction.ready_pattern", maximum=1000
        )
        busy_pattern = require_string(
            interaction["busy_pattern"], label="interaction.busy_pattern", maximum=1000
        )
        for pattern_label, pattern_value in (
            ("interaction.ready_pattern", ready_pattern),
            ("interaction.busy_pattern", busy_pattern),
        ):
            try:
                re.compile(pattern_value)
            except re.error as exc:
                raise CommandVideoError(f"{pattern_label} is invalid: {exc}") from exc
        require_number(
            interaction["settle_seconds"],
            label="interaction.settle_seconds",
            minimum=0.25,
            maximum=10.0,
        )
        shutdown_mode = interaction.get("shutdown_mode", "exit-text")
        if shutdown_mode not in {"exit-text", "target-exit"}:
            raise CommandVideoError(
                "interaction.shutdown_mode must be 'exit-text' or 'target-exit'"
            )
        if shutdown_mode == "exit-text":
            if "exit_text" not in interaction:
                raise CommandVideoError(
                    "interaction.exit_text is required when shutdown_mode is 'exit-text'"
                )
            exit_text = require_string(
                interaction["exit_text"], label="interaction.exit_text", maximum=200
            )
            if "\n" in exit_text or "\r" in exit_text:
                raise CommandVideoError("interaction.exit_text must be single-line")
            validate_prompt_safety(exit_text, label="interaction.exit_text")
        elif "exit_text" in interaction:
            raise CommandVideoError(
                "interaction.exit_text must be omitted when shutdown_mode is 'target-exit'"
            )
        require_number(
            interaction["exit_timeout_seconds"],
            label="interaction.exit_timeout_seconds",
            minimum=1,
            maximum=600,
            integer=True,
        )
        validate_exit_codes(
            interaction["expected_exit_codes"], label="interaction.expected_exit_codes"
        )
        if float(render["speed"]) != 1.0 or render["idle_time_limit"] is not None:
            raise CommandVideoError(
                "TUI recordings require render.speed 1.0 and idle_time_limit null to preserve real timing"
            )
    if start_at == "tui-ready" and mode != "tui":
        raise CommandVideoError("render.start_at 'tui-ready' requires TUI interaction mode")
    if end_at == "before-final-key" and mode != "tui":
        raise CommandVideoError("render.end_at 'before-final-key' requires TUI interaction mode")

    steps = plan["steps"]
    if not isinstance(steps, list) or not 1 <= len(steps) <= 50:
        raise CommandVideoError("steps must contain between 1 and 50 interaction steps")
    seen_ids: set[str] = set()
    for index, raw_step in enumerate(steps):
        label = f"steps[{index}]"
        if mode == "tui":
            if not isinstance(raw_step, dict):
                raise CommandVideoError(f"{label} must be a JSON object")
            has_prompt = "prompt" in raw_step
            has_actions = "actions" in raw_step
            if has_prompt == has_actions:
                raise CommandVideoError(
                    f"{label} must contain exactly one of prompt or actions"
                )
            step_fields = TUI_PROMPT_STEP_FIELDS if has_prompt else TUI_ACTION_STEP_FIELDS
            step = require_exact_fields(
                raw_step,
                label=label,
                allowed=step_fields,
                required=step_fields - {"completion"},
            )
        else:
            step = require_exact_fields(
                raw_step,
                label=label,
                allowed=ARGV_STEP_FIELDS,
                required=ARGV_STEP_FIELDS,
            )
        step_id = require_string(step["id"], label=f"{label}.id", maximum=63)
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", step_id):
            raise CommandVideoError(f"{label}.id must be lowercase hyphen-case")
        if step_id in seen_ids:
            raise CommandVideoError(f"Duplicate step id: {step_id}")
        seen_ids.add(step_id)

        if mode == "tui":
            completion = tui_step_completion(step)
            if completion not in {"ready", "target-exit"}:
                raise CommandVideoError(
                    f"{label}.completion must be 'ready' or 'target-exit'"
                )
            if "prompt" in step:
                prompt = require_string(
                    step["prompt"], label=f"{label}.prompt", maximum=100_000
                )
                validate_prompt_safety(prompt, label=f"{label}.prompt")
                if "\n" in prompt or "\r" in prompt:
                    raise CommandVideoError(
                        f"{label}.prompt must be single-line for timed TUI typing"
                    )
                if completion != "ready":
                    raise CommandVideoError(
                        f"{label}.prompt uses implicit Enter and must complete at 'ready'; "
                        "use explicit actions for a target-exit step"
                    )
            else:
                actions = validate_tui_actions(step["actions"], label=f"{label}.actions")
                if completion == "ready" and not any(
                    action["type"] == "key" for action in actions
                ):
                    raise CommandVideoError(
                        f"{label}.actions with ready completion must deliver at least one key"
                    )
        else:
            prompt = require_string(
                step["prompt"], label=f"{label}.prompt", maximum=100_000
            )
            validate_prompt_safety(prompt, label=f"{label}.prompt")
            args = step["args"]
            if not isinstance(args, list) or not args or len(args) > 128:
                raise CommandVideoError(f"{label}.args must be an argv array with 1 to 128 items")
            prompt_placeholders = 0
            for arg_index, item in enumerate(args):
                if not isinstance(item, str):
                    raise CommandVideoError(f"{label}.args[{arg_index}] must be a string")
                if "\x00" in item or "\n" in item or "\r" in item:
                    raise CommandVideoError(
                        f"{label}.args[{arg_index}] contains a forbidden character"
                    )
                prompt_placeholders += item.count("{prompt}")
            if prompt_placeholders != 1:
                raise CommandVideoError(f"{label}.args must contain {{prompt}} exactly once")

        require_number(
            step["timeout_seconds"],
            label=f"{label}.timeout_seconds",
            minimum=1,
            maximum=86_400,
            integer=True,
        )
        require_number(
            step["pause_after_seconds"],
            label=f"{label}.pause_after_seconds",
            minimum=0.0,
            maximum=30.0,
        )
        if mode == "argv":
            validate_exit_codes(
                step["expected_exit_codes"], label=f"{label}.expected_exit_codes"
            )

    if mode == "tui":
        target_exit_steps = [
            index
            for index, step in enumerate(steps)
            if tui_step_completion(step) == "target-exit"
        ]
        shutdown_mode = str(interaction.get("shutdown_mode", "exit-text"))
        if shutdown_mode == "target-exit":
            if target_exit_steps != [len(steps) - 1]:
                raise CommandVideoError(
                    "shutdown_mode 'target-exit' requires exactly the final step to use "
                    "completion 'target-exit'"
                )
        elif target_exit_steps:
            raise CommandVideoError(
                "completion 'target-exit' requires interaction.shutdown_mode 'target-exit'"
            )
        if end_at == "before-final-key":
            final_step = steps[-1]
            final_actions = final_step.get("actions")
            if (
                shutdown_mode != "target-exit"
                or not isinstance(final_actions, list)
                or not final_actions
                or final_actions[-1].get("type") != "key"
            ):
                raise CommandVideoError(
                    "render.end_at 'before-final-key' requires a target-exit action plan "
                    "whose final action is a key"
                )
            if float(render["last_frame_duration"]) <= 0:
                raise CommandVideoError(
                    "render.end_at 'before-final-key' requires a positive last_frame_duration"
                )

    resolved_plan_path = plan_path.resolve()
    working_directory = normalize_working_directory(resolved_plan_path, working_value)
    return LoadedPlan(
        path=resolved_plan_path,
        data=plan,
        sha256=sha256_file(resolved_plan_path),
        working_directory=working_directory,
    )


def load_plan(path_value: str | Path) -> LoadedPlan:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise CommandVideoError(f"Plan does not exist: {path}")
    return validate_plan_data(path, load_json(path))


def plan_summary(plan: LoadedPlan) -> dict[str, Any]:
    mode = plan_mode(plan)
    steps = plan_steps(plan)
    sessions = plan_tui_sessions(plan)
    step_summaries = [
        {
            "id": step["id"],
            "input_kind": "prompt" if "prompt" in step else "actions",
            "input_sha256": tui_step_input_sha256(step),
            "prompt_sha256": (
                sha256_text(step["prompt"]) if "prompt" in step else None
            ),
            "actions": (
                [
                    {
                        "type": action["type"],
                        "sha256": sha256_json(action),
                    }
                    for action in step.get("actions", [])
                ]
                or None
            ),
            "completion": (
                tui_step_completion(step) if is_tui_mode(mode) else "process-exit"
            ),
            "args_template": step.get("args"),
            "timeout_seconds": step["timeout_seconds"],
        }
        for step in steps
    ]
    return {
        "status": "passed",
        "schema_version": SCHEMA_VERSION,
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "title": plan.data["title"],
        "working_directory": str(plan.working_directory),
        "declared_scope": plan.data["declared_scope"],
        "target": plan.data.get("target"),
        "targets": plan_targets(plan),
        "mode": mode,
        "interaction": plan.data.get("interaction"),
        "tui_session_count": len(sessions),
        "tui_sessions": [
            {
                "id": session["id"],
                "target": session["target"],
                "step_ids": [step["id"] for step in session["steps"]],
            }
            for session in sessions
        ],
        "terminal": plan.data["terminal"],
        "render": plan.data["render"],
        "prompt_count": len(steps),
        "text_prompt_count": sum("prompt" in step for step in steps),
        "action_count": sum(len(step.get("actions", [])) for step in steps),
        "steps": step_summaries,
    }


def path_with_tools(env: Mapping[str, str], tools_dir: Path | None) -> str:
    current = env.get("PATH", "")
    if tools_dir is None:
        return current
    return str(tools_dir.resolve()) + os.pathsep + current


def resolve_executable(name: str, *, working_directory: Path, path_value: str) -> Path:
    has_separator = any(separator in name for separator in ("/", "\\"))
    if has_separator or Path(name).is_absolute():
        candidate = Path(name).expanduser()
        if not candidate.is_absolute():
            candidate = working_directory / candidate
        candidate = candidate.resolve()
        if not candidate.is_file():
            raise CommandVideoError(f"Executable does not exist: {candidate}")
    else:
        resolved = shutil.which(name, path=path_value)
        if resolved is None:
            raise CommandVideoError(f"Executable is not available on PATH: {name}")
        candidate = Path(resolved).resolve()
    if os.name != "nt" and not os.access(candidate, os.X_OK):
        raise CommandVideoError(f"File is not executable: {candidate}")
    return candidate


def command_output(
    argv: Sequence[str], *, cwd: Path, env: Mapping[str, str], timeout: int = 30
) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=str(cwd),
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CommandVideoError(f"Could not run {argv[0]}: {exc}") from exc
    return completed.returncode, completed.stdout[:32_768]


def expanded_step_argv(
    executable: Path, args: Sequence[str], prompt: str, run_id: str
) -> list[str]:
    return [str(executable)] + [
        item.replace("{prompt}", prompt).replace("{run_id}", run_id) for item in args
    ]


def displayed_step_argv(
    executable: Path, args: Sequence[str], prompt: str, run_id: str
) -> list[str]:
    prompt_label = f"<PROMPT sha256={sha256_text(prompt)[:16]}...>"
    expanded = [str(executable)] + [
        item.replace("{prompt}", prompt_label).replace("{run_id}", run_id) for item in args
    ]
    return [
        item
        if len(item) <= 120
        else f"<ARG chars={len(item)} sha256={sha256_text(item)[:16]}...>"
        for item in expanded
    ]


def marker(run_id: str, *parts: str) -> str:
    return "::" + "::".join((MARKER_NAMESPACE, run_id, *parts)) + "::"


def emit_hidden_marker(run_id: str, *parts: str) -> None:
    """Keep machine evidence in the cast while hiding it from the rendered terminal."""
    sys.stdout.write(f"\033]0;{marker(run_id, *parts)}\007")
    sys.stdout.flush()


def terminate_process(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        try:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except OSError:
            pass


def launch_args_request_windows_working_directory(args: Sequence[str]) -> bool:
    return any(WINDOWS_WORKING_DIRECTORY_TOKEN in item for item in args)


def plan_targets_lazygit(plan: LoadedPlan | Mapping[str, Any]) -> bool:
    for target in plan_targets(plan):
        if "lazygit" in str(target.get("name", "")).lower() or "lazygit" in str(
            target.get("executable", "")
        ).lower():
            return True
    return False


def plan_has_bridged_lazygit(plan: LoadedPlan | Mapping[str, Any]) -> bool:
    for session in plan_tui_sessions(plan):
        target = session["target"]
        if not (
            "lazygit" in str(target.get("name", "")).lower()
            or "lazygit" in str(target.get("executable", "")).lower()
        ):
            continue
        if launch_args_request_windows_working_directory(
            session["interaction"]["launch_args"]
        ):
            return True
    return False


def expanded_launch_argv(
    executable: Path,
    args: Sequence[str],
    run_id: str,
    *,
    windows_working_directory: str | None = None,
) -> list[str]:
    if launch_args_request_windows_working_directory(args) and windows_working_directory is None:
        raise CommandVideoError(
            f"Launch arguments require {WINDOWS_WORKING_DIRECTORY_TOKEN}, but no verified Windows path bridge is active"
        )
    expanded: list[str] = [str(executable)]
    for item in args:
        value = item.replace("{run_id}", run_id)
        if windows_working_directory is not None:
            value = value.replace(
                WINDOWS_WORKING_DIRECTORY_TOKEN, windows_working_directory
            )
        expanded.append(value)
    return expanded


def resolve_windows_path_bridge_helpers(
    *, working_directory: Path, env: Mapping[str, str]
) -> tuple[Path, Path]:
    if not is_wsl():
        raise CommandVideoError(
            f"{WINDOWS_WORKING_DIRECTORY_TOKEN} requires WSL2 with Windows interoperability"
        )
    path_value = env.get("PATH", "")
    native_wslpath = NATIVE_WSLPATH
    if not native_wslpath.is_file() or not os.access(native_wslpath, os.X_OK):
        raise CommandVideoError(
            f"{WINDOWS_WORKING_DIRECTORY_TOKEN} requires the native WSL helper /usr/bin/wslpath"
        )
    # Preserve the wslpath argv[0] dispatch name. Resolving its /init symlink
    # makes WSL interpret "-w" as an /init argument instead of a path mode.
    wslpath = native_wslpath
    subst = resolve_executable(
        "subst.exe", working_directory=working_directory, path_value=path_value
    )
    return wslpath, subst


def windows_path_bridge_preflight(
    *, working_directory: Path, target: Path | None, env: Mapping[str, str]
) -> dict[str, Any]:
    if target is not None and target.suffix.lower() != ".exe":
        raise CommandVideoError(
            f"{WINDOWS_WORKING_DIRECTORY_TOKEN} requires a native Windows .exe target"
        )
    wslpath, subst = resolve_windows_path_bridge_helpers(
        working_directory=working_directory, env=env
    )
    code, windows_path = command_output(
        [str(wslpath), "-w", str(working_directory)],
        cwd=working_directory,
        env=env,
    )
    windows_path = windows_path.strip()
    if code != 0 or not re.fullmatch(r"[A-Za-z]:\\.*", windows_path):
        raise CommandVideoError(
            f"Could not translate the TUI working directory to a Windows path: {windows_path or 'no output'}"
        )
    list_code, _ = command_output(
        [str(subst)], cwd=working_directory, env=env
    )
    if list_code != 0:
        raise CommandVideoError("subst.exe could not enumerate Windows drive mappings")
    return {
        "mode": "temporary-subst-drive",
        "token": WINDOWS_WORKING_DIRECTORY_TOKEN,
        "source_working_directory": str(working_directory),
        "windows_source_path": windows_path,
        "wslpath": str(wslpath),
        "wslpath_sha256": sha256_file(wslpath),
        "subst": str(subst),
        "subst_sha256": sha256_file(subst),
        "candidate_drive_count": len(SUBST_DRIVE_LETTERS),
    }


def lazygit_longpaths_preflight(
    *, working_directory: Path, env: Mapping[str, str]
) -> dict[str, Any]:
    native_git = NATIVE_WSL_GIT
    if not native_git.is_file() or not os.access(native_git, os.X_OK):
        raise CommandVideoError(
            "Native Windows lazygit path bridging requires /usr/bin/git for project-local checks"
        )
    code, output = command_output(
        [
            str(native_git),
            "-C",
            str(working_directory),
            "config",
            "--local",
            "--bool",
            "core.longpaths",
        ],
        cwd=working_directory,
        env=env,
    )
    if code != 0 or output.strip().lower() != "true":
        raise CommandVideoError(
            "Before recording lazygit.exe through the Windows path bridge, set "
            "core.longpaths=true in that repository's local Git config"
        )
    return {
        "status": "passed",
        "scope": "project-local",
        "setting": "core.longpaths",
        "value": True,
        "git": str(native_git),
        "git_sha256": sha256_file(native_git),
    }


def acquire_windows_working_directory_bridge(
    *, working_directory: Path, env: Mapping[str, str], run_id: str
) -> dict[str, Any]:
    preflight = windows_path_bridge_preflight(
        working_directory=working_directory,
        target=None,
        env=env,
    )
    subst = Path(preflight["subst"])
    windows_path = str(preflight["windows_source_path"])
    failure_details: list[str] = []
    for letter in SUBST_DRIVE_LETTERS:
        drive = f"{letter}:"
        lock_path = Path(tempfile.gettempdir()) / (
            f"asciinema-real-command-video-subst-{letter.lower()}.lock"
        )
        descriptor: int | None = None
        mapping_created = False
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            continue
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                descriptor = None
                handle.write(run_id + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            completed = subprocess.run(
                [str(subst), drive, windows_path],
                cwd=str(working_directory),
                env=dict(env),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            if completed.returncode == 0:
                mapping_created = True
                return {
                    **preflight,
                    "status": "active",
                    "created": True,
                    "released": False,
                    "drive": drive,
                    "mount_root": f"{drive}/",
                    "create_exit_code": completed.returncode,
                    "_lock_path": str(lock_path),
                }
            detail = completed.stdout.strip()
            failure_details.append(f"{drive}={completed.returncode}:{detail[:160]}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            failure_details.append(f"{drive}:{exc}")
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if not mapping_created and lock_path.exists():
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
    detail = "; ".join(failure_details[-3:]) or "no candidate drive was available"
    raise CommandVideoError(f"Could not create a temporary Windows path bridge: {detail}")


def release_windows_working_directory_bridge(
    bridge: Mapping[str, Any], *, working_directory: Path, env: Mapping[str, str]
) -> dict[str, Any]:
    subst = Path(str(bridge["subst"]))
    drive = str(bridge["drive"])
    lock_path = Path(str(bridge["_lock_path"]))
    exit_code: int | None = None
    detail = ""
    try:
        completed = subprocess.run(
            [str(subst), drive, "/d"],
            cwd=str(working_directory),
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
        exit_code = completed.returncode
        detail = completed.stdout.strip()[:512]
    except (OSError, subprocess.TimeoutExpired) as exc:
        detail = str(exc)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
    return {
        "released": exit_code == 0,
        "release_exit_code": exit_code,
        "release_output": detail,
    }


def tmux_run(
    tmux: Path,
    server_name: str,
    args: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    check: bool = False,
    timeout: float = 10.0,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            [str(tmux), "-L", server_name, *args],
            cwd=str(cwd),
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CommandVideoError(f"tmux command failed: {exc}") from exc
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise CommandVideoError(
            f"tmux {' '.join(args[:2])} exited with {completed.returncode}: {detail}"
        )
    return completed


def tmux_capture_pane(
    tmux: Path,
    server_name: str,
    session_name: str,
    *,
    cwd: Path,
    env: Mapping[str, str],
) -> str:
    completed = tmux_run(
        tmux,
        server_name,
        ["capture-pane", "-p", "-J", "-t", session_name],
        cwd=cwd,
        env=env,
        check=True,
    )
    return completed.stdout.replace("\r\n", "\n").replace("\r", "\n")


def tmux_send_literal(
    tmux: Path,
    server_name: str,
    session_name: str,
    text: str,
    *,
    interval_seconds: float,
    cwd: Path,
    env: Mapping[str, str],
) -> None:
    for character in text:
        tmux_run(
            tmux,
            server_name,
            ["send-keys", "-l", "-t", session_name, "--", character],
            cwd=cwd,
            env=env,
            check=True,
        )
        time.sleep(interval_seconds)


def tmux_send_key(
    tmux: Path,
    server_name: str,
    session_name: str,
    key: str,
    *,
    cwd: Path,
    env: Mapping[str, str],
) -> None:
    tmux_run(
        tmux,
        server_name,
        ["send-keys", "-t", session_name, key],
        cwd=cwd,
        env=env,
        check=True,
    )


def screen_matches_ready(screen: str, ready_pattern: str) -> bool:
    return re.search(ready_pattern, screen) is not None


def screen_matches_busy(screen: str, busy_pattern: str) -> bool:
    return re.search(busy_pattern, screen) is not None


def wait_for_ready_screen(
    tmux: Path,
    server_name: str,
    session_name: str,
    *,
    ready_pattern: str,
    busy_pattern: str,
    timeout_seconds: float,
    settle_seconds: float,
    baseline: str | None,
    cwd: Path,
    env: Mapping[str, str],
) -> str:
    deadline = time.monotonic() + timeout_seconds
    ready_since: float | None = None
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            screen = tmux_capture_pane(
                tmux, server_name, session_name, cwd=cwd, env=env
            )
            last_error = None
        except CommandVideoError as exc:
            last_error = str(exc)
            time.sleep(0.1)
            continue
        changed = baseline is None or screen != baseline
        if (
            changed
            and screen_matches_ready(screen, ready_pattern)
            and not screen_matches_busy(screen, busy_pattern)
        ):
            if ready_since is None:
                ready_since = time.monotonic()
            elif time.monotonic() - ready_since >= settle_seconds:
                return screen
        else:
            ready_since = None
        time.sleep(0.1)
    detail = f"; last tmux error: {last_error}" if last_error else ""
    raise CommandVideoError(
        f"TUI did not return to its ready prompt within {timeout_seconds} seconds{detail}"
    )


def bounded_screen_snapshot(screen: str, *, maximum: int = 200_000) -> str:
    return screen if len(screen) <= maximum else screen[-maximum:]


def wait_for_target_status(
    target_status_path: Path,
    tmux: Path,
    server_name: str,
    session_name: str,
    *,
    timeout_seconds: float,
    initial_screen: str,
    cwd: Path,
    env: Mapping[str, str],
) -> tuple[dict[str, Any], str]:
    deadline = time.monotonic() + timeout_seconds
    last_screen = initial_screen
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            last_screen = tmux_capture_pane(
                tmux, server_name, session_name, cwd=cwd, env=env
            )
            last_error = None
        except CommandVideoError as exc:
            last_error = str(exc)
        if target_status_path.is_file():
            target_status = load_json(target_status_path)
            if not isinstance(target_status, dict) or target_status.get("status") != "passed":
                raise CommandVideoError("TUI target status report did not pass")
            return target_status, last_screen
        time.sleep(0.05)
    detail = f"; last tmux error: {last_error}" if last_error else ""
    raise CommandVideoError(
        f"TUI target did not exit within {timeout_seconds} seconds{detail}"
    )


def execute_tui_action_step(
    step: Mapping[str, Any],
    *,
    index: int,
    interaction: Mapping[str, Any],
    target_status_path: Path,
    run_id: str,
    tmux: Path,
    server_name: str,
    session_name: str,
    hold_before_final_key: bool,
    cwd: Path,
    env: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    started_at = utc_now()
    started_monotonic = time.monotonic()
    starting_screen = tmux_capture_pane(
        tmux, server_name, session_name, cwd=cwd, env=env
    )
    last_screen = starting_screen
    completion_baseline = starting_screen
    action_reports: list[dict[str, Any]] = []
    total_typing_elapsed = 0.0
    total_keystrokes = 0
    enter_submitted = False
    emit_hidden_marker(run_id, "STEP", str(step["id"]), "BEGIN")
    for action_index, action in enumerate(step["actions"], start=1):
        action_type = str(action["type"])
        action_digest = sha256_json(action)
        action_started = time.monotonic()
        emit_hidden_marker(
            run_id,
            "ACTION",
            str(step["id"]),
            str(action_index),
            "BEGIN",
            action_type.upper(),
            action_digest,
        )
        report: dict[str, Any] = {
            "index": action_index,
            "type": action_type,
            "action_sha256": action_digest,
        }
        if action_type == "text":
            text_value = str(action["text"])
            text_hash = sha256_text(text_value)
            emit_hidden_marker(
                run_id, "TYPING", str(step["id"]), str(action_index), "BEGIN", text_hash
            )
            typing_started = time.monotonic()
            tmux_send_literal(
                tmux,
                server_name,
                session_name,
                text_value,
                interval_seconds=float(interaction["typing_interval_seconds"]),
                cwd=cwd,
                env=env,
            )
            typing_elapsed = time.monotonic() - typing_started
            total_typing_elapsed += typing_elapsed
            total_keystrokes += len(text_value)
            last_screen = tmux_capture_pane(
                tmux, server_name, session_name, cwd=cwd, env=env
            )
            if text_value not in last_screen:
                raise CommandVideoError(
                    f"TUI did not visibly echo action text before the next key: {step['id']}"
                )
            emit_hidden_marker(
                run_id, "TYPING", str(step["id"]), str(action_index), "END", text_hash
            )
            report.update(
                {
                    "text_sha256": text_hash,
                    "keystroke_count": len(text_value),
                    "typing_elapsed_seconds": round(typing_elapsed, 6),
                    "visible_before_next_key": True,
                    "screen_sha256": sha256_text(last_screen),
                    "screen": bounded_screen_snapshot(last_screen),
                }
            )
        elif action_type == "key":
            key_value = str(action["key"])
            completion_baseline = last_screen
            if hold_before_final_key and action_index == len(step["actions"]):
                emit_hidden_marker(run_id, "TUI", "FINAL-KEY")
            if key_value == "Enter":
                enter_submitted = True
                emit_hidden_marker(run_id, "SUBMIT", str(step["id"]), "ENTER")
            else:
                emit_hidden_marker(run_id, "KEY", str(step["id"]), key_value)
            tmux_send_key(
                tmux,
                server_name,
                session_name,
                key_value,
                cwd=cwd,
                env=env,
            )
            total_keystrokes += 1
            report["key"] = key_value
        else:
            seconds = float(action["seconds"])
            time.sleep(seconds)
            report["seconds"] = seconds
        report["elapsed_seconds"] = round(time.monotonic() - action_started, 6)
        action_reports.append(report)
        emit_hidden_marker(
            run_id,
            "ACTION",
            str(step["id"]),
            str(action_index),
            "END",
            action_type.upper(),
            action_digest,
        )

    completion = tui_step_completion(step)
    target_status: dict[str, Any] | None = None
    if completion == "ready":
        completion_screen = wait_for_ready_screen(
            tmux,
            server_name,
            session_name,
            ready_pattern=str(interaction["ready_pattern"]),
            busy_pattern=str(interaction["busy_pattern"]),
            timeout_seconds=float(step["timeout_seconds"]),
            settle_seconds=float(interaction["settle_seconds"]),
            baseline=completion_baseline,
            cwd=cwd,
            env=env,
        )
        ready_after = screen_matches_ready(
            completion_screen, str(interaction["ready_pattern"])
        )
        busy_after = screen_matches_busy(
            completion_screen, str(interaction["busy_pattern"])
        )
        target_exited = False
    else:
        target_status, completion_screen = wait_for_target_status(
            target_status_path,
            tmux,
            server_name,
            session_name,
            timeout_seconds=float(step["timeout_seconds"]),
            initial_screen=last_screen,
            cwd=cwd,
            env=env,
        )
        ready_after = False
        busy_after = False
        target_exited = True

    elapsed = time.monotonic() - started_monotonic
    step_report = {
        "id": step["id"],
        "index": index,
        "status": "passed",
        "input_kind": "actions",
        "input_sha256": tui_step_input_sha256(step),
        "completion": completion,
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "typing_elapsed_seconds": round(total_typing_elapsed, 6),
        "typing_method": "tmux-send-keys",
        "keystroke_count": total_keystrokes,
        "enter_submitted": enter_submitted,
        "action_count": len(action_reports),
        "actions": action_reports,
        "completion_screen": bounded_screen_snapshot(completion_screen),
        "completion_screen_sha256": sha256_text(completion_screen),
        "ready_after_response": ready_after,
        "busy_after_response": busy_after,
        "target_exited_after_actions": target_exited,
    }
    exit_code = target_status.get("exit_code") if target_status else 0
    emit_hidden_marker(run_id, "STEP", str(step["id"]), "END", str(exit_code))
    return step_report, target_status


def execute_tui_target(
    plan: LoadedPlan,
    *,
    status_path: Path,
    gate_path: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
    session_id: str | None = None,
    final_hold_seconds: float | None = None,
) -> int:
    selected_session_id, plan = select_tui_session_plan(plan, session_id)
    runtime_env = dict(env or os.environ)
    status: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "run_id": run_id,
        "session_id": selected_session_id,
        "started_at_utc": utc_now(),
    }
    return_code = 2
    windows_bridge: dict[str, Any] | None = None
    try:
        if plan_mode(plan) != "tui":
            raise CommandVideoError("run-tui-target requires a TUI interaction plan")
        deadline = time.monotonic() + 30.0
        while not gate_path.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not gate_path.exists():
            raise CommandVideoError("TUI recording client did not open the start gate")
        target = plan.data["target"]
        target_path = resolve_executable(
            target["executable"],
            working_directory=plan.working_directory,
            path_value=runtime_env.get("PATH", ""),
        )
        interaction = plan.data["interaction"]
        windows_working_directory: str | None = None
        if launch_args_request_windows_working_directory(interaction["launch_args"]):
            windows_bridge = acquire_windows_working_directory_bridge(
                working_directory=plan.working_directory,
                env=runtime_env,
                run_id=run_id,
            )
            windows_working_directory = str(windows_bridge["mount_root"])
            status["windows_working_directory_bridge"] = {
                key: value
                for key, value in windows_bridge.items()
                if not key.startswith("_")
            }
        argv = expanded_launch_argv(
            target_path,
            interaction["launch_args"],
            run_id,
            windows_working_directory=windows_working_directory,
        )
        if "copilot" in target["name"].lower() or "copilot" in target["executable"].lower():
            if runtime_env.get("COPILOT_ALLOW_ALL", "").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                raise CommandVideoError(
                    "COPILOT_ALLOW_ALL is enabled; refuse unattended TUI recording without explicit narrow permissions"
                )
        status.update(
            {
                "resolved_executable": str(target_path),
                "executable_sha256": sha256_file(target_path),
                "launch_argv": argv,
                "launch_argv_sha256": sha256_bytes("\x00".join(argv).encode("utf-8")),
            }
        )
        process = subprocess.Popen(
            argv,
            cwd=str(plan.working_directory),
            env=runtime_env,
            stdin=None,
            stdout=None,
            stderr=None,
        )
        return_code = process.wait()
        status["exit_code"] = return_code
        status["status"] = "passed"
        configured_hold = (
            float(plan.data["render"]["last_frame_duration"])
            if final_hold_seconds is None
            else float(final_hold_seconds)
        )
        status["final_hold_seconds"] = configured_hold
        if configured_hold > 0:
            time.sleep(configured_hold)
    except Exception as exc:
        status["error"] = str(exc)
    finally:
        if windows_bridge is not None:
            release = release_windows_working_directory_bridge(
                windows_bridge,
                working_directory=plan.working_directory,
                env=runtime_env,
            )
            status["windows_working_directory_bridge"].update(release)
            status["windows_working_directory_bridge"]["status"] = (
                "released" if release["released"] else "release-failed"
            )
            if not release["released"]:
                status["status"] = "failed"
                status["error"] = (
                    "The temporary Windows path bridge could not be released: "
                    f"{release['release_output']}"
                )
                return_code = 2
        status["finished_at_utc"] = utc_now()
        write_json_atomic(status_path.resolve(), status)
    return return_code


def execute_tui_sequence_targets(
    plan: LoadedPlan,
    *,
    state_directory: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
) -> int:
    if plan_mode(plan) != "tui-sequence":
        raise CommandVideoError("run-tui-sequence-targets requires a TUI sequence plan")
    state_root = state_directory.resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    sessions = plan_tui_sessions(plan)
    for index, session in enumerate(sessions):
        session_id = str(session["id"])
        status_path = state_root / f"{index:02d}-{session_id}.status.json"
        gate_path = state_root / f"{index:02d}-{session_id}.gate"
        return_code = execute_tui_target(
            plan,
            status_path=status_path,
            gate_path=gate_path,
            run_id=run_id,
            env=env,
            session_id=session_id,
            final_hold_seconds=(
                float(plan.data["render"]["last_frame_duration"])
                if index == len(sessions) - 1
                else 0.0
            ),
        )
        status = load_json(status_path)
        expected = session["interaction"]["expected_exit_codes"]
        if (
            return_code not in expected
            or not isinstance(status, dict)
            or status.get("status") != "passed"
            or status.get("exit_code") not in expected
        ):
            return 1
    return 0


def automate_tui_session(
    session_plan: LoadedPlan,
    *,
    session_id: str,
    runtime_target: dict[str, Any],
    runtime_interaction: dict[str, Any],
    runtime_steps: list[dict[str, Any]],
    target_status_path: Path,
    run_id: str,
    tmux: Path,
    server_name: str,
    session_name: str,
    cwd: Path,
    env: Mapping[str, str],
    emit_primary_ready: bool,
    hold_before_final_key: bool,
    emit_final_target_exit: bool,
) -> dict[str, Any]:
    interaction = session_plan.data["interaction"]
    emit_hidden_marker(run_id, "TUI-SESSION", session_id, "BEGIN")
    ready_screen = wait_for_ready_screen(
        tmux,
        server_name,
        session_name,
        ready_pattern=interaction["ready_pattern"],
        busy_pattern=interaction["busy_pattern"],
        timeout_seconds=interaction["startup_timeout_seconds"],
        settle_seconds=min(0.75, float(interaction["settle_seconds"])),
        baseline=None,
        cwd=cwd,
        env=env,
    )
    runtime_interaction["startup_ready_screen_sha256"] = sha256_text(ready_screen)
    runtime_interaction["startup_ready_at_utc"] = utc_now()
    emit_hidden_marker(run_id, "TUI-SESSION", session_id, "READY")
    if emit_primary_ready:
        emit_hidden_marker(run_id, "TUI", "READY")

    target_status: dict[str, Any] | None = None
    for index, step in enumerate(session_plan.data["steps"], start=1):
        if "actions" in step:
            step_report, observed_target_status = execute_tui_action_step(
                step,
                index=index,
                interaction=interaction,
                target_status_path=target_status_path,
                run_id=run_id,
                tmux=tmux,
                server_name=server_name,
                session_name=session_name,
                hold_before_final_key=(
                    hold_before_final_key
                    and index == len(session_plan.data["steps"])
                ),
                cwd=cwd,
                env=env,
            )
            runtime_steps.append(step_report)
            if observed_target_status is not None:
                target_status = observed_target_status
        else:
            prompt = step["prompt"]
            prompt_hash = sha256_text(prompt)
            started_at = utc_now()
            started_monotonic = time.monotonic()
            emit_hidden_marker(run_id, "STEP", step["id"], "BEGIN")
            emit_hidden_marker(run_id, "TYPING", step["id"], "BEGIN", prompt_hash)
            typing_started = time.monotonic()
            tmux_send_literal(
                tmux,
                server_name,
                session_name,
                prompt,
                interval_seconds=float(interaction["typing_interval_seconds"]),
                cwd=cwd,
                env=env,
            )
            typing_elapsed = time.monotonic() - typing_started
            pre_submit_pause = float(interaction["pre_submit_pause_seconds"])
            if pre_submit_pause:
                time.sleep(pre_submit_pause)
            typed_screen = tmux_capture_pane(
                tmux,
                server_name,
                session_name,
                cwd=cwd,
                env=env,
            )
            if prompt not in typed_screen:
                raise CommandVideoError(
                    f"TUI did not visibly echo the exact prompt before Enter: {step['id']}"
                )
            emit_hidden_marker(run_id, "TYPING", step["id"], "END", prompt_hash)
            emit_hidden_marker(run_id, "SUBMIT", step["id"], "ENTER")
            tmux_send_key(
                tmux,
                server_name,
                session_name,
                "Enter",
                cwd=cwd,
                env=env,
            )
            submitted_at = utc_now()
            response_screen = wait_for_ready_screen(
                tmux,
                server_name,
                session_name,
                ready_pattern=interaction["ready_pattern"],
                busy_pattern=interaction["busy_pattern"],
                timeout_seconds=step["timeout_seconds"],
                settle_seconds=interaction["settle_seconds"],
                baseline=typed_screen,
                cwd=cwd,
                env=env,
            )
            elapsed = time.monotonic() - started_monotonic
            runtime_steps.append(
                {
                    "id": step["id"],
                    "index": index,
                    "status": "passed",
                    "input_kind": "prompt",
                    "input_sha256": prompt_hash,
                    "completion": "ready",
                    "started_at_utc": started_at,
                    "submitted_at_utc": submitted_at,
                    "finished_at_utc": utc_now(),
                    "elapsed_seconds": round(elapsed, 6),
                    "typing_elapsed_seconds": round(typing_elapsed, 6),
                    "typing_method": "tmux-send-keys",
                    "keystroke_count": len(prompt),
                    "submit_key": "Enter",
                    "prompt_sha256": prompt_hash,
                    "typed_screen_sha256": sha256_text(typed_screen),
                    "response_screen_sha256": sha256_text(response_screen),
                    "prompt_visible_before_submit": True,
                    "ready_after_response": screen_matches_ready(
                        response_screen, interaction["ready_pattern"]
                    ),
                    "busy_after_response": screen_matches_busy(
                        response_screen, interaction["busy_pattern"]
                    ),
                    "typed_screen": bounded_screen_snapshot(typed_screen),
                    "response_screen": bounded_screen_snapshot(response_screen),
                }
            )
            emit_hidden_marker(run_id, "STEP", step["id"], "END", "0")
        pause = float(step["pause_after_seconds"])
        if pause:
            time.sleep(pause)

    if tui_shutdown_mode(session_plan) == "exit-text":
        emit_hidden_marker(run_id, "TUI-SESSION", session_id, "EXIT", "BEGIN")
        tmux_send_literal(
            tmux,
            server_name,
            session_name,
            interaction["exit_text"],
            interval_seconds=float(interaction["typing_interval_seconds"]),
            cwd=cwd,
            env=env,
        )
        if interaction["pre_submit_pause_seconds"]:
            time.sleep(float(interaction["pre_submit_pause_seconds"]))
        tmux_send_key(
            tmux,
            server_name,
            session_name,
            "Enter",
            cwd=cwd,
            env=env,
        )
        emit_hidden_marker(run_id, "TUI-SESSION", session_id, "EXIT", "ENTER")
        target_status, _ = wait_for_target_status(
            target_status_path,
            tmux,
            server_name,
            session_name,
            timeout_seconds=float(interaction["exit_timeout_seconds"]),
            initial_screen=ready_screen,
            cwd=cwd,
            env=env,
        )
    elif target_status is None:
        raise CommandVideoError(
            f"TUI session {session_id} completed without a target status report"
        )
    assert target_status is not None
    target_exit_code = target_status.get("exit_code")
    runtime_target["final_exit_code"] = target_exit_code
    runtime_interaction["target_status"] = target_status
    if target_exit_code not in interaction["expected_exit_codes"]:
        raise CommandVideoError(
            f"TUI session {session_id} exited with {target_exit_code}; "
            f"expected {interaction['expected_exit_codes']}"
        )
    emit_hidden_marker(
        run_id, "TUI-SESSION", session_id, "EXIT", str(target_exit_code)
    )
    if emit_final_target_exit:
        emit_hidden_marker(run_id, "TARGET", "EXIT", str(target_exit_code))
    return target_status


def execute_tui_plan(
    plan: LoadedPlan,
    *,
    report_path: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
    require_asciinema_session: bool = True,
    require_tty: bool = True,
) -> int:
    runtime_env = dict(env or os.environ)
    tmux_env = dict(runtime_env)
    tmux_env.pop("TMUX", None)
    asciinema_session = runtime_env.get("ASCIINEMA_SESSION", "")
    tty_state = {
        "stdin": bool(getattr(sys.stdin, "isatty", lambda: False)()),
        "stdout": bool(getattr(sys.stdout, "isatty", lambda: False)()),
        "stderr": bool(getattr(sys.stderr, "isatty", lambda: False)()),
    }
    base_report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "mode": "tui",
        "run_id": run_id,
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "started_at_utc": utc_now(),
        "working_directory": str(plan.working_directory),
        "asciinema_session": asciinema_session,
        "tty": tty_state,
        "target": {},
        "interaction": {},
        "steps": [],
    }
    report_path = report_path.resolve()
    gate_path = report_path.with_name(f".{report_path.stem}.{run_id}.tui-gate")
    target_status_path = report_path.with_name(
        f".{report_path.stem}.{run_id}.tui-target.json"
    )
    server_name = f"arcv-{run_id.replace('-', '')[:20]}"
    session_name = "recording"
    tmux: Path | None = None
    worker: threading.Thread | None = None
    worker_state: dict[str, Any] = {}
    return_code = 2
    try:
        uuid.UUID(run_id)
        if require_asciinema_session and not asciinema_session:
            raise CommandVideoError(
                "ASCIINEMA_SESSION is missing; the plan is not running inside Asciinema"
            )
        if require_tty and not all(tty_state.values()):
            raise CommandVideoError(
                "The TUI runner requires a real PTY on stdin, stdout, and stderr"
            )
        if gate_path.exists() or target_status_path.exists():
            raise CommandVideoError("Temporary TUI evidence paths already exist")

        target = plan.data["target"]
        target_path = resolve_executable(
            target["executable"],
            working_directory=plan.working_directory,
            path_value=runtime_env.get("PATH", ""),
        )
        target_digest = sha256_file(target_path)
        version_argv = [str(target_path), *target["version_args"]]
        version_code, version_output = command_output(
            version_argv, cwd=plan.working_directory, env=runtime_env
        )
        if version_code != 0:
            raise CommandVideoError(
                f"Target version command exited with {version_code}: {shlex.join(version_argv)}"
            )
        tmux_requested = runtime_env.get("ASCIINEMA_TMUX", "tmux")
        tmux = resolve_executable(
            tmux_requested,
            working_directory=plan.working_directory,
            path_value=runtime_env.get("PATH", ""),
        )
        tmux_code, tmux_version = command_output(
            [str(tmux), "-V"], cwd=plan.working_directory, env=tmux_env
        )
        if tmux_code != 0:
            raise CommandVideoError("tmux version check failed")
        base_report["target"] = {
            "name": target["name"],
            "requested_executable": target["executable"],
            "resolved_executable": str(target_path),
            "executable_sha256": target_digest,
            "version_argv": version_argv,
            "version_exit_code": version_code,
            "version_output": version_output,
        }
        interaction = plan.data["interaction"]
        base_report["interaction"] = {
            "mode": "tui",
            "input_delivery": "tmux-send-keys",
            "action_model": "prompt-or-explicit-actions",
            "shutdown_mode": tui_shutdown_mode(plan),
            "submit_key": (
                "Enter" if all("prompt" in step for step in plan.data["steps"]) else "per-step"
            ),
            "typing_interval_seconds": interaction["typing_interval_seconds"],
            "pre_submit_pause_seconds": interaction["pre_submit_pause_seconds"],
            "ready_pattern_sha256": sha256_text(interaction["ready_pattern"]),
            "busy_pattern_sha256": sha256_text(interaction["busy_pattern"]),
            "tmux": {
                "requested": tmux_requested,
                "resolved_executable": str(tmux),
                "executable_sha256": sha256_file(tmux),
                "version_output": tmux_version.strip(),
                "isolated_server": server_name,
                "session": session_name,
            },
        }

        print("\033[2J\033[H", end="")
        emit_hidden_marker(run_id, "RUN", "BEGIN")
        print(f"REAL INTERACTIVE TUI SESSION: {plan.data['title']}")
        print(f"Target: {target['name']}")
        print(f"Executable: {target_path}")
        print(f"Executable SHA-256: {target_digest[:16]}... (full value in manifest)")
        print("Version command output:")
        print(version_output.rstrip())
        print(f"Declared scope: {plan.data['declared_scope']}")
        print("Input method: reviewed timed text and explicit PTY key actions")
        print(f"Plan SHA-256: {plan.sha256[:16]}... (full value in manifest)", flush=True)
        emit_hidden_marker(run_id, "IDENTITY", "END")
        time.sleep(0.75)

        wrapper_argv = [
            sys.executable,
            str(Path(__file__).resolve()),
            "run-tui-target",
            "--plan",
            str(plan.path),
            "--status",
            str(target_status_path),
            "--gate",
            str(gate_path),
            "--run-id",
            run_id,
        ]
        terminal = plan.data["terminal"]
        tmux_run(
            tmux,
            server_name,
            [
                "-f",
                "/dev/null",
                "new-session",
                "-d",
                "-x",
                str(terminal["cols"]),
                "-y",
                str(terminal["rows"]),
                "-s",
                session_name,
                shlex.join(wrapper_argv),
            ],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )
        tmux_run(
            tmux,
            server_name,
            ["set-option", "-g", "history-limit", "100000"],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )
        tmux_run(
            tmux,
            server_name,
            ["set-option", "-g", "status", "off"],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )

        def automate_tui() -> None:
            try:
                client_deadline = time.monotonic() + 15.0
                while time.monotonic() < client_deadline:
                    clients = tmux_run(
                        tmux,
                        server_name,
                        ["list-clients", "-F", "#{client_session}"],
                        cwd=plan.working_directory,
                        env=tmux_env,
                    )
                    if clients.returncode == 0 and session_name in clients.stdout.splitlines():
                        break
                    time.sleep(0.05)
                else:
                    raise CommandVideoError("tmux client did not attach to the recording session")
                gate_path.write_text(run_id + "\n", encoding="utf-8")
                automate_tui_session(
                    plan,
                    session_id="primary",
                    runtime_target=base_report["target"],
                    runtime_interaction=base_report["interaction"],
                    runtime_steps=base_report["steps"],
                    target_status_path=target_status_path,
                    run_id=run_id,
                    tmux=tmux,
                    server_name=server_name,
                    session_name=session_name,
                    cwd=plan.working_directory,
                    env=tmux_env,
                    emit_primary_ready=True,
                    hold_before_final_key=(render_end_at(plan) == "before-final-key"),
                    emit_final_target_exit=True,
                )
                emit_hidden_marker(run_id, "RUN", "END", "0")
                base_report["status"] = "passed"
                worker_state["return_code"] = 0
            except Exception as exc:
                base_report["status"] = "failed"
                base_report["error"] = str(exc)
                worker_state["error"] = str(exc)
                worker_state["return_code"] = 1
                emit_hidden_marker(run_id, "RUN", "END", "1")
                tmux_run(
                    tmux,
                    server_name,
                    ["kill-server"],
                    cwd=plan.working_directory,
                    env=tmux_env,
                )

        worker = threading.Thread(target=automate_tui, name="tui-automation", daemon=True)
        worker.start()
        attach = subprocess.run(
            [str(tmux), "-L", server_name, "attach-session", "-t", session_name],
            cwd=str(plan.working_directory),
            env=tmux_env,
            stdin=None,
            stdout=None,
            stderr=None,
            check=False,
        )
        base_report["interaction"]["tmux_attach_exit_code"] = attach.returncode
        worker.join(timeout=5.0)
        if worker.is_alive():
            raise CommandVideoError("TUI automation did not finish after tmux detached")
        return_code = int(worker_state.get("return_code", 1))
        if return_code != 0 and worker_state.get("error"):
            print(f"Interactive TUI runner failed: {worker_state['error']}", file=sys.stderr)
    except Exception as exc:
        base_report["status"] = "failed"
        base_report["error"] = str(exc)
        print(f"Interactive TUI runner failed: {exc}", file=sys.stderr, flush=True)
        return_code = 2
    finally:
        if tmux is not None:
            tmux_run(
                tmux,
                server_name,
                ["kill-server"],
                cwd=plan.working_directory,
                env=tmux_env,
            )
        base_report["finished_at_utc"] = utc_now()
        write_json_atomic(report_path, base_report)
        for temporary_path in (gate_path, target_status_path):
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
    return return_code


def execute_tui_sequence_plan(
    plan: LoadedPlan,
    *,
    report_path: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
    require_asciinema_session: bool = True,
    require_tty: bool = True,
) -> int:
    runtime_env = dict(env or os.environ)
    tmux_env = dict(runtime_env)
    tmux_env.pop("TMUX", None)
    asciinema_session = runtime_env.get("ASCIINEMA_SESSION", "")
    tty_state = {
        "stdin": bool(getattr(sys.stdin, "isatty", lambda: False)()),
        "stdout": bool(getattr(sys.stdout, "isatty", lambda: False)()),
        "stderr": bool(getattr(sys.stderr, "isatty", lambda: False)()),
    }
    sessions = plan_tui_sessions(plan)
    base_report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "mode": "tui-sequence",
        "run_id": run_id,
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "started_at_utc": utc_now(),
        "working_directory": str(plan.working_directory),
        "asciinema_session": asciinema_session,
        "tty": tty_state,
        "target": {
            "name": "multi-tool-tui-sequence",
            "target_count": len(sessions),
        },
        "targets": [],
        "tui_sessions": [],
        "steps": [],
    }
    report_path = report_path.resolve()
    state_directory = report_path.with_name(
        f".{report_path.stem}.{run_id}.tui-sequence"
    )
    server_name = f"arcv-{run_id.replace('-', '')[:20]}"
    tmux_session_name = "recording"
    tmux: Path | None = None
    worker: threading.Thread | None = None
    worker_state: dict[str, Any] = {}
    return_code = 2
    try:
        uuid.UUID(run_id)
        if require_asciinema_session and not asciinema_session:
            raise CommandVideoError(
                "ASCIINEMA_SESSION is missing; the plan is not running inside Asciinema"
            )
        if require_tty and not all(tty_state.values()):
            raise CommandVideoError(
                "The TUI sequence runner requires a real PTY on stdin, stdout, and stderr"
            )
        if state_directory.exists():
            raise CommandVideoError("Temporary TUI sequence evidence path already exists")
        state_directory.mkdir(parents=False)

        target_records: list[dict[str, Any]] = []
        for session in sessions:
            target = session["target"]
            target_path = resolve_executable(
                target["executable"],
                working_directory=plan.working_directory,
                path_value=runtime_env.get("PATH", ""),
            )
            target_digest = sha256_file(target_path)
            version_argv = [str(target_path), *target["version_args"]]
            version_code, version_output = command_output(
                version_argv, cwd=plan.working_directory, env=runtime_env
            )
            if version_code != 0:
                raise CommandVideoError(
                    f"TUI session {session['id']} version command exited with "
                    f"{version_code}: {shlex.join(version_argv)}"
                )
            target_records.append(
                {
                    "session_id": session["id"],
                    "name": target["name"],
                    "requested_executable": target["executable"],
                    "resolved_executable": str(target_path),
                    "executable_sha256": target_digest,
                    "version_argv": version_argv,
                    "version_exit_code": version_code,
                    "version_output": version_output,
                }
            )
        base_report["targets"] = [dict(record) for record in target_records]

        tmux_requested = runtime_env.get("ASCIINEMA_TMUX", "tmux")
        tmux = resolve_executable(
            tmux_requested,
            working_directory=plan.working_directory,
            path_value=runtime_env.get("PATH", ""),
        )
        tmux_code, tmux_version = command_output(
            [str(tmux), "-V"], cwd=plan.working_directory, env=tmux_env
        )
        if tmux_code != 0:
            raise CommandVideoError("tmux version check failed")
        tmux_record = {
            "requested": tmux_requested,
            "resolved_executable": str(tmux),
            "executable_sha256": sha256_file(tmux),
            "version_output": tmux_version.strip(),
            "isolated_server": server_name,
            "session": tmux_session_name,
        }

        print("\033[2J\033[H", end="")
        emit_hidden_marker(run_id, "RUN", "BEGIN")
        print(f"REAL MULTI-TOOL TUI SESSION: {plan.data['title']}")
        for index, target_record in enumerate(target_records, start=1):
            print(
                f"Target {index}/{len(target_records)}: {target_record['name']} "
                f"({target_record['resolved_executable']})"
            )
            print(
                "Executable SHA-256: "
                f"{target_record['executable_sha256'][:16]}... (full value in manifest)"
            )
            print("Version command output:")
            print(str(target_record["version_output"]).rstrip())
        print(f"Declared scope: {plan.data['declared_scope']}")
        print("Input method: reviewed timed text and explicit PTY key actions")
        print(f"Plan SHA-256: {plan.sha256[:16]}... (full value in manifest)", flush=True)
        emit_hidden_marker(run_id, "IDENTITY", "END")
        time.sleep(0.75)

        wrapper_argv = [
            sys.executable,
            str(Path(__file__).resolve()),
            "run-tui-sequence-targets",
            "--plan",
            str(plan.path),
            "--state-directory",
            str(state_directory),
            "--run-id",
            run_id,
        ]
        terminal = plan.data["terminal"]
        tmux_run(
            tmux,
            server_name,
            [
                "-f",
                "/dev/null",
                "new-session",
                "-d",
                "-x",
                str(terminal["cols"]),
                "-y",
                str(terminal["rows"]),
                "-s",
                tmux_session_name,
                shlex.join(wrapper_argv),
            ],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )
        tmux_run(
            tmux,
            server_name,
            ["set-option", "-g", "history-limit", "100000"],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )
        tmux_run(
            tmux,
            server_name,
            ["set-option", "-g", "status", "off"],
            cwd=plan.working_directory,
            env=tmux_env,
            check=True,
        )

        def automate_sequence() -> None:
            try:
                client_deadline = time.monotonic() + 15.0
                while time.monotonic() < client_deadline:
                    clients = tmux_run(
                        tmux,
                        server_name,
                        ["list-clients", "-F", "#{client_session}"],
                        cwd=plan.working_directory,
                        env=tmux_env,
                    )
                    if (
                        clients.returncode == 0
                        and tmux_session_name in clients.stdout.splitlines()
                    ):
                        break
                    time.sleep(0.05)
                else:
                    raise CommandVideoError(
                        "tmux client did not attach to the multi-tool recording session"
                    )

                for index, session in enumerate(sessions):
                    session_id = str(session["id"])
                    session_plan = loaded_tui_session(plan, session)
                    status_path = state_directory / f"{index:02d}-{session_id}.status.json"
                    gate_path = state_directory / f"{index:02d}-{session_id}.gate"
                    if gate_path.exists() or status_path.exists():
                        raise CommandVideoError(
                            f"Temporary TUI session evidence already exists: {session_id}"
                        )
                    runtime_target = dict(target_records[index])
                    interaction = session["interaction"]
                    runtime_interaction: dict[str, Any] = {
                        "mode": "tui",
                        "input_delivery": "tmux-send-keys",
                        "action_model": "prompt-or-explicit-actions",
                        "shutdown_mode": tui_shutdown_mode(session),
                        "submit_key": (
                            "Enter"
                            if all("prompt" in step for step in session["steps"])
                            else "per-step"
                        ),
                        "typing_interval_seconds": interaction[
                            "typing_interval_seconds"
                        ],
                        "pre_submit_pause_seconds": interaction[
                            "pre_submit_pause_seconds"
                        ],
                        "ready_pattern_sha256": sha256_text(
                            interaction["ready_pattern"]
                        ),
                        "busy_pattern_sha256": sha256_text(
                            interaction["busy_pattern"]
                        ),
                        "tmux": dict(tmux_record),
                    }
                    runtime_steps: list[dict[str, Any]] = []
                    emit_hidden_marker(
                        run_id,
                        "TUI-SEQUENCE",
                        "HANDOFF",
                        str(index + 1),
                        session_id,
                    )
                    gate_path.write_text(run_id + "\n", encoding="utf-8")
                    automate_tui_session(
                        session_plan,
                        session_id=session_id,
                        runtime_target=runtime_target,
                        runtime_interaction=runtime_interaction,
                        runtime_steps=runtime_steps,
                        target_status_path=status_path,
                        run_id=run_id,
                        tmux=tmux,
                        server_name=server_name,
                        session_name=tmux_session_name,
                        cwd=plan.working_directory,
                        env=tmux_env,
                        emit_primary_ready=(index == 0),
                        hold_before_final_key=(
                            index == len(sessions) - 1
                            and render_end_at(plan) == "before-final-key"
                        ),
                        emit_final_target_exit=True,
                    )
                    base_report["targets"][index] = runtime_target
                    base_report["tui_sessions"].append(
                        {
                            "id": session_id,
                            "index": index + 1,
                            "target": runtime_target,
                            "interaction": runtime_interaction,
                            "steps": runtime_steps,
                        }
                    )
                    base_report["steps"].extend(runtime_steps)

                last_target = base_report["targets"][-1]
                base_report["target"]["final_exit_code"] = last_target.get(
                    "final_exit_code"
                )
                emit_hidden_marker(run_id, "RUN", "END", "0")
                base_report["status"] = "passed"
                worker_state["return_code"] = 0
            except Exception as exc:
                base_report["status"] = "failed"
                base_report["error"] = str(exc)
                worker_state["error"] = str(exc)
                worker_state["return_code"] = 1
                emit_hidden_marker(run_id, "RUN", "END", "1")
                tmux_run(
                    tmux,
                    server_name,
                    ["kill-server"],
                    cwd=plan.working_directory,
                    env=tmux_env,
                )

        worker = threading.Thread(
            target=automate_sequence,
            name="tui-sequence-automation",
            daemon=True,
        )
        worker.start()
        attach = subprocess.run(
            [str(tmux), "-L", server_name, "attach-session", "-t", tmux_session_name],
            cwd=str(plan.working_directory),
            env=tmux_env,
            stdin=None,
            stdout=None,
            stderr=None,
            check=False,
        )
        base_report["tmux_attach_exit_code"] = attach.returncode
        worker.join(timeout=5.0)
        if worker.is_alive():
            raise CommandVideoError(
                "TUI sequence automation did not finish after tmux detached"
            )
        return_code = int(worker_state.get("return_code", 1))
        if return_code != 0 and worker_state.get("error"):
            print(
                f"Multi-tool TUI runner failed: {worker_state['error']}",
                file=sys.stderr,
            )
    except Exception as exc:
        base_report["status"] = "failed"
        base_report["error"] = str(exc)
        print(f"Multi-tool TUI runner failed: {exc}", file=sys.stderr, flush=True)
        return_code = 2
    finally:
        if tmux is not None:
            tmux_run(
                tmux,
                server_name,
                ["kill-server"],
                cwd=plan.working_directory,
                env=tmux_env,
            )
        base_report["finished_at_utc"] = utc_now()
        write_json_atomic(report_path, base_report)
        if state_directory.is_dir():
            for temporary_path in state_directory.iterdir():
                if temporary_path.is_file():
                    try:
                        temporary_path.unlink()
                    except FileNotFoundError:
                        pass
            try:
                state_directory.rmdir()
            except OSError:
                pass
    return return_code


def execute_argv_plan(
    plan: LoadedPlan,
    *,
    report_path: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
    require_asciinema_session: bool = True,
    require_tty: bool = True,
) -> int:
    runtime_env = dict(env or os.environ)
    asciinema_session = runtime_env.get("ASCIINEMA_SESSION", "")
    tty_state = {
        "stdin": bool(getattr(sys.stdin, "isatty", lambda: False)()),
        "stdout": bool(getattr(sys.stdout, "isatty", lambda: False)()),
        "stderr": bool(getattr(sys.stderr, "isatty", lambda: False)()),
    }
    base_report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "run_id": run_id,
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "started_at_utc": utc_now(),
        "working_directory": str(plan.working_directory),
        "asciinema_session": asciinema_session,
        "tty": tty_state,
        "target": {},
        "steps": [],
    }
    try:
        if not re.fullmatch(r"[0-9a-fA-F-]{36}", run_id):
            raise CommandVideoError("run_id must be a UUID string")
        uuid.UUID(run_id)
        if require_asciinema_session and not asciinema_session:
            raise CommandVideoError("ASCIINEMA_SESSION is missing; the plan is not running inside Asciinema")
        if require_tty and not all(tty_state.values()):
            raise CommandVideoError("The target runner requires a real PTY on stdin, stdout, and stderr")

        target = plan.data["target"]
        target_path = resolve_executable(
            target["executable"],
            working_directory=plan.working_directory,
            path_value=runtime_env.get("PATH", ""),
        )
        target_digest = sha256_file(target_path)
        version_argv = [str(target_path), *target["version_args"]]
        version_code, version_output = command_output(
            version_argv, cwd=plan.working_directory, env=runtime_env
        )
        base_report["target"] = {
            "name": target["name"],
            "requested_executable": target["executable"],
            "resolved_executable": str(target_path),
            "executable_sha256": target_digest,
            "version_argv": version_argv,
            "version_exit_code": version_code,
            "version_output": version_output,
        }
        if version_code != 0:
            raise CommandVideoError(
                f"Target version command exited with {version_code}: {shlex.join(version_argv)}"
            )

        print("\033[2J\033[H", end="")
        emit_hidden_marker(run_id, "RUN", "BEGIN")
        print(f"REAL TERMINAL SESSION: {plan.data['title']}")
        print(f"Target: {target['name']}")
        print(f"Executable: {target_path}")
        print(f"Executable SHA-256: {target_digest[:16]}... (full value in manifest)")
        print("Version command output:")
        print(version_output.rstrip())
        print(f"Declared scope: {plan.data['declared_scope']}")
        print(f"Plan SHA-256: {plan.sha256[:16]}... (full value in manifest)")
        emit_hidden_marker(run_id, "IDENTITY", "END")
        time.sleep(0.5)

        overall_passed = True
        for index, step in enumerate(plan.data["steps"], start=1):
            prompt_hash = sha256_text(step["prompt"])
            argv = expanded_step_argv(target_path, step["args"], step["prompt"], run_id)
            display_argv = displayed_step_argv(target_path, step["args"], step["prompt"], run_id)
            argv_hash = sha256_bytes("\x00".join(argv).encode("utf-8"))
            started_at = utc_now()
            started_monotonic = time.monotonic()
            print()
            emit_hidden_marker(run_id, "STEP", step["id"], "BEGIN")
            print(
                f"PROMPT {index}/{len(plan.data['steps'])} [{step['id']}] "
                f"SHA-256 {prompt_hash[:16]}..."
            )
            emit_hidden_marker(run_id, "PROMPT", step["id"], "BEGIN")
            print(step["prompt"])
            emit_hidden_marker(run_id, "PROMPT", step["id"], "END")
            print(f"Direct argv: {shlex.join(display_argv)}", flush=True)

            process: subprocess.Popen[Any] | None = None
            exit_code: int | None = None
            timed_out = False
            launch_error: str | None = None
            try:
                process = subprocess.Popen(
                    argv,
                    cwd=str(plan.working_directory),
                    env=runtime_env,
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    start_new_session=(os.name != "nt"),
                )
                exit_code = process.wait(timeout=step["timeout_seconds"])
            except subprocess.TimeoutExpired:
                timed_out = True
                if process is not None:
                    terminate_process(process)
                    exit_code = process.returncode
            except OSError as exc:
                launch_error = str(exc)
                exit_code = None

            elapsed = time.monotonic() - started_monotonic
            accepted = (
                not timed_out
                and launch_error is None
                and exit_code in step["expected_exit_codes"]
            )
            status = "passed" if accepted else "failed"
            if timed_out:
                status = "timed_out"
            elif launch_error is not None:
                status = "launch_error"
            step_report = {
                "id": step["id"],
                "index": index,
                "status": status,
                "started_at_utc": started_at,
                "finished_at_utc": utc_now(),
                "elapsed_seconds": round(elapsed, 6),
                "prompt_sha256": prompt_hash,
                "argv_sha256": argv_hash,
                "display_argv": display_argv,
                "expected_exit_codes": step["expected_exit_codes"],
                "exit_code": exit_code,
                "timed_out": timed_out,
                "launch_error": launch_error,
            }
            base_report["steps"].append(step_report)
            emit_hidden_marker(run_id, "STEP", step["id"], "END", str(exit_code))
            print(f"Observed exit code: {exit_code}; expected: {step['expected_exit_codes']}", flush=True)
            if not accepted:
                overall_passed = False
                print("Stopping after the first unexpected target result.", flush=True)
                break
            pause = float(step["pause_after_seconds"])
            if pause:
                time.sleep(pause)

        if overall_passed and len(base_report["steps"]) == len(plan.data["steps"]):
            base_report["status"] = "passed"
            emit_hidden_marker(run_id, "RUN", "END", "0")
            return_code = 0
        else:
            base_report["status"] = "failed"
            base_report["error"] = "One or more target steps failed"
            emit_hidden_marker(run_id, "RUN", "END", "1")
            return_code = 1
    except Exception as exc:
        base_report["status"] = "failed"
        base_report["error"] = str(exc)
        print(f"Real-session runner failed: {exc}", file=sys.stderr, flush=True)
        return_code = 2
    finally:
        base_report["finished_at_utc"] = utc_now()
        write_json_atomic(report_path.resolve(), base_report)
    return return_code


def execute_plan(
    plan: LoadedPlan,
    *,
    report_path: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
    require_asciinema_session: bool = True,
    require_tty: bool = True,
) -> int:
    mode = plan_mode(plan)
    if mode == "tui-sequence":
        return execute_tui_sequence_plan(
            plan,
            report_path=report_path,
            run_id=run_id,
            env=env,
            require_asciinema_session=require_asciinema_session,
            require_tty=require_tty,
        )
    if mode == "tui":
        return execute_tui_plan(
            plan,
            report_path=report_path,
            run_id=run_id,
            env=env,
            require_asciinema_session=require_asciinema_session,
            require_tty=require_tty,
        )
    return execute_argv_plan(
        plan,
        report_path=report_path,
        run_id=run_id,
        env=env,
        require_asciinema_session=require_asciinema_session,
        require_tty=require_tty,
    )


def parse_cast(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise CommandVideoError(f"Could not read asciicast {path}: {exc}") from exc
    if not lines:
        raise CommandVideoError("Asciicast is empty")
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise CommandVideoError(f"Invalid asciicast header: {exc}") from exc
    if not isinstance(header, dict) or header.get("version") not in (2, 3):
        raise CommandVideoError("Asciicast must use format version 2 or 3")
    version = int(header["version"])
    output_chunks: list[str] = []
    event_count = 0
    output_event_count = 0
    input_event_count = 0
    marker_event_count = 0
    exit_codes: list[int] = []
    times: list[float] = []
    for line_number, line in enumerate(lines[1:], start=2):
        if not line or line.startswith("#"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CommandVideoError(f"Invalid asciicast event on line {line_number}: {exc}") from exc
        if (
            not isinstance(event, list)
            or len(event) != 3
            or isinstance(event[0], bool)
            or not isinstance(event[0], (int, float))
            or event[0] < 0
            or not isinstance(event[1], str)
        ):
            raise CommandVideoError(f"Malformed asciicast event on line {line_number}")
        event_count += 1
        times.append(float(event[0]))
        code = event[1]
        data = event[2]
        if code == "o":
            if not isinstance(data, str):
                raise CommandVideoError(f"Output event data is not text on line {line_number}")
            output_chunks.append(data)
            output_event_count += 1
        elif code == "i":
            input_event_count += 1
        elif code == "m":
            marker_event_count += 1
        elif code == "x":
            try:
                exit_codes.append(int(data))
            except (TypeError, ValueError) as exc:
                raise CommandVideoError(f"Invalid exit event on line {line_number}") from exc
    duration = sum(times) if version == 3 else (max(times) if times else 0.0)
    if version == 3:
        term = header.get("term", {})
        cols = term.get("cols") if isinstance(term, dict) else None
        rows = term.get("rows") if isinstance(term, dict) else None
    else:
        cols = header.get("width")
        rows = header.get("height")
    return {
        "header": header,
        "version": version,
        "cols": cols,
        "rows": rows,
        "duration_seconds": duration,
        "event_count": event_count,
        "output_event_count": output_event_count,
        "input_event_count": input_event_count,
        "marker_event_count": marker_event_count,
        "exit_codes": exit_codes,
        "output_text": "".join(output_chunks),
    }


def cast_output_text_time(
    path: Path, expected_text: str, *, last: bool = False
) -> float:
    """Return the cast-relative time of the first or last output fragment."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise CommandVideoError("Asciicast is empty")
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise CommandVideoError(f"Invalid asciicast header: {exc}") from exc
    if not isinstance(header, dict) or header.get("version") not in (2, 3):
        raise CommandVideoError("Asciicast must use format version 2 or 3")
    version = int(header["version"])
    elapsed = 0.0
    found_at: float | None = None
    for line_number, line in enumerate(lines[1:], start=2):
        if not line or line.startswith("#"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CommandVideoError(f"Invalid asciicast event on line {line_number}: {exc}") from exc
        if not isinstance(event, list) or len(event) != 3:
            raise CommandVideoError(f"Malformed asciicast event on line {line_number}")
        event_time = float(event[0])
        elapsed = elapsed + event_time if version == 3 else event_time
        if event[1] == "o" and isinstance(event[2], str) and expected_text in event[2]:
            found_at = elapsed
            if not last:
                return found_at
    if found_at is not None:
        return found_at
    raise CommandVideoError(f"Asciicast is missing presentation fragment: {expected_text!r}")


def verify_tui_action_step(
    planned: Mapping[str, Any],
    observed: Mapping[str, Any],
    *,
    planned_interaction: Mapping[str, Any],
    run_id: str,
    output_text: str,
    final_exit_code: Any,
) -> list[str]:
    step_id = str(planned["id"])
    if (
        observed.get("id") != step_id
        or observed.get("status") != "passed"
        or observed.get("input_kind") != "actions"
        or observed.get("input_sha256") != tui_step_input_sha256(planned)
        or observed.get("typing_method") != "tmux-send-keys"
    ):
        raise CommandVideoError(f"Runtime TUI action step did not pass: {step_id}")
    planned_actions = planned["actions"]
    observed_actions = observed.get("actions")
    if (
        not isinstance(observed_actions, list)
        or observed.get("action_count") != len(planned_actions)
        or len(observed_actions) != len(planned_actions)
    ):
        raise CommandVideoError(f"TUI action count mismatch for step {step_id}")
    expected_keystrokes = 0
    expected_enter = False
    for action_index, (planned_action, observed_action) in enumerate(
        zip(planned_actions, observed_actions, strict=True), start=1
    ):
        action_type = planned_action["type"]
        action_digest = sha256_json(planned_action)
        if (
            not isinstance(observed_action, dict)
            or observed_action.get("index") != action_index
            or observed_action.get("type") != action_type
            or observed_action.get("action_sha256") != action_digest
        ):
            raise CommandVideoError(
                f"TUI action evidence mismatch for {step_id} action {action_index}"
            )
        required_fragments = (
            marker(
                run_id,
                "ACTION",
                step_id,
                str(action_index),
                "BEGIN",
                str(action_type).upper(),
                action_digest,
            ),
            marker(
                run_id,
                "ACTION",
                step_id,
                str(action_index),
                "END",
                str(action_type).upper(),
                action_digest,
            ),
        )
        if any(fragment not in output_text for fragment in required_fragments):
            raise CommandVideoError(
                f"Asciicast action markers are incomplete for {step_id} action {action_index}"
            )
        if action_type == "text":
            text_value = planned_action["text"]
            text_hash = sha256_text(text_value)
            screen = observed_action.get("screen")
            if (
                observed_action.get("text_sha256") != text_hash
                or observed_action.get("keystroke_count") != len(text_value)
                or observed_action.get("visible_before_next_key") is not True
                or not isinstance(screen, str)
                or text_value not in screen
                or observed_action.get("screen_sha256") != sha256_text(screen)
            ):
                raise CommandVideoError(
                    f"TUI text action evidence is incomplete for {step_id} action {action_index}"
                )
            typing_fragments = (
                marker(run_id, "TYPING", step_id, str(action_index), "BEGIN", text_hash),
                marker(run_id, "TYPING", step_id, str(action_index), "END", text_hash),
            )
            if any(fragment not in output_text for fragment in typing_fragments):
                raise CommandVideoError(
                    f"Asciicast typing markers are incomplete for {step_id} action {action_index}"
                )
            expected_keystrokes += len(text_value)
        elif action_type == "key":
            key_value = planned_action["key"]
            if observed_action.get("key") != key_value:
                raise CommandVideoError(
                    f"TUI key evidence mismatch for {step_id} action {action_index}"
                )
            if key_value == "Enter":
                expected_enter = True
                key_marker = marker(run_id, "SUBMIT", step_id, "ENTER")
            else:
                key_marker = marker(run_id, "KEY", step_id, key_value)
            if key_marker not in output_text:
                raise CommandVideoError(
                    f"Asciicast key marker is missing for {step_id} action {action_index}"
                )
            expected_keystrokes += 1
        elif float(observed_action.get("seconds", -1.0)) != float(planned_action["seconds"]):
            raise CommandVideoError(
                f"TUI pause evidence mismatch for {step_id} action {action_index}"
            )
    if (
        observed.get("keystroke_count") != expected_keystrokes
        or observed.get("enter_submitted") is not expected_enter
    ):
        raise CommandVideoError(f"TUI aggregate action evidence is incomplete for {step_id}")
    completion = tui_step_completion(planned)
    completion_screen = observed.get("completion_screen")
    if (
        observed.get("completion") != completion
        or not isinstance(completion_screen, str)
        or observed.get("completion_screen_sha256") != sha256_text(completion_screen)
    ):
        raise CommandVideoError(f"TUI completion evidence is incomplete for {step_id}")
    if completion == "ready":
        if (
            observed.get("ready_after_response") is not True
            or observed.get("busy_after_response") is not False
            or not screen_matches_ready(
                completion_screen, str(planned_interaction["ready_pattern"])
            )
            or screen_matches_busy(
                completion_screen, str(planned_interaction["busy_pattern"])
            )
        ):
            raise CommandVideoError(f"TUI action step did not return ready: {step_id}")
        step_exit_code = 0
    else:
        if observed.get("target_exited_after_actions") is not True:
            raise CommandVideoError(f"TUI action step did not prove target exit: {step_id}")
        step_exit_code = final_exit_code
    step_fragments = (
        marker(run_id, "STEP", step_id, "BEGIN"),
        marker(run_id, "STEP", step_id, "END", str(step_exit_code)),
    )
    if any(fragment not in output_text for fragment in step_fragments):
        raise CommandVideoError(f"Asciicast step markers are incomplete for {step_id}")
    checks = ["explicit-tui-actions", "action-markers"]
    if any(action["type"] == "text" for action in planned_actions):
        checks.append("timed-keystrokes")
    if expected_enter:
        checks.append("enter-submission")
    if any(action["type"] == "key" and action["key"] != "Enter" for action in planned_actions):
        checks.append("command-keys")
    if completion == "target-exit":
        checks.append("target-exit-completion")
    else:
        checks.append("tui-ready")
    return checks


def verify_runtime_and_cast(
    plan: LoadedPlan, runtime: Mapping[str, Any], cast: Mapping[str, Any]
) -> list[str]:
    checks: list[str] = []
    if runtime.get("schema_version") != SCHEMA_VERSION or runtime.get("status") != "passed":
        raise CommandVideoError("Runtime report did not pass")
    if runtime.get("plan_sha256") != plan.sha256:
        raise CommandVideoError("Runtime report plan hash does not match the plan")
    run_id = runtime.get("run_id")
    if not isinstance(run_id, str):
        raise CommandVideoError("Runtime report has no run_id")
    try:
        uuid.UUID(run_id)
    except ValueError as exc:
        raise CommandVideoError("Runtime report run_id is not a UUID") from exc
    if not runtime.get("asciinema_session"):
        raise CommandVideoError("Runtime report has no Asciinema session ID")
    tty = runtime.get("tty")
    if not isinstance(tty, dict) or not all(tty.get(key) is True for key in ("stdin", "stdout", "stderr")):
        raise CommandVideoError("Runtime report does not prove a three-stream PTY")
    checks.extend(["runtime-status", "plan-hash", "asciinema-session", "pty"])

    if cast.get("input_event_count") != 0:
        raise CommandVideoError("Asciicast contains input events; input capture must stay disabled")
    output_text = cast.get("output_text")
    if not isinstance(output_text, str):
        raise CommandVideoError("Asciicast output could not be reconstructed")
    if plan_has_bridged_lazygit(plan):
        normalized_output = output_text.lower()
        lazygit_path_failures = (
            "filename too long",
            "fatal: '$git_dir' too big",
            "error getting repo paths",
        )
        if any(term in normalized_output for term in lazygit_path_failures):
            raise CommandVideoError(
                "The lazygit cast contains a Windows repository path failure"
            )
        checks.append("lazygit-path-clean")
    header = cast.get("header")
    command = header.get("command", "") if isinstance(header, dict) else ""
    if "run-plan" not in command or run_id not in command:
        raise CommandVideoError("Asciicast header does not identify the bundled runner and run UUID")
    if marker(run_id, "RUN", "BEGIN") not in output_text or marker(run_id, "RUN", "END", "0") not in output_text:
        raise CommandVideoError("Asciicast is missing run boundary markers")
    checks.extend(["no-input-events", "cast-command", "run-markers"])

    mode = plan_mode(plan)
    planned_steps = plan_steps(plan)
    runtime_steps = runtime.get("steps")
    if not isinstance(runtime_steps, list) or len(runtime_steps) != len(planned_steps):
        raise CommandVideoError("Runtime report step count does not match the plan")
    if mode == "tui-sequence":
        if runtime.get("mode") != "tui-sequence":
            raise CommandVideoError("Runtime report does not identify a TUI sequence")
        planned_sessions = plan_tui_sessions(plan)
        observed_sessions = runtime.get("tui_sessions")
        observed_targets = runtime.get("targets")
        if (
            not isinstance(observed_sessions, list)
            or not isinstance(observed_targets, list)
            or len(observed_sessions) != len(planned_sessions)
            or len(observed_targets) != len(planned_sessions)
        ):
            raise CommandVideoError(
                "Runtime report does not contain every planned TUI session and target"
            )
        observed_step_offset = 0
        resolved_target_identities: set[tuple[str, str]] = set()
        previous_boundary = -1
        for index, (planned_session, observed_session, observed_target) in enumerate(
            zip(
                planned_sessions,
                observed_sessions,
                observed_targets,
                strict=True,
            )
        ):
            if not isinstance(observed_session, dict) or not isinstance(
                observed_target, dict
            ):
                raise CommandVideoError("Runtime TUI sequence entry is not an object")
            session_id = str(planned_session["id"])
            if (
                observed_session.get("id") != session_id
                or observed_session.get("index") != index + 1
                or observed_session.get("target") != observed_target
            ):
                raise CommandVideoError(
                    f"Runtime TUI sequence order or target mismatch: {session_id}"
                )
            session_steps = observed_session.get("steps")
            if not isinstance(session_steps, list) or len(session_steps) != len(
                planned_session["steps"]
            ):
                raise CommandVideoError(
                    f"Runtime TUI session step count mismatch: {session_id}"
                )
            flattened_slice = runtime_steps[
                observed_step_offset : observed_step_offset + len(session_steps)
            ]
            if flattened_slice != session_steps:
                raise CommandVideoError(
                    f"Runtime flattened steps do not preserve TUI session {session_id}"
                )
            observed_step_offset += len(session_steps)

            resolved_executable = observed_target.get("resolved_executable")
            executable_digest = observed_target.get("executable_sha256")
            if not isinstance(resolved_executable, str) or not re.fullmatch(
                r"[0-9a-f]{64}", str(executable_digest)
            ):
                raise CommandVideoError(
                    f"Runtime target provenance is incomplete: {session_id}"
                )
            resolved_target_identities.add(
                (resolved_executable.casefold(), str(executable_digest))
            )

            boundary_fragments = [
                marker(
                    run_id,
                    "TUI-SEQUENCE",
                    "HANDOFF",
                    str(index + 1),
                    session_id,
                ),
                marker(run_id, "TUI-SESSION", session_id, "BEGIN"),
                marker(run_id, "TUI-SESSION", session_id, "READY"),
                marker(
                    run_id,
                    "TUI-SESSION",
                    session_id,
                    "EXIT",
                    str(observed_target.get("final_exit_code")),
                ),
            ]
            boundary_positions = [output_text.find(fragment) for fragment in boundary_fragments]
            if any(position < 0 for position in boundary_positions) or boundary_positions != sorted(
                boundary_positions
            ):
                raise CommandVideoError(
                    f"Asciicast TUI session boundaries are missing or out of order: {session_id}"
                )
            if boundary_positions[0] <= previous_boundary:
                raise CommandVideoError("Asciicast TUI sessions are not sequential")
            previous_boundary = boundary_positions[-1]

            session_plan = loaded_tui_session(plan, planned_session)
            session_data = dict(session_plan.data)
            session_render = dict(session_data["render"])
            if index < len(planned_sessions) - 1:
                session_render["end_at"] = "target-exit"
                session_render["last_frame_duration"] = 0.0
            session_data["render"] = session_render
            session_plan = LoadedPlan(
                path=session_plan.path,
                data=session_data,
                sha256=session_plan.sha256,
                working_directory=session_plan.working_directory,
            )
            session_runtime = {
                "schema_version": runtime["schema_version"],
                "status": runtime["status"],
                "mode": "tui",
                "run_id": run_id,
                "plan_sha256": runtime["plan_sha256"],
                "asciinema_session": runtime["asciinema_session"],
                "tty": runtime["tty"],
                "target": observed_target,
                "interaction": observed_session.get("interaction"),
                "steps": session_steps,
            }
            checks.extend(verify_runtime_and_cast(session_plan, session_runtime, cast))
        if observed_step_offset != len(runtime_steps):
            raise CommandVideoError("Runtime contains unassigned TUI sequence steps")
        if len(resolved_target_identities) < 2:
            raise CommandVideoError(
                "Runtime report does not prove at least two distinct TUI executables"
            )
        checks.extend(
            [
                "multi-tui-sequence",
                "multi-target-provenance",
                "tui-session-boundaries",
                "step-count",
            ]
        )
        if cast.get("version") == 3 and cast.get("exit_codes") and cast["exit_codes"][-1] != 0:
            raise CommandVideoError("Asciicast exit event is not successful")
        checks.append("cast-exit")
        return checks
    if mode == "tui":
        interaction = runtime.get("interaction")
        planned_interaction = plan.data["interaction"]
        if (
            runtime.get("mode") != "tui"
            or not isinstance(interaction, dict)
            or interaction.get("mode") != "tui"
            or interaction.get("input_delivery") != "tmux-send-keys"
        ):
            raise CommandVideoError("Runtime report does not prove TUI keystroke delivery")
        if interaction.get("shutdown_mode", "exit-text") != tui_shutdown_mode(plan):
            raise CommandVideoError("Runtime report TUI shutdown mode does not match the plan")
        target_status_evidence = interaction.get("target_status")
        if launch_args_request_windows_working_directory(
            planned_interaction["launch_args"]
        ):
            if not isinstance(target_status_evidence, dict):
                raise CommandVideoError(
                    "Runtime report is missing Windows working-directory bridge evidence"
                )
            bridge = target_status_evidence.get("windows_working_directory_bridge")
            if (
                not isinstance(bridge, dict)
                or bridge.get("status") != "released"
                or bridge.get("created") is not True
                or bridge.get("released") is not True
                or bridge.get("source_working_directory")
                != str(plan.working_directory)
                or not re.fullmatch(r"[D-Z]:/", str(bridge.get("mount_root", "")))
                or bridge.get("create_exit_code") != 0
                or bridge.get("release_exit_code") != 0
            ):
                raise CommandVideoError(
                    "Runtime report does not prove a created and released Windows working-directory bridge"
                )
            launch_argv = target_status_evidence.get("launch_argv")
            resolved_executable = target_status_evidence.get("resolved_executable")
            if not isinstance(launch_argv, list) or not isinstance(
                resolved_executable, str
            ):
                raise CommandVideoError(
                    "Runtime report is missing the bridged target launch argv"
                )
            expected_launch_argv = expanded_launch_argv(
                Path(resolved_executable),
                planned_interaction["launch_args"],
                run_id,
                windows_working_directory=str(bridge["mount_root"]),
            )
            if launch_argv != expected_launch_argv or any(
                WINDOWS_WORKING_DIRECTORY_TOKEN in str(item) for item in launch_argv
            ):
                raise CommandVideoError(
                    "Runtime bridged target launch argv does not match the reviewed plan"
                )
            checks.append("windows-working-directory-bridge")
        elif isinstance(target_status_evidence, dict) and target_status_evidence.get(
            "windows_working_directory_bridge"
        ) is not None:
            raise CommandVideoError(
                "Runtime report contains an undeclared Windows working-directory bridge"
            )
        if render_start_at(plan) == "tui-ready":
            if marker(run_id, "TUI", "READY") not in output_text:
                raise CommandVideoError("Asciicast is missing the TUI-ready presentation marker")
            if not interaction.get("startup_ready_at_utc"):
                raise CommandVideoError("Runtime report is missing the TUI-ready timestamp")
            checks.append("tui-ready-marker")
        if render_end_at(plan) == "before-final-key":
            if marker(run_id, "TUI", "FINAL-KEY") not in output_text:
                raise CommandVideoError(
                    "Asciicast is missing the before-final-key presentation marker"
                )
            checks.append("before-final-key-marker")
        for planned, observed in zip(plan.data["steps"], runtime_steps, strict=True):
            if "actions" in planned:
                checks.extend(
                    verify_tui_action_step(
                        planned,
                        observed,
                        planned_interaction=planned_interaction,
                        run_id=run_id,
                        output_text=output_text,
                        final_exit_code=runtime.get("target", {}).get("final_exit_code"),
                    )
                )
                continue
            prompt = planned["prompt"]
            prompt_hash = sha256_text(prompt)
            if observed.get("id") != planned["id"] or observed.get("status") != "passed":
                raise CommandVideoError(f"Runtime TUI step did not pass: {planned['id']}")
            if observed.get("prompt_sha256") != prompt_hash:
                raise CommandVideoError(f"Prompt hash mismatch for step {planned['id']}")
            typed_screen = observed.get("typed_screen")
            response_screen = observed.get("response_screen")
            if not isinstance(typed_screen, str) or prompt not in typed_screen:
                raise CommandVideoError(
                    f"Typed TUI screen does not show the exact prompt: {planned['id']}"
                )
            if not isinstance(response_screen, str) or not screen_matches_ready(
                response_screen, planned_interaction["ready_pattern"]
            ) or screen_matches_busy(response_screen, planned_interaction["busy_pattern"]):
                raise CommandVideoError(
                    f"TUI response screen is not ready after step: {planned['id']}"
                )
            if observed.get("typed_screen_sha256") != sha256_text(typed_screen):
                raise CommandVideoError(f"Typed screen hash mismatch for step {planned['id']}")
            if observed.get("response_screen_sha256") != sha256_text(response_screen):
                raise CommandVideoError(f"Response screen hash mismatch for step {planned['id']}")
            if (
                observed.get("typing_method") != "tmux-send-keys"
                or observed.get("keystroke_count") != len(prompt)
                or observed.get("submit_key") != "Enter"
                or observed.get("prompt_visible_before_submit") is not True
                or observed.get("ready_after_response") is not True
                or observed.get("busy_after_response") is not False
            ):
                raise CommandVideoError(f"TUI input evidence is incomplete for {planned['id']}")
            required_fragments = (
                marker(run_id, "STEP", planned["id"], "BEGIN"),
                marker(run_id, "TYPING", planned["id"], "BEGIN", prompt_hash),
                marker(run_id, "TYPING", planned["id"], "END", prompt_hash),
                marker(run_id, "SUBMIT", planned["id"], "ENTER"),
                marker(run_id, "STEP", planned["id"], "END", "0"),
            )
            if any(fragment not in output_text for fragment in required_fragments):
                raise CommandVideoError(
                    f"Asciicast TUI markers are incomplete for step {planned['id']}"
                )
        final_exit_code = runtime.get("target", {}).get("final_exit_code")
        if final_exit_code not in planned_interaction["expected_exit_codes"]:
            raise CommandVideoError(f"Unexpected final TUI target exit code: {final_exit_code}")
        if render_start_at(plan) == "tui-ready":
            if (
                not isinstance(target_status_evidence, dict)
                or abs(
                    float(target_status_evidence.get("final_hold_seconds", -1.0))
                    - float(plan.data["render"]["last_frame_duration"])
                )
                > 0.001
            ):
                raise CommandVideoError("Runtime report does not prove the configured final TUI hold")
            checks.append("tui-final-hold")
        if marker(run_id, "TARGET", "EXIT", str(final_exit_code)) not in output_text:
            raise CommandVideoError("Asciicast is missing the final TUI target exit marker")
        checks.extend(
            [
                "step-count",
                "input-hashes",
                "step-markers",
                "target-exit",
            ]
        )
        if any("prompt" in step for step in plan.data["steps"]):
            checks.extend(
                [
                    "prompt-hashes",
                    "typed-prompt-screens",
                    "timed-keystrokes",
                    "enter-submission",
                    "tui-ready",
                ]
            )
    else:
        for planned, observed in zip(plan.data["steps"], runtime_steps, strict=True):
            if observed.get("id") != planned["id"] or observed.get("status") != "passed":
                raise CommandVideoError(f"Runtime step did not pass: {planned['id']}")
            if observed.get("prompt_sha256") != sha256_text(planned["prompt"]):
                raise CommandVideoError(f"Prompt hash mismatch for step {planned['id']}")
            if observed.get("exit_code") not in planned["expected_exit_codes"]:
                raise CommandVideoError(f"Unexpected exit code for step {planned['id']}")
            required_fragments = (
                marker(run_id, "STEP", planned["id"], "BEGIN"),
                marker(run_id, "PROMPT", planned["id"], "BEGIN"),
                planned["prompt"],
                marker(run_id, "PROMPT", planned["id"], "END"),
                marker(run_id, "STEP", planned["id"], "END", str(observed.get("exit_code"))),
            )
            if any(fragment not in output_text for fragment in required_fragments):
                raise CommandVideoError(
                    f"Asciicast evidence is incomplete for step {planned['id']}"
                )
        checks.extend(
            ["step-count", "prompt-hashes", "prompt-text", "step-markers", "exit-codes"]
        )
    if cast.get("version") == 3 and cast.get("exit_codes") and cast["exit_codes"][-1] != 0:
        raise CommandVideoError("Asciicast exit event is not successful")
    checks.append("cast-exit")
    return checks


def normalized_platform_key() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"amd64", "x64"}:
        machine = "x86_64"
    elif machine in {"arm64", "armv8", "armv8l"}:
        machine = "aarch64"
    return system, machine


def download_pinned_asset(name: str, metadata: Mapping[str, Any], destination: Path) -> dict[str, Any]:
    expected_hash = str(metadata["sha256"])
    if destination.exists():
        actual_hash = sha256_file(destination)
        if actual_hash != expected_hash:
            raise CommandVideoError(
                f"Existing {name} has SHA-256 {actual_hash}, expected {expected_hash}; choose a clean directory"
            )
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return {"status": "reused", "sha256": actual_hash, "path": str(destination)}

    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.download")
    request = urllib.request.Request(
        str(metadata["url"]), headers={"User-Agent": "asciinema-real-command-video-skill"}
    )
    digest = hashlib.sha256()
    size = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        actual_hash = digest.hexdigest()
        if actual_hash != expected_hash:
            raise CommandVideoError(
                f"Downloaded {name} has SHA-256 {actual_hash}, expected {expected_hash}"
            )
        if size != int(metadata["size"]):
            raise CommandVideoError(
                f"Downloaded {name} has {size} bytes, expected {metadata['size']}"
            )
        temporary.chmod(0o755)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"status": "downloaded", "sha256": expected_hash, "path": str(destination)}


def bootstrap_tools(directory: Path) -> dict[str, Any]:
    key = normalized_platform_key()
    if key not in PINNED_TOOL_ASSETS:
        if key[0] == "windows":
            raise CommandVideoError("Asciinema recording requires WSL2 on Windows; run bootstrap-tools inside WSL2")
        raise CommandVideoError(f"No pinned toolchain is available for {key[0]}/{key[1]}")
    destination = directory.expanduser().resolve()
    if destination == SKILL_ROOT or SKILL_ROOT in destination.parents:
        raise CommandVideoError("Install project-local tools outside the skill directory")
    destination.mkdir(parents=True, exist_ok=True)
    records: dict[str, Any] = {}
    env = dict(os.environ)
    for name, metadata in PINNED_TOOL_ASSETS[key].items():
        target = destination / name
        result = download_pinned_asset(name, metadata, target)
        code, version_output = command_output([str(target), "--version"], cwd=destination, env=env)
        if code != 0:
            raise CommandVideoError(f"Installed {name} failed its version check")
        records[name] = {
            **result,
            "version": metadata["version"],
            "source_url": metadata["url"],
            "version_output": version_output.strip(),
        }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "generated_at_utc": utc_now(),
        "platform": {"system": key[0], "machine": key[1]},
        "tools": records,
    }
    manifest_path = destination / "toolchain-manifest.json"
    write_json_atomic(manifest_path, manifest)
    return {**manifest, "manifest": str(manifest_path)}


def ensure_output_paths(paths: Iterable[Path]) -> None:
    resolved: list[Path] = []
    for path in paths:
        candidate = path.expanduser().resolve()
        if candidate == SKILL_ROOT or SKILL_ROOT in candidate.parents:
            raise CommandVideoError(f"Generated outputs must stay outside the skill directory: {candidate}")
        if candidate.exists():
            raise CommandVideoError(f"Refusing to overwrite existing evidence: {candidate}")
        resolved.append(candidate)
    if len(set(resolved)) != len(resolved):
        raise CommandVideoError("All output paths must be distinct")


def recording_attempt_ledger_path(plan: LoadedPlan) -> Path:
    path = plan.path.with_name(f".{plan.path.stem}.recording-attempt.json").resolve()
    if path == SKILL_ROOT or SKILL_ROOT in path.parents:
        raise CommandVideoError(
            "Copy the session plan outside the skill before recording; the attempt ledger "
            "must not be written into the skill bundle"
        )
    return path


def claim_recording_attempt(
    plan: LoadedPlan,
    *,
    run_id: str,
    cast_path: Path,
    mp4_path: Path,
    manifest_path: Path,
    runtime_path: Path,
) -> tuple[Path, dict[str, Any]]:
    ledger_path = recording_attempt_ledger_path(plan)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "claimed",
        "claimed_at_utc": utc_now(),
        "run_id": run_id,
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "outputs": {
            "cast": str(cast_path),
            "mp4": str(mp4_path),
            "manifest": str(manifest_path),
            "runtime_report": str(runtime_path),
        },
        "policy": (
            "This immutable plan-scoped claim permits exactly one record transaction. "
            "Preserve failed evidence. A different plan path or output name does not authorize "
            "a retry for the same user-requested deliverable."
        ),
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        descriptor = os.open(
            ledger_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError as exc:
        raise CommandVideoError(
            f"Recording attempt already claimed for this plan: {ledger_path}. "
            "Do not delete, move, or overwrite prior evidence to retry."
        ) from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            ledger_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return ledger_path, payload


def is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def windows_path_to_wsl(path: Path) -> str:
    """Translate an absolute Windows path to the default WSL automount form."""
    windows_path = PureWindowsPath(str(path))
    if not windows_path.is_absolute() or not windows_path.drive:
        raise CommandVideoError(f"Expected an absolute Windows path, got: {path}")
    if windows_path.drive.startswith("\\"):
        raise CommandVideoError(
            f"UNC paths are not supported by the automatic WSL bridge: {windows_path}"
        )
    drive = windows_path.drive.rstrip(":").lower()
    tail = "/".join(windows_path.parts[1:])
    return f"/mnt/{drive}/{tail}" if tail else f"/mnt/{drive}"


def resolve_windows_path_argument(value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    return candidate.resolve()


def forward_windows_command_to_wsl(raw_argv: Sequence[str]) -> int:
    """Re-execute Unix-only commands in WSL with translated paths."""
    command = raw_argv[0]
    path_options_by_command = {
        "bootstrap-tools": {"--directory"},
        "preflight": {"--tools-dir"},
        "record": {
            "--cast",
            "--mp4",
            "--manifest",
            "--runtime-report",
            "--gif",
            "--tools-dir",
        },
        "validate": {"--plan", "--cast", "--mp4", "--manifest", "--tools-dir"},
    }
    path_options = path_options_by_command[command]
    translated: list[str] = [command]
    index = 1
    if command in {"preflight", "record"}:
        if index >= len(raw_argv) or raw_argv[index].startswith("-"):
            raise CommandVideoError(f"{command} requires a plan path")
        translated.append(
            windows_path_to_wsl(resolve_windows_path_argument(raw_argv[index]))
        )
        index += 1
    while index < len(raw_argv):
        token = raw_argv[index]
        if "=" in token and token.split("=", 1)[0] in path_options:
            option, value = token.split("=", 1)
            translated.append(
                f"{option}={windows_path_to_wsl(resolve_windows_path_argument(value))}"
            )
            index += 1
            continue
        translated.append(token)
        if token in path_options:
            if index + 1 >= len(raw_argv):
                raise CommandVideoError(f"{token} requires a path value")
            translated.append(
                windows_path_to_wsl(resolve_windows_path_argument(raw_argv[index + 1]))
            )
            index += 2
            continue
        if token in {"--asciinema", "--agg", "--tmux", "--ffmpeg", "--ffprobe"}:
            if index + 1 >= len(raw_argv):
                raise CommandVideoError(f"{token} requires an executable value")
            value = raw_argv[index + 1]
            if re.match(r"^[A-Za-z]:[\\/]", value):
                translated.append(
                    windows_path_to_wsl(resolve_windows_path_argument(value))
                )
            else:
                translated.append(value)
            index += 2
            continue
        index += 1

    if command in {"preflight", "record", "validate"} and "--ffprobe" not in translated:
        native_ffprobe = shutil.which("ffprobe")
        translated.extend(
            [
                "--ffprobe",
                windows_path_to_wsl(Path(native_ffprobe).resolve())
                if native_ffprobe
                else "ffprobe.exe",
            ]
        )
    if command in {"preflight", "record"} and "--ffmpeg" not in translated:
        native_ffmpeg = shutil.which("ffmpeg")
        translated.extend(
            [
                "--ffmpeg",
                windows_path_to_wsl(Path(native_ffmpeg).resolve())
                if native_ffmpeg
                else "ffmpeg.exe",
            ]
        )

    wsl = shutil.which("wsl") or shutil.which("wsl.exe")
    if wsl is None:
        raise CommandVideoError("WSL2 is required for Asciinema recording on Windows")
    script_path = windows_path_to_wsl(Path(__file__).resolve())
    working_directory = windows_path_to_wsl(Path.cwd().resolve())
    shell_command = (
        f"cd {shlex.quote(working_directory)} && "
        f"exec python3 {shlex.quote(script_path)} {shlex.join(translated)}"
    )
    completed = subprocess.run(
        [wsl, "bash", "-lc", shell_command],
        stdin=None,
        stdout=None,
        stderr=None,
        check=False,
    )
    return completed.returncode


def windows_interop_path(path: Path, executable: Path) -> str:
    if not is_wsl() or executable.suffix.lower() != ".exe":
        return str(path)
    wslpath = shutil.which("wslpath")
    if wslpath is None:
        raise CommandVideoError("wslpath is required for Windows media-tool interop")
    code, output = command_output([wslpath, "-w", str(path)], cwd=path.parent, env=os.environ)
    if code != 0 or not output.strip():
        raise CommandVideoError(f"Could not convert WSL path for Windows executable: {path}")
    return output.strip()


def run_checked(argv: Sequence[str], *, cwd: Path, env: Mapping[str, str], label: str) -> None:
    try:
        completed = subprocess.run(
            list(argv), cwd=str(cwd), env=dict(env), check=False
        )
    except OSError as exc:
        raise CommandVideoError(f"Could not start {label}: {exc}") from exc
    if completed.returncode != 0:
        raise CommandVideoError(f"{label} exited with {completed.returncode}: {shlex.join(argv)}")


def run_checked_capture(
    argv: Sequence[str], *, cwd: Path, env: Mapping[str, str], label: str
) -> str:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=str(cwd),
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise CommandVideoError(f"Could not start {label}: {exc}") from exc
    if completed.returncode != 0:
        details = (completed.stderr or completed.stdout)[-4000:]
        raise CommandVideoError(
            f"{label} exited with {completed.returncode}: {details.strip()}"
        )
    return completed.stdout


def probe_video(
    mp4_path: Path, *, ffprobe: Path, cwd: Path, env: Mapping[str, str]
) -> tuple[dict[str, Any], list[str]]:
    media_path = windows_interop_path(mp4_path, ffprobe)
    argv = [
        str(ffprobe),
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        media_path,
    ]
    raw = run_checked_capture(argv, cwd=cwd, env=env, label="ffprobe")
    try:
        probe = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CommandVideoError(f"ffprobe returned invalid JSON: {exc}") from exc
    streams = probe.get("streams", [])
    video_streams = [item for item in streams if item.get("codec_type") == "video"]
    audio_streams = [item for item in streams if item.get("codec_type") == "audio"]
    if len(video_streams) != 1:
        raise CommandVideoError("MP4 must contain exactly one video stream")
    if audio_streams:
        raise CommandVideoError("Direct terminal MP4 must not contain an unexpected audio stream")
    video = video_streams[0]
    if video.get("codec_name") != "h264":
        raise CommandVideoError(f"MP4 codec is {video.get('codec_name')}, expected h264")
    if video.get("pix_fmt") != "yuv420p":
        raise CommandVideoError(f"MP4 pixel format is {video.get('pix_fmt')}, expected yuv420p")
    width = int(video.get("width", 0))
    height = int(video.get("height", 0))
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise CommandVideoError(f"MP4 dimensions must be positive and even, got {width}x{height}")
    try:
        frame_rate = float(Fraction(video.get("avg_frame_rate", "0/1")))
        duration = float(probe.get("format", {}).get("duration", 0.0))
    except (ValueError, ZeroDivisionError) as exc:
        raise CommandVideoError("MP4 contains invalid frame-rate or duration metadata") from exc
    if frame_rate <= 0 or duration <= 0:
        raise CommandVideoError("MP4 frame rate and duration must be positive")
    summary = {
        "codec_name": video.get("codec_name"),
        "profile": video.get("profile"),
        "pix_fmt": video.get("pix_fmt"),
        "width": width,
        "height": height,
        "avg_frame_rate": video.get("avg_frame_rate"),
        "avg_frame_rate_decimal": frame_rate,
        "duration_seconds": duration,
        "nb_frames": video.get("nb_frames"),
        "format_name": probe.get("format", {}).get("format_name"),
        "size_bytes": mp4_path.stat().st_size,
    }
    return summary, argv


def tool_record(
    requested: str,
    resolved: Path,
    version_args: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
) -> dict[str, Any]:
    code, output = command_output([str(resolved), *version_args], cwd=cwd, env=env)
    if code != 0:
        raise CommandVideoError(f"Tool version check failed for {requested}")
    return {
        "requested": requested,
        "resolved_executable": str(resolved),
        "executable_sha256": sha256_file(resolved),
        "version_output": output.strip(),
    }


def terminal_control_state_order(mode: str) -> list[str]:
    if is_tui_mode(mode):
        states = [
            "preflight-passed",
            "recording-started",
            "pty-attached",
            "target-launched",
            "target-ready",
            "input-action-delivered",
            "interaction-step-complete",
            "target-exit-requested",
            "target-exited",
            "recording-stopped",
            "cast-validated",
            "render-complete",
            "encode-complete",
            "media-validated",
        ]
        if mode == "tui-sequence":
            states.insert(states.index("target-exit-requested"), "target-handoff")
        return states
    return [
        "preflight-passed",
        "recording-started",
        "pty-attached",
        "target-launched",
        "command-exited",
        "recording-stopped",
        "cast-validated",
        "render-complete",
        "encode-complete",
        "media-validated",
    ]


def terminal_control_contract(
    plan: LoadedPlan,
    *,
    asciinema: Path,
    agg: Path,
    tmux: Path | None,
    ffmpeg: Path,
    ffprobe: Path,
    targets: Sequence[Path],
    pty_allocator: Path | None,
) -> dict[str, Any]:
    mode = plan_mode(plan)
    state_order = terminal_control_state_order(mode)
    if is_tui_mode(mode):
        interaction = (
            "reviewed timed text and explicit PTY keys with ready/busy or target-exit gating"
        )
    else:
        interaction = "direct argv process execution with finite timeout and exit-code gating"
    return {
        "mode": mode,
        "state_order": state_order,
        "components": {
            "recorder": str(asciinema),
            "pty_allocator": str(pty_allocator) if pty_allocator else "inherited-tty",
            "multiplexer": str(tmux) if tmux else None,
            "target": str(targets[0]),
            "targets": [str(target) for target in targets],
            "renderer": str(agg),
            "encoder": str(ffmpeg),
            "media_probe": str(ffprobe),
        },
        "interaction": interaction,
        "repeatable_states": (
            (
                [
                    "target-launched",
                    "target-ready",
                    "input-action-delivered",
                    "interaction-step-complete",
                    "target-exit-requested",
                    "target-exited",
                ]
                if mode == "tui-sequence"
                else ["input-action-delivered", "interaction-step-complete"]
            )
            if is_tui_mode(mode)
            else ["target-launched", "command-exited"]
        ),
        "shutdown": (
            "verify target-driven exit, detach PTY, then stop recording"
            if is_tui_mode(mode) and final_tui_shutdown_mode(plan) == "target-exit"
            else "request target exit, verify status, detach PTY, then stop recording"
        ),
        "conversion": "validate cast before agg render; validate H.264 MP4 after ffmpeg encode",
    }


def build_preflight_context(plan: LoadedPlan, args: argparse.Namespace) -> PreflightContext:
    if platform.system().lower() == "windows":
        raise CommandVideoError("Run terminal preflight inside WSL2, not native Windows")
    tools_dir = Path(args.tools_dir).expanduser().resolve() if args.tools_dir else None
    env = dict(os.environ)
    env["PATH"] = path_with_tools(env, tools_dir)
    if not env.get("TERM") or env.get("TERM") == "dumb":
        env["TERM"] = "xterm-256color"

    asciinema = resolve_executable(
        args.asciinema, working_directory=plan.working_directory, path_value=env["PATH"]
    )
    agg = resolve_executable(
        args.agg, working_directory=plan.working_directory, path_value=env["PATH"]
    )
    tmux: Path | None = None
    if is_tui_mode(plan_mode(plan)):
        tmux = resolve_executable(
            args.tmux, working_directory=plan.working_directory, path_value=env["PATH"]
        )
        env["ASCIINEMA_TMUX"] = str(tmux)
    ffmpeg = resolve_executable(
        args.ffmpeg, working_directory=plan.working_directory, path_value=env["PATH"]
    )
    ffprobe = resolve_executable(
        args.ffprobe, working_directory=plan.working_directory, path_value=env["PATH"]
    )
    target_specs = plan_targets(plan)
    targets = [
        resolve_executable(
            target_spec["executable"],
            working_directory=plan.working_directory,
            path_value=env["PATH"],
        )
        for target_spec in target_specs
    ]
    target = targets[0]

    pty_allocator: Path | None = None
    if not (sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()):
        if platform.system().lower() != "linux":
            raise CommandVideoError("Automated non-TTY recording requires util-linux script on Linux/WSL2")
        pty_allocator = resolve_executable(
            "script", working_directory=plan.working_directory, path_value=env["PATH"]
        )

    toolchain = {
        "asciinema": tool_record(
            args.asciinema, asciinema, ["--version"], cwd=plan.working_directory, env=env
        ),
        "agg": tool_record(args.agg, agg, ["--version"], cwd=plan.working_directory, env=env),
        "ffmpeg": tool_record(
            args.ffmpeg, ffmpeg, ["-version"], cwd=plan.working_directory, env=env
        ),
        "ffprobe": tool_record(
            args.ffprobe, ffprobe, ["-version"], cwd=plan.working_directory, env=env
        ),
        "target_preflight": tool_record(
            target_specs[0]["executable"],
            target,
            target_specs[0]["version_args"],
            cwd=plan.working_directory,
            env=env,
        ),
    }
    target_preflights = []
    for index, (target_spec, resolved_target) in enumerate(
        zip(target_specs, targets, strict=True)
    ):
        record = tool_record(
            target_spec["executable"],
            resolved_target,
            target_spec["version_args"],
            cwd=plan.working_directory,
            env=env,
        )
        sessions = plan_tui_sessions(plan)
        if sessions:
            record["session_id"] = sessions[index]["id"]
        target_preflights.append(record)
    toolchain["target_preflights"] = target_preflights

    bridge_preflights: list[dict[str, Any]] = []
    for index, session in enumerate(plan_tui_sessions(plan)):
        if not launch_args_request_windows_working_directory(
            session["interaction"]["launch_args"]
        ):
            continue
        bridge_preflight = windows_path_bridge_preflight(
            working_directory=plan.working_directory,
            target=targets[index],
            env=env,
        )
        bridge_preflight["session_id"] = session["id"]
        target_spec = session["target"]
        if "lazygit" in str(target_spec.get("name", "")).lower() or "lazygit" in str(
            target_spec.get("executable", "")
        ).lower():
            bridge_preflight["lazygit_longpaths"] = lazygit_longpaths_preflight(
                working_directory=plan.working_directory,
                env=env,
            )
        bridge_preflights.append(bridge_preflight)
    if bridge_preflights:
        toolchain["windows_working_directory_bridges"] = bridge_preflights
        if plan_mode(plan) == "tui" and len(bridge_preflights) == 1:
            toolchain["windows_working_directory_bridge"] = bridge_preflights[0]
    if tmux is not None:
        toolchain["tmux"] = tool_record(
            args.tmux, tmux, ["-V"], cwd=plan.working_directory, env=env
        )
    if pty_allocator is not None:
        toolchain["pty_allocator"] = tool_record(
            "script", pty_allocator, ["--version"], cwd=plan.working_directory, env=env
        )

    terminal_control = terminal_control_contract(
        plan,
        asciinema=asciinema,
        agg=agg,
        tmux=tmux,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
        targets=targets,
        pty_allocator=pty_allocator,
    )
    if bridge_preflights:
        terminal_control["components"]["windows_working_directory_bridges"] = [
            str(bridge["subst"]) for bridge in bridge_preflights
        ]
        if plan_mode(plan) == "tui" and len(bridge_preflights) == 1:
            terminal_control["components"]["windows_working_directory_bridge"] = str(
                bridge_preflights[0]["subst"]
            )
    return PreflightContext(
        env=env,
        tools_dir=tools_dir,
        asciinema=asciinema,
        agg=agg,
        tmux=tmux,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
        target=target,
        targets=targets,
        pty_allocator=pty_allocator,
        toolchain=toolchain,
        terminal_control=terminal_control,
    )


def preflight_session(args: argparse.Namespace) -> dict[str, Any]:
    plan = load_plan(args.plan)
    context = build_preflight_context(plan, args)
    return {
        "status": "passed",
        "plan": str(plan.path),
        "plan_sha256": plan.sha256,
        "working_directory": str(plan.working_directory),
        "target": context.toolchain["target_preflight"],
        "targets": context.toolchain["target_preflights"],
        "toolchain": context.toolchain,
        "terminal_control": context.terminal_control,
    }


def record_session(args: argparse.Namespace) -> dict[str, Any]:
    if platform.system().lower() == "windows":
        raise CommandVideoError("Run the Asciinema recording pipeline inside WSL2, not native Windows")
    plan = load_plan(args.plan)
    planned_steps = plan_steps(plan)
    cast_path = Path(args.cast).expanduser().resolve()
    mp4_path = Path(args.mp4).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    runtime_path = (
        Path(args.runtime_report).expanduser().resolve()
        if args.runtime_report
        else manifest_path.with_name(f"{manifest_path.stem}.runtime.json")
    )
    gif_path = Path(args.gif).expanduser().resolve() if args.gif else None
    output_paths = [cast_path, mp4_path, manifest_path, runtime_path]
    if gif_path is not None:
        output_paths.append(gif_path)
    ensure_output_paths(output_paths)
    preflight = build_preflight_context(plan, args)
    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)

    tools_dir = preflight.tools_dir
    env = preflight.env
    asciinema = preflight.asciinema
    agg = preflight.agg
    ffmpeg = preflight.ffmpeg
    ffprobe = preflight.ffprobe
    toolchain = preflight.toolchain

    run_id = str(uuid.uuid4())
    attempt_ledger_path, attempt_ledger = claim_recording_attempt(
        plan,
        run_id=run_id,
        cast_path=cast_path,
        mp4_path=mp4_path,
        manifest_path=manifest_path,
        runtime_path=runtime_path,
    )
    runner_argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "run-plan",
        "--plan",
        str(plan.path),
        "--report",
        str(runtime_path),
        "--run-id",
        run_id,
    ]
    asciinema_argv = [
        str(asciinema),
        "rec",
        "-c",
        shlex.join(runner_argv),
        "-t",
        plan.data["title"],
        str(cast_path),
    ]
    pty_wrapper: list[str] | None = None
    if sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty():
        recording_argv = asciinema_argv
    else:
        if platform.system().lower() != "linux":
            raise CommandVideoError("Automated non-TTY recording requires util-linux script on Linux/WSL2")
        script_executable = preflight.pty_allocator
        if script_executable is None:
            raise CommandVideoError("Terminal preflight did not resolve a PTY allocator")
        terminal = plan.data["terminal"]
        wrapped = (
            f"stty cols {terminal['cols']} rows {terminal['rows']} >/dev/null 2>&1; "
            f"exec {shlex.join(asciinema_argv)}"
        )
        pty_wrapper = [
            str(script_executable),
            "--quiet",
            "--return",
            "--command",
            wrapped,
            "/dev/null",
        ]
        recording_argv = pty_wrapper

    run_checked(
        recording_argv, cwd=plan.working_directory, env=env, label="Asciinema recording"
    )
    if not cast_path.is_file() or not runtime_path.is_file():
        raise CommandVideoError("Recording did not produce both the cast and runtime report")
    runtime = load_json(runtime_path)
    cast_info = parse_cast(cast_path)
    evidence_checks = verify_runtime_and_cast(plan, runtime, cast_info)
    presentation_start = render_start_at(plan)
    presentation_trim_seconds = 0.0
    presentation_end_seconds = float(cast_info["duration_seconds"])
    presentation: dict[str, Any] = {
        "start_at": presentation_start,
        "trim_leading_seconds": presentation_trim_seconds,
        "source_cast_duration_seconds": float(cast_info["duration_seconds"]),
    }
    if presentation_start == "tui-ready":
        ready_marker_seconds = cast_output_text_time(
            cast_path, marker(run_id, "TUI", "READY")
        )
        presentation_lead_seconds = tui_ready_presentation_lead_seconds(plan)
        presentation_trim_seconds = max(
            0.0, ready_marker_seconds - presentation_lead_seconds
        )
        presentation.update(
            {
                "trim_leading_seconds": round(presentation_trim_seconds, 6),
                "ready_marker_seconds": round(ready_marker_seconds, 6),
                "lead_seconds": presentation_lead_seconds,
            }
        )
    if is_tui_mode(plan_mode(plan)) and render_end_at(plan) == "before-final-key":
        final_key_marker_seconds = cast_output_text_time(
            cast_path, marker(run_id, "TUI", "FINAL-KEY")
        )
        presentation_end_seconds = final_key_marker_seconds
        if presentation_end_seconds <= presentation_trim_seconds:
            raise CommandVideoError(
                "The final-key marker occurred before the user-facing presentation began"
            )
        presentation.update(
            {
                "end_at": "before-final-key",
                "final_key_marker_seconds": round(final_key_marker_seconds, 6),
                "presentation_end_seconds": round(presentation_end_seconds, 6),
                "trim_trailing_seconds": round(
                    max(0.0, float(cast_info["duration_seconds"]) - presentation_end_seconds),
                    6,
                ),
                "final_hold_seconds": float(plan.data["render"]["last_frame_duration"]),
            }
        )
        evidence_checks.append("before-final-key-presentation")
        if presentation_start == "tui-ready":
            evidence_checks.append("tui-ready-presentation")
    elif presentation_start == "tui-ready":
        terminal_restore_seconds = cast_output_text_time(
            cast_path,
            "\033[?1049l",
            last=(plan_mode(plan) == "tui-sequence"),
        )
        presentation_end_seconds = max(
            0.0, terminal_restore_seconds - TUI_EXIT_PRESENTATION_MARGIN_SECONDS
        )
        if presentation_end_seconds <= presentation_trim_seconds:
            raise CommandVideoError("TUI terminal restored before the user-facing presentation began")
        presentation.update(
            {
                "end_at": "tui-exit",
                "terminal_restore_seconds": round(terminal_restore_seconds, 6),
                "presentation_end_seconds": round(presentation_end_seconds, 6),
                "trim_trailing_seconds": round(
                    max(0.0, float(cast_info["duration_seconds"]) - presentation_end_seconds),
                    6,
                ),
                "final_hold_seconds": float(plan.data["render"]["last_frame_duration"]),
            }
        )
        evidence_checks.extend(["tui-ready-presentation", "tui-exit-presentation"])

    temporary_directory: tempfile.TemporaryDirectory[str] | None = None
    if gif_path is None:
        temporary_directory = tempfile.TemporaryDirectory(
            prefix="asciinema-render-", dir=str(manifest_path.parent)
        )
        render_gif = Path(temporary_directory.name) / "session.gif"
    else:
        render_gif = gif_path
    render = plan.data["render"]
    terminal = plan.data["terminal"]
    agg_argv = [
        str(agg),
        "--theme",
        str(render["theme"]),
        "--font-size",
        str(render["font_size"]),
        "--line-height",
        str(render["line_height"]),
        "--speed",
        str(render["speed"]),
    ]
    if render["idle_time_limit"] is not None:
        agg_argv.extend(["--idle-time-limit", str(render["idle_time_limit"])])
    agg_argv.extend(
        [
        "--fps-cap",
        str(render["fps"]),
        "--last-frame-duration",
        str(render["last_frame_duration"]),
        "--cols",
        str(terminal["cols"]),
        "--rows",
        str(terminal["rows"]),
        "--no-loop",
        str(cast_path),
        str(render_gif),
        ]
    )
    temporary_mp4 = mp4_path.with_name(f".{mp4_path.stem}.{uuid.uuid4().hex}.tmp.mp4")
    try:
        run_checked(agg_argv, cwd=manifest_path.parent, env=env, label="agg render")
        if not render_gif.is_file() or render_gif.stat().st_size == 0:
            raise CommandVideoError("agg did not produce a non-empty GIF")
        cast_digest = sha256_file(cast_path)
        ffmpeg_input = windows_interop_path(render_gif, ffmpeg)
        ffmpeg_output = windows_interop_path(temporary_mp4, ffmpeg)
        video_filters: list[str] = []
        if (
            presentation_trim_seconds > 0
            or presentation_end_seconds < float(cast_info["duration_seconds"])
        ):
            trim_parts: list[str] = []
            if presentation_trim_seconds > 0:
                trim_parts.append(f"start={presentation_trim_seconds:.6f}")
            if presentation_end_seconds < float(cast_info["duration_seconds"]):
                trim_parts.append(f"end={presentation_end_seconds:.6f}")
            video_filters.extend(
                [
                    "trim=" + ":".join(trim_parts),
                    "setpts=PTS-STARTPTS",
                ]
            )
        video_filters.append(f"fps={render['fps']}")
        if render_end_at(plan) == "before-final-key":
            video_filters.append(
                "tpad=stop_mode=clone:stop_duration="
                f"{float(render['last_frame_duration']):.6f}"
            )
        video_filters.append(
            "pad=ceil(iw/2)*2:ceil(ih/2)*2:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        filter_graph = ",".join(video_filters)
        ffmpeg_argv = [
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-n",
            "-i",
            ffmpeg_input,
            "-vf",
            filter_graph,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-metadata",
            f"comment=Derived from asciicast SHA-256 {cast_digest}",
            ffmpeg_output,
        ]
        run_checked(ffmpeg_argv, cwd=manifest_path.parent, env=env, label="ffmpeg MP4 encode")
        if not temporary_mp4.is_file() or temporary_mp4.stat().st_size == 0:
            raise CommandVideoError("ffmpeg did not produce a non-empty MP4")
        os.replace(temporary_mp4, mp4_path)
        video_probe, ffprobe_argv = probe_video(
            mp4_path, ffprobe=ffprobe, cwd=manifest_path.parent, env=env
        )
        if abs(float(video_probe["avg_frame_rate_decimal"]) - float(render["fps"])) > 0.05:
            raise CommandVideoError(
                f"MP4 frame rate is {video_probe['avg_frame_rate_decimal']}, expected {render['fps']}"
            )
        if is_tui_mode(plan_mode(plan)) and render["idle_time_limit"] is None:
            expected_timeline_seconds = max(
                0.0,
                presentation_end_seconds - presentation_trim_seconds,
            )
            if render_end_at(plan) == "before-final-key":
                expected_timeline_seconds += float(render["last_frame_duration"])
            if float(video_probe["duration_seconds"]) + 0.25 < expected_timeline_seconds:
                raise CommandVideoError(
                    "MP4 is shorter than the preserved real-time TUI presentation"
                )
            evidence_checks.append("real-time-duration")
        artifacts: dict[str, Any] = {
            "plan": {
                "path": str(plan.path),
                "sha256": plan.sha256,
                "size_bytes": plan.path.stat().st_size,
            },
            "cast": {
                "path": str(cast_path),
                "sha256": cast_digest,
                "size_bytes": cast_path.stat().st_size,
            },
            "runtime_report": {
                "path": str(runtime_path),
                "sha256": sha256_file(runtime_path),
                "size_bytes": runtime_path.stat().st_size,
            },
            "mp4": {
                "path": str(mp4_path),
                "sha256": sha256_file(mp4_path),
                "size_bytes": mp4_path.stat().st_size,
            },
            "recording_attempt": {
                "path": str(attempt_ledger_path),
                "sha256": sha256_file(attempt_ledger_path),
                "size_bytes": attempt_ledger_path.stat().st_size,
            },
        }
        if gif_path is not None:
            artifacts["gif_intermediary"] = {
                "path": str(gif_path),
                "sha256": sha256_file(gif_path),
                "size_bytes": gif_path.stat().st_size,
            }
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "pipeline_revision": 2,
            "status": "passed",
            "generated_at_utc": utc_now(),
            "pipeline": "asciinema-cast-to-agg-gif-to-ffmpeg-mp4",
            "run_id": run_id,
            "plan": {
                "title": plan.data["title"],
                "mode": plan_mode(plan),
                "declared_scope": plan.data["declared_scope"],
                "working_directory": str(plan.working_directory),
                "prompt_count": len(planned_steps),
                "text_prompt_count": sum("prompt" in step for step in planned_steps),
                "prompt_sha256": [
                    sha256_text(step["prompt"])
                    for step in planned_steps
                    if "prompt" in step
                ],
                "step_input_sha256": [
                    tui_step_input_sha256(step) for step in planned_steps
                ],
                "tui_session_count": len(plan_tui_sessions(plan)),
            },
            "recording_attempt": attempt_ledger,
            "target": runtime["target"],
            "targets": runtime.get("targets", [runtime["target"]]),
            "tui_sessions": runtime.get("tui_sessions", []),
            "recording": {
                key: value for key, value in cast_info.items() if key not in {"header", "output_text"}
            },
            "cast_header": cast_info["header"],
            "render": {**render, **terminal},
            "presentation": presentation,
            "video_probe": video_probe,
            "artifacts": artifacts,
            "toolchain": toolchain,
            "terminal_control": preflight.terminal_control,
            "commands": {
                "asciinema": asciinema_argv,
                "pty_wrapper": pty_wrapper,
                "agg": agg_argv,
                "ffmpeg": ffmpeg_argv,
                "ffprobe": ffprobe_argv,
            },
            "validation": {
                "passed": True,
                "checks": sorted(set(evidence_checks + ["agg-render", "h264", "yuv420p", "even-dimensions", "constant-frame-rate"])),
            },
        }
        write_json_atomic(manifest_path, manifest)
        validation = validate_existing_artifacts(
            plan_path=plan.path,
            cast_path=cast_path,
            mp4_path=mp4_path,
            manifest_path=manifest_path,
            ffprobe_name=str(ffprobe),
            tools_dir=tools_dir,
        )
        return {
            "status": "passed",
            "plan": str(plan.path),
            "cast": str(cast_path),
            "runtime_report": str(runtime_path),
            "mp4": str(mp4_path),
            "manifest": str(manifest_path),
            "recording_attempt": str(attempt_ledger_path),
            "gif_intermediary": str(gif_path) if gif_path else None,
            "target": runtime["target"],
            "targets": runtime.get("targets", [runtime["target"]]),
            "tui_sessions": runtime.get("tui_sessions", []),
            "video_probe": video_probe,
            "validation": validation,
            "terminal_control": preflight.terminal_control,
            "presentation": presentation,
        }
    finally:
        if temporary_mp4.exists():
            temporary_mp4.unlink()
        if temporary_directory is not None:
            temporary_directory.cleanup()


def verify_artifact_record(
    manifest: Mapping[str, Any], name: str, supplied_path: Path
) -> list[str]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not isinstance(artifacts.get(name), dict):
        raise CommandVideoError(f"Manifest is missing artifact record: {name}")
    record = artifacts[name]
    path = supplied_path.resolve()
    if Path(record.get("path", "")).resolve() != path:
        raise CommandVideoError(f"Manifest path does not match supplied {name} path")
    if not path.is_file():
        raise CommandVideoError(f"Artifact does not exist: {path}")
    actual_hash = sha256_file(path)
    if record.get("sha256") != actual_hash:
        raise CommandVideoError(f"SHA-256 mismatch for {name}")
    if record.get("size_bytes") != path.stat().st_size:
        raise CommandVideoError(f"Size mismatch for {name}")
    return [f"{name}-path", f"{name}-sha256", f"{name}-size"]


def validate_existing_artifacts(
    *,
    plan_path: Path,
    cast_path: Path,
    mp4_path: Path,
    manifest_path: Path,
    ffprobe_name: str,
    tools_dir: Path | None,
) -> dict[str, Any]:
    plan = load_plan(plan_path)
    cast_path = cast_path.expanduser().resolve()
    mp4_path = mp4_path.expanduser().resolve()
    manifest_path = manifest_path.expanduser().resolve()
    if not manifest_path.is_file():
        raise CommandVideoError(f"Manifest does not exist: {manifest_path}")
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise CommandVideoError("Manifest must be a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("status") != "passed":
        raise CommandVideoError("Manifest status did not pass")
    checks = ["manifest-status"]
    checks += verify_artifact_record(manifest, "plan", plan.path)
    checks += verify_artifact_record(manifest, "cast", cast_path)
    checks += verify_artifact_record(manifest, "mp4", mp4_path)
    runtime_record = manifest.get("artifacts", {}).get("runtime_report", {})
    runtime_path = Path(runtime_record.get("path", "")).expanduser().resolve()
    checks += verify_artifact_record(manifest, "runtime_report", runtime_path)
    attempt: Mapping[str, Any] | None = None
    if int(manifest.get("pipeline_revision", 1)) >= 2:
        attempt_path = recording_attempt_ledger_path(plan)
        checks += verify_artifact_record(manifest, "recording_attempt", attempt_path)
        loaded_attempt = load_json(attempt_path)
        if (
            not isinstance(loaded_attempt, dict)
            or loaded_attempt.get("status") != "claimed"
            or loaded_attempt.get("plan_sha256") != plan.sha256
        ):
            raise CommandVideoError("Recording-attempt ledger does not match the plan")
        expected_attempt_outputs = {
            "cast": str(cast_path),
            "mp4": str(mp4_path),
            "manifest": str(manifest_path),
            "runtime_report": str(runtime_path),
        }
        if loaded_attempt.get("outputs") != expected_attempt_outputs:
            raise CommandVideoError("Recording-attempt ledger output paths do not match")
        attempt = loaded_attempt
        checks.append("single-record-attempt")
    runtime = load_json(runtime_path)
    cast_info = parse_cast(cast_path)
    checks += verify_runtime_and_cast(plan, runtime, cast_info)
    if manifest.get("run_id") != runtime.get("run_id"):
        raise CommandVideoError("Manifest and runtime report run IDs do not match")
    if attempt is not None and attempt.get("run_id") != runtime.get("run_id"):
        raise CommandVideoError("Recording-attempt and runtime report run IDs do not match")
    if plan_mode(plan) == "tui-sequence" and (
        manifest.get("targets") != runtime.get("targets")
        or manifest.get("tui_sessions") != runtime.get("tui_sessions")
    ):
        raise CommandVideoError(
            "Manifest multi-TUI target or session evidence does not match runtime"
        )
    checks.append("run-id")

    terminal_control = manifest.get("terminal_control")
    if terminal_control is not None:
        mode = plan_mode(plan)
        if not isinstance(terminal_control, dict) or terminal_control.get("mode") != mode:
            raise CommandVideoError("Manifest terminal-control mode does not match the plan")
        if terminal_control.get("state_order") != terminal_control_state_order(mode):
            raise CommandVideoError("Manifest terminal-control lifecycle is incomplete or out of order")
        components = terminal_control.get("components")
        if not isinstance(components, dict) or any(
            not components.get(key)
            for key in (
                "recorder",
                "pty_allocator",
                "target",
                "renderer",
                "encoder",
                "media_probe",
            )
        ):
            raise CommandVideoError("Manifest terminal-control components are incomplete")
        if is_tui_mode(mode) and not components.get("multiplexer"):
            raise CommandVideoError("Manifest does not identify the TUI terminal multiplexer")
        if mode == "tui-sequence":
            component_targets = components.get("targets")
            if (
                not isinstance(component_targets, list)
                or len(component_targets) != len(plan_targets(plan))
            ):
                raise CommandVideoError(
                    "Manifest does not identify every TUI sequence target"
                )
        bridged_sessions = [
            session
            for session in plan_tui_sessions(plan)
            if launch_args_request_windows_working_directory(
                session["interaction"]["launch_args"]
            )
        ]
        if bridged_sessions:
            component_bridges = components.get("windows_working_directory_bridges")
            bridge_preflights = manifest.get("toolchain", {}).get(
                "windows_working_directory_bridges"
            )
            if (
                not isinstance(component_bridges, list)
                or not isinstance(bridge_preflights, list)
                or len(component_bridges) != len(bridged_sessions)
                or len(bridge_preflights) != len(bridged_sessions)
            ):
                raise CommandVideoError(
                    "Manifest does not identify every Windows working-directory bridge"
                )
            for planned_session, bridge_preflight in zip(
                bridged_sessions, bridge_preflights, strict=True
            ):
                if (
                    not isinstance(bridge_preflight, dict)
                    or bridge_preflight.get("session_id") != planned_session["id"]
                    or bridge_preflight.get("mode") != "temporary-subst-drive"
                    or bridge_preflight.get("token")
                    != WINDOWS_WORKING_DIRECTORY_TOKEN
                ):
                    raise CommandVideoError(
                        "Manifest Windows working-directory bridge preflight is incomplete"
                    )
                target_spec = planned_session["target"]
                if "lazygit" in str(target_spec.get("name", "")).lower() or "lazygit" in str(
                    target_spec.get("executable", "")
                ).lower():
                    longpaths = bridge_preflight.get("lazygit_longpaths")
                    if (
                        not isinstance(longpaths, dict)
                        or longpaths.get("status") != "passed"
                        or longpaths.get("scope") != "project-local"
                        or longpaths.get("setting") != "core.longpaths"
                        or longpaths.get("value") is not True
                    ):
                        raise CommandVideoError(
                            "Manifest does not prove project-local lazygit long-path support"
                        )
                    checks.append("lazygit-project-longpaths")
            checks.append("windows-working-directory-bridges")
        checks.append("terminal-control-lifecycle")

    planned_start = render_start_at(plan)
    planned_end = render_end_at(plan)
    presentation = manifest.get("presentation")
    presentation_trim_seconds = 0.0
    presentation_end_seconds = float(cast_info["duration_seconds"])
    if presentation is None:
        if planned_start != "recording" or planned_end == "before-final-key":
            raise CommandVideoError("Manifest is missing the requested TUI presentation evidence")
    else:
        if not isinstance(presentation, dict) or presentation.get("start_at") != planned_start:
            raise CommandVideoError("Manifest presentation start does not match the plan")
        try:
            presentation_trim_seconds = float(presentation.get("trim_leading_seconds", 0.0))
            source_cast_duration = float(presentation.get("source_cast_duration_seconds"))
        except (TypeError, ValueError) as exc:
            raise CommandVideoError("Manifest presentation timing is invalid") from exc
        if abs(source_cast_duration - float(cast_info["duration_seconds"])) > 0.01:
            raise CommandVideoError("Manifest presentation cast duration does not match the cast")
        if planned_start == "recording":
            if abs(presentation_trim_seconds) > 0.001:
                raise CommandVideoError("Recording-start presentation cannot trim the cast")
        else:
            ready_marker_seconds = cast_output_text_time(
                cast_path, marker(runtime["run_id"], "TUI", "READY")
            )
            expected_trim = max(
                0.0,
                ready_marker_seconds - tui_ready_presentation_lead_seconds(plan),
            )
            if abs(presentation_trim_seconds - expected_trim) > 0.01:
                raise CommandVideoError("Manifest TUI-ready trim does not match the cast marker")
            if abs(float(presentation.get("ready_marker_seconds", -1.0)) - ready_marker_seconds) > 0.01:
                raise CommandVideoError("Manifest TUI-ready marker time does not match the cast")
            if presentation_trim_seconds <= 0:
                raise CommandVideoError("TUI-ready presentation did not remove the controller lead-in")
            checks.append("tui-ready-presentation")

        if is_tui_mode(plan_mode(plan)) and planned_end == "before-final-key":
            final_key_marker_seconds = cast_output_text_time(
                cast_path, marker(runtime["run_id"], "TUI", "FINAL-KEY")
            )
            expected_presentation_end = final_key_marker_seconds
            expected_trailing_trim = max(
                0.0, float(cast_info["duration_seconds"]) - expected_presentation_end
            )
            if presentation.get("end_at") != "before-final-key":
                raise CommandVideoError(
                    "Manifest TUI presentation does not end before the final key"
                )
            if (
                abs(
                    float(presentation.get("final_key_marker_seconds", -1.0))
                    - final_key_marker_seconds
                )
                > 0.01
            ):
                raise CommandVideoError(
                    "Manifest final-key marker time does not match the cast"
                )
            if (
                abs(
                    float(presentation.get("presentation_end_seconds", -1.0))
                    - expected_presentation_end
                )
                > 0.01
            ):
                raise CommandVideoError(
                    "Manifest before-final-key presentation end does not match the cast"
                )
            if (
                abs(
                    float(presentation.get("trim_trailing_seconds", -1.0))
                    - expected_trailing_trim
                )
                > 0.01
            ):
                raise CommandVideoError("Manifest trailing trim does not match the cast")
            if (
                abs(
                    float(presentation.get("final_hold_seconds", -1.0))
                    - float(plan.data["render"]["last_frame_duration"])
                )
                > 0.001
            ):
                raise CommandVideoError("Manifest final TUI hold does not match the plan")
            if expected_presentation_end <= presentation_trim_seconds:
                raise CommandVideoError(
                    "The final-key marker occurred before the user-facing presentation began"
                )
            presentation_end_seconds = expected_presentation_end
            checks.append("before-final-key-presentation")
        elif planned_start != "recording":
            terminal_restore_seconds = cast_output_text_time(
                cast_path,
                "\033[?1049l",
                last=(plan_mode(plan) == "tui-sequence"),
            )
            expected_presentation_end = max(
                0.0, terminal_restore_seconds - TUI_EXIT_PRESENTATION_MARGIN_SECONDS
            )
            expected_trailing_trim = max(
                0.0, float(cast_info["duration_seconds"]) - expected_presentation_end
            )
            if presentation.get("end_at") != "tui-exit":
                raise CommandVideoError("Manifest TUI presentation does not end at TUI exit")
            if (
                abs(
                    float(presentation.get("terminal_restore_seconds", -1.0))
                    - terminal_restore_seconds
                )
                > 0.01
            ):
                raise CommandVideoError("Manifest terminal-restore time does not match the cast")
            if (
                abs(
                    float(presentation.get("presentation_end_seconds", -1.0))
                    - expected_presentation_end
                )
                > 0.01
            ):
                raise CommandVideoError("Manifest TUI presentation end does not match the cast")
            if (
                abs(
                    float(presentation.get("trim_trailing_seconds", -1.0))
                    - expected_trailing_trim
                )
                > 0.01
            ):
                raise CommandVideoError("Manifest trailing trim does not match the cast")
            if (
                abs(
                    float(presentation.get("final_hold_seconds", -1.0))
                    - float(plan.data["render"]["last_frame_duration"])
                )
                > 0.001
            ):
                raise CommandVideoError("Manifest final TUI hold does not match the plan")
            presentation_end_seconds = expected_presentation_end
            checks.append("tui-exit-presentation")

    env = dict(os.environ)
    env["PATH"] = path_with_tools(env, tools_dir)
    ffprobe = resolve_executable(
        ffprobe_name, working_directory=manifest_path.parent, path_value=env["PATH"]
    )
    probe, _ = probe_video(mp4_path, ffprobe=ffprobe, cwd=manifest_path.parent, env=env)
    expected_fps = float(plan.data["render"]["fps"])
    if abs(float(probe["avg_frame_rate_decimal"]) - expected_fps) > 0.05:
        raise CommandVideoError(
            f"MP4 frame rate is {probe['avg_frame_rate_decimal']}, expected {expected_fps}"
        )
    if is_tui_mode(plan_mode(plan)) and plan.data["render"]["idle_time_limit"] is None:
        expected_timeline_seconds = max(
            0.0,
            presentation_end_seconds - presentation_trim_seconds,
        )
        if planned_end == "before-final-key":
            expected_timeline_seconds += float(plan.data["render"]["last_frame_duration"])
        if float(probe["duration_seconds"]) + 0.25 < expected_timeline_seconds:
            raise CommandVideoError("MP4 is shorter than the preserved real-time TUI presentation")
        checks.append("real-time-duration")
    manifest_probe = manifest.get("video_probe", {})
    for key in ("codec_name", "pix_fmt", "width", "height"):
        if manifest_probe.get(key) != probe.get(key):
            raise CommandVideoError(f"Manifest video probe mismatch for {key}")
    checks.extend(["ffprobe", "h264", "yuv420p", "even-dimensions", "frame-rate"])
    return {
        "status": "passed",
        "plan_sha256": plan.sha256,
        "cast_sha256": sha256_file(cast_path),
        "mp4_sha256": sha256_file(mp4_path),
        "run_id": runtime["run_id"],
        "target": runtime["target"],
        "targets": runtime.get("targets", [runtime["target"]]),
        "tui_sessions": runtime.get("tui_sessions", []),
        "prompt_count": len(plan_steps(plan)),
        "presentation": (
            presentation
            if isinstance(presentation, dict)
            else {
                "start_at": "recording",
                "trim_leading_seconds": 0.0,
                "source_cast_duration_seconds": float(cast_info["duration_seconds"]),
            }
        ),
        "video_probe": probe,
        "checks": sorted(set(checks)),
    }


def add_common_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")


def add_recording_tool_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tools-dir")
    parser.add_argument("--asciinema", default="asciinema")
    parser.add_argument("--agg", default="agg")
    parser.add_argument("--tmux", default="tmux")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record real prompt-driven terminal commands with Asciinema and render verified MP4s."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_plan_parser = subparsers.add_parser("validate-plan", help="Validate a session plan without executing it")
    validate_plan_parser.add_argument("plan")
    add_common_json_flag(validate_plan_parser)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-tools", help="Download pinned official Asciinema and agg binaries locally"
    )
    bootstrap_parser.add_argument("--directory", required=True)
    add_common_json_flag(bootstrap_parser)

    preflight_parser = subparsers.add_parser(
        "preflight", help="Verify the recorder, PTY controller, target, and converters before recording"
    )
    preflight_parser.add_argument("plan")
    add_recording_tool_args(preflight_parser)
    add_common_json_flag(preflight_parser)

    run_parser = subparsers.add_parser("run-plan", help=argparse.SUPPRESS)
    run_parser.add_argument("--plan", required=True)
    run_parser.add_argument("--report", required=True)
    run_parser.add_argument("--run-id", required=True)

    tui_target_parser = subparsers.add_parser("run-tui-target", help=argparse.SUPPRESS)
    tui_target_parser.add_argument("--plan", required=True)
    tui_target_parser.add_argument("--status", required=True)
    tui_target_parser.add_argument("--gate", required=True)
    tui_target_parser.add_argument("--run-id", required=True)
    tui_target_parser.add_argument("--session-id")

    tui_sequence_parser = subparsers.add_parser(
        "run-tui-sequence-targets", help=argparse.SUPPRESS
    )
    tui_sequence_parser.add_argument("--plan", required=True)
    tui_sequence_parser.add_argument("--state-directory", required=True)
    tui_sequence_parser.add_argument("--run-id", required=True)

    record_parser = subparsers.add_parser("record", help="Record a plan and render its MP4")
    record_parser.add_argument("plan")
    record_parser.add_argument("--cast", required=True)
    record_parser.add_argument("--mp4", required=True)
    record_parser.add_argument("--manifest", required=True)
    record_parser.add_argument("--runtime-report")
    record_parser.add_argument("--gif", help="Optionally retain the agg GIF intermediary")
    add_recording_tool_args(record_parser)
    add_common_json_flag(record_parser)

    validate_parser = subparsers.add_parser("validate", help="Independently validate existing artifacts")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--cast", required=True)
    validate_parser.add_argument("--mp4", required=True)
    validate_parser.add_argument("--manifest", required=True)
    validate_parser.add_argument("--tools-dir")
    validate_parser.add_argument("--ffprobe", default="ffprobe")
    add_common_json_flag(validate_parser)
    return parser


def print_result(payload: Mapping[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Status: {payload.get('status', 'unknown')}")
        for key, value in payload.items():
            if key != "status" and isinstance(value, (str, int, float)):
                print(f"{key}: {value}")


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
    raw_argv = list(argv if argv is not None else sys.argv[1:])
    if os.name == "nt" and raw_argv and raw_argv[0] in {
        "bootstrap-tools",
        "preflight",
        "record",
        "validate",
    } and not any(token in {"-h", "--help"} for token in raw_argv[1:]):
        try:
            return forward_windows_command_to_wsl(raw_argv)
        except CommandVideoError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
    parser = build_parser()
    args = parser.parse_args(raw_argv)
    try:
        if args.command == "validate-plan":
            result = plan_summary(load_plan(args.plan))
            print_result(result, as_json=args.json)
            return 0
        if args.command == "bootstrap-tools":
            result = bootstrap_tools(Path(args.directory))
            print_result(result, as_json=args.json)
            return 0
        if args.command == "preflight":
            result = preflight_session(args)
            print_result(result, as_json=args.json)
            return 0
        if args.command == "run-plan":
            return execute_plan(
                load_plan(args.plan),
                report_path=Path(args.report),
                run_id=args.run_id,
            )
        if args.command == "run-tui-target":
            return execute_tui_target(
                load_plan(args.plan),
                status_path=Path(args.status),
                gate_path=Path(args.gate),
                run_id=args.run_id,
                session_id=args.session_id,
            )
        if args.command == "run-tui-sequence-targets":
            return execute_tui_sequence_targets(
                load_plan(args.plan),
                state_directory=Path(args.state_directory),
                run_id=args.run_id,
            )
        if args.command == "record":
            result = record_session(args)
            print_result(result, as_json=args.json)
            return 0
        if args.command == "validate":
            result = validate_existing_artifacts(
                plan_path=Path(args.plan),
                cast_path=Path(args.cast),
                mp4_path=Path(args.mp4),
                manifest_path=Path(args.manifest),
                ffprobe_name=args.ffprobe,
                tools_dir=Path(args.tools_dir) if args.tools_dir else None,
            )
            print_result(result, as_json=args.json)
            return 0
        raise CommandVideoError(f"Unsupported command: {args.command}")
    except CommandVideoError as exc:
        error_payload = {"status": "failed", "error": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(error_payload, indent=2, ensure_ascii=False), file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
