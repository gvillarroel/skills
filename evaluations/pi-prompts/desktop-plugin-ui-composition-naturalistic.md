We need a plugin experience for reviewing synthetic document exports across
Codex desktop/CLI, Pi TUI/RPC and Claude Desktop Chat/Code. The current proposal
places a 12-row queue, five equal red action buttons, raw event logs, a status
widget and a second chat input in every view. In Pi it would also replace the
footer for branding. Users need to find one export, inspect its outcome and
choose the next action while continuing their conversation.

Give us a better design in `deliverables/review.md` and an executable acceptance
plan in `deliverables/acceptance.json`. The JSON must contain `scenarios` (an
array of objects with `id`, `surface`, `state`, `action`, `expected`, `layer`)
and `limitations` (an array of strings). No implementation is requested.

Explain which surfaces work together, what to remove or retain and why, and
how state, deterministic actions, failure/cancel and expansion behave. Account
for differences between the named hosts. Recommend a fair screenshot comparison
and behavior checks. Say which conclusions would still need actual-host or
user testing. Avoid claiming to have executed this plan or seen screenshots.
Include concise H1-H10 review notes, palette/styling ownership and sources from
the bundle as needed. Keep the plan useful without adding a reporting system.

Use only the supplied skill and ordinary local tools; do not browse, discover
other skills or read host/global configuration. Treat `skills/desktop-plugin-ui/`
as read-only. Write exact outputs outside it. Do not install software, launch
assistant sessions, change settings or call a model through a tool.
