# Crawl pinned product documentation

Use the bundled crawler when the product's authorized documentation
is maintained as Markdown in a public GitHub repository. Identify the
edition, version, or plan being assessed and the pages the caller wants
included. Review the source roster before freezing it. Pin each file's
exact bytes at a full commit SHA and set bounded seed coverage.

Create a version 2 JSON specification with these fields.

| Field | Value |
| --- | --- |
| `version` | `2` |
| `repository`, `revision` | GitHub `owner/name` and full lowercase commit SHA |
| `docs_origin` | The publisher's canonical HTTPS origin, without a path or trailing slash |
| `docs_base_path` | Optional version prefix such as `/2.19` for the exact Jekyll `{{site.url}}{{site.baseurl}}` link prefix |
| `max_depth`, `max_sources`, `max_source_bytes` | Positive collection bounds, except depth can be zero |
| `seeds` | Distinct source IDs at which the crawl starts |
| `allowlist` | A row for each approved source, with `source_id`, repository-relative `source_path`, lowercase `sha256`, and absolute `publisher_path`. Add `aliases` with exact publisher paths for known alternate routes. |

Keep stable source IDs and use the publisher's trailing-slash
convention in each canonical path so relative links resolve correctly.
The crawler traverses inline Markdown links to approved repository
paths or publisher routes and requires the full roster to be reachable
within the bounds. It fetches bytes from the pinned GitHub revision,
with redirects disabled. The publisher URL describes provenance and
link context. Unapproved pages, dynamic sites, and other source formats
require a separately supplied corpus or collection method.

```text
uv run --script SKILL/scripts/crawl_product_docs.py crawl --spec crawl-spec.json --output corpus
uv run --script SKILL/scripts/crawl_product_docs.py verify --spec crawl-spec.json --output corpus
```

Replace `SKILL` with the skill directory. Leave the output path
absent. If necessary, create its parent only. The crawler creates the
output directory and stores the exact source
bytes under `corpus/sources` and records the revision, digest,
publisher path, discovery path, and in-scope links in
`corpus/manifest.json`. Verification reconstructs the manifest from
the stored files offline. Retain the spec with the capture. Supply
the saved manifest to the [numbered source view](artifacts.md#inspect-numbered-source-lines)
and [assertion materializer](artifacts.md#materialize-a-graph-and-evidence-from-one-plan).

Keep collection coverage, schema conformity, and semantic support
separate. The crawl covers its approved roster. An absent feature,
availability claim, or mechanism may need further authorized sources.
