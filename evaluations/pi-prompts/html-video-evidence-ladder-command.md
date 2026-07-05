Run this command first from the isolated workspace root: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/evidence-ladder-video/artifacts/reviews/prompt-contract-build.json`

Create a deterministic standalone HTML video scaffold for a research-backed recommendation explainer.

Use the `evidence-ladder` scaffold. Use 12 seconds, 12 fps, and 1280x720.

Topic: Research-backed recommendation
Video title: Evidence Ladder For Research Claims
Checked date: July 4, 2026

Required exact scaffold outputs:

- `projects/evidence-ladder-video/source/source-package.json`
- `projects/evidence-ladder-video/source/production-notes.md`
- `projects/evidence-ladder-video/src/index.html`
- `projects/evidence-ladder-video/src/render.mjs`
- `projects/evidence-ladder-video/artifacts/video-renders/draft/videos/evidence-ladder-research.mp4`
- `projects/evidence-ladder-video/artifacts/video-renders/draft/review/evidence-ladder-research-contact-sheet.jpg`
- `projects/evidence-ladder-video/artifacts/video-renders/draft/review/evidence-ladder-research-contact-sheet.json`
- `projects/evidence-ladder-video/artifacts/reviews/self-review.md`
- `projects/evidence-ladder-video/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/evidence-ladder-video/artifacts/reviews/render-state-check.json`.

Preserve these source facts:

- A research video should state the claim before ranking source support.
- Counterevidence and source gaps must remain visible before confidence rises.
- Recommendation timing should follow evidence, not precede it.

Preserve these visual anchors:

- working claim
- evidence tiers
- counterevidence
- source gap
- confidence meter
- uncertainty meter
- recommendation

Preserve these claim labels:

- Adopt the method
- baseline holds
- risk remains
- recommend pilot

Preserve these evidence labels:

- primary study
- replication
- field data
- expert review
- mixed results
- missing long-term data

After the command finishes, verify the exact output paths, the wrapper report, the contact-sheet manifest, media properties, source preservation, and derived render-state check. Keep generated task files under `projects/evidence-ladder-video/`; do not write into the copied skill directory.
