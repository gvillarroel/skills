# Built Pages Visual Review

The final locally built Pages outputs pass the independent browser review on
2026-10-03: **zero layout, paint, control-contrast or source-copy findings**.
The review serves `dist/pages/` over a local HTTP server and uses installed
Microsoft Edge through Playwright. It checks 1440 px desktop and 390 px mobile
viewports and waits two animation frames before screenshots.

| Output | Evidence |
| --- | --- |
| Main catalog | 14 discoverable cards; borderless cards; 14/14 filled badges have maximum-contrast white text; zero horizontal overflow |
| D3 colorset1 | 225 SVG cards; 7,498 eligible filled marks; zero decorative filled-mark outlines or static decorative alpha; visible text uses exact black/white |
| D3 colorset2 | Same 225-card/7,498-mark checks; zero paint or layout findings |
| D3 cartogram | Five distinct opaque, borderless region fills in both palettes; geometry retains the value scaling |
| D3 Category Burst | Nine distinct filled nodes; zero separate `fill="none"` circular rims or filter overlays; eight meaningful relationship spokes remain |
| Three.js | 24 rendered scenes; no authored `EdgesGeometry` overlays; replay works; 25/25 filled control labels pass actual-background contrast |
| Procedural SVG | 66 cards; 645/645 family, primary, metadata, signature and card-control text checks pass; directly rendered sequencer/stagger SVGs have borderless fills and black/white labels |
| Vector galleries | Masterpiece and abstract-map pages remain readable at both widths; paired source/geometry and map path preservation are covered by the fixture evidence |
| Source copies | 206/206 copies match exact bytes or documented Pages transformations; embedded D3 logo vendor runtime remains byte-for-byte preserved |

Manual screenshot inspection covered the catalog, both Category Burst palette
versions, the expanded procedural family browser, the mobile procedural page,
the Three.js cube and the abstract maps. It inspected the full visible result,
including separate line geometry surrounding filled marks. This caught the
Category Burst satellite rims that a filled-mark-only DOM check had missed.
Those decorative rims, the guide ring and drop shadow were removed from the
owning builder and fixture. The updated direct assertion prevents that blind
spot while preserving connectors, open line geometry and physical lighting.

The initial Pages review also found five procedural chrome contrast failures:
four family counts and the primary replay label used black over red or maroon
fills. The reusable gallery generator now assigns unique solid family colors
and the exact `textOnFill` black/white mapping; the primary replay label is
white over red and maroon hover paint. The final checks include inherited and
alpha-composited backgrounds, so transparent child labels cannot bypass the
contrast check. These initial findings are retained here as resolved findings;
the screenshots and detailed JSON now show the final state.

Source preservation accounts for the builder's pinned CDN substitutions,
metadata/favicon injection where applicable, and trailing-whitespace
normalization. These intentional transformations are evaluated against the
actual builder functions rather than misreported as source mutations. This
review verifies local Pages output and does not claim remote deployment.

```powershell
uv run --script projects/custom-solid-style/scripts/review_built_pages.py
uv run --script projects/custom-solid-style/scripts/audit_galleries.py
uv run --script projects/custom-solid-style/scripts/check_custom_styles.py
uv run --script projects/custom-solid-style/scripts/check_alpha_and_chrome.py
uv run --script projects/custom-solid-style/scripts/check_overflow_boundaries.py
```

The compact [machine-readable review](pages-review-20261003.json) records every
page, viewport and final gate. Detailed control rows, source-copy rows and large
screenshots remain locally under
`projects/solid-colorset-style/artifacts/reviews/` and
`projects/solid-colorset-style/artifacts/screenshots/pages/`.
The [custom renderer evidence](../custom-solid-style/validation-20261003.md)
records the isolated runs, deterministic checks, exact payload identities,
retained failures and limitations.
