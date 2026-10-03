# Blog knowledge atlas validation

Date: 2026-09-13. Applied `usefulcharts-style` to the public source material in `C:/Users/villa/dev/blog`. The source repository is read-only for this task. The output language follows the repository's English artifact convention.

The delivered set has three posters: a 60-milestone shared numerical history with ten additional comparisons/interpretations; a 29-record agent mechanism map; and a 31-record evaluation and skill-evolution map. The total is 130 editorial records, 35 illustration placements, 12 distinct generated conceptual specimens and 130 clickable PDF source annotations. The combined PDF has three pages. These counts describe the artifact inventory, not independent facts or reference-density parity.

The first chronological design was rejected for whitespace and excessive vertical extent. Further revisions corrected image/text and image/route collisions, clarified typed graph relations, repeated the same environment in the two experimental arms, and joined retained evidence to all grading layers. The evaluation article is attributed to Gerardo Villarroel after checking its actual frontmatter. The history article is by Guillermo Villarroel.

The actual SVG whole/detail previews and Poppler-rendered PDF pages were inspected. The gallery passes six poster/viewport checks across desktop (1440 × 1020) and mobile (390 × 844), including search, record-source association, fitting, zoom, case switching and hash reload. The mobile fitting defect in the first viewer was fixed by permitting zoom below 10% for the giant timeline.

The final text palette has at least 4.5:1 contrast against the paper and each color's own tinted panel. The browser uses explicit image hit regions because the retained, viewport-cropped source sheet otherwise exposes misleading native SVG click bounds; real clicks on all three posters now select the correct image owner on both screen sizes. Final integrity checks hash actual SVG file bytes rather than newline-normalized strings.

The final application preserves the existing skill's unresolved reference target: no semantic census, density-parity result or blind authorship claim is reported. This task changes no skill runtime behavior, so no new isolated `pi` run or skill promotion is claimed. The general skill remains `validating` for the gates already recorded in `SKILLS.md`.

## Reproduction commands

Run from the skills repository root:

```powershell
uv run --script projects/blog-knowledge-atlas/scripts/extract_sources.py
uv run --script projects/blog-knowledge-atlas/scripts/record_provenance.py
uv run --script projects/blog-knowledge-atlas/scripts/check_source_links.py
uv run --script projects/blog-knowledge-atlas/scripts/build_atlas.py
uv run --script projects/blog-knowledge-atlas/scripts/render_and_check.py
uv run --script projects/blog-knowledge-atlas/scripts/package_atlas.py
uv run --script projects/blog-knowledge-atlas/scripts/audit_gallery.py
uv run --script projects/blog-knowledge-atlas/scripts/audit_final.py
```

Rendering requires the generated sheet in `artifacts/images/specimen-sheet.png`; its provenance, source hash, normalized generation brief and twelve SVG crop viewports are retained in `artifacts/images/provenance.json`. No raster edits were applied. Source integrity checks confirm that all six inspected source files retain their extracted hashes. The two public blog URLs, the public context file and four primary references returned HTTP 200 on 13 September 2026.

Machine and visual evidence is retained in the ignored project artifacts: `reviews/technical.json`, `reviews/gallery-audit.json`, `reviews/source-integrity.json`, `reviews/source-links.json`, `reviews/visual-review.md`, each poster's `checks.json`, and actual PDF/PNG outputs. The first rejected previews remain under `reviews/iteration-1/`.

Repository validation also passes:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

No published example, Pages catalog or skill installation changed. The generated media and source extracts remain under this project's ignored `artifacts/` directory.
