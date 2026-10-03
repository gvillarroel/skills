# Purpose-matched techniques and the same SVG skill on Astra

Date: 2026-09-26. Status: completed public comparison; no skill promotion.

The installed skill was evaluated unchanged on exact GPT-6 Astra medium. One
experimental variant adds a conditional mark-selection guide, leaving all helper
code unchanged. Both full bundles and every public attempt are preserved.

## Results

Scores below are native Jev 6.3 expected reference-relative utility, scaled to
100. They are not absolute design grades or pixel similarity. The reference
parity convention is 90, and uncertainty across categories affects the scalar.
Every displayed family mean requires all three scored, error-free attempts.

| Family | Luna current skill, historical | Astra current skill | Astra new guide | Guide minus current on Astra |
| --- | ---: | ---: | ---: | ---: |
| Expressive figure | 57.31 | Unavailable (2/3 judged) | 83.86 | Unavailable |
| Integrated ornament | Unavailable (2/3 judged) | 62.80 | 55.90 | -6.90 |
| Compact HUD | 68.29 | 80.30 | 82.56 | +2.26 |
| Compact label | 64.35 | 88.37 | Unavailable (1/3 judged) | Unavailable |
| Vintage diagram | 66.93 | 65.65 | 66.67 | +1.02 |
| Open space insignia | 59.32 | 96.96 | 96.17 | -0.79 |

The same-skill historical model contrast has 4
complete shared families and a mean difference of
+18.10 points. This is a descriptive model
transfer result, not a randomized contemporaneous model comparison. Missing
families are disclosed above and are not silently assigned zeros or partial means.
The full per-attempt values, native dimensions and reference preferences are in
[the comparison data](../runs/svt8/comparison-summary.json).

## Native Pareto decision and failures

| Arm | Attempts | Trial errors | Tool-error events | Visual-provider failures | Native qualified |
| --- | ---: | ---: | ---: | ---: | --- |
| Current | 18 | 1 | 0 | 1 | False |
| New guide | 18 | 2 | 2 | 0 | False |

Native archive: []. No finalist passes the frozen guards.
The baseline contains an external visual-observer service failure; that leaves
one generated SVG without a quality judgment and makes the full comparison
inconclusive under the frozen rule. The candidate's two preserved tool failures
occurred in label tasks: a font-resource probe exited unsuccessfully, and a
render operation rejected an invalid SVG size. They are separate from the
observer service failure. Native diagnostic means can contain failure zeros; they are
not presented as visual-quality means here. There were no retries, rescoring,
post-hoc evaluator changes, or private gate calls.

The installed and local skill remain unchanged. The adopted two-family private
reserve was neither opened nor consumed. The one-generation experiment is closed;
the earlier three-rejection campaign has not been reset.

## What changed and why

The earlier contour/print proposals supplied broad advice that did not reliably
select the right construction. The new guide chooses by intended use and assigns
each mark a representational function: boundary, occlusion, plane change, joint,
trace, identifier or requested ornament. It then addresses local construction:

- Expressive figures: landmarks and meaningful plane relationships, preserving
  mood rather than forcing a generic pictogram grid.
- Interlaced ornament: resolve a band's adjacent void and each union, separation
  or crossing before repeating it; coordinate both band edges.
- Open mechanical forms: align separated masses and exterior channels along
  a shared directional structure.
- Compact technical graphics: actual content or aperture determines the frame,
  with one reading cue and only functional supporting marks.
- Editorial scientific diagrams: the relationship determines axes and notation;
  printed mark character must come from related traces and terminals.

This is an experimental synthesis. Princeton/Rutgers research supports selecting
shape-conveying lines; Adobe documents joining, trimming and variable width;
NPS design guidance ties layout and label hierarchy to purpose. None establishes
that these instructions improve generated SVGs. IBM's fixed pictogram grid was
explicitly rejected as a general style recipe. See the
[source review and applicability limits](../../projects/svg-brief-design/evaluation/purpose-techniques-astra-20260926.md).

Only `SKILL.md` routing and `references/mark-selection.md` differ from the parent.
The guide was observed in 18/18 candidate traces.
The [exact patch](purpose-astra-c-20260926.patch) and
[file-difference audit](../runs/svt8/candidate-diff-audit.json) preserve the change.

## Visual interpretation

The current Astra outputs show better controlled mechanical planes and compact
layout in several cases, while the reviewed ornament still uses uniform strands
and the vintage diagram still resembles a modern mathematical plot. The new
guide's first ornament retains thin interrupted curves, with weak terminal and
band relationships; the first diagram retains uniform treatment. Cleaner SVG
geometry and fewer labels are insufficient evidence of editorial finish.

