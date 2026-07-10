Write `projects/zero-padding-transition/transition-plan.json`.

Isolated-run constraint: do not run workspace discovery, output search, or orientation commands such as `ls`, `find`, `rg --files`, `pwd`, `Get-ChildItem`, or `Test-Path`. Read `../prompt.md`, read only directly required skill files by known path if needed, then write the exact requested output path.

Create a validation-ready transition plan for these exact scenes:

- `s01-source-board`: a hard-edge board with a queued work packet
- `s02-validation-board`: a hard-edge board where the same work packet becomes validated evidence

Persistent element name: `work packet`
Required transition count: 1
Required anchors: `zero internal padding`, `grayscale hierarchy levels`, `0-radius rectangular panels`

The transition must preserve square/0-radius geometry, zero internal padding for masks and panels, and distinct grayscale hierarchy levels through outgoing, midpoint, and incoming frames. Hue may mark semantic state, but hierarchy must be visible through grayscale values.

After writing the JSON, validate it with:

```powershell
uv run --script skills/scene-transition-director/scripts/validate_transition_plan.py --plan projects/zero-padding-transition/transition-plan.json --expect-transitions 1 --expect-persistent-name "work packet" --expect-chain s01-source-board,s02-validation-board --require-anchor "zero internal padding" --require-anchor "grayscale hierarchy levels" --require-anchor "0-radius rectangular panels" --require-semantic-fields --require-square-edge-style --require-zero-box-padding --require-grayscale-hierarchy
```
