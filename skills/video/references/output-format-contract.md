# Output Format Contract

## Declare exact media properties

Store these values in the scene contract before composition:

- integer `width` and `height` in pixels;
- reduced `aspectRatio` string derived from those integers;
- positive `fps` and `durationSeconds`;
- background color or transparency policy;
- safe-area margins in pixels;
- pixel-density policy for browser capture;
- scaling policy for each asset: `contain`, `cover`, `stretch`, or `none`;
- output paths and codec/container expectations.

Treat dimensions as exact API values. A request for 1080×1920 is not permission to build at 720×1280. Verify the encoded stream with ffprobe.

## Ratio-aware composition

- Compose against the requested canvas, not a generic 16:9 master that will be cropped later.
- Use normalized element bounds in the contract so the same semantic layout can be recalculated for another ratio.
- Create a separate layout variant when a simple scale would make labels, ports, or focal objects too small.
- Keep safe areas explicit. Do not infer caption or platform UI zones unless the user requests a platform preset.
- For multiple requested ratios, share asset IDs and semantic events but allow different bounds, camera paths, and text wrapping per variant.

## Validation

Check that every element remains within the frame unless `overflow: allow` is intentional, every normalized port remains within its element, raster assets do not exceed declared upscale limits, and the final MP4 matches width, height, fps, and duration within the stated tolerance.
