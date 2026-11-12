# Agent micro decisions

Use a temporary UI around one concrete question the agent needs a person to
resolve. The agent supplies the relevant context, presents comparable options,
accepts a selected answer or deferral, and continues the task with a typed result.
Every visible element must influence that choice, justify it, expose uncertainty
or prevent an error. Remove unrelated navigation, counters and permanent panels.

The corrected [taxonomy example](../projects/plugin-ui-micro-decisions/) asks
where **Ontology alignment** should sit: beside Concept definition under
Knowledge modeling, or beside Schema mapping under Data integration. It shows
the operative definition, two local trees, one reason for each placement and
optional scope evidence. The parent heading also labels the tree root. One
answer completes the interaction. Deferral chooses no parent.

The earlier [complex workbenches](plugin-ui-complex-workbenches.md) remain a
renderer/data/transaction stress fixture. Their global directory, view tabs and
permanent summaries are inappropriate as the default for a single agent
decision. A full workbench is appropriate for an explicitly requested continuous
application. Complex underlying data can still support a focused micro UI.

## Implementation and verification

Run from `projects/plugin-ui-micro-decisions/`:

```powershell
npm ci
npm run build
npm run serve
node scripts/verify.mjs --label review-1
npm ci --prefix host-tests
node host-tests/capture.mjs --host pi --label review-1
```

The standalone preview is `http://127.0.0.1:8876/`. It explicitly records choices
in a local example and resets on reload. The separate portable MCP App is under
`artifacts/packages/taxonomy-choice/`. It records a receipt for one question in
the server process; it does not edit a taxonomy. Reopening restores that receipt.

The Pi source is `pi/taxonomy-choice.ts`. Use `/taxonomy-choice` for the native
choice, arrows to select, Enter to return the placement, E for the relevant
evidence and Escape to defer. Its command puts a typed result into model-visible
history without starting a model turn. RPC uses a native selector; print/JSON
accept explicit option IDs. The default native theme supplies accent for the
active option, warning for the unresolved concept, success for an acknowledged
selected answer and muted/dim for context. Text, circle/check markers, weight,
spacing and tree connectors also convey meaning.

Final local acceptance includes 25 browser/model/MCP/SDK checks at 780, 542, 390
and 320 CSS pixels, 8 installed Pi 1.4.0 TUI checks at 80x32 and 60x16, and 10
installed Codex 0.167.0-alpha.3.2 package/app-server checks. Real integrated-browser
screenshots verify the corrected 542px comparison, selected and recorded states.
Screenshots and raw host exchanges stay in ignored project artifacts.

## Completion is a host contract

The result contains the decision ID, question revision, selected option ID or
explicit deferral, and a request/receipt ID. The UI validates the offered IDs and
revision and rejects a different second answer. Recording this result is
separate from applying a taxonomy edit and from continuing an agent turn.

For an MCP App, the example waits for server-tool capability and actual state,
records through the real server, optionally updates future model context, then
sends at most one user-initiated continuation when the host advertises text
messages. A context update alone does not start a response. Missing capabilities
produce a direct chat fallback. The SDK fixture acknowledges that continuation;
it is not a claim that a stock host executed a live model turn.

Native awaited UI must resolve its completion callback with the choice. A2UI
hosts need their supported catalog components and A2A action contract. Do not
substitute arbitrary HTML for a native/catalog renderer or treat a browser demo
as signed-in host acceptance. Remaining Claude/ChatGPT/Gemini host gates are
recorded separately in the [micro-decision evaluation](../evaluations/desktop-plugin-ui/micro-decisions-20261112.md).

## Focused craft refinement

The [Impeccable source review](plugin-ui-impeccable-review.md) adds a design-first
quality pass without expanding the decision. Subject nodes now use neutral ink
and outline, the action names the chosen parent, and browser-relative reading
roles preserve user text scaling. An equivalent text tree replaces diagram
labels when they no longer fit. The additional 14-check quality audit remains
separate from the functional and actual-host evidence above.

## Reusable skill guidance

The comparison router and all six host bundles link their own compact
`references/micro-decisions.md` directly from `SKILL.md`. Each copy contains the
decision relevance gate, taxonomic comparison recipe, typed return lifecycle,
semantic terminal roles and host-specific fallback. Pi also includes the tested
formatted choice under `assets/templates/pi-command/micro-choice.ts`. No sibling
bundle or project source is required to use that guidance.
