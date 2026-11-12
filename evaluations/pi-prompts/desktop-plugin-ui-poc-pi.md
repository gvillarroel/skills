Create a small loadable Pi extension for reviewing an import before committing
it. Deliver exactly these required files: `poc/extension.ts`,
`poc/package.json`, `poc/test-scenarios.json`, `poc/USAGE.md`, and
`poc/review.json`. Additional small local test scratch files are allowed.

The synthetic starting rows are `{id:"I-11",name:"Atlas"}`,
`{id:"I-12",name:""}`, and `{id:"I-13",name:"Cedar"}`. A valid row has a
nonempty trimmed name. Keep the original input unchanged and maintain a draft,
a monotonically increasing draft revision, a reviewed snapshot and an
in-memory committed result. Nothing persists when Pi exits.

Register one native `/import-review` command, with deterministic argument
routes `status`, `edit <row-id> <name>`, `review`, `commit <revision>`, and
`cancel`. Names may contain spaces. A changed edit invalidates the previous
review. Review captures only currently valid rows and the current draft
revision; show excluded invalid rows clearly. Commit succeeds only for the
exact current reviewed revision, with a nonempty reviewed snapshot. Reject a
missing/stale review or wrong revision without changing committed data.
Repeating the same commit must not duplicate rows. Unknown IDs/arguments,
blank names and an unavailable UI must have useful recovery without losing
the draft. `cancel` clears an uncommitted review but preserves both draft and
committed data.

With no arguments and native UI available, show a small keyboard-native menu
for status, edit, review, commit or cancel, then return after that action.
Use native input for editing and native confirmation before a UI-initiated
commit. Escape/dismissal at the menu, input or confirmation must never edit,
review or commit accidentally. Declining commit preserves the review for
retry. With no UI and no arguments, show current rows/revisions plus the
explicit argument syntax, without invoking a UI method. Explicit argument
routes must work without UI and must never start a model turn.

Every completed action, including a rejection or cancellation, must emit a
caller-visible custom Pi message (`customType: "import-review"`) with English
readable content and a `details` object containing `draftRevision`,
`reviewRevision` (number or null), `draftRows`, `reviewedRows`, and
`committedRows`. This is an observation contract for clients and local tests,
not an instruction to expose implementation diagnostics to users. An Escape
that makes no change may omit a message. Output success only after the actual
in-memory transition succeeds.

Keep this local and minimal: no runtime dependency, server, browser, database,
filesystem writes, network request, subprocess or assistant/model call in the
extension. Pi host packages may be type-only imports. No optional model
explanation is needed. Authored copy and comments must be English. Use the
host-native theme and explain the chosen default palette/styling ownership.

The package must declare this extension for project-local Pi discovery, and
USAGE must include a one-invocation local load command without global
installation. `test-scenarios.json` must enumerate executable command/UI
sequences and expected state invariants, including valid/invalid edits,
missing and stale review rejection, valid commit, repeated commit,
cancellation at every dialog, no-UI output and zero inference. Run meaningful
available local checks. `review.json` must include the exact performed check
commands/results, H1-H10 findings tied to concrete actions, complexity counts
and justified tradeoffs, and `host_paint_verified:false` and
`user_testing_performed:false`. A stub check is not real Pi paint or a user
study. Keep notes concise and preserve any observed failed attempt.

Use only this task, the copied read-only `skills/desktop-plugin-ui/` bundle,
and normal local tools. Stay offline; do not read installed package sources,
other skills or repository context, install dependencies, operate external
apps/accounts, change global configuration or write outside this workspace.
Do not modify the copied skill. Put all generated files and local check
scratch files inside this workspace and outside that copied bundle.
