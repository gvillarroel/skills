# Asciinema Real Command Video Interactive TUI Validation - 2026-08-20

## Outcome

`asciinema-real-command-video` now records authentic interactive terminal applications as well as direct-argv commands. When a user asks to see a TUI, the skill launches one persistent target in an isolated tmux PTY, types each reviewed prompt character by character, sends Enter, waits for the real application's busy state to clear, and preserves the complete terminal transaction at real speed in an Asciinema cast. The derived H.264 MP4 can present only the real target interaction, from its stable ready screen through its own final exit screen, without discarding the untrimmed cast evidence.

The implementation does not invoke Copilot with `-p`, reconstruct output, draw a browser terminal, enable Asciinema input capture, upload a session, or grant broad tool permissions.

## Interactive implementation evidence

- The strict JSON plan has separate schemas for persistent TUI and direct-argv steps.
- TUI launch arguments start the named executable exactly once and cannot contain `{prompt}`.
- Each single-line prompt is delivered one Unicode character at a time with `tmux send-keys -l`, held visibly before submission, and followed by a real Enter key.
- A response completes only when the configured ready pattern matches, the transient busy pattern does not match, and that state remains stable for the configured settle interval.
- The controller captures bounded visible-screen snapshots and SHA-256 values immediately before Enter and after every completed response.
- Independent validation requires exact prompt hashes, exact keystroke counts, visible pre-submit prompts, Enter markers, non-busy ready screens, one final target exit status, a real Asciinema PTY/session, and zero Asciinema input events.
- TUI plans require render speed `1.0` and `idle_time_limit: null`; the MP4 cannot be shorter than the uncapped cast timing.
- The final exit command is typed through the same PTY. Copilot's `/exit` therefore remains visible and produces Copilot's own session summary.
- A `tui-ready` presentation emits a hidden marker after the stable startup gate and derives a small evidence-backed lead so the first MP4 frame shows the real empty editor before typing begins.
- The controller holds the target's real final screen inside its PTY, then ends the MP4 immediately before tmux restores the outer controller terminal. The cast retains both controller transitions for provenance.
- Windows recording continues to use the public Python entrypoint, automatic WSL2 path translation, official project-local Asciinema/agg binaries, native Windows target execution where requested, and ffmpeg/ffprobe media verification.

## Real GitHub Copilot CLI capture

The initial successful run used this public command:

```powershell
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record projects/asciinema-copilot-tui-demo/source/session-plan.json --cast projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-4/session.cast --mp4 projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-4/session.mp4 --manifest projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-4/session.manifest.json --tools-dir projects/asciinema-real-command-video/artifacts/tools --json
```

One authenticated `copilot.exe` TUI received these exact prompts in order:

1. `Show only a Python add(a, b) function. Do not use tools.`
2. `Add integer type hints and a one-line docstring to that function. Do not use tools.`
3. `Give three concise pytest assertions for the final function. Do not use tools.`

Observed evidence:

- Resolved executable: `/mnt/c/Users/villa/AppData/Local/Microsoft/WinGet/Links/copilot.exe`.
- Executable SHA-256: `3a2095d3b6ac51a53c68329599f3d5bbe0e17e2efb04c1f5c758618683f78731`.
- Version command: GitHub Copilot CLI 1.0.75; the interactive banner displayed Copilot v1.0.73.
- Run UUID: `19120651-6761-46e6-9679-d8c8a7ce5082`.
- Final target status: 0 after a visibly typed `/exit` and Copilot session summary.
- Plan SHA-256: `4c54d8f79dbe58a2fb78ea86d567031f5d602ea6559dd5306e3c505c841ed763`.
- Cast SHA-256: `078c91f3cc981865f4942e929fa891b4302d7d2a334ce8655c6f94217fd5b4eb`.
- MP4 SHA-256: `d73130f5e46cc783aed5e50530a7a05b78bdf4b8a2b27be18b674de00d03b9c8`.
- MP4: H.264 High, yuv420p, 1214x882, 30 fps, 1,448 frames, 48.266667 seconds, 735,078 bytes.
- All 36 distinct provenance, PTY, keystroke, completion, cast, and media checks passed in both the internal and independent validators.
- Runtime evidence records 56, 83, and 78 keystrokes respectively; every step shows the exact prompt before Enter and ends ready with `busy_after_response: false`.
- The three completed responses visibly contain the requested function, typed/docstring revision, and three assertions. The final Copilot footer reported 1.16 AIC used.

