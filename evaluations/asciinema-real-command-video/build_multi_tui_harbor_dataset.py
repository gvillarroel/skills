#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a frozen Harbor cohort for long sequential multi-tool TUI videos."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any


HELPER_ROOT = Path(__file__).resolve().parent
BASE_BUILDER_PATH = HELPER_ROOT / "build_harbor_dataset.py"
BASE_SPEC = importlib.util.spec_from_file_location(
    "asciinema_multi_tui_base_builder", BASE_BUILDER_PATH
)
if BASE_SPEC is None or BASE_SPEC.loader is None:
    raise RuntimeError(f"Cannot load base dataset builder: {BASE_BUILDER_PATH}")
BASE = importlib.util.module_from_spec(BASE_SPEC)
sys.modules[BASE_SPEC.name] = BASE
BASE_SPEC.loader.exec_module(BASE)


def multi_tui_contract(
    task_id: str,
    split: str,
    case_type: str,
    session_ids: list[str],
    target_names: list[str],
    executable_sequence: list[list[str]],
    prompt_count: int,
    required_cast_terms: list[str],
    *,
    required_prompt_sequence: list[str] | None = None,
    required_text_sequence: list[str] | None = None,
    required_key_sequence: list[str] | None = None,
    min_action_count: int = 0,
    min_pause_action_count: int = 0,
    min_planned_pause_seconds: float = 0.0,
    min_source_duration_seconds: float = 0.0,
    any_cast_term_groups: list[list[str]] | None = None,
    required_checks: list[str] | None = None,
    min_duration_seconds: float = 10.5,
    max_duration_seconds: float = 600.0,
) -> dict[str, Any]:
    flattened_executables = list(
        dict.fromkeys(
            executable
            for executable_group in executable_sequence
            for executable in executable_group
        )
    )
    result = BASE.contract(
        task_id,
        split,
        case_type,
        "multi-tool-tui-sequence",
        flattened_executables,
        "tui-sequence",
        prompt_count,
        required_cast_terms,
        any_cast_term_groups=any_cast_term_groups,
        required_checks=required_checks,
        require_target_only=True,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        fps=30,
    )
    result.update(
        {
            "schemaVersion": 3,
            "sessionIds": session_ids,
            "targetNames": target_names,
            "executableSequence": executable_sequence,
            "requiredPromptSequence": required_prompt_sequence or [],
            "requiredTextSequence": required_text_sequence or [],
            "requiredKeySequence": required_key_sequence or [],
            "minActionCount": min_action_count,
            "minPauseActionCount": min_pause_action_count,
            "minPlannedPauseSeconds": min_planned_pause_seconds,
            "minSourceDurationSeconds": min_source_duration_seconds,
        }
    )
    return result


COMMON_MULTI_CHECKS = [
    "single-record-attempt",
    "multi-tui-sequence",
    "multi-target-provenance",
    "tui-session-boundaries",
    "explicit-tui-actions",
    "action-markers",
    "timed-keystrokes",
    "enter-submission",
    "target-exit",
    "target-exit-completion",
    "tui-ready-presentation",
    "tui-exit-presentation",
    "real-time-duration",
]


HOLDOUT_COPILOT_PROMPT = (
    "Reply with exactly: MULTI TUI COPILOT COMPLETE. Do not use tools."
)


