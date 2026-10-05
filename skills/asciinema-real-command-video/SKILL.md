---
name: asciinema-real-command-video
description: "Records authentic persistent, one-shot, command-key, or sequential multi-tool TUI executions and direct-argv runs of installed terminal programs as isolated per-video Asciinema artifact bundles with H.264 MP4 derivatives and executable, action, process, single-attempt, and media provenance. Use when one or several demos must visibly interact with real CLIs, including GitHub Copilot, pickers, or several TUIs in one continuous video, instead of showing a simulated terminal."
---

# Asciinema Real Command Video

Use `render.theme: colorset1` by default, or `colorset2` for extended terminal roles. The renderer resolves a bundled ANSI theme and maps indexed/truecolor SGR paint in a separate presentation cast to exact [colorset tokens](assets/palettes/colorsets.json). Preserve the original recording bytes, text, commands, timestamps and evidence. Authored presentation and template themes must fit a colorset; do not select unrelated built-in agg themes. Imported terminal image protocols, emoji glyph artwork, antialiasing and lossy MP4 pixels are source/rendering effects, not a claim of exact pixel membership.

Treat the asciicast as the source of truth and the MP4 as its rendered derivative. Run the named product with the requested prompts in the requested project. Never substitute prerecorded text, a browser terminal, generated output, or a look-alike command.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. For colorset1, follow the bundled `solidSequence`: primary red `#9e1b32`, then interleaved black/grays (darkest, middle, next darkest, next middle), white, and the remaining colors. Apply this order to categorical identities; keep quantitative and ordered grayscale ramps monotonic. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Choose the execution mode

Use interactive TUI mode when the user wants the product UI, visible typing, live work, selections, command keys, conversational continuity, or multiple terminal applications in one video. Persistent prompts type text, send real Enter, and wait for ready-without-busy. One-shot pickers and command-key TUIs use explicit text/key/pause actions and target-exit gating. Direct-argv mode is for explicitly non-interactive recordings; pass each prompt as one direct argument and omit the entire `interaction` key, including `null` or `{}`.

Read only the applicable guidance:

| Task | Reference |
| --- | --- |
| Author or validate any session plan | [session-plan.md](references/session-plan.md) |
| Plan a live UI, persistent prompts, or explicit actions | [tui-plan.md](references/tui-plan.md) |
| Record/review a TUI or diagnose a preserved attempt | [recording-lifecycle.md](references/recording-lifecycle.md) |
| Produce several video bundles or inspect ownership | [video-bundles.md](references/video-bundles.md) |
| Show several TUIs in one uninterrupted cast | [multi-tui-sequences.md](references/multi-tui-sequences.md) |
| Record GitHub Copilot CLI | [github-copilot-cli.md](references/github-copilot-cli.md) |
| Use pickers, command keys, native Windows lazygit, or a fixed PowerShell pipeline | [interaction-recipes.md](references/interaction-recipes.md) |
| Bootstrap tools or resolve platform/WSL paths | [platform-and-tooling.md](references/platform-and-tooling.md) |

For plan-only work, stop after the requested plan validation; recording, installation, and launching the target require the task to call for them. Keep generated files outside the skill bundle. During normal use, execute the documented helper without reading its monolithic source or acceptance examples.

For an offline presentation-color task, use `uv run --script scripts/terminal_colorsets.py <source.cast> <presentation.cast> --colorset colorset1 --report <theme.json>` with paths relative to this bundle for the script and the current workspace for artifacts; no recording lifecycle is needed. Honor each requested output path exactly. The helper preserves source SHA-256, non-theme header fields and event timing/type, and deliberately replaces the presentation header's `theme` with the asciicast object `{bg, fg, palette}`. The colorset name is in the report's `colorset` field, not the cast header. Compare parsed events for text semantics; do not assert that the entire presentation header equals the original. The report includes `colorset`, `aggTheme`, source hash and preservation checks.

## Preserve authenticity and ownership

