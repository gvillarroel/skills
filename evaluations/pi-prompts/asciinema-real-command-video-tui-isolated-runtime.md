Use `$asciinema-real-command-video` to produce a real interactive TUI recording and a verified real-time MP4. Do not simulate a terminal, synthesize output, use a browser terminal, or substitute direct-argv prompt execution. After reading this prompt, read `skills/asciinema-real-command-video/SKILL.md` directly. The skill is an instruction directory, not a binary.

Work only inside the isolated workspace. This host is Windows with WSL2 available. The bundled Python entrypoint automatically converts paths and forwards Unix-only operations into WSL2. Invoke the literal workspace-relative script path shown below from the current shell. Do not assign `ASCIINEMA_VIDEO_SKILL`, probe `--help`, call `wsl`, `wslpath`, or `cygpath`, construct nested shell commands, create executable wrappers, inspect PATH, or invent alternate entrypoints. If `asciinema` and `agg` are missing, use the skill's project-local pinned bootstrap command under `.tools/asciinema`; do not install machine-global packages. Do not inspect bundled script source, acceptance fixtures, sibling skills, or repository documentation.

Create `source/fake_tui.py`, a small real line-oriented Python TUI. It must run unbuffered, print `REAL INTERACTIVE PYTHON TUI`, then display an empty `READY> ` prompt. For every submitted line except `/exit`, it must print a standalone transient `BUSY` line, pause briefly, move the cursor back one row and erase that entire `BUSY` line with ANSI control sequences, visibly stream a deterministic `RESPONSE: <exact received text>` on the cleared row, then display a fresh empty `READY> ` prompt. No completed screen may retain the word `BUSY`. On `/exit`, it must print `REAL TUI EXIT: 3 prompts processed` and exit with status 0. Keep the implementation deterministic, local, and dependency-free.

Create `source/session-plan.json` with working directory `..`, target name `Real Python TUI`, executable `python3`, version arguments `--version`, and an interactive TUI object. Launch the persistent target with `-u source/fake_tui.py`. Type one character every 0.025 seconds, pause 0.25 seconds before Enter, allow 30 seconds for startup and exit, use ready pattern `(?m)^READY>\s*$`, busy pattern `(?m)^BUSY$`, settle for 0.5 seconds, type `/exit` to close, and accept only target exit status 0. Use 100 columns, 26 rows, GitHub Dark theme, 16 px font, 1.35 line height, 24 fps, speed 1, null idle-time limit, final-frame duration 0.5 seconds, and `start_at` value `tui-ready`. The declared scope must say this is a deterministic local TUI with no file, network, or external side effects.

Use exactly these three single-line prompts, in this order:

1. `alpha one`
2. `beta two`
3. `gamma three`

Each step must have a 30-second response timeout and 0.3-second pause. TUI steps must not contain direct-argv fields. The video must show each prompt appearing character by character in the real `READY>` editor, a real Enter submission, the `BUSY` state, the streamed response, and the next ready editor. All prompts must share the same Python process. Preserve real timing; do not cap idle time or speed up rendering.

Create the needed artifact directories, then run these public commands exactly in order. The direct relative script path and `MSYS_NO_PATHCONV=1` avoid Git Bash path rewriting; do not probe alternative forms first. The explicit preflight must pass before `record`, and the returned state order must begin with `preflight-passed` and end with `media-validated`.

```bash
MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-plan source/session-plan.json --json
MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py bootstrap-tools --directory .tools/asciinema --json
MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py preflight source/session-plan.json --tools-dir .tools/asciinema --json
MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --tools-dir .tools/asciinema --json
MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate --plan source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --json > artifacts/manifests/validation.json
mkdir -p artifacts/reviews
ffmpeg -hide_banner -loglevel error -y -i artifacts/videos/session.mp4 -frames:v 1 artifacts/reviews/first.png
ffmpeg -hide_banner -loglevel error -y -sseof -0.1 -i artifacts/videos/session.mp4 -frames:v 1 artifacts/reviews/last.png
```

Use these exact output paths:

- `source/fake_tui.py`
- `source/session-plan.json`
- `artifacts/casts/session.cast`
- `artifacts/videos/session.mp4`
- `artifacts/manifests/session.manifest.json`
- `artifacts/manifests/session.manifest.runtime.json`
- `artifacts/manifests/validation.json`
- `artifacts/reviews/first.png`
- `artifacts/reviews/last.png`

Save the independent validator's unmodified JSON result to `artifacts/manifests/validation.json`. It must report `status: passed`, `prompt_count: 3`, target name `Real Python TUI`, H.264 codec, yuv420p pixel format, 24 fps, presentation start `tui-ready`, positive lead-in and trailing trims, and checks including `timed-keystrokes`, `enter-submission`, `tui-ready`, `tui-ready-marker`, `tui-ready-presentation`, `tui-final-hold`, `tui-exit-presentation`, `target-exit`, and `real-time-duration`. Use only the two exact ffmpeg frame-extraction commands above for visual sampling; do not run exploratory timestamp sweeps, alternate seeks, image-recognition tools, or undeclared image packages. Leave both PNGs for the independent evaluator, which will confirm that the first frame is the real ready TUI and the final frame is the target's own exit screen, with no blank/controller lead-in, tmux `[exited]` screen, or restored outer terminal. Return a concise result with the exact paths and validation status.