TASKS = (
    BASE.TaskSpec(
        split="development",
        task_id="multi-tui-dev-fzf-television",
        instruction="""Create two reviewed picker fixtures under `fixture/`.
`fzf-items.txt` must contain `alpha`, `beta`, `gamma`, and `omega`; `tv-items.txt`
must contain `alpha.txt`, `beta.txt`, `gamma.txt`, and `omega.txt`, each in that
order and one value per line.

Record one continuous multi-TUI session with exactly these ordered session IDs
and real targets:

1. `fzf-picker`: launch `fzf.exe` with prompt `QUERY> ` and the deterministic
   PowerShell start/reload source binding. After ready, pause 2.5 seconds, type
   `gam`, pause 3.5 seconds, and press Enter. The real `gamma` selection must
   exit fzf with status 0.
2. `television-picker`: launch `tv.exe` as an ad-hoc channel over `tv-items.txt`
   with source output `{}`, preview/remote/help disabled, and input prompt
   `FILTER> `. After ready, pause 2.5 seconds, type `bet`, pause 3.5 seconds,
   and press Enter. The real `beta.txt` selection must exit Television with
   status 0.

Use one top-level `tui_sessions` plan, one Asciinema transaction, one attached
tmux PTY, `tui-ready` presentation, target-exit ending, real speed, and no idle
cap. The MP4 must exceed 11.5 seconds and the untrimmed cast 15 seconds. Both
authentic UIs and the handoff must be visible; do not create separate clips or
a shell imitation."""
        + BASE.COMMON_TAIL,
        contract=multi_tui_contract(
            "multi-tui-dev-fzf-television",
            "development",
            "long-two-picker-tui-sequence",
            ["fzf-picker", "television-picker"],
            ["fzf", "Television"],
            [["fzf.exe", "fzf"], ["tv.exe", "tv"]],
            2,
            ["QUERY>", "gamma", "FILTER>", "beta.txt"],
            required_text_sequence=["gam", "bet"],
            required_key_sequence=["Enter", "Enter"],
            min_action_count=8,
            min_pause_action_count=4,
            min_planned_pause_seconds=12.0,
            min_source_duration_seconds=15.0,
            required_checks=COMMON_MULTI_CHECKS,
            min_duration_seconds=11.5,
        ),
    ),
    BASE.TaskSpec(
        split="validation",
        task_id="multi-tui-val-television-fzf-lazygit",
        instruction="""Create `fixture/repo` as a small real Git repository with
one committed `src.txt`, a visible uncommitted modification to it, and an
untracked `todo.md`. Put `tv-items.txt` (`alpha.txt`, `delta.txt`, `omega.txt`)
and `fzf-items.txt` (`alpha`, `theta`, `omega`) inside that repository. Copy the
skill's deterministic lazygit config to `.git/lazygit-config/config.yml` and
set only this repository's `core.longpaths` to true.

Use `working_directory: ../fixture/repo` and record one continuous three-tool
TUI sequence with these exact sessions:

1. `television-first`: real `tv.exe`, ad-hoc source `tv-items.txt`, `{}` output,
   no preview/remote/help, prompt `FILTER> `; pause 1.5 seconds, type `del`,
   pause 2.5 seconds, Enter, and prove real `delta.txt` selection/status 0.
2. `fzf-second`: real `fzf.exe`, deterministic PowerShell reload of
   `fzf-items.txt`, prompt `QUERY> `; pause 1.5 seconds, type `the`, pause 2.5
   seconds, Enter, and prove real `theta` selection/status 0.
3. `lazygit-final`: real `lazygit.exe` using the reviewed temporary
   `{windows_working_directory}` bridge for both its config directory and repo
   path. After its Files/branches UI is ready, pause 2 seconds, key `Down`,
   pause 2 seconds, key `Tab`, pause 2 seconds, then key `q` to exit status 0.

Use `tui-ready`, `before-final-key`, a positive final hold, real speed, and no
idle cap. The MP4 must exceed 14.5 seconds and the source cast 19 seconds. The
video must show all three real UIs in order; the held final frame must be the
authentic lazygit screen before `q`."""
        + BASE.COMMON_TAIL,
        contract=multi_tui_contract(
            "multi-tui-val-television-fzf-lazygit",
            "validation",
            "long-three-tool-bridge-tui-sequence",
            ["television-first", "fzf-second", "lazygit-final"],
            ["Television", "fzf", "lazygit"],
            [
                ["tv.exe", "tv"],
                ["fzf.exe", "fzf"],
                ["lazygit.exe", "lazygit"],
            ],
            3,
            ["FILTER>", "delta.txt", "QUERY>", "theta", "lazygit", "src.txt"],
            required_text_sequence=["del", "the"],
            required_key_sequence=["Enter", "Enter", "Down", "Tab", "q"],
            min_action_count=13,
            min_pause_action_count=7,
            min_planned_pause_seconds=14.0,
            min_source_duration_seconds=19.0,
            required_checks=[
                *[
                    check
                    for check in COMMON_MULTI_CHECKS
                    if check != "tui-exit-presentation"
                ],
                "command-keys",
                "before-final-key-marker",
                "before-final-key-presentation",
                "windows-working-directory-bridge",
                "windows-working-directory-bridges",
                "lazygit-path-clean",
                "lazygit-project-longpaths",
            ],
            min_duration_seconds=14.5,
        ),
    ),
    BASE.TaskSpec(
        split="holdout",
        task_id="multi-tui-holdout-copilot-television",
        instruction=f"""Create `fixture/tv-items.txt` with `amber.txt`,
`cobalt.txt`, and `violet.txt`, in that order and one per line. Record one
continuous two-tool TUI sequence with these exact sessions:

1. `copilot-first`: launch the authentic `copilot.exe` persistent TUI exactly
   once with auto-update, remote sessions/export, mouse, custom instructions,
   and experimental features disabled. Type the exact prompt
   `{HOLDOUT_COPILOT_PROMPT}` character by character, show it before real
   Enter, wait for Copilot's real busy footer to clear and stable empty editor,
   then type `/exit` through the same PTY. No Copilot tools or file access are
   authorized.
2. `television-final`: launch real `tv.exe` over `tv-items.txt` with an ad-hoc
   channel, source output `{{}}`, preview/remote/help disabled, and input prompt
   `FILTER> `. Pause 2.5 seconds, type `vio`, pause 5.5 seconds, and press Enter
   to select real `violet.txt` and exit status 0.

Use a top-level `tui_sessions` plan, one Asciinema/tmux transaction,
`tui-ready`, target-exit ending, real speed, and no idle cap. The MP4 must
exceed 14 seconds and the untrimmed cast 18 seconds. The visible video must
begin in the real Copilot TUI, include its real response and exit, hand off to
the real Television UI, and end there. Do not pre-render, splice, simulate, or
run either tool outside the one claimed recording."""
        + BASE.COMMON_TAIL,
        contract=multi_tui_contract(
            "multi-tui-holdout-copilot-television",
            "holdout",
            "long-persistent-plus-picker-tui-sequence",
            ["copilot-first", "television-final"],
            ["GitHub Copilot CLI", "Television"],
            [["copilot.exe", "copilot"], ["tv.exe", "tv"]],
            2,
            [
                "MULTI TUI COPILOT COMPLETE",
                "/exit",
                "FILTER>",
                "violet.txt",
            ],
            required_prompt_sequence=[HOLDOUT_COPILOT_PROMPT],
            required_text_sequence=["vio"],
            required_key_sequence=["Enter"],
            min_action_count=4,
            min_pause_action_count=2,
            min_planned_pause_seconds=8.0,
            min_source_duration_seconds=18.0,
            required_checks=COMMON_MULTI_CHECKS,
            min_duration_seconds=14.0,
        ),
    ),
)


