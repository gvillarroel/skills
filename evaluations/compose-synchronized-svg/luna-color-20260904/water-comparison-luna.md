# Independent visual comparison: Municipal Water Operations

## Scope

This review compares only the rendered screenshots at the requested 1600×1000 view. The panels, visible labels, and displayed figures appear materially identical in A and B, so the findings concern visual presentation. No arithmetic, interaction, or accessibility compliance is inferred from the images.

## Criterion comparison

| Criterion | Better | Visible evidence |
|---|---|---|
| Palette restraint | **A** | A uses a muted teal, slate, brown, purple, and burgundy set against warm white cards. B uses several highly saturated blue, green, purple, pink, and teal accents; they compete more strongly with the content and make the dashboard feel noisier. |
| Meaning of recurring colors | **A** | A reuses related tokens across views: demand is teal, capacity brown, leakage burgundy, delivered water slate, and leakage fraction purple. B has more visible shifts, including capacity changing from green in the network to teal in the lower bar and leakage fraction using purple while leakage outcome uses green. A’s mapping is easier to reconstruct from repeated marks. |
| Text hierarchy and readability | **A, slightly** | Both have the same apparent type scale and line breaks. A’s dark neutral body copy and clearer card outlines separate headings, explanatory copy, and values more calmly. B’s saturated blue labels pull attention toward metadata. Small footer, axis, and supporting labels remain a reading burden in both. |
| Connector clarity | **B** | B’s network paths, arrowheads, and row-boundary dependency lines have stronger contrast and are easier to see at a glance. A’s gray-green connectors recede into the white cards, especially around the central network convergence and along the long dotted lines below the cards. B’s stronger strokes do not resolve the underlying path crossings. |
| Spacing and grouping | **Neither** | The card geometry, gaps, chart placement, and large unused areas are effectively the same. A’s borders make grouping feel a little more deliberate, but neither version fixes the dense upper-left network or the under-filled lower cards. |
| Overall utility | **A** | A provides the clearer visual system: calmer color use, stronger semantic reuse, and more legible grouping. Its connector-contrast regression is real and should be repaired before treating it as final. |

## Remaining issues, ranked by severity

1. **High — Network routes remain difficult to follow in both versions.** Multiple paths leave the three left input nodes, converge tightly around the processed/load-ratio area, and place arrowheads close to node edges. B makes the strokes more visible; neither makes the causal routing unambiguous.

2. **High — Long cross-row dependencies have weak source-to-target correspondence.** The dotted paths running across the boundary below the cards span much of the page, while their small arrowheads sit away from clearly named endpoints. A’s lower contrast makes this worse; B’s visibility does not fix the mapping.

3. **Medium — Supporting text is too small for comfortable scanning.** Section questions, axis labels, radial endpoints, footer legend text, and compact table/chart annotations are visibly subordinate to the point that they require deliberate reading in both screenshots.

4. **Medium — Visual weight is uneven across cards.** The upper-left network is comparatively crowded while the lower cards retain large uninterrupted blank areas above their visualizations. The shared grid does not yet produce an even reading rhythm.

5. **Low — A still has a few closely related teal encodings.** Processed water, demand load ratio, and the bullet chart’s current bar can look like one family at a glance. Labels carry the distinction, but a stable token or secondary mark treatment would reduce the reconstruction effort.

## Recommendation

Use **A as the base for the next revision**, because it is more restrained and its recurring semantic colors are easier to follow. Restore some of B’s connector contrast by darkening A’s flow/dependency strokes and separating arrowheads from node edges. Re-route the network and cross-row dependencies before release; the comparison does not support a forced pass for either screenshot in its current form.

