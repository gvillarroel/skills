# Cross-family visual revision

Date: 2026-09-11 (work continued after midnight UTC on September 12).
Skill: `usefulcharts-style`. Status: validating.

## Preserved v11 baseline

The published runtime contains 55 files, SHA-256
`dcbbe7a98e22b1fd0c8aaec2b4065ded565d2ef9edcab31c8d7d37aecb4ecaa9`.
The institution cohort passed 3/3 strict image-capable GPT-5.5 runs, as recorded in
[the institutional revision](institution-revision-20260911.md). That result did
not establish broader visual quality. Three additional first runs were executed
in fresh isolated runtime-only workspaces:

| Run | Model | Strict outcome | Artifact review |
| --- | --- | --- | --- |
| `usefulcharts-cohorts-v11-20260911-gpt55-1` | `openai-codex/gpt-5.5` | Fail: one imprint-length tool error; all six outputs present | Reject visually: a 1600 × 1900 page leaves large empty gutters around 19 people. The extra purple category is unrequested, but the source's overlapping transitive descendant rules also make the final generation's category ambiguous; see the prompt correction below. |
| `usefulcharts-transport-v11-20260911-gpt55-1` | `openai-codex/gpt-5.5` | Pass; all six outputs present | Reject visually: 15 phases become long wide ribbons on an 1800 × 2400 page. Rotated labels and excessive gaps weaken small-museum readability. Strict execution success is not a visual pass. |
| `usefulcharts-boundary-v11-20260911-spark-1` | `openai-codex/gpt-5.3-codex-spark` | Pass; both required JSON outputs present | The diagnostic requests the missing `unknown-42` parent and does not substitute the known unrelated person. No final SVG is requested or needed. |

Both GPT-5.5 traces include supported preview reads; Spark is retained for the
nonimage boundary case. The scoped vision-model exception was recorded in
`SKILLS.md` before the image-dependent tests. The baseline workspaces and event
logs are preserved under `evaluations/runs/`; subsequent author repairs do not
change these outputs.

Commands use `scripts/run-pi-skill-eval.py usefulcharts-style`, `--mode json
--strict`, `--forbid-event-command-regex "(?i)\bgit\s"`, the corresponding
`--model`, `--run-id` and `--prompt-file`, `--timeout-seconds 600`, and an
`--expect-output` argument for every path in each prompt. Prompts are
`evaluations/pi-prompts/usefulcharts-cohorts.md`,
`evaluations/pi-prompts/usefulcharts-generalization.md`, and
`evaluations/pi-prompts/usefulcharts-boundary.md` respectively. Each run's exact
invocation and original harness results are retained in its run folder.

## Repair under validation

Review of the genealogy prompt found an evaluator defect: "Nella and her
descendants" and "Cedric/Ines's descendants" overlap after Leda and Simon marry.
The fresh prompt now lists all 19 category memberships explicitly. Do not score
the earlier category choice as an unambiguous model error, or silently apply
the corrected prompt retroactively. Its strict imprint failure and sparse
visual composition remain directly observed. The raw run retains its original
prompt. This correction changes task data precision, not the implementation
recipe or required outputs.

Measure small genealogical cohorts from actual partner units and wrapped names.
Use larger default typography and bounded generation gaps instead of stretching
a small family across a mural. Preserve each declared category through marriages.
Add a compact numeric chronology with thin duration ribbons, adjacent horizontal
names and visible endpoint dates. Its label bounds remain separate from duration
bounds so independent time verification still uses the actual interval geometry.

These are reusable composition changes, not edits to failed evaluation outputs.
The changes were tested in fresh runs as recorded below. Dense reference parity
remains open, so the skill retains its validating status.

## Development and final runtime evidence

The 60-file v12 development runtime has SHA-256
`6046e30017873e01d37c63fbdd58740bcf66ddb5a4be74e779bebfc3988e698c`.
Its genealogy, transport and command-contract first runs all passed strict
execution. Both visual artifacts passed independent data and geometry checks.
The genealogy still had manually added floating branch labels: a large horizontal
offset placed the coral label above an unrelated neutral person. This was a
composition/association defect despite a clean collision audit. The final
runtime adds a separate measured category key above small genealogies and directs
ordinary use away from redundant floating branch labels.