def task_fingerprint(spec: Any) -> str:
    payload = spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_specs() -> dict[str, Any]:
    expected_counts = {"development": 1, "validation": 1, "holdout": 1}
    counts = Counter(spec.split for spec in TASKS)
    if dict(counts) != expected_counts:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    task_ids = [spec.task_id for spec in TASKS]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Task IDs must be unique.")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item) for item in task_ids):
        raise ValueError("Task IDs must be lowercase hyphen-case.")
    fingerprints = [task_fingerprint(spec) for spec in TASKS]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Task contracts must be byte-disjoint.")
    for spec in TASKS:
        contract = spec.contract
        if contract["schemaVersion"] != 3:
            raise ValueError(f"Multi-TUI contract must use schema version 3: {spec.task_id}")
        if contract["taskId"] != spec.task_id or contract["split"] != spec.split:
            raise ValueError(f"Contract identity mismatch: {spec.task_id}")
        if not (
            len(contract["sessionIds"])
            == len(contract["targetNames"])
            == len(contract["executableSequence"])
            and len(contract["sessionIds"]) >= 2
        ):
            raise ValueError(f"Multi-TUI sequence shape mismatch: {spec.task_id}")
        if contract["minDurationSeconds"] <= 10.0:
            raise ValueError(f"Multi-TUI MP4 duration gate is too short: {spec.task_id}")
        if contract["minSourceDurationSeconds"] <= contract["minDurationSeconds"]:
            raise ValueError(f"Source cast duration gate is too short: {spec.task_id}")
    return {
        "taskCount": len(TASKS),
        "splitCounts": expected_counts,
        "multiTuiTaskCount": len(TASKS),
        "twoToolTaskCount": sum(len(spec.contract["sessionIds"]) == 2 for spec in TASKS),
        "threeToolTaskCount": sum(len(spec.contract["sessionIds"]) == 3 for spec in TASKS),
        "longVideoTaskCount": len(TASKS),
        "authorizedMutationCount": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--model", default="openai-codex/gpt-5.6-luna")
    parser.add_argument("--pi-version", default="0.84.2")
    parser.add_argument(
        "--runtime-resource-root",
        type=Path,
        help="Optional repository root containing the shared Harbor cache and recording tools.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.run_id):
        raise SystemExit("--run-id must be lowercase hyphen-case.")
    if args.attempts < 1:
        raise SystemExit("--attempts must be positive.")
    output_root = args.output_root.resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Refusing non-empty output directory: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    repo_root = HELPER_ROOT.parents[1]
    verifier_source = HELPER_ROOT / "verify_task.py"
    if not verifier_source.is_file():
        raise SystemExit(f"Verifier source is missing: {verifier_source}")

    stats = validate_specs()
    for spec in TASKS:
        BASE.write_task(output_root, spec, verifier_source)
    configs = {
        split: str(
            BASE.write_job_config(
                output_root,
                repo_root,
                split,
                args.run_id,
                args.attempts,
                args.model,
                args.pi_version,
                args.runtime_resource_root,
            )
        )
        for split in ("development", "validation", "holdout")
    }
    split_digests = {
        split: BASE.tree_digest(output_root / split)
        for split in ("development", "validation", "holdout")
    }
    manifest = {
        "schemaVersion": 3,
        "runId": args.run_id,
        "harborVersion": "0.18.0",
        "agent": "pi",
        "agentAdapter": "WorkspaceWindowsPi",
        "piVersion": args.pi_version,
        "model": args.model,
        "attempts": args.attempts,
        "concurrency": 1,
        "stats": stats,
        "splitDigests": split_digests,
        "jobConfigs": configs,
        "evaluationPolicy": (
            "Run development and validation, freeze the candidate digest, then release "
            "the untouched holdout once. Preserve every one-attempt artifact and require "
            "ordered multi-target process, action, cast, presentation, and media evidence."
        ),
    }
    (output_root / "dataset-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
