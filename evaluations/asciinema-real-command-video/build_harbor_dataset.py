#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build frozen live-CLI Harbor datasets and Pi job configs."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


TASK_TOML = """version = "1.0"

[metadata]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 300.0
"""

TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_task.py"
"""

REQUIRED_FILES = [
    "source/session-plan.json",
    "deliverables/session.cast",
    "deliverables/session.mp4",
    "deliverables/session.manifest.json",
    "deliverables/session.manifest.runtime.json",
    "deliverables/validation.json",
]

COMMON_TAIL = """

Use the installed `$asciinema-real-command-video` skill and the real named
program. Work only in this Harbor task workspace. The evaluated skill is
read-only. Do not inspect ancestor repositories, other skills, prior trials,
credentials, or authentication files. Never print environment variables.

Create `source/session-plan.json`, run plan validation and explicit preflight,
record once to the exact paths below with the pre-provisioned project-local
tools under `.tools/asciinema`, and save the independent validator's unmodified
JSON output to `deliverables/validation.json`:

- `source/session-plan.json`
- `deliverables/session.cast`
- `deliverables/session.mp4`
- `deliverables/session.manifest.json`
- `deliverables/session.manifest.runtime.json`
- `deliverables/validation.json`

The MP4 must be H.264/yuv420p at the requested real speed. The cast must keep
zero Asciinema input events. Do not replace the target with a fake program,
wrapper that prints expected output, browser terminal, animation, or `--help`
unless this task explicitly requests help. If this is a TUI case, the target
must run inside the skill-controlled PTY and all requested keys must be visibly
delivered to that real process. Keep every task input free of secrets.
"""

PUBLIC_CONTRACT_MARKER = "Public acceptance contract (all fields are requirements):"


@dataclass(frozen=True)
class TaskSpec:
    split: str
    task_id: str
    instruction: str
    contract: dict[str, Any]


def contract(
    task_id: str,
    split: str,
    case_type: str,
    target_name: str,
    executable_names: list[str],
    mode: str,
    prompt_count: int,
    required_cast_terms: list[str],
    *,
    any_cast_term_groups: list[list[str]] | None = None,
    required_checks: list[str] | None = None,
    require_target_only: bool = False,
    min_duration_seconds: float = 1.0,
    max_duration_seconds: float = 600.0,
    fps: int = 24,
    authorized_mutation: str = "none",
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "taskId": task_id,
        "split": split,
        "caseType": case_type,
        "targetName": target_name,
        "executableNames": executable_names,
        "mode": mode,
        "promptCount": prompt_count,
        "requiredCastTerms": required_cast_terms,
        "anyCastTermGroups": any_cast_term_groups or [],
        "requiredChecks": required_checks or [],
        "requireTargetOnly": require_target_only,
        "minDurationSeconds": min_duration_seconds,
        "maxDurationSeconds": max_duration_seconds,
        "fps": fps,
        "authorizedMutation": authorized_mutation,
        "requiredFiles": REQUIRED_FILES,
    }


TASKS = (
    TaskSpec(
        split="development",
        task_id="dev-copilot-persistent-tui",
        instruction="""Record one authentic GitHub Copilot CLI TUI session. Launch
`copilot.exe` once with auto-update, remote sessions, mouse input, custom
instructions, and experimental features disabled. Type these exact prompts
character by character, press a real Enter after each, wait for Copilot's real
`Working ... esc interrupt` state to clear, and then type `/exit`:

1. `Reply with exactly: HARBOR COPILOT REAL TUI. Do not use tools.`
2. `Reply with exactly: SECOND PROMPT SAME SESSION. Do not use tools.`

Use the current Copilot ready and busy signals documented by the skill. Keep
one persistent process, preserve real response timing, set the presentation to
`tui-ready`, and require Copilot's own final session summary as the last visible
screen. No file, shell, remote, or repository action is authorized.""" + COMMON_TAIL,
        contract=contract(
            "dev-copilot-persistent-tui",
            "development",
            "conversational-tui",
            "GitHub Copilot CLI",
            ["copilot.exe", "copilot"],
            "tui",
            2,
            [
                "HARBOR COPILOT REAL TUI",
                "SECOND PROMPT SAME SESSION",
                "/exit",
            ],
            required_checks=[
                "timed-keystrokes",
                "enter-submission",
                "tui-ready-marker",
                "tui-ready-presentation",
                "tui-final-hold",
                "tui-exit-presentation",
                "target-exit",
            ],
            require_target_only=True,
            min_duration_seconds=5.0,
            fps=30,
        ),
    ),
    TaskSpec(
        split="development",
        task_id="dev-gh-repo-view-argv",
        instruction="""Record the real GitHub CLI resolving the public `cli/cli`
