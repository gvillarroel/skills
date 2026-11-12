Use the supplied skill to prepare an English reference for an engineering team
adding plugin UI to ordinary Claude Desktop Chat. They also maintain a separate
Claude Desktop Code-tab extension and keep confusing the two APIs.

Create exactly `results/reference.md` and `results/decisions.json` in this
workspace. Include at least ten applicable canonical bundled pattern IDs with
their concrete rules, input needs, failure alternatives, and a validation action.
Explain which UI methods fit Chat versus Code and what is packaging/configuration.
Include host-owned elicitation forms/URL flows and native render sites in the
surface comparison, with their evidence and compatibility limits.
Distinguish documented support, SDK/browser/native test observations, conditional
features, and actual signed-in host acceptance. Include source links and the
snapshot date. No real host session is available in this task.

The JSON should contain `host`, `surface`, `patterns` (array of objects with
`id`, `rule`, `validation`, and `evidence`), `host_acceptance_verified` (boolean),
and `limits` (array). Use the bundled knowledge snapshot; network access or
external application changes are unnecessary. The copied
`skills/desktop-plugin-ui/` directory is read-only. Write all generated
files outside that directory. Keep the reference useful and specific.
