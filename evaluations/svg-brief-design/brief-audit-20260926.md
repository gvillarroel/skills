# SVG Brief Design: development brief audit

Audit date: 2026-09-26. Scope: the **24 existing development instructions only**
in `fox-vector-benchmark-v1/datasets-v1.1/development`. No private task,
instruction, reference artwork, or private result was opened for this audit.
The dataset and skill were not edited. This is a prompt-content audit, not a
new performance metric or a model evaluation.

The briefs broadly meet the user's request for ordinary short descriptions of
the desired subject and style. They do not provide coordinates or stepwise
reconstruction instructions. Their uniform authoring style and substantial
evaluation boilerplate mean they should be described as **curated human-like
requests**, rather than a sample of naturally collected user messages.

## Method and quantitative results

Read each development `instruction.md`, split it at the first blank line,
and audit the natural brief separately from its delivery contract. Count
whitespace-delimited tokens with `\S+`; these are word counts, not model tokens.
Inspect every brief manually for geometric recipes, source identities, exact
feature counts, and open design choices. Inspect all development `task.toml`
files for family tags. Automated scans supplement the manual review; they do
not prove that no conceivable information leakage exists.

| Property | Observed result |
| --- | --- |
| Development instructions read | 24 of 24 |
| Language | Spanish throughout |
| Natural-brief word count | Minimum 22; median 27; mean 27.2083; maximum 32 |
| Total natural-brief words | 653 |
| Sentence structure | All 24 have two sentences |
| Native instruction structure | All 24 have two paragraphs: brief, then delivery contract |
| Delivery-contract length | 40 words in every instruction |
| Full instruction word count | 62–72; mean 67.2083; total 1,613 |
| Contracts after replacing only the output path | One identical contract |
| Output paths | Six variants across two directories and three SVG basenames |
| Natural briefs with digit numerals | 0 |
| Natural briefs with URLs, markup, or hex color literals | 0 |
| Natural briefs with task IDs, reference filenames, source hashes, or vendor names | 0 |
| Natural briefs with coordinates, dimensions, ratios, or numerical stroke widths | 0, by manual review |
| Natural briefs with an explicit nontrivial feature count | 1: a four-point central opening |

The exact feature count is an ordinary property of the requested symbol, not
a path recipe. It is still worth recording because the simplest geometric
tasks necessarily leave fewer design choices open than an illustrative brief.
Singular subjects and terms such as several, some, or a few are not counted
as exact nontrivial feature counts.

The family distribution is uneven: geometry 10, diagrams 6, and cyborg, HUD,
labels, and space 2 each. A pooled mean therefore weights geometry more than
the other families unless a separate family-balanced aggregation is declared.
This audit does not change any existing aggregation.

Coverage by native task number and natural-brief word count:

| Task | Words | Task | Words | Task | Words |
| --- | ---: | --- | ---: | --- | ---: |
| 003 | 27 | 004 | 27 | 005 | 26 |
| 006 | 27 | 007 | 27 | 008 | 23 |
| 009 | 28 | 010 | 28 | 011 | 25 |
| 012 | 26 | 013 | 22 | 014 | 25 |
| 015 | 27 | 016 | 32 | 017 | 29 |
| 018 | 28 | 019 | 25 | 020 | 28 |
| 021 | 29 | 022 | 31 | 023 | 27 |
| 024 | 29 | 029 | 27 | 030 | 30 |

## What the briefs require and leave open

The following examples are English paraphrases for analysis, not replacement
prompts or new skill instructions:

- The [wireframe globe request][globe] asks for thin black meridians and
  parallels, symmetry, and no landmasses or labels. It leaves their count,
  exact spacing, projection, and line width open.
- The [periodic-oscillation request][oscillation] asks for axes, small letters,
  and an old scientific illustration style. It does not specify an equation,
  cycle count, amplitude, vertical offset, or exact labels. Reference mismatch
  in those choices is not automatically a failure to follow the request.
