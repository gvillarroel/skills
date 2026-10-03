# Visible discovery

Use when an illustrated poster must support exploration or a demanding reference
comparison. Pattern ID: `usefulcharts-visible-discovery`. Preserve the separate
content, geometry and reference-density requirements.

## Compose the answer into the diagram

Declare the factual questions and their visible reading paths before layout.
Choose a few paths that exercise different regions and operations: follow a
lineage, compare a mechanism or identify concurrent periods. Name the source
records, the answer and the graphical elements that make the answer visible.
A printed instruction to find something is not itself a visual explanation.

Compose an image and its particular fact as one measured unit. Suitable patterns
include an illustrated classification leaf, a portrait beside a named node,
a vehicle connected to its dated endpoint, and a comparison whose objects align
with the same attributes. Reserve the complete unit before packing. Use images
of exact objects or labelled representative classes; do not introduce false
identity, chronology or scale.

Make ownership explicit in the printed result. Metadata and proximity are not
visible evidence. For classification specimens, print the exact local category
code beside the image and add a short connector to that leaf. For contextual
hardware, name the associated release or family and label the picture as
illustrative. Keep question prompts near the paths that answer them. Validate
connectors against every text box, including their own source and target labels;
excluding endpoint records from obstacle routing can hide serious collisions.

Keep useful insets when they encode an additional comparison, such as population
or geography using the same categories as the main graph. Avoid mandatory
full-height art rails and uniformly spaced picture cards. A grid is appropriate
when its visual cells make direct comparison possible; irregularity is not a
quality criterion by itself.

Keep the important relations continuously traceable. A few paired portals can
resolve long routes, but they should not replace the main explanatory network.
For numeric chronology, preserve X and adjust Y, label side, image footprint and
released row allocation. Empty years remain empty; pictures do not create dates.
Separate undated or conditional histories explicitly.

## Review the reading operation

Open the final whole poster and details. For each selected discovery, point to
the printed graphical steps, record the supported answer and inspect the same
operation with the relevant reference. Distinguish local recognition, visible
relationships and textual explanation. Describe any distant lookup needed.

Assign stable SVG IDs to the inspected image/fact groups and relationship paths.
Use `data-record-id` on record groups and `data-source`/`data-target` on relation
groups when applicable. The review helper checks that cited IDs exist; seeing
those elements and judging their usefulness still requires actual image input.

Keep three acceptance results separate:

1. **Illustrated coverage:** meaningful, recognized body images with valid owners.
2. **Exploratory composition:** at least three demonstrated reading paths in two
   body regions, visible ownership, no detached lookup for those paths, and no
   material unresolved composition defect. Record whole/detail reference
   comparisons for structure, image ownership, color continuity and reading rhythm.
3. **Reference target:** the exploratory gate plus convincing reference-family
   composition and the independently verified knowledge-density minimum.

Use [the exploration template](../assets/templates/exploration-review.json), retain
the ordinary illustrated review, and run:

```sh
uv run --script <skill-dir>/scripts/assess_exploration_review.py exploration.json --output assessment.json
```

The command exits unsuccessfully when exploratory evidence is insufficient.
Its report can still show an exploratory pass with reference acceptance pending
or failed. Never rename a coverage result as a complete aesthetic pass. Hashes,
IDs and review declarations cannot prove visual truth or indistinguishability.

Compare two fully illustrated candidates when testing this evaluator. Include a
relevant reference and whole/detail views; a no-image versus image comparison
tests only basic coverage. Give isolated reviewers raw artifacts without the
author's diagnosis. Retain disagreement, repair supported defects and inspect
the new revision. State when the author already knows the source; no self-review
is a blind authorship experiment.

Bind comparison verdicts to the right artifact before counting agreement. Give
each candidate a neutral identifier that is visibly printed outside the chart
on its review sheet, and repeat it on the whole and detail views. Preserve the
unchanged source image and its hash. Require the reviewer to report each exact
image path, its visible identifier, a distinctive printed title and a short
description of its layout before choosing a preferred identifier. Check those
fingerprints against the supplied pixels. If the prose describes a different
candidate from the selected identifier, mark the verdict invalid; never silently
swap labels or count it as a favorable vote. Reissue a fresh, clearly identified
comparison when needed, retaining the failed review. This identity check does
not establish the correctness of the aesthetic judgment.
