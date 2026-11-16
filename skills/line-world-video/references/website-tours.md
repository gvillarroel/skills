# Tutorials from real website screenshots

## Contents

- [Capture light interfaces](#capture-light-interfaces)
- [Capture observed states](#capture-observed-states)
- [Write the timed tour](#write-the-timed-tour)
- [Build, inspect and export](#build-inspect-and-export)

Use this mode to teach navigation or participation in a real website. Preserve
the actual interface and its labels, rather than drawing a lookalike. Explain
what the viewer can do, where it leads and any account requirement. Keep
visible presentation titles opt-in. UI headings already present in a capture
are source content. The white/gray/red theme applies to added composition and
the guide; preserve the site's captured native light theme and semantic colors.
Do not apply secondary-photo grayscale/color focus to an entire UI screenshot.

## Capture light interfaces

Use the website or application's supported **Light** appearance setting before
taking screenshots. Verify the visible canvas, menus and account dialogs;
`Auto` may inherit a dark system preference. Keep every capture in the same
light theme and record `source.theme: "light"` with the selected control in
the capture-session metadata. If no light setting is available, resolve that
capture limitation before delivering a dark view. Do not invert or recolor
screenshots to simulate a website theme. Preserve the actual source UI.

The builder rejects declared dark captures and regions dominated by dark
neutral UI. Its sampled-background check catches a regression, but does not
prove the native appearance option was selected. It never modifies capture
pixels and does not impose the composition's approximate color proportions
on website UI. Review the actual source setting and encoded result.

## Capture observed states

Use the supported browser interface for live navigation and screenshots. The
bundled renderer only consumes local captures; it never controls a live site
or uses an account. Follow the browser's own screenshot/export instructions.
Record canonical source URLs, capture date, image dimensions, signed-in/out
state and what actions actually occurred. Keep captures and metadata together.
Exclude tokens, private account panels and unrelated personal information.

Resolve a control from the current visible state. Hydration can replace inputs;
several hidden fields can share a placeholder. Prefer the actual visible
textbox role/name and inspect the new destination after navigation before
saving its screenshot. A scoped locator that disagrees with a visible modal
needs a fresh supported AX/screenshot check, not a guessed selector loop.

A tutorial does not itself authorize sending a comment, publishing a post or
creating an account. Stay within the requested actions and preserve real
account/permission gates. A signed-out participation prompt is useful evidence;
explain that prerequisite instead of inventing an available composer or a
successful submission. Keep source rights and attribution honestly recorded.

Record control rectangles in **screenshot pixels** as `[x,y,width,height]` and
an adjacent guide `port: [x,y]`. Prefer observed DOM/AX bounds, converting from
CSS pixels when the capture's pixel scale differs; inspect the final raster.
Do not assume device pixel ratio one. Include complete control labels. Reserve
space outside text, icons, avatars and separators. Annotate nearby obstacles
with `avoid: [[x,y,width,height]]` when they are not already a target.
Sampled coordinates alone do not provide OCR coverage or identity verification.

## Write the timed tour

Keep one project-owned story and all its media inside the project root:

```json
{"fps":30,"source":{"url":"https://example.org/","capturedAt":"2026-11-16",
"provenance":"Actual authorized browser capture","accountState":"signed out"},
"scenes":[{"id":"find-topic","capture":"media/search.jpg","duration":7,
"region":[0,0,1000,600],"scale":1.6,
"targets":{"search":{"box":[200,90,400,50],"port":[180,115]}},
"cues":[{"target":"search","at":1.2,"phrase":"search field"}]}]}
```

`region` is `[left,top,right,bottom]`, a crop of the unchanged source pixels.
Omit it to use the whole screenshot. Crop away irrelevant ads/panels when that
preserves the needed context; retain the complete active control. Small crops
are centered in white space. Large regions pan inside a full-frame viewport.
Choose a readable `scale`, usually 1.6--2 for a typical desktop capture. Use one
gentle initial entry and fixed-scale pans afterward. The helper routes the dot
around annotated controls with the existing focus runtime, with a white halo
for contrast on dark source UIs. Do not add filled highlight boxes over labels.
If it cannot find a clear route, reserve a better port/lane and rebuild.

For narration, provide `audio: "audio/scene.wav"`, `audioLead: 0.65` and a
duration covering actual measured audio plus entry/reading holds. Record the
real voice provider. Use measured word boundaries or reviewed audio timings for
`cues[].at`; they include the lead and are local to the scene. The builder
checks actual audio extents, not script word-count estimates. It does not
generate voices or certify independent speech alignment. Preserve an approved
voice when changing only crops, ports or camera motion.

## Build, inspect and export

```text
uv run --script <skill-root>/scripts/website_video.py build --project film --story film/story.json
uv run --script <skill-root>/scripts/website_video.py render --project film --output film/final.mp4 --report film/review.json --poster film/poster.png
```

Use `render ... --audit-only` before a long export. Build writes `index.html`,
`preview.html`, `tour.json`, `tour.js` and both local runtimes. Do not hand-edit
compiled story/HTML to change timings; edit the source JSON and rebuild.
`render` checks every frame for guide/control collisions and each spoken
arrival for complete annotated control bounds. It tests backward/repeated
seeking, saves actual cue images and validates original capture/audio digests.
Review the actual screenshot and pointer at every cue: the helper cannot tell
that a rectangle refers to the wrong visually similar control.

Exact-frame silent clips are cached by their actual source/runtime/state.
Unchanged complete output is reused by digest. Narration is assembled as one
sample-aligned PCM track and AAC is encoded once, avoiding repeated scene
encoder delays. The final movie is fully decoded and its frame count verified
before atomic replacement. Silent stories remain explicitly silent. Source
screenshots, actual voices, region/port choices and provider timing precision
remain editable/auditable in the project. These are local outputs; native
Google Vids completion still needs its actual editor/export workflow.

Serve `film/preview.html` over localhost to play/scrub the same movie clock and
supplied audio. Preview controls stay outside the encoded frame. For full-film
review use the existing encoded review with measured scene durations and cue
times. Use this renderer's raster/control audit for source clearance: treating
an entire website screenshot as an indivisible photographic obstacle would
misclassify clear UI margins. Inspect encoded reading poses, pans and joins;
keep all screenshot captures, speech and source digests with the delivered MP4.
