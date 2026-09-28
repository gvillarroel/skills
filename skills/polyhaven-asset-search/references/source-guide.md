# Poly Haven source guide

## Resource choice

- **Textures:** surface and material searches such as wood, plaster, brick, stone,
  soil, fabric and metal. Refine wear, color, finish, scale and intended surface.
- **HDRIs:** lighting environments. Refine indoor/outdoor, time of day, weather,
  contrast and horizon. Download `hdr` or `exr` for lighting; a tonemapped JPEG
  cannot preserve the lighting range of an HDRI.
- **Models:** objects and scanned props. Inspect available model formats and all
  dependent texture files. A preview image is not the model.

These are search dimensions, not a frozen list of current site categories.
Retrieve the current hierarchy with:

```sh
uv run --script <skill-dir>/scripts/polyhaven.py taxonomy --type textures --out taxonomy.json
```

## Selection and variants

For image-tool review, `previews --manifest options.json --output-dir
artifacts/previews` downloads only thumbnails to a fresh workspace directory and
returns their exact local paths. It does not download texture maps, HDRIs or
models. Keep these files inside the active workspace so shell and image-tool
paths refer to the same files on Windows.

`search` uses the provider's ordered semantic/keyword results and retrieves each
listed asset's metadata. `--limit` is 1–20. Preserve the order; raw similarity
scores are not probabilities. `inspect` and `download` accept an exact `--id`
slug, or `--manifest` plus exactly one `--option` or `--id`. Saved option numbers
are scoped to that manifest; save a new filename for a revised shortlist.

Inspection returns `variants`, each with a `key`, `url`, `bytes`, `extension`,
optional provider `md5`, and `include` dependency map. Keys reflect the actual
response hierarchy, for example `Diffuse/2k/jpg`, `nor_gl/2k/exr`,
`hdri/2k/hdr`, or `gltf/2k/gltf`. Do not assume all assets expose these keys.

For material packages, choose color, the appropriate normal map and roughness;
add displacement, ambient occlusion or other maps when needed and available.
OpenGL (`nor_gl`) and DirectX (`nor_dx`) normal maps use different Y conventions.
Some files combine channels, such as ARM; check the source before assigning them.

`download --variant KEY --output FILE` saves one self-contained file and
`FILE.json`. Repeat `--variant` and use a fresh `--output-dir DIR` for multiple
maps or dependent model formats. Dependencies retain the relative paths supplied
by the API. The bundle receipt records each relative file and its checksum.
The default `--max-mib 512` applies to the complete bundle. Inspect sizes before
choosing very large resolutions; increase the limit only for the user's intended
download. Interrupted staging directories are cleaned and existing files stay intact.

## Service and rights

Verified on 2026-09-27:

- [API overview](https://polyhaven.com/our-api): public free API, including
  commercial integrations; identifying User-Agent and visible source credit.
- [API schema](https://api.polyhaven.com/api-docs/swagger.json): `/search`,
  `/info/{id}`, `/files/{id}`, `/taxonomy/{type}`. Search accepts `q`, `t`, `limit`
  and `future=false`. Metadata can change; downloads always refresh identity.
- [Asset license](https://polyhaven.com/license): asset files are CC0. Website
  branding and unrelated page content have separate terms.

The helper uses returned download URLs, checks expected origins, response length,
provider checksum and file signatures where supported, and writes source/hash
receipts. Those checks verify transfer identity, not whether a model will import
correctly into every 3D application. Verify in the target application when the
task includes integration or rendering.
