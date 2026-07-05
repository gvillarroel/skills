# Composition Brief Contract

Use this contract when writing a scene composition handoff. Keep it renderer-neutral unless the user asks for implementation. The brief may mention a later renderer skill or Anime.js handoff, but it should not contain implementation code, GSAP timelines, library imports, or exact CSS/animation parameters.

## Markdown Brief

Use this structure for `composition-plan.md`:

```markdown
# Composition Plan

## Video Direction
- format:
- source anchors:
- palette/type source:
- alignment mode:
- edge/corner policy:
- box interior policy:
- grayscale hierarchy scale:
- safe zones:
- caption policy:
- editorial text policy:
- functional text policy:
- operating model:
- megacanvas:
- zones:
- camera path:
- rhythm:
- held scenes:
- negative list:

## Scene 1 - <title>
- id:
- duration:
- source anchors:
- scene job:
- viewer task:
- composition choice:
- rejected alternatives:
- choice rationale:
- focal:
- roles:
- armature:
- alignment grid:
- edge policy:
- corner policy:
- box interior policy:
- box model:
- grayscale hierarchy:
- megacanvas role:
- section bounds:
- camera path:
- functional text policy:
- editorial text policy:
- armature anchors:
- object bounds:
- layout:
- hierarchy:
- safe zones:
- depth layers:
- motion phases:
- renderer handoff:
- validation contract:
- validation checks:
- risks:
```

## JSON Plan

Use this shape for `composition-plan.json`:

```json
{
  "version": 1,
  "format": "1920x1080",
  "videoDirection": {
    "sourceAnchors": [],
    "paletteTypeSource": "",
    "alignmentMode": "",
    "edgeCornerPolicy": "",
    "boxInteriorPolicy": "zero internal padding; content flush to declared bounds",
    "grayscaleHierarchyScale": [
      { "level": 0, "role": "primary", "grayHex": "#333333" },
      { "level": 1, "role": "secondary", "grayHex": "#696969" },
      { "level": 2, "role": "tertiary", "grayHex": "#9c9c9c" }
    ],
    "safeZones": "",
    "captionPolicy": "",
    "editorialTextPolicy": "",
    "functionalTextPolicy": "",
    "operatingModel": "fixed-frame",
    "megacanvas": null,
    "zones": [],
    "cameraPath": [],
    "rhythm": "",
    "heldScenes": [],
    "negativeList": []
  },
  "scenes": [
    {
      "id": "scene-01",
      "title": "",
      "duration": "",
      "sourceAnchors": [],
      "sceneJob": "",
      "viewerTask": "",
      "compositionChoice": "",
      "rejectedAlternatives": [],
      "choiceRationale": "",
      "focal": "",
      "roles": {},
      "armature": "",
      "alignmentGrid": "",
      "edgePolicy": "",
      "cornerPolicy": "",
      "boxInteriorPolicy": "zero internal padding; no inset labels, chips, or nested panels",
      "boxModel": {
        "internalPaddingPx": 0,
        "contentFlushToBounds": true,
        "separation": "external gutters only"
      },
      "grayscaleHierarchy": [
        { "level": 0, "role": "primary", "grayHex": "#333333" },
        { "level": 1, "role": "secondary", "grayHex": "#696969" },
        { "level": 2, "role": "tertiary", "grayHex": "#9c9c9c" }
      ],
      "megacanvasRole": "",
      "sectionBounds": [],
      "cameraPath": [],
      "functionalTextPolicy": "",
      "editorialTextPolicy": "",
      "armatureAnchors": [],
      "objectBounds": [],
      "layout": "",
      "hierarchy": "",
      "density": "",
      "safeZones": "",
      "depthLayers": [],
      "motionPhases": [
        {
          "name": "entrance",
          "cue": "",
          "visualChange": "",
          "motionVerb": ""
        }
      ],
      "captionPlan": "",
      "rendererHandoff": "",
      "validationContract": {
        "alignment": "",
        "safeZones": "",
        "edgePolicy": "",
        "boxPadding": "internalPaddingPx is 0 and content is flush to bounds",
        "grayscaleHierarchy": "Each hierarchy level uses a distinct monotonic grayscale hex value",
        "focalHierarchy": "",
        "verificationArtifacts": []
      },
      "validationChecks": [
        {
          "method": "screenshot-review",
          "target": "scene-01 keyframe",
          "passCriterion": "Major objects align to the declared grid and safe zones."
        }
      ],
      "risks": []
    }
  ]
}
```

## Required Scene Fields

Every scene should include:

