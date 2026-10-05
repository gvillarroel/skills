---
name: diagram-composition
description: "Decomposes a complex idea into related subdiagrams, chooses suitable visual forms, and composes a compact page with explicit grid spans, consistent semantic colors, readable text, shared SVG icons, and meaningful cross-panel connections. Use for dense explanatory figures, architecture plates, visual comparisons, and multi-panel diagrams that need semantic planning before layout; coordinate available diagram and icon skills without requiring them."
---

# Diagram Composition

Read [palette-policy.md](references/palette-policy.md) before authoring or composing visuals. Apply one exact colorset to authored content and report preserved source media separately.
Read [solid-surfaces.md](references/solid-surfaces.md) for solid-first category fills, black/white text on the actual fill, and palette exhaustion before border variants.

Design the explanation before packing the page. Deliver one coherent figure whose
subdiagrams answer different questions and whose relationships explain the whole.
Default to the smallest readable diagram footprint: compact nodes, panels and
connector routes while preserving visible arrowheads, unambiguous endpoints,
separated lines and every required label. Use the bounded compaction pass in
[layout-and-density.md](references/layout-and-density.md); chart bodies retain
their quantitative reading space.
Keep generated files outside this read-only bundle.

Read [arrow-visibility.md](references/arrow-visibility.md) when producing, importing or reviewing directional arrows. Audit actual shafts/heads at delivery scale.

## Execution contract

Keep every source, draft, report, and screenshot inside the user's workspace;
use its output folder for scratch files too. Do not use a system temp directory.
Choose the shortest reliable production path:

- For hubs, matrices, taxonomies, cycles, and boundary maps, read
  [native-panels.md](references/native-panels.md) and author a brief for
  `build_panels.py`. Prefer its measured geometry unless a supplied asset,
  specialized notation, or unsupported shape requires a custom renderer.
  Hubs support rectangular/elliptical nodes and an optional named enclosure.
  Use the one-command `render_diagram.py` workflow in that reference for standard
  plan/SVG/report/audit/preview outputs; it rebuilds and verifies the entire figure.
- For custom SVG, author a small generator using the layout's body dimensions.
  Set typography for the final display scale. Change the generator and regenerate;
  avoid hand-editing serialized/prepared SVG. Read
  [connectors-and-surfaces.md](references/connectors-and-surfaces.md).
- Parse/update/serialize JSON; use XML APIs or the generator for SVG. Do not use
  text-match edits on generated JSON/SVG, where repeated fragments and formatting
  changes make replacements unreliable. Keep authored input and generated plan
  separate.

For owned generated outputs, use `--overwrite` from the first command below so
the same command is safe to repeat during revision. Preserve supplied originals.
Read each report's `ok` before continuing; a failed draft may leave an older
figure on disk. Use distinct layout, composition, and audit report paths.

## 1. Divide the idea

State the audience, one-sentence thesis, intended display/print size, and facts to
preserve. Infer sensible dimensions if unspecified. Separate entities, relations,
quantities, chronology, and uncertainty. Give recurring concepts stable IDs.

For each necessary subdiagram, write its viewer question, claim, inputs, and
connection to the thesis. Merge panels that answer the same question. Keep a
cross-panel relationship only when it carries a named dependency, contrast,
shared identity, containment, or synthesis; proximity alone is not a relation.
Use the requested panel count, otherwise let the explanation determine it.

Read [visual-selection.md](references/visual-selection.md) to select each form.
Compare the preferred form with a plausible alternative, including a non-flow
form when considering a flowchart. Use flowcharts for real ordered actions or
decisions, not as a default for all nouns. Do not force variety when the same
form is the clearest choice. Preserve explicit user choices when truthful.

## 2. Allocate space

Read [layout-and-density.md](references/layout-and-density.md). Sketch at least
two plausible arrangements for a complex brief; choose by semantic reading order,
aspect-ratio fit, crossings, and readable density. This can be a small planning
note, not an extra user approval step.

Set grid row/column weights and rectangular spans before rendering. Allocate
wide regions to sequences and comparisons, tall regions to deep hierarchies or
stacks, and near-square regions to radial or adjacency views. Respect the actual
labels and node counts; these are tendencies, not fixed family restrictions.
Reserve title, legend, and connector space. White space is useful separation,
not a failure to fill every pixel. Do not solve overcrowding by shrinking text.

Before building panels, read [shared-colors.md](references/shared-colors.md) and
freeze one semantic palette for the whole composition. Bind recurring colored
concepts to registry IDs and exact colors; carry those bindings into every panel
and specialist handoff. Do not assign fresh colors by panel, renderer, row order,
or orientation. Keep neutral surfaces/text and relationship styling aligned too.

Record the chosen plan using [composition-contract.md](references/composition-contract.md)
and the compact [template](assets/templates/composition.json). Run:

```text
uv run --script <skill-root>/scripts/compose_diagram.py layout --spec composition.json --output layout.json --overwrite
```

The layout report supplies each panel's exact body rectangle. Author to those
dimensions; use it to set companion renderer dimensions before generating assets.
It may report deferred port coordinates before source panels exist. The final
compose step requires every endpoint to resolve.

## 3. Build subdiagrams and icons

