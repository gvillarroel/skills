---
name: mermaid
description: Create, select, style, render, validate, and animate Mermaid diagrams. Use when Codex must turn prose, relationships, workflows, schedules, schemas, hierarchies, interactions, or tabular data into an appropriate Mermaid diagram; honor an explicitly requested Mermaid type; choose the best diagram family when none is specified; apply colorset1 as the standard palette or colorset2 when extended/full-color styling is explicitly requested; restyle Mermaid files or Markdown fences; render static SVG; or produce faithful animated SVG.
---

# Mermaid

## Non-negotiables

- Create every requested output at its exact path and keep outputs outside this skill.
- Honor an explicit Mermaid family when it represents the facts truthfully. Otherwise choose by the relationship the viewer must understand.
- Default to `colorset1`. Use `colorset2` only for an explicit request for extended, expanded, full-color, or multicolor styling; ordinary "colored" and an explicit negation of extended styling both mean `colorset1`.
- Preserve labels verbatim and preserve all supplied units, direction, order, cardinality, dates, weights, values, and attribute types. Never invent or silently aggregate data.
- Use Mermaid YAML frontmatter with `config.theme: "base"`; do not generate JSON init directives.
- When routing metadata is requested, copy the canonical family `id` from `references/diagram-types.json` exactly.

## Load only what the task needs

- Read `references/diagram-selection.md` when no family is specified, when authoring from data, or when orientation, fidelity, or semantic color roles need judgment.
- Read `references/diagram-types.json` only for an exact declaration, alias, canonical family ID, or `classDef` capability.
- Read `references/animation.md` only for animated output, custom choreography, or directive selectors.
- Execute scripts without reading their implementation. Inspect script source only to debug a failed command.
- For a source-only task that delegates rendering to an evaluator, do not read animation material or render locally.

## Procedure

1. Extract exact outputs, requested family, facts, ordering constraints, and palette language.
2. Select the family when needed, then write one concise Mermaid message. Create requested routing metadata before styling and keep the canonical family ID distinct from its declaration (`xyChart` versus `xychart`). Split overload only when the output contract permits it.
3. Apply the palette to the source directory. Omit `--colorset` for standard; pass `--colorset colorset2` only for explicit extended styling.
4. Run the styler with `--check` and require the expected declaration, colorset, and `missingStyleCount: 0`.
5. Unless rendering is explicitly out of scope, render SVG with `--animation none` for static output or `--animation auto` for animation.
6. Inspect rendered geometry—not just configuration—for palette color, label clearance, density, direction, fidelity, and Mermaid error markers. Revise and rerender if any check fails.

## Commands

```powershell
# Standard styling; append --colorset colorset2 only for explicit extended color.
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --write --report mermaid-style.json
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --check --report mermaid-check.json

# Static or animated SVG.
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.svg --static-output diagram.static.svg --animation none
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.animated.svg --static-output diagram.static.svg --animation auto
```

Before custom animation ordering or selectors, run the renderer with `--list-elements`.

## Acceptance gate

- Every exact output exists and is non-empty.
- The selected family represents the intended relationship and any explicit family was honored.
- Routing metadata uses the canonical family ID, exact rendered declaration, and requested colorset.
- The source uses the requested palette, YAML frontmatter, and no generated JSON init directive.
- Styler validation passes with no missing styles.
- Required labels and facts remain literal, complete, and correctly ordered.
- Rendered SVG is legible, error-free, and visibly uses the requested palette.
- Animated SVG settles to the static render's geometry, labels, markers, and colors.
