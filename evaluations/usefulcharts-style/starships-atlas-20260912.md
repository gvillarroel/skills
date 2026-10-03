# Star Trek spacecraft atlas: direct application

Date: 2026-09-12. Method: direct Codex authoring with usefulcharts-style guidance, web research and project-specific vector composition. This is an application review, not an isolated Pi test, a model comparison or a skill release certification.

The requested reading question is which Star Trek spacecraft were built and used, and in what years. The unit is an individual physical vessel, including selected prototypes, a probe and uniquely identified unnamed craft. The atlas separates construction observations, launch or commissioning, selected active years, supported service intervals, loss, preservation and temporal displacement. It does not infer the factory production dates of an entire class from the oldest or newest vessel seen.

Authored sources: `projects/star-trek-starships/`. Generated deliverables and detailed evidence: that project's ignored `artifacts/` directory.

## Content and encoding

| Dimension | Delivered evidence |
| --- | --- |
| Individual spacecraft | 79, with unique IDs and per-record sources |
| Origin/operator groups | 11: Earth, Federation, Vulcan, Andorian, Klingon, Romulan, Reman, Cardassian, Dominion, Borg and Ferengi |
| Documented launch/commission/build dates | 29; 50 remain unstated |
| Construction observations | Four records; these are observations of building, not manufacturing durations |
| Fleet-lane year marks | 143, independently checked against actual SVG geometry |
| Dated spans | Seven supported service/mission bands and two qualified uncertainty ranges |
| Relationships | 21 typed data relations; the viewer exposes the related vessels. The poster has Enterprise name succession and eight explanatory mini diagrams |
| Illustrations | Nine original simplified Enterprise dorsal identifiers |
| Sources | 79 record sources and two additional official cross-checks |
| Page | 3600 × 6698 SVG units; one vector PDF page, approximately 36 × 66.98 inches |
| Display/export | Searchable offline HTML, editable SVG, full PNG, vector PDF, JSON, CSV and portable ZIP |

Each of five chronological chapters has its own explicitly labeled linear year scale. The three left chapters and two right chapters retain a consistent ship/date/consequence reading order. Selected dates joined by dashes do not assert uninterrupted operation. Museum years and time-jump arrivals outside the chapter are labeled separately. A renamed Titan-A/Enterprise-G is one record; the two modern Defiants and the two Delta Flyers are distinct records.

The source field called `design` contains 65 distinct class/type descriptors. That is not a count of 65 formally established Star Trek ship classes. Operator colors describe the stated origin/group and do not claim constant ownership over a vessel's entire history.

## Factual review and corrections

- Used episode-cited Memory Alpha pages and official StarTrek.com cross-checks. A source inventory records URLs actually returned by the research index. It establishes retrieval rather than live HTTP health; some direct pages were unavailable to the browser's text retrieval. Screen trails make the synthesis reviewable without claiming every episode was freshly watched.
- Added documented 2102 commissioning for Horizon, 2245 launch for Constellation, 2285 launch for Excelsior and 2372 launch for Valiant. Construction remains a distinct field.
- Rejected unsupported conversion of promotional/reference dates into Prime launch dates for Enterprise-F, Titan-A and Cerritos. Farragut's alternate-future dedication material does not silently establish its Prime launch.
- Kept Enterprise-D's 2363–2371 service separate from its 2401 reactivation and later preservation. Discovery's 2258 departure is not joined to 3189 by a solid service band. Voyager's replaced 2404 future is not its Prime return date.
- Corrected Gr'oth to the dated 2268 tribble incident, D'kyr to the individually attested 2152 ship and Friendship 1 to registry UESPA-1. Corrected source aliases that otherwise named a character, ship class or different article.
- NX-Delta's 2144–2145 and Athena's disputed 3190s calendar placement use hatched uncertainty ranges. They are not exact launch intervals. The earliest and latest selected sightings do not become asserted construction/retirement endpoints.

## Critique and repair

The UsefulCharts Timeline of World History reference was inspected alongside the complete project render. Its continuous field, strong title hierarchy, close association of dates and explanations, restrained colored bands and informative local branches guide the comparison.

