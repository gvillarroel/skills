I need a tiny Pi extension to browse three release checks while preparing a
deployment. The checks are `R-21` (ready), `R-22` (blocked), and `R-23` (ready).
Give me a `release-checks` slash command that lets me view All checks, Ready,
or Blocked and see matching IDs and states. It should feel native in Pi,
work with a keyboard, let me leave without accidentally selecting anything,
and still return a useful summary when the UI is unavailable. Keep it local
and deterministic, with no assistant completion, network call, extra server,
browser, database, persistent state, or new dependency. All copy is English.

Deliver `extension/releases.ts`, `review/design.md`, and
`review/validation.json`. The TypeScript file must be a loadable Pi extension
with a default initializer. Include the local command to try it without a
global install. Explain why the interaction and architecture are suitably
small, what the primary action is, what happens on cancel, and how the user
recovers from missing UI. Review all H1-H10 against the actual interaction,
including any justified nonapplicable checks. Record the chosen default
palette and distinguish host-owned controls from authored styling.

Run whatever meaningful checks are possible offline. In `validation.json`,
include `checks` with name, method, expected, actual, and status; `heuristics`
with id, interaction, finding, status, and evidence; `complexity` with
visible_controls, required_decisions, primary_actions,
runtime_processes_added, and rationale; `host_paint_verified`; and
`user_testing_performed`. Separate source or stub checks from actual Pi paint
and from representative-user testing. Do not invent a pass for an unrun check.

Use only this prompt and the read-only copied
`skills/desktop-plugin-ui/` bundle. Stay offline, do not inspect installed
package sources or sibling skills, do not operate external applications or
accounts, and do not install or activate anything. Write all generated files
and check scratch files inside this workspace and outside the copied skill.
