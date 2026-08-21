#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a frozen complex and long-form Harbor terminal-video cohort."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


HELPER_ROOT = Path(__file__).resolve().parent
BASE_BUILDER_PATH = HELPER_ROOT / "build_harbor_dataset.py"
BASE_SPEC = importlib.util.spec_from_file_location(
    "asciinema_harbor_base_builder", BASE_BUILDER_PATH
)
if BASE_SPEC is None or BASE_SPEC.loader is None:
    raise RuntimeError(f"Cannot load base dataset builder: {BASE_BUILDER_PATH}")
BASE = importlib.util.module_from_spec(BASE_SPEC)
sys.modules[BASE_SPEC.name] = BASE
BASE_SPEC.loader.exec_module(BASE)


def complex_contract(
    task_id: str,
    split: str,
    case_type: str,
    target_name: str,
    executable_names: list[str],
    mode: str,
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
    require_target_only: bool = False,
    min_duration_seconds: float = 1.0,
    max_duration_seconds: float = 600.0,
    fps: int = 30,
) -> dict[str, Any]:
    result = BASE.contract(
        task_id,
        split,
        case_type,
        target_name,
        executable_names,
        mode,
        prompt_count,
        required_cast_terms,
        any_cast_term_groups=any_cast_term_groups,
        required_checks=required_checks,
        require_target_only=require_target_only,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        fps=fps,
    )
    result.update(
        {
            "schemaVersion": 2,
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


COPILOT_PROMPTS = [
    "Reply with exactly: COMPLEX COPILOT STEP ONE. Do not use tools.",
    "Using the previous reply as context, reply with exactly: COMPLEX COPILOT STEP TWO. Do not use tools.",
    "Reply with exactly: COMPLEX COPILOT STEP THREE COMPLETE. Do not use tools.",
]

GH_REPOSITORIES = ["cli/cli", "github/gitignore", "microsoft/terminal"]


TASKS = (
    BASE.TaskSpec(
        split="development",
        task_id="complex-dev-copilot-three-prompt-tui",
        instruction="""Record one authentic persistent GitHub Copilot CLI TUI
session with three context-preserving turns. Launch `copilot.exe` exactly once
with auto-update, remote sessions and export, mouse input, custom instructions,
and experimental features disabled. Type these exact prompts character by
character and submit each with a real Enter only after the complete text is
visible:

1. `Reply with exactly: COMPLEX COPILOT STEP ONE. Do not use tools.`
2. `Using the previous reply as context, reply with exactly: COMPLEX COPILOT STEP TWO. Do not use tools.`
3. `Reply with exactly: COMPLEX COPILOT STEP THREE COMPLETE. Do not use tools.`

Wait after each turn until Copilot's real busy footer clears and its empty
editor is stably ready. After the third response, type `/exit` through the same
PTY and retain Copilot's own session summary. Set render speed to 1.0 with no
idle cap and start the MP4 at `tui-ready`. The MP4 must exceed 10.5 seconds and
the untrimmed source cast must exceed 14 seconds. No tool use, file access,
shell command, remote action, or repository mutation is authorized."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-dev-copilot-three-prompt-tui",
            "development",
            "long-contextual-conversational-tui",
            "GitHub Copilot CLI",
            ["copilot.exe", "copilot"],
            "tui",
            3,
            [
                "COMPLEX COPILOT STEP ONE",
                "COMPLEX COPILOT STEP TWO",
                "COMPLEX COPILOT STEP THREE COMPLETE",
                "/exit",
            ],
            required_prompt_sequence=COPILOT_PROMPTS,
            required_checks=[
                "single-record-attempt",
                "timed-keystrokes",
                "enter-submission",
                "tui-ready-marker",
                "tui-ready-presentation",
                "tui-final-hold",
                "tui-exit-presentation",
                "target-exit",
                "real-time-duration",
            ],
            require_target_only=True,
            min_duration_seconds=10.5,
            min_source_duration_seconds=14.0,
        ),
    ),
    BASE.TaskSpec(
        split="development",
        task_id="complex-dev-fzf-edit-navigate-tui",
        instruction="""Create `fixture/fzf-items.txt` with exactly these values,
one per line and in this order: `alpha`, `beta`, `delta`, `gamma`, `iota`,
`theta`, `zeta`, and `omega`. Record the real `fzf.exe` full-screen picker and
load only that fixture with the deterministic start/reload binding documented
by the skill. Use prompt label `QUERY> `.

After the real picker is ready, execute exactly this explicit action sequence:
text `taz`; pause 2.5 seconds; key `BSpace`; pause 2.5 seconds; key `Down`;
pause 2.5 seconds; key `Down`; pause 2.5 seconds; key `Up`; key `Enter`.
The intermediate typo and correction must remain visible. Enter must select a
real result and end fzf with status 0; accept any result that actually matches
the corrected `ta` query. Use `target-exit`, render from `tui-ready`, and keep
the real-speed MP4 over 10.5 seconds and source cast over 13 seconds. No fake
picker, input loop, or synthetic shell UI is allowed."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-dev-fzf-edit-navigate-tui",
            "development",
            "long-edit-navigation-picker-tui",
            "fzf",
            ["fzf.exe", "fzf"],
            "tui",
            1,
            ["QUERY>", "taz"],
            required_text_sequence=["taz"],
            required_key_sequence=["BSpace", "Down", "Down", "Up", "Enter"],
            min_action_count=10,
            min_pause_action_count=4,
            min_planned_pause_seconds=10.0,
            min_source_duration_seconds=13.0,
            any_cast_term_groups=[["beta", "delta", "iota", "theta", "zeta"]],
            required_checks=[
                "single-record-attempt",
                "explicit-tui-actions",
                "action-markers",
                "timed-keystrokes",
                "command-keys",
                "enter-submission",
                "target-exit",
                "target-exit-completion",
                "tui-ready-presentation",
                "tui-exit-presentation",
                "real-time-duration",
            ],
            require_target_only=True,
            min_duration_seconds=10.5,
        ),
    ),
    BASE.TaskSpec(
        split="development",
        task_id="complex-dev-staged-pipeline-argv",
        instruction="""Record one real long-running PowerShell pipeline in
direct-argv mode with target `pwsh.exe`. Use the exact inert prompt
`complex-pipeline-sentinel` as the only argument following `-CommandWithArgs`.
Keep the PowerShell source fixed in the plan. It must process the fixed values
`discover`, `filter`, `aggregate`, and `complete` through a real pipeline,
print `STAGE=DISCOVER`, `STAGE=FILTER`, `STAGE=AGGREGATE`, and
`STAGE=COMPLETE` in that order, wait exactly three seconds after each stage,
then print `LABEL=complex-pipeline-sentinel` from `$args[0]`.

Do not interpolate the label into PowerShell syntax. Preserve speed 1.0 with
no idle-time cap. Both the MP4 and untrimmed cast must prove more than 12
seconds of authentic execution. No filesystem, network, or host mutation is
authorized."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-dev-staged-pipeline-argv",
            "development",
            "long-staged-fixed-pipeline-argv",
            "PowerShell",
            ["pwsh.exe", "pwsh"],
            "argv",
            1,
            [
                "STAGE=DISCOVER",
                "STAGE=FILTER",
                "STAGE=AGGREGATE",
                "STAGE=COMPLETE",
                "LABEL=complex-pipeline-sentinel",
            ],
            required_prompt_sequence=["complex-pipeline-sentinel"],
            required_checks=[
                "single-record-attempt",
                "target-exit",
                "real-time-duration",
            ],
            min_duration_seconds=12.0,
            min_source_duration_seconds=12.0,
        ),
    ),
    BASE.TaskSpec(
        split="validation",
        task_id="complex-val-television-edit-navigate-tui",
        instruction="""Create `fixture/tv-items.txt` with exactly these values,
one per line and in this order: `alpha.txt`, `beta.txt`, `delta.txt`,
`gamma.txt`, `iota.txt`, `theta.txt`, `zeta.txt`, and `omega.txt`. Record the
real Television 0.14.x `tv.exe` picker with an ad-hoc channel that reads only
this fixture. Disable preview, remote control, and the help panel; use source
output `{}` and input label `FILTER> `.

After Television is ready, execute exactly this action sequence: text `taz`;
pause 2.5 seconds; key `BSpace`; pause 2.5 seconds; key `Down`; pause 2.5
seconds; key `Up`; pause 2.5 seconds; key `Enter`. The typo, correction, and
navigation must be visible. Enter must select a real corrected-query result
and end Television with status 0. Use `target-exit`, render from `tui-ready`,
and keep the real-speed MP4 over 10.5 seconds and source cast over 13 seconds.
Do not substitute another picker or a custom input loop."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-val-television-edit-navigate-tui",
            "validation",
            "long-edit-navigation-picker-tui",
            "Television",
            ["tv.exe", "tv"],
            "tui",
            1,
            ["FILTER>", "taz"],
            required_text_sequence=["taz"],
            required_key_sequence=["BSpace", "Down", "Up", "Enter"],
            min_action_count=9,
            min_pause_action_count=4,
            min_planned_pause_seconds=10.0,
            min_source_duration_seconds=13.0,
            any_cast_term_groups=[
                ["beta.txt", "delta.txt", "iota.txt", "theta.txt", "zeta.txt"]
            ],
            required_checks=[
                "single-record-attempt",
                "explicit-tui-actions",
                "action-markers",
                "timed-keystrokes",
                "command-keys",
                "enter-submission",
                "target-exit",
                "target-exit-completion",
                "tui-ready-presentation",
                "tui-exit-presentation",
                "real-time-duration",
            ],
            require_target_only=True,
            min_duration_seconds=10.5,
        ),
    ),
    BASE.TaskSpec(
        split="validation",
        task_id="complex-val-lazygit-panel-navigation-tui",
        instruction="""Create a local Git repository under `fixture/repo` with
three commits, a `feature/demo` branch, one staged tracked change in
`app.txt`, one unstaged tracked change in `notes.txt`, and one untracked file
named `draft.txt`. Configure a project-local lazygit directory with startup
popups disabled. Record the real `lazygit.exe` TUI in that repository.

After the authentic Files/branches/commits surface is stably ready, execute
exactly this action sequence: pause 2.5 seconds; key `Down`; pause 2.5 seconds;
key `Up`; pause 2.5 seconds; key `Tab`; pause 2.5 seconds; key `Tab`; pause 2.5
seconds; key `q`. The navigation must occur in the real interface. The final
`q` must end lazygit with status 0 without an invented Enter. Render from
`tui-ready` through `before-final-key`, hold the authentic frame preceding
`q`, and keep the MP4 over 12 seconds and source cast over 15 seconds. The full
cast/runtime report must retain proof of the real final key and process exit."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-val-lazygit-panel-navigation-tui",
            "validation",
            "long-panel-navigation-command-key-tui",
            "lazygit",
            ["lazygit.exe", "lazygit"],
            "tui",
            1,
            ["lazygit", "app.txt", "notes.txt"],
            required_key_sequence=["Down", "Up", "Tab", "Tab", "q"],
            min_action_count=10,
            min_pause_action_count=5,
            min_planned_pause_seconds=12.5,
            min_source_duration_seconds=15.0,
            required_checks=[
                "single-record-attempt",
                "explicit-tui-actions",
                "action-markers",
                "command-keys",
                "target-exit",
                "target-exit-completion",
                "tui-ready-presentation",
                "before-final-key-marker",
                "before-final-key-presentation",
                "real-time-duration",
            ],
            require_target_only=True,
            min_duration_seconds=12.0,
        ),
    ),
    BASE.TaskSpec(
        split="validation",
        task_id="complex-val-gh-three-repository-argv",
        instruction="""Record three real read-only GitHub CLI lookups in one
direct-argv session plan. Use target `gh.exe` and these exact prompts in this
order: `cli/cli`, `github/gitignore`, and `microsoft/terminal`. Each step must
use this fixed argument shape with its own `{prompt}` substitution:

`repo view {prompt} --json nameWithOwner,url,defaultBranchRef --jq .nameWithOwner + " | " + .defaultBranchRef.name + " | " + .url`

Keep every repository name as one argv item. The cast must show each real
repository name, its default branch, and its GitHub URL, with status 0 for all
three processes. Pause one second after the first and second lookups for
readability. This authorizes public network reads only; no issue, repository,
gist, release, or authentication mutation is allowed."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-val-gh-three-repository-argv",
            "validation",
            "multi-step-network-read-argv",
            "GitHub CLI",
            ["gh.exe", "gh"],
            "argv",
            3,
            [
                "cli/cli",
                "github/gitignore",
                "microsoft/terminal",
                "https://github.com/cli/cli",
                "https://github.com/github/gitignore",
                "https://github.com/microsoft/terminal",
            ],
            required_prompt_sequence=GH_REPOSITORIES,
            required_checks=[
                "single-record-attempt",
                "target-exit",
                "real-time-duration",
            ],
            min_duration_seconds=2.0,
            min_source_duration_seconds=2.0,
        ),
    ),
    BASE.TaskSpec(
        split="holdout",
        task_id="complex-holdout-television-long-edit-tui",
        instruction="""Create `fixture/tv-holdout-items.txt` with exactly these
values, one per line and in this order: `alpha.log`, `bravo.log`, `charlie.log`,
`delta.log`, `echo.log`, `foxtrot.log`, `golf.log`, `hotel.log`, `india.log`,
and `juliet.log`. Record the real Television 0.14.x `tv.exe` picker with an
ad-hoc channel that reads only this fixture. Disable preview, remote control,
and the help panel; use source output `{}` and input label `FILTER> `.

After the real picker is stable, execute exactly: text `ox`; pause 2.5 seconds;
key `BSpace`; pause 2.5 seconds; key `Down`; pause 2.5 seconds; key `Down`;
pause 2.5 seconds; key `Up`; pause 2.5 seconds; key `Enter`. The typo,
correction, and navigation must remain visible. Enter must select a real
result matching `o` and end Television with status 0. Use `target-exit`, render
from `tui-ready`, and keep the real-speed MP4 over 12 seconds and source cast
over 15 seconds. Do not substitute another picker or a custom input loop."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-holdout-television-long-edit-tui",
            "holdout",
            "long-double-navigation-picker-tui",
            "Television",
            ["tv.exe", "tv"],
            "tui",
            1,
            ["FILTER>", "ox"],
            required_text_sequence=["ox"],
            required_key_sequence=["BSpace", "Down", "Down", "Up", "Enter"],
            min_action_count=11,
            min_pause_action_count=5,
            min_planned_pause_seconds=12.5,
            min_source_duration_seconds=15.0,
            any_cast_term_groups=[["echo.log", "foxtrot.log", "golf.log", "hotel.log"]],
            required_checks=[
                "single-record-attempt",
                "explicit-tui-actions",
                "action-markers",
                "timed-keystrokes",
                "command-keys",
                "enter-submission",
                "target-exit",
                "target-exit-completion",
                "tui-ready-presentation",
                "tui-exit-presentation",
                "real-time-duration",
            ],
            require_target_only=True,
            min_duration_seconds=12.0,
        ),
    ),
    BASE.TaskSpec(
        split="holdout",
        task_id="complex-holdout-powershell-five-stage-argv",
        instruction="""Record one real timed PowerShell pipeline in direct-argv
mode with target `pwsh.exe`. Use the exact inert prompt
`holdout-pipeline-label` as the only argument following `-CommandWithArgs`.
Keep the PowerShell source fixed in the plan. It must process the fixed values
`prepare`, `scan`, `rank`, `package`, and `finish` through one real pipeline,
print `PHASE=PREPARE`, `PHASE=SCAN`, `PHASE=RANK`, `PHASE=PACKAGE`, and
`PHASE=FINISH` in that order, wait exactly 2.5 seconds after each phase, then
print `LABEL=holdout-pipeline-label` from `$args[0]`.

Do not interpolate the label into PowerShell syntax. Preserve speed 1.0 with
no idle-time cap. Both the MP4 and untrimmed source cast must exceed 12.5
seconds. No filesystem, network, package, or host mutation is authorized."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-holdout-powershell-five-stage-argv",
            "holdout",
            "long-five-stage-fixed-pipeline-argv",
            "PowerShell",
            ["pwsh.exe", "pwsh"],
            "argv",
            1,
            [
                "PHASE=PREPARE",
                "PHASE=SCAN",
                "PHASE=RANK",
                "PHASE=PACKAGE",
                "PHASE=FINISH",
                "LABEL=holdout-pipeline-label",
            ],
            required_prompt_sequence=["holdout-pipeline-label"],
            required_checks=[
                "single-record-attempt",
                "target-exit",
                "real-time-duration",
            ],
            min_duration_seconds=12.5,
            min_source_duration_seconds=12.5,
        ),
    ),
    BASE.TaskSpec(
        split="holdout",
        task_id="complex-holdout-lazygit-deep-path-tui",
        instruction="""Create a local Git repository under `fixture/repo` with
four commits, a `release/demo` branch, one staged tracked change in `src.txt`,
one unstaged tracked change in `todo.md`, and one untracked file named
`release-notes.txt`. Configure a project-local lazygit directory with startup
popups disabled. Record the real `lazygit.exe` TUI in that exact repository;
the Harbor workspace path is intentionally deep.

After the authentic Files/branches/commits surface is stably ready, execute
exactly: pause 2.25 seconds; key `Down`; pause 2.25 seconds; key `Down`; pause
2.25 seconds; key `Up`; pause 2.25 seconds; key `Tab`; pause 2.25 seconds; key
`Tab`; pause 2.25 seconds; key `q`. The final `q` must end lazygit with status
0 without Enter. Render from `tui-ready` through `before-final-key`, hold the
authentic frame preceding `q`, and keep the MP4 over 13 seconds and source cast
over 16 seconds. The visible TUI must not contain a long-path, repository-path,
or Git-dir error. The full cast/runtime report must prove the real final key,
process exit, and release of every temporary path bridge."""
        + BASE.COMMON_TAIL,
        contract=complex_contract(
            "complex-holdout-lazygit-deep-path-tui",
            "holdout",
            "long-deep-path-panel-navigation-tui",
            "lazygit",
            ["lazygit.exe", "lazygit"],
            "tui",
            1,
            ["lazygit", "src.txt", "todo.md", "release/demo"],
            required_key_sequence=["Down", "Down", "Up", "Tab", "Tab", "q"],
            min_action_count=12,
            min_pause_action_count=6,
            min_planned_pause_seconds=13.5,
            min_source_duration_seconds=16.0,
            required_checks=[
                "single-record-attempt",
                "explicit-tui-actions",
                "action-markers",
                "command-keys",
                "target-exit",
                "target-exit-completion",
                "tui-ready-presentation",
                "before-final-key-marker",
                "before-final-key-presentation",
                "real-time-duration",
                "windows-working-directory-bridge",
                "lazygit-path-clean",
                "lazygit-project-longpaths",
            ],
            require_target_only=True,
            min_duration_seconds=13.0,
        ),
    ),
)