- The [industrial-label request][label] specifies a horizontal label, black
  header, short information text, and a small barcode. It leaves the text,
  code payload, encoding standard, dimensions, and detailed layout open.
- The [space-insignia request][insignia] combines an inclined elongated tip
  with a mechanical body and fins. It leaves angle, proportions, topology,
  ornament, and the precise interpretation as spacecraft or spear open.

These are useful freedoms for simulating real short requests. They also limit
what a single reference SVG can establish as the correct answer. The curator
had seen the reference artwork before authoring these briefs, as disclosed in
the [existing study record](evolution-20260925.md). The absence of coordinate
recipes does not remove that curation dependence or make the benchmark an
independently authored generalization set.

## Actual limitations to preserve in interpretation

All briefs use the same two-sentence shape and a narrow 22–32-word range.
The phrasing is plausible, but the regularity underrepresents normal user
variation in verbosity, grammar, languages, uncertainty, and context. The
development distribution is also narrow in visual style: monochrome vector
objects and decorative or scientific motifs. Do not infer coverage of general
SVG illustration or real user traffic from this set.

The uniform 40-word contract constitutes approximately 59.5% of the combined
instruction words. Its machine path, two-megabyte cap, self-contained SVG,
editable-vector requirement, transparency, and prohibited-resource rules are
evaluation controls. They are not a reconstruction recipe, but the full
native instruction is less like an unassisted everyday user message than its
first paragraph alone. Report both lengths rather than advertising the full
instruction as a 27-word request.

Two label briefs mention barcodes without a payload or an encoding standard;
one separately calls its square code decorative. The text does not establish
that every barcode must scan, nor does it establish that they are all merely
decorative. A correctness claim about encoding would need a prospective task
contract. The inventory-label phrase about black and white also leaves a
small stylistic ambiguity, although the common black-on-transparent delivery
contract explicitly governs the output background.

The scientific briefs describe visual subjects and style without full
mathematical or physical specifications. This is consistent with decorative
diagram generation; it does not support a claim of scientific correctness.
Similarly, an explicit short-text request should be checked for meaningful
readable text, while exact reference wording cannot be required when the
brief does not provide it.

## Future changes only

Keep all existing tasks and scores unchanged. For a future registered dataset,
use an independent curator who cannot see reference geometry, include more
natural variation in brief length and phrasing, and retain a clearly separated
format contract. Declare the role of barcodes and scientific semantics before
generation. Add only enough information to define the intended task; do not
insert reference counts, placements, or construction steps to improve scores.

Freeze prompt-derived semantic checks before viewing outputs. Score required
content, relationships, legibility, and explicit exclusions separately from
reference style similarity. Leave unspecified geometric choices unconstrained.
If family-balanced reporting is desired, register it in the new study instead
of reweighting these completed results. Use disjoint private gates under the
existing exposure rules; this audit provides no private validation evidence.

## Input identity and reproducibility

Read-only source root:
`C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1`.
Discovery was limited to `datasets-v1.1/development/*/instruction.md` and the
matching development `task.toml` files. The mixed-split JSONL was not opened.

The input collection digest is
`08c3933f085486040ded2fcbf111fa8735359221c9ef74404406e8cfb84e7ab6`.
To reproduce it, sort the 24 development directory names ordinally; for each,
form `directory-name`, one ASCII space, and the lowercase SHA-256 of the raw
`instruction.md` bytes. Join these records with LF and append one terminal
LF, encode UTF-8, and compute SHA-256. It binds the exact audited instructions,
including their unchanged delivery contracts.

[globe]: <C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/datasets-v1.1/development/vector-008--802d6fa26f7bca86/instruction.md>
[oscillation]: <C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/datasets-v1.1/development/vector-024--652120566170fbf2/instruction.md>
[label]: <C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/datasets-v1.1/development/vector-020--09ee2ae28c7c367a/instruction.md>
[insignia]: <C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/datasets-v1.1/development/vector-030--d3c57e0c21dbede0/instruction.md>
