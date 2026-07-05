# Metro Minimal Tonal Motion

Use this reference for Metro Minimal Tonal Motion, strict-grid, square-edge, no-padding, colorset1, grayscale-hierarchy, or feedback that the video is not following the design.

This is a final-design contract, not a scaffold contract. A wrapper pass, contact-sheet pass, render-state pass, and Metro audit pass prove that the artifact is buildable and mechanically valid. They do not prove that the video is polished, aligned, rich, or faithful to this style.

## Core Contract

Design the video as one large navigable visual object.

- Build a megacanvas with at least three functional zones, and at least five for polished Metro, complex low-text, or design-rejection repair work. Useful zones include summary blocks, main mechanism, table or matrix, graph, process, evidence surface, or operational state board.
- For generated helper outputs, make the zone contract machine-checkable: `source-package.json` should expose `visualZones` and `semanticBindings`, the SVG should expose visible `data-zone-id`, `data-zone-role`, and `data-source-anchor-json` markers with legacy `data-source-anchor` fallback, and `renderConceptFrame` should return `visibleZoneCount`, a changing `activeZoneId`, and `activeSourceAnchors`.
- Use camera exploration between zones: zoom in, zoom out, pan, diagonal move, masked reframe, tile morph, surface wipe, or expanding block transition. For generated audits, small decorative camera nudges do not count; render-state evidence should show meaningful travel and zoom depth.
- Keep the composition continuous. Do not make a series of unrelated slide frames with repeated titles.
- Do not reserve any visible area for titles, subtitles, captions, checked dates, draft labels, or editorial text. Those belong in source packages, manifests, filenames, or post-production.
- Use visible text only when it is part of the visual object: node names, states, axis values, table cells, compact legends, counters, or labels that identify data-bearing marks.
- Do not render labels with `...` or `…`. If a label cannot fit, redesign the local layout or source label. Ellipsized text makes the object read unfinished and hides source meaning.

## Palette

Default to colorset1:

| Role | Color |
| --- | --- |
| primary red | `#9e1b32` |
| dark red | `#6d1222` |
| status red | `#e8002a` |
| red highlight | `#ffccd5` |
| neutral text | `#333e48` |
| white | `#ffffff` |
| black | `#000000` |
| gray 100 | `#e7e7e7` |
| gray 200 | `#cfcfcf` |
| gray 300 | `#b5b5b5` |
| gray 400 | `#9c9c9c` |
| gray 500 | `#828282` |
| gray 600 | `#696969` |
| gray 700 | `#4f4f4f` |
| gray 800 | `#363636` |
| gray 900 | `#1c1c1c` |

Use colorset2 only when colorset1 cannot separate necessary semantic states. Record the reason in production notes. Extra color must carry state, category, or risk; it must not be decoration.

## Geometry

Use hard modular geometry.

- Rectangle corner radius is `0`.
- Line caps and joins are hard, not rounded.
- Major edges snap to a 4 px grid.
- Blocks align by shared edges, shared baselines, and repeated module widths.
- Use external gutters to separate modules.
- Boxes have no internal padding. The rectangle edge is the content boundary.
- Do not create inset bars, padded chips, rounded tags, nested inner panels, or small rectangles that simulate padding inside a box.
- Put labels on the edge, in adjacent flush lanes, or in separate flush rectangles.

## Grayscale Hierarchy

Build hierarchy with distinct gray levels before adding hue.

- Use at least four visible gray hierarchy levels in any final frame with more than one zone.
- Reserve red for state, emphasis, failure, selection, or alert paths.
- Keep red area small in comparison and product-choice modules. Prefer gray hierarchy for surfaces, with red as a route, state edge, thin cap, or selected path; broad red panels make the composition read like branded UI instead of Metro tonal motion.
- Keep gray roles stable across the video: background, surface, module, connector, inactive mark, active mark, and high-emphasis mark.
- Avoid one-note gray fields where all blocks sit at the same luminance.
- In dense zones, prefer alternating gray bands, edge weights, or surface levels over extra padding.

## Composition Rules

The first frame should already read as a designed object.

- No empty title band, lower-caption strip, or centered text-first intro.
- At least two intentional focal points should exist in dense frames.
- Primary and secondary zones should align to an obvious armature: grid, diagonal, central spine, left-to-right flow, radial hub, or masonry wall.
- Transitions should preserve geometry: a tile expands, a surface wipes, a block becomes a chart, a table becomes bars, or the camera enters a subsection.
- Avoid decorative shadows, bevels, blur fields, perspective, gradients, floating decorative objects, or generic UI chrome.
- Avoid nested cards. A zone can be a surface or block; repeated objects can be modules. Do not put cards inside cards.

## Motion Requirements

For polished Metro output, require all of these:

- At least three semantic motion systems across the video, such as queue fill, packet route, meter update, matrix activation, edge draw, table-to-chart transform, block construction, graph expansion, or camera reframe.
- At least two camera or reframe events when duration is 20 seconds or longer.
- At least one transition that uses the modular style itself: expanding block, tile morph, surface wipe, masked reframe, or masonry construction.
- Ordered render-state samples should prove the path, not just the summary. `statesSample` should show adjacent `activeZoneId` changes, and those zone changes should coincide with camera pan, zoom, or reframe deltas.
- Pauses after major reveals so frames can be read.
- Motion must change state. Do not rely on fades, slides, global sweeps, or ambient particles as the main explanation.

## Mute Test

Review without narration.

