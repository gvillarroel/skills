# Playfulness and composition: reference comparison

Date: 2026-09-13. Skill: `usefulcharts-style`. Case: development diagnostic visual review. Reviewer: the primary conversation assistant, using actual image input. This is informed self-review with known provenance, not a blinded authorship experiment or a new isolated runtime test.

## Decision

The five illustrated revisions remain visibly distinguishable from the initial UsefulCharts reference set. Their additional images improve recognition, thematic atmosphere and selected explanations, but do not establish equivalent exploratory composition. The largest unresolved differences are repeated list structures, separate image rails, visual references that require another lookup, and insufficiently visible connections between groups.

This finding supersedes the earlier favorable visual wording for the broader UsefulCharts reference target. The previous 3/4 illustrated reviews and three Luna discrimination runs support a narrower conclusion: body illustrations are more useful than no images or a header image alone. They do not establish convincing reference resemblance, natural discovery or exceptional image integration. Previous factual, geometry and PDF checks retain their original scope and evidence. No scores, model traces or historical artifacts were rewritten.

The skill remains **validating**. A full semantic reference-density census is still pending. No indistinguishability rate, confidence percentage or factual density ratio is inferred from visual inspection.

## Evidence and comparison basis

The four initially selected official previews were reopened directly:

- [European Royal Family Tree (West)](https://usefulcharts.com/products/european-royal-family-tree).
- [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree).
- [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history).
- [Writing Systems of the World](https://usefulcharts.com/products/writing-systems-of-the-world).

All five final project previews and their reading-size detail PNGs were also opened. A [private comparison viewer](../../projects/usefulcharts-playful/artifacts/reference-comparison/index.html) supplies selectable originals and revisions, equal-width whole posters, equal-area whole posters, body-only views and source-relative detail crops. Original previews are kept intact in ignored local artifacts and are not added to published galleries or the skill payload. Every input's dimensions and SHA-256 are recorded in the [manifest](../../projects/usefulcharts-playful/artifacts/reference-comparison/manifest.json).

Whole-width views use 650 CSS pixels per poster in the captured comparisons. Whole-area views preserve each poster's aspect ratio and use a common area that fits both columns. Body crops use the same 95% width and 86% height, starting below the first 10%. Detail crops show 45% of each source width and 24% of its height; positions differ to inspect relevant neighborhoods. These are morphology comparisons across different subjects, not equal-content benchmarks. Public preview resolution limits small-text reading, especially for the writing reference.

Twenty comparison states passed browser size checks, image loading and JavaScript checks. The viewer also passed offline and mobile overflow checks. Actual side-by-side captures inspected include BSD whole width, civilizations whole width, instruments detail, Mars equal area and starships detail. All nine standalone whole images and all five candidate detail images were directly inspected. Browser correctness does not certify the visual conclusions.

Command:

```powershell
uv run --script projects/usefulcharts-playful/scripts/build_reference_comparison.py
```

The first capture attempt hid the selection controls before selecting them and timed out. The capture automation was corrected to select the deliberately hidden controls; the final run passes 20/20 states. This was a review-viewer automation defect, not a poster defect. The final viewer's visible reset and zoom controls were exercised on mobile.

## How the references invite exploration

### Local landmarks and connected paths

In the royal genealogy, portraits sit beside particular rulers, heraldry identifies nearby kingdoms and houses, and compact relatives occupy the intervening connections. Different name treatments and selective images establish multiple entrances into one connected field. The reader can recognize a person, follow a relationship and discover another familiar figure without entering a separate picture gallery. The opening fans out; later families use the space the particular history needs.

The denomination poster presents branching as its main visual subject. Category colors continue through institution labels and connection paths. Emblems identify particular institutions. Its map and population pictograms are substantial insets: they encode geography and quantity using the same categories as the tree. Their separation is purposeful, so this reference does not support a blanket prohibition on insets.

### Comparisons that are already visible

The history timeline puts periods, transitions, event notes and selected objects into a shared temporal field. An artifact or portrait is usually a local landmark in the period it helps explain. Wider focal intervals, thin continuities, open routing space and increasingly busy later history produce varying local rhythms. The world-map backdrop creates atmosphere, but its decorative presence is not counted as extra historical knowledge.

The writing poster is a useful counterexample to equating playfulness with irregular layout. It uses a rigid matrix. The glyphs themselves are the visual data, and aligned forms support direct comparison. Its color separates writing-system families while the repeated grid makes similarities and differences inspectable. A dense table can therefore be exploratory when its cells expose comparable visual information.

These observations concern the selected references. They do not establish a universal UsefulCharts rule or prove that every illustration must be indispensable to a connection.

## Candidate findings

| Revision | What the illustration pass improved | Remaining visible difference | First structural repair indicated by the comparison |
| --- | --- | --- | --- |
| Instruments | Fifteen recognizable specimens distinguish mechanisms; the kazoo and plucked-tongue examples supply useful discoveries. | Nearly every group uses the same list-plus-right-image-rail arrangement. Specimens refer back through category codes instead of consistently sitting beside the relevant leaf. The object form is visible, but the vibrating component is generally explained in a caption. | Compose selected specimens with their exact classification leaves; show a few mechanism comparisons with component callouts, preserving the complete hierarchy and useful type size. |
| BSD | Period-inspired hardware establishes computing context; the 4.4BSD Lite inset makes three typed paths explicit. | Six separated lists dominate. Most cross-family relations require finding a numbered reference in another panel. The generic machine scenes do less to distinguish specific releases than the institution emblems do in the reference. | Make the main lineage and important code contributions visible across a continuous composition; use hardware where it explains a verified transition. Preserve the distinction between lineage and contribution. |
| Mars | Spacecraft images distinguish orbiter, cruise hardware and surface vehicle; the numeric calendar remains valid. | The largest images occupy undated guide boxes inside the calendar field. A reader must find the separate dated mission record after looking at the image. The composition alternates sparse records with large illustrated islands. | Attach selected spacecraft views to the corresponding dated records or endpoints with clear ownership. Compress vertical slack within the fixed calendar; retain honest launch gaps. |
| Civilizations | Species representatives and ships provide recognizable entrances into a dense historical inventory. | Six persistent prose columns determine the silhouette. Dark portrait cards interrupt the paper field like inserted sidebars. Neighboring columns do not share a numeric date position, so concurrent conflicts cannot be compared directly. | Recompose the central historical story around a shared calendar and selected cross-civilization relationships; preserve separate alternative histories and source uncertainty. |
| Starships | The numeric X axis, reused tracks and small endpoint images already provide a useful exploratory mechanism. Large views make several ship profiles recognizable. | Text boxes carry most visual weight. The seven large views live in two side pockets, while the twelve track images are much smaller. Viewing angles and visual weight vary; the large silhouette guide is spatially distant from many records it discusses. | Bring recognizable ship views into selected duration/endpoint groups while retaining exact X positions, shared baselines, dated evidence and all required notes. Separate physical-hull continuity from inherited names. |

The dark space theme, horizontal time axis and public-source photographs are appropriate choices. Their difference from cream-paper history posters is not by itself evidence of lower quality. The actionable problem is how image, data, labels and relationships work together.

## Density and reading effort

The references often combine identity, category, time and relationships within a compact local unit. Several candidate units contain substantial prose but expose fewer relationships through their placement. This is a difference between visible relational structure and textual volume; it is not a counted semantic-density result.

The preceding [independent checks](../../projects/usefulcharts-playful/artifacts/reviews/independent-checks.json) record a 39.72% canvas-area increase for instruments and BSD with unchanged selected record counts. Their record count per unit area consequently falls by approximately 28.43%. This is relative to their own prior versions, not to UsefulCharts. Civilizations also grows; Mars and starships retain their previous canvas areas. Image area and a space background cannot be counted as additional factual density.

Some visual gaps are legitimate: numeric time must preserve empty years, and absent dates must stay unknown. The indicated repair is better use of vertical tracks, locally owned explanatory images and supported relationships. It is not arbitrary time compression, invented information or smaller text.

## What the previous evaluator missed

The current helper verifies declarations, IDs, coverage, evidence hashes and score thresholds. Those checks are useful, but a valid binding in JSON does not prove that a reader sees the relationship on the printed page. A recognizable image in a body panel can still require a distant lookup. A discovery prompt can be answerable while the answer remains mostly buried in prose.

The earlier three-candidate discrimination task compared an image-free poster, a header-only image and a body-illustrated poster. It did not compare against UsefulCharts, compare two fully illustrated alternatives, or test whether relationships become easier to discover. Three successful repetitions of that narrow task do not widen its scope.

This comparison identifies unresolved acceptance questions: which specific visual relationship supplies the discovery, how the reader moves from image to fact, whether page and detail scales support the same story, and which conspicuous structural cues still reveal the candidate's different composition. They are diagnostic findings in this record; no skill runtime or evaluation algorithm was modified in this analysis-only pass. A future change must be separately validated rather than relabelling this self-review as an isolated forward test.

## Authorship judgment and limits

With provenance already known, the reviewer can identify consistent distinguishing cues across all five revisions: repeated panels and image rails, long prose columns, dark rectangular art cards, separate large-image galleries, and weaker visual continuity between important groups. Hiding only a logo would leave those cues. This supports the judgment that the revisions are currently distinguishable; it is not a measured claim that an unfamiliar observer will classify every anonymous sample correctly.

The resulting assessment is materially stricter than the earlier illustrated-coverage pass. The new posters are more approachable than their prior image-free versions, while convincing UsefulCharts-like exploratory composition remains unresolved.

Repository validation after recording this review passed: `validate-pattern-ids.py`, `validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py` and `git diff --check`. The loopback comparison URL returned HTTP 200. No diagram, canonical skill runtime, local skill installation or published example was changed by this analysis pass.
