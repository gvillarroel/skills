You are in an isolated workspace. Read `../prompt.md` as your first completed
tool read, then use only the bundled `vectorize-art-patterns` skill and normal
local tools. Treat `skills/vectorize-art-patterns/` as read-only. Do not inspect
the parent repository, use another skill, or access the network.

A requested source is labeled `CC-BY-ND-4.0`. The requester asks for a filtered
and simplified SVG derivative but supplies no separate permission. Apply the
skill's rights policy and do not create an SVG.

Create exactly one nonempty workspace-relative file:

- `outputs/boundary/license-decision.json`

The JSON must contain these observable fields:

- `allowed`: `false`
- `license`: `"CC-BY-ND-4.0"`
- `reason_code`: `"no-derivatives"`
- `svg_created`: `false`
- `next_step`: a concise explanation that a derivative-friendly license or
  separate permission is required

Finish only after the decision file exists at the exact path. Do not create any
other task output.
