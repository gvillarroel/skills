# Star Trek atlas: direct visual application

Date: 2026-09-12. Method: direct interactive authoring with usefulcharts-style guidance and project-specific SVG composition. This is not an isolated Pi run, a Luna/Spark comparison, or evidence that the general skill has passed its release gate.

The user requested a graphic combining canonical chronology, civilizations and wars. Delivered an editable SVG, full-size PNG, zoomable searchable HTML viewer, single-page vector PDF, numbered source catalog, JSON, CSV and an offline ZIP. Authored sources are under `projects/star-trek-canonical-timeline/`; media and detailed audits are under that project's ignored `artifacts/` tree.

## Content and encoding

| Dimension | Delivered evidence |
| --- | --- |
| Main chronology | 123 historical entries |
| Ancient context | 12 entries |
| Distant future | 12 entries |
| Alternative histories | 8 separately labeled summaries |
| Total historical entries | 155, each with a screen credit and source key |
| Main subject categories | 32, mixing species, polities and other powers explicitly |
| Research catalog | 72 references; 69 cited by historical entries |
| Page | 3600 × 5800 SVG units; single-page 36 × 58 inch vector PDF |
| Typography | 18-unit body, 14-unit episode credits, 16-unit dates; scalable SVG/PDF |

Six branches use unequal widths. Chronology is read down within a branch; independent local spacing is explicitly declared. A compact Prime overview supplies the shared sequence without pretending that its intervals are equal. Color identifies subjects, while labeled diagrams express Federation founding membership, Dominion hierarchy and changing wartime alignments. The 139 manifest links include 129 reading-sequence links; they must not be described as 139 political relationships. The war panel separately states Bajoran neutrality and Son'a supply of ketracel-white.

## Critique and repairs

The official UsefulCharts Timeline of World History preview was inspected again at full page. Its condensed title, continuous cream field, light categorical colors, multiple text scales and close placement of dates, labels and explanatory fragments informed this composition.

1. The initial era-by-era layout measured 3600 × 9786. Its excessive height and empty cells made it unsuitable. Its first large browser capture failed; no visual pass is claimed for that attempted render.
2. Version 2 reduced the page to 3600 × 6156 with continuous subject histories. Its screenshot exposed a long Federation tail and empty regions below the shorter histories. The title also had overlapping text bounds.
3. Version 3 moved distant futures to a shared lower region, placed clearly separated alternative histories in released space, added a Prime overview and explained Dominion governance. The title bounds still needed repair.
4. Subsequent renders fixed the title, connected both ends of the war relation, made war bidirectional, reserved backgrounds behind joining-date labels, improved the contrast of the Cardassian side-change label and qualified the Borg membership request.
5. Content review corrected Endgame, Kaminar and the unnamed Tholian-attacked starbase. Coverage review added the Temporal Cold War, Kzinti wars and the Tzenkethi conflict. Source review replaced broad contact citations for Ferengi and Vidiian entries and added Son'a support to the war explanation.
6. Browser interaction testing caught an apostrophe escaping error in the color-key JavaScript. It was repaired before delivery. A failed intermediate interaction check is not counted as a successful run.

Final PDF proof, the complete PNG, dense details and the actual viewer were inspected. The result is a dense, readable chronological atlas with compact political diagrams. Its six-column morphology remains more regular and text-led than the braided duration bands and selective illustrations of the reference. No claim of indistinguishability is made.

## Final verification

Run sequence:

```powershell
uv run --script projects/star-trek-canonical-timeline/scripts/build_data.py
uv run --script projects/star-trek-canonical-timeline/scripts/build_dense_poster.py
uv run --script projects/star-trek-canonical-timeline/scripts/render_review.py --version final --pdf
uv run --script projects/star-trek-canonical-timeline/scripts/package_atlas.py
uv run --script projects/star-trek-canonical-timeline/scripts/verify_atlas.py
```

The final browser audit finds all 155 records, 935 text nodes, zero text intersections, zero out-of-page text boxes and zero record-envelope overflows. The independent artifact check matches the source and SVG hashes, resolves all 155 source keys, tests search, source inspection, zoom and section navigation, and observes zero JavaScript errors. PDF extraction preserves every historical title and confirms 155 source hyperlinks on one page. The final Dominion search returns 18 entries.

Repository checks also pass: `uv run --script scripts/validate-pattern-ids.py` (1222 canonical IDs), `uv run --script scripts/validate-skills.py`, `uv run --script scripts/test-skill-independence.py`, and `uv run --script scripts/check-repo-payload.py`. No canonical skill behavior, public example, Pages output, or release status is changed in this application.

Detailed evidence:

- `projects/star-trek-canonical-timeline/artifacts/reviews/final/browser-audit.json`
- `projects/star-trek-canonical-timeline/artifacts/reviews/final/verification.json`
- `projects/star-trek-canonical-timeline/artifacts/reviews/final/pdf-audit.json`
- `projects/star-trek-canonical-timeline/artifacts/reviews/final/pdf-proof.png`
- `projects/star-trek-canonical-timeline/artifacts/reviews/final/viewer-overview.png`
- `projects/star-trek-canonical-timeline/artifacts/reviews/final/viewer-reading.png`
- Retained `v2/`, `v3/` and `v4/` visual reviews in the same project review directory.

## Acceptance boundary

The artifact is delivered and its geometry, record preservation, offline behavior and export paths are verified. Screen credits and the source catalog make the factual synthesis reviewable; this is not a claim that every episode was freshly watched or every derived date has an uncontested authoritative answer.

The reference still lacks a completed semantic census under the density contract. Accordingly, 155 entries and 935 text nodes are evidence of this artifact's contents, not a measured proof that every reference-density minimum has been met. Keep usefulcharts-style in `validating`; do not promote this project as a new published pattern or a general aesthetic/isolated-runtime pass.
