# Editable collection slides

Prepare a Slidev deck at `deck/` that an editor can reuse for changing numbers of content cards. Write `deck/slides.md`, `deck/package.json`, `deck/components/CollectionStory.vue`, `deck/data/cards.json`, and `deliverables/layout-review.md`, plus any supporting runtime files the deck needs. Use the loaded skill's established default colors and typography. The package must declare Slidev, the default theme, and any other runtime dependencies needed by the components. The evaluator will supply dependencies and build/render the result; do not install dependencies or run a build in this authoring pass.

Make exactly four slides, each using the same data-driven CollectionStory component with a different composition:

1. Equal-width columns with an editable column count.
2. An equal-cell grid with an editable column count.
3. Horizontal masonry arranged in exactly three rows, with variable card widths.
4. Vertical masonry arranged in columns, with variable card heights.

The first state of every slide contains three cards. The first and second Slidev clicks grow the collection to seven and eleven cards. For the column-based compositions, the three states use two, three and four columns respectively. Horizontal masonry keeps exactly three rows. At narrower available widths, preserve readable minimum card sizes and use explicit pagination if content cannot fit. Keep every card available; do not silently clip or discard overflow. Provide accessible pagination controls named Previous page and Next page when the selected layout needs multiple pages.

Use one complete, persistent identity list for all eleven cards, including cards not currently visible. Store the editable data in `deck/data/cards.json`. Give the cards stable IDs `card-01` through `card-11` and these titles, in order: Intake, Scope, Research, Draft, Diagram, Review, Revise, Check, Approve, Publish, Archive. Give each card a short explanatory body, varying its length from one to three brief sentences (at most 25 words per body) so the masonry geometry has a purpose. Reusing a card in another slide, changing its order, and paging must preserve its color.

Keep content and layout settings editable as ordinary data and component props. Avoid hardcoding separate rectangles or a unique layout for each card count. The delivered deck must remain usable with the loaded skill's reusable layout machinery. Use explicit labels or numbering to preserve reading order when visual packing changes.

In the review file, identify the selected palette, the data/identity contract, the difference between the two masonry directions, how overflow is exposed, and the local build/check commands. State which verification you actually performed; do not claim browser rendering in this authoring pass.

Treat `skills/slidev-animejs/` as read-only and keep generated files outside it. Use only this loaded skill and normal local tools. Do not read acceptance examples, other skills, repository documents, or files outside this isolated workspace. Do not publish anything.
