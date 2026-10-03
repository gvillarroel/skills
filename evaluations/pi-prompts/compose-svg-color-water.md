Use the loaded `compose-synchronized-svg` skill to make a polished standalone
SVG explaining a municipal water system. This should be suitable for an
operations review: calm, deliberate color, strong visual hierarchy, clear
relationships, and readable exact values. Make the palette easy to adjust
from one documented source of truth when the organization changes its visual
identity. Keep recurring concepts visually consistent.

Treat `skills/compose-synchronized-svg/` as read-only. Use only this prompt,
the skill, and normal local tools. Do not read sibling skills, repository
documentation, acceptance examples, parent directories, or the network.
Generate all task files inside the workspace. Do not modify helper scripts or
hand-patch the generated SVG. Work from the brief and the bundled tools.

Use English labels and synthetic data, with a visible note explaining that
the numbers are illustrative. Use a compact composition with six useful
modules: operating dependencies, daily water allocation, demand against
capacity, leakage share, a comparison of demand and capacity, and an exact
operating ledger. Choose appropriate distinct encodings and meaningful
relationships. This is an interactive scenario comparison; do not add an
autoplay timeline.

Canonical inputs are daily demand, treatment capacity (both in ML/day), and
leakage fraction of processed water. Use these scenarios:

| Scenario | Demand | Capacity | Leakage fraction |
| --- | ---: | ---: | ---: |
| normal | 120 | 150 | 0.15 |
| peak | 180 | 150 | 0.20 |
| repair | 180 | 150 | 0.08 |

Processed water is the lesser of demand and capacity. Leakage equals processed
water times the leakage fraction. Delivered water equals processed water
minus leakage. Unmet demand equals demand minus processed water. Demand load
is demand divided by capacity. Show that demand equals delivered water plus
leakage plus unmet demand in every scenario. A value over 100% is a load ratio,
not a bounded utilization measure. Comparing peak with repair must leave
demand, capacity, processed water, unmet demand, and load ratio unchanged.

Choose credible domains that include zero demand, demand up to 240 ML/day,
capacity from 80 to 220 ML/day, and leakage fractions from 0 to 0.35. Ensure
legal zero values remain visually and numerically truthful.

Create these exact outputs:

- `outputs/water/composition-brief.json`
- `outputs/water/composition-plan.json`
- `outputs/water/composition-report.json`
- `outputs/water/water.svg`
- `outputs/water/static-validation.json`
- `outputs/water/browser-audit.json`
- `outputs/water/overview.png`
- `outputs/water/color-editing.md`

Use the normal preflight, compiler, composer, static validator, and compact
browser audit. Both validation reports must have `ok: true`. Inspect the
overview. In color-editing.md explain the supported way to change colors,
which file owns them, and how to regenerate and check the result. If the
bundle cannot support a requested color-editing behavior, state the exact
limitation instead of inventing a configuration or editing the skill.

Keep the SVG self-contained, with useful script-free and reduced-motion
states, accessible labeled controls, no clipped essential content, and no
remote dependencies. Report output paths and any remaining quality issue.
