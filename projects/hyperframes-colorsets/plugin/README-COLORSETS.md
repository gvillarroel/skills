# Original HyperFrames with colorsets

This package comes directly from `heygen-com/hyperframes`. Its manifests,
launcher and four core skills are unchanged: `hyperframes`, `hyperframes-cli`,
`hyperframes-registry` and `media-use`. `SOURCE.json` records the upstream release
and commit.

The only functional addition is `skills/colorsets`: two native `FRAME.md` styles
with the exact colors and typography from the user's original YAML files.
Use `$colorsets` to select `colorset1` (the default) or `colorset2`. Copy the
selected style to the video project as `frame.md`, then follow the original
HyperFrames workflow.

```text
Use $colorsets and HyperFrames to create a video with colorset1.
Use $colorsets and HyperFrames to create a video with colorset2.
```

Plugin instructions, metadata and examples are in English. The requested video's
language remains part of the task; for example, add "with English on-screen text"
when requesting an English video.

The styles define colors and typography. Composition, story, animation, media,
components and rendering follow the original skills and the user's request.

The canonical package lives at `projects/hyperframes-colorsets/plugin` in the
skills repository. The versioned catalog at
`projects/hyperframes-colorsets/.agents/plugins/marketplace.json` makes that
project directory a marketplace root. From the repository root, register it with
`codex plugin marketplace add ./projects/hyperframes-colorsets`.
The **HyperFrames Colorsets** source contains **HyperFrames by HeyGen** under the
technical name `hyperframes`. Marketplace files alone do not confirm installation
or activation in the desktop application.

The original Apache-2.0 license is preserved as `LICENSE`. Upstream source:
https://github.com/heygen-com/hyperframes/tree/v0.8.199.
