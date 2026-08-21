# Per-video bundle isolation validation — 2026-08-21

## Goal

Prevent artifact mixing when one request produces several terminal videos.
Every video must own one fresh directory containing its complete recording and
validation evidence, while retaining the existing single-attempt and authentic
process contracts.

## Evolved behavior

- `init-video <directory> --template <name>` creates a new lowercase-hyphen-
  case directory and its `session-plan.json`; it refuses an existing path.
- `preflight-video <directory>` writes the plan-bound `preflight.json` only
  before recording evidence exists.
- `record-video <directory>` derives every reserved artifact path, requires a
  matching plan digest from preflight, and permits one claimed transaction.
- `validate-video <directory>` independently validates the cast, runtime,
  manifest, and MP4, then writes `validation.json` and a SHA-256/size-sealed
  `bundle.json`.
- `audit-video-bundles <directory>...` read-only audits two or more completed
  directories for distinct ownership, canonical entry sets, sibling paths,
  and unchanged hashes and sizes.
- The fixed non-GIF directory contains ten entries. `bundle.json` indexes the
  other nine; retained `session.gif` is an optional eleventh entry and tenth
  indexed artifact.
- A dedicated `direct-argv` template removes the need to convert the TUI
  template manually. Direct-argv plans omit the entire `interaction` key.

## Manual two-video real-process smoke

The evolved Windows entrypoint initialized, preflighted through WSL2,
recorded, validated, and batch-audited two real `python3` direct-argv videos at:

`projects/asciinema-real-command-video/artifacts/videos/bundle-isolation-smoke-20260821/`

| Video ID | Entries | Indexed artifacts | MP4 | Duration | MP4 SHA-256 |
| --- | ---: | ---: | --- | ---: | --- |
| `first-real-command` | 10 | 9 | H.264/yuv420p, 24 fps | 3.041667 s | `a11ee31bdc799f275d1bc6343dab344c64965feb1f36235a991ae5cb6cccd19a` |
| `second-real-command` | 10 | 9 | H.264/yuv420p, 24 fps | 3.250000 s | `a4f94b561cac65461699b677490d140282300fb31f1d06c239547eceb3bc9aba` |

Both real targets exited zero. The batch audit passed nine isolation checks and
confirmed distinct directories, video IDs, run IDs, casts, MP4 hashes, and
sibling-only evidence. A separate JSON scan found no cross-video ID reference.

## Isolated Pi progression

The immutable prompt is
`evaluations/pi-prompts/asciinema-real-command-video-bundle-isolation.md`.

- Spark run `asciinema-real-command-video-bundle-isolation-20260821-spark-1`
  was externally blocked before the first tool call with `The usage limit has
  been reached`, zero tokens, and no task artifacts. This is retained as an
  infrastructure failure, not a skill result.
- Luna development run `...-luna-1` produced and passed both artifact sets,
  all six JSON assertions, and skill integrity, but failed strict events after
  four recovered tool errors. The trace exposed ambiguous direct-argv template
  conversion and native-Windows handling of WSL absolute paths. Those findings
  produced the dedicated template and portable `relative_path` guidance.
- Luna development run `...-luna-2` again passed artifacts, JSON assertions,
  and integrity, but failed strict events after three recovered manual JSON and
  ad hoc audit errors. That finding produced the deterministic batch auditor
  and narrowed the holdout to bundle isolation.
- Final strict run
  `asciinema-real-command-video-bundle-isolation-20260821-luna-3` passed in
  136.145 seconds with `openai-codex/gpt-5.6-luna`: four exact outputs, six JSON
  field assertions, valid JSON events, the required observed model, prompt read
  first, zero tool errors, and unchanged runtime payload SHA-256
  `aee5aaeda97cb2a87816e29da3bac63843011b67f82a07fc0f74f02da2ed9971`.
  The trace made 15 tool calls, ran exactly one `record-video` per directory,
  and read only the prompt, `SKILL.md`, and three directly required references.
  Both output directories had ten entries and nine indexed artifacts; their
  H.264/yuv420p/30 fps MP4s were 1.700 seconds with different SHA-256 values.

## Regression gates

- Controller: 55/55 passed.
- Independent verifier: 14/14 passed.
- Complex Harbor dataset: 7/7 passed.
- Multi-TUI Harbor dataset: 5/5 passed.
- Pi trace auditor: 4/4 passed.
- Harbor Pi wrapper: 2/2 passed.
- Pattern ID, skill structure, skill independence, repository payload, and
  `git diff --check` gates passed.

The source skill contains 15 files / 363,838 bytes. Generated recordings and
bulky Pi run directories remain ignored local evidence.
