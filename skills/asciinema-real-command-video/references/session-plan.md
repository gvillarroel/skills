# Session plan contract

Use one JSON plan as the reviewed source for target identity, prompt order, interaction behavior, terminal geometry, render settings, and declared side-effect scope. The bundled runner rejects duplicate JSON keys and unknown fields.

## Required top-level fields

- `schema_version`: integer `1`.
- `title`: non-empty recording title.
- `working_directory`: existing directory, resolved relative to the plan file when not absolute.
- `declared_scope`: plain-English statement of authorized behavior. This is evidence, not a sandbox; enforce restrictions with the target's own permission flags.
- `terminal`: terminal geometry object.
- `render`: deterministic render settings.
- Choose exactly one execution shape:
  - `target` plus `steps`, and optional `interaction`, for direct-argv or one TUI.
  - `tui_sessions` for two to eight sequential real TUIs in one recording. Omit top-level `target`, `steps`, and `interaction` in this shape.

## Target

```json
{
  "name": "GitHub Copilot CLI",
  "executable": "copilot",
  "version_args": ["--version"]
}
```

`executable` must resolve in the recording environment or be an absolute executable path. TUI mode launches it once; direct-argv mode launches it once per step. `version_args` are run before the prompts and the real output is recorded.

## Interactive TUI mode

Use this mode when the video must show a real application UI, prompt typing, Enter submission, live work, and responses in one continuous session.

```json
{
  "interaction": {
    "mode": "tui",
    "launch_args": ["--no-auto-update", "--no-remote"],
    "typing_interval_seconds": 0.035,
    "pre_submit_pause_seconds": 0.5,
    "startup_timeout_seconds": 120,
    "ready_pattern": "(?m)^❯\\s*$",
    "busy_pattern": "(?mi)Working.*esc interrupt|esc interrupt",
    "settle_seconds": 1.5,
    "shutdown_mode": "exit-text",
    "exit_text": "/exit",
    "exit_timeout_seconds": 60,
    "expected_exit_codes": [0]
  }
}
```

- `launch_args` starts the real target exactly once. It may contain `{run_id}` but never `{prompt}`. For a native Windows `.exe` that must receive the real WSL working directory as a short Windows path, it may also contain `{windows_working_directory}`. The token expands only while a verified temporary `subst.exe` mapping is active; it includes the trailing slash, so append relative children directly, for example `{windows_working_directory}.git/config`.
- `typing_interval_seconds` is the delay after every Unicode character. Use roughly `0.025` to `0.06` for readable typing.
- `pre_submit_pause_seconds` leaves the complete prompt visible before the controller sends a real `Enter` key.
- `ready_pattern` must match the target's empty input editor. Anchor it narrowly so output text cannot satisfy it accidentally.
- `busy_pattern` must match every target state that still means a response is running. It must identify transient active UI, not a word retained in response history; anchor it to a footer, spinner row, or other region the target clears on completion. A screen is complete only when the ready pattern matches, the busy pattern does not match, and that condition remains stable for `settle_seconds`.
- `startup_timeout_seconds`, each step's `timeout_seconds`, and `exit_timeout_seconds` are independent finite limits.
- `shutdown_mode` defaults to `exit-text`. In that mode, `exit_text` is required,
  typed through the same PTY, and submitted with Enter after the final response.
  Use `target-exit` and omit `exit_text` when the final reviewed action itself
  ends a one-shot picker or command-key TUI.
- The target's final status must be in `expected_exit_codes` for either shutdown mode.
- The controller records a hash and bounded screen snapshot before Enter and after completion for every step. Independent validation requires the exact prompt to appear in the pre-submit snapshot, the right keystroke count, Enter evidence, non-busy readiness, and the final process status.

TUI steps omit both `args` and `expected_exit_codes` because all prompts share one process:

