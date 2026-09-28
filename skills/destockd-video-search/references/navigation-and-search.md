# Navigation, categories and search

Verified on 2026-09-27 against the live UI and its public frontend. Refresh
collection counts with `collections`; this table is a dated snapshot.

## Actual navigation

| Route | Purpose |
| --- | --- |
| Home / Search shots | Visual similarity search across individual shots; submit with Enter. |
| `#/collections` | Small editorial selections, not an exhaustive taxonomy of the archive. |
| `#/random` | Discovery without a specific brief. |
| `#/films` | Film-title substring search and a paginated catalog; 648 films observed. |
| `#/shot/<encoded-film>/<encoded-shot>` | Shot player, download, sources, previous/next shot, similar shots. |
| `#/film/<encoded-film>` | All indexed shots of a film and its full-film source link. |
| `#/similar/<encoded-film>/<encoded-shot>` | Visual neighbors of a particular shot. |

The header advertised 41,000+ shots. Collections overlap and cover only a
selection; do not add their counts to estimate unique archive coverage.

## Editorial collections

| Collection | Slug | Shots | Practical meaning |
| --- | --- | ---: | --- |
| Color | color | 102 | Color palettes and tonal inspiration. |
| Beauty | beauty | 47 | Landscapes, culture and appealing compositions. |
| World War 2 | ww2 | 38 | Wartime historical material. |
| Asia | asia | 47 | Regional footage, including Japan and Korea. |
| Technology | technology | 76 | Computers, cables, screens and equipment. |
| Data | data | 50 | Charts, diagrams and numeric displays. |
| Destruction | destruction | 36 | Fires, explosions and damage. |
| Industry | industry | 42 | Production, machinery, labor and goods. |
| Animation | animation | 35 | Drawn animation and stop motion. |
| Textures | textures | 48 | Film grain, leaders and burns. |
| Curios | strange | 53 | Unusual and experimental imagery. |
| Selections | favorites | 136 | The curator's personal selection. |

## A useful classification for user requests

Classify along independent dimensions rather than forcing everything into one
collection. These are assistant-side labels, not additional website filters:

- **Subject:** people and daily life; science and technology; work and industry;
  nature; transport; war and history; graphics and animation.
- **Action:** walking, operating equipment, manufacturing, launching, moving crowds.
- **Place and period:** geography or historical event, only when source evidence
  supports it. An archival appearance alone does not establish a decade.
- **Appearance:** color/black-and-white, framing, textures, camera movement, mood.
- **Technical constraints:** duration, dimensions, aspect ratio, sound. Measure
  these from media; they are absent from the observed search response.
- **Provenance:** film, shot ID, Archive.org and National Archives record if present.

Map a brief to subject + visible action + setting, then add one visual constraint.
Use title search for a named film and collections for inspiration. The helper's
color and film-name filters run locally over fetched results; they do not prove
the entire archive contains no match.

## Query recipes

Use these as patterns, not as guaranteed matches:

| User intent | Useful English visual phrases | Initial collection |
| --- | --- | --- |
| Old computer footage | `vintage computer room`, `computer operator magnetic tape` | Technology |
| Manufacturing | `factory workers assembly line`, `industrial machinery close up` | Industry |
| Charts in motion | `animated bar chart`, `scientific diagram animation` | Data / Animation |
| Film overlays | `film leader countdown`, `scratched film texture` | Textures |
| Landscape | `mountain lake landscape`, `ocean waves rocky coast` | Beauty |
| Historical city traffic | `vintage city street traffic`, `cars driving through city` | Global search |

For a Spanish brief, translate the visual concept instead of sending a long
conversation to the search engine. Example user wording: “un video de ordenadores
antiguos” becomes `vintage computer room`. Do not claim English is a mandatory
API language; it is the practical starting point demonstrated by the site's FAQ.

Inspect results. During verification, `astronaut walking on the moon` returned
training and unrelated historical shots near the top; `woman using computer`
also returned weak matches. A title and similarity score cannot certify the
requested scene. Remove abstract words, try a concrete alternate description,
and use similar shots from a visually checked seed. Stop after a bounded search
and describe a gap honestly if the requested action is absent.

## Sources

- [Collections](https://www.destockd.com/#/collections)
- [Films](https://www.destockd.com/#/films)
- [About](https://www.destockd.com/content/about.md)
- [FAQ](https://www.destockd.com/content/faq.md)
- [Rights and provenance](https://www.destockd.com/content/legal.md)
- [Public frontend defining routes and GET requests](https://www.destockd.com/app.js)

Destockd reports FedFlix/public-domain or unrestricted origins and exposes source
links. Preserve these links; its notice does not independently clear every clip
or embedded element. There is no account requirement for the observed flow.