1. The first poster had two intersecting text pairs: the title and the final modern-axis tick labels. It also used overly similar principal ship silhouettes. Version 1 evidence remains retained.
2. Version 2 uses a single clear title, removes a redundant overlapping axis label and gives all nine hero vessels separate hull/nacelle geometry. The illustration caption explicitly limits them to schematic identification; they do not compare physical size or claim engineering accuracy.
3. The initial body made important ship identity relationships too dependent on prose. The final revision adds eight small diagrams distinguishing test programs, sister ships, replacement hulls, prototype/production, name succession and renaming. Intermediate Voyager name bearers are explicitly omitted, rather than implying J immediately succeeds A.
4. The viewer now links related vessels, clears incompatible filters on a relationship jump and brings the evidence panel into view. Search, selection and interaction screenshots were inspected at reading size. The full PNG, fleet details, diagram strip and rendered PDF proof were inspected.
5. The independent verifier caught a hash mismatch caused by hashing LF source text before Windows wrote CRLF file bytes. The manifest now hashes the actual delivered SVG bytes. A later verifier locator matched both the ship heading and the newly added related-vessels heading; it was corrected to target the ship heading specifically. Those intermediate failures are not successful checks.

The result is a dense illustrated fleet register with chronological marks and compact relationship diagrams. The reference remains more varied in band width, branch placement and contextual imagery. This artifact's repeated rows are effective for comparing vessel evidence, but they do not establish aesthetic indistinguishability. The nine drawings are simplified identifiers, not detailed reproductions of studio ship assets.

## Final verification

```powershell
uv run --script projects/star-trek-starships/scripts/build_data.py
uv run --script projects/star-trek-starships/scripts/build_atlas.py
uv run --script projects/star-trek-starships/scripts/render_atlas.py --version final --pdf
uv run --script projects/star-trek-starships/scripts/verify_atlas.py
uv run --script projects/star-trek-starships/scripts/package_atlas.py
```

Final independent artifact verification passes: all 79 records survive SVG, JSON, CSV and PDF export. The actual browser-measured geometry of all 143 year marks and nine ranges matches the declared chapter scales. The browser audit reports 744 text nodes, zero text intersections, zero text outside the page and zero record-envelope overflows. Every PDF record has the correct URI over its corresponding location; all three PDF fonts are embedded.

Offline viewer checks cover registry search, origin/operator and date-evidence filters, record selection, dating qualifications, related-vessel navigation, zoom, chapter navigation, keyboard selection, compact layout and relative companion downloads. No JavaScript errors or HTTP requests occur during the offline test.

Repository validation also passes: `uv run --script scripts/validate-pattern-ids.py` (1,222 canonical IDs), `uv run --script scripts/validate-skills.py`, `uv run --script scripts/test-skill-independence.py`, `uv run --script scripts/check-repo-payload.py` and the scoped `git diff --check`. The ZIP integrity and per-file hashes pass for all 14 packaged files. Unrelated working-tree changes are preserved; this project does not publish Pages or modify a skill runtime payload.

Final artifact hashes:

- Source JSON SHA-256: `6a71ba662c7e9c3f1da59f37ff6d99baf738eaeb4d643911f3ef89f058cbdef8`
- SVG SHA-256: `82e3b58f6cd8c59946d0046f599f25b4ee4ed45c31a28fc8ff2ac1914598d325`

Retained evidence includes `artifacts/reviews/v1/`, `v2/` and `final/`. The final folder contains the browser audit, independently checked verification JSON, PDF audit/proof, full/detail renders and viewer screenshots. The portable archive contains the final compact reports, not bulky capture tiles or reference images.

## Acceptance boundary

The artifact's content inventory, date encodings, source linkage, exports and offline interactions pass their checks. The source qualifications remain part of its factual meaning. It is a selected fleet history, not an exhaustive catalog of every background vessel or a class-production chronology.

The reference still lacks a complete semantic census under the skill's density contract. The 79 records, 143 geometric year marks, relationship diagrams and explanatory notes establish what this atlas contains; they do not prove every reference-density minimum is met. Keep usefulcharts-style in `validating`. No general skill behavior changes, isolated runtime pass, public example or new reusable/published pattern is claimed by this project application.
