---
name: colorsets
description: Apply the user's original colorset1 or colorset2 palette and Open Sans typography to HyperFrames videos through its native frame.md design specification. Use colorset1 by default and colorset2 when explicitly selected.
---

# Colorsets for HyperFrames

Apply the selected visual identity through HyperFrames' native design spec.
Read [HyperFrames](../hyperframes/SKILL.md) and its
[look reference](../hyperframes/references/look.md) for the video workflow.

## Select the style

Use **colorset1** when no colorset is named. Use **colorset2** when requested.
Read the selected preset and its original YAML values:

| Selection | Native design preset | Original definition |
| --- | --- | --- |
| colorset1 | [FRAME.md](assets/colorset1/FRAME.md) | [colorset1.yml](assets/colorset1/colorset1.yml) |
| colorset2 | [FRAME.md](assets/colorset2/FRAME.md) | [colorset2.yaml](assets/colorset2/colorset2.yaml) |

The YAML files preserve the user's original colors, roles and font declarations.
The preset exposes those colors and typography as native design frontmatter.

## Apply the style

Read the first existing project-root spec in this order: `frame.md`, `design.md`,
`DESIGN.md`. When one exists, reconcile its colors and typography with the
selected colorset while preserving the person's content and other design work.
When none exists, copy the selected `FRAME.md` into the project as `frame.md`.

Use the exact selected colors and Open Sans family. Material Symbols Rounded is
available for icons when needed. Follow the original font-loading rules for any
family that is not bundled by HyperFrames.

Expose the selected palette and fonts through the original root
`data-composition-variables` mechanism and reference those variables in scenes
and registry components. Preserve source photographs, footage and artwork as
directed by the original HyperFrames workflow.

Continue with the original authoring, animation, preview, check and render steps.
Composition, narrative, dimensions, timing and effects follow that workflow and
the user's request.
