# Content-sized fallback diagram assets

Use this route only when the video task requires a simple connected label box
and no specialist producer is available. Preserve supplied SVGs and richer
producer-owned geometry; do not replace them with this scaffold.

For a simple ordered spine of 2–6 concepts with at most one last-to-first
feedback route and one upward branch, use the measured scene scaffold first:

```text
uv run --script <skill-root>/scripts/scaffold_compact_scene.py --node sensor=Sensor --node controller=Controller --node motor=Motor --feedback --branch controller=Alarm --width 960 --height 540 --contract source/scene-contract.json --html src/index.html --review deliverables/geometry.json
```

Quote an entire `stable-id=Complete label` argument when it contains spaces.
For domain-specific relationship meaning, add repeatable quoted
`--meaning "sensor:controller=Sensor supplies measured input to Controller."`
arguments. A branch target ID is `<source-id>-branch`. These descriptions are
JSON-escaped metadata; they do not change routing or add unbudgeted captions.
Read generated asset paths from the scene contract rather than guessing its
asset-folder name. Keep the generated contract intact for this supported route.
For later contract customization, parse and serialize JSON with a normal JSON
library; never text-replace multiline object/array fragments.
The scaffold retains all requested relationships, measures each full label at
18 px, preserves the declared canvas, centers the complete motion envelope,
and reserves 52 px between adjacent bodies. At the default 4 px stroke this
leaves a 12 px head, visible endpoint clearance, a 7 px token radius and at
least 12 px of token travel. A tighter local candidate that violates that
envelope is rejected by the native compositor. Feedback uses a separate
22 px outer terminal lane, enough for the complete head approach, and a 10 px
lower corridor, keeping the 7 px token at least 3 px clear of concept bodies.
The geometry report includes the entire moving envelope.
Run the native validator and inspect initial, mid-route, arrival and held
states before writing the requested human review. The geometry report is a
measured baseline, not proof of a global packing optimum. Use fresh output
paths; `--force` rebuilds only the named task outputs and their asset folder.
Keep different branch topology, richer concepts, charts and supplied assets
on the normal producer-contract workflow.

Run the bundled helper for each required concept, outside the skill directory:

```text
uv run --script <skill-root>/scripts/scaffold_connected_asset.py --label "Controller" --output source/controller.svg --report source/controller-asset.json
```

The helper measures the complete label in Chromium at 18 px and creates a
small white SVG with readable black text, modest text clearance and two named
edge ports (`#in`, `#out`). The report supplies actual intrinsic dimensions and
port declarations for the scene contract. Record the fallback reason, source
hash and validation report. Keep the asset at native size in the fixed output
canvas before comparing compact placements; large empty source boxes are not
a substitute for measured label bounds. Do not enlarge a simple asset merely
to occupy the frame.

Place related assets close enough for short routes but preserve the complete
painted shaft/head envelope outside opaque shapes. Use distinct lanes for
feedback and branches; inspect endpoints, crossing identity and signal travel
at delivery scale. The asset report does not validate compositor routing.
Retain source geometry when animating supplied assets and preserve chart scales.
