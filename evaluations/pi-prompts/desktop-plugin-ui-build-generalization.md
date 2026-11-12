A team wants a small plugin to review an import before committing it. The
input is three synthetic rows: `I-11` valid, `I-12` invalid with a missing
name, and `I-13` valid. Users need to inspect errors, correct a draft, cancel,
and commit only the valid reviewed rows. A model explanation is optional and
must happen only when the user explicitly requests it. No palette is selected.

Prepare a concrete implementation blueprint for Claude Desktop ordinary Chat,
Claude Desktop Code tab, Claude Code CLI, ChatGPT Desktop, Codex desktop and
CLI, and Pi extension. Deliver `blueprint/implementation.md` and
`blueprint/contracts.json`; this task is a plan, not a host installation or
application build. Choose the smallest supported mechanism per surface,
identify required files and a local validation path, and explain which logic
can be shared and which packaging, interaction or transport needs an adapter.
Use exact products and surfaces; do not invent one portable manifest or infer
visible native panels from protocol support alone. Keep current capability
claims limited to the dated bundled snapshot because this task is offline.

Compare the proposed small route with one plausible more complex alternative.
Count required user decisions, initially visible controls, primary actions,
added runtime processes, and extra model turns for normal operations. Explain
any tradeoff; do not treat fewer clicks as proof of better quality. Describe
authoritative data, local drafts, loading/empty/invalid/success/error/cancel
states, draft preservation, and a concrete acceptance sequence. Apply all
H1-H10, and identify authored styling versus host-owned controls, the default
palette, and keyboard and narrow-layout checks where relevant.

JSON must include `hosts` (product, surface, mechanism, required_files,
shared_logic, adapter_logic, conditions, fallback, and validation),
`interaction_contract`, `complexity_comparison`, `heuristics` (H1-H10 with
interaction, finding, evidence, and planned_validation), `sources`,
`host_acceptance_verified`, and `user_testing_performed`. Keep the last two
flags false. Distinguish documentation/source declarations from executed
observations and unperformed checks; cite exact primary URLs from the bundle.

Read only this prompt and the read-only `skills/desktop-plugin-ui/` bundle.
No network, extra providers, installed package source inspection, global
configuration, account operations, installation, or deployment. Keep every
generated file inside this workspace and outside the copied skill.
