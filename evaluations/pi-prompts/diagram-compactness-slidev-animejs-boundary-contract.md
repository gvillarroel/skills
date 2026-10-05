# Connected routing boundary command contract

Create a native connected-flow deck from the loaded skill's deterministic
scaffold, at its supported six-main-concept boundary. Write `flow.json`
with exactly this data:

```json
{"id":"access-routing","title":"Access request routing","labels":["Request","Parse","Authorize","Queue","Run","Notify"],"branch":{"at":0,"label":"Policy store"},"return":{"source":5,"target":0,"label":"retry"},"palette":"colorset1"}
```

Run this exact command as its own shell tool call:

```sh
uv run --script skills/slidev-animejs/scripts/scaffold_connected_flow.py flow.json --deck deck --component AccessRouting
```

Build the deck with npm using its deck prefix, then use the loaded skill's
UV capture helper with `--deck deck --output-dir captures`. Inspect all
seven concepts and all eight directions at native readable size. Do not
edit the generated component or reduce its type. Record measured native
dimensions and complete heads, separate first-node reciprocal ports and
the last-to-first return. Watch each entire sequence: the five main hops
on click 1, then the longer return plus both Policy-store directions on
click 2. The capture helper's brief sampling alone may not cover this
longer sequence; add correctly awaited browser samples inside this
workspace as needed. Check closest parcel approaches against nodes,
route labels and full heads, Replay, reduced motion and computed primary
parcel fill `rgb(158, 27, 50)`.

Required exact outputs: `flow.json`, `deck/slides.md`,
`deck/components/AccessRouting.vue`, `deck/package.json`,
`captures/capture.json`, `captures/state-0.png`,
and `deliverables/layout-review.md`. Record actual native/browser findings
and commands in the review. Other generated verification files may remain.

Treat `skills/slidev-animejs/` as read-only. Use only its runtime resources
and normal local tools; do not inspect acceptance examples, other skills
or repository files. Write all generated files and verification captures
in this workspace, use a real `flow.json` input file, and install
dependencies here. Do not publish anything.
