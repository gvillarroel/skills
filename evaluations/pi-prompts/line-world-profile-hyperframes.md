Create a clean eight-second native HyperFrames HTML composition at
`film/index.html`, with 1920x1080 dimensions and 30 fps. Divide the entire frame
into two equal columns. Show a simple geometric queue on the left and its item
count on the right, both derived from count=15*t/8. Keep source units as items,
white surfaces, neutral thin lines and one red attention dot. No visible title,
chapter badge, slogan or explanatory banner. Put any transport controls outside
the composition.

Use the real bundled GSAP library and register one paused timeline driving pure
`window.renderAt(seconds)` and `window.snapshot()`. Do not start an independent
animation loop. Write editable `film/timing.json` and actually inspect browser
states at 0, 4 and 8 seconds plus a repeated backward seek. Save
`review/frame.png` and `review/seek-check.json` with actual values and check
results. No npm install or encoded MP4 is required for this producer test.
Keep the copied skill read-only and use only its own resources and normal tools.
