Use `$one-bit-dither-svg` from `skills/one-bit-dither-svg/` to complete this task in the isolated workspace.

Do not read acceptance fixtures or any repository path outside the copied skill and this prompt.

Create two raster inputs:

1. `result/source.png`: a self-contained 480×320 RGBA image with transparent rounded outer corners, a dark blue background, a warm orange sun, a pale tower with two dark windows, a green hill, four thin white wave lines, and the small visible label `NORTH 47`.
2. `result/animated.gif`: a two-frame 320×200 animated GIF. Frame zero must contain a large blue circle on a pale background. Frame one must instead contain a large orange triangle, a green horizontal stripe, and a small black square. Make the two frames unmistakably different.

Transform `source.png` into all three palette modes with `--quality-profile detailed`:

- `result/png-original.svg` in `original` mode.
- `result/png-custom.svg` in `custom` mode using exactly `#145da0`.
- `result/png-regional.svg` in `regional` mode.

Transform frame one of `animated.gif` to `result/gif-frame1.svg` in `regional` mode using `--frame 1` and `--quality-profile balanced`.

For every transformed SVG, create a same-basename PNG preview and JSON conversion report. Run the shipped validator for each output, requiring the corresponding mode, `raster` source kind, exact source format (`PNG` or `GIF`), and exact source frame; also require the custom color where applicable. Write validator reports as:

- `result/png-original-validation.json`
- `result/png-custom-validation.json`
- `result/png-regional-validation.json`
- `result/gif-frame1-validation.json`

Inspect the previews. The PNG outputs must retain the tower, hill, sun, waves, transparent corners, and distinguishable label area. The GIF output must visibly correspond to frame one—the orange triangle, green stripe, and black square—and not frame zero's blue circle. Finish only after all four validators pass. Do not modify any file under `skills/one-bit-dither-svg/`.