repository. Use direct-argv mode with target `gh.exe`, one prompt equal to
`cli/cli`, and this exact fixed argument shape:

`repo view {prompt} --json nameWithOwner,url --jq .nameWithOwner + " " + .url`

The prompt must remain one argv item and the real output must include the
repository name and URL. This is a read-only public GitHub request.""" + COMMON_TAIL,
        contract=contract(
            "dev-gh-repo-view-argv",
            "development",
            "network-read-argv",
            "GitHub CLI",
            ["gh.exe", "gh"],
            "argv",
            1,
            ["cli/cli", "https://github.com/cli/cli"],
            required_checks=["target-exit", "real-time-duration"],
            min_duration_seconds=1.0,
        ),
    ),
    TaskSpec(
        split="development",
        task_id="dev-powershell-pipeline-argv",
        instruction="""Record one real PowerShell pipeline without interpolating
the user-controlled label into shell syntax. Target `pwsh.exe` in direct-argv
mode. Use prompt `harbor-pipeline-sentinel`, pass it as the one argument after
`-CommandWithArgs`, and run a fixed command that pipes
`alpha, bravo, beta` through `Where-Object`, `Sort-Object`, and
`ForEach-Object` to print uppercase matches followed by
`LABEL=harbor-pipeline-sentinel`. The visible target output must be `BETA`,
`BRAVO`, and that label, in that order. No filesystem or external side effect
is authorized.""" + COMMON_TAIL,
        contract=contract(
            "dev-powershell-pipeline-argv",
            "development",
            "fixed-pipeline-argv",
            "PowerShell",
            ["pwsh.exe", "pwsh"],
            "argv",
            1,
            ["BETA", "BRAVO", "LABEL=harbor-pipeline-sentinel"],
            required_checks=["target-exit", "real-time-duration"],
            min_duration_seconds=1.0,
        ),
    ),
    TaskSpec(
        split="development",
        task_id="dev-winget-install-winapp",
        instruction="""Record the real Windows Package Manager installing the
official per-user Microsoft Windows App Development CLI. This task explicitly
authorizes exactly this reversible host mutation and no other installation.
Use target `winget.exe`, direct-argv mode, and prompt `Microsoft.WinAppCli` in
this exact command shape:

`install --id {prompt} --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity`

Accept exit status 0 only. A real successful installation or a real
already-installed/no-upgrade result is acceptable; simulated success is not.""" + COMMON_TAIL,
        contract=contract(
            "dev-winget-install-winapp",
            "development",
            "authorized-install-argv",
            "Windows Package Manager",
            ["winget.exe", "winget"],
            "argv",
            1,
            ["Microsoft.WinAppCli"],
            any_cast_term_groups=[
                [
                    "Successfully installed",
                    "already installed",
                    "existing package already installed",
                    "No available upgrade found",
                ]
            ],
            required_checks=["target-exit", "real-time-duration"],
            min_duration_seconds=2.0,
            max_duration_seconds=900.0,
            authorized_mutation="Install Microsoft.WinAppCli 0.6.x per user via winget.",
        ),
    ),
    TaskSpec(
        split="validation",
        task_id="val-television-one-shot-tui",
        instruction="""Create `fixture/tv-items.txt` with exactly `alpha.txt`,
