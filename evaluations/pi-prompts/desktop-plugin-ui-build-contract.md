Build a small local Pi extension for a support queue. Create exactly
`plugin/queue.ts`, `review/interaction-review.md`, and `review/checks.json`.

The extension must default-export a Pi extension initializer and register a
`queue-view` slash command. Use synthetic rows `T-104` (pending, high), `T-105`
(pending, normal), and `T-106` (closed, high). With UI available, let the user
choose All tickets, Pending tickets, or High priority through an appropriate
native interaction, then show the matching ticket IDs and their status and
priority. Cancelling must make no change and must not choose the first option.
Without UI, provide a useful caller-visible plain-text result with all three
rows and explain how to request an interactive view. Keep ordinary selection,
filtering, help, and cancellation deterministic: no assistant/model turn,
HTTP request, server, browser, database, persistent file, or added dependency.
All authored copy must be English. Preserve the supplied IDs and data values.

Keep the interface small and usable by keyboard. The review must explain the
user task, chosen host surface, why this is the least complex suitable route,
essential versus optional controls, visible status and recovery, and each of
H1-H10 with concrete findings and evidence. State the palette choice and why
host-owned terminal controls do not imply exact authored palette pixels.
Give a runnable local load command without installing or activating globally.

Run available local checks. `checks.json` must contain `artifacts`, `checks`
(each with name, method, expected, actual, and status), `heuristics` (one entry
for each H1-H10 with id, interaction, finding, status, and evidence),
`complexity` (visible_controls, required_decisions, primary_actions,
runtime_processes_added, and rationale), `host_paint_verified`, and
`user_testing_performed`. Use real results for performed checks and explicitly
mark unperformed target-host painting as untested. Heuristic inspection and a
stub or source check are not a user study or proof of real Pi terminal paint.

This is a closed-book, workspace-only task. Read only this task and the copied
read-only `skills/desktop-plugin-ui/` bundle. Do not discover other skills,
inspect installed package sources, use network, call another provider, install
packages, operate accounts/apps, or change global configuration. Generated
files and local check scratch files must remain in this workspace, outside
the copied skill. The review must identify any checks these limits prevent.
