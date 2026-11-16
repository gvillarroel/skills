# CUDA and AlexNet native production validation — November 15, 2026

This is a second real native production case using the existing OpenAI-compatible
Line World Video 0.9.0 six-skill plugin. It changes project content and utilities,
not canonical skill behavior or the existing qualification status. There is no
new isolated model-run claim; the extracted source bundle is tested directly.

This record describes the original film before portraits were added. Its movies
and baseline reviews are retained under
`projects/cuda-alexnet-vids/artifacts/baseline-no-portraits/`, preserving the
original relative paths inside that directory. Current delivery paths now point
to the portrait revision. See the subsequent
[media revision evidence](../line-world-video/portraits-and-logos-20261115.md).

## Deliverables and scope

- [Separate native Google Vids project](https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit):
  ten verified Spanish scripts, ten native Nyla voice tracks and one matching
  uploaded video per scene. The preceding ML film was preserved.
- [Production instructions](../../projects/cuda-alexnet-vids/production.md):
  primary historical sources, style decisions and editable timing commands.
- Original native movie: `projects/cuda-alexnet-vids/artifacts/videos/cuda-alexnet-google-vids-final.mp4`;
  SHA-256 `7d0a3bdf0dde2cd80fb48e2d998375aaa480f72bc9fd54c4e920f20437b81a10`.
- Clean delivery: `projects/cuda-alexnet-vids/artifacts/videos/cuda-alexnet-final.mp4`;
  SHA-256 `20c35342c716fac9e8520ca487de9002e8a28034c0dabc92f371723099d5a995`.

Both movies contain the native encoded visual and voice payloads: 1920 by 1080,
nominal 30 fps, 6099 frames and 203.313923 seconds. The clean container omits the
optional default subtitle stream without re-encoding. Video packet hashes,
audio packet hashes and decoded 16 kHz mono PCM hashes match the native export.

## Actual observations

All ten native scenes were selected and checked for the correct media identifier,
one video object and the preserved original narration. Scene announcements give
millisecond extents. Frame-ceiled source clips cover the measured speech; the
native export differs by one frame, approximately 47 ms in total duration, and
has no blank tail. Actual UI receipts leave zero pending native actions. Sharing
remains private. Uploads used the ordinary Windows Open dialog, without changing
extension permissions. Native export/download completed through the supported UI.

All 6099 frames decode and the frame scan detects zero white or black frames.
All 51 speech-aligned adjacent guide arrivals are detected in the actual encoded
native movie. Ten voice windows correlate with the pre-insertion native voice
reference at 0.9933 or higher. ASR boundaries are approximate and proper names
can be misrecognized; correlation and UI track observations are separate checks.

Browser audits pass text/text clearance, actual stroke/text clearance, guide
envelopes, repeated seeking, and exact camera/guide source joins in all ten
scenes. Manual inspection repaired Mermaid word wrapping and the schematic
top-five checkmark before final upload. Full-frame partitions, primary red
focus and dark-gray secondary bars follow the approved visual style.

## Commands and retained evidence

Run project commands from `projects/cuda-alexnet-vids/`:

```powershell
uv run --script scripts/render_video.py
uv run --script scripts/prepare_uploads.py
uv run --script scripts/verify_export.py --video artifacts/videos/cuda-alexnet-google-vids-final.mp4
uv run --script scripts/finalize_delivery.py
uv run --script scripts/package_project.py
uv run --script scripts/check_source_bundle.py
```

Actual source/native reviews, queue receipts, measured timing and packet hashes
remain under the project's ignored `artifacts/reviews/`, `artifacts/manifests/`
and `artifacts/data/`. The first upload preparation copied all ten clips without
encoding; final preparation reused all ten. Source-bundle validation extracts
the ZIP into a clean workspace, checks every recorded file hash, rebuilds using
only `resources/plugin/`, reuses ten cached clips, audits ten scenes and exercises
the ten-scene browser preview with zero browser errors.

Repository gates run from the repository root on November 15, 2026:

- `uv run --script scripts/validate-pattern-ids.py`: pass, 1348 canonical IDs.
- `uv run --script scripts/test-skill-independence.py`: pass.
- `uv run --script scripts/check-repo-payload.py`: pass.
- `uv run --script scripts/validate-skills.py`: four pre-existing unrelated
  `authoring/reference-route` findings. They concern `schema-validation-review.md`
  in curate-semantic-model, `premise-reuse.md` in extract-ontologies, and
  `keyword-witnesses.md` / `product-crawl.md` in extract-with-ontology. No finding
  concerns the video plugin or this project; unrelated source edits were preserved.