The final 60-file v13 runtime is frozen at SHA-256
`5fb3de42911cd4b1fb39356cd5accbb188aca6da900f7bcc1a536be784264b3c`.
All ten final runs used that identical runtime and preserved its bytes.

| Final case and run IDs | Model | Strict results | Independent result |
| --- | --- | --- | --- |
| `usefulcharts-cohorts-v13-20260911-gpt55-{1,2,3}` | `openai-codex/gpt-5.5` | 3/3 pass | 3/3 pass: all 19 people, exact lifespan labels, six partnerships, exact parentage, and three explicitly assigned categories. Each page is 1000 × 854.8; each trace contains a supported PNG read. |
| `usefulcharts-transport-v13-20260911-gpt55-{1,2,3}` | `openai-codex/gpt-5.5` | 3/3 pass | 3/3 pass: all 15 phases, exact endpoint dates, three networks, a common 1900–2020 scale, and no invented events or transitions. Each page is 1000 × 770; each trace contains a supported PNG read. |
| `usefulcharts-contract-v13-20260911-spark-1` | `openai-codex/gpt-5.3-codex-spark` | 1/1 pass | Source-backed Chromium audit passes all ten starter nodes and ten typed edges. The classic starter tests command compatibility, not editorial resemblance. |
| `usefulcharts-boundary-v13-20260911-spark-{1,2,3}` | `openai-codex/gpt-5.3-codex-spark` | 2/3 pass | All three preserve the known people, birth years and unresolved parent. The first run failed strict execution because it read `review/source.json` before creating it; its eventual valid diagnostic does not erase that tool error. |

The six final image-dependent traces read only the prompt, `SKILL.md`, the chosen
compact reference/template and their generated output. They did not read fixture
sources, renderer implementation, repository documentation, sibling skills, or
the web. Every strict pass has valid events, the declared observed model, zero
tool errors, exact output paths and an unchanged payload. The median record text
size in both visual cohorts is 15.93 units, combining 18-unit names and subordinate
dates. This is a readability observation, not a style similarity score.

All 16 executed attempts in this continuation are preserved in
[the complete run summary](cross-family-revision-summary-20260911.json): 14 strict
passes and two strict failures. Earlier institutional attempts remain in their
separate, unchanged record. No retries replace failed evidence. The boundary
contract accepts both the renderer's `nodes/unions` structure and ordinary
`people/parent_references` or `people/relationships` review JSON: that prompt does
not prescribe a renderer schema. An initial evaluator assumption about field
names was corrected before the final result; supplied facts are checked directly.

Reproduce the independent collection with:

```powershell
uv run --script projects/usefulcharts-style/scripts/summarize_cross_family_revision.py
```

It reruns the event summarizer with `--require-model`,
`--fail-on-invalid-json`, and `--fail-on-tool-error` for every retained attempt,
then applies `evaluations/contracts/verify-usefulcharts-families.py` to the
unambiguous v12/v13 visual cases. Each raw manifest records the complete launch
command, prompt SHA-256 and exact expected output list. Final commands follow
the same harness flags listed above, using the v13 run IDs; the contract adds
`deliverables/chart.svg`, `deliverables/chart.html`, `deliverables/layout.json`,
and the boundary case requires `review/source.json`, `review/diagnostic.json`.

## Authored mural and artwork repairs

The institution fixture retains 141 records and 171 paths, adding one sourced
telescope observer to a relevant observatory. The timeline retains all 50 periods,
55 transitions and 60 events while changing the page from 1800 × 2700 to
1800 × 2400. Its event reservations now use the actual numeric year scale instead
of a hard-coded pixel rate. The rejected 2250-unit attempt did not have enough
room. At 2400, the browser exposed a bridge crossing the last word of a canal
annotation and another crossing an observation illustration. Repositioning the
first annotation and proportionally sizing the second image resolved both.
The final source hash is
`a7383704c8308619e3e2c07c88f659b26adb6ad989677d9819fb705f15e4b0c7`.

Two unchanged public-domain source files were added:

