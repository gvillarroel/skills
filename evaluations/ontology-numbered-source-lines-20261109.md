# Numbered source views for ontology evidence

The extraction checker exposes a `lines` command for pinned UTF-8
snapshots. It checks the source path and SHA-256, then shows the
one-based physical line numbers used by `bind` and `materialize`.
The actor selects a range and the materializer obtains its exact
quote from the original bytes. The design separates selection of a
locator from reconstruction of the quotation. [ALCE citation
evaluation](https://aclanthology.org/2023.emnlp-main.398/) ·
[W3C selectors](https://www.w3.org/TR/annotation-model/#selectors)

## Diagnosis and comparison

Ten citations in a retained V44 trial pointed one line after an
approved same-source span. All ten quotes were mechanically exact
at their selected offsets. The support rubric identified
that those locations failed to support the claim. [V44 native
comparison](ontology-single-claim-plan-20261109.md#native-harbor-development-comparison)

The synthetic pilot froze 12 decisions, including two abstentions,
over neighboring negation, authority, revised facts, directional
relations, multilingual text, blank lines and CRLF. Three shards
were each tested in four conditions with GPT-6 Luna low, one
attempt per cell. All 12 strict Pi cells were admitted. The
preflight exercised 98 controls for correct spans, exact but
unsupported citations, conflicting copied quotes and false
positives.

| Presentation | Required copied quote | Correct pointer or abstention | Complete result |
| --- | --- | ---: | ---: |
| Raw | No | 7/12 | 7/12 |
| Numbered | No | 12/12 | 12/12 |
| Raw | Yes | 11/12 | 11/12 |
| Numbered | Yes | 12/12 | 11/12 |

In the last arm the actor chose the correct line for one claim and
copied the following line's text. Each conflicting copied quote
had a unique exact match. Auto-relocating to that quote would
correct one raw-arm case and break one numbered-arm case. The
released workflow derives the quote from the chosen range.

## Transfer to real documentation

The follow-up compared nine evidence decisions from three Argo CD
guides at one pinned revision. Seven needed multiline evidence and
two needed abstention. Forty-one verifier controls passed. All six
strict Luna low cells were admitted, with the numbered arm run
first. Each raw window included its absolute starting line number.
[Automated sync](https://github.com/argoproj/argo-cd/blob/d719b9d7d24dff414672aff57c19bd53e66a9a54/docs/user-guide/auto_sync.md) ·
[Sync options](https://github.com/argoproj/argo-cd/blob/d719b9d7d24dff414672aff57c19bd53e66a9a54/docs/user-guide/sync-options.md) ·
[Sync phases and waves](https://github.com/argoproj/argo-cd/blob/d719b9d7d24dff414672aff57c19bd53e66a9a54/docs/user-guide/sync-waves.md)

| Presentation | Sufficient evidence or correct abstention | Shortest reviewed range or correct abstention |
| --- | ---: | ---: |
| Raw | 4/9 | 4/9 |
| Numbered | 9/9 | 6/9 |

The numbered arm improved coverage in five cases with no losses.
Three numbered citations included the required passage and
neighboring lines. These comparisons start from proposed claims
and measure evidence selection. Full-corpus claim discovery
remains a separate outcome.

## Integration

Use the SHA-256 from the source manifest and preserve original
line numbers when selecting from a subrange.

```text
uv run --script SKILL/scripts/check_extraction.py lines --source-root . --source sources/register.txt --sha256 SOURCE_SHA256 --start-line 10 --end-line 16
```

The candidate CLI matched the nine frozen Argo CD source windows
and passed 14 independent encoding, integrity and output controls.
The two interpreter runs produced identical audit bytes. The
numbered view and binder share LF boundary logic. Blank lines
count, CRLF is removed from the displayed line ending, and
interior CRLF stays in multiline evidence. A UTF-8 BOM, bare CR
and Unicode separator remain within the physical line.

An independent replay of the 14 pinned GitHub Docs files matched
all 1,653 physical lines. Materializing the reviewed 47-assertion
product plan produced the same graph and evidence bytes as V44.
An exhaustive local boundary check over 400 short source layouts
matched the original binder on 393 accepted and 223 rejected
ranges. Seven binding and numbered-view tests and four
materializer tests passed on Python 3.11 and 3.14. [Product reference
evaluation](product-feature-inventory-20261109.md)

Two strict isolated runtime checks used three GitHub Docs excerpts
preseeded byte for byte. Both invoked the installed `lines` and
`materialize` commands and recovered all three expected classes
with the same graph digest
`bf375990dab654cce4c98e7ad299b55ea86e7255e8bafc9e9262c53fc4503f56`.
The evidence ledgers differed. Both cited the same rule for
auto-merge and selected different passages for the review model
and the usage metrics. One metrics citation described the
broader metrics capability, while the other named the dashboard
and its neighboring entries. Both kept the mechanism in review.
The initial smoke prompt embedded a large encoded setup command.
It produced an invalid ontology in one attempt and a Python
syntax error in the other. Both failures remain in the archive.
The preseeded smoke removes setup transcription from the test.

| Local evidence in `numbered-lines` | SHA-256 |
| --- | --- |
| Synthetic protocol | `28246e915db5671d3350170fa9aa7461ddbf5a66d85daa911864f9298f20b839` |
| Synthetic results | `cffa3bb185691b96453fafbadc815e4c2bd011a784f435008a2e95b884f71c56` |
| Argo CD protocol | `ccfbdc06582e3b428aa18b76092f9c05fedd8f7a7ac74559ec2f716756507dca` |
| Argo CD results | `e82f795ab11f3ad64cb583a7ba9b5a0172cda2f786efc3183d944d14834d6137` |
| Candidate view audit | `95fae4224223840842a800fdc8ee6045528c51891837bb9c0e9a74bfcfa593a4` |
| GitHub Docs compatibility replay | `55db6d524fc404029d71c01063b68299de4f7faa3f04965a2d94966693248e72` |
