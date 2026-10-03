# Luna text/background contrast review

Scope: the rendered `water.svg` and `microgrid.svg` artifacts under `projects/svg-quality-luna/artifacts/luna/`, their overview screenshots, the current compose synchronized SVG theme contract, and the controlled before/after fixtures under `projects/svg-text-contrast/artifacts/`. I inspected the rendered overviews and the emitted SVG/CSS; I did not infer arithmetic, interactivity, or accessibility compliance from the pictures.

I computed ratios from the declared opaque colors using relative luminance. These are nominal paint ratios; anti aliasing, font size, filters, and opacity can lower the contrast of visible pixels. The existing screenshot helper reported no direct failures in the two compact artifacts, but it returned `ok: false` because 7 water text records and 6 microgrid records were inconclusive (tspan or multicolor paint). That result is therefore evidence of incomplete coverage, not a pass.

## Severity-ranked findings

### High: navigation focus and control borders are checked against the wrong background

The current generator emits `.navigation-control rect { fill: var(--ink); stroke: var(--muted) }` and uses `var(--focus)` for the focused or pressed stroke. The navigation HUD panel has the same `var(--ink)` fill. `theme_contract.py` checks `focus` against `canvas` and `surface`, but never against `ink`, and it does not check the resting navigation border against `ink`.

This is a confirmed contract defect, with visible impact in the `world-light/after-overview.png` HUD when world navigation is shown:

* editorial light: `focus #94591c` against HUD `ink #203332` is **2.343:1** (below a 3:1 focus indicator target); `muted #586a68` against that same panel is **2.325:1**, so ordinary navigation borders are also weak;
* compact dark: the HUD panel and navigation controls use light `ink #f1f5f9`; `focus #ffcf70` is only **1.330:1**, and `muted #b8c5d2` is **1.603:1** against it.

The compact dark overview is module mode, so this dark HUD state is not visible in that particular screenshot. The ratio is nevertheless determined by the emitted theme and selector pairing. Focus should be derived or checked against the actual HUD/control fill, and the resting border needs a separate control visibility check.

### High: the focus audit substitutes the module frame for every text background

`audit_focus_readability()` obtains the fill from `.module-frame` and compares every descendant `text` node with that one color. It does not resolve the painted element behind each text run, so text over a local plaque, value surface, colored mark, filtered layer, or custom fragment can be checked against a different background from the one actually rendered. It also loops only over `.sync-module[data-focused="false"]`, skipping the focused module, and it does not inspect top-level scenario, reset, timeline, or navigation controls.

This is a confirmed audit coverage/method defect. The standard controlled after fixtures reduce the risk with explicit `text-value-*` and `surface-value-*` pairs, but the checker still cannot establish local-background correctness for arbitrary fragments. A local screenshot sampler is a better diagnostic for opaque local backgrounds, provided unsupported tspan, filter, and multicolor cases remain explicitly inconclusive.

### Medium: disabled navigation text can fall below 4.5 in the dark theme

The current CSS applies `opacity: 0.52` to `[aria-disabled="true"]` navigation controls. In the dark theme, navigation text is `on-ink #18242f` over a light HUD/control fill `ink #f1f5f9`; after the group opacity is composited over that fill, the approximate solid text becomes `#808890`, only **3.281:1** against `#f1f5f9`. The light editorial pairing (`on-ink #ffffff` over `#203332`) is approximately **4.787:1**, so it is close to the normal-text threshold even there.

The world-light screenshot visibly shows the disabled `UP` control as substantially fainter than its neighbors. The dark disabled state was not present in the compact-dark module-mode overview, so the dark result is a confirmed theme/state contract risk rather than a visible failure in that sampled frame. Disabled controls need a state-specific contrast check after compositing, or a less aggressive opacity treatment.

### Medium: current compact artifacts are older than the current token contract

The requested `water.svg` and `microgrid.svg` files still contain the old `color-mix()` soft tokens and old HUD declarations (`navigation-current-tier`, `navigation-help`, and `navigation-control text` use `var(--muted)` or `var(--surface-subtle)`). They do not contain the current `--on-ink`, `--on-ink-muted`, `--text-value-*`, or opaque generated soft-surface tokens emitted by the current scaffold.

For the old water artifact, `muted #4b6460` against the dark HUD `ink #173b38` is **1.914:1**; for old microgrid, `muted #526663` against `ink #172d2a` is **2.380:1**. Those declarations would make HUD secondary text fail if world mode exposes them. The compact overview artifacts are `data-world-mode="false"`, so this old HUD defect is not visible in their supplied screenshots. Regenerate these artifacts before treating them as evidence of the current generator.

### Low: near-threshold text has almost no margin

The controlled `near-threshold` fixture uses `#767676` on white for its base ink. The nominal ratio is **4.542:1**, only 0.042 above 4.5. This is not a confirmed ratio failure, but it is fragile under opacity, antialiasing, or any compositing change. The after fixture improves semantic value labels by assigning safe `text-value-*` tokens; the base gray remains a watch item.

## Confirmed improvements in the controlled after fixtures

* `world-light/after-overview.png` has visibly stronger HUD eyebrow, tier, handoff, and help text. The after CSS uses `on-ink #ffffff` and `on-ink-muted #ced2d2` on `ink #203332`; those ratios are **13.280:1** and **8.712:1**, respectively. The before HUD used muted/subtle surface colors directly on the dark panel and was visibly faint.
* The `light-mark` after fixture separates the raw `input-rate` mark color `#888888` from its text token. Raw gray is only **3.545:1** on white and is unsafe as ordinary text; the after input value uses `text-value-input-rate #203332`, which is **12.237:1** on the canvas and **11.043:1** against its generated value surface.
* The compact dark after fixture keeps semantic value colors while pairing them with generated surfaces. For example, `#eb9494` on `#3e3841` is **4.980:1**, `#94adeb` on `#2e3d51` is **4.960:1**, and `#c6eb94` on `#374841` is **7.250:1**. The visible module overview remains readable, although the smallest labels are still dense.
* Generated `on-ink` and `on-ink-muted` tokens fix the secondary HUD text pairing in both light and dark themes. They do not fix focus/border pairings because focus still uses the un-derived `focus` token on the HUD's `ink` fill.

## Remaining suspicions and limits

The world navigation focus ring, minimap strokes, filtered world links, `paint-order` labels, and multicolor/tspan text need rendered-state checks. I found no reproducible direct text ratio failure for the compact light module text sampled by the existing helper, but its inconclusive records and frame-background shortcut prevent a clean conclusion. The supplied overviews also do not exercise every focus, disabled, dark-world, or filtered state.

Recommendation: retain the inverse HUD foreground and separate semantic value tokens, regenerate the stale water/microgrid artifacts, and extend the contract/audit to check each text run against its actual painted local background after fill opacity and ancestor opacity are resolved. Add explicit checks for HUD resting borders, focus strokes, disabled controls, and focused modules before calling the contrast work complete.
