---
name: destockd-video-search
description: "Finds archival video shots on Destockd from a natural-language description, browses its collections and films, presents a numbered preview shortlist, and downloads the exact selected MP4. Use for Destockd footage discovery, similar-shot searches, source lookup, and follow-up requests to download a previously selected clip."
---

# Destockd Video Search

Turn a visual brief into a short, reviewable list of real Destockd shots, then
download the selected shot without changing its identity. Use the user's language
in conversation. The helper requires Python 3.11+ through `uv`; `ffprobe` is
optional for measuring and validating downloaded media. No account is normally
needed.

## Presentation colors

Use colorset1 for authored preview chrome: `#f7f7f7` stage, `#ffffff` cards, `#333e48` text, `#cfcfcf` borders and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.

## Find footage

1. Extract the subject, action, setting, visual style and any essential constraints.
   Use existing context; start a search unless a missing detail changes the task.
   Translate visual search phrases into concise English, usually one to three
   alternatives. Preserve the original request in your explanation. Read
   [navigation-and-search.md](references/navigation-and-search.md) for the real
   collections, query recipes and the difference between shot and film search.
2. Prefer the bundled helper, which calls the same public GET endpoints as the
   website. From the active workspace, use the actual path to this skill:

   ```sh
   uv run --script <skill-dir>/scripts/destockd.py search --query "vintage computer room" --query "computer operator magnetic tape" --limit 6 --out results.json --html options.html
   ```

   Keep generated files outside the skill. Choose a project artifact directory
   when one exists. `--out` saves the selection state, and `--html` creates an
   optional preview gallery. These commands retrieve candidate metadata; they do
   not download every video. See [commands.md](references/commands.md) for
   collections, film titles, source films, similar shots, local filters and errors.
3. Inspect candidate thumbnails or preview clips with the available image/browser
   tools before claiming a visual match. The helper has no visual understanding.
   A score ranks similarity; it is **not** a probability or proof of an event,
   location, date, identity or action. If inspection is unavailable, label the
   options as unverified candidates. Check source records for historical claims.
   Refine with a concrete alternate query, a relevant collection, neighboring
   shots or `similar` when the initial results miss essential constraints.
4. Present roughly 3–6 useful options with the saved option number, stable ID,
   film/shot, preview link, observed content and any mismatch. Preserve numbering
   from the JSON even if you omit irrelevant candidates. State which option you
   recommend and why. Do not invent duration, resolution, sound or production
   year: measure them or mark them unknown. Keep the manifest path in context.

## Download the chosen video

- Resolve “download option 2” against the **same saved list**. Resolve “download
  it” against a single selected or clearly referenced clip. If several remain
  plausible, ask only which option; never silently choose the first result.
- Once the clip is identified, download it immediately without another permission
  question. A request to search alone calls for options; a request to find and
  download the best match permits selecting a checked match and downloading it.
- Download by saved stable ID or by the actual shot-page URL:

  ```sh
  uv run --script <skill-dir>/scripts/destockd.py download --manifest results.json --option 2 --output chosen-video.mp4
  ```

- The helper refreshes the selected film/shot record and downloads its `clip`
  field. It never substitutes the lower-quality `preview` or reruns search to
  resolve an option. It refuses existing output paths, saves atomically, and
  produces `<output>.json` with source links, byte size, SHA-256 and media checks.
  Read the result before claiming success and return a clickable local file.
- Download full films only when requested: `film` exposes the actual Archive.org
  source page. Follow that page's download options; the clip downloader handles
  individual shots only. Preserve provenance, and describe source rights as
  reported by Destockd, without certifying every embedded element for reuse.

## Browser fallback

If the public endpoint changes or is unavailable, use `https://www.destockd.com/`:
enter a visual phrase in **Search shots…**, press Enter, open a candidate, and use
**See similar shots**, **All shots from this film**, or **Download clip**. Search
text is held in page state, so the home URL does not preserve a search. Keep the
actual `#/shot/<film>/<shot>` URL for each choice. Verify the completed local
download. Stop with a clear failure if the selected clip is missing; do not
replace it with another shot or work around an access restriction.
