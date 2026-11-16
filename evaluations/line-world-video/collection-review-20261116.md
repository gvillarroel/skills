# Collection review and plugin polish, 2026-11-16

Release candidate: Line World Video 0.26.0. The primary skill remains
`validating` for its established broad-generation and native-delivery limits.
This pass reviews the maintained film collection and promotes reusable fixes
into the canonical skill and dedicated plugin producers.

## Scope

The initial local inventory contains 32 standalone movie files, 30 unique
digests. Eight current demonstrations are selected explicitly; the final
collection includes five revised deliveries plus unchanged Reddit and the two
feature demonstrations, with 29 historical files retained as references.
An encoded archive scan is distinct from a manual scene review. Intermediate
quality-pass atlas renders are build output, not newly selected deliveries.

See the [project review and current movie index](../../projects/line-world-quality-review/review.md).
The local collection report preserves exact hashes, current/reference roles,
frame counts, source-specific checks, effect proofs and operator note status.
No new native Google Vids or HyperFrames completion is inferred.

## Retained findings and corrections

The baseline review found small portrait captions, inactive original-photo
focus, long static graphs and stale delivery links. Increasing caption size
first exposed an Ian Buck line overlap; spacing was corrected and the actual
source was re-audited. Atlas quantity flights crossed its pie legend. The guide
and secondary points now take clear paths with frame-internal lanes, and the
guide shrinks during travel.

The actual atlas focus plan had 136 windows but zero intervals longer than two
seconds because semantic row holds were divided by pane visits. The correction
keeps the complete row focus across linked representations. Actual target-pixel
inspection then found four invisible traces inside thicker red quantitative
marks. A white inset trace fixes contrast while preserving source width and
endpoints. These failed reports remain in local artifacts.

Native SVG fitting also revealed small glyphs, name/value overlap after enlarging
treemap labels, and an axis-unit collision. Recomposition and actual glyph-size
measurement resolve those cases. The final atlas source audit passes with zero
findings and zero typography warnings. Original paper ink stays outside words
and annotated figures; source attribution is enlarged and long holds animate
only the existing safe margin emphasis.
Actual encoded visual review additionally caught pink/obscured native nodes:
Mermaid's important node-fill CSS overrode the animation clone's ordinary
transparent-fill declaration. The runtime now protects its own transparent fill
and stroke, and the inspector rejects an opaque emphasis layer even if it moves.
The linked category map now uses white outlined group surfaces with exact
proportional geometry, supporting the requested predominantly white composition.

Strict byte equality over SVG screenshots produced sparse repeat differences
with identical geometry and computed paint: up to 42/255 on 21 edge pixels in
one target. The inspector now reports exact equality and bounds a separate
sparse edge allowance; uniform interior, large, geometry and paint changes
still fail. Positive and negative pixel fixtures test that distinction.

## Final validation

- All eight current movies pass their encoded and source-specific checks and
  have frozen observations for all 63 scenes. Current coverage is 31,881 frames;
  the complete 37-file archive coverage is 180,857 frame instances and 35 unique
  movie digests. No current frame fails the content-presence gate.
- Nine reference entries retain findings: one intentional voice-only source
  (6,234 low-content frames) and eight superseded visual/utility renders with
  258 low-content frames in total. They are never selected as current deliveries.
- The selected eight utility suites pass 73 tests: focus motion 14, scene effects
  5, collection review 4, atlas reading 4, single-film review 6, photo focus 15,
  paper motion 10 and paper preparation/player 15. The paper pixel test proves
  only the existing safe emphasis ink moves while original source pixels stay
  unchanged. Positive/negative tests cover opaque emphasis and antialiasing.
- The final exact-source isolated cohort passes 2/2 strict JSON runs with exact
  output paths, correct observed model, zero tool errors, a clean read surface
  and an unchanged 158-file runtime payload. Four earlier passing candidate
  runs remain recorded separately; only the two release runs match final bytes.
  The independent scene-effects artifact was inspected and preserves the
  authored renderer, stable reading label, parent-clock offsets and cache rules.
- The recorded model exception is `openai-codex/gpt-6.1-sol --thinking medium`
  because Spark is unavailable. The broader primary skill remains `validating`.
- The portable/native package verifies against its schema, exact archive/source
  parity and the real Codex 0.167.0 loader. All six skills install and register
  in an isolated task-local home with zero model turns. The package has 354 files.
  An initial direct verifier invocation ran before its schema cache existed;
  the normal ordered verification pipeline materialized the schema and passed.
- Fresh local Chrome verifies HTTP access, correct file sizes, 1080p metadata,
  seeking and actual muted playback for all eight movies. This is local playback,
  not a Google Vids cloud playback claim or a new audio listening pass.
- Repeating the complete collection review reuses all 37 content scans and
  1,280 gallery frames with zero newly captured gallery frames. Source and
  supplemental effect receipts are reused by their actual digests. No model
  call is made by these utilities.
- The three narrated visual revisions preserve the approved AAC payloads
  exactly. CUDA retains its two extra final hold frames; no approved audio tail
  is trimmed. Reddit and both feature-demo movie bytes remain unchanged.
- Root pattern-ID, independence and payload gates pass. Root validation retains
  only four pre-existing unrelated semantic reference-route findings. The clean
  publication worktree passes the pattern-ID, skill, independence and payload
  gates separately before the authorized push.

The [compact evidence record](collection-review-20261116.json) contains exact
movie/source/audio/archive digests, case identities and counts. Bulky reports,
frames, traces, playback receipts and failed visual passes remain under local
project artifacts/evaluation runs. Source-specific audits and the declared
focus inventory do not prove independent speech alignment or broad generation
quality for every possible input. Review reuse is qualified with separate
composition and review directories. The existing native Vids upload limitation
remains explicit; these revised movies are local assemblies.

## Repeated commands

```powershell
uv run --script skills/line-world-video/scripts/review_collection.py --manifest projects/line-world-quality-review/collection.json --output projects/line-world-quality-review/artifacts/current --include-reference --jobs 3
uv run --script projects/line-world-quality-review/scripts/apply_observations.py
uv run --script projects/line-world-quality-review/scripts/check_playback.py
uv run --script projects/line-world-quality-review/scripts/summarize_review.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

Final forward runs:

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-collection-review-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-line-world-0260-release-collection --expect-output artifacts/film.mp4 --expect-output artifacts/collection.json --expect-output artifacts/reviews/summary.json --expect-output artifacts/reviews/index.html --expect-output-json-field artifacts/reviews/summary.json::ok=true --expect-output-json-field artifacts/reviews/summary.json::deliveryReady=false
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-scene-effects-naturalistic.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-line-world-0260-release-effects --expect-output artifacts/scene.html --expect-output artifacts/motion-review.json --expect-output artifacts/reading.png --expect-output-json-field artifacts/motion-review.json::ok=true
```

Both release event streams also pass `summarize-pi-json-events.py` with
`--require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error`.
No GitHub Pages example source or catalog changed in this pass.
