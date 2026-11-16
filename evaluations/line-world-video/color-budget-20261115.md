# Rejected pixel-budget interpretation — 2026-11-15

**Archived, rejected interpretation.** The user clarified that the desired
balance is a flexible composition hierarchy, not a pixel percentage, background
split or numerical pass criterion. Version 0.13.1 removes this checker, tests,
quantitative policy and its invocation from the runtime package. Preserve the
following results as implementation history, not current acceptance criteria.
See [the corrected direction](color-hierarchy-20261115.md).

The initial 0.13.0 experiment translated the preceding color preference into
an area budget. It recorded that interpretation in the primary instructions,
color reference, dedicated-producer contract and shared JSON policy. The white floor
is 70%; gray/red shares are upper budgets rather than mandatory ink quotas.
Sparse line art can contain more white. Extra diagram hues share the existing
30% nonwhite allowance, with documented necessity and stable category mapping.
Photos and logos retain their original identity.

## Implementation and deterministic checks

`skills/line-world-video/scripts/color_balance.py` measures rendered pixel area
with NumPy and FFmpeg. It accepts an image, a default one-fps video sample, or
`--every-frame`; it composites transparency on white. It records raw fractions,
means, worst frames, actual frame coverage and budget overages. Near-white,
neutral and red-hue classifier thresholds are explicit in
`assets/palettes/video-balance.json`. Other hues are reported without inferring
asset provenance or whether another categorical color is justified. Authored
colorset2 use requires `--extra-color-reason`. Palette necessity, useful content,
label readability and geometry require their existing separate checks.

An unchanged repeat verifies the input, script, policy and result hashes and
reuses the report. The full disk measurements live under `result`; the compact
stdout summary exposes the same principal fields directly plus `reused`.
The primary delivery procedure now includes the area check after rendering.
All five visual producer bundles ship identical budget JSON and guidance.
The adapter retains its unchanged native production contract.

Run the specific checks with:

```powershell
uv run --script skills/line-world-video/scripts/test_color_balance.py
uv run --script skills/line-world-video/scripts/color_balance.py --video projects/cuda-alexnet-vids/artifacts/videos/cuda-alexnet-final.mp4 --every-frame --output projects/line-world-video/artifacts/color-balance/cuda-alexnet.json
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

Seven new deterministic tests pass: exact reference fractions, sparse-white
allowance, separate gray/red/white overages, charcoal/orange classification,
transparent composition, a 30-frame excess-red interval in a 90-frame movie,
hash-bound cache/result corruption/source-change rejection, exact CLI outputs
and colorset2-reason handling. Some methods combine related assertions.

The first CLI path fixture sat exactly at 10% authored red and returned diagnostic
exit 2 after raster resampling. That was a test-boundary issue, not a weakened
production limit. The path/reason test was moved inside the budget (80/12/8),
while the direct exact 70/20/10 pixel test remains unchanged. The reference now
explains edge filtering and recommends a small composition margin. Preserve the
initial failed test outcome; it is not included in the final passing count.

## Isolated forward test

Final run `line-world-color-budget-20261115` passes strict runtime validation
with all six exact outputs, valid events, zero tool errors and an unchanged
117-file payload. The model is the recorded account exception
`openai-codex/gpt-6.1-sol`, medium thinking, because Spark is unavailable.
The runtime digest before/after is
`2f5aef9b119405c6b48f0fe726ffd211b4ef4244507d4faf5511c46892338e0f`.

The trace reads only the canonical prompt, entrypoint, compact color-priority
reference and its own negative report. It does not read helper internals,
acceptance examples, sibling skills or repository/project context. The evaluator
independently inspected both PNGs and their reports: balanced authored 72/19/9
measures 71.875/19.0625/9.0625% and passes; excess-red authored 50/20/30 measures
exactly 50/20/30% and fails the white floor and red cap. The repeated balanced
check records genuine `reused: true`. Its notes correctly separate diagram
palette necessity, natural asset hues, content and readability from area checks.

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-color-budget.md --mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium --run-id line-world-color-budget-20261115 --expect-output frames/balanced.png --expect-output frames/excess-red.png --expect-output reports/balanced.json --expect-output reports/excess-red.json --expect-output reports/reuse.json --expect-output notes.md
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/line-world-color-budget-20261115/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/line-world-color-budget-20261115/read-surface.json
```

## Existing native-film audit

The previously delivered native stream-copy movie remains bound to SHA-256
`6ce267121fef869e4f0dbef8d0fbe840f4c6fde3086159485839c228a527bdb1`.
The new area checker covers all **6099 encoded frames**, with zero budget
violations. Mean measured shares are 93.4786% white, 5.3150% grayscale,
0.5589% red and 0.6475% other. The least-white frame still has **86.3776% white**
at 100.566667 seconds. Maximum grayscale is 10.9271%, maximum red is 2.6306%.
Other hues include the preserved portraits and brand artwork. These pixel
statistics do not imply any newly authored colorset2 categories.

The actual encoded scan passed and its unchanged repeat reused the verified
report. No new native edit/export or timing change was necessary for this
policy update. The original editable-project archive remains the reproducible
0.12.4 delivery; the new standalone plugin is 0.13.0. Do not describe the old
movie as newly rendered with this release. Existing presence, cue, media,
matrix and visual-review evidence remains in the prior release record.

## Package and repository gates

The 0.13.0 archive has 297 files and 5,126,643 uncompressed payload bytes.
Portable ZIP SHA-256:
`5bedf2f25efc423f458911c5b829aa168e40cb34c4e5ada89c264249488b5ae7`.
Marketplace ZIP SHA-256:
`a8ef8a5c9eadbbf3b1c4756410fb1002bcc2eec92a6963be84f33c3d1f7d6348`.
Task-local native Codex installation, six-skill discovery, schema validation,
archive/installed/canonical byte parity and all eight installed utility runners
pass **72 tests**. The verifier also checks the identical budget JSON in every
visual producer. Missing-runtime negative rejection remains covered. No global
native activation or account publication is claimed.

Both source bundles pass bounded local sync: 117/18 files verified, 6/0 changed.
Pattern IDs (1348), independence and payload gates pass. Global structure and
standard sync retain the same four unrelated semantic reference-route findings
documented in the preceding release. The primary stays `validating` for its
previous broader generated-layout limit; the new area mechanism and its scoped
forward test pass. No acceptance gallery or Pages publication changed.
