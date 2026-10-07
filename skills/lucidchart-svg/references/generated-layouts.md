# Explicit data-backed layouts

Use this route when the supplied hierarchy or sequence meaning matters and Lucid-generated layout is acceptable. Preserve fixed SVG coordinates with the ordinary [native reconstruction](native-reconstruction.md) route instead. Generated positions identify a top-left origin; they do not establish the resulting dimensions, node positions, font metrics or line routing.

The bounded offline driver packages explicit inline collections and documented `orgChart`, `mindMap`, `umlSequence`, and `assistedLayout` objects. It performs no network/account access:

```sh
uv run --script <skill>/scripts/build_generated.py layout.json --output layout.lucid --document-json layout-document.json --report layout-report.json
```

The input has `layouts` (nonempty array), optional `collections`, and optional `graph` using the native compiler contract. A missing graph defaults to an empty page. Collections go at document level; generated objects go in `pages[0].dataBackedShapes`, never ordinary `shapes`.

## Hierarchy input

```json
{
  "graph": {"title":"Engineering", "nodes":[], "infinite_canvas":true},
  "collections": [{"id":"people", "values":[
    {"employee":"e1", "manager":"", "name":"Ada", "role":"Director"},
    {"employee":"e2", "manager":"e1", "name":"Lin", "role":"Engineer"}
  ]}],
  "layouts":[{"id":"organization", "type":"orgChart", "position":{"x":20,"y":20},
    "collectionId":"people", "idField":"employee", "foreignKeyField":"manager", "nameField":"name", "roleField":"role"}]
}
```

For `mindMap`, replace the org-chart fields with `idField`, `parentIdField`, and `textField`. Every hierarchy row needs a unique nonblank string primary key and a literal label; a root parent is empty/absent/null. The driver checks missing parents, cycles and duplicate keys. Its conservative policy requires one root for a mind map and allows org-chart forests; these are local constraints, not vendor promises.

Optional org-chart `roleField` and `extraFields:[names]` refer to supplied fields; extra data need not be directly displayed by the default layout. The documented `imageUrlField` is excluded from this offline resource-free profile. Keep remote portrait dependencies for a separately reviewed resource workflow.

Documented limits are 4,000 org-chart users and 4,000 mind-map items summed across document pages. This single-page driver counts every generated object, including reuse of a collection, against its family total. Position coordinates use a conservative nonnegative 0–20,000 profile. Data cells are flat JSON scalars and hierarchy IDs are strings; unsupported nested cells/numeric identities fail rather than undergo undocumented coercion.

## Sequence and assisted layout

`umlSequence` requires `{id,type,position:{x,y},markup}`. Nonblank markup is limited to 50,000 characters. The driver preserves supplied markup and checks that limit; it does not implement Lucid's complete supported PlantUML-style sequence grammar. It rejects external include/import directives pending separate resource review. The UI sequence route supports only a subset of PlantUML and does not accept arbitrary styling syntax. Ungrouping permits independent styling but ends markup editing. Preserve that editing tradeoff in the report.

`assistedLayout` requires `{id,type}` and optionally `shapeIds:[existing shape IDs]`. Omission selects all ordinary page shapes. The driver rejects empty selections, unknown IDs, duplicates or non-shape IDs. Choose it as an explicit reflow/adaptive-routing step; it relinquishes source layout fidelity.

## Resource and validation boundaries

Inline collections use `{id,values:[objects]}`. The driver excludes external `dataSource` files and validates IDs/references. It sets a local 1,000,000-byte cap for inline collection JSON. The vendor's 1 MB cap applies to packaged `data/`, which this driver does not produce; do not confuse these limits. Final document JSON retains the native compiler's conservative limit below2,000,000 bytes and deterministic ZIP packaging.

Inspect the report for item/root/relationship counts, preserved records/markup, reflow decisions, and actual native-graph choices. No offline report claims parser/rendering acceptance. Submit through [standard-import.md](standard-import.md), verify generated content, literal labels, hierarchy edges and editing behavior, then disclose substitutions. For a finite output page, inspect generated extents and clipping; their size cannot be derived from source SVG boxes.

Checked 2026-10-07: [Data-backed shape contract](https://lucid.readme.io/docs/data-backed-shapes-si), [collections](https://lucid.readme.io/docs/data-si), [page settings](https://lucid.readme.io/docs/pages-si), [UI sequence markup](https://help.lucid.co/hc/en-us/articles/16262874090900-Create-a-sequence-diagram-with-UML-markup-in-Lucidchart).
