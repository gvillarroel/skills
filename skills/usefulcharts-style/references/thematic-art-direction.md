# Thematic art direction

Use this guide for subject-specific poster treatments, such as spacecraft in dark space, maritime histories or richly illustrated scientific collections. It also applies when planning those outputs without drawing. Keep the information-sufficiency, editorial-selection and knowledge-density requirements from the entry point.

## Choose a visual system

Write a short art-direction contract alongside the source data: atmosphere, palette, focal subjects, camera direction, lighting, material treatment, background activity and what the visual metaphor encodes. Give each choice a purpose. A space chronology can place a right-facing ship at the end of its dated wake; a botanical lineage can use specimens beside branches. Neither requires copying the same paper-and-box treatment across subjects.

Keep semantic category colors distinguishable within the chosen palette. Use illustration scale for editorial emphasis only when physical scale is not encoded, and say so. Reserve quiet fields behind dense explanations. Vary focal groups and supporting records according to importance; decorative backgrounds and larger pictures do not increase knowledge density.

## Produce recognizable artwork

Keep facts and illustration production separate. Bind each asset to a record ID and its verified name/class; chronology and captions come from the evidence data. A search caption or generated hull label cannot establish the identity or date of a ship. Open candidate references and confirm visible distinguishing features before using them. Prefer authoritative photographs, physical-model photographs or production frames when exact objects matter.

Use the available image-generation tool for individual subjects when it improves the result; follow that tool's instructions. Generate a representative focal asset first and inspect it before repeating the treatment. Specify:

- Exact subject and distinguishing geometry from the inspected reference.
- Complete silhouette, sufficient crop margin, facing direction, elevation and perspective.
- Shared lighting and materials while retaining authentic subject colors.
- Intended placement size and background treatment; exclude stands, captions and factual diagram marks from the image.

Generate the atmospheric background separately from subjects, dates and connectors. Keep text, routes and time scales in SVG or HTML, so revisions do not require the image model to redraw facts. Save accepted prompts, reference URLs, asset IDs, actual outputs and relevant rejected attempts in a manifest beside the deliverable.

For a planning-only prompt pack, define one shared camera, lighting and output contract, then apply it explicitly to every subject prompt. Match the background aspect ratio to the proposed canvas. Keep record dates and placement rules in adjacent metadata, outside the generated subject's prompt. State **no trails or motion streaks** in subject prompts when vector wakes carry duration: even a small baked forward streak can contradict the direction or evidence. Ask for the complete object alone. Distinct record IDs do not imply different designs; two hulls of one class may share geometry. Require reference evidence before adding newer fittings or silhouette changes to a successor.

An effective starting contract is: `complete subject; elevated three-quarter dorsal view; bow right; shared cool upper-left key light; authentic subject colors; no background scenery, display stand, captions, dates, trails or motion streaks`. Adapt the camera and lighting to the subject rather than making this example universal. Pair that common contract with each asset's verified distinguishing features and pending photograph identifier. Do not label an absent photograph as verified or a prompt pack as production-ready.

Inspect generated files themselves. A painted checkerboard is not transparency: check alpha and view edges against the destination background. Inspect interior gaps, stands, missing extremities, unrelated designs and invented structural features. Repair a defective asset with the image tool or reject it. If genuine alpha is unavailable, a uniform dark background may support compositing on dark space; verify the actual composite and its PDF export, because a rectangular matte or blending shift can survive unnoticed in a thumbnail. Preserve provenance and do not describe a solid-black image as transparent.

If generation is unavailable or blocked, retain the inspected reference or another suitable asset within the user's scope, and state the limitation. Do not report a successful generation or silently replace the subject with an unrelated silhouette. A useful local fallback is to leave a reserved focal footprint and continue the editable data composition.

## Bind a thematic duration mark

For an object's dated wake, establish the chapter's linear mapping before art placement:

```text
x(year) = plot_left + (year - first_year) / (last_year - first_year) * plot_width
```

Draw an exact, sharp core between supported interval endpoints. A glow may soften that core, but the legend and endpoint markers must make the interval unambiguous. Place the subject just beyond the endpoint marker, with any illustration overhang excluded from the measured duration. Reserve the complete image viewport and label envelope before packing neighboring records.

Use a continuous wake only for a supported service or mission interval. A first and last sighting do not prove continuous service: use dated points and a broken connector. Keep uncertain ranges, loss, reactivation and off-scale time jumps distinct. A single known year remains a point even if a longer trail would look more exciting. Explain whether length represents years, physical distance or another quantity; never interchange them. Any ambient animation may change glow intensity, but must not move the quantitative endpoints. Respect reduced motion and freeze decorative animation for export.

The bundled renderer may not support a selected metaphor. Author a custom SVG outside the read-only skill bundle when needed, retaining equivalent source inventory, actual date-position and browser geometry checks. Do not invent renderer options or distort the data into a supported layout.

## Review the composition and exports

Open the whole poster, a dense region and each focal image at its placed size. First identify the largest visible problems: subject identity, composition, readability, image integration or weak hierarchy. Repair those problems and inspect the changed output. Check text/image clearance as well as text/text clearance; reserve whitespace for actual font bounds, not just baselines. In mixed-size paragraphs, measure separate runs and provide visible separation before source credits.

Measure text contrast against the actual composited background, including bright stars or texture behind small labels. A nominal dark palette does not prove contrast on a textured image. Recheck readable density and its distribution after adding larger illustrations or growing the canvas. Compare the raster preview and rendered PDF for retained imagery, clipping, blend modes, selectable factual text and font resources. Exercise the offline viewer and exports if supplied. Separate technical acceptance, factual confidence and the remaining visual differences; a clean audit never establishes reference-level parity by itself.
