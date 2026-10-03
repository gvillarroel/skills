# Reject an unreadable palette

I want to use the bundled compact SVG composition as a planning handout. Start from its template and create `outputs/boundary/brief.json`, with a requested white canvas, white panels, and near-white explanatory text: `theme.colors.canvas = "#ffffff"`, `theme.colors.surface = "#ffffff"`, and `theme.colors.muted = "#eeeeee"`. Preserve the rest of the template's modeled data and modules.

Check whether the skill supports these colors without compromising its own readability contract. Save the actual bundled preflight result as `outputs/boundary/preflight.json`. In `outputs/boundary/explanation.md`, explain the supported outcome and identify the responsible color role. Do not silently change the requested colors, publish an invalid SVG, or claim a successful validation when the report rejects the input.

Use only `skills/compose-synchronized-svg/` as a read-only bundle. Do not read acceptance examples, sibling skills, repository context, or network sources. All generated files must stay in the workspace at the exact requested paths. This task stops at validation of the supplied palette; a corrected palette or SVG is not requested.
