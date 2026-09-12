# Focal people and the opening family fan

Use this refinement when a genealogy has become a sequence of equally weighted nameplates. Start from the declared records, partnerships, parentage and contextual fields. Decide which supplied people deserve emphasis before changing the layout. Preserve names, dates, categories, portrait identities and annotation bindings.

## Give selected records enough presence

Choose a small source-supported set: named founders, consequential rulers, or people explicitly highlighted in the task. A person's position in a list or an arbitrary generation interval is not evidence of importance. Preserve existing source emphasis. Do not invent titles, events or historical consequences to justify a larger card.

Use a correctly identified portrait for a factual person. For an explicitly fictional study, the bundled museum samples may serve as disclosed decorative illustrations; say they are not likenesses. Keep an existing image identifier when adjusting its size. Read [the editorial contract](editorial-contract.md) for supported artwork. Never replace an identified image with a more convenient face merely to fit a box.

Keep the name and dates as real editable text. Use `detail_position: outside` so the portrait and colored name panel are distinct from the subordinate date line. Set `icon_width` and `size` before measuring the family. Let the panel width accommodate both the longest word and the image; preserve complete portrait, name and date envelopes. A short name need not be forced onto two lines to imitate the reference.

For a dense mural with ordinary 11–12-unit principal names, try selected 13–15.5-unit names and roughly 40–48-unit portraits. A compact family already uses larger names: start with `emphasis: true`, the normal measured 22-unit focal type and an approximately 44–50-unit image. These are initial proportions, not mandatory values. Compare the complete page at the same display width as the reference, then inspect the selected figures at reading scale. A larger image should create a focal group without making its neighboring spouse disappear.

For a new family, declare these fields in the data-first cohort brief and use the baseline helper. Its measured defaults account for images and complete captions. Preserve required context annotations and use `--reserve-context` when applicable. For a dense authored mural, recompose the affected family units and their connections deliberately, or rebuild the cohort arrangement while retaining all source records. Do not enlarge every portrait and then repeatedly grow the page until geometry happens to pass. One justified proportional change to a dense canvas may be useful; judge its effect on the other names at the same final display or print size.

## Open the first branches deliberately

Use `cohort_spread` only after a preview shows a visibly tapered opening or tightly clustered early branches. The object maps existing generation rows to expansion factors from 1 through 2:

```json
{"cohort_spread": {"1": 1.35, "2": 1.25, "3": 1.15}}
```

The cohort packer expands complete family units around each row's occupied center after its ordinary parent/child relaxation. Partnerships retain their internal gaps and ordering. The printable field limits the requested expansion; a row that is already full has little or no available expansion. This is an authored schematic preference, not a change to dates, ancestry, membership or the numeric time scale. Do not use it to manufacture extra branches.

Use fewer or smaller factors when the opening consumes the useful side pockets or creates dominant horizontal connectors. Leave later generations unconfigured unless a specific part of the source warrants their expansion. Do not mistake a broader fan for a complete composition: inspect the middle and lower parts independently.

## Render, compare and preserve difficult context

Run the normal `space_family_branches.py`, `render_chart.py` and `audit_chart.py` sequence documented in [local family baselines](branch-baselines.md). Keep source input and resolved output separate. Open the final PNG and trace a cross-family marriage beside an enlarged portrait, an early founder, a terminated line and the longest local connection.

Changing a family width may consume a former caption pocket. Keep its exact node/field binding. Try a narrower readable caption with stacked artwork or compose local room; do not silently omit the caption or attach it to another fact. The source-bound landmark workflow measures the complete text and art, including connecting paths.

The router keeps seven units of clearance in its obstacle search. It tries the existing broad search regions first, then adds closer visibility coordinates if all broad searches fail. This preserves ordinary successful routes while making an otherwise legal narrow gap discoverable. It does not permit text collisions or make every difficult junction solvable. If the actual attachment is crowded, move the surrounding family unit and rerender; widening an abstract search window cannot repair an occupied port.

Accept the refinement only if the enlarged records help reading at page scale and the remaining people, dates, partnerships and local captions remain legible. Record residual repetition and long routes separately from geometry passes. Neither a larger portrait count nor a lower crossing count proves visual equivalence to the reference.