`beta.txt`, and `gamma.txt`, one per line. Record the real Television 0.14.x
picker using `tv.exe` itself as the target. Launch an ad-hoc channel whose
source command reads that file, set source output to `{}`, disable preview,
remote control, and the help panel, and label the input `FILTER> `. Show the
real picker ready, visibly type `beta`, press Enter once to select `beta.txt`,
capture the real selected output and status 0, and stop without a synthetic
shell UI. This is a one-shot TUI: selection ends the target process.""" + COMMON_TAIL,
        contract=contract(
            "val-television-one-shot-tui",
            "validation",
            "one-shot-picker-tui",
            "Television",
            ["tv.exe", "tv"],
            "tui",
            1,
            ["FILTER>", "beta", "beta.txt"],
            required_checks=["timed-keystrokes", "enter-submission", "target-exit"],
            require_target_only=True,
            min_duration_seconds=2.0,
            fps=30,
        ),
    ),
    TaskSpec(
        split="validation",
        task_id="val-fzf-one-shot-tui",
        instruction="""Create `fixture/fzf-items.txt` with exactly `alpha`,
`beta`, and `gamma`, one per line. Record the real `fzf.exe` full-screen picker
as the target, load those choices with a deterministic start/reload binding,
use prompt label `QUERY> `, visibly type `gamma`, press Enter once, and capture
the real `gamma` selection and target status 0. This is a one-shot TUI:
selection ends the target process. Do not substitute a fake input loop.""" + COMMON_TAIL,
        contract=contract(
            "val-fzf-one-shot-tui",
            "validation",
            "one-shot-picker-tui",
            "fzf",
            ["fzf.exe", "fzf"],
            "tui",
            1,
            ["QUERY>", "gamma"],
            required_checks=["timed-keystrokes", "enter-submission", "target-exit"],
            require_target_only=True,
            min_duration_seconds=2.0,
            fps=30,
        ),
    ),
    TaskSpec(
        split="validation",
        task_id="val-lazygit-quit-tui",
        instruction="""Create a small local Git repository under `fixture/repo`
with one committed file and one visibly modified tracked file. Record the real
`lazygit.exe` TUI targeting that repository. The video must show the authentic
Files/branches interface for at least two seconds, visibly deliver lazygit's
normal `q` quit key, exit with status 0, and retain lazygit's final screen.
There is no text prompt and Enter must not be invented. Do not record
`lazygit --help` or replace the TUI with Git output.""" + COMMON_TAIL,
        contract=contract(
            "val-lazygit-quit-tui",
            "validation",
            "command-key-tui",
            "lazygit",
            ["lazygit.exe", "lazygit"],
            "tui",
            1,
            ["lazygit"],
            required_checks=["target-exit"],
            require_target_only=True,
            min_duration_seconds=2.0,
            fps=30,
        ),
    ),
    TaskSpec(
        split="validation",
        task_id="val-winapp-help-argv",
        instruction="""Record the installed real Microsoft Windows App
