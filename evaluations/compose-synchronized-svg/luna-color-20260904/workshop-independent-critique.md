# Independent visual critique: Workshop Throughput Atlas

## Overall assessment

The atlas is a polished, coherent dashboard composition with a clear two-row story: drivers and constraints above, outcomes and consequences below. The restrained blue and pale panel backgrounds, repeated section labels, and consistent card geometry make the page feel intentional. The strongest communication comes from the large network diagram and the radial/bullet pair, which establish the operating model and its two headline ratios quickly.

At the intended 1600×1000 size, the main titles and headline values are legible, but several supporting labels are close to the minimum comfortable reading size. The lower row has substantial unused vertical space while the network panel is comparatively busy. The cross-row dashed connectors and a few compact chart annotations weaken the otherwise strong visual hierarchy.

## Prioritized findings

### 1. High — Cross-row connectors read as an accidental seam

**Evidence:** A blue dotted path and an orange dashed path run horizontally across the boundary around y=535, with short vertical segments and arrowheads near x≈350–390 and x≈1380. They visually cut through the gap between the two section containers and appear to terminate without an obvious source or destination.

**Why it matters:** These lines compete with the section labels and can be mistaken for clipping, a border artifact, or a third row. The intended relationship is hard to follow at a glance.

**Transferable remedy:** Route dependencies as short, explicit connectors from a named source card to a named target card, using generous clearance from container edges. If a relationship spans rows, add a small labeled bridge or a legend keyed to the line style and keep the path outside the section titles. Avoid long horizontal runs that cross an entire dashboard width.

### 2. High — Network diagram connectors collide and create ambiguous routing

**Evidence:** In the upper-left card, multiple curved/angled lines leave the three left nodes and converge near the Capacity applied / Excess arrivals nodes around x≈260–280. Several arrowheads overlap or sit directly on the node edges; the route into Completed work around x≈465 is also visually tight.

**Why it matters:** The diagram is meant to explain causality, but the visual crossing makes it difficult to determine which input feeds which intermediate outcome. This is an objective legibility problem at the displayed scale.

**Transferable remedy:** Use orthogonal lanes with one departure lane per input, fixed vertical ordering, and a minimum gap between parallel paths. Put arrowheads in the open space immediately before the destination node and use line offsets or small ports so no connector enters through another connector’s path.

### 3. Medium — The lower row is vertically under-filled relative to the upper row

**Evidence:** The Sankey, comparison table, and waterfall occupy mainly the lower half of their cards, leaving large uninterrupted pale areas above the chart content. The upper cards devote more of their height to explanatory copy and diagram structure.

**Why it matters:** The page’s visual weight is top-heavy, and the outcome section can feel disconnected from the driver section despite the shared container treatment.

**Transferable remedy:** Align each lower visualization closer to its explanatory copy, or use the available height for a larger chart, stronger annotation, or a compact takeaway row. Keep a consistent internal rhythm across cards: title, question, one-sentence interpretation, then visualization with a defined baseline.

### 4. Medium — Supporting typography is small and low-contrast in several places

**Evidence:** The section subtitles, chart questions, footer legend, axis labels, and small value annotations (especially around the radial gauge and waterfall) are rendered in fine, small blue-gray text. They remain visible in the full screenshot but are not as immediately readable as the headline values.

**Why it matters:** The hierarchy between explanatory text and decorative metadata is not always clear, and the smallest labels are likely to be skipped when the page is scanned.

**Transferable remedy:** Establish two explicit supporting-text tiers: a readable explanatory tier for questions and captions, and a smaller metadata tier only for axis/legend details. Increase line height and darken the explanatory tier slightly; reserve all-caps micro-labels for short, high-value tags.

### 5. Medium — Color semantics are mostly consistent but the purple/magenta distinction is too subtle

**Evidence:** Purple is used for First pass success in the input card and gauge needle, while a nearby magenta outline marks Excess arrivals. In the lower Sankey, first-pass failures use pink and excess arrivals use a pale purple swatch. These hues are close enough that the category mapping takes effort to reconstruct from the legend and labels.

**Why it matters:** Color appears to carry category meaning, but related outcome states do not have a single unmistakable visual identity across panels.

**Transferable remedy:** Assign one stable color token per semantic state and reuse it for outlines, marks, swatches, and annotations. Choose visibly separated hues or pair each color with a repeated label, line style, or shape so the meaning does not depend on subtle hue differences.

### 6. Low — Waterfall annotations and baseline labels are cramped

**Evidence:** In the lower-right card, “+60 items/hour,” “−60 items/hour,” and “0 items/hour” sit close to the top of narrow bars; the x-axis labels and down-arrow in “Capacity applied ↓” are packed along the bottom baseline.

**Why it matters:** The chart is visually compact enough that the annotations compete with the marks and require careful reading to parse as a sequence.

**Transferable remedy:** Give the waterfall a little more horizontal and vertical breathing room, place values in a dedicated annotation band, and use a simpler axis label without the directional glyph. Keep the step labels aligned to a consistent baseline and reserve the bar area for the bars themselves.

