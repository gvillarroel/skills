# Pi version-only runtime preflight repair

Date: October 25, 2026. The parent observed the same irrelevant missing-`tsc`
probe in three otherwise functional Pi generations. A shell chain ending in
`command -v tsc` exited 1, failing strict evaluation even though Pi loads the
extension's TypeScript directly. More prose had not prevented that repeated
preflight habit.

Added [probe_runtime.py](../../skills/desktop-plugin-ui/scripts/probe_runtime.py)
and a compact preflight route in
[pi-extensions.md](../../skills/desktop-plugin-ui/references/pi-extensions.md).
No entrypoint, backlog or unrelated canonical file was edited by this repair.
The parent freezes and tests the next combined subject separately.

## Runtime contract

```powershell
uv run --script skills/desktop-plugin-ui/scripts/probe_runtime.py --host pi
```

The helper is a standalone Python 3.11+ script with uv metadata and no
dependencies. It inventories the executing Python, available Node, and Pi
using only their version flags. Python runs this helper; it is not a Pi
extension runtime dependency. There is no compiler probe, package install,
session, extension, provider, login or configuration operation.

On POSIX, it launches the resolved Pi executable directly. On Windows, native
executables are direct; npm CMD/PowerShell/extensionless shims are read with a
bounded 64-KiB read and resolved to their existing local `pi-coding-agent` CLI.
It launches `[node, cli-entry, "--version"]`, never CMD or PowerShell. Both
current bundled and older CLI package layouts are covered. Missing, unrelated,
ambiguous, malformed, oversized and invalid-encoding shims are not executed.
Every subprocess uses an argv array, `shell=False`, closed stdin and a
10-second timeout; Windows version processes do not open a new window.

Output is JSON with `passed`, three check records, status, version, exact
resolved command and execution exit code. No raw wrapper or arbitrary stderr
is echoed. This does not replace extension loading or runtime acceptance.

| Condition | JSON status | Default exit | With `--fail-on-missing` |
| --- | --- | --- | --- |
| All three runtimes answer recognized versions | available / passed true | 0 | 0 |
| Runtime not found | missing / passed false | 0 diagnostic | 1 |
| Wrapper cannot be resolved safely | unresolved-wrapper / passed false | 0 diagnostic | 1 |
| A launched version command fails or cannot start | execution-failed / passed false | 1 | 1 |
| A launched command times out or returns unexpected output | timeout or unexpected-output / passed false | 1 | 1 |

Thus diagnostic exit 0 for absence is not a success flag, and actual required
execution failures remain visible even without CI mode. The guide tells the
agent to read JSON statuses and use the helper instead of manual PATH/compiler
chains; it does not hide errors behind a successful final command.

## Independent tests and actual local result

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-runtime-probe.py
uv run --script scripts/validate-skills.py --skill skills/desktop-plugin-ui
```

The [evaluator-owned tests](../../projects/desktop-plugin-ui/scripts/test-runtime-probe.py)
pass **17/17**, including:

- Normal POSIX and Windows executable argv, spaces in Node paths, actual-style
  CMD, PowerShell and extensionless npm shims, older package layouts and an
  adjacent Node runtime.
- Missing Pi/Node, missing or unreadable entries, traversal/unrelated/ambiguous
  wrapper references, bounded oversized and invalid-encoding wrappers.
- Default diagnostic and explicit CI exit behavior, nonzero execution,
  timeout/spawn failure and empty/malformed/multiline version output.
- No compiler/package-manager lookup or shell/session/provider arguments.
- A copied standalone helper operating outside the repository source tree,
  exact JSON stdout, empty stderr, unchanged source and no task-directory writes.

Actual standalone inventory passes on this Windows host:

| Runtime | Observed version |
| --- | --- |
| Helper's Python | Python 3.13.12 |
| Node | v24.18.0 |
| Pi | 1.4.0 |

Pi resolves to the installed npm package's local
`@earendil-works/pi-coding-agent/dist/bundle/cli.js` through Node; the wrapper
itself is not executed. Helper SHA-256:
`758c01241ad4b807606103a53f60cc19728c386e51e9996ac109a8bb483fb390`.
Scoped skill validation passes.

Final test artifacts are under
`projects/desktop-plugin-ui/artifacts/runtime-probe-tests/run-20261025T220608568402/`.
The first deterministic development run retained two synthetic-path assertion
failures because the host's Path normalized cross-platform lookup strings;
direct launch argv now preserves the lookup result. Its 15/17 result remains
under `run-20261025T220508779794/`. No failed forward attempt is rewritten.

This is version-preflight evidence only. It does not establish extension
registration, TypeScript correctness, native dialogs, RPC execution, terminal
painting or inference barriers for arbitrary future plugin code. Those remain
the responsibility of the separate frozen forward and runtime PoC checks.
