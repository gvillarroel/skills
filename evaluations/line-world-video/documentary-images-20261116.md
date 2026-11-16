# Documentary object imagery

Date: November 16, 2026. Qualified package: Line World 0.21.1.
Keep the primary skill validating for its previously recorded broad-generation
limits. This revision tests the bounded photographic-object workflow and the
actual CUDA/AlexNet film. It does not claim a new complete native Vids export.

## Reusable behavior

Prefer a verified source photograph for the identity of a documented physical
object. Preserve diagrams for mechanisms, relationships, architecture and
quantities. A network-partition diagram can sit between actual card photographs.
Do not disguise an incorrect model or memory variant with a filter. Keep the
source's exact identity, provenance and rights separate from an illustrative
role or a claim about a particular historical physical specimen.

The primary entry point, agent prompt and shared contract for all four dedicated
producers carry this rule. The compact `references/documentary-images.md`
documents the request, binding contract, source review and final-size inspection.
The self-contained `scripts/documentary_assets.py` provides:

- Checked source acquisition with an identity-review-pending receipt.
- Exact model/variant assertions, original bytes and digests, reviewed crops and
  subject polygons, aspect preservation, grayscale, edge, pixel and ordered
  one-bit treatments.
- Cached PNG/SVG variants, original/prepared/derived lineage, credits and a
  compact comparison. Pixel SVGs are described as photographic derivatives.
- Source/prepared/variant integrity and exact one-bit palette checks.
- Actual rendered object/asset bindings and a browser-selected screenshot from
  `audit --html ... --screenshot ...`, without a new launcher per prototype.

The pinned one-bit engine is bundled, with its source provenance and palette
lookup contained in the skill. No sibling skill is required at runtime. Final
Pi traces did not read that implementation or any acceptance gallery.

## Actual source selection

| Source | Evidence and role |
| --- | --- |
| EVGA/Newegg product photograph | Product record identifies GeForce GTX 580, 03G-P3-1584-AR, 3 GB. Inspect the actual fan, shroud and ports. This illustrates that model, not the authors' exact physical boards. No open license is asserted. |
| Fritzchens Fritz, Core i7-920 photograph | Commons source identifies the package and CC0 1.0 rights. A reviewed polygon/crop removes the holder. Illustrates the CPU role without inventing the experimental host. |
| Original AlexNet paper, Figure 4, page 8 | Extract 30 actual training-image neighbours from the right panel, excluding its test column. Extract the labelled leopard test photograph from the left panel for pixel input and illustrative crop/flip views. Record PDF digest, page, xref, dimensions and extraction bounds. Preserve paper/underlying image rights. |

