# Per-video artifact bundles

Use one fresh directory for every requested video. The directory leaf is the
stable video ID and must use lowercase hyphen-case. A batch of three videos
therefore has three sibling directories, not three casts and MP4s in shared
format-specific folders.

## Fixed layout

The bundle commands reserve this layout:

```text
<video-id>/
├── session-plan.json
├── preflight.json
├── .session-plan.recording-attempt.json
├── session.cast
├── session.runtime.json
├── session.mp4
├── session.manifest.json
├── record-result.json
├── validation.json
├── bundle.json
└── session.gif                 # only with --retain-gif
```

The project-local recorder toolchain may be shared between videos because it
is a dependency, not recording evidence. Keep every plan and generated
recording artifact in the owning video directory.

## Batch workflow

Initialize every directory before editing its plan:

```bash
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" init-video projects/demo/artifacts/terminal-videos/copilot-basics --template single-tui --json
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" init-video projects/demo/artifacts/terminal-videos/fzf-to-tv --template multi-tui --json
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" init-video projects/demo/artifacts/terminal-videos/lazygit-status --template lazygit --json
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" init-video projects/demo/artifacts/terminal-videos/python-command --template direct-argv --json
```

Edit each `session-plan.json`, then run the rest of the lifecycle against the
directory rather than supplying independent output paths:

```bash
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" preflight-video projects/demo/artifacts/terminal-videos/copilot-basics --tools-dir .tools/asciinema --json
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" record-video projects/demo/artifacts/terminal-videos/copilot-basics --tools-dir .tools/asciinema --json
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" validate-video projects/demo/artifacts/terminal-videos/copilot-basics --tools-dir .tools/asciinema --json
```

Repeat those three commands for the other initialized directories. Do not run
several recording processes concurrently: target configuration, credentials,
terminal focus, and shared working files may still conflict even though the
artifact destinations are isolated.

After every directory passes `validate-video`, audit the batch together:

```bash
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" audit-video-bundles projects/demo/artifacts/terminal-videos/copilot-basics projects/demo/artifacts/terminal-videos/fzf-to-tv projects/demo/artifacts/terminal-videos/lazygit-status --json
```

This command is read-only and runs natively on Windows. It rejects duplicate
directories or IDs, missing or extra entries, foreign absolute-path suffixes,
non-sibling relative paths, and changed artifact hashes or sizes.

## Isolation rules

- Treat the video directory as the unit of ownership, review, delivery, and
  retention.
- Never reuse an existing directory, including after a failed recording.
- Never move another video's cast, MP4, manifest, or ledger into the directory.
- Do not override fixed filenames. `record-video` derives them and rejects any
  pre-existing reserved output before starting Asciinema.
- `preflight-video` may refresh `preflight.json` while the plan is still being
  prepared. Once any recording evidence exists, it refuses to change the
  report.
- `record-video` requires the plan path and SHA-256 recorded by the matching
  preflight. If the plan changes, preflight it again before the first attempt.
- `validate-video` is independent and single-write. It refuses existing
  `validation.json` or `bundle.json`, then records every artifact's sibling
  filename, SHA-256, and byte size in the sealed bundle index.
- Use each index entry's `relative_path` as the portable ownership field. On
  Windows, capture commands run inside WSL, so absolute `path` values use WSL
  syntax even when a native Windows process later reads the index. Verify that
  the normalized absolute path ends in `/<video-id>/<relative_path>`; do not
  pass a WSL absolute path to native `Path.resolve()`.

The legacy `preflight`, `record`, and `validate` commands remain available for
diagnosing an existing explicit-path artifact set. Use the bundle commands for
all new video work, especially batches.