Development CLI after the development-stage installation. Target `winapp.exe`
in direct-argv mode. Use one prompt equal to `--help` and pass it as the only
command argument. The real help must identify winapp and its Windows app
development commands. No project initialization, package creation, certificate
operation, or additional host mutation is authorized.""" + COMMON_TAIL,
        contract=contract(
            "val-winapp-help-argv",
            "validation",
            "installed-tool-argv",
            "Windows App Development CLI",
            ["winapp.exe", "winapp"],
            "argv",
            1,
            ["winapp", "Windows"],
            required_checks=["target-exit", "real-time-duration"],
            min_duration_seconds=1.0,
        ),
    ),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def validate_specs() -> dict[str, Any]:
    expected_counts = {"development": 4, "validation": 4}
    counts = Counter(spec.split for spec in TASKS)
    if dict(counts) != expected_counts:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    task_ids = [spec.task_id for spec in TASKS]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Task IDs must be unique.")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item) for item in task_ids):
        raise ValueError("Task IDs must be lowercase hyphen-case.")
    fingerprints: list[str] = []
    for spec in TASKS:
        if spec.contract["taskId"] != spec.task_id or spec.contract["split"] != spec.split:
            raise ValueError(f"Contract identity mismatch: {spec.task_id}")
        fingerprints.append(
            sha256_bytes(
                (spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)).encode(
                    "utf-8"
                )
            )
        )
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Task content must be byte-disjoint.")
    case_counts = Counter(spec.contract["caseType"] for spec in TASKS)
    return {
        "taskCount": len(TASKS),
        "splitCounts": expected_counts,
        "caseTypeCounts": dict(sorted(case_counts.items())),
        "tuiCount": sum(spec.contract["mode"] == "tui" for spec in TASKS),
        "argvCount": sum(spec.contract["mode"] == "argv" for spec in TASKS),
        "authorizedMutationCount": sum(
            spec.contract["authorizedMutation"] != "none" for spec in TASKS
        ),
    }


def render_instruction(spec: TaskSpec) -> str:
    return (
        spec.instruction.strip()
        + "\n\n"
        + PUBLIC_CONTRACT_MARKER
        + "\n\n```json\n"
        + json.dumps(spec.contract, indent=2, sort_keys=True)
        + "\n```\n"
    )


def write_task(root: Path, spec: TaskSpec, verifier_source: Path) -> None:
    task_root = root / spec.split / spec.task_id
    (task_root / "environment").mkdir(parents=True)
    (task_root / "tests").mkdir(parents=True)
    (task_root / "instruction.md").write_text(
        render_instruction(spec), encoding="utf-8", newline="\n"
    )
    (task_root / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task_root / "environment" / ".gitkeep").write_text("", encoding="utf-8")
    (task_root / "tests" / "contract.json").write_text(
        json.dumps(spec.contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (task_root / "tests" / "test.sh").write_text(
        TEST_SH, encoding="utf-8", newline="\n"
    )
    shutil.copy2(verifier_source, task_root / "tests" / "verify_task.py")


def quoted(value: str | Path) -> str:
    return json.dumps(str(value).replace("\\", "/"))


def write_job_config(
    output_root: Path,
    repo_root: Path,
    split: str,
    run_id: str,
    attempts: int,
    model: str,
    pi_version: str,
) -> Path:
    skill_source = (repo_root / "skills" / "asciinema-real-command-video").resolve()
    pi_wrapper = (
        repo_root
        / "evaluations"
        / "asciinema-real-command-video"
        / "harbor_pi_wrapper.py"
    ).resolve()
    config_path = output_root / f"{split}-job.yaml"
    config = f"""job_name: {quoted(f'{run_id}-{split}-pi')}
jobs_dir: {quoted(output_root / 'jobs')}
n_attempts: {attempts}
n_concurrent_trials: 1
quiet: true
retry:
  max_retries: 0
environment:
  import_path: "evaluations.asciinema-real-command-video.harbor_wsl_environment:RecordingWorkspaceWSLEnvironment"
  delete: false
  cpu_enforcement_policy: ignore
  memory_enforcement_policy: ignore
  kwargs:
    shared_cache_dir: {quoted(repo_root / 'evaluations' / 'runs' / 'harbor-shared-cache')}
    skill_source_dir: {quoted(skill_source)}
    recording_tools_dir: {quoted(repo_root / 'projects' / 'asciinema-real-command-video' / 'artifacts' / 'tools')}
agents:
  - import_path: "evaluations.asciinema-real-command-video.harbor_pi_agent:WorkspaceWindowsPi"
    model_name: {quoted(model)}
    skills:
      - {quoted(skill_source)}
    kwargs:
      version: {quoted(pi_version)}
      expected_version: {quoted(pi_version)}
      wrapper_path: {quoted(pi_wrapper)}
      thinking: high
datasets:
  - path: {quoted(output_root / split)}
artifacts:
  - source: "/app/source"
    destination: "source"
  - source: "/app/deliverables"
    destination: "deliverables"
"""
    config_path.write_text(config, encoding="utf-8", newline="\n")
    return config_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--model", default="openai-codex/gpt-5.3-codex-spark")
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
    helper_root = Path(__file__).resolve().parent
    repo_root = helper_root.parents[1]
    verifier_source = helper_root / "verify_task.py"
    if not verifier_source.is_file():
        raise SystemExit(f"Verifier source is missing: {verifier_source}")

    stats = validate_specs()
    for spec in TASKS:
        write_task(output_root, spec, verifier_source)
    configs = {
        split: str(
            write_job_config(
                output_root,
                repo_root,
                split,
                args.run_id,
                args.attempts,
                args.model,
                args.pi_version,
            )
        )
        for split in ("development", "validation")
    }
    split_digests = {
        split: tree_digest(output_root / split) for split in ("development", "validation")
    }
    manifest = {
        "schemaVersion": 1,
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
            "Initial live diagnostic: run development before validation; preserve every "
            "failure; do not interpret a one-attempt result as a release threshold."
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
