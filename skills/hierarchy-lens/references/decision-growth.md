# Composition by explicit decisions

**Pattern ID:** `hierarchy-decision-growth` · **Example set:** `hierarchy-lens`

Use for priorities, roles, importance, proximity, packing rules, or explanations of how records enter a procedural image. The engine makes two real decisions per step: select an eligible record, then select an unoccupied frontier cell. Shape depends on these decisions and the data. This is a deterministic greedy heuristic, not a global optimizer or an organization's history.

## Input and policy

Use the normal [input contract](data-contract.md), plus a top-level `composition` object, or pass this object as a separate JSON file with `--composition policy.json`:

```json
{
  "priority": {"key": "role", "order": ["Engineering", "Product", "Operations", "Sales", "Finance", "People", "Leadership"]},
  "affinity": "role",
  "eligibility": "generation",
  "weights": {"parent": 2, "affinity": 6, "compactness": 2, "radial": 1},
  "frontierWindow": 4
}
```

This is an editable demonstration order, not intrinsic role importance. Honor a supplied category order. For a prototype without a chosen order, identify the choice as provisional and expose ordering controls. Custom categorical priority requires every declared category exactly once; palette order alone is not a placement policy. For numeric priority use `{"key":"tokens","direction":"descending"}` or `ascending`. Missing values enter last; zero is observed. Equal priorities use lexicographic record ID, independent of locale.

`affinity` is one categorical key or null. All four weights are finite numbers from 0 to 10. `frontierWindow` is an integer from 1 to 8, in cell units. Priorities choose entry order, affinity and spatial weights choose positions, and color paints the resulting cells.

- `eligibility: "generation"`: complete lower-depth generations first, then select the highest priority in the next generation. This is the demonstration default.
- `eligibility: "parent"`: any record whose parent has entered is eligible. A high-priority grandchild may precede a lower-priority uncle. This relaxes generation order; do not interpret radius as a depth scale.

The root is always first at the center. Preserve every source identity, value, and parent. Pass the requested cell size explicitly: **one logical pixel per record means `--cell-pixels 1`; a 2 by 2 square means `--cell-pixels 2`, which is four pixels per record.** The option is a side length, not an area. Do not leave the four-pixel default when the user asks for one pixel.

## Build and inspect

Decision builds require Python/`uv` and Node.js. Python calls the same bundled JavaScript engine used for browser recomposition. The resulting HTML works offline without Node, CDNs, or uploads. Normal runtime use needs this reference and the input contract, not engine/UI source or acceptance examples.

```text
uv run --script <skill-root>/scripts/build_explorer.py --input hierarchy.json --view decision --output explorer.html --report build.json
uv run --script <skill-root>/scripts/audit_decisions.py explorer.html --report audit.json --screenshot overview.png
```

For a fictional organization, use `--demo --demo-size N` and `--data-output hierarchy.json`. This supplies the explicit editable role policy above. For example:

```text
uv run --script <skill-root>/scripts/build_explorer.py --demo --demo-size 430 --view decision --output explorer.html --data-output hierarchy.json --report build.json
```

Keep requested output paths outside the bundle. The interactive decision engine supports at most 5000 records; the other organic mode's 20000-record cap does not apply here.

### Apply the requested policy, including to demo data

The demo's role priority is only a starting policy. Override it when the user asks for a different factor. These CLI options update both the embedded policy and `--data-output`, so no intermediate rebuild or JSON patch is needed:

```text
uv run --script <skill-root>/scripts/build_explorer.py --demo --demo-size 430 --view decision --priority tokens --priority-direction descending --affinity role --eligibility generation --cell-pixels 2 --output explorer.html --data-output hierarchy.json --report build.json
uv run --script <skill-root>/scripts/build_explorer.py --input portfolio.json --view decision --priority tokens --priority-direction descending --affinity status --eligibility parent --weights 4 3 2 1 --frontier-window 2 --cell-pixels 1 --output portfolio.html --report build.json
```

Replace dimension keys with the actual input keys. For categorical priority, pass `--priority KEY --priority-order FIRST SECOND ...`, quoting category values with spaces; include every category exactly once. `--affinity none` disables that preference. CLI policy options override the corresponding fields from `source.composition` or `--composition policy.json`. Numeric priorities require an explicit direction. Read the build report before delivery: verify `composition.priority`, `composition.eligibility`, and minimum/maximum pixels per record against the request. A passing browser audit validates the supplied policy, so it cannot substitute for checking that this is the policy the user requested.

When custom input already exists at its requested deliverable path, use it as `--input`; do not also pass that same path as `--data-output`. Input, HTML, report, policy file, and optional data-output paths must be distinct.

## Vacancy scoring

Every candidate is empty and orthogonally adjacent to the placed body. Consider radius at most `minimumFrontierRadius + frontierWindow`, allowing existing gaps to be filled while preserving compact growth. Reject a candidate that would disconnect the surrounding background and enclose a hole. Hard constraints take precedence over weights.

The explicit weighted sum uses:

- **Parent:** `1 / (1 + Manhattan distance to the placed parent)`.
- **Affinity:** `0.65 / (1 + Manhattan distance to the centroid of placed matching records) + 0.35 × matching adjacent cells / 4`. Use zero when disabled, missing, or without a placed match. Missing values are not an affinity category.
- **Compactness:** occupied orthogonal neighbors divided by four.
- **Radial:** `1 / (1 + Euclidean distance to the root)`.

Choose the highest sum. Seeded integer hashing breaks equal-score vacancy ties; the seed does not prescribe the contour. Retain the two next-best allowed alternatives with positions, terms, and scores. Record eligible count, priority value, candidate count, and hole-forming candidates skipped before retaining the best three. The root has an explicit mandatory-placement exception. Do not claim the heuristic evaluates every future arrangement.

Cell contact is spatial packing, not a reporting edge. Parent proximity and affinity are preferences, not guarantees of adjacency or connected subtrees. Every replay prefix is connected and hole-free, with equal area per record. Under generation eligibility, completed generation prefixes are connected too.

## Playback and recomposition

The opening view shows the completed composition. Replay reveals actual recorded placements; arrows and the range slider inspect exact prefixes. Speed changes presentation, not decisions. The outside panel explains the current record, eligibility/priority, score contributions, and alternatives. Searching for a future record advances the visible prefix to include it.

Rules expose priority dimension, categorical order, numeric direction, affinity, eligibility, four weights, and growth allowance. Apply rules invokes the engine on the original records and shows the complete new composition. Restore rules reproduces the opening layout. Color lenses change neither positions, decisions, nor replay progress.

PNG and SVG capture the current prefix. SVG metadata contains source context, policy, complete trace, and visible count. The JSON decision-log download includes records, policy, seed, cell size, and full sequence. Keep this context with a bare PNG when sharing its meaning.

## Validate

Run `test_decisions.py` and `test_explorer.py` after engine changes. `audit_decisions.py` includes pixel validation, independent priority/eligibility checks, parent precedence, score sums, exact prefix pixel counts, play/pause/step/scrub, editable policies, deterministic restore, real SVG/JSON downloads, color independence, offline requests, and browser errors. Inspect the role view, partial growth, rules panel, and mobile controls. Exercise scale, parent-ready, missing-value, singleton, and one-pixel cases. Report measured limits without claiming optimality or unlimited scale.

Preserve prior view links when publishing the [decision example](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-decision-growth). The [organic recipe](organic-pixels.md) remains available for geometric growth without attribute-driven placement.