- `id`: stable scene or shot ID from the input when available.
- `sceneJob`: what the scene must do in the story.
- `viewerTask`: what the viewer must do visually.
- `compositionChoice`: named family such as centered hero, asymmetric editorial, split screen, grid, diagonal armature, radial hub, flow spine, or dense label lanes.
- `choiceRationale`: why this choice fits the scene better than alternatives.
- `focal`: the hero object or idea.
- `roles`: role map for visible objects, such as foreground subject, background, supporting, caption rail, data field, label lane, or CTA.
- `armature`: the geometric or reading-path structure.
- `alignmentGrid`: explicit grid, axis, baseline, or modular system that major objects attach to.
- `edgePolicy`: whether panels, masks, apertures, and frames are square, rectangular, hard-edge, soft, or inherited from source media.
- `cornerPolicy`: specific corner rule, such as 0-radius, square corners, source-native corners only, or allowed radius.
- `boxInteriorPolicy`: whether boxes allow internal padding. For no-padding, hard-edge, Metro, terminal, blueprint, or strict-grid styles, require zero internal padding and content flush to declared bounds.
- `boxModel`: structured box model with `internalPaddingPx: 0`, `contentFlushToBounds: true`, and separation via external gutters only. Do not include any positive `padding`, `paddingPx`, `boxPaddingPx`, or `internalPaddingPx` value anywhere in strict no-padding plans.
- `grayscaleHierarchy`: structured hierarchy scale with at least three levels. Each item should include `level`, `role`, and a distinct `grayHex` where R=G=B; gray values should be monotonic by level.
- `megacanvasRole`: for Metro, Masonry, strict-grid, or design-repair prompts, state whether this scene is overview, detail, transition, or return-to-system inside the larger navigable object. Use `not-applicable` only for true fixed-frame styles.
- `sectionBounds`: for megacanvas plans, list functional sections with IDs, roles, and relative bounds or grid tracks.
- `cameraPath`: for megacanvas plans, list overview/detail frames, pan/zoom targets, and expected framing outcome. Each target should name the zone it reveals and what remains visible as context.
- `functionalTextPolicy`: what text is allowed because it belongs to visual objects, such as values, axes, states, node names, table cells, or data-bearing marks.
- `editorialTextPolicy`: for Metro/design-repair prompts, set to `none`; do not reserve title, subtitle, caption, checked-date, draft-label, CTA, or narration-summary bands unless explicitly requested.
- `armatureAnchors`: concrete focal, axis, baseline, split, vanishing point, or grid anchors that organize the frame.
- `objectBounds`: semantic bounds for major groups so a renderer can check placement, overlap, and safe-zone clearance.
- `layout`: where major groups sit, stated semantically rather than in pixels.
- `hierarchy`: how #1 and #2 visual priorities are separated.
- `safeZones`: captions, edge margins, face/UI keep-out, text-safe areas, and crop concerns.
- `depthLayers`: at least background, midground, and foreground.
- `motionPhases`: at least a meaningful entrance/development/settle plan, or fewer phases only for a deliberately held read.
- `validationContract`: per-scene proof targets for alignment, safe zones, edge/corner policy, focal hierarchy, and expected verification artifacts.
- `validationChecks`: structured checks a renderer can verify with screenshots, DOM, canvas pixels, labels, or manual review. Prefer objects with `method`, `target`, and `passCriterion`.

## Quality Bar

- Preserve literal source anchors. If the input says "92% retention", "June 2026", or a file name, carry it into `sourceAnchors` and the relevant scene.
- Keep text placement intentional. Text never covers a face, key UI, dense chart labels, or the caption band.
- Keep the hero large enough for video. If the main visual would read as a small web card, scale the concept up or change composition.
- Include at least three depth layers for normal scenes. A deliberate title card or held CTA can be simpler if the rationale says so.
- Explain rejected alternatives. This is what makes the brief teach how the choice was made.
- Avoid renderer-specific implementation in planning artifacts. Name `count-up`, `draws on`, `pushes through`, `locks in`, or `holds still`; do not specify JS timelines.
- Allow Anime.js in `rendererHandoff` when it is a suitable downstream runtime. Do not treat Anime.js as forbidden; only GSAP-related terms are forbidden by default.
- For multi-scene pieces, preserve continuity through stable roles, palette, type, spacing, or tracked objects, and vary armature when scenes have different jobs. Do not specify a repeated background sweep or ambient validation motion unless it has the same semantic role in every scene.
- For strict-grid or Metro-style plans, require square or 0-radius edge/corner policy and include a validation check for grid alignment, shared baselines, and unchanged corner radius. Do not say rounded cards, pills, soft edges, blobs, or positive radius unless the field explicitly says a source-native exception is being preserved.
- For no-padding box critiques, reject padded cards, inset bars, internal chips, nested panels, and labels placed inside boxes with padding. Use external gutters, boundary labels, or adjacent lanes instead.
- For hierarchy-level critiques, assign levels with grayscale values, not only opacity or hue. Hue can express semantic state, but grayscale should carry level separation.
- For Metro Minimal Tonal Motion, require `operatingModel: navigable-megacanvas`, populated `megacanvas`, `zones`, scene `sectionBounds`, scene `cameraPath`, `editorialTextPolicy: none`, and a functional text policy that subordinates labels to visible marks, state, motion, or data.
- For Masonry, require varied module sizes, shared edges, external gutters, a construction order, and a transition plan where blocks fit, push, reveal, expand, or collapse. A grid of equal cards does not satisfy Masonry.
