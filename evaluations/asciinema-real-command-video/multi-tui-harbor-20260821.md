# Sequential multi-TUI Harbor validation — 2026-08-21

## Outcome

The evolved `asciinema-real-command-video` bundle passed all three native
Harbor 0.18.0 cases with scalar reward `1.0`, every component reward at `1.0`,
and zero execution errors or retries. Each case used installed Pi 0.84.2 with
`openai-codex/gpt-5.6-luna`, only the evaluated skill payload, one outer
Asciinema recording, one attached tmux PTY, and two or three distinct real TUI
executables launched sequentially.

The frozen candidate contains 13 files / 324,267 bytes and has canonical tree
SHA-256
`04482703de8df8872a3b8e2679832249f0a26b0f09802409ef0940a87c9e96e1`.
The digest was recorded after development and validation, checked immediately
before holdout release, and was not changed during or after holdout execution.

## Capability added

- A `tui_sessions` plan can declare two to eight real TUI processes in one
  ordered recording.
- Every session has its own target, readiness contract, actions, completion,
  executable version and SHA-256, process status, and optional Windows working
  directory bridge.
- The supervisor opens one start gate at a time, requires the current target to
  complete successfully before handoff, and applies the final hold only to the
  last session.
- Runtime and cast verification require ordered begin, ready, exit, and
  handoff markers, globally unique step IDs, distinct executable identities,
  zero Asciinema input events, one immutable attempt ledger, and one MP4.
- Target-only rendering trims at the final TUI exit rather than the first
  alternate-screen restore.

## Frozen dataset

The dataset was generated under ignored local evidence root
`evaluations/runs/asciinema-multi-tui-harbor-20260821-v3` with one attempt per
task and concurrency one.

| Split | Ordered real targets | Source cast | MP4 | Reward |
| --- | --- | ---: | ---: | ---: |
| Development | fzf 0.70.0 → Television 0.14.5 | 18.071 s | 16.333 s | 1.0 |
| Validation | Television 0.14.5 → fzf 0.70.0 → lazygit 0.60.0 | 21.952 s | 19.733 s | 1.0 |
| Holdout | GitHub Copilot CLI 1.0.73 → Television 0.14.5 | 29.894 s | 24.267 s | 1.0 |

Frozen split tree digests:

- Development:
  `fc69c7410e3aaf1ac1f193f8eea73c7274fa3c3c809d2bca5d878421295bf846`
- Validation:
  `493778e4662a3eace371116337537313c38a590cdf1ce9b5008946910d880d90`
- Holdout:
  `8d04a4c4b37ad0aa552c5c9592b015932f0deff5da2f1f64f65b397f6c006394`

The holdout was released exactly once after the candidate digest was frozen.
Its Copilot process visibly received the exact prompt `Reply with exactly:
MULTI TUI COPILOT COMPLETE. Do not use tools.`, returned the required text,
exited through the real TUI, and handed the same recording to Television.

## Independent evidence checks

The evaluator-owned verifier passed all twelve reward dimensions for every
case: artifacts, complexity, interaction, media, output, plan, presentation,
provenance, scalar reward, target, validation, and visual. Reverification of
the stable collected copies passed 3/3. Independent Pi trace audits passed 3/3
and confirmed complete prompt transport, exactly one skill `record` call per
trial, explicit plan validation and preflight, independent post-validation,
no direct recorder bypass, no custom controller, no artifact-renaming retry,
and completed agent traces.

Full-resolution frame review confirmed both tools in the development video,
all three tools in the validation video, and Copilot typing, Copilot's real
response, Television typing, and the final selection in the holdout video.
The retained user-facing local copies are:

- `projects/asciinema-real-command-video/artifacts/videos/multi-tui-harbor-v3-20260821/01-fzf-television.mp4`
  — SHA-256 `b930fcd61026cd3e9bf70206e43fc003cf01771a172d8e058166655bc96b1b9e`
- `projects/asciinema-real-command-video/artifacts/videos/multi-tui-harbor-v3-20260821/02-television-fzf-lazygit.mp4`
  — SHA-256 `9ad5c60766bb3974090860ba441dea0121338f655da3fb1a44ef5b743c178c74`
- `projects/asciinema-real-command-video/artifacts/videos/multi-tui-harbor-v3-20260821/03-copilot-television.mp4`
  — SHA-256 `a34aa50a15a9b54bd25d695b3ba32d0a153baa50d76c967e11ad6672b1556b10`

All three MP4s are H.264, yuv420p, 30 fps, even-dimensioned, nonblank at both
ends, and longer than ten seconds.

## Failure preservation

An earlier v2 orchestration attempt failed before the agent created a plan or
started a recording because the Windows wrapper decoded a Unicode skill
reference with CP1252. It is classified as external infrastructure evidence,
not a skill result. The wrapper now fixes stdin/stdout/stderr to UTF-8. The
`harbor-resume-external-failures` doctor correctly refused to resume the
incomplete Harbor root because it lacked a trustworthy `finished_at` state, so
the evidence was preserved and a fresh v3 dataset was created. No claimed
recording was retried.

## Regression results

- Controller: 46/46
- Evaluator verifier: 14/14
- Sequential multi-TUI dataset: 5/5
- Complex dataset: 7/7
- Base dataset: 7/7
- Pi trace auditor: 4/4
- Pi wrapper: 2/2
- Stable-artifact reverification: 3/3
- Live Pi trace audit: 3/3

Repository-wide pattern-ID, skill, independence, payload, and diff checks all
passed. The synchronized local installation is checked again after publication.
