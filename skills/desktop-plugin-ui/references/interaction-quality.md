# Task-first interaction quality

Use this loop when building or improving a plugin. It operationalizes the
[Nielsen checks](usability-and-color.md#ten-usability-checks); the selection
and measurement rules below are engineering recommendations, not host APIs
or a promise of measured user satisfaction.

## Define the smallest useful path

Name the user's task, starting context, authoritative result and observable
completion condition. Record the applicable host, surface and mode. Infer
routine choices from the request; ask only when a missing choice materially
changes the result, authority or supported route.

Sketch the shortest complete path: entry, necessary inputs, action, result,
and exit. Keep one clear primary action per decision. Put advanced settings
behind a useful secondary action and derive safe defaults from existing
context. Preserve labels and information needed to recognize the next action.
Do not hide essential errors, recovery or permission meaning to save space.

Prefer, in order when they satisfy the task: an existing command/text result,
a native choice or form, a bounded custom view, and a dedicated application.
This is a selection aid, not a ban on rich UI: a chart, spatial task or live
inspection may justify a view immediately. Reuse host focus, keys, theme,
permission dialogs and accessible semantics instead of recreating them.

For each new control, service or dependency, state the user need it serves and
why the simpler route is insufficient. Remove duplicate controls, setup steps
and intermediate screens that add no necessary decision or feedback. Do not
add a web server, account, OAuth flow, database or background agent for a
local deterministic selection unless the task needs it.

## Define actions and state ownership

For each action specify its input, validation, result/state change, feedback,
cancel/retry behavior and authority. Use a small transition table or code
tests where useful. Cover only states the task actually reaches:

| State or transition | Required behavior |
| --- | --- |
| Entry / empty | Show the task and next action, with a useful empty explanation. |
| Draft / invalid | Preserve useful input; explain the specific correction before committing. |
| Busy | Show real status; prevent duplicate submission; allow supported cancellation. |
| Success | Show the authoritative result and a relevant next action or clear exit. |
| Error / retry | Explain the problem and recovery; retain drafts and avoid duplicate effects. |
| Cancel / back / close | Leave without committing; distinguish cancellation from an empty value. |
| Reopen / reload | Restore or reset intentionally; disclose persisted state when it matters. |

Keep transient view state separate from committed application data and model
context. A visible success message must follow the actual committed result.
Handle stale asynchronous responses and disposal when the design is async;
do not let a late result overwrite newer input or revive a closed view.

Run selection, validation, formatting, filtering, pagination, cancellation and
known local operations directly when deterministic. Mark any action that
needs model reasoning explicitly. Do not send a chat message or trigger a
model turn merely to handle a button or refresh. Verify the count when
claiming zero inference; network requests and inference are separate measures.

## Inspect, exercise, simplify

1. Implement a complete useful path before adding optional features.
2. Inspect H1-H10 against actual states. Record a short finding with the
   affected action, evidence, consequence and fix. Use `not-applicable` with
   a reason for an irrelevant state; use `untested` for a check not performed.
3. Exercise success, invalid input, cancel and relevant error/retry paths.
   Check keyboard-only operation, focus, accessible names and narrow layout
   where the surface permits them. Reopen or reload if state persists.
4. Fix task blockers first, then error-prone paths, then friction. Recheck
   the failed transition and affected successful path after each change.
5. Remove remaining unneeded decisions, visible controls, required fields,
   dependencies or setup. Recheck task completion and recovery after removal.

Record before/after values only where a comparison exists: task steps, user
decisions, initially visible controls, required inputs, setup operations,
services/dependencies and model calls. For a new plugin use a proposed design
baseline and label it as such; never invent a measured former interface.
Keep a justified extra step when it prevents an expensive error or preserves
clarity. Fewer clicks alone does not prove a better experience.

Stop when the requested path and relevant recovery checks pass, blocking
findings are fixed, remaining limitations are explicit, and extra controls or
infrastructure have a task-based reason. If an account or host gate prevents
paint testing, finish all available local checks and leave that layer untested.
Do not loop on unchanged evidence or report every heuristic as passed.

## Keep the evidence useful

For small builds, source, runnable tests and brief review notes can hold this
contract; avoid a second reporting framework. For a requested evidence report,
use the bundle's typed ledger/report workflow. Preserve inspected source,
executed unit/native/protocol checks, browser checks and actual host paint as
different layers. Native stubs prove handler logic, not focus or visual quality.

Describe a concrete improvement and its observed tradeoff. If representative
user tests were not run, call the result a heuristic review and implementation
check. [Nielsen's heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
are broad review principles; they do not certify usability or host support.
