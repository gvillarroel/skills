# Qualitative composition color hierarchy — 2026-11-15

The user clarified that the desired balance describes overall composition:
predominantly white, then grays for structure/information, with selective red
emphasis. It is not a required background split, exact percentage or pixel
quota. Colorset2 is exceptional when multiple entities, independent lines or
categories need additional distinct identities.

Plugin **0.13.1** applies that corrected direction in the primary entrypoint,
color reference and dedicated-producer contract. All five visual bundles ship
the same small `assets/palettes/video-color-direction.json`, with qualitative
roles rather than numerical limits. Primary red remains `#9e1b32`; dark-gray
secondary comparisons, white faces/red edges and explicit solid-red objects
with white internal labels remain available. Pink object backgrounds remain
excluded by the existing video style. Photo/brand identity is preserved.

The earlier 0.13.0 pixel-budget interpretation was rejected. Its script, tests,
numerical policy and delivery invocation were removed from the canonical bundle
and repository-local installation. The package verifier explicitly rejects those
retired files. Keep the [rejected experiment](color-budget-20261115.md) and its
artifacts as history, not current acceptance criteria. Existing empty-content,
label/guide geometry and actual native export checks remain separate mechanisms.

## Isolated forward validation

Run `line-world-color-hierarchy-20261115` passes strict runtime validation with
all four exact outputs, valid JSON events, zero tool errors and an unchanged
115-file skill payload. The model is the recorded exception
`openai-codex/gpt-6.1-sol`, medium thinking, because Spark is unavailable for
this account. The payload digest before/after is
`227fe1f8aec41e313e4f2cec9f524a41833368a658da7990563bf4970fee341b`.

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-color-hierarchy.md --mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium --run-id line-world-color-hierarchy-20261115 --expect-output figure.html --expect-output decisions.json --expect-output focus-check.json --expect-output preview.png
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/line-world-color-hierarchy-20261115/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/line-world-color-hierarchy-20261115/read-surface.json
```

The task creates five synthetic independent sensor histories, including crossing
lines. The output uses bundled colorset2 blue/green/purple/orange/ochre for stable
entity identities, gray axes/context/labels, a white composition and a separate
primary-red point beside the current endpoint. Direct endpoint labels establish
an essential legend without a decorative panel. The source exposes deterministic
reading states; the standalone inspector passes all three states and repeat
seeking with no label/stroke/guide conflicts or browser errors.

The evaluator independently inspected the actual 1920×1080 preview and recorded
decisions: the five histories are distinguishable, labels and units are readable,
crossings remain honest, the red cue is beside the selected series, and no
numerical color criterion or background division was invented. The decisions
correctly disclose synthetic data and static/sample-limited verification; no
new native video, voice or continuous-motion proof is claimed. Only the prompt,
entrypoint, specific compact references, palette, small helper/runtime and own
outputs were read; no sibling skills, examples or repository context were used.

This is a scoped qualitative diagnostic, not a proof of every possible
composition, color-vision condition or future generation. The primary skill
retains its previously recorded broader composition-generalization limit.

## Native package and local installation

```powershell
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
uv run --script projects/line-world-video/scripts/sync_local.py
```

The 0.13.1 portable ZIP contains 295 files and 5,114,579 uncompressed payload
bytes. Its SHA-256 is
`1c41de17f8a519a96989af544467a38e1f96fd12ee43de6a98465e166e603282`.
The marketplace ZIP SHA-256 is
`537f3845d46ed7fa1967469e007ddd5355a675943899c2dbe0d1d7345626c546`.
Actual clean extraction, schema validation, task-local Codex install, all six
native skill registrations and exact archive/installed/canonical parity pass.
The identical qualitative policy is checked in all five visual producer copies,
and the retired pixel-quota implementation is absent. Seven installed utility
runners pass **65 tests**. No global activation or account publication is claimed.

Bounded local refresh verifies 115 primary and 18 adapter files, copying 4/0
changed files after explicitly removing the three retired local resources.
Pattern IDs (1348), independence and payload gates pass. Global structure and
standard sync retain the same four unrelated semantic reference-route findings
in curate-semantic-model, extract-ontologies and extract-with-ontology. No Pages
example changed. The existing native CUDA/AlexNet movie/source archive remains
the reproducible 0.12.4 production; this update corrects plugin guidance and
does not claim a new video export.
