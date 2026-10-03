# Independent visual review: Municipal Water Operations v2

## Scope

I inspected the v2 overview, the supplied network and capacity crops, the Peak state render, and the prior `after/overview.png` where comparison was useful. This is a screenshot-only review. It does not infer arithmetic, interactivity, accessibility compliance, or implementation details from the images.

## What changed visibly

The v2 network replaces the earlier curved and converging routes with mostly orthogonal runs and separated vertical lanes. That makes the overall routing easier to scan, and the connector strokes are darker and more visible than in the prior after render. The change improves structure, but the small arrowheads remain close to box edges and several junctions still require effort to interpret.

The overview keeps the same two-row card grid, muted palette, and typography scale. The Peak screenshot preserves the composition while visibly updating the state-specific marks and values: the unmet-demand bar becomes visible, the demand bar extends further, and the bullet chart moves to a 120% current state. These changes are easy to locate without disturbing the layout.

## Criterion assessment

| Criterion | v2 assessment | Visible evidence |
|---|---|---|
| Routing structure | **Improved, unresolved** | The network crop shows straighter, lane-like routes with fewer broad curves and less apparent crossing than the prior after render. The central vertical runs still crowd the processed/load-ratio area, and the top rectangular runs are not self-explanatory at their junctions. |
| Endpoint direction | **Improved slightly, unresolved** | Dark arrowheads are more visible, but several sit immediately beside intermediate box edges or narrow vertical segments. In the network crop, it is still difficult to tell at a glance which branch terminates at processed water, leakage, unmet demand, or delivered water. |
| Line contrast | **Improved** | v2’s charcoal flow lines and dotted dependencies stand out more clearly against the white cards than the gray-green lines in the prior after render. The thinnest arrowheads remain easy to miss at full overview scale. |
| Typography and hierarchy | **Unchanged** | Headline, question, section-label, and value treatments appear materially the same as the prior after render. The main copy reads well, while footer legend text, axis endpoints, and supporting annotations remain small and secondary. |
| Color restraint | **Maintained** | v2 retains the restrained teal, slate, brown, purple, burgundy, and ochre system. Peak adds no visibly noisy saturation; its changed marks remain within the same visual language. |
| Changed-state utility | **Improved** | The Peak screenshot keeps card positions stable while making state changes visible in the network, bars, bullet chart, gauge, and comparison table. The state is scannable, though the dense network still slows causal reading. |
| Spacing and density | **Unchanged, unresolved** | Card gaps and internal placement are effectively the same. The network remains the most crowded panel, while the lower cards retain large blank areas above their visualizations. |

## Previous findings status

- **Network connector collisions and ambiguous routing — reduced, remains.** Orthogonal lanes and darker strokes address the broad visual tangle. Tight ports, adjacent arrowheads, and unclear junctions still prevent a clean endpoint read.
- **Cross-row dependency seam — remains, slightly reduced in contrast problem.** The long dotted paths still span the boundary below the cards and do not make their source and destination obvious. Darker lines help visibility but do not clarify correspondence.
- **Supporting typography is small — remains.** The v2 type scale is not visibly larger; the smallest labels still require deliberate reading.
- **Uneven vertical fill — remains.** The lower row is still under-filled relative to the crowded network card.
- **Close or unstable semantic color mapping — no new regression visible; prior capacity-color claim is unconfirmed.** The screenshots do not establish that capacity changed color in the earlier comparison, so that claim is excluded as evidence of a fix or regression. v2’s restrained palette appears coherent, but screenshot resemblance alone does not prove canonical token identity.
- **A’s connector contrast regression — resolved/reduced.** v2 visibly darkens the flow and dependency strokes compared with the prior after render, while the endpoint ambiguity persists.

## Remaining issues, ranked

1. **High — Endpoint direction is still ambiguous in the network.** Arrowheads are small and frequently touch node borders or narrow lane turns. Use explicit ports, consistent arrowhead placement in open space, and enough gap before each destination box to make direction unambiguous.

2. **High — Cross-row dependencies still read as a page-wide seam.** The dotted routes below the cards have weak source-to-target correspondence. Shorten them or route each dependency to a named card with a clear endpoint.

3. **Medium — The network remains denser than the rest of the page.** Even with orthogonal routing, several parallel runs and junctions cluster in the center-left panel. A fixed lane order and larger inter-lane spacing would reduce the remaining reconstruction effort.

4. **Medium — Supporting text remains small.** Increase the readable explanatory tier for questions and captions, and reserve the smallest type for low-value axis or legend metadata.

5. **Medium — Lower cards leave too much unused vertical space.** Enlarge or vertically rebalance their visualizations so the two rows carry a more even visual weight.

## Recommendation

The v2 iteration is a **meaningful visual improvement** in line contrast and network structure, and the Peak state is easier to compare because the layout stays stable while marks update. It is not ready for a clean pass: endpoint direction and cross-row dependency correspondence remain the main blockers. Keep the v2 routing approach, then make ports and arrowheads explicit and rebalance the unused lower-card space. Treat the prior capacity-color discrepancy as unconfirmed rather than as a scored regression.

