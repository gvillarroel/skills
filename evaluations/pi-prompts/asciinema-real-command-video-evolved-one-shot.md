Use `$asciinema-real-command-video` to produce one authentic recording of the
installed `fzf` TUI. Do not simulate a terminal, replace fzf, or use a custom
picker. After reading this prompt, read
`skills/asciinema-real-command-video/SKILL.md` and its linked interaction
recipe for one-shot fzf. Do not inspect the bundled Python source, acceptance
fixtures, ancestor repositories, or any other skill.

Work only inside this isolated workspace. The host is Windows with WSL2, and
the bundled entrypoint handles path translation. Create `source/fzf-items.txt`
with exactly these lines in this order:

```text
alpha
beta
gamma
```

Create `source/session-plan.json`. It must use:

- target name `fzf`, executable `fzf.exe`, and version args `["--version"]`;
- working directory `..` (the workspace root, because the plan is under
  `source/`) and a read-only local declared scope;
- one real TUI process launched with prompt `QUERY> ` and the documented
  Windows/WSL-compatible fixed `pwsh.exe Get-Content` start/reload binding for
  `source/fzf-items.txt`;
- typing interval 0.08 seconds, pre-submit pause 0.5 seconds, startup and exit
  timeouts of 30 seconds, ready pattern
  `(?m)(?:^QUERY>\s*$|^gamma\s*$)`, never-matching busy pattern `(?!)`, settle
  time 0.5 seconds, `shutdown_mode` `target-exit`, no `exit_text`, and only
  exit status 0;
- terminal size 100x30, GitHub Dark theme, font size 18, line height 1.4,
  30 fps, speed 1.0, null idle-time limit, and a two-second final hold;
- presentation start `tui-ready` and end `before-final-key`;
- exactly one action step: visibly type `gamma`, pause 0.75 seconds, then send
  one real `Enter`; complete on `target-exit`, allow 30 seconds, and add no
  post-step pause.

Follow this order exactly after reading the skill instructions. The workspace
starts without `source/` or `artifacts/`; do not read, list, or execute either
path before creating its requested content:

1. Create `source/`, `artifacts/casts/`, `artifacts/videos/`,
   `artifacts/manifests/`, and `artifacts/reviews/`.
2. Write `source/fzf-items.txt` immediately, then write
   `source/session-plan.json` immediately. Confirm both are non-empty before
   running any target or source command.
3. Run the fixed `pwsh.exe -NoLogo -NoProfile -NonInteractive -Command
   "Get-Content -LiteralPath source/fzf-items.txt"` source command once outside
   the camera and require it to print the three fixture lines. This is a
   read-only launch preflight, not a second fzf process or recording.
4. Run plan validation, project-local pinned tool bootstrap, and explicit
   preflight.
5. Run one and only one `record` command.
6. Run the independent `validate` command and save its unmodified JSON output
   at `artifacts/manifests/validation.json`.
7. Create the two requested PNG samples.

Use the literal workspace-relative skill script and `.tools/asciinema`. Do not
copy or rename the plan, and do not invoke `record` a second time if anything
fails. A tool or command error is an evaluation failure; do not deliberately
probe missing paths or unsupported alternatives.

Use exactly these recording outputs:

- `artifacts/casts/session.cast`
- `artifacts/videos/session.mp4`
- `artifacts/manifests/session.manifest.json`

The runner must also produce:

- `source/.session-plan.recording-attempt.json`
- `artifacts/manifests/session.manifest.runtime.json`

After independent validation passes, create exactly two visual samples with
the installed ffmpeg, without overwriting existing files:

```bash
ffmpeg -hide_banner -loglevel error -n -i artifacts/videos/session.mp4 -frames:v 1 artifacts/reviews/first.png
ffmpeg -hide_banner -loglevel error -n -sseof -0.05 -i artifacts/videos/session.mp4 -frames:v 1 artifacts/reviews/last.png
```

The validator must report `status: passed`, target `fzf`, final exit status 0,
H.264/yuv420p at 30 fps, zero cast input events, `presentation.start_at` equal
to `tui-ready`, `presentation.end_at` equal to `before-final-key`, a positive
final hold, and checks that include `explicit-tui-actions`,
`enter-submission`, `target-exit-completion`, `before-final-key-marker`,
`before-final-key-presentation`, `single-record-attempt`, and
`real-time-duration`. The first and last PNG must visibly belong to the real
fzf UI; the final PNG should retain the filtered `gamma` picker immediately
before Enter. The untrimmed cast/runtime evidence, not the presentation trim,
must prove Enter and fzf's real exit.

Return a concise result with the exact output paths and validation status.
