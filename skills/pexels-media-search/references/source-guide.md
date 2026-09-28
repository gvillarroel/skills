# Pexels source guide

## Search dimensions

Pexels is useful for contemporary people, work, food, travel, nature,
architecture and lifestyle media. Treat these as query families, not a fixed
category taxonomy. Visual composition and specific actions still need inspection.

```sh
uv run --script <skill-dir>/scripts/pexels.py search --type photo --query "coffee shop" --orientation portrait --color brown --locale en-US --page 1 --limit 6 --out photos.json --html photos.html
uv run --script <skill-dir>/scripts/pexels.py search --type video --query "ocean waves" --orientation landscape --out videos.json --html videos.html
uv run --script <skill-dir>/scripts/pexels.py inspect --id photo:2014422 --out selected.json
```

- `--orientation`: `landscape`, `portrait`, `square`.
- `--size`: `large`, `medium`, `small`; meanings differ for photos/videos, so
  verify actual dimensions. It is a minimum search filter, not the download key.
- `--color`: photos only; a supported color name or hex value.
- `--locale`: default `en-US`; `es-ES` is supported for Spanish queries.
- `--page`: positive; `--limit`: 1–20. Keep `total` and `has_more` in context.

## Exact download variants

Use an exact typed `--id`, or `--manifest` plus exactly one `--option` or `--id`.
The manifest records IDs, source pages, authors, dimensions and candidate
variants. Follow-up downloads refresh the asset directly without another search.

Photo `original` preserves source dimensions. Other `src` keys may resize or
crop; do not use them for an original request. Use the extension in inspection.
Video keys are the numeric IDs of the returned `video_files`, not the video ID.
Use the listed width, height, fps and format. The helper supports returned MP4
renditions; it does not manufacture a resolution that is absent.

```sh
uv run --script <skill-dir>/scripts/pexels.py download --manifest videos.json --option 2 --variant <inspected-video-file-id> --output selected.mp4
```

`--max-mib` defaults to 512. HTTP length and file signatures are checked and a
local SHA-256 is recorded. These checks do not fully decode an image or video;
use an available image decoder or `ffprobe` when actual dimensions, playback or
audio matter. Report limits honestly. Existing media and receipt paths are not
overwritten. Access errors, rate limits or a removed variant produce an error,
not another media selection.

## API and rights

Verified against [official documentation](https://www.pexels.com/api/documentation/)
on 2026-09-27:

- Photos: `GET https://api.pexels.com/v1/search` and `/v1/photos/{id}`.
- Videos: `/v1/videos/search` and `/v1/videos/videos/{id}`. The repeated `videos`
  segment in exact lookup is part of the documented route.
- Every API request needs an `Authorization` header. The helper attaches it
  only to metadata requests on `api.pexels.com`; downloads use no API credential.
- [Free API access](https://help.pexels.com/hc/en-us/articles/360042327714-Does-Pexels-offer-an-API)
  requires the user's own key. Published quotas apply; respect `429` and
  `Retry-After`. No account creation, paid upgrade or quota bypass is part of this skill.
- Include a visible Pexels link and credit the creator when possible. Use this
  workflow for selecting resources for the user's projects; do not build a
  redistributed stock catalog or wallpaper service from API results.
- Content uses the [Pexels License](https://www.pexels.com/license/), not CC0.
  Retain the page, creator and license URL. Do not infer every possible use is
  permitted simply because the download is free.

If a returned legacy video URL redirects to a new CDN, inspect the official
source and exact URL before extending allowed origins. Never forward the API key.