Read [specialist-handoffs.md](references/specialist-handoffs.md) when coordinating
other skills or importing their SVG. Select only available specialists relevant
to the chosen forms. Give each the exact question, facts, source/output paths,
body size, typography, shared identities, and connection ports. Invoke skills
sequentially unless the task separately authorizes parallel agents.

Use technical-logo-assets for exact brands/products and iconify-icon-search for
generic pictograms when available. Export chosen SVGs into the deliverable with
their provenance/license files. Distinguish GitHub Copilot from Microsoft Copilot,
and a generic cloud from a product name. Never guess a brand from a similar word.
If a diagram companion is absent, read [native-panels.md](references/native-panels.md)
and use `scripts/build_panels.py` for supported hubs, matrices, taxonomies, cycles,
and boundary maps. Describe their data instead of manually placing every label,
icon, and arrow. The builder creates exact-size sources and semantic ports;
compose its generated plan. Use custom native SVG only for unsupported forms.
For missing brand artwork, use a short honest label. No sibling
bundle, repository file, network, or renderer is required for this fallback.

Replace repeated names with recognizable icons where the audience can identify
them. Explain unfamiliar symbols once in a shared legend; keep visible qualifiers
for ambiguous products, units, state, negation, and relationship verbs. Give every
icon-only entity an accessible name. Preserve brand geometry and aspect ratio.
Use one visual grammar across panels: label scale, stroke weight, arrow meanings,
and icon optical size. Native objects use `concept` bindings; imported SVGs tag
their semantic accent marks as described in the shared-color contract. Keep
brand artwork intact and put semantic colors on an adjacent swatch or enclosure.
Use one shared key when colors need explanation. Harmonize source settings
without changing quantitative encodings, units, or data.

## 4. Assemble

Use a static vector SVG per panel with a tight, honest `viewBox`; exclude HTML
labels, external resources, scripts, and animation. Inline icons in that SVG.
For renderer CSS, first use the bundled `prepare` command documented in the
handoff reference; it materializes styles before importing.

```text
uv run --script <skill-root>/scripts/compose_diagram.py compose --spec composition.json --output diagram.svg --report composition-report.json --inspect --overwrite
```

The composer preserves aspect ratio, namespaces IDs and local references, inserts
panels in reading order, and connects ports bound to actual object boundaries.
Read [connectors-and-surfaces.md](references/connectors-and-surfaces.md) for
object annotations, measured imports, outward ports, and routing. Native panels
export these bindings automatically. Use automatic routing first; reserve `via`
for a specific route that still respects object interiors and terminal direction.
Wires stop at node surfaces, while enclosing regions may admit a wire to a child.
An edge must identify the intended object. Use the shared concept key when a
long cross-panel identity edge adds clutter; preserve explicitly requested edges.
Never add an arrow that invents order, causality, magnitude, or equivalence.

For a draft, append `--inspect` to composition and inspect its report's `ok`.
On a route finding, choose an outward side or widen the corridor, then regenerate.
Keep automatic routing unless a reviewed geometry needs explicit waypoints.
Failed drafts save diagnostics without publishing a new SVG; do not audit a stale
figure. Finish with a clean compose command **without `--inspect`**.

For native panel revisions, change the authored brief and rebuild the generated
plan before composing again. For custom SVG revisions, regenerate source and
measure changed geometry before updating the composition plan.

## 5. Review at the delivery size

```text
uv run --script <skill-root>/scripts/audit_diagram.py audit --input diagram.svg --report visual-audit.json --screenshot preview.png --inspect --overwrite
```

Draft `--inspect` reports expected authoring findings with `ok: false` without
failing the command. Repair them and rerun with `--inspect --overwrite`. Once
clean, run the same audit with `--overwrite` and **without `--inspect`** as the
final failing-on-findings gate. Never treat inspection mode as a passing audit.

The audit checks label size/contrast, containment, text collisions, annotated
connector intrusions/crossings/contacts, object geometry, resource requests,
vector portability, and declared semantic color bindings across panels.
It also detects obscured accents and contradictory fills on semantic objects.
Require `semanticColors.status: checked`
when using semantic accents; `not-declared` is not evidence of color consistency.
Repair mismatched, missing, or hidden bindings at source. Inspect its screenshot yourself for claim/form
fit, reading order, icon recognition, crossing ambiguity, contrast, and wasted
space. Inspect every connector at both ends and every colored object's complete
surface, not just its legend swatch. A mechanical pass does not prove semantic
or visual quality. Review any
`clippedMarks` to distinguish intentional renderer clipping (such as
sequence lifelines) from cropped information. For print,
convert physical width to the agreed viewing scale before review. A narrow
screen may need a separate reflowed composition, not a microscopic whole page.

If crowded, shorten redundant prose, share the legend, change orientation/form,
rebalance spans, or move secondary detail into an explicitly identified companion
view. Preserve the requested facts and size; report an unresolved conflict instead
of silently dropping facts. Revise source assets/plan and rerun affected checks.
Keep the specified canvas **and displayWidth** fixed; increasing the display width
to make text pass is not a repair. Check the subject and actor in every headline,
and inspect icon/label separation and source-internal arrowheads in the screenshot.
If Chromium is unavailable, deliver static checks with that validation gap stated.

Deliver the figure and editable plan/source assets, plus a concise explanation of
the visual choices and actual checks. Respect exact requested paths. This skill
handles compact editorial composition; use an available synchronized-canvas skill
when shared live values, semantic zoom, or a navigable world are the main task.
