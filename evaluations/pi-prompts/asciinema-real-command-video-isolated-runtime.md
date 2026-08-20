Use `$asciinema-real-command-video` to produce a real, local terminal recording and a verified MP4. Do not simulate a terminal, synthesize command output, or use a browser terminal. After reading this prompt, read `skills/asciinema-real-command-video/SKILL.md` directly. The skill is an instruction directory, not a binary, and it intentionally has no README; do not probe or execute a command named after the skill.

Work only inside the isolated workspace. This host is Windows with WSL2 available. The bundled Python entrypoint automatically converts paths and forwards Unix-only operations into WSL2. Invoke it directly from the current shell; do not call `wsl`, `wslpath`, or `cygpath`, construct nested shell commands, create executable wrappers, or inspect PATH. If `asciinema` and `agg` are missing, use the skill's project-local pinned bootstrap command and install them under `.tools/asciinema`; do not install machine-global packages. Do not inspect bundled script source or `assets/examples`.

Create `source/session-plan.json` with working directory `..`, target name `CPython`, executable `python3`, version arguments `--version`, 92 columns, 24 rows, GitHub Dark theme, 16 px font, 1.35 line height, 24 fps, speed 1, idle limit 1 second, and final-frame duration 1.5 seconds. The declared scope must say these are read-only local Python invocations.

Use exactly these three prompts, in this order:

1. `Count every word in this exact first prompt.`
2. `Compute the SHA-256 of this exact second prompt.`
3. `Report which Python executable handled this exact third prompt.`

For each step, invoke the real `python3` target with direct argv: `-c`, a short Python program, and `{prompt}` as its own argument. The Python program must print `REAL CPYTHON PROCESS`, `sys.executable`, the exact prompt received, its word count, and its SHA-256. Use a 30-second timeout, a 0.3-second pause, and expected exit code 0. Do not route prompt text through a shell.

After creating the plan, run these public commands from the workspace root in this order. Do not replace them with hand-built WSL commands:

```bash
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-plan source/session-plan.json --json
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py bootstrap-tools --directory .tools/asciinema --json
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --tools-dir .tools/asciinema --json
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate --plan source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --json > artifacts/manifests/validation.json
```

Create these exact non-empty outputs:

- `source/session-plan.json`
- `artifacts/casts/session.cast`
- `artifacts/videos/session.mp4`
- `artifacts/manifests/session.manifest.json`
- `artifacts/manifests/session.manifest.runtime.json`
- `artifacts/manifests/validation.json`

Run the bundled independent `validate` command after recording. Write its unmodified `--json` stdout to `artifacts/manifests/validation.json`. The final validation must report `status: passed`, `prompt_count: 3`, target name `CPython`, H.264 codec, yuv420p pixel format, and 24 fps. Return a concise result with the output paths and validation status.
