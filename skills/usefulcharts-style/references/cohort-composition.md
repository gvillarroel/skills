# Genealogical cohort composition

Use `design: editorial`, `mode: genealogy`, and `layout: cohorts` when the source supplies people, generations, partnerships, and parentage. The renderer allocates a horizontal unit to each partnership, keeps supporting individuals separate, and relaxes these units around their actual parents and children. It never assigns a dynasty column or invents relatives.

Each person needs an integer `row` starting at zero, a stable `id`, `label`, `group`, and `detail` for supplied dates. Supply normal `unions` with two distinct known `partners` and explicit `children`. Single-parent or uncertain relations can use typed `edges`. A parent must precede the child's row. A person in several partnerships requires authored coordinates or explicit, labeled same-person aliases; the cohort packer rejects it rather than quietly duplicating identity.

For 30 people or fewer, start from [the family template](../assets/templates/cohorts.json) without page dimensions, generation bounds, custom imprint or per-node widths. The renderer uses 18-unit names, measures the busiest generation and wrapped text, and reserves short relationship corridors. A separate category key identifies the source groups above the family. Keep this key for an ordinary small family; extra floating family labels can accidentally name a neighboring branch. Placement does not change category membership. Inspect the first preview before adding exceptional emphasis. Dates need no repeated parentage prose when connectors already explain it.

Write explicit category membership before unions. A cross-family marriage keeps two category colors; its children retain the branch specified by the source. Do not turn a marriage, convergence or mixed ancestry into a new category unless the source defines one. For ambiguous category membership, preserve the available fact and qualify it instead of asserting a blended family.

Optional page controls:

| Field | Purpose |
| --- | --- |
| `cohort_top`, `cohort_bottom` | Centers of the first and last generations. Small families measure these automatically; dense pages default to 225 and page bottom minus 125. |
| `cohort_gap` | Minimum space between family units; default 22, minimum 5. |
| `partner_gap` | Empty space between partners; default 24, minimum 16. |
| `cohort_weights` | Object from row numbers to positive spacing weights before those rows. Reserve extra space for a consequential transition or family label. This is schematic spacing, not elapsed time. |

For more than 30 people, set node widths suited to their names and a page large enough for the busiest generation. A dense 1800 × 2700 poster can carry many generations, provided measured text and connector gutters fit. If a cohort exceeds the available width, widen the canvas or arrange that region explicitly. Never remove people to pass the check. Explicit dimensions override compact defaults and can recreate excessive blank space.

Use the `resolved_layout.nodes` coordinates in the render report to inspect or start an authored composition. To refine those positions manually, copy them into the source and change `layout` to `authored`; the ordinary `x`/`y` path then uses them directly. Preserve all identity and relationship fields.

Annotations can follow a named person using `{node,dx,dy,width,label,kind,group}` instead of absolute `x,y`. They resolve after family placement. Check that a moved family pill still names the right branch. It may move within a small search area to avoid labels; it does not search the whole page.

Use these branch annotations for dense authored compositions. A large horizontal `dx` can place an otherwise valid family name above an unrelated person. In a compact composition prefer the automatic category key; `legend: false` suppresses it only when a deliberate replacement is needed.

The mechanism is a starting composition, not an aesthetic certification. Inspect the middle and bottom as critically as the founding fan. Persistent parallel spines, synchronized unrelated dates, equal card widths, and periodically placed portraits still look mechanical. Use source-supported generational overlap, terminated lines, substantial sibling groups, and cross-family marriages where present. For complex trees, compose local regions explicitly instead of forcing all history through the cohort grid.

Run `render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json`, then `audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png`. Inspect the actual page and a dense marriage junction at 100%. The source JSON remains unchanged by layout.
