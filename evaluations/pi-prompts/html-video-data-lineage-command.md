Run this command first from the isolated workspace root: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/data-lineage-video/artifacts/reviews/prompt-contract-build.json`

Create a deterministic standalone HTML video scaffold for a data lineage readiness explainer.

Use the `data-lineage` scaffold. Use 12 seconds, 12 fps, and 1280x720.

Topic: Data lineage readiness
Video title: Data Lineage Readiness
Checked date: July 4, 2026

Required exact scaffold outputs:

- `projects/data-lineage-video/source/source-package.json`
- `projects/data-lineage-video/source/production-notes.md`
- `projects/data-lineage-video/src/index.html`
- `projects/data-lineage-video/src/render.mjs`
- `projects/data-lineage-video/artifacts/video-renders/draft/videos/data-lineage-readiness.mp4`
- `projects/data-lineage-video/artifacts/video-renders/draft/review/data-lineage-readiness-contact-sheet.jpg`
- `projects/data-lineage-video/artifacts/video-renders/draft/review/data-lineage-readiness-contact-sheet.json`
- `projects/data-lineage-video/artifacts/reviews/self-review.md`
- `projects/data-lineage-video/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/data-lineage-video/artifacts/reviews/render-state-check.json`.

Preserve these source facts:

- Data lineage explainers should distinguish source provenance, derived transforms, quality gates, consumer contracts, and rollback readiness.
- Schema checks, freshness windows, drift monitoring, and rollback plans should not be hidden behind a single pipeline arrow.

Preserve these visual anchors:

- source system
- lineage path
- transform rule
- schema check
- freshness window
- drift monitor
- consumer contract
- rollback route

Preserve these lineage labels:

- Product event stream
- Raw landing table
- Clean session model
- Feature aggregate
- Risk scoring table
- Analyst dashboard

Preserve these quality labels:

- schema compatibility
- freshness SLA
- distribution drift
- rollback snapshot

After the command finishes, verify the exact output paths, the wrapper report, the contact-sheet manifest, media properties, source preservation, and derived render-state check. Keep generated task files under `projects/data-lineage-video/`; do not write into the copied skill directory.
