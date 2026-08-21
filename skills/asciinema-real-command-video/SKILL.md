---
name: asciinema-real-command-video
description: Record authentic persistent, one-shot, command-key TUI, or direct-argv executions of installed terminal programs as local Asciinema casts and derived H.264 MP4 videos with executable, text/key action, process, single-attempt, and media provenance. Use when a demo must visibly interact with the real CLI, including GitHub Copilot, pickers, or other TUIs, instead of showing a simulated terminal.
---

# Asciinema Real Command Video

Treat the asciicast as the source of truth and the MP4 as a rendered derivative. Run the named product, with the requested prompts, in the requested project. Never substitute prerecorded text, an HTML terminal, generated output, or a look-alike command.

Use interactive TUI mode whenever the user asks to see the product UI, prompt typing, live work, selections, command keys, or conversational continuity. Launch the target once and deliver only the reviewed text and key actions through its real PTY. Persistent editors use typed prompts plus Enter and return-to-ready gating; one-shot pickers and command-key TUIs use explicit actions and target-exit gating. Use direct-argv mode only for explicitly non-interactive command recordings.

Run the capture pipeline natively on Linux or macOS. On Windows, the bundled command automatically translates paths and re-executes Unix-only operations inside the default WSL2 distribution. Invoke the bundled script by its literal absolute or workspace-relative path. If using `ASCIINEMA_VIDEO_SKILL`, assign and export it in a separate shell statement before expanding it; a one-shot prefix such as `ASCIINEMA_VIDEO_SKILL=... uv run --script "$ASCIINEMA_VIDEO_SKILL/..."` expands the old or empty value in POSIX shells.

## Authenticity contract

- Resolve the target executable before recording and capture its real version output.
- Put the exact prompt text in a reviewed session plan. Never interpolate it into a shell command.
- In TUI mode, launch one target process inside an isolated tmux terminal. Use a `prompt` step only for text that is visibly typed, submitted with real Enter, and followed by a stable ready-without-busy screen. Use explicit `text`, `key`, and `pause` actions when Enter exits a picker or a command key such as `q` ends the TUI; never invent prompt text or Enter.
- In direct-argv mode, pass each prompt as one direct argument. Preserve conversation context with an explicit session identifier rather than a global "most recent session."
- Record the target inside `asciinema rec`. Require an Asciinema session ID, a PTY, step/action markers, input hashes, observed exit codes, and zero Asciinema input events. TUI keystrokes are injected into the inner PTY and recorded as visible terminal output, not secret-bearing cast input events.
- Allow exactly one `record` transaction per user-requested deliverable. The runner atomically claims an immutable plan-adjacent attempt ledger after preflight. Freeze the plan and exact output paths first; a renamed plan, alternate output path, or technically adjusted launch does not authorize a retry. Preserve the ledger and every failed artifact.
- Keep the plan, `.cast`, runtime report, MP4, and final manifest. Hash every evidence artifact and independently validate them after rendering.
- Preserve real-time TUI timing with render speed `1.0` and no idle-time cap. Do not shorten Copilot thinking time or response latency.
- For a user-facing TUI deliverable, set `render.start_at` to `tui-ready`. Keep the complete technical lead-in in the cast and manifest, while starting the MP4 on the real product UI instead of blank frames or the controller provenance card. For a command-key TUI that clears its screen on quit, also set `render.end_at` to `before-final-key` so the derivative freezes the last authentic in-app frame while the full cast still proves delivery of the quit key and the real process status.
- Do not claim that a successful render proves the target behaved correctly. Report the target exit codes and inspect the visible response.

## Terminal-control lifecycle

Treat recording as one controlled terminal transaction, not as independent command output plus later animation. Enforce this order:

1. Run preflight and resolve/version the recorder, PTY allocator, TUI multiplexer when needed, real target, renderer, encoder, and media probe.
2. Start `asciinema rec` and attach the outer PTY before allowing the target to launch. The TUI start gate exists to prevent missing its opening screen.
3. In TUI mode, wait for a real ready screen and execute the reviewed step contract. For a persistent prompt, type, capture, send Enter, and wait for ready-without-busy. For explicit actions, send each declared text/key/pause in order and gate completion on either ready or the target's real exit. In direct-argv mode, run each real process and gate on its timeout and exit status.
4. Either request the configured normal exit or accept the final action's target-driven exit, verify the real process status, detach the inner PTY, and let Asciinema stop. Always clean up the isolated tmux server.
5. Validate the cast and runtime evidence before rendering. Only then render with agg, encode with ffmpeg, probe the MP4, and run the independent artifact gate.

When `render.start_at` is `tui-ready`, emit and verify a hidden ready-screen marker, retain the full cast, and trim only the MP4 lead-in to just before the first stable ready-screen update. Derive the lead from the startup settle window plus a small render margin so the empty editor appears before the first typed character. By default, end the MP4 immediately before tmux restores the controller terminal. When a target-exit action plan ends in a quit or selection key and that key clears the TUI, use `render.end_at: "before-final-key"`: the controller emits a hidden marker immediately before that real key, the MP4 ends at the marker, and ffmpeg freezes that authentic target frame for `last_frame_duration`. The untrimmed cast and runtime report must still prove the key, target exit, and exit status. Never use presentation trims to shorten prompt typing, target work, responses, or any target-owned output that the user asked to see.