Sources:
[GTX 580 product record](https://www.newegg.com/evga-03g-p3-1584-ar-geforce-gtx-580-3gb-graphics-card-single-fan/p/N82E16814130655),
[published product image](https://c1.neweggimages.com/productimage/nb640/14-130-655-04.jpg),
[CPU source](https://commons.wikimedia.org/wiki/File:Nehalem_Corei7-920_DSCF1581_(15990812314).jpg),
[original paper](https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf).

Reject mismatched Commons search hits for GTX 590/545/560. Historical EVGA
guide URLs redirected to its home page and were not treated as retrieved
evidence. The ImageNet examples are published ILSVRC-2010 examples; they do not
certify the exact 2012 training-file inventory.

## Deterministic and package checks

All 12 documentary tests pass, including wrong model/memory, missing review or
rights, crop bounds, exact gray/white one-bit colors, original preservation,
cache repair, source tampering, metadata-only status and actual static capture.

```text
uv run --script skills/line-world-video/scripts/test_documentary_assets.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

The qualified release has 321 declared files in six skills, 137 primary runtime
files and 22 adapter files. Both ZIPs contain identical plugin bytes. Actual
task-local Codex marketplace installation, six native `skills/list`
registrations, canonical parity and all 18 installed suites / 207 tests pass.
No global installation or account publication is claimed.

Marketplace archive SHA-256:
`3cda8ff932366055bef176d1a1bbafe869898dff9936c035a7a3257b3ab8c70d`.
Preserve the earlier immutable 0.21.0 development package; the added bundled
capture and integrity helpers ship in 0.21.1.

## Isolated runtime evidence

Model exception remains `openai-codex/gpt-6.1-sol`, medium thinking, because
Spark is unavailable on this account. Use fresh runtime-only workspaces, exact
outputs and strict JSON. The skill payload remains read-only. The final
contract has 16 tool calls; the first final naturalistic run has 22. Both read
only the prompt, entry point, selected compact references and their own assets.

| Run ID suffix after `20261116-documentary-` | Outcome and classification |
| --- | --- |
| `contract-sol`, `natural-sol` | Pre-runtime source gate: missing reference TOC. Skill/source issue fixed before a model run. |
| `contract-final-sol` | Strict pass on earlier payload. |
| `natural-final-sol` | Retained strict failure: temporary paths, unnecessary protected-page request, and ambiguous dual local/URL input. Skill/agent issues; add project-owned acquisition and local-file precedence. |
| `contract-release-sol` | Strict pass on earlier payload. |
| `natural-release-sol` | Retained strict failure: extra evidence qualifier in an exact variant identifier. Clarify normalized identity versus evidence fields. |
| `contract-normalized-sol` | Retained strict failure: ad hoc system Python did not have Pillow. Add integrity/palette checks to the helper rather than relying on a shell import. |
| `natural-normalized-sol` | Retained strict failure: default Playwright browser unavailable. Add bundled screenshot capture using the existing browser selection. |
| `contract-capture-sol` | Final exact-payload contract passes; inspect comparison and metadata-only audit without claiming an actual scene. |
| `natural-capture-sol` | Final exact-payload naturalistic pass; inspect the actual two-card scene and observed binding audit. |
| `natural-capture-sol-2` | Fresh strict pass, 17 tool calls; actual screenshot preserves card identity, separated network diagram and adjacent guide. |
| `natural-capture-sol-3` | Fresh strict pass, 18 tool calls; actual screenshot and observed bindings pass with no implementation/gallery reads. |

The final exact-payload cohort is one contract pass and 3/3 fresh naturalistic
passes, with all output artifacts and screenshots independently inspected.
All three choose grayscale for their static card photographs; the actual film
uses the user's requested minimal one-bit option after final-size review.
Keep every earlier failure; no failed run is counted as a successful forward.

```text
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-documentary-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-documentary-contract-capture-sol --expect-output media/gtx580-gray.png --expect-output media/gtx580-one-bit.png --expect-output media/manifest.json --expect-output comparison.png --expect-output story.json --expect-output object-review.json --expect-output review.md
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-documentary-natural.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261116-documentary-natural-capture-sol --expect-output scene.html --expect-output scene.png --expect-output story.json --expect-output objects.json --expect-output media/manifest.json --expect-output review.md
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261116-documentary-natural-capture-sol/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

## Actual film review

The 1080p30 CUDA/AlexNet revision is 220.6 seconds / 6,618 frames. Its SHA-256 is
`a8c0e72506755516e3e5e982ba077a65c44b06711820b187b8bd24d8fd9025ba`.
There are 36 source/preparation entries, 43 reusable variants and 39 actual
photographic placements. A second prepare reuses all 43 variants. Gray/white
one-bit hardware preserves the primary red for guidance; photographs of image
examples remain grayscale or restrained pixels. The generic hardware/image
helpers are removed. JSON object bindings choose treatment IDs; selected
photograph files participate in per-scene cache inputs.

All ten reading/cue/join montages and full-size revised GPU/contributor/network
views were inspected. The complete decode, 6,618 content frames, 6,618 source
trajectory frames and 258 encoded samples pass. No empty content intervals or
guide-route events were detected. Six 23 px contributor-caption advisories
remain explicitly reviewed at full size. Hash-bound manual notes are recorded.
These tests are not a universal claim of automatic visual understanding.

The visual-only revision preserves all narration/cue text and 38,916,096 bytes
of decoded PCM exactly. This is approved Google Vids Nyla speech in a local
complete assembly, not a new native final export. The native upload permission
blocker remains unchanged. The current revision's resume queue identifies all
ten replacement clips and retains the approved voices.

The source archive `cuda-alexnet-vids-photo-sources-0.21.1-r1.zip` contains 660
manifested files. Its SHA-256 is
`ee68d466c2e9f7b6015a8cc59923e89cd271733816b60fce1062ef0f5e5815d3`.
Clean extraction, every file hash, standalone build and standalone visual audit
pass, including all 43 cached treatments. Source-bundle rebuilding now accepts
project, version and revision arguments, preserving earlier immutable bundles.

Evidence resides under `projects/cuda-alexnet-vids/artifacts/revisions/photo-0210/`,
`artifacts/reviews/photo-review/` and `artifacts/reviews/photo-bindings.json`.
The complete source film, comparison, credits and actual encoded GPU frame are
available in the project artifacts.

## Repository gates

Pattern IDs, independence and payload checks pass. Global structure validation
and global sync retain the same four unrelated semantic reference-route
findings in `curate-semantic-model`, `extract-ontologies` and
`extract-with-ontology`. Scoped primary/adapter validation and bounded local
sync pass: 137/22 canonical files verified. No Pages sources changed, so no
publication or push is required for this project-only media revision.
