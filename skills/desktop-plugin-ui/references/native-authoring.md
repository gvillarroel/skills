# Create a native Claude Code plugin

Use this route for an executable Mod in Claude Code or Claude Desktop's Code
tab. Ordinary Desktop Chat uses MCP Apps instead. Tested build: Claude Code
2.1.302, Windows, October 25, 2026. Native engine acceptance is separate from
terminal/Desktop painting, account enablement and keyboard usability.

## Contents

- [Start from the runtime template](#start-from-the-runtime-template)
- [Preserve real event contracts](#preserve-real-event-contracts)
- [Use native constructor and test contracts](#use-native-constructor-and-test-contracts)
- [Validate a copied package](#validate-a-copied-package)

## Start from the runtime template

Copy [claude-native](../assets/templates/claude-native/) into the requested
output directory. It is a dependency-free native Mod, not an acceptance
gallery. Claude loads its TypeScript directly. Do not add a build tool,
`node_modules`, server or model call for this deterministic list interaction.

The template contains metadata, `hooks/hooks.json`, `hooks/register.ts`,
`package.json` and real `claude-code/testing` tests. The neutral task list is
placeholder domain data. Adapt the data, filters, copy and tests to the user
request. Keep the following identities aligned when renaming:

| Location | Meaning |
| --- | --- |
| `.claude-plugin/plugin.json` `name` | Plugin identity used by a native mount's `plugin`. |
| `$.command.register({ name })` | Public command registration. |
| `on("command.run", { command })` | Literal matcher for command execution. |
| `$.command.run({ command, args })` in tests | Authentic execution event. |
| `$.ui.open({ id })`, `requestId` guard and mount | The pane identity. |
| Control keys and test actions | Stable selection and close targets. |

Use one main task and the smallest useful native controls. Preserve direct
text routes, invalid-input recovery and a pane-placement fallback. The
template's read-only list needs no draft/commit form; add one only when the
user task actually writes or commits data. Review H1-H10 against the adapted
states and preserve the host theme/accessibility boundary.

## Preserve real event contracts

Registration's `name` and execution's `command` are different fields. Prefer
the literal matcher below and avoid an additional field guard:

```typescript
on("session.start", async ($, event, next) => {
  await $.command.register({ name: "task-view", description: "Inspect tasks" });
  return next(event);
});
on("command.run", { command: "task-view" }, async ($, event) => {
  return { text: "Requested view: " + event.args };
});
// In a native test:
const answer = await $.command.run({ command: "task-view", args: "open" });
```

Do not branch on `event.name` for `command.run`, and do not make a test pass
by fabricating `{ name: ... }`. A test helper can forward undeclared fields:
the hook and its own tests may agree on a false contract while the real CLI
does not dispatch the command. The observed faulty PoC passed manifest
validation and 13 self-tests but failed seven of nine independent native
checks. Correcting the field restored all behavior and a real headless command
returned the expected rows with zero turns, API milliseconds and inference
cost. [Native creation contract](https://code.claude.com/docs/en/plugins/mods/create),
[test contract](https://code.claude.com/docs/en/plugins/mods/test).

## Use native constructor and test contracts

- Keep hooks and mods API calls statically visible. Use literal `on` event
  names/matchers and named `($, event, next)` arguments. Do not reflect on or
  alias `$`/its namespaces, use rest arguments to discover the hook signature,
  or pass `$` through arbitrary imported/nested helpers. Keep API calls in the
  hook or a supported top-level helper.
- Use `Box({ flexDirection, children })`, `Text({ children })`,
  `Select({ key, options, value, onSelect })` and
  `Button({ key, children, onPress })` as the starter does. Generic DOM/CSS
  props, `direction`, `Text.text` and `Select.onChange` were rejected in the
  observed PoC. Preserve explicit native surface and `requestId` guards.
- `$.ui.open()` resolves to the placement itself, so read
  `placement.isPlaced`, not `placement.value.isPlaced`. A test stub answers
  with `{ value: { isPlaced: true } }`; the wrapper belongs to the stub.
- Import the native test kit from `claude-code/testing`. Every `*.test.ts`
  file needs a `test()` and a real hooks module. Register all `on` stubs before
  the first `$` call. `session.start` is not automatic: stub its floor with
  `{ cwd }` and `command.register` with `{ value: undefined }`, then fire it.
- Let the native test engine implement `ui.invalidate`; a custom no-op stub
  suppresses redraw and can make a correct selector appear stale. Supply
  realistic mount `plugin`, `component`, `requestId`, `surface`, viewport and
  pane props. Host-supplied fields such as `origin` can appear in close events;
  assert necessary fields rather than an invented exact minimal object.

## Validate a copied package

Keep scratch host state, logs and caches inside the task workspace. Use a
fresh task-local `CLAUDE_CONFIG_DIR` for account-free validation. Run from the
workspace, replacing `<plugin-dir>` with the copied/adapted package:

```text
claude --version
claude plugin validate <plugin-dir> --strict --json
claude plugin test <plugin-dir>
```

Check registration and authentic command event input independently, each
filter's values, invalid input, denied/unplaced fallback, supported terminal
and Desktop trees, cancellation, reopen, and unrelated-pane pass-through.
The native test engine needs no sign-in or model request. A static manifest
pass and mutually consistent self-tests alone do not prove a real command.
Where available, an explicit headless native command can verify its receipt:

```text
claude -p "/task-view open" --plugin-dir <plugin-dir> --output-format json --no-session-persistence
```

Only run the known registered direct command; do not send a model prompt to
simulate it. Inspect the actual receipt before claiming zero inference. A
signed-out/account/trust gate is separate from the command's native-engine
logic. Loading/painting in an interactive terminal or Desktop Code remains a
separate check; do not report focus, placement, contrast or accessibility as
passed from engine tests. [Native limits](claude-host-limits.md),
[interaction review](interaction-quality.md).

Preserve slash-command arguments literally when a shell rewrites path-like
arguments. Prefer a native Node/Python argv launcher for automated probes;
for a known Windows CLI under Git Bash, `MSYS_NO_PATHCONV=1` prevents MSYS path
conversion. Verify the registered command before invoking it: a rewritten or
unknown command can be treated as an ordinary prompt. This is an invocation
boundary, separate from the native hook's correctness.
