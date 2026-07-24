You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, access the network, or modify bundled
assets.

I want a restrained black-and-white pattern derived from the open Hilma af
Klint Pleiades image included with the skill. Keep the irregular loops,
calligraphic flow, and hand-drawn character; I do not want a composition of
generic circles, polygons, or other rigid geometry. Simplify it enough to work
as a small decorative motif and make it mirror-repeatable. Choose suitable
deterministic settings from the skill.

Create exactly these nonempty workspace-relative files:

- `outputs/naturalistic/pleiade-ink-mirror.svg`
- `outputs/naturalistic/pleiade-ink-mirror.json`
- `outputs/naturalistic/pleiade-ink-mirror-validation.json`

Use the bundled provenance manifest, the source ID `hilma-pleiade-14`, and the
stable pattern ID `pleiade-ink-mirror`. Validate the SVG against its report,
expected ID, `ink` mode, and `mirror` tile mode, requiring an SVG pattern
element. The SVG must remain editable vector content with no embedded raster,
script, `foreignObject`, or external reference. Finish only after every
required file exists at the exact path.
