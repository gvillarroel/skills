Use `$one-bit-dither-svg` from `skills/one-bit-dither-svg/` to complete this task in the isolated workspace.

Do not read acceptance fixtures or any repository path outside the copied skill and this prompt. Do not modify any file under `skills/one-bit-dither-svg/`. Keep every generated artifact inside the workspace under `result/`. Do not write or read `/tmp`, an absolute path, or any location outside this isolated workspace.

Create `result/source.animated.svg`, a self-contained 640×360 SVG bar-chart animation with no JavaScript and no external resources. It must use declarative SMIL or CSS animation. Include a readable title, five labeled bars, visible values, axes, and a staggered two-second growth sequence. Make the bars change substantially across the timeline and return cleanly to the first state after two seconds.

Pass that SVG directly to the shipped animated-image transformer—do not pre-render it to GIF or call another skill. Create `result/styled.gif` in `custom` mode with exactly `#1b4d3e` plus white. Use the `detailed` quality profile, exact 1280×720 output dimensions, 12 fps, a two-second SVG capture window, a two-color encoding palette, and infinite looping. Also create:

- `result/styled-contact.png`
- `result/styled.json`

Run the shipped animated-GIF validator. Supply the conversion manifest and require custom mode with exact color `#1b4d3e`, SVG source kind and format, 1280×720 dimensions, approximately 12 fps, loop value 0, at least 24 frames, at least 10 visually distinct frames, and no more than two colors. Write its JSON report to `result/styled-validation.json`.

After validation, inspect the contact sheet and GIF directly with the image-reading tool. Confirm that the bars visibly grow in sequence and the title, labels, and values remain recognizable. Once the visual review, shipped validator, and five exact output paths pass, stop without custom pixel-analysis scripts.
