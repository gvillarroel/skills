# Platform and tooling

Asciinema records through a Unix pseudo-terminal. Use native Linux or macOS. On Windows, the bundled Python entrypoint automatically forwards `bootstrap-tools`, `record`, and `validate` into the default WSL2 distribution and translates every declared path. Use the same documented commands from PowerShell, Command Prompt, or Git Bash; do not hand-build a nested `wsl bash -lc` command.

## Required commands

- `asciinema`: records the real PTY session to `.cast`.
- `agg`: renders the cast to a one-pass GIF intermediary.
- `ffmpeg`: converts the intermediary to H.264/yuv420p MP4.
- `ffprobe`: verifies codec, pixel format, dimensions, frame rate, and duration.
- `tmux`: provides the real inner terminal emulator used to launch one TUI process or an ordered sequence of distinct TUI processes, inject timed text and explicit keys, inspect ready/busy or target-exit state, and preserve one attached recorded PTY across multi-tool handoffs.
- `script`: required only when an automated shell lacks a TTY; the bundled recorder uses the util-linux implementation to allocate one.

The workflow never enables Asciinema input capture. TUI keystrokes go to tmux's inner PTY and become visible output frames in the outer Asciinema recording. It also never uploads to asciinema.org.

## Terminal preflight

Run preflight after bootstrapping project-local tools and before allocating output paths:

```bash
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" preflight source/session-plan.json --tools-dir .tools/asciinema --json
```

Preflight resolves and hashes every executable, runs each version command, verifies `script` when an automated shell needs a PTY, requires tmux for TUI mode, and returns the expected control-state sequence from recorder startup through media validation. `record` performs the same preflight internally and then atomically creates the plan-scoped one-record claim before Asciinema starts, so bypassing the explicit command does not bypass either gate.

## Project-local pinned tools

When `asciinema` or `agg` is unavailable, install official release binaries into the current project rather than changing the machine globally:

```bash
uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" bootstrap-tools --directory .tools/asciinema --json
```

The bootstrap command supports x86-64 and ARM64 Linux/macOS, pins Asciinema 3.2.1 and agg 1.9.0, verifies the SHA-256 digests published by GitHub's release API, and writes `toolchain-manifest.json`. Add the directory to `PATH` or pass `--tools-dir .tools/asciinema` to `record`.

Install tmux, ffmpeg, and ffprobe through the environment's normal trusted mechanism. The bootstrap command intentionally does not install them.

## Windows/WSL2 path rules

- Let the bundled entrypoint convert skill, plan, working-directory, tool, and output paths. Pass ordinary absolute or workspace-relative Windows paths.
- The bridge runs one complete WSL capture command and invokes the Linux side with `python3`; it does not round-trip prompt text through nested shell interpolation.
- Windows programs exposed through WSL usually resolve with their `.exe` suffix, such as `copilot.exe`, `ffmpeg.exe`, and `ffprobe.exe`.
- The bridge automatically resolves native Windows ffmpeg/ffprobe and the recorder converts their media paths for interop.
- If Copilot is installed only on Windows, set `target.executable` to `copilot.exe`. WSL's normal Windows-path import resolves the authentic binary; use an absolute WSL-visible executable path only when PATH import is disabled.
- Some native Windows TUIs pass the working directory back to Windows tools and fail on a deep WSL-mounted path. Put `{windows_working_directory}` in reviewed TUI `launch_args` only when the target needs a Windows path. Preflight verifies native `/usr/bin/wslpath` and `subst.exe`; the target runner then claims an unused drive letter, maps the exact working directory for that process lifetime, records the expanded argv and helper hashes, removes the mapping, and refuses success without release evidence. For `lazygit.exe`, also set `core.longpaths=true` in the repository-local Git config; preflight rejects a missing value and cast validation rejects long-path errors. Do not create or remove drive mappings manually or change global Git configuration.

## Rendering facts

Asciinema creates the cast, not an MP4. agg officially renders the cast to GIF. The bundled pipeline asks agg for a non-looping render, then uses ffmpeg to create a constant-frame-rate MP4 with even dimensions, H.264 video, yuv420p pixel format, and fast-start metadata. TUI plans require uncapped cast timing, and validation rejects an MP4 shortened below the real-time cast duration. The manifest records every exact command and artifact hash so this derivation is auditable.

Official references:

- <https://docs.asciinema.org/manual/cli/quick-start/>
- <https://docs.asciinema.org/manual/asciicast/v3/>
- <https://docs.asciinema.org/manual/agg/usage/>