These are located public observations, not additional scores. They were recorded
after the candidate was frozen and did not change it or the evaluation. See
[the baseline observations](../runs/svt8/public-visual-review-b.json) and the
all-attempt galleries below. A high utility score in one family does not establish
professional parity across the portfolio.

## Versions and outputs

- [Current skill archive for Astra](../runs/svt8/packages/svg-brief-design-astra-current.zip)
  contains the exact installed nine-file bundle.
- [Experimental guide archive for Astra](../runs/svt8/packages/svg-brief-design-astra-purpose-guide-experimental.zip)
  contains the ten-file variant. It is not promoted or installed.
- [Usage instructions](../runs/svt8/packages/USAGE.md) explain loading one bundle
  and selecting Astra externally; the skill does not choose its own model.
- [Exact Astra profile and file hashes](../runs/svt8/packages/astra-profile.json).
- [Luna/Astra generated-output gallery](../runs/svt8/gallery-models/index.html)
  contains all 54 historical/current/experimental attempt slots and no purchased
  artwork. Rows are display pairings, not shared random seeds.
- [Astra comparison with purchased reference previews](../runs/svt8/gallery-c/index.html)
  is for the owner's local review. It includes all 36 Astra attempt slots.
- [Editable generated SVG package](../runs/svt8/packages/astra-generated-svg.zip)
  includes available generated files and a manifest distinguishing scored and
  failed attempts; purchased references are excluded.

Native bundle digests:

- Current: `sha256:935e7cee66c23f17341affd953c16b336dedaff12e4f438236247db774b68a95`.
- Experimental: `sha256:d4a4fa226f394dfe1718257ef286eb01894ac0f462b6e8dd6b41101c9d0f4fad`.

## Controls and scope

The runtime adapter is a versioned Astra counterpart; old sealed Luna helpers and
jobs were not rewritten. The [transfer audit](../runs/svt8/model-transfer-audit.json)
checks identical baseline bytes and native configuration except model/adapter
identity and study paths. Both profiles retain Pi 0.84.2, medium effort, the
configured 16,384 output cap, container, tools, time limits, three attempts,
concurrency three and unchanged Jev 6.3. The new guide has not been tested on Luna.

All 36 new traces report `gpt-6-astra`. Input isolation and unchanged-bundle
receipts pass for both arms. Both 13-test scaffold suites and skill quick
validation pass. A packaging and public-reference audit found zero exact reuse
among 52 long paths from six public sources; this does not exclude every possible
transformed reconstruction. No purchased SVG, benchmark identities or recorded
answers are inside either skill archive. Archive contents were checked against
the frozen file hashes.

Native evidence: [protocol](../runs/svt8/protocol.json),
[Pareto archive](../runs/svt8/pareto/development/generation-000/pareto-archive.json),
[selection](../runs/svt8/selection-g0.json),
[final decision](../runs/svt8/final-decision.json),
[organizer status](../runs/svt8/study/status.md).
The judge includes subjective and low-confidence fields, the cohorts are small,
and the models are provider aliases without an immutable checkpoint. No broad
statistical superiority, independent effect of individual rules, or measured
provider cost is claimed.

## Delivery verification

[Playwright gallery checks](../runs/svt8/gallery-qa.json) verify 54 images in each
HTML gallery, no horizontal overflow at 390px and 1440px, correct Astra labeling,
collapsed methodology and working family navigation. The sole browser console
message was a missing favicon (404). The browser blocked direct file URLs, so
QA used loopback-only servers rooted at the individual gallery directories;
private datasets were not served. One initial shell-quoting error was corrected.
The [mobile preview](../runs/svt8/visual-review/models-mobile.png) was inspected.
[The six-family visual review](../runs/svt8/public-visual-review-c.json) records
remaining construction weaknesses without rescoring or modifying the candidate.

The clearest next hypothesis is a change in the original procedural construction
itself: coordinated band edges and junctions for ornament, and a purpose-specific
printed trace construction for editorial diagrams. More prose alone did not
establish that behavior here. This is an untested next direction, not a promoted
rule or a claim that any source artwork should be reconstructed.

Repository pattern-ID validation (1,222 IDs), skill validation, independence
validation, payload validation and `git diff --check` all passed. The latter
emitted only existing CRLF-normalization warnings. All 21 local report links,
all 36 exported SVG hashes and the Astra script compilation checks passed.
The closed organizer verifies successfully. No changes to unrelated work,
commits or publication were made.