- Freeze exact prompts/actions, order, executable, working directory, completion signals, shutdown mode, and allowed side effects in the plan. Authenticate and resolve first-run trust outside the recording. Never record credentials or broaden target permissions to make unattended execution succeed.
- Resolve/version the real executable before capture. A single TUI launches once; multi-TUI plans launch two to eight ordered sessions with at least two distinct resolved executables, each once. Finish one target before starting the next in the same recorded PTY. Direct-argv steps invoke actual processes and use an explicit session ID when context is needed.
- Attach the recorder's outer PTY before launching a target. Require session ID, PTY, step/action markers, input hashes, and observed exit codes. Keep Asciinema input capture disabled: TUI keys go only to the isolated inner PTY and appear as visible output.
- Give every requested video one fresh lowercase-hyphen-case directory. Keep its plan, preflight, immutable attempt ledger, cast, runtime, MP4, manifest, record result, validation, and sealed bundle index together. Never share evidence paths between videos.
- Allow one `record-video` transaction per requested deliverable. After it begins, a renamed plan, alternate directory, or adjusted launch does not authorize a retry. Preserve failed artifacts and diagnose them. A later recording needs a new user request or explicit authorization.
- Preserve real TUI timing: render speed `1.0`, no idle-time cap. Start a user-facing TUI MP4 at `tui-ready`; for a final key that clears the screen, use `before-final-key`. Keep the complete cast and disclose trims. Never trim requested target work or responses.
- Verify all target exits and recording closure, then validate cast/runtime evidence before conversion. A rendered MP4 alone does not prove successful behavior. Never upload recordings unless requested.

## Run the bundle workflow

The helper captures natively on Linux/macOS and forwards Unix-only operations from Windows into default WSL2 with path translation. Use its literal bundle path; the skill name is not an executable. The commands below use `skills/asciinema-real-command-video` as an example bundle root—replace it with the actual path when installed elsewhere. In Git Bash on Windows, prefix with `MSYS_NO_PATHCONV=1` to preserve Unix target arguments. If using `ASCIINEMA_VIDEO_SKILL` in reference examples, assign/export it in a separate statement before expansion; an inline assignment expands the old value.

1. Initialize the exact new video directory once, selecting `single-tui`, `direct-argv`, `multi-tui`, or `lazygit`:

   ```text
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py init-video <video-directory> --template <template> --json
   ```

   `init-video` refuses an existing directory and creates only `session-plan.json`. Adapt that plan using the applicable schema and recipes. For native Windows lazygit, follow the recipe's project-local `core.longpaths` setting, config template, and `{windows_working_directory}` bridge.

2. Validate the plan before executing it:

   ```text
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-plan <video-directory>/session-plan.json --json
   ```

3. Ensure `asciinema`, `agg`, `ffmpeg`, and `ffprobe` are available in the recording environment; TUI mode also needs `tmux`. When recorder/renderer binaries are missing, follow the platform reference's pinned project-local bootstrap. Run preflight and inspect it before recording:

   ```text
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py preflight-video <video-directory> --tools-dir .tools/asciinema --json
   ```

   Preflight binds the plan hash and checks tools, target version, PTY allocation, and lifecycle ordering. If the plan changes, refresh preflight before the first attempt. It cannot refresh once recording evidence exists.

4. Record/render once, then independently validate and seal the directory:

   ```text
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record-video <video-directory> --tools-dir .tools/asciinema --json
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-video <video-directory> --tools-dir .tools/asciinema --json
   ```

   Stop on an unexpected target exit or capture failure and retain the attempt evidence. Do not render a failed session as a successful deliverable. `validate-video` writes `validation.json` and `bundle.json` once; do not rerun it over sealed reports. For new recordings use these bundle commands, not the legacy explicit-path `record` interface.

5. For several videos, complete each lifecycle sequentially, then run the read-only batch audit:

   ```text
   uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py audit-video-bundles <first-directory> <second-directory> --json
   ```

6. Replay the cast and inspect the MP4 at full resolution: opening, typed text before each key, key effect, active work, completed response/selection, every TUI handoff, and final exit. Verify every declared real tool appears in order. For `before-final-key`, the MP4 must hold the authentic pre-key target frame; use the full cast/runtime to prove the omitted final key and exit. Follow the lifecycle reference for detailed trim checks. Diagnose a failed review from preserved evidence without rerecording.

## Deliver the evidence

Link each `session.mp4` first, then its `bundle.json`, in its clearly labeled video directory. Report real target identities and exit statuses, completed prompts/actions, and that conversion followed target/recorder closure and cast validation. Keep the untrimmed cast and all hashed evidence beside the MP4. Disclose presentation boundaries, the final key when omitted from the derivative, any requested Windows directory bridge's creation/release, and authorized side effects. If this recording becomes part of a mixed-media production, hand its validated MP4 and manifest to the available compositor.
