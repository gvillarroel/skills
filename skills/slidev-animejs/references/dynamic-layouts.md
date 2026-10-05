# Dynamic Slidev composition templates

Keep changing collections in editable data and reuse one component across counts and click states.

## Contents

- [Install the pack](#install-the-pack)
- [Select a composition](#select-a-composition)
- [Keep identities and colors stable](#keep-identities-and-colors-stable)
- [Compose richer components](#compose-richer-components)
- [Handle capacity and pages](#handle-capacity-and-pages)
- [Validate delivery](#validate-delivery)

## Install the pack

Copy [the runtime template](../assets/templates/slidev-layouts/) into the deck root. Keep the three copied runtime files unchanged: `components/SlidevLayout.vue`, `components/SlidevCollection.vue` and `lib/slidev-layouts.mjs`. Customize the wrapper, data or documented props/slots; the exact-runtime checker rejects runtime edits. Declare `@slidev/cli`, the chosen theme (`@slidev/theme-default` for the default theme), and `vue` in the deck package.

Set `fonts.sans: Open Sans` in Slidev headmatter. Preserve existing Mermaid setup; [native diagram defaults](mermaid-defaults.md) remain responsible for plain Mermaid. Use the same colorset for layouts, charts and authored PlantUML.

## Select a composition

| Mode | Geometry | Choose it for |
| --- | --- | --- |
| `columns` | Equal-width columns; contiguous input groups stack vertically and balance their item counts. | Parallel sections or a changing number of panels. |
| `grid` | Equal-width and equal-height cells, in row-major order. | Comparable components or a small dashboard. |
| `masonry-columns` | Assign each measured card to the shortest column. Preserve natural height. | Independent content with different lengths. |
| `masonry-rows` | Assign each variable-width card to the shortest horizontal row. | A collection in a literal three-row composition. |

Pass `:columns="n"` for column modes and `:rows="3"` for horizontal masonry. With fewer items on a partial page, fewer tracks are occupied; never add dummy cards to claim three populated rows. Masonry retains DOM/source order. Use a sequential diagram when relationships carry meaning.

Supply `items` as an array of objects with unique nonempty string `id` values. Built-in cards render optional `title` and `body`. Optional `category` groups related identities into one paint, and optional positive `width` supplies a preferred horizontal masonry width. Other fields reach the item slot.

Prefer the copy-ready `SlidevCollection.vue` parent for an editable collection. It supplies fixed 16px titles/14px bodies, palette-painted pagination, full-data identity allocation, actual-width column limits and a globally qualified page budget. Stage `height` excludes the pager; reserve another 36px plus a concise heading. An individually oversized card still reports failure.

Pass the complete `items`, optional `count`, `mode`, requested upper-bound `columns`, `rows`, `colorset`, `categoryOrder`, and optional desired `pageSize`. Capture via exposed `page`, `pages`, `report`, `nextPage()` and `previousPage()`. Default text cards are measured across all pages before exposing a stable partition; `data-collection-qualified` signals readiness. The optional `#item` forwards engine slot props. Custom slots need an explicit, qualified `pageSize`; their partition stays fixed and any overflow reports failure.

For visible order, prefix display titles in the wrapper; preserve original JSON titles and IDs. Use the default card body for this metadata so automatic page qualification remains available. Save `data/cards.json` and `components/CollectionStory.vue`:

```vue
<script setup>
import { computed } from 'vue'
import SlidevCollection from './SlidevCollection.vue'
import cards from '../data/cards.json'
const labeledCards = cards.map((item, index) => ({
  ...item, title: String(index + 1) + '. ' + (item.title || item.id),
}))
const props = defineProps({ mode: String, clicks: { type: Number, default: 0 } })
const counts = [3, 7, 11]
const columns = [2, 3, 4]
const step = computed(() => Math.min(2, Math.max(0, Math.floor(props.clicks))))
</script>
<template>
  <SlidevCollection :items="labeledCards" :count="counts[step]" :columns="columns[step]"
    :mode="mode" :rows="mode === 'grid' ? 2 : 3" label="Delivery collection" />
</template>
```

Register `clicks: 2` for real keyboard navigation. Set `layout: default` explicitly on the first slide and subsequent slides; the first-slide cover default can enlarge headings and push the stage/pager outside the viewport. Use a short, class-qualified heading with a fixed 28px/1.2 scale, 16px bottom margin, and no extra copy above the collection. In first-slide headmatter also declare theme/fonts; subsequent slides use:

```markdown
---
layout: default
clicks: 2
---
<h1 class="collection-heading" style="font-size:28px;line-height:1.2;margin:0 0 16px">Delivery grid</h1>
<CollectionStory mode="grid" :clicks="$clicks" />
```

Direct `SlidevLayout` control needs an identity manifest, page/pageSize and page clamping. Qualify every page and inner width.

## Keep identities and colors stable

The pack embeds the owning skill's exact solid sequence. Colorset1 starts with primary red `#9e1b32`, then the established interleaved black/grays; colorset2 explicitly selects the extended palette. The actual white canvas is excluded from categorical solids. Exhaust usable solids before outlined overflow variants. Use opaque fills and maximum-luminance-contrast black/white ink.

Keep a complete, stable `categoryOrder` of `item.category ?? item.id` across slides, including hidden/paged identities. Without it, the engine retains only each mount's first-seen registry. The parent allocates from full data before count selection. Preserve order when adding categories. Native Mermaid retains its own role/indexed-category contract.

## Compose richer components

Use `#item="{ item, index, color, style, box }"` for richer Vue content. `index` is the active input index across pages. Apply the supplied fill and maximum-contrast black/white ink to opaque labels; simple SVG marks may inherit `currentColor`. Check each label against its actual backing. A background of `currentColor` with the same text color makes text invisible. Slots own typography, paint and chart lifecycle. Use Open Sans, exact tokens and opacity 1; qualify actual computed paint.

Use `box.contentWidth` and `box.contentHeight` as the entire inner component budget. Outer `box.width`/`box.height` include padding and border. Setting an inner chart to the outer height creates measurement growth. Reserve any title/caption height inside the content budget, resize native charts after layout changes, and keep complete axes, labels and diagram semantics. Intrinsic text cards need no explicit inner height.

A dense custom slot can use fixed 16px titles/14px bodies, line-height 1.35, opaque inherited ink and zero margins. Keep type unchanged across states and qualify final export readability. Start at height 330, gap 12 and minimum height 72; prefer two rows per page for columns/grid. Engine fallback retains 20/18px; the parent uses 16/14px.

## Handle capacity and pages

Native ResizeObserver/font readiness drives measurement. Changed `capacity` reports expose fits/reasons, overflowIds/visibleIds, required dimensions, pages and configured/occupied tracks. The engine `SlidevLayout` exposes `data-layout-fits`, dimension/page/track attributes, `report` and `remeasure()`. For parent capture, wait for `data-collection-qualified=true` and require `data-collection-fits=true`/`report.fits=true`.

Require `fits: true` in every delivered state. A finite slide cannot hold an unlimited count or arbitrarily long copy. Reduce `pageSize`, widen cards, use fewer columns, or split slides while keeping every item reachable. Pagination alone cannot repair an individually oversized card or too many minimum-width columns. For three horizontal rows with longer copy, start with three items per page and wider preferred widths, clamped to the actual available width. Increase the page size only after every page passes.

Failed capacity keeps content accessible by scrolling; publication still requires fit. Debug is opt-in. Preserve supplied copy and values; never crop, discard or automatically shrink type.

## Validate delivery

Run the bundled static check before native rendering:

```powershell
uv run --script <skill-root>/scripts/check_layout_deck.py --deck deck --data data/cards.json --expect-items 11 --require-bundled-runtime
```

Adjust the data path/count to the task or omit those optional flags. The checker verifies nonempty runtime copies, CLI/theme/Vue declarations, balanced fences, unique data IDs and optional exact item count. It does not infer Slidev slide count or browser fit. Use native Slidev metadata for slides; avoid counting global headmatter separators.

Build, serve over HTTP, and inspect every count/column/page/width plus real Slidev keyboard clicks. Check actual frame/card boxes, no overlap, full glyph bounds, correct row/column membership, stable identity paint, exact palette/maximum black-white contrast and `fits=true`. Walk all pages to verify every active ID appears once. Resize the actual inner container rather than only the outer Slidev viewport, which scales a fixed slide. Check UI dark/reduced-motion states, async font/content updates and a real custom slot. Keep stage height within the slide after reserving headings and controls.

Published acceptance patterns: [slidev-animejs-dynamic-columns](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/32), [slidev-animejs-dynamic-grid](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/33), [slidev-animejs-masonry-rows](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/34), [slidev-animejs-masonry-columns](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/35). Copy the runtime pack for authoring.
