# Interaction recipes

Read this reference when a TUI exits after a selection, uses command keys
instead of a text prompt, or when a direct command contains shell-like syntax
that must remain fixed while user text stays inert argv data.

## Choose the interaction contract

- Use a legacy `prompt` step only for a persistent editor that accepts typed
  text with Enter and returns to the configured ready screen. Copilot is the
  canonical example.
- Use explicit `actions` when Enter ends the process, a command key such as
  `q` exits the application, or navigation needs named keys. Do not disguise a
  command key as prompt text and do not invent Enter.
- Set `completion` to `ready` when the same process remains available for the
  next step. Set it to `target-exit` only on the final step when the selected
  item or quit key ends the real process.
- For a target-driven exit, set `interaction.shutdown_mode` to `target-exit`
  and omit `interaction.exit_text`. The controller waits for the target's real
  status instead of sending a second exit sequence.

Explicit actions are executed in order and recorded individually:

```json
{
  "id": "select-item",
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

`text` uses `interaction.typing_interval_seconds` and must be visible in the
real pane before the next key. `pause` is an on-camera dwell, not synthetic
output. `key` accepts one printable character, Enter, Escape, Tab, BSpace,
Space, arrows, Home, End, PageUp, PageDown, or `C-a` through `C-z`.

## One-shot fzf picker

Create the choices before recording. Let fzf load the file through its own
fixed start binding; do not pipe unreviewed text through a shell wrapper.

```json
{
  "target": {
    "name": "fzf",
    "executable": "fzf.exe",
    "version_args": ["--version"]
  },
  "interaction": {
    "mode": "tui",
    "launch_args": [
      "--prompt=QUERY> ",
      "--bind=start:reload(pwsh.exe -NoLogo -NoProfile -NonInteractive -Command \"Get-Content -LiteralPath fixture/fzf-items.txt\")"
    ],
    "typing_interval_seconds": 0.08,
    "pre_submit_pause_seconds": 0.5,
    "startup_timeout_seconds": 30,
    "ready_pattern": "(?m)(?:^QUERY>\\s*$|^gamma\\s*$)",
    "busy_pattern": "(?!)",
    "settle_seconds": 0.5,
    "shutdown_mode": "target-exit",
    "exit_timeout_seconds": 30,
    "expected_exit_codes": [0]
  }
}
```

The `pwsh.exe` source command is the Windows/WSL-interoperable form for
`fzf.exe`; a native Unix `fzf` plan may use `cat fixture/fzf-items.txt`
instead. Validate the exact source command outside the recording before
claiming the plan. Use `text`, an optional pause, and one Enter action with
`completion: "target-exit"`. The final output and status come from fzf itself.

## Television one-shot picker

For Television 0.14.x, use the real `tv` executable and an ad-hoc channel. A
known working launch shape for a three-line fixture is:

```json
{
  "launch_args": [
    "--source-command", "pwsh.exe -NoLogo -NoProfile -NonInteractive -Command \"Get-Content -LiteralPath fixture/tv-items.txt\"",
    "--source-output", "{}",
    "--no-preview",
    "--no-remote",
    "--no-help-panel",
    "--input-prompt", "FILTER> "
  ],
  "ready_pattern": "(?m)(?:FILTER>|beta\\.txt)",
  "busy_pattern": "(?!)",
  "shutdown_mode": "target-exit"
}
```

This is the Windows/WSL-interoperable source form; native Unix Television may
use `cat fixture/tv-items.txt`. Keep the complete launch arguments in
`interaction`; never replace Television
with a custom input loop. Type the filter as a `text` action and select with an
Enter action. Selection is the exit request.

## lazygit command-key exit

Point `working_directory` at the prepared repository. Before recording, create
the isolated config directory, set `disableStartupPopups: true` in its
`config.yml`, and run `lazygit --use-config-dir <dir>` outside the recording if
any other first-run dialog still needs acknowledgement. Then launch lazygit
with that same project-local config directory:

```json
{
  "launch_args": ["--use-config-dir", ".git/lazygit-config"],
  "ready_pattern": "(?s)Files - Worktrees - Submodule.*(?:Local branches|Commits \\(main\\))",
  "busy_pattern": "(?!)",
  "shutdown_mode": "target-exit"
}
```

The final step should dwell on the authentic interface and send only `q`:

```json
{
  "id": "quit",
  "actions": [
    {"type": "pause", "seconds": 2.0},
    {"type": "key", "key": "q"}
  ],
  "completion": "target-exit",
  "timeout_seconds": 30,
  "pause_after_seconds": 0.0
}
```

Because lazygit normally clears its alternate screen when `q` exits, use this
render contract for the user-facing derivative:

```json
{
  "start_at": "tui-ready",
  "end_at": "before-final-key",
  "last_frame_duration": 2.0
}
```

The full cast and runtime evidence still contain and verify the real `q`, the
target-driven exit, and its status. The MP4 intentionally ends at the hidden
pre-key marker and holds the last authentic lazygit frame instead of showing a
cleared or restored terminal.

Do not add a dummy text prompt, a numeric panel-selection key, or Enter merely
to dismiss first-run UI or fit a prompt-oriented controller. Treat an
unexpected modal as a failed preserved attempt, prepare a new reviewed session
outside the recording, and use a new plan path.

## Fixed PowerShell pipeline with inert input

Use direct-argv mode. Keep the pipeline source fixed in the plan and pass the
reviewed label as the single argument following `-CommandWithArgs`:

```json
{
  "prompt": "reviewed-label",
  "args": [
    "-NoLogo",
    "-NoProfile",
    "-NonInteractive",
    "-CommandWithArgs",
    "@('alpha', 'bravo', 'beta') | Where-Object { $_ -match 'b' } | Sort-Object | ForEach-Object { $_.ToUpperInvariant() }; 'LABEL=' + $args[0]",
    "{prompt}"
  ]
}
```

Do not interpolate `{prompt}` into the PowerShell program. Validate the plan
and run preflight before claiming the one allowed recording attempt.
