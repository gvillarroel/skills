Use the loaded `d3-animated-svg` skill to create the exact file `outputs/agent-loop-overlay.html`.

Build a standalone HTML artifact for the canonical `d3-agent-loop-overlay` pattern. Preserve the bundled agent-loop reference image by embedding it as a PNG data URL; the delivered HTML must not depend on the skill directory, a sibling skill, a repository file, a CDN, or network access. Include the image-backed SVG, all five semantic cover regions, deterministic SVG-native reveal motion, a replay control, accessible title/description text, and a legible final state. Keep `skills/d3-animated-svg/` read-only and write only the requested output outside it.

Acceptance criteria:

- The exact output path exists and is non-empty.
- The HTML contains `data-pattern-id="d3-agent-loop-overlay"`.
- The reference image uses `data:image/png;base64,`.
- The five region IDs are present: `main-loop`, `prompt-builder`, `tool-system`, `sub-agents`, and `compaction`.
- No `http://`, `https://`, CDN, `.agents/skills`, `skills/d3-animated-svg`, or `assets/examples` dependency remains in the output.
