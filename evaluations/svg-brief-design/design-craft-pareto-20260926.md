# New design recommendations evaluated with native Pareto

Two new skill candidates were authored from public development evidence and
primary design sources, then compared with the installed skill in **54 fresh
GPT-6 Luna medium attempts**. Jev 6.3 and all task, runtime and scoring settings
remained fixed. **Neither candidate qualified for promotion.** Every arm had at
least one preserved tool error, leaving the native Pareto archive empty.
The installed and canonical skill remain unchanged.

## What was added

**Contour and counterform candidate (c).** A new conditional guide asks the
generator to construct large material and empty shapes together before detail:
define exterior-connected openings and their mouths, resolve unions/gaps/overlaps,
coordinate tangents and taper, remove near-tangencies, and inspect optical balance
with secondary detail hidden. Its intended mechanism is an earlier construction
decision, rather than another general instruction to use more white space.

**Print and optical finishing candidate (d).** A separate conditional guide asks
the generator to choose a coherent mark-making method, distinguish relief-like
cuts from engraved lines, use controlled gesture instead of random distress,
remove purposeless annotations, fit actual text before its container, and make
small optical corrections to glyph spacing and visual alignment. It explicitly
preserves quantitative accuracy and does not assume every historic print is thick.

Each candidate changes only the entrypoint routing and adds one reference file.
Scaffold geometry, renderer, recipe APIs and other baseline instructions are
unchanged. The earlier Trace interface patch was not silently included.

- [Research, source links and distinction from prior proposals](../../projects/svg-brief-design/evaluation/design-craft-research-20260926.md)
- [Contour guide](../runs/svt7/inputs/c/svg-brief-design/references/contour-counterform.md) and [exact patch](design-craft-c-20260926.patch)
- [Print guide](../runs/svt7/inputs/d/svg-brief-design/references/print-optical-finish.md) and [exact patch](design-craft-d-20260926.patch)

The sources are Getty's design principles, The Met's woodcut and engraving
technique descriptions, Butterick's layout principles, and W3C SVG curve
semantics. Their transfer into SVG procedures is a hypothesis; these sources do
not establish that a candidate improves model performance.

## Measured execution

| Variant | Fixed attempts | Jev-scored outputs | Trials with tool errors | New-guide use observed |
| --- | ---: | ---: | ---: | ---: |
| Installed baseline | 18 | 17 | 1 | Not applicable |
| Contour and counterform | 18 | 17 | 1 | 16/18 |
| Print and optical finish | 18 | 15 | 3 | 18/18 |

All 54 observed generator identities were `gpt-6-luna`, with 54 input-isolation
and 54 unchanged-skill receipts. There were no observer provider failures, no
retries and no substituted attempts. The unchanged visual-observer role remains
separate from the Luna artifact generator; Jev owns the reported score.

The baseline tried an unavailable `rg` command. The contour candidate passed a
shell command to the `write` tool. Print trials included the same tool-schema
mistake, an unsupported zero construction stroke, and guessed reference filenames
instead of the actual link targets. A trial with multiple tool errors is counted
once. These are execution outcomes, not zero-valued aesthetic judgments.

## Visual results by family

The table reports native family means on a 0–100 scale **only where all three
attempts in that arm received a valid Jev judgment**. An incomplete cell is not
filled with a partial mean or an administrative failure zero. These are
development diagnostics, not independent acceptance results.

| Public family | Baseline | Contour | Print |
| --- | ---: | ---: | ---: |
| Expressive figure | 57.31 | 58.46 | Incomplete: 2/3 |
| Integrated ornament | Incomplete: 2/3 | 64.34 | Incomplete: 2/3 |
| Compact HUD | 68.29 | 63.93 | 69.00 |
| Compact label | 64.35 | 63.51 | Incomplete: 2/3 |
| Vintage diagram | 66.93 | 59.85 | 66.27 |
| Open space insignia | 59.32 | Incomplete: 2/3 | 72.87 |

The print candidate's strongest complete family is the open space insignia,
**+13.55 points** over baseline. Its HUD delta is +0.71 and its printed-diagram
delta is -0.66. The contour candidate improves figure by +1.15 but loses 4.36
on HUD, 0.84 on labels and 7.07 on printed diagrams. These mixed results do not
establish a general design improvement. Three repetitions do not create three
independent families, and a single-family gain is especially uncertain.

The predeclared guard uses *all* five completely valid baseline families. It
fails for both candidates because each has missing candidate measurements in
that set. No favorable smaller subset was substituted for selection. The native
diagnostic overall means in the JSON/archive include preserved failure zeros;
they must not be presented as pure visual-quality grades.

Manual inspection also remains mixed. Contour outputs can become generic faces,
fragmented or pinched ornaments, dense labels and rigid black mechanical bodies.
The first print diagram still adds numeric ticks and uses nearly uniform curves.
Some print-candidate mechanical forms have more legible long openings than their
baseline counterparts, but the curated originals still show stronger integration
of masses and white space. Jev utility is not proof of professional parity.

## Pareto decision and independent gate

The actual native engine evaluated the frozen inputs and analyzed their native
Harbor jobs. Model, profile and source-digest provenance checks passed. Its
qualified archive contains **zero members** and its best aggregate candidate is
null. The predeclared next generation requires a qualified archived parent;
therefore no third candidate or merge was fabricated.

The source skill and repository-local installation remain byte-identical to the
frozen nine-file baseline. Both new ten-file proposals and their rejected
development evidence are retained. The two-family reserve adopted from the
unopened svt6 cohort remains unopened and unconsumed. No private artifact or
result was used to author, rank or revise these guides. The evolution stage is
completed and validation is stopped; previous campaigns remain closed.

## Reviewable outputs and validation

- [All contour attempts with their purchased references and baseline](../runs/svt7/gallery-c/index.html)
- [All print attempts with their purchased references and baseline](../runs/svt7/gallery-d/index.html)
- [Contour comparison image](../runs/svt7/gallery-c/comparison.png)
- [Print comparison image](../runs/svt7/gallery-d/comparison.png)
- [Native Pareto archive](../runs/svt7/pareto/development/generation-000/pareto-archive.json)
- [Declared selection guards](../runs/svt7/selection-g0.json)
- [Frozen protocol](../runs/svt7/protocol.json), [cohort adoption](../runs/svt7/cohort-adoption.json), and [closed study status](../runs/svt7/study/status.md)
- [Compact machine-readable result](design-craft-pareto-20260926.json)

The responsive galleries contain every fixed attempt. Unjudged SVGs preserved
by failed trials are rendered for human inspection only, with no quality score;
this does not replay the generator or verifier. Montage rows use the first sorted
attempt, not the highest-scoring result. Original files remain immutable.

Both candidate bundles passed the 13 scaffold tests and skill validation.
Payload inspection found no stored artwork; comparison against the six public
reference anchors found no copied match among 52 long paths. This exact-match
audit is limited and does not by itself prove every possible form of independent
creation. The new changes are text-only guidance, with no artwork imported.
Repository pattern, skill, independence, payload and diff checks passed.

Two local preparation/reporting issues were resolved without model retries:
the preparation environment initially lacked Pillow, so its declared dependencies
were completed before any generator launch; and two optional public proof PNGs
were initially put in the sealed review directory. Those newly added PNGs were
moved to `visual-review/`, restoring the exact sealed review tree before ledger
closure. Organizer verification passed before and after closure. No original
review file, native trial, score, candidate, dataset or protocol was rewritten.
Pi billed cost is unavailable; no zero-cost execution claim is made.
