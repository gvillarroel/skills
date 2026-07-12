# PlantUML technical logo catalog — 1,531 assets — 2026-07-12

- Skill: `plantuml-colorset-renderer`
- Goal: provide at least 400 different commercially redistributable logos for AWS, GCP, large technology companies, and technical architecture diagrams.
- Result: 1,531 unique source artworks and 1,531 normalized SVG wrappers.

## Authoritative inventory

| Provider | Unique logos | Pinned source | Artwork license |
| --- | ---: | --- | --- |
| AWS | 860 | `awslabs/aws-icons-for-plantuml@50efda948226ff4e06937596201528b707ef3ef9` (`v23.0`) | CC-BY-ND-2.0 |
| GCP | 93 | `davidholsgrove/gcp-icons-for-plantuml@f103741ffdca5793142103d7f5206814be92a405` | CC-BY-ND-2.0 |
| Devicon | 578 | `devicons/devicon@7330accdbc47e2dc0c19789a48533c4a3c50fe58` | MIT |

The first attempted GCP tag, `v1.0`, was rejected because inspection showed that it still contained inherited AWS assets. The final manifest uses the actual GCP branch commit and contains recognizable Compute Engine, Cloud Run, GKE, BigQuery, Pub/Sub, Cloud SQL, Cloud Storage, networking, security, AI, and developer-tool symbols.

`assets/logos/logo_manifest.json` is the source of truth. It records 1,531 unique IDs and 1,531 unique original SHA-256 values. Representative large-company and technical entries include AWS, Google Cloud, Azure, Oracle, SQL Server, GitHub, GitLab, Docker, Kubernetes, Cloudflare, Red Hat, Salesforce, Facebook, LinkedIn, Apple, Android, Chrome, and Firefox.

## Normalization and legal contract

- Every output is a self-contained SVG with `width="256"`, `height="256"`, `viewBox="0 0 256 256"`, 16-unit padding, and centered `preserveAspectRatio="xMidYMid meet"`.
- Every wrapper embeds the original pinned source payload byte-for-byte as a base64 data URI. Validation decodes the payload and compares its SHA-256 with the manifest.
- CC-BY-ND AWS/GCP artwork is not recolored, cropped, redrawn, or geometrically edited. Only the outer technical viewport controls display size.
- `assets/logos/license_log.md` contains one provenance row per SVG plus source-group attribution, redistribution requirements, license URLs, and trademark caveats.
- Full CC-BY-ND-2.0 and MIT texts ship in `assets/logos/licenses/`.
- Copyright licenses do not grant trademark rights or imply endorsement.

## Deterministic validation

- Manifest rebuild from the three pinned clones produced byte-identical SHA-256 `55687F362F97BDCE5EE2BF4535F332CC81F77111EEE34E6D6ECBA62BA215BFEF`.
- Local sync and offline export both validated all 1,531 SVGs, their embedded source hashes, manifest, license log, and license files.
- `scripts/test_logo_assets.py`: 5/5 tests passed, covering the 400-logo minimum, exact provider counts, unique IDs/hashes, representative AWS/GCP/company assets, full wrapper validation, and license-log completeness.
- Existing PlantUML coverage suite: 16/16 tests passed.
- Python compilation passed for the manifest builder, sync/export validator, search tool, and tests.

## Browser validation

Playwright Chromium loaded the complete 1,531-card catalog:

- 1,531/1,531 images decoded.
- 1,531/1,531 reported natural dimensions 256×256.
- Zero intrinsic-size failures.
- Zero rendered 80×80 containment-box failures.
- Zero browser console errors or warnings.
- Provider card counts exactly matched AWS 860, GCP 93, and Devicon 578.
- Direct screenshot review of AWS Lambda, DynamoDB, S3, Google Cloud, Azure, Docker, GitHub, Kubernetes, Oracle, Cloud Run, Compute Engine, BigQuery, and Cloud Storage found no stretching or clipping.

## Repository and isolated validation

- `scripts/validate-pattern-ids.py`: passed.
- `scripts/validate-skills.py`: passed.
- `scripts/check-repo-payload.py`: passed with the complete catalog.
- `scripts/test-pi-eval-harness.py`: 11/11 tests passed.
- `git diff --check`: passed for the skill, backlog, and evaluation records.

Final strict runtime cohort, model `openai-codex/gpt-5.3-codex-spark`, prompt `evaluations/pi-prompts/plantuml-normalized-logo-export.md`:

- `20260712-plantuml-logo-catalog-1531-export-spark-3`: passed.
- `20260712-plantuml-logo-catalog-1531-export-spark-4`: passed.
- `20260712-plantuml-logo-catalog-1531-export-spark-5`: passed.

All three runs exported 1,531 SVGs plus manifest, license log, and license texts; exact AWS/GCP/Devicon outputs and `logoCount=1531` passed; skill payload integrity was unchanged; external validation independently decoded and checked every exported source hash. Read surfaces contain only `../prompt.md` and the target `SKILL.md`, with no acceptance-example, sibling-skill, repository, or outside-workspace reads. Durable trace summaries are stored in `evaluations/plantuml-logo-catalog-1531-export-spark-{3,4,5}-read-surface.json`.

Earlier runs `spark-1` and `spark-2` are retained as failure evidence: run 1 timed out in harness shutdown after writing all required files, and run 2 produced correct artifacts but failed strict event checks due to an ad hoc malformed Python heredoc. Guidance was tightened to use the single validated export operation without enumerating the large bundle; the unchanged final design then passed 3/3.
