Read the supplied skill's authored-language rules and apply them to a small
support-ticket plugin copy contract. Resolve the wording under that contract;
do not build or render an application. This is a contract smoke test, not a
host-capability comparison.

The legacy display strings below are source fixtures to adapt, not approved
output copy:

```text
Save action: "Guardar"
Loading state: "Cargando..."
Empty queue: "No hay resultados"
Ticket sample: "Revisar el acceso al servidor"
```

The stable ticket identifier `TICKET-7`, diagnostic code `E409`, and protocol
method `ui/initialize` must retain their exact spelling. A failed save needs
a helpful explanation and recovery action while keeping its code secondary.
Do not echo the raw legacy fixture in the generated artifacts.

Create exactly `audit/language-contract.md` and
`audit/language-contract.json`. The Markdown must explain the selected
authored language and include an `authored_ui_copy` table. Supply concrete
copy for every category below, covering both component labels and displayed
content rather than just naming the categories:

- title/navigation;
- button;
- input label and placeholder;
- pending/success status;
- error and validation message;
- empty state;
- contextual help;
- accessibility label and live announcement;
- tooltip;
- notification;
- chart title/category/axis label;
- sample ticket content;
- host-native terminal confirmation prompt; and
- plain text fallback result.

Use `TICKET-7` in the sample ticket and fallback, keep `E409` available beside
the human error explanation, and mention `ui/initialize` only in a clearly
identified technical note. Explain what the authored-language contract can
control when a host's existing chrome or terminal locale differs. Do not
claim a locale was changed or that host-owned controls were restyled.

JSON must contain `language` (the full language name), `authored_ui_copy`
(an array with one record per category, including `category` and concrete
`copy`), `host_locale_scope`, `untranslated_identifiers`,
`host_acceptance_verified`, and `task_empirical_tests_performed`.
`untranslated_identifiers` must preserve the three stable values above and
explain why they retain their spelling. Both task-level booleans must be
false: no running plugin, host session, or empirical UI test is supplied.

Use only the copied skill and this prompt. Do not use network, call a
provider, install software, operate external applications/accounts, change
configuration or locale, build/render a prototype, or modify the read-only
`skills/desktop-plugin-ui/` bundle. Write generated files outside it. After
both final artifacts exist, run the bundled report checker on both files,
inspect its `passed` field, and repair any findings before finishing.
