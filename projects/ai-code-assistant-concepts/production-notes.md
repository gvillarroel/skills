# Production Notes

## Direction

The package treats each concept as a compact visual module. The same work packet moves through every video so the audience sees a single system becoming more complete: model, billing, probability, agent loop, guardrail, harness, hook, plugin, skill, MCP, product alternatives, observability, instruction layers, tool permissions, and data governance.

## Deliberate Choices

- Runtime is 42 seconds per module to make the full set reviewable in one pass.
- Videos are silent and visual-first; every module has enough on-screen structure to stand alone.
- Exact volatile pricing and plan limits are documented in research notes rather than animated into the final frames.
- The right-side panel is consistent across videos so the left-side metaphor can vary without changing the reading path.

## Improvement Loop

The expected critique loop is:

1. Generate plans from the concept data.
2. Smoke-test representative frames for browser errors, blank frames, and composition bounds.
3. Render quick MP4s and inspect contact sheets.
4. Fix visual composition or data copy problems.
5. Render final MP4s and run ffprobe, blackdetect, freezedetect, and keyframe extraction.
6. Promote reusable lessons to the owning video workflow skill.

## Actual Validation Log

- Planned and generated fifteen per-video subfolders from one structured concept data model.
- Browser smoke validation passed across 75 representative screenshots.
- First quick MP4 review found freeze-detection failures in six structurally static modules: guardrail, plugin, skill, alternatives, instruction layers, and permissions.
- The renderer was improved with scene-local semantic motion: lane packets, install packets, skill-loading packets, pilot checklist movement, precedence sweeps, and permission indicators.
- Quick MP4 review then passed for all fifteen videos.
- Final keyframe inspection found a shared lower-third term chip colliding with the recurring work-packet label. The duplicate chip was removed because the right panel already carries the scene terms.
- Contact-sheet generation was corrected from an overlarge tile grid to a 4x2 grid so review sheets do not introduce empty black cells.
- Final renders were upgraded to 30 fps to match the workflow skill's delivery standard.
- Final MP4 review passed for all fifteen videos: each is 42.000 seconds, 1920x1080, 1260 frames, with zero black-detect and freeze-detect failures.
- Reusable lessons were promoted to `html-d3-anime-video-workflow/references/production-loop.md` and recorded in `SKILLS.md`.
