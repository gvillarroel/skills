# Connected handoff command contract

Create a connected-flow deck using the loaded skill's deterministic scaffold.
Write `flow.json` with exactly this data:

```json
{"id":"order-handoff","title":"Order handoff","labels":["Order","Pick","Pack","Dispatch"],"branch":{"at":1,"label":"Inventory check"},"return":{"source":2,"target":1,"label":"missing item"},"palette":"colorset1"}
```

Then run this exact command as its own shell tool call:

```sh
uv run --script skills/slidev-animejs/scripts/scaffold_connected_flow.py flow.json --deck deck --component OrderHandoff
```

Build the deck with npm using its deck prefix. Use the loaded skill's UV
capture helper with `--deck deck --output-dir captures`, and independently
inspect native text, complete arrowheads, all six route identities, actual
parcel motion, Replay and reduced-motion states. Confirm the parcel's
computed rendered fill is the primary color `rgb(158, 27, 50)` and that
measured geometry remains 457 by 240 native SVG units with 18px concept
type. Do not edit the generated geometry or component; this is a
deterministic implementation contract.

Required exact outputs: `flow.json`, `deck/slides.md`,
`deck/components/OrderHandoff.vue`, `deck/package.json`,
`captures/capture.json`, `captures/state-0.png`,
and `deliverables/layout-review.md`. Record build/browser commands and
actual color, geometry, route, replay and reduced-motion findings in the
review. Other generated verification files may remain in this workspace.

Treat `skills/slidev-animejs/` as read-only. Use only its runtime resources
and normal local tools; do not inspect acceptance examples, other skills
or repository files. Write every generated file in this workspace, use a
real `flow.json` file as the input, and install dependencies here. Do not
publish anything.
