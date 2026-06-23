# Projects

Use this directory for project-scoped work that is not meant to ship as a reusable skill or GitHub Pages example.

- Keep one subdirectory per stable lowercase hyphen-case project ID.
- Keep reusable public examples inside the owning skill's `assets/examples/` directory.
- Put project automation in `projects/<project-id>/scripts/`.
- Put generated artifacts under `projects/<project-id>/artifacts/`, grouped by type: `documents/`, `videos/`, `svgs/`, `gifs/`, `images/`, `screenshots/`, `data/`, `manifests/`, and `reviews/`.
- Keep source notes, manifests intended for review, and lightweight project documentation beside the scripts when they should remain versioned.

The `artifacts/`, `work/`, and `cache/` folders inside each project are ignored by git. Commit only reusable source, scripts, and intentionally small project notes.
