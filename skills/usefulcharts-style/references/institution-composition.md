# Composing institutional histories

Use this procedure for a dense `usefulcharts-branching-lineage` poster. It addresses a visible failure: exchanging city names inside a fixed sequence of institution types still produces a template, even if cards have different colors and positions.

For 30 records or fewer without prescribed positions, begin with [compact lineage](compact-lineage.md). For a medium history of roughly 31–100 records, use [packed stories](packed-stories.md) to measure a page from relative neighborhoods. Small institutional mergers are supported by automatic placement. Reserve the authored workflow below for a specific difficulty observed in the first preview, prescribed coordinates, or a larger, denser source.

## Write the records before the geometry

Give each institution a stable ID, name, category, founding or reorganisation date, source, and short historical role. Record its actual predecessors separately. Distinguish a continuing institution, a new branch, a closure, a merger, and intellectual influence. In the renderer, a stated merger can have two incoming `branch` paths and an explicit label such as “The two colleges unite”; this must not imply two biological parents. An `influence` path does not transfer institutional identity.

Do not derive dates from coordinates, choose a parent by nearest x position, or generate a family from a list such as office → school → college → institute. In a synthetic demonstration, author coherent individual histories and declare them invented. In a factual chart, preserve the supplied history even when it is inconvenient to lay out.

## Build the page from local stories

1. Select a small number of consequential establishments, divisions, unions, or changes of function. These become visual landmarks. Allocate widths and emphasis to their roles, not to every nth record.
2. Put shared precursors in a compact upper story. Use adjacent free space for a relevant count or map; repeat the map's category key beside the map. A distant color key may not explain an inset clearly.
3. Compose each local story around a short, readable descent spine. Put a terminating side branch beside that spine rather than in front of its next port. Keep mergers close enough that their two predecessors can be followed without leaving the local group.
4. Let an old family persist beside a newer tradition when the records require it. Reclaim space after closures. Keep approximate chronological order across neighboring stories where possible; large backward influence paths often reveal inconsistent placement of the same historical period.
5. Reserve long influence corridors before finalizing the cards. Give them specific entry and exit positions. Do not let a route search produce a large loop around several unrelated institutions merely to satisfy collision checks.

Use `corridor_y` to align a clear local merge, or `via` for deliberate orthogonal bends. Where two same-category paths represent the same stated merger, a common final corridor can be clearer than nearly parallel lines a few units apart. Inspect it as a relationship, not only as geometry. Crossings between unrelated paths must remain distinguishable from joins.

If the renderer reports a crowded search port, move the neighboring node or reserve at least 18 units at the attachment. Enlarging the search area cannot repair an endpoint inside an obstacle. A substantial detour is also a reason to recompose the group rather than accept the first technically valid route.

## Add identity and verify the result

Use plain names for routine continuations, compact colored cards for established institutions, and larger treatment for a few consequential institutions. Keep a colored panel focused on the name. Put the date immediately above it, where the incoming connection ends, and the contextual caption below it on the paper. This makes a consequential name visible without giving every explanation the weight of a colored card.

For this treatment, set `detail_position: outside`, put the exact historical date text in `date_label`, and put only the contextual phrase in `detail`. For example:

```json
{"id":"public-library","label":"The Public Library","group":"civic","x":580,"y":760,"width":148,"style":"card","detail_position":"outside","date_label":"c. 1740–1745","detail":"Two collections unite"}
```

Do not infer a date from the position or parse an uncertain date into false precision. An existing `founded` field is data, not a printed label: supply its intended wording as `date_label`. Omit a missing date rather than invent one. The renderer reserves the whole date/name/caption envelope; the node center and connector ports refer to that envelope. After converting old cards, inspect nearby attachments because the colored panel shrinks while the complete envelope may grow. Move the local group when needed. Never route through an external caption to regain space.

A precise phrase such as “Civil instruction separates” often provides more identity than another generic star or book. Use a relevant source illustration for selected landmarks; never treat a historic drawing as that fictional institution's logo or an unrelated real person's likeness. White image panels can deliberately contain opaque source drawings. Keep those panels compact and inspect the visible silhouette at the placed size; a delicate full figure needs more room than a strong compass card. Repetition should follow a shared identity, not substitute for selecting relevant artwork.

Run the renderer, then `audit_chart.py --source brief.json --report browser.json --png poster.png`. Compare the whole page and at least two dense local groups against the reference at the same relative scale. Trace each merger in both directions and follow the longest influence path. Check that the larger titles, meaningful small names, illustrations and empty corridors form a hierarchy. Passing the audit does not establish visual parity.