```json
{
  "id": "prompt-1",
  "prompt": "Explain what a Git commit is in two sentences.",
  "timeout_seconds": 600,
  "pause_after_seconds": 1.0
}
```

Keep TUI prompts on one line. If the intended submission itself requires multiline editor shortcuts, treat that as a target-specific extension rather than embedding newline characters in `prompt`.

## Explicit TUI actions

Use an action step when the real interaction is not the persistent
text-plus-Enter cycle. This includes one-shot pickers whose Enter selection
ends the process and command-key TUIs that quit with `q` without Enter.

```json
{
  "id": "select-gamma",
  "actions": [
    {"type": "text", "text": "gamma"},
    {"type": "pause", "seconds": 0.75},
    {"type": "key", "key": "Enter"}
  ],
  "completion": "target-exit",
  "timeout_seconds": 30,
  "pause_after_seconds": 0.0
}
```

- A TUI step contains exactly one of `prompt` or `actions`.
- `text` is sent one Unicode character at a time using the interaction typing
  interval. The exact text must be visible before the next key.
- `key` is sent as one tmux key event. Use the real application key; do not add
  Enter unless the TUI requires it.
- `pause` holds the live target screen for 0.05 to 30 seconds.
- `completion` defaults to `ready`. It waits for ready-without-busy and keeps
  the same process alive. `target-exit` is valid only for the final step with
  `interaction.shutdown_mode: "target-exit"`.
- The runtime report records each action digest, text hash, raw key, timing,
  screen hash, completion mode, and target status. The cast contains matching
  hidden action markers and still contains zero Asciinema input events.

Read [interaction-recipes.md](interaction-recipes.md) for fzf, Television,
lazygit, and fixed PowerShell pipeline plans.

## Sequential multi-TUI mode

Use `tui_sessions` only when one cast and MP4 must visibly exercise more than
one authentic terminal application. Each entry contains its own `id`,
`target`, `interaction`, and `steps` using the same single-TUI contracts above:

```json
{
  "tui_sessions": [
    {
      "id": "search-with-fzf",
      "target": {
        "name": "fzf",
        "executable": "fzf.exe",
        "version_args": ["--version"]
      },
      "interaction": {"mode": "tui", "launch_args": [], "...": "..."},
      "steps": [{"id": "select-alpha", "actions": [], "...": "..."}]
    },
    {
      "id": "search-with-television",
      "target": {
        "name": "Television",
        "executable": "tv.exe",
        "version_args": ["--version"]
      },
      "interaction": {"mode": "tui", "launch_args": [], "...": "..."},
      "steps": [{"id": "select-beta", "actions": [], "...": "..."}]
    }
  ]
}
```

- Declare two to eight sessions and at least two distinct executable strings.
  Runtime validation also requires at least two distinct resolved executable
  identities and hashes.
- Use unique lowercase hyphen-case session IDs and globally unique step IDs.
- The supervisor launches sessions in array order. A session must reach its
  real ready gate, complete every action, and exit with an allowed status
  before the next start gate opens.
- The outer recorder, tmux client, run UUID, cast, runtime report, attempt
  ledger, MP4, and manifest remain singular. Each target has separate version,
  executable hash, launch argv, ready, action, exit, and optional Windows path
  bridge evidence.
- `render.start_at: "tui-ready"` refers to the first target. `render.end_at:
  "before-final-key"` refers only to the final target and requires that final
  session to satisfy the normal target-exit/final-key contract. With
  `end_at: "target-exit"`, the MP4 ends at the final alternate-screen restore,
  not an intermediate handoff.

Read [multi-tui-sequences.md](multi-tui-sequences.md) before recording and
start from `assets/templates/multi-tui-session-plan.json`.

## Direct-argv mode

```json
{
  "id": "prompt-1",
  "prompt": "Explain what a Git commit is in two sentences.",
  "args": ["--session-id", "{run_id}", "-p", "{prompt}"],
  "timeout_seconds": 600,
  "pause_after_seconds": 1.0,
  "expected_exit_codes": [0]
}
```

