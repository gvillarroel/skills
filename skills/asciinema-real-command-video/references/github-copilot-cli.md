# GitHub Copilot CLI recipe

Use interactive mode when the requested video must show the GitHub Copilot CLI TUI, prompt typing, Enter submission, Copilot's live `Working` state, and the real response. The controller launches `copilot` once inside a real tmux PTY; it does not use `copilot -p`, reconstruct output, or imitate the UI.

## Preflight outside the recording

1. Resolve `copilot` and run `copilot --version`.
2. Complete `copilot login` and any working-directory trust confirmation outside the recording.
3. Decide whether the prompts may read files, run commands, change files, or perform remote actions. Preserve the user's authorization boundary.
4. Disable auto-update and remote session export for a stable local capture unless the user explicitly requests those features.

## Persistent interactive TUI

Use this interaction object with current Copilot CLI releases:

```json
{
  "mode": "tui",
  "launch_args": [
    "--no-auto-update",
    "--no-remote",
    "--no-remote-export",
    "--no-mouse",
    "--no-custom-instructions",
    "--no-experimental"
  ],
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
```

Running `copilot` without `-p` opens the authentic interactive interface. The empty editor line begins with `❯`; while a response is still active, the footer includes `Working` and `esc interrupt`. Require both signals: an empty prompt alone is not sufficient because Copilot can accept queued input while it is busy. The separate `Loading` resource indicator may remain after a response and must not be treated as response work.

The controller types every prompt character into the TUI, pauses with the complete text visible, sends `Enter`, waits until `Working ... esc interrupt` disappears and the empty editor is stable, then types the next prompt. After the last response, the `exit-text` shutdown types `/exit`, presses Enter, and records Copilot's own session summary and process status. All prompts therefore share one real Copilot process and conversational context. Do not convert Copilot prompts to explicit actions unless the user requested a nonstandard editor-key sequence.

Do not add `--yolo`, `--allow-all`, or broad tool permissions. If a prompt needs tools, add only explicit permission flags authorized for this recording. Keep `--no-custom-instructions` when the video must demonstrate only the reviewed prompts rather than ambient repository instructions. A real Copilot run can consume the signed-in account's usage allowance. Disclose this and never delete the attempt ledger or rerecord the requested deliverable under the same or an alternate plan/output name to improve an already captured result.

## Non-interactive alternative

Use direct-argv mode only when the user explicitly asks for a programmatic command recording rather than the TUI. Copilot's `-p` / `--prompt` mode executes one real prompt and exits. Reuse an explicit `--session-id {run_id}` across steps when programmatic context is required; never select a global latest session.

## Windows host with WSL2 capture

The bundled entrypoint automatically runs the recorder inside WSL2. If Copilot is installed only on Windows, set the plan target executable to `copilot.exe`; WSL normally imports its Windows path. Confirm the real binary before recording:

```bash
command -v copilot.exe
copilot.exe --version
```

WSL can execute the authentic Windows binary inside Asciinema's PTY. Keep the plan, working directory, cast, and outputs on a path visible to both WSL and Windows when Windows `ffmpeg.exe` / `ffprobe.exe` are used.

## Evidence to inspect

- The recorded version block says `GitHub Copilot CLI`.
- The TUI itself visibly shows every exact prompt before and after submission.
- The footer visibly changes to `Working ... esc interrupt`, then back to a non-busy ready editor before the next prompt.
- The manifest records one resolved Copilot executable, one tmux-backed target process, prompt hashes, timed keystroke counts, Enter submissions, screen hashes, and final exit status.
- The cast contains zero Asciinema input events even though the inner PTY visibly receives keystrokes.
- The visible responses are substantive and later prompts remain in the same TUI history.
- The final frame shows Copilot's own exit/session summary.

Official references:

- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference>
- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>
