---
name: mermaid
description: Create, select, style, render, validate, and animate Mermaid diagrams from prose or structured data, including verified accessible title and description metadata for newly authored work. Use when Codex must honor or infer an appropriate Mermaid family; preserve workflows, schedules, schemas, hierarchies, interactions, behavioral contracts, tabular data, or quantitative facts; simplify or audience-adapt an existing diagram with an explicit fidelity ledger; apply colorset1 as the standard palette or colorset2 only when extended/full-color styling is explicitly requested; restyle Mermaid files or Markdown fences; render static SVG; or produce faithful animated SVG.
---

# Mermaid

## Rules

- Create every requested output at its exact path and keep outputs outside this skill.
- Honor an explicit Mermaid family when it represents the facts truthfully. Otherwise choose by the relationship the viewer must understand.
- Default to `colorset1`. Use `colorset2` only for an explicit request for extended, expanded, full-color, or multicolor styling; ordinary "colored" and an explicit negation of extended styling both mean `colorset1`.
- Preserve fact-bearing labels, proper nouns, identifiers, validator literals, and every supplied unit, direction, order, cardinality, date, duration, weight, value, coordinate, and attribute type. Rewrite explanatory wording only when audience adaptation is explicitly authorized, and account for each changed label in the fidelity ledger. Never invent or silently aggregate data.
- For newly authored diagrams, include non-empty `accTitle` and `accDescr` directives. Describe the content and conclusion, not the geometry. When editing is out of scope or the source meaning is unclear, report missing accessibility metadata instead of inventing it.
- Use Mermaid YAML frontmatter with `config.theme: "base"`; do not generate JSON init directives.
- When routing metadata is requested, copy the canonical family `id` from `references/diagram-types.json` exactly and keep it distinct from the rendered declaration (`xyChart` versus `xychart`).

## Read selectively

- Read `references/diagram-selection.md` when no family is specified, when authoring from data, or when orientation, fidelity, data syntax, or semantic color roles need judgment.
- Read `references/editorial-diagram-contracts.md` when behavior, state, enforcement, capacity, trust, or residual risk carries the message; when simplifying or audience-adapting an existing diagram; or when rendered edge traceability needs an editorial release gate.
- Read `references/accessible-svg-metadata.md` for newly authored diagrams, authorized accessibility edits, or any `--require-accessibility` release gate.
- Read `references/diagram-types.json` only for an exact declaration, alias, canonical family ID, or `classDef` capability.
- Read `references/palette-capacity.md` when a task asks for maximum distinct colors, a palette boundary, or enough peer branches, sections, curves, groups, sets, slices, columns, or series to approach cycling.
- Read `references/animation.md` only for animated output, custom choreography, or directive selectors.
- Execute scripts without reading their implementation. Inspect script source only to debug a failed command.
- For a source-only task that delegates rendering to an evaluator, do not read animation material or render locally.

## Workflow

1. Extract exact outputs, requested family, facts, ordering constraints, palette language, destination, audience, and whether simplification is authorized.
2. When the message is behavior-heavy, choose one primary semantic contract before choosing a Mermaid family. When adapting a source, set detail and audience independently and prepare the fidelity ledger before drawing.
3. Select the family when needed, then write one concise Mermaid message. Create requested routing metadata before styling and keep the canonical family ID distinct from its declaration (`xyChart` versus `xychart`). Split overload only when the output contract permits it.
4. For indexed-color density, distinguish Mermaid's reachable palette capacity from an unlimited node count. Author through the last requested slot, include a boundary-cycle element only when requested, and keep unlimited families role-based rather than inventing a maximum.
5. Add `accTitle` and `accDescr` to newly authored or authorized-to-edit sources. Apply the palette to the source directory. Omit `--colorset` for standard; pass `--colorset colorset2` only for explicit extended styling.
6. Run the styler with `--check`; add `--require-accessibility` for newly authored or authorized-to-edit diagrams. Require the expected declaration, colorset, `missingStyleCount: 0`, and, when gated, `missingAccessibilityCount: 0`.
7. Unless rendering is explicitly out of scope, render SVG with `--animation none` for static output or `--animation auto` for animation. Add `--require-accessibility` for newly authored or authorized-to-edit diagrams so the renderer verifies the final SVG metadata, not only the source directives.
8. Inspect rendered geometry—not just configuration—for palette color, label clearance, edge traceability, density, direction, fidelity, accessible title/description, and Mermaid error markers. Revise and rerender if any check fails; change source layout or split the figure instead of hand-patching rendered SVG geometry.

## Commands

```powershell
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --write --report mermaid-style.json
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --check --require-accessibility --report mermaid-check.json

# Static or animated SVG.
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.svg --static-output diagram.static.svg --animation none --require-accessibility
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.animated.svg --static-output diagram.static.svg --animation auto --require-accessibility
```

Append `--colorset colorset2` only for explicit extended color. Before custom animation ordering or selectors, render with `--list-elements`.

## Acceptance gate

- Every exact output exists and is non-empty.
- The selected family represents the intended relationship and any explicit family was honored.
- Routing metadata uses the canonical family ID, exact rendered declaration, and requested colorset.
- The source uses the requested palette, YAML frontmatter, and no generated JSON init directive.
- Styler validation passes with no missing styles.
- Required labels, validator literals, and facts remain literal, complete, and correctly ordered; any authorized explanatory-label adaptation is recorded in the fidelity ledger.
- Every newly authored diagram has a useful `accTitle` and content-oriented `accDescr`; rendered SVG resolves both accessible references.
- Behavior-heavy diagrams satisfy one primary semantic contract before family styling; state, capacity, boundary, and outcomes are not encoded by color or motion alone.
- Any authorized simplification has a fidelity ledger that accounts for kept, merged, omitted, and moved-to-detail source content. Audience wording never changes facts or silently changes element count.
- Dense indexed diagrams reach the intended terminal slot without premature cycling; any requested boundary element exhibits the documented cycle.
- Rendered SVG is legible, error-free, and visibly uses the requested palette.
- Animated SVG settles to the static render's geometry, labels, markers, and colors.
