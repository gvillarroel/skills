# Real objects and photographic treatments

## Contents

- [Select and verify](#select-and-verify)
- [Prepare once](#prepare-once)
- [Place and inspect](#place-and-inspect)

Prefer a researched photograph when the scene identifies a real physical
object, product, place or specimen. A documented GTX 580 should appear as a
GTX 580 photograph, not as a generic chip drawn to impersonate that card.
Apply this decision to other objects in the scene, not only the first example.
Use sourced photographs for examples of photographs too; avoid repeating a
mountain pictogram as a substitute for actual image data.

Keep diagrams for mechanisms, relationships, quantities, architecture and
functional cutaways. A photograph can identify a card beside a diagram that
explains how the model is split across two cards. The useful distinction is
the explanatory purpose. Do not replace a graph, mathematical function or
original-paper diagram with an unrelated photograph merely because an image
search returns one.

## Select and verify

1. Inventory the visible real objects before drawing. Record each object's
   scene, stable ID, purpose and chosen representation in `scene.objects`.
2. Search official media, archives, museums or Commons. The bundled
   `media_assets.py search` offers a bounded Commons candidate search. Inspect
   the actual photograph and source page; verify the exact model, variant,
   historical date and viewpoint needed by the explanation. Search results can
   mix GTX 580, GTX 590 and several memory variants. A filename is not identity
   evidence. Never pass a different model through a filter to disguise a mismatch.
3. Prefer a clean, adequately sized source and keep its original bytes, digest,
   source page, creator, rights and credit. Do not invent an open license for a
   vendor photograph. Keep an illustrative CPU separate from a claim about the
   exact host used in a historical experiment. State that scope in the source
   record. Do not add production disclaimers to narration when no claim needs one.
4. Preserve identities while simplifying appearance. Try the original on white,
   then grayscale or a restrained edge treatment. Pixelation and ordered one-bit
   dithering are available when they preserve recognition at the delivered size.
   Obra Dinn can guide the monochrome dither texture; keep the real source's
   silhouette, fan, ports and other identifying features. Never generate a
   substitute documentary object or use a filter to invent missing evidence.

## Prepare once

Use the self-contained helper; optional external image skills are not required:

```text
uv run --script <skill-root>/scripts/documentary_assets.py fetch --url https://example.org/card.jpg --output media/sources/card.jpg
uv run --script <skill-root>/scripts/documentary_assets.py prepare --request photos.json --output media/objects --comparison media/comparison.png
uv run --script <skill-root>/scripts/documentary_assets.py audit --story story.json --manifest media/objects/manifest.json --output object-review.json
```

The request contains an `assets` array. Each reviewed entry needs `id`, `label`,
`sourcePage`, `identityEvidence`, `scope`, `reviewed: true`, `rights` with
`creator`, `license` and `credit`, and either `sourceFile` relative to the request
or `downloadUrl`. When both are supplied, use the local file and retain the
download URL as provenance. Pin `sourceSha256` after acquisition. Optional
`model: {expected, observed}` and `variant: {expected, observed}` reject declared
identity mismatches. Use exactly the same normalized identifier in `expected`
and `observed` when they match; put source qualifiers and explanations in
`identityEvidence`, not inside one identifier. These checks do not perform
visual recognition.
`crop: [x0,y0,x1,y1]` uses EXIF-oriented source pixels. Optional
`subjectPolygon` uses the same coordinates to remove a reviewed background;
leave the complete subject inside it. `flip` mirrors a prepared image only when
that transformation preserves the example's meaning.

```json
{"assets":[{"id":"documented-card","label":"Documented card",
"sourceFile":"original.jpg","sourcePage":"https://example.org/archive/card",
"identityEvidence":"Reviewed source photograph and model specification",
"scope":"Illustrates the model; not the experiment's exact physical specimen",
"reviewed":true,"model":{"expected":"Model A","observed":"Model A"},
"rights":{"creator":"Archive author","license":"Recorded source terms",
"credit":"Archive author; source page retained"},"width":640,
"treatments":[{"id":"gray","mode":"grayscale"},
{"id":"one-bit","mode":"one-bit","ink":"#696969","cell":2}]}]}
```

Modes are `photo`, `grayscale`, `edges`, `pixel` and `one-bit`. Use canonical
gray `#696969` for quiet derived objects; keep primary red for selective focus.
Avoid making every photograph red or filling a slide with dark dither texture.
Preserve original colors when color itself carries evidence. `cell` controls
pixel/dither density; `levels` controls pixel grayscale levels. Start with two
pixel dither cells at the actual display size. The helper preserves originals,
bakes each treatment once, exports PNG plus a self-contained SVG, writes credit
and lineage records, and reuses unchanged variants by digest. Its bundled
one-bit engine is a pinned copy adapted from the repository's one-bit skill;
do not read that large implementation during ordinary use.

Keep downloaded sources, request JSON, comparisons, screenshots and review
records inside the current project. Use workspace-relative paths in an isolated
run; do not move them to a system temporary folder or assume `/tmp` exists on
Windows. Use `fetch` for a compact, checked acquisition receipt, then inspect
the local image. If the user supplies reviewed identity/source facts, preserve
them as supplied evidence and inspect the photograph; an unnecessary protected
product-page fetch should not derail the preparation task. Do not bypass a
source's access rejection.

## Place and inspect

Use rectangular image bounds with aspect-preserving `meet` fitting. Do not
circle-crop hardware, add decorative card borders or hide distinctive ports.
Place diagrams and guide paths beside the photo. Reserve an adjacent semantic
port around the photo plus its essential label. Use a fixed baked treatment
throughout the shot so a dither pattern does not change on every frame.

Declare a physical identity view as
`{"id":"card-left","kind":"physical","purpose":"identity","depiction":"photo-treatment","asset":"documented-card","variant":"one-bit"}`.
Declare an explanatory diagram with `kind: "concept"`, `purpose: "mechanism"`,
`depiction: "diagram"` and a concrete `reason`. The audit rejects an unreasoned
physical identity diagram and missing asset/variant bindings. With
`--html composition/index.html`, it also checks rendered `[data-object-id]`
wrappers and their `[data-documentary-id]` image references against the selected
manifest file. Metadata-only audit reports rendered verification as pending.

For a static HTML or SVG prototype, use this minimal binding contract without
reading the helper implementation:

```html
<section id="scene-hardware">
  <div data-object-id="card-left">
    <img data-documentary-id="documented-card"
         src="media/objects/documented-card-one-bit.png" alt="Documented card">
  </div>
</section>
```

Give that wrapper visible, nonzero layout dimensions. The matching story is
`{"scenes":[{"id":"hardware","objects":[{"id":"card-left","kind":"physical","purpose":"identity","depiction":"photo-treatment","asset":"documented-card","variant":"one-bit"}]}]}`.
Run `audit --story story.json --manifest media/objects/manifest.json --html scene.html --screenshot scene.png --output object-review.json`.
The audit verifies source, prepared and variant digests and exact one-bit inks.
With HTML it also checks rendered bindings and can capture the actual scene
using the bundled browser selection. Inspect that screenshot with the image
reader. Use this option instead of writing a new Playwright launcher for each
static prototype. The metadata-only command needs no browser. These checks
already cover byte preservation and the one-bit palette; do not recreate them
in an ad hoc Python shell. If another custom check needs Pillow or Playwright,
declare it with `uv run --with pillow` or `uv run --with playwright` rather than
assuming those packages are installed in system Python.
Do not delete the source request, receipt,
prepared image or credits after review: these small records make later changes
and cached reuse cheaper.

Inspect original and treatments side by side at final display size. Reject an
edge-only silhouette that loses recognition, coarse pixels that erase the
subject, noisy backgrounds, cropped parts, distorted aspect ratios and flashing
textures during pans. The photographic record remains authoritative; a derived
SVG of pixel rectangles is not original vector artwork. Preserve the approved
speech and measured cue times during a visual-only change, then audit the new
target bounds, routes, affected scenes and neighboring joins.