def task_fingerprint(spec: Any) -> str:
    payload = spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_specs() -> dict[str, Any]:
    expected_counts = {"development": 3, "validation": 3, "holdout": 3}
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
        if contract["schemaVersion"] != 2:
            raise ValueError(f"Complex contract must use schema version 2: {spec.task_id}")
        if contract["taskId"] != spec.task_id or contract["split"] != spec.split:
            raise ValueError(f"Contract identity mismatch: {spec.task_id}")
        if contract["minDurationSeconds"] > 10.0:
            if contract["minSourceDurationSeconds"] <= 10.0:
                raise ValueError(
                    f"Long task lacks an authentic source-duration gate: {spec.task_id}"
                )
    return {
        "taskCount": len(TASKS),
        "splitCounts": expected_counts,
        "tuiCount": sum(spec.contract["mode"] == "tui" for spec in TASKS),
        "argvCount": sum(spec.contract["mode"] == "argv" for spec in TASKS),
        "longVideoTaskCount": sum(
            spec.contract["minDurationSeconds"] > 10.0 for spec in TASKS
        ),
        "explicitActionTaskCount": sum(
            spec.contract["minActionCount"] > 0 for spec in TASKS
        ),
        "multiStepTaskCount": sum(spec.contract["promptCount"] > 1 for spec in TASKS),
        "authorizedMutationCount": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--model", default="openai-codex/gpt-5.6-luna")
    parser.add_argument("--pi-version", default="0.84.2")
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
            )
        )
        for split in ("development", "validation", "holdout")
    }
    split_digests = {
        split: BASE.tree_digest(output_root / split)
        for split in ("development", "validation", "holdout")
    }
    manifest = {
        "schemaVersion": 2,
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
            "Run development before validation, freeze the candidate, then release the "
            "untouched holdout once. Preserve every one-attempt result and require "
            "plan/runtime sequence plus source-duration evidence."
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