A full-resolution 16-frame contact sheet was reviewed at `projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-4/screenshots/contact-sheet.png`. It shows the controller identity card, incremental prompt typing, `Working ... esc interrupt`, each completed answer, the persistent shared history, and the final Copilot exit summary. No clipping, wrapping failure, tmux status bar, synthetic terminal chrome, or missing response was found. Later user review correctly identified that the controller card and restored outer terminal did not belong in the user-facing MP4.

### Target-only replacement capture

The corrected run retained the entire controller transaction in the cast but derived the MP4 only from the real Copilot TUI interval:

```powershell
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record projects/asciinema-copilot-tui-demo/source/session-plan-clean.json --cast projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-clean-2/session.cast --mp4 projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-clean-2/session.mp4 --manifest projects/asciinema-copilot-tui-demo/artifacts/real-copilot-tui-clean-2/session.manifest.json --tools-dir projects/asciinema-real-command-video/artifacts/tools --json
```

Observed evidence:

- Run UUID: `3ecdd364-d14a-4436-b94c-3bc374f9f233`; target exit status 0.
- Plan SHA-256: `cfa57c09f393caad01495fa0e855e0116dbc90a961075a857aa0da23f3ef353b`.
- Cast SHA-256: `ce55c01c1a85de9b8cccc5a716a2934b7882a3d3b642ce6d688a9a863c5e29ac`; full cast duration 56.409 seconds.
- MP4 SHA-256: `b4a3fca2f3d9de4c808f763860d0f6e70fe783f44bc464ea3deee704b478a9e3`.
- MP4: H.264 High, yuv420p, 1214x882, 30 fps, 1,580 frames, 52.666667 seconds, 845,271 bytes.
- The hidden ready marker occurred at cast time 4.594 seconds. The derived presentation includes a 0.9-second real-TUI lead, trims 3.694 seconds of controller/startup material, holds Copilot's final summary for 0.5 seconds, and ends 0.126 seconds before the outer terminal restoration.
- The internal gate passed 26 checks and a separate `validate` invocation passed 41 checks, including `tui-ready-marker`, `tui-ready-presentation`, `tui-final-hold`, and `tui-exit-presentation`.
- Full-resolution first-frame, opening-contact-sheet, whole-video-contact-sheet, and last-frame review confirmed: Copilot is already visible and ready in frame one; all three prompts are typed and answered in one process; `/exit` is visible; the last frame is Copilot's own Changes/AIC/Tokens/Resume summary. No controller card, blank lead-in, tmux `[exited]` screen, or restored outer terminal appears in the MP4.

## Deterministic integration and regression tests

The final deterministic TUI integration used the public Windows entrypoint and current visible-pane state capture:

```powershell
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record projects/asciinema-real-command-video/source/fake-tui-session-plan.json --cast projects/asciinema-real-command-video/artifacts/tui-smoke-4/session.cast --mp4 projects/asciinema-real-command-video/artifacts/tui-smoke-4/session.mp4 --manifest projects/asciinema-real-command-video/artifacts/tui-smoke-4/session.manifest.json --tools-dir projects/asciinema-real-command-video/artifacts/tools --json
```

It passed the same 36-check gate with three visibly typed prompts, one persistent CPython 3.12.3 TUI, target exit 0, an 11.566667-second 1106x782/30 fps H.264 MP4, cast SHA-256 `8b3687cf62fe4fd62f344cf95c7c93d8e3ab22219c63968e3f73edd4b9def740`, and MP4 SHA-256 `00083145991f24311aec227e177de0d152189e749cde180fb453562b0cf1b2a7`.

