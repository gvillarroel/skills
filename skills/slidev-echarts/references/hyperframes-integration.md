# HyperFrames inside Slidev

## Contents

[Install](#copy-and-install) · [Clicks](#clicks-activity-and-static-states) · [Scenes](#composition-and-color-contract) · [Cells](#dynamic-layout-cells-and-qualification)

Embed an explanatory HTML scene in a slide or qualified layout cell. It uses the official `@hyperframes/player` **0.8.134** web component, local HyperFrames core **0.8.134**, and GSAP **3.14.2**. The optional `hyperframes-explainer` companion can create richer scenes; the starter is standalone.

## Copy and install

For a **new deck**, run:

```powershell
uv run --script <skill-root>/scripts/scaffold_hyperframes_deck.py --deck deck
```

`--config story.json` merges overrides for titles/cues/palette/layout/body into the [default JSON](../assets/templates/slidev-hyperframes-starter/data/hyperframes-story.json). It writes the three-slide Story/data/slides/package/Vite inputs, local font/Mermaid setup, complete runtime packs and sibling `deliverables/hyperframes-review.md`. It runs static checks only. Identical existing files are accepted; differing planned files fail before writes. Edit JSON seconds directly; a new cue count also needs both frontmatter click counts set to length minus one. Integrate existing decks manually below.

Copy `assets/templates/slidev-hyperframes/` into the deck root, retaining every runtime resource. Customize a separate wrapper/scene folder; skip acceptance fixtures.

```powershell
Copy-Item <skill-root>/assets/templates/slidev-hyperframes/* <deck-root>/ -Recurse -Force
```

Use Node 24. Merge [starter package pins](../assets/templates/slidev-hyperframes-starter/package.json), preserving dependencies/theme/lock policy. Vite 8.0.16, UnoCSS 66.7.2 and lightningcss 1.32.0 prevent CLI 52.16 minifier drift. HTTP-only decks can omit the HTML plugin/script. Scaffolds pin Mermaid 11.15.0/types 52.16.0 and wire plain fences to the JSON colorset and Open Sans.

Merge this conditional plugin into `vite.config.ts`, preserving existing setup. Vite serves the copied `public/` folder.

```ts
import { defineConfig } from 'vite'
import { hyperframesBuildPlugins } from './lib/hyperframes-vite'
export default defineConfig({ plugins: [...hyperframesBuildPlugins()] })
```

Run `npm run build:html` for **`dist/slidev.html`**, with inlined JavaScript/CSS/fallback font. `slidev export` has no HTML format. Normal builds serve compositions/resources over HTTP.

## Clicks, activity and static states

Declare the click count and pass `$clicks` directly. Cue entries are seconds, including the initial state; forward/backward clicks seek the same timeline. Step indices clamp to the first/last cue; invalid seconds are rejected.

```md
---
theme: default
layout: default
wakeLock: false
fonts:
  sans: Open Sans
  provider: none
---

<h1 style="font-size:28px">Valve-controlled transport</h1>

---
layout: default
clicks: 2
---

<HyperframeSlide :step="$clicks" :cue-times="[0, 4, 9]" :height="330" />
```

`playing` defaults to `false`, so each cue remains a deterministic explanatory frame. Set `:playing="true"` only for intentional playback. The wrapper pauses inactive slides, hidden documents, reduced-motion playback, and unmounted players. On reentry it reapplies the current cue. No `isCustomElement` setting is needed.

For ready-made Play/Pause controls use the copied **HyperframePreview**. It owns paused preview state, leave reset, palette-derived control contrast and reduced-motion disabling. Static/noninteractive/file states omit live controls. Its `height` is scene-only: the 38 px control row plus 10 px gap need **48 extra px**. Prefer qualified **330 px hero / 210 px compact scenes**; a live hero needs 378 px below the heading. In Markdown:

```vue
<HyperframePreview :step="$clicks" :cue-times="[0,4,9]" :height="330" />
```

Preview forwards core props except its own `playing`; cues default to `[0,4,9]`. `controls=false` omits its row. Core events/message slots and paint-qualified ref methods are forwarded. In a Vue adapter declare a `step` prop and pass `:step="step"`; Markdown supplies `$clicks`. If retaining custom controls around the core, reset their playing ref with `onSlideLeave` and reserve their own row.

For adaptive sizing, observe a fixed-budget container using **`ResizeObserverEntry.contentRect`** or padding-adjusted `clientWidth/clientHeight`. **Never feed `getBoundingClientRect()` into CSS dimensions**: Slidev scales that rectangle. Reserve controls/captions before player height; never shrink fonts or CSS-scale content to fit.

Use an explicit static state for export/capture:

```vue
<HyperframeSlide :static="true" :export-time="9" :height="330" />
```

Noninteractive Slidev render contexts also use `exportTime`; use explicit `static` for requested exports. Wait for `[data-ready="true"]`: timeline/assets, fonts, cue and native paints must be ready.

Core props: `src`, `step`, `cueTimes`, `active`, `playing`, `height`, `colorset`, `static`, `exportTime`, `label`, `poster`. Defaults: starter, step 0, `[0,3,6,9]`, auto activity, paused, 330 px, colorset1, export 9. Height is positive/finite; explicit activity still obeys visibility. Events: `ready({time,duration,sourceKind})`, `timeupdate(seconds)`, `error(message)`. Ref: paint-qualified `seek(seconds)`, `play()`, `pause()`, `getPlayer()`. Manual seek stays paused and resets on cue/source/activity changes.

`.hyperframe-slide` reports `data-ready/status/time/paused/source-kind/colorset/static`; status is loading/ready/error. Message slots: `#loading({status})`, `#error({message})`, `#fallback({time,colorset,label})`.

## Composition and color contract

The starter has a 12-second paused GSAP timeline; live and SVG fallback use the same pure `sceneState(seconds)` model: fill 0%, 20%, 70% at 0, 4, 9 seconds. Inspect `[data-scene-mark]` values `tank`, `tank-fill`, `level-readout`, `valve-readout`, `transport`, `parcel` and actual scene state, independently of host attributes.

Default to colorset1; select colorset2 explicitly. The starter loads its local palette and **Open Sans** inside the iframe, with opaque solids and maximum black/white contrast. Host CSS cannot style it. Add local font subsets for other scripts. Licenses accompany assets; copy minified vendor code without reading/editing it.

Copy an independently generated scene's **complete** resource folder into `public/<scene>/`; pass `src="<scene>/index.html"`. Preserve root `data-composition-id`, `data-width`, `data-height`, duration, and paused GSAP registration under matching `window.__timelines[id]`. Keep a pure seek-safe state function. New default HTML/SVG loads local Open Sans and the selected palette inside the scene. Preserve user styles/media; the wrapper changes only the starter's palette query.

Same-origin HTML uses checked fetch + official `srcdoc`. `<base>` preserves local assets, resolving existing bases against the original URL. Local `runtime-src` runs before body scripts, avoiding remote fallback. Read source queries via **`new URL(document.baseURI).searchParams`**; `location` is the host. External origins are outside this recipe. Raw paused-GSAP explainer CLI 0.8.111 scenes were probed without upgrades/style changes.

Relative public sources resolve through `import.meta.env.BASE_URL`, supporting nested Pages and `--base ./`. An explicit `/...` stays origin-root. Serve live builds over HTTP.

On **`file://`**, the single-file build bypasses fetch/player creation for same-model static SVG + inline Open Sans. No live playback is promised. Custom scenes need an inlined `poster` data URL or `#fallback`; otherwise an accessible HTTP instruction appears. Relative posters may need external files. Report offline limits.

## Dynamic-layout cells and qualification

Read [dynamic composition templates](dynamic-layouts.md) for the collection contract. Custom `#item` content owns its fixed, qualified page size. Use the slot's **`box.contentWidth` / `box.contentHeight`**, subtracting title/caption space; outer `box.height` includes card padding. Preview needs 48 px beyond scene height; this recipe reserves another 32 px for the title.

```vue
<SlidevCollection :items="items" :columns="2" :page-size="2" :height="330" :min-item-width="330" :min-item-height="320">
  <template #item="{ item, box }">
    <h3 style="font-size:16px;margin:0 0 8px">{{ item.title }}</h3>
    <HyperframePreview src="hyperframes/starter.html?compact=1" :step="step"
      :cue-times="[0,4,9]" :height="Math.min(210, box.contentHeight - 80)" />
  </template>
</SlidevCollection>
```

Qualify the custom page size at the actual narrow width; reduce to one column/page when needed. The compact scene is authored at **420×260**, with 24 px labels; maintain at least **245×152 CSS px** of actual content so text stays at least 14 px. Prefer 300–420 px wide cells. The full scene is 720×400 with 22 px labels; it needs at least 459×255 px. Keep complete glyphs within the scene and all card content within the Slidev frame. Do not accept transform fitting if labels become unreadable.

Run the bundled static check, both builds, and native inspection:

```powershell
uv run --script <skill-root>/scripts/check_hyperframes_deck.py --deck <deck-root> --require-bundled-runtime --direct-open
npm --prefix <deck-root> run build
npm --prefix <deck-root> run build:html
```

Serve the SPA; inspect forward/back cues, reentry, inactive pause, resize, fonts, reduced motion, paint and zero errors/remote requests. Verify readiness, actual fill/readout, every page and unobstructed controls at scaled/narrow widths. Open `dist/slidev.html` directly and verify fallback time, font, full labels and custom offline behavior.

Published: [slidev-echarts-hyperframes](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/42), [slidev-echarts-hyperframes-cells](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/43), [slidev-echarts-hyperframes-export](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/44).
