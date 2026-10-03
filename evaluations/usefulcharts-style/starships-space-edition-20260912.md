# Star Trek spacecraft: space edition — 2026-09-12

## Delivered application

The user's art direction requested photographed/model-referenced generated ships, a dark space atmosphere and right-facing spacecraft at the end of dated wakes. The separate space edition preserves the previous cream edition and its evidence. The output lives under `projects/star-trek-starships/artifacts/space-edition/` with SVG, PNG, single-page PDF, offline viewer, source ledger, JSON/CSV, accepted artwork, prompts and an integrity-checked archive.

The canvas is 3600 × 7760, with a 36 × 77.60-inch PDF. Six generated ship assets depict Enterprise NX-01, Voyager, Defiant, Discovery, Protostar and a Klingon Bird-of-Prey. Voyager also anchors the opening reading example. The atmospheric background was generated separately. All factual text and time geometry remain editable vector elements. The six illustrations are selected focal subjects; the other records do not have new individual pictures.

The canonical source JSON is unchanged: SHA-256 `6a71ba662c7e9c3f1da59f37ff6d99baf738eaeb4d643911f3ef89f058cbdef8`. It contains 79 individual spacecraft, 11 origin/operator groups, 29 documented launch/commission/build years, 50 unstated launch years, four construction observations and 21 typed relations. The poster preserves every record's note, credit and registry. Eight relationship stories and the nine-vessel Enterprise name chain remain visible.

## Artwork process and provenance

The built-in image generator was used on visually inspected photographs of physical/studio models and a production screencap. The accepted prompt pack is `projects/star-trek-starships/design/image-generation.json` and is copied to the deliverable's `data/image-generation.json`. It records photographic source pages, accepted prompts, Discovery's edit sequence, original generated-file paths and portable asset paths. One supplementary NX dorsal reference has an unretained original URL; that limitation is explicit in the manifest. Reference photos are not included in the archive.

The first Enterprise-D and NCC-1701 generation attempts were output-moderation blocked and produced no assets. These subjects were not retried after their blocks. An image labeled Protostar by search was visually identified as Voyager-A and rejected before generation. Discovery's first two outputs contained painted checkerboard backgrounds; the first also retained model support artifacts. A subsequent edit produced a solid-black background without the support. Accepted Discovery, Protostar and Bird-of-Prey images are RGB on black, not transparent. NX, Voyager and Defiant have actual alpha channels. The SVG embeds the unmodified final generated assets with screen blending; the composite was inspected in PNG and PDF.

## Retained critique and revision

- **Space v1:** 3600 × 9543. Rejected for excessive vertical space, an incorrectly letterboxed nebula, eight text intersections and 79 name-envelope violations. Generated ships already improved subject recognition compared with the previous schematic drawings.
- **Space v2:** 3600 × 7712. Inline source credits, tighter prose and corrected baselines reduce length without removing records or shrinking type. Full-height background fixes the letterboxing. One mixed-font paragraph still overlaps, and focal art needs more breathing room.
- **Space v3:** 3600 × 7760. Larger image/note clearance and a visible gap before source credits remove all text collisions. Bounded tapered glow strengthens verified wakes. An independent background audit finds 21 contrast shortfalls under bright stars and one hero image/date footprint collision; retain the rejected audit and screenshots under `reviews/v3/`.
- **Final:** stronger dark compositing raises the worst complete-text-box contrast from 2.74:1 to 4.74:1; the hero image moves clear of its endpoint label. Geometry, actual date mappings, image/text envelopes, data and offline interactions pass. The author opened the final header, chapter detail, full PDF proof, overview and compact viewer screenshots after rendering.

The visual improvement is subject-specific: a dark navy/violet field, bright category colors, recognizable generated ships, rightward movement cues and luminous duration marks. The camera angles remain approximate rather than identical, the body still uses two regular chronology columns, and the many records with only one known year correctly remain point marks. Six pictures do not constitute a fully illustrated 79-ship catalog.

Knowledge-density parity is **not certified**. All facts are preserved, but this canvas is 15.86% larger than the 3600 × 6698 cream edition; raw records per full-page area consequently decrease by 13.69%. It is 18.68% shorter than the first space revision. Decorative art does not count as additional knowledge, and the earlier missing complete UsefulCharts semantic census remains unresolved. No indistinguishability or aesthetic-equivalence claim is made.

## Verification

The final browser audit measures 624 text nodes: zero text/text collisions, zero outside bounds and zero record-envelope overflow. The separate image audit measures seven image placements with zero image/text collisions and tests the actual composited background behind every complete text bounding box, including bright stars. Every contrast exceeds 4.74:1; the acceptance thresholds are 4.5 for small text and 3 for large text.

The independent artifact verifier checks all 143 date symbols and 40 temporal spans: seven supported service/mission wakes, 31 broken observation spans and two uncertainty ranges. It independently calculates positions from chapter scales and verifies each pictured ship's endpoint binding. Unknown launch dates remain unknown; Discovery's centuries-long time jump is not drawn as a service interval.

The one-page PDF preserves every name, registry, note and credit. All 79 record areas link to their correct source. Three TrueType fonts are embedded; a Type 3 fallback includes actual embedded glyph drawing streams. The verifier explicitly handles the latter instead of mistaking its absence of a font file for a missing font. Offline search, date/operator filters, linked records, zoom, chapter navigation, keyboard activation, compact layout and relative downloads pass without browser errors or HTTP requests.

```powershell
uv run --script projects/star-trek-starships/scripts/build_space_atlas.py
uv run --script projects/star-trek-starships/scripts/render_atlas.py --space --version final --pdf
uv run --script projects/star-trek-starships/scripts/verify_atlas.py --space
uv run --script projects/star-trek-starships/scripts/audit_space_art.py
uv run --script projects/star-trek-starships/scripts/package_atlas.py --space
```

The original commands retain their original output root when `--space` is omitted. Reusable art-direction decisions are promoted into `skills/usefulcharts-style/references/thematic-art-direction.md`; isolated planning validation is recorded separately in `thematic-art-direction-20260912.md`. The visual application is direct author work, not an isolated-model quality result. The overall skill remains `validating`.
