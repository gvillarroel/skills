# Evaluation and repair

## Browser geometry

```sh
uv run --script <skill-dir>/scripts/audit_chart.py chart.svg --report audit.json --png preview.png
```

The audit uses Playwright and an available Chromium browser. It first tries Playwright's bundled Chromium, then installed Chrome and Edge. If none is available, install the Playwright browser using the same environment (`uv run --with playwright python -m playwright install chromium`) or pass `--browser-executable` to a known compatible browser. Follow the workspace's installation scope. An unavailable browser is an infrastructure failure, not a visual pass.

The audit recomputes actual text bounding boxes in Chromium, tests node label containment, unrelated text overlap, page bounds, missing text, and text/fill contrast. It also checks the SVG's declared node and edge inventory against rendered DOM elements. The JSON records measured boxes and findings. A preview is written even when geometry fails so the issue can be diagnosed.

At page scale, check the whole silhouette. At full resolution, inspect the densest branch, each union, route crossings, long names, and footnotes. Treat a zero-finding report as necessary evidence; judge visual character separately.

## Visual rubric

Score each dimension 0–4: 0 absent/broken, 1 weak, 2 adequate with clear issues, 3 good, 4 convincing. Use prose explaining the observation. This is an anchored reviewer rubric, not a pixel similarity metric.

| Dimension | A strong result |
| --- | --- |
| Poster composition | Shallow strong title, one coherent light field, diagram dominates the page, footer remains quiet. |
| Spatial hierarchy | Origins above descendants; stable neighboring branches; meaningful focal labels; no arbitrary scattering. |
| Connection semantics | Every relation matches the source; unions and influence differ; endpoints visible; crossings unambiguous. |
| Color system | Stable named categories carried through fills and paths; readable contrast; neither rainbow decoration nor an undifferentiated graph. |
| Typography | Condensed title, compact clear names, subordinate dates, consistent wrapping, no crowding. |
| Density and rhythm | Enough detail to read as an information poster, balanced open corridors, few accidental blank zones. |
| Reference-family resemblance | Comparable silhouette, branching/interval structure, visual hierarchy, and rhythm to the chosen reference family. |
| Fidelity and usability | All source entities/relations preserved; exact outputs; editable SVG; full-size inspection and source provenance available. |

A release-quality example should score at least 24/32 with no dimension below 2, and have zero unresolved factual, label-occlusion, graph, or contrast failures. A high total cannot compensate for a wrong parent or a hidden label. Record missing capabilities (for example portraits, historical source verification, or very large intermarriage networks).

## Repair order

1. Fix missing/incorrect relationships and invalid chronology.
2. Improve branch ordering and row/column allocation.
3. Clear node/connector collisions; reserve routing corridors.
4. Widen or wrap labels; enlarge the page if necessary.
5. Strengthen hierarchy and compact excessive empty areas.
6. Adjust color/contrast and footer details.

Do not claim broad skill reliability from the fixture alone. Evaluate a different subject, a different layout family, long-label and invalid-input boundaries, and independent agent-created briefs. Retain failed runs and distinguish agent/skill problems from browser or provider failures.
