# Evaluation and repair

## Browser geometry

```sh
uv run --script <skill-dir>/scripts/audit_chart.py chart.svg --report audit.json --png preview.png
```

The audit uses Playwright and an available Chromium browser. It first tries Playwright's bundled Chromium, then installed Chrome and Edge. If none is available, install the Playwright browser using the same environment (`uv run --with playwright python -m playwright install chromium`) or pass `--browser-executable` to a known compatible browser. Follow the workspace's installation scope. An unavailable browser is an infrastructure failure, not a visual pass.

The audit recomputes actual text bounding boxes in Chromium, tests node label containment, unrelated text overlap, page bounds, missing text, and text/fill contrast. With `--source`, it checks the source revision hash before comparing visible records and numeric dates. A stale SVG from a failed rerender must not pass against a newer brief. It also checks the SVG's declared node and edge inventory against rendered DOM elements. The JSON records measured boxes and findings. A preview is written even when geometry fails so the issue can be diagnosed.

At page scale, check the whole silhouette. At full resolution, inspect the densest branch, each union, route crossings, long names, and footnotes. Treat a zero-finding report as necessary evidence; judge visual character separately.

## Visual rubric

Score each dimension 0–4: 0 absent/broken, 1 weak, 2 adequate with clear issues, 3 good, 4 convincing. Use prose explaining the observation. This is an anchored reviewer rubric, not a pixel similarity metric.

| Dimension | A strong result |
| --- | --- |
| Poster composition | A clear entrance, coherent subject-specific atmosphere, connected visual neighborhoods and a quiet footer; the information remains the main attraction. |
| Spatial hierarchy | Origins above descendants; stable neighboring branches; meaningful focal labels; no arbitrary scattering. |
| Connection semantics | Every relation matches the source; unions and influence differ; endpoints visible; crossings unambiguous. |
| Color system | Stable named categories carried through fills and paths; readable contrast; neither rainbow decoration nor an undifferentiated graph. |
| Typography | Condensed title, compact clear names, subordinate dates, consistent wrapping, no crowding. |
| Density and rhythm | At least the reference's useful knowledge density in each information layer, with balanced readable distribution across the full page and its thirds; no reliance on decorative fill or unreadable type. |
| Reference-family resemblance | Comparable silhouette, branching/interval structure, visual hierarchy, and rhythm to the chosen reference family. |
| Fidelity and usability | All required display entities/relations preserved; any authorized selection traceable to the original source pool; exact outputs; editable SVG; full-size inspection and provenance available. |
| Illustrated explanation | Recognizable subject images are attached to the facts they explain, visible at their placed size, and distributed through the body; a banner or decorative background alone is insufficient. |
| Playful discovery | Concrete visual comparisons, varied meaningful focal points and source-answerable reading invitations make the subject rewarding to explore without reducing accuracy or density. |

The old 24/32 aggregate threshold was insufficient: the user rejected examples that passed it because their visual morphology was still clearly deficient. Keep the dimensions as critique prompts, but **do not average correctness into aesthetic acceptance**. Resemblance, composition, density/rhythm, and typography must each be convincing when compared beside the reference. Record visible differences, even when all technical checks pass. A high total cannot compensate for a wrong parent, hidden label, repetitive matrix, or empty poster.

For a playful or illustrated brief, use [illustrated discovery](illustrated-discovery.md) before accepting any construction route. The illustration and discovery dimensions are required, independent gates. Reject a technically clean text catalog, images confined to the header, generic repeated symbols standing in for distinct objects, or artwork so small that its subject cannot be recognized. A request for a sober technical diagram may use a different visual contract; do not impose playfulness on unrelated briefs.

For a reference-level or requested indistinguishable result, apply [visible discovery](visible-discovery.md). Keep illustrated coverage, exploratory composition and reference-target acceptance separate. Coverage cannot establish image ownership or reading structure. Require at least three source-answerable routes through actual rendered elements, two operation types and two body regions, plus whole/detail reference evidence. Compare fully illustrated alternatives; a picture-versus-no-picture control is too easy for this gate. Normalize reference and candidate to the same display width or area and compare both whole pages and relative detail crops. Record whether the reviewer can still distinguish them by layout, rhythm, emphasis, illustration texture, or chronology structure. A self-review is not a blinded panel experiment. Do not report indistinguishability from self-assigned rubric scores.

Apply [the knowledge-density protocol](knowledge-density.md) as a separate minimum. Count distinct supported records, typed relations, temporal anchors and contextual claims consistently on both sides. The candidate's conservative density must reach at least 1.0 times the reference for every layer; extra names or text cannot compensate for missing context or relationships. Use the same full-poster area and inspect upper/middle/lower distribution. OCR, pixel coverage and colored area are only screening evidence. An unknown or incomplete semantic census cannot yield a numerical density pass.

## Repair order

Start by checking whether the poster answers the working brief's reading question and retains all required information. If the explanation is unsupported or the selected scope is misleading, repair that before polishing geometry. Revisit [information and editorial planning](information-design.md) when needed.

1. Fix missing/incorrect relationships and invalid chronology.
2. Improve branch ordering and row/column allocation.
3. Clear node/connector collisions; reserve routing corridors.
4. Widen or wrap labels; enlarge the page if necessary.
5. Strengthen hierarchy and compact excessive empty areas.
6. Integrate recognizable images, meaningful visual comparisons and reading invitations; remeasure their complete footprints and reclaim released space.
7. Adjust color/contrast and footer details; inspect the actual final artwork and PDF again.

## Acceptance and remaining work

Accept a revision only after checking the final rendered files in three separate areas:

- **Content:** the displayed story answers the intended question; required facts remain present; relationships, dates, unknowns and source scope are represented faithfully.
- **Technical execution:** final source and image match, required files exist, labels and routes remain legible, and material geometry findings are resolved.
- **Visual quality:** whole-page composition and dense details support the requested aesthetic, the knowledge-density minimum is met, and material weaknesses identified by the comparison are resolved. Record any unresolved criterion as remaining work rather than an accepted exception.

Continue when the critique identifies a concrete improvement. An unchanged rerender, a high average rubric score or a fixed number of iterations is not progress or an acceptance gate. If the available data, tools or rendering approach prevent the requested quality, state the specific unresolved limitation and keep that part of the result pending. An explicit limitation does not convert a failed criterion into a pass. Never substitute self-review for evidence of requested indistinguishability.

Do not claim broad skill reliability from the fixture alone. Evaluate a different subject, a different layout family, long-label and invalid-input boundaries, and independent agent-created briefs. Retain failed runs and distinguish agent/skill problems from browser or provider failures.
