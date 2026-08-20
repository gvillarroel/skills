# Asciinema Real Command Video Evolution — 2026-08-20

## Outcome

Promote `asciinema-real-command-video` from `validating` to `done`.

The evolved bundle fixes the three failure modes exposed by the first frozen
Harbor/Pi matrix: repeated recording attempts, ad hoc recording bypasses for
one-shot pickers, and the inability to express a raw TUI command key such as
`q` without inventing Enter. The final bundle has 9 files, 233,974 bytes, and a
91-line `SKILL.md`.

## Evidence boundary

The original benchmark remains preserved at
`evaluations/runs/asciinema-real-command-video-evolution-frozen-20260820/`.
Its development and validation tree digests are respectively
`8509bc698e9d5605a19286b9c4b1d69a4d18a5fb212223cc37ac0c253b038377`
and `d6d1ed2c3fa09fd5fd4f62c59fbee0aec5ddeabe3f55752e784f80e527878569`.
It supplied development evidence only after
three trace failures were observed: the PowerShell pipeline was recorded
twice, lazygit required six recording calls, and Television bypassed the skill
recorder.

The corrected verifier benchmark is a separate immutable dataset at
`evaluations/runs/asciinema-real-command-video-evolution-corrected-20260820/`.
Its full split digests are:

- development: `2c88a7a1f60e78626851feb49c0e51573301ae962897f78b0aec89202b49708a`
- validation: `e31d83f9781bfc31ac76b25df0e0b96574e55f2d593cd247b5d97980e01971b1`

The correction changes only evaluator-owned media path handling: when Harbor
runs in WSL but resolves Windows `ffprobe.exe` or `ffmpeg.exe`, `/mnt/c/...`
inputs are translated back to `C:\...`. It also recognizes the evolved
`before-final-key` presentation contract while retaining support for the
legacy `tui-exit` contract. Task instructions and public acceptance contracts
remain unchanged.

## Evolved behavior

- TUI plans can use explicit `text`, `key`, and `pause` actions. Supported key
  actions include Enter, `q`, arrows, escape, tab, backspace, and control keys.
- One-shot TUIs can declare `target-exit`; the real process terminates the
  session after its final action instead of requiring synthetic shutdown text.
- A plan-scoped immutable recording-attempt ledger is created after preflight
  and before Asciinema starts. A second recording invocation is refused even
  when different output paths are supplied.
- `render.end_at: before-final-key` keeps the full cast and runtime proof of the
  final quit key and exit status, while the MP4 ends on and briefly freezes the
  preceding authentic TUI frame.
- Manifests and independent validation now prove action hashes, key delivery,
  target completion, the final-key marker, frozen-frame duration, and the
  single-record ledger.
- Runtime guidance now contains focused recipes for lazygit, fzf, Television,
  PowerShell pipelines, and persistent conversational TUIs.

## Forward validation

Strict isolated Pi run
`evaluations/runs/asciinema-real-command-video-evolved-one-shot-20260820-spark-3/`
passed with `gpt-5.3-codex-spark`: 10 exact outputs, 8 JSON assertions, valid
event JSON, zero tool errors, focused reads of `SKILL.md` and three references,
and unchanged runtime payload SHA-256
`b8aea4b1dd8ff5972728fb0b2fe0826d0707dc200a07f34e3161c657ae625162`.
The real fzf 0.70.0 target exited 0 and produced H.264/yuv420p at 30 fps.

Native Harbor 0.18.0 with installed Pi 0.84.2 and
`openai-codex/gpt-5.6-luna` produced these post-evolution results:

| Gate | Task | Reward | Trace audit | MP4 SHA-256 |
| --- | --- | ---: | --- | --- |
| validation | `val-lazygit-quit-tui` | 1.0 | pass, one record | `e37c290453b9ef6d428dbaf2c7a56585680a7eed41f1ac49ba167796cd4f99be` |
| validation | `val-television-one-shot-tui` | 1.0 | pass, one record | `58f1929dbdf55c167b2607b2620a45e0000751c2ab685fe21b0ec5a8f117f2b4` |
| sealed holdout | `val-fzf-one-shot-tui` | 1.0 | pass, one record | `b1d2dc27dc58d0f8c9c10cbad12f74382609d8aed5acf24a53273703100a98ec` |
| sealed holdout | `val-winapp-help-argv` | 1.0 | pass, one record | `3550c660bdf3743b9de88ca5805fcfcd7e99959f2ba514f91f2e8908b3125670` |

Every task passed all 11 native reward dimensions with zero execution errors
and zero retries. The trace audits found no direct recorder calls, custom
source paths, retry mutations, incomplete prompts, invalid JSON, or wrapper
marker mismatches. Reports are under
`evaluations/runs/asciinema-real-command-video-evolution-20260820-v1/reports/`
and audits are under the sibling `audits/` directory.

All nine canonical files in the promoted source are byte-identical to the
corresponding files loaded by each of the four Harbor trials. Generated Python
`__pycache__` directories created by local tests were excluded from the
canonical bundle after this comparison; no instruction, script, reference,
template, or agent metadata changed after holdout release.

Manual full-resolution frame review confirmed authentic target surfaces:
lazygit's Files/branches/diff view persists through the final MP4 frame;
Television shows `FILTER> beta` and its selected `beta.txt`; fzf shows the
progressive `gamma` query and selected output; and WinApp CLI shows its real
help surface and exit code 0. Review frames are under
`projects/asciinema-real-command-video-evolution/artifacts/screenshots/harbor-gate/`.

The deterministic pipeline re-verification also passes 1/1 at
`evaluations/runs/asciinema-real-command-video-evolution-20260820-v1/reverification/train-pipeline/aggregate.json`.

## Automated gates

- Controller unit tests: 32/32 pass.
- Verifier unit tests: 8/8 pass.
- Frozen Harbor dataset tests: 7/7 pass.
- Pi trace-auditor tests: 2/2 pass.
- Pi wrapper tests: 2/2 pass.

## GEPA status

`evolution-config-20260820.yaml` passes the Harbor/GEPA dry run with four
development tasks, two validation tasks, and two disjoint holdout tasks. The
automatic reflective search did not start because `doctor` correctly reports
the required `OPENAI_API_KEY` as missing. No metric-call budget or candidate
proposal was consumed. The promoted implementation is therefore the
evidence-guided human/Pi/Harbor candidate, not a claimed GEPA winner.
