Use the loaded `compose-synchronized-svg` skill to create an explanatory,
self-contained SVG for a neighborhood microgrid. It will be used in a
technical decision review. Use an intentional, restrained visual hierarchy
and make the colors easy to change through the supported authoring interface.
The organization supplies these brand choices: canvas #f8faf9, panel #ffffff,
primary text #172d2a, secondary text #526663, and primary accent #087f78. Honor
those colors where the skill supports them, document any limitation, and use
clearly distinguishable labeled identities for separate quantities.

Treat `skills/compose-synchronized-svg/` as read-only. Work only from this
prompt, the loaded skill, and normal local tools. Do not use the network,
sibling skills, parent directories, repository documentation, or acceptance
examples. Do not modify helpers or post-edit the monolithic generated SVG.

Use six distinct useful modules: energy balance, source comparison,
dependency network, renewable share, demand versus connection capacity, and
an exact ledger. Use English and state visibly that all numbers are synthetic.
Use scenarios, meaningful focus controls, and a readable static fallback, but
no autoplay timeline.

Inputs are demand, solar generation, wind generation, and connection capacity,
all in kW. The renewable output is solar plus wind. Renewable energy used is
the lesser of demand and renewable output. Grid imports equal demand minus
renewable energy used. Curtailed renewable energy equals renewable output
minus renewable energy used. Load ratio is demand divided by connection
capacity. Renewable share is renewable energy used divided by max(demand, 1).
Use this exact reconciliation for the allocation: demand equals renewable
energy used plus grid imports. Curtailed energy is a separate excess value
and must not be included as a part of demand.

| Scenario | Demand | Solar | Wind | Connection capacity |
| --- | ---: | ---: | ---: | ---: |
| morning | 90 | 35 | 25 | 120 |
| midday | 110 | 100 | 45 | 120 |
| evening | 145 | 10 | 30 | 120 |

Choose credible nonnegative domains covering these scenarios and zero demand;
the connection-capacity domain must exclude zero. Above-100% load ratios must
remain exact and use a suitable threshold encoding. Switching scenarios must
update all affected marks, visible values, and accessible descriptions.

Required exact files:

- `outputs/microgrid/composition-brief.json`
- `outputs/microgrid/composition-plan.json`
- `outputs/microgrid/composition-report.json`
- `outputs/microgrid/microgrid.svg`
- `outputs/microgrid/static-validation.json`
- `outputs/microgrid/browser-audit.json`
- `outputs/microgrid/overview.png`
- `outputs/microgrid/color-editing.md`

Use the documented preflight, compiler, composer, static validator, and compact
browser audit. Both reports must contain `ok: true`. Review the overview and
explain the supported recoloring/regeneration procedure in color-editing.md.
Preserve accessible labeled controls, meaningful script-free/reduced-motion
states, and unclipped essential content. Report any remaining limitation.