If target startup, interaction, shutdown, or cast validation fails, preserve the attempt ledger, failed cast, and runtime report for diagnosis. Stop the requested deliverable. Do not invoke `record` again under the same or a different plan/output name, and do not convert the failure into a successful deliverable. A later recording requires a new user request or explicit authorization, not an agent-authored retry.

## Workflow

1. Freeze the exact prompts or actions, their order, target executable, working directory, interaction and shutdown modes, completion signals, allowed side effects, and exact output paths. Do not broaden tool permissions merely to make an unattended recording finish.
2. Authenticate and accept any first-run trust prompt outside the recording. Never place credentials, tokens, passwords, private keys, or authentication UI in the plan or video.
3. Copy `assets/templates/session-plan.json` outside the skill and adapt it. For a native Windows lazygit command-key recording, copy both `assets/templates/lazygit-session-plan.json` and `assets/templates/lazygit-config.yml` to the plan and repository paths documented in [references/interaction-recipes.md](references/interaction-recipes.md), and enable `core.longpaths=true` in that repository's local Git config only. Keep the template's `{windows_working_directory}` arguments: during the single recorded launch, the controller creates a collision-checked temporary drive mapping for the real repository, expands the reviewed token, records the exact launch argv, and removes the mapping before reporting success. Read [references/session-plan.md](references/session-plan.md) for the schema. For GitHub Copilot CLI, also read [references/github-copilot-cli.md](references/github-copilot-cli.md). For one-shot pickers, raw command keys, or a fixed PowerShell pipeline, read [references/interaction-recipes.md](references/interaction-recipes.md).
4. Validate the plan before executing it:

   ```bash
   uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" validate-plan source/session-plan.json --json
   ```

   In a Windows Git Bash tool shell, avoid variable/path rewriting ambiguity by using the literal relative path and `MSYS_NO_PATHCONV=1`, for example:

   ```bash
   MSYS_NO_PATHCONV=1 uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py validate-plan source/session-plan.json --json
   ```

5. Confirm `asciinema`, `agg`, `ffmpeg`, and `ffprobe` are available in the same Unix environment. TUI mode also requires `tmux`. If Asciinema or agg is absent, read [references/platform-and-tooling.md](references/platform-and-tooling.md) and install the pinned official binaries into a project-local tool directory.
6. Run terminal preflight before creating recording artifacts. It verifies every lifecycle component, the target version, the PTY allocator for non-interactive automation, and the expected state order:

   ```bash
   uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" preflight source/session-plan.json --tools-dir .tools/asciinema --json
   ```

7. Record and render the frozen deliverable to its exact new paths once. `record` repeats preflight, atomically creates the immutable attempt ledger, starts Asciinema, and refuses existing evidence or a second transaction for the plan. Never create `retry`, `fixed`, numbered, or alternate plan/output names after this command begins:

   ```bash
   uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" record source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --tools-dir .tools/asciinema --json
   ```

8. Run the independent gate even though `record` validates internally:

   ```bash
   uv run --script "$ASCIINEMA_VIDEO_SKILL/scripts/asciinema_command_video.py" validate --plan source/session-plan.json --cast artifacts/casts/session.cast --mp4 artifacts/videos/session.mp4 --manifest artifacts/manifests/session.manifest.json --json
   ```

9. Replay the cast and inspect the MP4 at full resolution. Sample the opening, every typed-text-before-key state, command-key effect, active work, completed response or selection, and final exit. For `tui-ready` presentation, require both the first and last visible frames to belong to the real target TUI, with no controller card, blank startup interval, tmux `[exited]` screen, or restored outer terminal. For `before-final-key`, verify the held last frame is the actual target screen immediately before the declared key; verify the key effect and exit in the cast/runtime evidence because they are intentionally outside the presentation derivative. If review fails, report and diagnose the preserved failed attempt; do not rerecord the deliverable under any name.

## Boundaries and safety

- Keep Asciinema input capture disabled. In TUI mode, the runner sends reviewed keystrokes only to the isolated inner PTY; in direct-argv mode, it prints prompt annotations and invokes the executable with direct arguments.
- The skill directory is an instruction bundle, not an executable named `asciinema-real-command-video`. Invoke the bundled Python script exactly as shown above.
- Never add blanket approval flags such as `--yolo` or `--allow-all-tools`. Add only permissions the user authorized and the target can narrowly enforce.
- Stop on the first unexpected target exit code. Preserve the attempt ledger, failed cast, and runtime report for diagnosis; do not render or rerecord a failed run as a successful deliverable, including through an alternate plan or output name.
- Never launch the target before the recorder's PTY is attached, and never begin conversion while the target or recording session is still active.
- Keep recording and rendering local. Upload a cast, gist, session, or video only when the user explicitly asks.
- Use this skill for a direct terminal MP4. If the terminal recording later becomes one element in a narrated or mixed-media production, hand the validated MP4 and manifest to the available video compositor without recreating the terminal.

## Delivery

Return the preflight result, session plan, immutable attempt ledger, `.cast`, runtime report, MP4, and manifest, plus the validation result and target version. For TUI work, state that one real target process received the reviewed prompt or explicit action sequence, how each step completed, and that conversion began only after the recording closed and the cast passed. When the Windows working-directory bridge was requested, include its created-and-released runtime evidence. Disclose every presentation trim. If the MP4 uses `before-final-key`, state which final key is proven by the full cast/runtime report and that the MP4 intentionally freezes the preceding authentic target frame. Confirm that the full cast remains untrimmed and disclose any authorized side effects.
