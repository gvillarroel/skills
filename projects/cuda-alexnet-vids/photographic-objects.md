# Photographic object revision

The current local film is
[cuda-alexnet-photographic-local.mp4](artifacts/videos/cuda-alexnet-photographic-local.mp4),
220.6 seconds, 1080p30. It preserves the approved Google Vids narration exactly.
Complete native visual replacement/export remains pending the existing browser
upload permission. The native project does not yet represent this revision.

## Choose and change treatments

`object-media.json` is the reviewed source/preparation request. Hardware uses
gray/white ordered one-bit at cell size 2. Training samples use grayscale; the
network input uses a restrained pixel treatment of an actual paper photograph.
Keep the source scope and credit records intact. Do not describe the EVGA
product image as the researchers' exact physical boards or the illustrative
CPU as the documented experiment host.

`story.json → scenes[].objects[]` binds each object ID to an asset and variant.
Choose `gray`, `edges`, `pixel` or `one-bit` for hardware there; its generic
renderer reads that policy. Add or adjust a treatment in `object-media.json`
before selecting it. The existing 43 variants are cached. Prepared and rendered
photographs preserve their complete silhouette and aspect ratio.

```text
uv run --script ../../skills/line-world-video/scripts/documentary_assets.py prepare --request object-media.json --output artifacts/media/objects --comparison artifacts/screenshots/photo-treatments.png
uv run --script scripts/prepare_project.py
uv run --script scripts/render_video.py
uv run --script ../../skills/line-world-video/scripts/documentary_assets.py audit --story story.json --manifest artifacts/media/objects/manifest.json --html artifacts/composition/index.html --output artifacts/reviews/photo-bindings.json
```

Run these from this project directory. In the standalone source archive, use
`uv run --script rebuild.py --audit`; it selects the bundled plugin instead of
requiring a repository installation. Use `--render` to regenerate the visual
clips. Repository rendering supports `--render --scene <stable-scene-id>` to
limit costly frame capture to affected scenes and their changed incoming joins.

The detailed source records and credits live in
[`artifacts/media/objects/manifest.json`](artifacts/media/objects/manifest.json)
and [`credits.md`](artifacts/media/objects/credits.md). The
[comparison](artifacts/screenshots/photo-treatments.png) preserves original,
grayscale, edge, pixel and one-bit alternatives for review. Source originals and
the original paper PDF are included with the project source archive. Extracted
paper photographs retain parent PDF digest, page, image xref and crop coordinates.

## Timing and native continuation

Keep the existing `scripts`, `clipSeconds`, approved voice measurements and
`artifacts/data/cues.json` during a purely photographic change. Update target
bounds and inspect the guide's clearance after changing image size. Re-audit
affected scenes and neighboring joins before assembly. A longer/new script
requires real speech generation, measurement and cue realignment before
changing the visual budget.

The revision folder `artifacts/revisions/photo-0210/` contains assembly metadata,
voice observations, the actual native reference, byte-identical PCM proof,
source-bundle rebuild results and the exact native resume queue. Scene 6 in the
live editor still has the earlier subject-first visual; every current clip must
be replaced before a new complete native export is claimed. Keep the approved
voices. Do not regenerate speech or bypass the browser upload rejection.

The complete
[review gallery](artifacts/reviews/photo-review/index.html) includes encoded
cue/join samples, source geometry checks and hash-bound manual decisions.
The [encoded GPU frame](artifacts/screenshots/gtx580-encoded.png) is taken from
the actual revised movie at 145.533 seconds.
