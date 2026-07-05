Validation setup: the isolated runtime shell is bash. Read this prompt from `../prompt.md`, and when reading the skill use the workspace-relative path `skills/html-d3-anime-video-workflow/SKILL.md`. Do not try absolute run-directory skill paths. Do not run PowerShell commands such as `Get-ChildItem` or directory-listing probes before reading the skill and prompt.

Required exact outputs:
- `projects/zero-padding-gray-video/source/source-package.json`
- `projects/zero-padding-gray-video/source/production-notes.md`
- `projects/zero-padding-gray-video/src/index.html`
- `projects/zero-padding-gray-video/src/render.mjs`
- `projects/zero-padding-gray-video/artifacts/video-renders/draft/videos/zero-padding-gray.mp4`
- `projects/zero-padding-gray-video/artifacts/video-renders/draft/review/zero-padding-gray-contact-sheet.jpg`
- `projects/zero-padding-gray-video/artifacts/video-renders/draft/review/zero-padding-gray-contact-sheet.json`
- `projects/zero-padding-gray-video/artifacts/reviews/self-review.md`
- `projects/zero-padding-gray-video/artifacts/reviews/prompt-contract-build.json`

Topic: Metro no-padding hierarchy
Video title: Zero Padding Gray Hierarchy
Checked date: July 4, 2026

Use 4 seconds, 6 fps, and 1280x720.
Use the `layered-architecture` scaffold.

This is a hard-edge strict-grid critique. Boxes must have no internal padding. Hierarchy levels must use different grayscale values. Do not use rounded borders, padded chips, inset bars, or nested panels to create hierarchy.

Do not list Metro audit JSON paths in the Required exact outputs. The skill wrapper should still create default `metro-style-audit.json`, `metro-composition-audit.json`, `metro-rendered-frame-audit.json`, and `metro-audit-suite.json` reports automatically because this prompt asks for hard-edge, no-padding, and grayscale hierarchy critique.

Preserve these source facts
- Boxes must have zero internal padding.
- Hierarchy levels must be separated by grayscale values, not padded interiors.
- Hues may mark semantic state, but grayscale must carry level separation.

Preserve these visual anchors
- zero internal padding
- grayscale hierarchy levels
- 0-radius rectangular panels

Preserve these layer labels
- input
- planner
- renderer
- validator
- audit
- delivery

Preserve these concern labels
- policy
- failure route
- observability
- rollout