- Use a unique lowercase hyphen-case `id`.
- Put the exact user-approved text in `prompt`.
- `args` is an argv array, not a command string. It must contain `{prompt}` exactly once. The runner replaces it inside that single argument, so prompt punctuation cannot become shell syntax.
- `{run_id}` is optional and expands to the recording UUID. Reuse it in each step when the target supports explicit session IDs.
- In direct-argv step arguments, only `{prompt}` and `{run_id}` are substituted. Other braces remain literal, so Python f-strings, JSON snippets, and similar argv content are preserved unchanged. `{windows_working_directory}` is reserved for TUI `launch_args`.
- Set a finite `timeout_seconds` for each real process.
- Use `pause_after_seconds` only for watchability; it does not alter target output.
- List every acceptable process status in `expected_exit_codes`. Use `[0]` for normal prompt sessions.

Do not assume any other placeholder is expanded. Do not put secrets in prompts or add an environment-variable map to the plan.

## One-record claim

After preflight passes, `record` atomically creates an immutable hidden ledger
next to the plan, named `.<plan-stem>.recording-attempt.json`. A second record
transaction for that plan fails even if previous output paths were moved or
deleted. Preserve the ledger and failed evidence. The one-attempt contract is
broader than this file guard: a different plan path, output name, or launch
adapter does not authorize another attempt for the same user-requested
deliverable. Stop after a failed `record`. Only a later user request or
explicit authorization may define a genuinely new recording session.

## Terminal and render settings

```json
{
  "terminal": {"cols": 100, "rows": 30},
  "render": {
    "theme": "github-dark",
    "font_size": 18,
    "line_height": 1.4,
    "fps": 30,
    "speed": 1.0,
    "idle_time_limit": null,
    "last_frame_duration": 2.0,
    "start_at": "tui-ready",
    "end_at": "target-exit"
  }
}
```

Use at least 90 columns for agent output. Increase rows before shrinking the font. `agg` renders a one-pass GIF intermediary with these settings; ffmpeg converts it to H.264/yuv420p MP4 at constant frame rate. The cast remains the authoritative timing and text record.

TUI mode requires `speed: 1.0` and `idle_time_limit: null`; this preserves visible typing, thinking, and response time. Direct-argv mode may set a finite idle limit when shortening inactive gaps is part of the reviewed recording design.

Use `start_at: "tui-ready"` for a user-facing TUI video. The cast still retains the complete recorder/controller lead-in and teardown, but the MP4 begins just before the independently detected stable ready-screen update. The derived lead includes the startup settle window and a small render margin, so the empty editor appears before the first typed character. Use `start_at: "recording"`, or omit the field, only when the complete visible recorder transaction is intentionally part of the deliverable. `tui-ready` is invalid for direct-argv mode.

`end_at` defaults to `target-exit`. With `tui-ready`, that presentation ends immediately before tmux restores the controller terminal. For a target-exit action plan whose final key clears the app—such as `q` in lazygit—set `end_at: "before-final-key"` and make the final action a `key`. The runner marks the instant immediately before delivering that real key, trims only the MP4 at that marker, and freezes the preceding authentic TUI frame for the positive `last_frame_duration`. The untrimmed cast and runtime report retain and verify the final key, the target's exit, and its status. `before-final-key` is invalid for direct-argv, prompt steps, non-final keys, and `exit-text` shutdown.

## Context modes

- Interactive shared context: use TUI mode. Every prompt is entered into one persistent target process.
- Programmatic shared context: in direct-argv mode, give every step the same explicit session UUID via `{run_id}` when the target supports it.
- Independent prompts: omit the session argument from every step and state that the prompts are separate in `declared_scope`.
- Do not use a global `--continue` or equivalent when concurrent or unrelated sessions could exist. If the target only supports “latest session,” isolate its config directory and document that limitation.
