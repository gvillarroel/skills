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
- safe zones:
- caption policy:
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
- layout:
- hierarchy:
- safe zones:
- depth layers:
- motion phases:
- renderer handoff:
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
    "safeZones": "",
    "captionPolicy": "",
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
      "validationChecks": [],
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
- `layout`: where major groups sit, stated semantically rather than in pixels.
- `hierarchy`: how #1 and #2 visual priorities are separated.
- `safeZones`: captions, edge margins, face/UI keep-out, text-safe areas, and crop concerns.
- `depthLayers`: at least background, midground, and foreground.
- `motionPhases`: at least a meaningful entrance/development/settle plan, or fewer phases only for a deliberately held read.
- `validationChecks`: concrete checks a renderer can verify with screenshots, DOM, canvas pixels, labels, or manual review.

## Quality Bar

- Preserve literal source anchors. If the input says "92% retention", "June 2026", or a file name, carry it into `sourceAnchors` and the relevant scene.
- Keep text placement intentional. Text never covers a face, key UI, dense chart labels, or the caption band.
- Keep the hero large enough for video. If the main visual would read as a small web card, scale the concept up or change composition.
- Include at least three depth layers for normal scenes. A deliberate title card or held CTA can be simpler if the rationale says so.
- Explain rejected alternatives. This is what makes the brief teach how the choice was made.
- Avoid renderer-specific implementation in planning artifacts. Name `count-up`, `draws on`, `pushes through`, `locks in`, or `holds still`; do not specify JS timelines.
- Allow Anime.js in `rendererHandoff` when it is a suitable downstream runtime. Do not treat Anime.js as forbidden; only GSAP-related terms are forbidden by default.
- For multi-scene pieces, preserve continuity through stable roles, palette, type, spacing, or tracked objects, and vary armature when scenes have different jobs. Do not specify a repeated background sweep or ambient validation motion unless it has the same semantic role in every scene.