The viewer should infer the major mechanic from object state, direction, transformation, and hierarchy. They do not need every detail, but they should see what changes because of what. If comprehension depends on reading a heading, caption, or paragraph, redesign the visual mechanism.

For generated artifacts, run `scripts/audit_metro_mute_test.py` directly or through `scripts/run_metro_audit_suite.py`. It hides rendered SVG text, samples `renderConceptFrame`, and fails when hidden-text frames lose visual motion, functional-zone evidence, gray hierarchy, nonbackground area, or mark density. Passing low text-area checks is not enough; the visual object must still change when text is hidden.

The suite defaults to a bounded four-sample mute test for long-video reliability. This is not a weaker design gate: the mute-test still requires three adjacent hidden-text changing pairs, so all sampled hidden-text pairs must change. Use a higher `--mute-test-samples` value only for manual deep audits after the faster suite passes.

## Rejection Gate

Reject or redesign the video when any item is true:

- The contact sheet looks like slides with labels.
- The encoded MP4 composition audit reports weak grid coverage, weak quadrant distribution, weak opening composition, weak spatial progression, or excessive text-like component pressure.
- The encoded MP4 composition audit reports `maxRedAreaRatio` above the threshold. Treat broad red-family surfaces in the contact sheet as a composition failure; red should read as a state/path/accent system, not as the dominant block material.
- The source omits the colorset1 typography contract. Generated Metro HTML should declare `font-family: 'Open Sans', Arial, sans-serif`; `Segoe UI` or an unscoped default UI font stack is a style failure.
- The opening tile is mostly empty or reserved for title text.
- The final tile has fewer than four visible gray hierarchy levels.
- Motion is mainly identical fade/slide entrances.
- Camera movement is absent or only decorative even though the prompt asks for Metro video style.
- Rounded borders, pills, soft panels, or padded boxes are visible.
- Required Masonry output has no zero-padding measurement coverage or reports any padded module interiors.
- Red rectangles become dominant surfaces instead of state/routing marks. For AI alternatives, Guardrail, Hook, Skill, LLM billing, metric dashboards, Sankey flows, and similar product-choice or risk modules, treat `maxRedRectAreaRatio > 0.10` in rendered-frame audits as a redesign signal even if other audits pass; for encoded MP4 review, treat `maxRedAreaRatio > 0.08` as a hard failure unless the prompt explicitly asks for a red-dominant warning state.
- Metro source keeps any nonzero rounded-corner fallback such as `rx: masonryRequired ? 0 : 14`, nonzero `ry`, or CSS `border-radius`. The rendered frame may normalize it, but the source is still off-contract.
- Text explains the concept while geometry only decorates it.
- Source anchors are only preserved in arrays or labels and are not bound to visible zones, mechanisms, rendered JSON source-anchor markers, and active render-state samples.
- One large label or paragraph block dominates the frame even if total text area stays low.
- Any visible functional label is truncated with `...` or `…`.
- Functional zones are not aligned to a grid, spine, masonry wall, or other stated armature.
- Color is used as decoration instead of role: colorset1 gray levels should separate structure, while red should mark state, emphasis, failure, selection, or alert paths.

When this gate fails, improve the storyboard, composition, or renderer from the design contract. Do not solve the issue by adding more text, shrinking labels, or adding a cosmetic palette pass. Recompose the megacanvas, align zones to the chosen armature, remove padded/rounded/title-led elements, and rerun the Metro audits, MP4 composition audit, and semantic-density gate before accepting the output.

## Plan Validation

For plan artifacts, run `scripts/validate_metro_design_contract.py` against the Markdown plan and `design-contract.json`. Use `--require-text` for source anchors that must be preserved. A passing report proves the plan carries the Metro contract fields, required sections, pattern counts, source anchors, and mute-test statement before implementation starts.

## Runtime Semantic-Density Validation

For generated Metro video artifacts, run `scripts/audit_metro_semantic_density.py` after the wrapper, render-state checker, contact-sheet composer, Metro audit suite, mute-test audit, and MP4 composition audit have produced JSON reports. The semantic-density audit combines those reports and rejects outputs with weak mechanism progression, too few dynamic state keys, too few source `visualZones`, missing or incomplete `semanticBindings`, source anchors that are not bound through source package plus rendered DOM plus render-state samples, missing `visibleZoneCount`, static `activeZoneId` evidence, too few ordered active-zone changes, weak camera/zone coupling, too few rendered DOM zone markers, missing camera movement, weak contact-sheet change, weak visual diversity, weak opening tiles, rendered text dominance, weak mark-to-text density, visible title/date/editorial bands, ellipsized rendered labels, rendered padded module interiors, failed mute-test evidence, missing MP4 composition evidence, missing source preservation, failed Metro child audits, missing modular transition types, or a missing/non-passing `metroPatternMix`.

Use this gate for polished Metro, complex, dynamic, or low-text requests. A passing style/composition audit proves the frame follows surface rules; the semantic-density audit proves the video changes enough state to be useful, exposes a real functional-zone map, binds source anchors to visible mechanisms, follows an ordered continuity path, passes the text-hidden mute test, passes encoded-MP4 composition checks, and that the rendered `visualPattern` follows the selected `helperPattern`, while the pattern mix carries enough patterns, zones, semantic motion systems, camera events, modular transition contracts, and anti-pattern risks to reject boxes-plus-labels output. The gate fails closed when wrapper, state, contact-sheet, Metro suite, source-package, rendered-frame, mute-test, or MP4 composition evidence is missing.