The final target-only deterministic regression used `fake-tui-session-plan-target-only.json` and output directory `tui-target-only-smoke-7`. The complete cast is 11.609 seconds; the derived 10.433333-second 1106x782/30 fps H.264 MP4 passed all 41 independent checks, target exit 0, and hashes `dcfac0f3b4524b7f8664c83fd727a8b7f9e1438edbf07a6e1d849d0aed3e4a82` (cast) and `09e0b30964584084dc268610497467eeca56b3d86f7c4bd8653b8cec0b692c48` (MP4). Full-resolution review confirmed an empty real `READY>` editor in the first frame and `TUI closed normally.` in the last frame, with no controller material at either boundary.

The expanded unit suite passed 22/22 cases:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --script skills/asciinema-real-command-video/scripts/test_asciinema_command_video.py
```

New coverage includes valid persistent-TUI plans, separation from direct-argv step fields, uncapped real-time rendering, simultaneous ready/busy detection, TUI prompt/screen hashes, timed-keystroke evidence, Enter evidence, non-busy completion, final target exit evidence, the complete terminal lifecycle contract, the public preflight parser, mode-safe `tui-ready` presentation, and cumulative asciicast timing for the hidden ready marker and terminal restoration. The original duplicate-key, secret, shell-metacharacter, direct-argv, stop-on-failure, no-overwrite, cast, input-event, WSL-path, and official-tool-pin tests remain green.

## Full terminal lifecycle hardening

The skill now treats terminal control as one ordered, fail-closed transaction rather than a collection of loosely related commands:

1. Run an explicit preflight before creating recording artifacts. Resolve, version, and hash the target, Asciinema, agg, ffmpeg, ffprobe, tmux for TUI mode, and the util-linux `script` PTY allocator used by non-TTY automation.
2. Start Asciinema and attach its recording PTY before launching the target.
3. Launch one persistent real TUI, wait for its ready screen, type literal characters, submit a real Enter key, and gate every response on ready-without-busy screen state.
4. Type the target's normal exit command, verify its accepted exit status, leave the target PTY, and only then stop Asciinema.
5. Validate the cast before agg rendering, encode the rendered stream with ffmpeg, and validate the final H.264/yuv420p media with ffprobe.

The manifest records and the independent validator checks this exact state order:

```text
preflight-passed
recording-started
pty-attached
target-launched
target-ready
prompt-typed
enter-submitted
response-complete
target-exit-requested
target-exited
recording-stopped
cast-validated
render-complete
encode-complete
media-validated
```

The prompt typing, Enter submission, and response completion states repeat once per prompt. Conversion cannot begin while the target or recorder is active.

The real Copilot plan passed the new public preflight with GitHub Copilot CLI 1.0.75, Asciinema 3.2.1, agg 1.9.0, tmux 3.4, util-linux `script` 2.39.3, and ffmpeg/ffprobe 8.1.1. The pre-hardening `real-copilot-tui-4` evidence bundle was then revalidated with the hardened code and retained `status: passed` across its original 36 backward-compatible checks, target exit 0, and unchanged cast/MP4 hashes. The deterministic full-lifecycle smoke used the same public Windows entrypoint and produced target exit 0, cast SHA-256 `05467625dd9fcd3af308c567226fcd517d5311cf46b40d4643f73e9eea49ba8f`, and MP4 SHA-256 `5fdb01467c7c27e0511124ead5f4cf625b66bb6b6763b4155303497cae6107e1`. Its 11.566667-second 1106x782/30 fps H.264 video passed all 37 independent checks, including `terminal-control-lifecycle`.

## Isolated Spark forward tests

All completed runs used the runtime payload profile, strict JSON mode, and `openai-codex/gpt-5.3-codex-spark`.

1. `asciinema-real-command-video-tui-20260820-spark-1` was terminated by the parent orchestration call after five seconds because that call used an accidental short tool timeout. It did not reach an evaluation result. Classification: external harness invocation error; no skill conclusion.
2. `asciinema-real-command-video-tui-20260820-spark-2` exited Pi successfully and passed all seven artifact, five JSON-field, and unchanged-payload gates, but failed the strict event gate after nine recoverable tool errors. The trace exposed a POSIX one-shot environment assignment whose variable expanded empty, a test TUI that retained `BUSY` as historical output, and an undeclared Pillow probe. Classification: skill operational guidance plus evaluation-fixture weakness. Fixes: document literal Git Bash invocation, inspect only the visible tmux pane, require busy indicators to be transient, give the fixture exact clearing behavior, and use ffmpeg/metadata-only visual checks.
3. `asciinema-real-command-video-tui-20260820-spark-3` passed every strict gate in 60.203 seconds. Pi exited 0; seven exact non-empty outputs, five asserted JSON fields, observed Spark model, valid event JSON, zero tool errors, a focused read surface, and unchanged payload all passed.
4. `asciinema-real-command-video-terminal-lifecycle-20260820-spark-1` passed every strict gate after the lifecycle hardening. The isolated agent executed validate-plan, bootstrap, explicit preflight, record, and independent validate in the required order. Pi exited 0; seven exact outputs, five JSON fields, observed Spark model, valid event JSON, zero tool errors, focused reads, and unchanged payload all passed.
5. `asciinema-real-command-video-target-only-20260820-spark-1` was terminated by its parent shell call after an accidental five-second wrapper timeout, before an evaluation result existed. Classification: external harness invocation error; no skill conclusion.
6. `asciinema-real-command-video-target-only-20260820-spark-2` exited Pi 0 and passed all seven artifact outputs, all seven JSON fields, and unchanged-payload gates. Strict status failed only because the agent improvised a four-timestamp ffmpeg loop and its final speculative seek exceeded the six-second video. Classification: evaluation prompt ambiguity, not recorder or artifact failure. The prompt was narrowed to two exact first/last frame extraction commands and made both PNGs evaluator-owned outputs.
7. `asciinema-real-command-video-target-only-20260820-spark-3` passed every strict gate after that evaluation correction. Pi exited 0; nine exact outputs, seven JSON fields, observed Spark model, valid event JSON, zero tool errors, focused reads, unchanged payload, and independent full-resolution first/last frame review all passed.

Pre-hardening isolated evidence:

- Payload SHA-256 before/after: `6f08fca21f533d53f84e8d776fdb5dd11b97b1198deba880434c4a122b7486a5`.
- Plan SHA-256: `7d22b607e3d662124df4e6b01c1dea40f26e0ab7740bf4c361393a6154db27ba`.
- Cast SHA-256: `025ca857f7dde14b178d200255fe573bc19c5a8862c38509ca97a4d093dd36f4`.
- MP4 SHA-256: `6eb2701189599efffdff38f5b279e6db9b586dec7fe9e90a0777f3fa0116bc07`.
- Video: H.264/yuv420p, 984x584, 24 fps, 187 frames, 7.791667 seconds.
- Read surface: prompt, `SKILL.md`, the session-plan template, and the generated plan/validation/manifests. It did not read script source, acceptance examples, sibling skills, repository documentation, or project artifacts.
- Independent contact-sheet review showed identity, all three incremental prompts, transient `BUSY`, deterministic responses, ready states, and the final target exit.

Lifecycle-hardening isolated evidence:

- Evaluation duration: 68.453 seconds; Pi exit 0; all artifact, event, JSON-field, and skill-integrity gates passed.
- Payload SHA-256 before/after: `84470595ce014f816ab2b5d4afcf217f1ad6f07adfc70e8be402d7dce4ed9d91`.
- Plan SHA-256: `7777faccecb2f2a0004fbfaf0371e18e297379f0931be1442ffde62e857ab0f4`.
- Cast SHA-256: `8e0420f1579b65994c1acbd43377e7ad8c564259e34e0886bf8619a32889c937`.
- MP4 SHA-256: `3aaa24ceef9428322724b0c7b325ecad2ff432dac1ab29959903e616be87b257`.
- Video: H.264/yuv420p, 984x584, 24 fps, 193 frames, 8.041667 seconds.
- The independent validator passed all 37 checks, including `terminal-control-lifecycle`; the target exited 0 after `REAL TUI EXIT: 3 prompts processed`.
- Read surface: prompt, `SKILL.md`, the session-plan template, the focused session-plan reference, and generated artifacts. It did not read script source, acceptance fixtures, sibling skills, repository documentation, or project artifacts.
- Full-resolution review confirmed incremental typing, each prompt before Enter, all three transient `BUSY` screens, completed responses, typed `/exit`, and the recorder's final exited state.

Target-only presentation isolated evidence:

- Evaluation duration: 66.953 seconds; Pi exit 0; all artifact, event, JSON-field, and skill-integrity gates passed.
- Payload SHA-256 before/after: `56a4c25e16bc32003de3723050d7cf8ed532e13ecab8e35dcc9b075304b0ede9`.
- Plan SHA-256: `9c2264b88cdf11537deef3a5b079a2f973c2115d1446e61256581df9fb9db263`.
- Cast SHA-256: `f67b84b3914dfa94b360c71b43cfd145ef8653c68496eaf8bd6bb06ee3c4de35`.
- MP4 SHA-256: `6e70b2abb0aa660f232e8dab6ec7d4bee4f4173c08bc65b1ea42cff099c5484c`.
- Video: H.264/yuv420p, 984x584, 24 fps, 150 frames, 6.25 seconds. The independent validator passed all 41 checks with target exit 0, a 1.109-second leading presentation trim, a 0.209-second trailing trim, and a 0.5-second real target final hold.
- Read surface: prompt, `SKILL.md`, the session-plan template, and generated manifests. It did not read script source, acceptance fixtures, sibling skills, repository documentation, or project artifacts.
- Full-resolution review of the evaluator-owned PNGs confirmed that frame one is `REAL INTERACTIVE PYTHON TUI` with an empty `READY>` editor and the final frame contains the three real prompt/response cycles, typed `/exit`, and `REAL TUI EXIT: 3 prompts processed`. Neither frame contains controller output or tmux restoration.

## Repository gates

The following passed after the interactive implementation:

```powershell
uv run --with pyyaml --script C:\Users\villa\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/asciinema-real-command-video
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
git diff --check
uv run --script scripts/sync-local-skills.py
```

`git diff --check` returned success with only existing CRLF-to-LF warnings for `SKILLS.md` and `skills/mermaid/agents/openai.yaml`. Local synchronization changed eight skill files, and SHA-256 comparison confirmed that all eight installed files exactly match the source bundle.

The lifecycle-hardening rerun also passed Python syntax compilation without bytecode output, 20/20 unit tests, skill quick validation, 1,159 canonical pattern-ID checks, repository validation, skill-independence tests, payload validation, and `git diff --check`. Synchronization copied five changed files into `.agents/skills`; a fresh recursive SHA-256 comparison then confirmed eight source files, eight installed files, and zero mismatches.

The target-only presentation correction passed the public Copilot plan validator, 22/22 unit tests, skill quick validation, 1,159 canonical pattern-ID checks, repository validation, skill-independence tests, payload validation, and the strict isolated run. Local synchronization copied six changed skill files; recursive SHA-256 comparison confirmed eight source files, eight installed files, and zero mismatches. Full-resolution boundary and contact-sheet review passed for both the deterministic TUI and the real Copilot replacement video.

## Source alignment

The interactive recipe follows GitHub's documented `copilot` interactive launch and `/exit` command rather than the programmatic `-p` interface. The recording and rendering path follows the official Asciinema CLI, asciicast v3, and agg documentation:

- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>
- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference>
- <https://docs.asciinema.org/manual/cli/quick-start/>
- <https://docs.asciinema.org/manual/asciicast/v3/>
- <https://docs.asciinema.org/manual/agg/usage/>
