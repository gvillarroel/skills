# Live terminal-video Harbor protocol

## Objective

Evaluate whether an isolated Pi agent can use only the runtime payload of
`asciinema-real-command-video` to create authentic Asciinema casts and H.264
MP4 derivatives of real installed terminal programs. The evaluator checks
target identity, process status, visible output, prompt/action ordering,
zero Asciinema input events, artifact hashes, media properties, and nonblank
opening and final frames.

This is an initial one-attempt diagnostic, not a release threshold. Preserve
all failures. Do not retry a failed trial into a pass or change a frozen split
after its first live run.

## Runtime profiles

- Harbor: `0.18.0`
- Agent: evaluator-owned Harbor adapter for the installed Windows Pi CLI;
  invoke the JavaScript entry point with `node.exe`, never the multiline-unsafe
  `pi.cmd` shim
- Pi: `0.84.2`
- Default release model: `openai-codex/gpt-5.3-codex-spark`
- Documented coverage fallback: `openai-codex/gpt-5.6-luna`, reported as a
  separate comparison profile and never merged with Spark
- Thinking level: `high`
- Attempts: one per task
- Concurrency: one trial
- Evaluated payload: only `skills/asciinema-real-command-video/`
- Execution boundary: a workspace-scoped WSL root with Windows CLI
  interoperability
- Private authentication: consumed by the installed Pi process without being
  copied into trial roots; excluded from datasets, artifacts, reports, and
  publication
- Pi isolation: disable ambient context, extensions, skill discovery, prompt
  templates, and themes; load only the copied evaluated skill explicitly
- Prompt transport: record bytes and SHA-256 before Pi starts, then compare the
  marker with Pi's complete user message

## Frozen datasets

Development contains four tasks:

1. One persistent GitHub Copilot CLI TUI process with two exact prompts,
   timed typing, Enter submission, completion gating, `/exit`, and target-only
   presentation.
2. A read-only GitHub CLI `repo view` direct-argv recording.
3. A fixed PowerShell pipeline that keeps the supplied label as inert argv
   data rather than shell syntax.
4. One explicitly authorized per-user `winget` installation of
   `Microsoft.WinAppCli`.

Validation contains four disjoint tasks:

1. A one-shot Television picker that exits after a real selection.
2. A one-shot fzf picker that exits after a real selection.
3. A lazygit command-key TUI that exits on `q` without an invented Enter.
4. A direct-argv recording of the installed `winapp --help` command.

Development and validation are optimizer-visible. There is no holdout in this
study because no independent holdout author supplied sealed tasks. Do not call
validation a holdout.

## Side-effect boundary

Every task is read-only except the development WinApp task. That task alone
authorizes this exact host mutation:

```text
winget install --id Microsoft.WinAppCli --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
```

No other installation, upgrade, repository publication, remote write, or
credential interaction is authorized. An already-installed result is valid
when the real command exits successfully and reports that state.

## Required artifacts

Each task must create these exact files:

- `source/session-plan.json`
- `deliverables/session.cast`
- `deliverables/session.mp4`
- `deliverables/session.manifest.json`
- `deliverables/session.manifest.runtime.json`
- `deliverables/validation.json`

The Harbor verifier writes evaluator-owned `verification.json` and
`reward.json`. The scalar reward is `1` only when every disclosed component
passes. Component rewards remain available to diagnose missing artifacts,
plan mismatch, target provenance, bundled validation, hashes, media encoding,
visual frames, TUI presentation, interaction lifecycle, and expected output.

After Harbor finishes collecting artifacts, rerun the same verifier against
the stable copies and audit `agent/pi.txt`. The trace audit requires one and
only one skill recorder call, explicit plan validation, preflight, independent
validation, complete prompt transport, no custom source controller, no direct
recorder bypass, and no moved or removed prior session artifacts. A valid MP4
does not override a failed trace audit.

## Failure classification

- `infrastructure`: Harbor, Pi setup/authentication, WSL adapter, or verifier
  could not execute independently of the evaluated behavior.
- `agent execution`: Pi did not create the required files or violated the
  public task contract.
- `skill capability`: the runtime payload lacks a workflow required by a
  correctly attempted task, such as one-shot process completion or raw
  command-key input.
- `target/environment`: the named real program, network, authentication, or
  authorized package operation failed after the harness started correctly.
- `verifier defect`: evaluator code rejected valid evidence or could not read
  its own disclosed format.

Do not relabel a verifier failure as an infrastructure failure merely because
the trial score is zero. Inspect the agent exception, verifier logs, artifacts,
and process evidence before assigning a class.

## Reproduction

Build a fresh ignored run directory, validate the generated dataset, print
both resolved Harbor configs, then run development before validation. The
example uses Luna only as a separately labeled coverage profile:

```powershell
uv run --script evaluations/asciinema-real-command-video/build_harbor_dataset.py --output-root evaluations/runs/asciinema-real-command-video-harbor-pi-coverage --run-id asciinema-real-command-video-harbor-pi-coverage --model openai-codex/gpt-5.6-luna
$env:ASCIINEMA_VIDEO_HARBOR_DATASET_ROOT = (Resolve-Path evaluations/runs/asciinema-real-command-video-harbor-pi-coverage).Path
$env:ASCIINEMA_VIDEO_HARBOR_MODEL = 'openai-codex/gpt-5.6-luna'
uv run --script evaluations/asciinema-real-command-video/test_harbor_dataset.py
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = (Get-Location).Path
harbor run --config evaluations/runs/asciinema-real-command-video-harbor-pi-coverage/development-job.yaml --print-config
harbor run --config evaluations/runs/asciinema-real-command-video-harbor-pi-coverage/development-job.yaml
harbor run --config evaluations/runs/asciinema-real-command-video-harbor-pi-coverage/validation-job.yaml --print-config
harbor run --config evaluations/runs/asciinema-real-command-video-harbor-pi-coverage/validation-job.yaml
```

Run `reverify_collected_job.py` and `audit_pi_job.py` on each completed job
before interpreting results. Keep `delete: false` until verification finishes,
then use `cleanup_failed_trial_roots.py` first in dry-run mode and again with
`--execute` to remove only the completed trials' disposable `_wsl-root` trees.

Retain bulky raw jobs only under `evaluations/runs/`. Publish only redacted,
aggregate summaries with checksums and pointers to the private evidence.

The 2026-08-20 live outcome and failure classifications are recorded in
[`harbor-pi-live-cli-20260820.md`](harbor-pi-live-cli-20260820.md).

## Sequential multi-TUI extension

Use `build_multi_tui_harbor_dataset.py` when one recording must prove ordered
interaction with multiple distinct TUI executables. Its three frozen splits
exercise fzf → Television, Television → fzf → lazygit, and a final-only
Copilot → Television holdout. Every task requires a source cast and MP4 longer
than ten seconds, one recording attempt, ordered per-session boundaries,
distinct executable provenance, real-time interaction, and stable collected
artifact reverification.

Run development and validation first. Freeze and independently recompute the
candidate tree digest before releasing holdout exactly once; do not change the
skill payload after that release. The builder accepts `--runtime-resource-root`
when immutable skill sources live in a clean worktree but large cached binaries
and installed recording tools must remain in the primary ignored evaluation
root. Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` before Harbor launches Pi
so Unicode skill references cross the Windows wrapper without locale-dependent
decoding.

The 2026-08-21 three-case result, digests, video hashes, frame review, and
failure-preservation record are in
[`multi-tui-harbor-20260821.md`](multi-tui-harbor-20260821.md).
