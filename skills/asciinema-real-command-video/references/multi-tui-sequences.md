# Sequential multi-TUI recordings

Read this reference when one requested video must visibly exercise two or more
real TUI programs. This is one recording transaction, not a montage and not a
set of separately captured clips.

## Freeze the sequence

1. List the tools in the exact visible order and give every session a unique
   lowercase hyphen-case ID.
2. Resolve each real executable and verify its version before claiming the
   recording attempt. Repeating aliases for one resolved binary does not count
   as multiple tools.
3. Give every session its own target, launch arguments, ready/busy gates,
   shutdown mode, allowed exit codes, and ordered steps. Step IDs must be
   unique across the entire sequence.
4. Budget visible time per tool. For a requested video longer than ten
   seconds, place reviewed `pause` actions while each authentic UI is visible;
   do not add a synthetic countdown, title card, or post-render slowdown.
5. Use one top-level terminal and render contract. `tui-ready` begins at the
   first stable target UI. `target-exit` ends at the final target's terminal
   restore. `before-final-key` applies only to the final session.

Start from `assets/templates/multi-tui-session-plan.json`. Create and inspect
all fixed source fixtures before plan validation. A picker source command must
be fixed launch data; do not construct it from typed text.

## Recorded lifecycle

The controller starts one outer Asciinema process and one attached isolated
tmux session. An inner supervisor performs this loop in the same pane:

1. Open the current session's start gate.
2. Launch exactly the reviewed executable and argv.
3. Wait for its real ready-without-busy screen.
4. Deliver reviewed text, key, and pause actions through tmux.
5. Verify step completion and the real process exit status.
6. Emit the session exit boundary, then hand the live recorded PTY to the next
   target.

The supervisor must not start the next executable early, detach and create a
new cast, replay terminal output, or hide a failed session. Intermediate
alternate-screen restores are valid handoffs; only the final restore may end a
`target-exit` presentation.

## Evidence gate

Require all of the following before rendering:

- exactly one run UUID, cast, runtime report, and recording-attempt ledger;
- the declared session order and complete `HANDOFF`, `BEGIN`, `READY`, and
  `EXIT` marker sequence for every session;
- one independent version output, resolved executable path, executable
  SHA-256, launch argv, action evidence, and allowed exit status per target;
- at least two distinct resolved executable-path/hash identities;
- a flattened step ledger that exactly preserves each session's contiguous
  step slice;
- zero Asciinema input events and one successful outer cast exit;
- created-and-released bridge evidence for every session using
  `{windows_working_directory}`.

After encoding, inspect frames from every TUI and every handoff. The first
visible frame must belong to the first target, and the last must belong to the
final target. Confirm that a final-target presentation was not accidentally
trimmed at an earlier application's alternate-screen restore. Report each
tool's version and visible result separately.

## Failure handling

Any startup timeout, unmatched ready gate, incorrect action, unexpected exit,
missing session boundary, duplicate resolved executable, or absent tool UI
fails the single claimed deliverable. Preserve all evidence and stop. Do not
drop the failed tool, substitute another program, splice clips, or create a
renamed retry without a new user request or explicit authorization.
