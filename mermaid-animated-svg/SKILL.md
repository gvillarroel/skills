---
name: mermaid-animated-svg
description: Generate high-quality animated SVGs from Mermaid diagrams while preserving Mermaid-rendered layout, colors, theme variables, custom CSS, and CLI options. Use when Codex needs to render a Mermaid diagram to a static SVG, post-process it into an animated SVG, tune timing or animation style, inspect detected animation elements, control reveal order with element IDs, classes, labels, or an order file, or design Mermaid-comment animation directives.
---

# Mermaid Animated SVG

## Core Workflow

1. Render the Mermaid source to a static SVG first. Preserve the same Mermaid CLI config, theme, CSS, background, and raw arguments for static and animated output.
2. Animate the rendered SVG with `scripts/animate_mermaid_svg.py`. Do not recreate Mermaid geometry by hand.
3. Use `--list-elements` when selectors, order, anchors, or generated classes are not obvious.
4. Keep the static SVG beside the animated SVG for verification and regression checks.
5. Verify that the final animated frame matches the static Mermaid rendering: layout, text, markers, colors, and edge styles should settle correctly.

## Progressive Disclosure Map

Read only the file needed for the task:

- `references/animation-directives.md`: read when the source contains `%% @animate`, when designing Mermaid-comment animation syntax, or when using targets, groups, points, marks, movement, color, pulse, hide, or orchestration directives.
- `references/diagram-directive-notes.md`: read when choosing selectors or choreography for a specific Mermaid diagram type.
- `references/cli-animation-controls.md`: read when tuning `--animation`, timing, dwell, branch duration, order tokens, or diagram-specific auto behavior.

## Common Commands

Render and animate in one step:

```powershell
uv run --script mermaid-animated-svg/scripts/animate_mermaid_svg.py diagram.mmd -o diagram.animated.svg --static-output diagram.static.svg --duration-ms 650 --stagger-ms 120
```

Render a Mermaid source that contains `%% @animate` comments:

```powershell
uv run --script mermaid-animated-svg/scripts/animate_mermaid_svg.py examples/mermaid-animation-directives/flowchart-token-routing.mmd -o output/mermaid-animation-directives/flowchart-token-routing.animated.svg --static-output output/mermaid-animation-directives/flowchart-token-routing.static.svg
```

Use a pre-rendered Mermaid SVG:

```powershell
uv run --script mermaid-animated-svg/scripts/animate_mermaid_svg.py --svg-input diagram.static.svg -o diagram.animated.svg --animation organic
```

Inspect detected elements before ordering or directive work:

```powershell
uv run --script mermaid-animated-svg/scripts/animate_mermaid_svg.py diagram.mmd --list-elements
```

## Selector Discipline

- Prefer IDs, labels, generated classes, and role tokens from `--list-elements` over guessed DOM order.
- Use `--order`, `--order-file`, and `--strict-order` when the reveal order must be exact.
- Prefer overlay marks for moving tokens, cursors, highlights, and callouts so Mermaid layout stays unchanged.
- Treat generated Mermaid SVG as the source of truth. Source notation can normalize into different relationship IDs or selector classes.

## Visual Tokens

Read `../ANIMATED_VISUAL_TOKENS.md` before creating or updating examples, galleries, custom Mermaid themes, overlay marks, or replay controls. Preserve Mermaid-rendered geometry, but use Open Sans, Material Symbols Rounded system icons, and the documented brand palette for editable theme variables, page chrome, controls, overlays, highlights, and generated gallery UI.

## Validation

After changing the skill, scripts, examples, or generated outputs, run the relevant render command and then:

```powershell
uv run --script scripts/validate-skills.py
```
