# SVG Brief Design: proposed next campaign

Status: **proposal only; no new candidate or evaluation launched**. Written on
2026-09-26 from development evidence, before the user's 10:00 UTC deadline.
Keep the original canonical and installed skill unchanged. This document does
not promote a mutation, change a reward, or establish an improvement claim.

## Development evidence and limits

The deadline campaign tested a small semantic-binding addition to the existing
guide with exact `openai-codex/gpt-6-luna`, medium reasoning, Pi SSE, and native
Harbor. Its matched three-case minibatch summed to 1.4565776455183686, below the
original guide's 1.6898118751201526. The unchanged guide remained selected.
The six-case original-guide mean was 0.4994161007565703. These are reference
similarity scores, not semantic accuracy. This review read development only;
private validation and holdout were not opened.

Several cases show weak similarity in the visible aspect component while
other style components are stronger:

| Original-guide development case | Aspect similarity | Relevant comparison |
| --- | ---: | --- |
| Optics diagram, initial observation | 0.3025354450773892 | Line weight 0.9467178550192189 |
| Optics diagram, minibatch observation | 0.18142277315920627 | Line weight 0.9641169444501055 |
| Horizontal interface frame | 0.3231080221696369 | Density 0.7909856094574992 |
| Industrial label, initial observation | 0.37754874352133644 | Orientation 0.8309975633457847 |
| Industrial label, minibatch observation | 0.48980588181300366 | Orientation 0.8237230491233677 |

Exact native verifier records: [optics initial][optics-initial],
[optics minibatch][optics-repeat], [frame][frame],
[label initial][label-initial], and [label minibatch][label-repeat].

This supports investigating composition before stroke refinement. It does not
prove that the natural-language briefs require the reference's exact aspect.
The short requests leave meaningful design choices open. A skill must not
turn reference dimensions, counts, chord arrangements, or specimen silhouettes
into hidden instructions.

Generation variation is substantial in at least one observed pair. With the
same original guide and aperture brief, visual similarity was
**0.5626203865598112** initially and **0.7364061222762962** in the minibatch,
a difference of **0.1737857357164850**. Both outputs passed technical validity.
See [first aperture trial][aperture-initial] and
[second aperture trial][aperture-repeat]. This pair is a warning about
single-observation rankings, not an estimate of population variance or a
statistical significance result.

The semantic-binding proposal also exposed a semantic/proxy disagreement.
Both original-guide label observations contained no SVG text elements; the
proposal contained nine with readable strings, while visual similarity fell
to **0.47419718520583076**. The preserved [candidate feedback][label-feedback]
records the element counts and text strings, and [native metrics][label-new]
record the score. Text-element presence is evidence of an explicit textual
representation, not proof of visual legibility. Rendered review is still
required. Do not reward invented content merely because text is present.

## One proposed mechanism

Test only a minimal visible-footprint addition to the original guide:

> Establish the proportions and direction of the visible artwork before sizing
> the canvas. Reserve space for the actual lengths of required labels so
> annotations do not stretch the composition unexpectedly. Judge words such as
> compact, slender, or horizontal from the occupied shapes and marks, not from
> the viewBox. Set the surrounding margins after this footprint is coherent.

This is an untested instruction hypothesis. Preserve the original guide's
remaining body, frontmatter, and reference files. Do not combine this with
the rejected semantic-binding mutation. Do not add SVG markup, images,
coordinates, copied paths, asset-specific examples, or target metric values.

## Prospective bounded evaluation

Register a new study before any further model calls. Declare the original
guide as the baseline, one mutation hypothesis, exact model/runtime/image
identities, task-family split commitments, attempts per task, call cap,
ordering policy, stopping rule, and promotion rule. Reserve enough time to
finish every required gate rather than shortening gates near a deadline.
Use native Harbor evidence and the existing guidance-only payload audit.

Treat tool access as an experimental factor. The native trial adapter gives
the generator writing-only tools. A later rendering-assisted workflow would
change the available feedback, so register it as a separate harness factor
with matched access for both baseline and candidate. Do not pool read/write
routing checks or rendering-assisted outputs with the writing-only guide
comparison, and do not attribute a tool-access change to the skill text.
The existing adapter loads the main instructions through the native skill
command, but its write-only tool list also prevents consulting the separate
mechanics reference. A read-enabled reference-consultation condition therefore
needs the same prospective treatment and must still exclude evaluator assets.

