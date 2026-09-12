# Genealogical cohort composition

Use `design: editorial`, `mode: genealogy`, and `layout: cohorts` when the source supplies people, generations, partnerships, and parentage. The renderer allocates a horizontal unit to each partnership, keeps supporting individuals separate, and relaxes these units around their actual parents and children. It never assigns a dynasty column or invents relatives.

Each person needs an integer `row` starting at zero, a stable `id`, `label`, `group`, and a `width` suited to the name and optional portrait. Supply normal `unions` with two distinct known `partners` and explicit `children`. Single-parent or uncertain relations can use typed `edges`. A parent must precede the child's row. A person in several partnerships requires authored coordinates or explicit, labeled same-person aliases; the cohort packer rejects it rather than quietly duplicating identity.

Optional page controls:

| Field | Purpose |
| --- | --- |
| `cohort_top`, `cohort_bottom` | Centers of the first and last generations; default 225 and page bottom minus 125. |
| `cohort_gap` | Minimum space between family units; default 22, minimum 5. |
| `partner_gap` | Empty space between partners; default 24, minimum 16. |
| `cohort_weights` | Object from row numbers to positive spacing weights before those rows. Reserve extra space for a consequential transition or family label. This is schematic spacing, not elapsed time. |

Start small. A brief with four generations should use a compact page and a short cohort range. A dense 1800 × 2700 poster can carry many more generations, provided measured text and connector gutters fit. If a cohort exceeds the available width, widen the canvas or arrange that region explicitly. Never remove people to pass the check.

Use the `resolved_layout.nodes` coordinates in the render report to inspect or start an authored composition. To refine those positions manually, copy them into the source and change `layout` to `authored`; the ordinary `x`/`y` path then uses them directly. Preserve all identity and relationship fields.

Annotations can follow a named person using `{node,dx,dy,width,label,kind,group}` instead of absolute `x,y`. They resolve after family placement. Check that a moved family pill still names the right branch. It may move within a small search area to avoid labels; it does not search the whole page.

The mechanism is a starting composition, not an aesthetic certification. Inspect the middle and bottom as critically as the founding fan. Persistent parallel spines, synchronized unrelated dates, equal card widths, and periodically placed portraits still look mechanical. Use source-supported generational overlap, terminated lines, substantial sibling groups, and cross-family marriages where present. For complex trees, compose local regions explicitly instead of forcing all history through the cohort grid.

Run `render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json`, then `audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png`. Inspect the actual page and a dense marriage junction at 100%. The source JSON remains unchanged by layout.
