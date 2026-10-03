# Interactive TUI Plan Fields

## Contents

- [Interactive TUI mode](#interactive-tui-mode)
- [Explicit TUI actions](#explicit-tui-actions)
- [Sequential multi-TUI mode](#sequential-multi-tui-mode)

Read this only when the recording must show a live product UI. Combine these mode-specific fields with the [shared session plan](session-plan.md). For one-shot pickers and command keys, also use [interaction-recipes.md](interaction-recipes.md); for several applications in one cast, use [multi-tui-sequences.md](multi-tui-sequences.md).

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

