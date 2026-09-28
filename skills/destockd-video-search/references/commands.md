# Helper commands and contracts

Run `uv run --script <skill-dir>/scripts/destockd.py --help`. Use paths relative
to the active workspace for outputs. The Python helper uses only the standard
library. No credentials, browser profile, hidden API key or repository files
are required. `ffprobe` on PATH strengthens downloaded-media validation.

## Discovery

```sh
uv run --script <skill-dir>/scripts/destockd.py collections --out categories.json
uv run --script <skill-dir>/scripts/destockd.py collection technology --limit 6 --out technology.json --html technology.html
uv run --script <skill-dir>/scripts/destockd.py search --query "vintage computer room" --query "computer operator" --pages 2 --limit 6 --color bw --out results.json --html options.html
uv run --script <skill-dir>/scripts/destockd.py films --query "space" --out films.json
uv run --script <skill-dir>/scripts/destockd.py film --film "The President Accounts" --limit 6 --out film-shots.json
uv run --script <skill-dir>/scripts/destockd.py similar --film "The President Accounts" --shot shot_094 --limit 6 --out similar.json --html similar.html
```

Search accepts up to three `--query` phrases and one to three pages per phrase.
Defaults: one page, six saved options. Deduplication uses `(film, shot)`;
reciprocal rank fusion combines alternative searches without pretending their
raw similarity scores are calibrated. Each row retains query-specific ranks and
scores. `--color color|bw` and `--film-contains TEXT` filter fetched rows locally.
`has_more` and fetched counts describe the retrieval boundary. Empty local
results mean no match in the fetched window, not no match in the archive.

Collections preserve their editorial order. Film-title search reads the public
film catalog (the frontend requests `per_page=1000`) and filters titles locally.
Full-film download is exposed as a source link, not a clip download operation.
`similar` uses the selected shot as its seed. No command enables the site's
optional disturbing/blank-footage setting.

## Exact selection and inspection

```sh
uv run --script <skill-dir>/scripts/destockd.py inspect --manifest results.json --option 2 --out selected.json
uv run --script <skill-dir>/scripts/destockd.py inspect --url "https://www.destockd.com/#/shot/The%20President%20Accounts/shot_094" --out selected.json
uv run --script <skill-dir>/scripts/destockd.py download --manifest results.json --id <saved-id> --output chosen.mp4
uv run --script <skill-dir>/scripts/destockd.py download --manifest results.json --option 2 --output chosen.mp4
```

Use exactly one selector: a shot page URL, or a manifest with one stable ID or
saved option number. Each option is tied to film and shot, not a mutable search
position. The manifest has `schema_version`, `retrieved_at`, `mode`, `retrieval`,
`results`; result rows contain `option`, `id`, `film`, `shot`, `page_url`,
`keyframe`, `preview`, `clip`, `color_type` and `visual_verified: false`. Agent
observations belong in the response or a separate review, not invented API data.

`inspect` refreshes metadata for only the chosen identity. `download` refreshes
again and uses the returned full clip. It validates public site/CDN origins,
HTTP status, response type, MP4 signature, length when supplied and a 512 MiB
default size cap (`--max-mib` changes it). With ffprobe, invalid/unreadable media
fails before promotion to the requested output path. Existing video or receipt
paths cause an error; choose a new path instead of overwriting someone's file.

Success writes the requested MP4 and `<output>.json`. The receipt includes
refreshed source metadata, final download URL, timestamp, byte size, SHA-256 and
probe results. Without ffprobe, the receipt explicitly reports the more limited
container-signature validation; duration, dimensions and audio remain unknown.
An audio stream's presence does not prove audible or useful sound.

## Failure handling

Errors emit JSON to stderr and exit 2. JSON/HTML discovery outputs are written
only after successful retrieval. Download uses a temporary file in the output
directory and removes it on failure. It does not replace a missing shot with
another one. Transient GET errors get at most two retries; a long Retry-After,
403, 404, malformed response or changed contract requires a clear report or the
browser workflow. Do not invent new endpoints to recover.

The API is a public website implementation detail, not a promised stable service.
Observed routes: `/api/search?q=…&page=…`, `/api/collections`,
`/api/collections/<slug>?page=…`, `/api/films?page=…&per_page=1000`,
`/api/film/<film>`, `/api/shot/<film>/<shot>` and `/api/similar/<film>/<shot>`.
Encode path components individually. Do not construct CDN file paths: use the
actual returned `clip` URL.