Use repeated observations per task on both sides, with a fixed count of at
least three declared before launch. Retain every evaluable attempt and
report within-task variation and all regressions. Do not resample a semantic
failure or choose the best sample. Fit the task and repetition counts to the
explicit budget before registration; do not choose them from interim scores.

Keep the existing verifier 1.1.0 similarity definition unchanged for
comparability. Any alternative verifier requires a separately versioned,
prospectively registered study. Do not rescore or relabel these completed
campaigns to make a candidate appear successful.

Select and digest-freeze the finalist using development evidence only. Use
preregistered, disjoint private validation. The presently unopened private
cohorts may be used only if their provenance still establishes that they are
unexposed and the new registration permits it. Any cohort whose feedback
informs a mutation is no longer private selection-independent evidence:
close that study and use fresh validation and, where applicable, a new
untouched holdout. No mutation or reselection may follow private outcomes
within the same promotion decision.

## Separate prompt-derived semantic checks

Before generation, an evaluator should derive a small acceptance checklist
from each natural request alone. Record required subjects and relationships,
explicit spatial/style qualifiers, textual-content requirements, and the
delivery contract. Leave unspecified proportions and ornamental choices
unconstrained. Freeze the checklist before viewing generated artifacts and
without consulting reference artwork.

Use deterministic checks only for facts they can establish, such as exact
output location, valid self-contained SVG, forbidden resource absence, and
presence of explicitly supplied text. Use blinded rendered review for
recognizability, relationships, actual legibility, clipping, and explicit
layout qualifiers. Record uncertain judgments and reviewer disagreements.
For stronger independence, have a separate curator write the new briefs and
semantic criteria without access to reference geometry.

Report semantic results separately from the shape/style proxy. Do not blend
them into a post-hoc score, infer semantics from a path or text count, or
require an exact reconstruction of one legitimate reference interpretation.
If semantic criteria become promotion gates, register that rule prospectively
for the new study and apply it equally to baseline and candidate.

All referenced native records below are local ignored development artifacts;
they are not shipped in the skill or published with purchased artwork.

[optics-initial]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00002-740953f66380-vector-016--3a1158bde80174e3-6748239f/trials/vector-016--3a1158bde80174e3__znqyLkN/verifier/metrics.json
[optics-repeat]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00009-740953f66380-vector-016--3a1158bde80174e3-01d43f66/trials/vector-016--3a1158bde80174e3__CCWhymc/verifier/metrics.json
[frame]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00004-740953f66380-vector-018--99a8559203bfe19b-1cd9ddbe/trials/vector-018--99a8559203bfe19b__MF4PAjz/verifier/metrics.json
[label-initial]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00005-740953f66380-vector-020--09ee2ae28c7c367a-fd45a363/trials/vector-020--09ee2ae28c7c367a__7qDxXTo/verifier/metrics.json
[label-repeat]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00008-740953f66380-vector-020--09ee2ae28c7c367a-f12e6b0d/trials/vector-020--09ee2ae28c7c367a__dpZaoGE/verifier/metrics.json
[aperture-initial]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00003-740953f66380-vector-007--e5b17b3bccb11ded-2a5fe122/trials/vector-007--e5b17b3bccb11ded__8smNdLh/verifier/metrics.json
[aperture-repeat]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00007-740953f66380-vector-007--e5b17b3bccb11ded-41203291/trials/vector-007--e5b17b3bccb11ded__tHAMHGv/verifier/metrics.json
[label-feedback]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00011-3b258c6293c3-vector-020--09ee2ae28c7c367a-33e48309/reflection-feedback.json
[label-new]: ../runs/svg-brief-design-deadline-20260926/run-async-compatible/harbor-trials/development/00011-3b258c6293c3-vector-020--09ee2ae28c7c367a-33e48309/trials/vector-020--09ee2ae28c7c367a__XrJ2nEi/verifier/metrics.json