- [Telescope (PSF)](https://commons.wikimedia.org/wiki/File:Telescope_(PSF).svg),
  a Pearson Scott Foresman illustration: transparent SVG, 117,104 bytes,
  SHA-256 `0d6f7043cebdf939be2e82264d220c702d3580e97607b689c87ca31054da1466`.
- [Cuneiform script2](https://commons.wikimedia.org/wiki/File:Cuneiform_script2.png),
  a transparent derivative of the Library of Congress tablet image: 416,361
  bytes, SHA-256 `47f330f9b68cdb3388871f93f9742639ac6d72724406eb456083d55bae38671f`.

The [bundled provenance](../../skills/usefulcharts-style/assets/illustrations/provenance.json)
records creator, source identity, revision, rights, dimensions and hash for all
four source illustrations. The timeline places three of them; the institutional
poster places three. The actual date and identity of each reference object remain
distinct from the invented chart event. Opaque vase, pendulum and conch candidates
were inspected and rejected, with their raw files retained only in ignored local
evidence. The gray photo rectangles are absent from the revised timeline.

During a rejected render attempt, an old SVG was accidentally audited against a
new brief. Inventory and date checks alone could pass this stale output because
the change was to the page dimensions. The runtime audit now compares the
embedded source SHA-256 with the complete supplied brief. An explicit stale-source
mutation verifies that this mismatch fails. The stale audit is not counted as
validation of the failed render.

## Visual judgment

The author inspected all six final forward previews, the three full authored
posters, and browser-rendered details. The local comparison retains reference,
previous v11 output and revised output at the same display width:

- `projects/usefulcharts-style/artifacts/reviews/cross-family-comparison/index.html`
- `projects/usefulcharts-style/artifacts/reviews/compact-forward-comparison/index.html`

The compact genealogy now has a coherent relationship fan, readable dates,
shorter connectors and an unambiguous key. The compact chronology has horizontal
labels, visible interval endpoints and narrow duration marks. The first-run
before/after comparison uses untouched isolated-agent outputs. It is unblinded,
and the genealogy prompt correction is disclosed next to it.

Dense visual parity is **not established**. The most visible remaining gaps are:

1. The five-region timeline still has a broad, sparse early section and large
   ribbon areas relative to the official history reference's finer streams and
   many local narrative groups. A shorter canvas improves balance but does not
   supply comparable historical complexity.
2. The institutional poster still exposes persistent subject districts and long
   lower influence corridors. Its major nodes vary, but the spatial rhythm is
   more regular than the official denominations reference.
3. The four-source illustration library is too limited to support the variety
   of silhouettes, photographs and focal points in dense official posters.
   The new telescope is clearer, yet the remaining small geometric emblems and
   thin line art still reveal the generated composition.

The next aesthetic iteration should address those specific dense structures and
source-supported illustration choices. Adding random records, duplicating art
or manufacturing relationships would invalidate the data and is not a repair.
No blind indistinguishability study or similarity percentage is claimed.

## Deterministic and browser validation

- Renderer tests: 26/26 classic and 35/35 editorial pass. New cases exercise
  measured family spacing, a multi-row key, stable cross-family categories,
  horizontal timeline labels, exact interval geometry and rejection of an
  impossibly short page.
- Adversarial browser mutations: 12/12 detected, including stale-source revision,
  deleted nodes, relation changes, hidden/oversized text, date displacement,
  detached/reentering paths, and filled bridges over records or illustrations.
- Three source-backed authored poster audits pass with no findings: genealogy
  561 nodes/323 paths/1144 text lines; institutions 141/171/579; chronology
  50/55/384 with all 60 events.
- Gallery checks pass at 1440 and 390 pixels, with no overflow or browser errors.
  All three viewers pass fit/zoom/full-size behavior. Embedded artwork retains
  its viewport and natural aspect ratio. The gallery checker was corrected to
  measure the transformed SVG viewport: a portrait's painted bounds can be
  narrower than its square viewport without being distorted.
- Quick skill validation passes with `uv run --with pyyaml --script
  C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py
  skills/usefulcharts-style`; the first invocation lacked that external helper's
  YAML dependency and was corrected without changing the skill.
- Pattern IDs, skill structure, independence and payload checks pass. Pages
  builds to `dist/pages/` with 639 files. Publication verification is recorded
  after the source commit and deployment.
- All 12 evaluation-harness regressions pass. The command-contract trace contains
  the exact requested render command. Local synchronization refreshed 22 changed
  files in `.agents/skills/` from the canonical sources.

Representative commands:

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/cross-family-mutations
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py dist/pages/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/cross-family-gallery
uv run --script projects/usefulcharts-style/scripts/compare_compact_outputs.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
```
