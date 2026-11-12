We are planning a reusable inventory-review plugin for ChatGPT, Claude Desktop
Chat, Codex desktop and CLI, Pi TUI and RPC, and Claude Code. The initial task
is small: find an item, select it, inspect its stock state and save a reversible
display preference. We already have plain domain functions and a small React
component library. Later, a warehouse map might need persistent spatial editing.

A proposal would use OpenUI to generate every screen and send every button
click as a new model turn. It would also deploy a separate full web app for
each assistant. We want a good interface with low setup, responsive ordinary
actions and manageable maintenance. Assess the proposal and choose a practical
delivery approach for every named surface, including when a preview or owned
client would be justified. No implementation or installation is requested.

Write `deliverables/delivery-plan.md` and `deliverables/decisions.json`. The JSON
must contain `routes` (nonempty objects with `host`, `surface`, `starting_point`,
`shared_actions`, `model_work`, `limits`, `verify`) and `generated_ui` (an object
with `decision`, `reason`, `requirements`). All field values must be nonempty
strings except `shared_actions` and `requirements`, which are nonempty arrays
of nonempty strings. Keep the Markdown useful and concise; avoid duplicating
every JSON field in prose.

Explain what is shared, what belongs to host adapters, and how the existing
components affect the choice. Account for OpenUI's renderer versus its agent
skill/docs connection. Give a concrete workflow, state/cancel/recovery rules,
an acceptance plan and meaningful efficiency measures without inventing a
benchmark. Distinguish documented contracts from proposed integrations and
unperformed host checks. Preserve usable output in noninteractive modes.

Use only the supplied skill and normal local tools; do not browse, discover
other skills or read host/global configuration. The copied
`skills/desktop-plugin-ui/` is read-only. Write the exact outputs outside it.
Do not install software, launch assistants, change settings or call another
model through a tool. Do not claim to have seen screenshots or tested host UI.
