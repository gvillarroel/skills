---
name: mermaid
description: Create, select, style, render, validate, and animate Mermaid diagrams from prose or structured data. Use when Codex must honor or infer a Mermaid family; preserve workflows, schedules, schemas, hierarchies, interactions, or quantitative facts; apply standard colorset1 or explicitly requested extended colorset2; restyle Mermaid files or Markdown fences; render static SVG; or produce faithful animated SVG.
---

# Mermaid

## Rules

- Create every requested artifact at its exact path outside this skill.
- Honor a truthful explicit family; otherwise select by the relationship the viewer must understand.
- Default to `colorset1`. Use `colorset2` only for explicit extended, expanded, full-color, or multicolor styling. Ordinary "colored" and explicit rejection of extended styling mean `colorset1`.
- Preserve labels and every supplied unit, direction, order, cardinality, date, duration, weight, value, coordinate, and attribute type. Never invent or silently aggregate facts.
- Use YAML frontmatter with `config.theme: "base"`; never generate a JSON init directive.
- When metadata is requested, copy the canonical family `id` from `references/diagram-types.json`; keep it distinct from the rendered declaration (`xyChart` versus `xychart`).

## Read selectively

- Read `references/diagram-selection.md` to infer a family or judge orientation, fidelity, data syntax, or semantic color roles.
- Read `references/diagram-types.json` only for exact declarations, aliases, canonical IDs, or `classDef` support.
- Read `references/palette-capacity.md` for maximum colors, boundary cycles, or dense peer branches, sections, curves, groups, sets, slices, columns, or series.
- Read `references/animation.md` only for animation, custom choreography, or directive selectors.
- Execute scripts without reading them unless debugging. For source-only evaluator tasks, skip animation material and local rendering.

## Workflow

1. Extract exact outputs, family and palette language, facts, and ordering constraints.
2. Select the family when needed and write one concise Mermaid message. Split overload only when the output contract permits it; create requested routing metadata before styling.
3. For indexed density, distinguish reachable palette capacity from unlimited node count. Reach the final requested slot, add a cycle-boundary element only when requested, and keep unlimited families role-based.
4. Style the source directory. Omit `--colorset` for standard; pass `--colorset colorset2` only for explicit extended styling.
5. Run the styler with `--check`; require the expected declaration and colorset plus `missingStyleCount: 0`.
6. Unless rendering is out of scope, render static SVG with `--animation none` or animated SVG with `--animation auto`.
7. Inspect rendered geometry for palette use, label clearance, density, direction, exact facts, and Mermaid error markers; revise and rerender on any failure.

## Commands

```powershell
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --write --report mermaid-style.json
uv run --script skills/mermaid/scripts/style_mermaid_directory.py diagrams --check --report mermaid-check.json
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.svg --static-output diagram.static.svg --animation none
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.animated.svg --static-output diagram.static.svg --animation auto
```

Append `--colorset colorset2` only for explicit extended color. Before custom animation ordering or selectors, render with `--list-elements`.

## Acceptance gate

- All exact outputs exist, are non-empty, use the requested palette and YAML frontmatter, and contain no generated JSON init directive.
- Family selection, declaration, canonical metadata ID, colorset, labels, facts, order, and relations are exact.
- Styler validation reports no missing styles.
- Dense indexed diagrams reach the intended terminal slot without premature cycling; any requested boundary exhibits the documented cycle.
- Rendered SVG is legible, error-free, and visibly palette-influenced.
- Animated SVG settles to the static geometry, labels, markers, and colors.
