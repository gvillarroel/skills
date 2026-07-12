Use the provided `plantuml-colorset-renderer` skill to prepare a portable logo bundle at `outputs/plantuml-logos/` for a PlantUML project.

The bundle must contain every normalized SVG logo shipped by the skill plus `license_log.md`, `logo_manifest.json`, and the `licenses/` directory. Preserve every file byte-for-byte so the common intrinsic size, viewBox, aspect-ratio behavior, titles, embedded source artwork, provenance, and licensing record remain intact. Complete the task without network access.

Treat `skills/plantuml-colorset-renderer/` as read-only. Write only to `outputs/plantuml-logos/`. Do not inspect repository-level files, sibling skills, acceptance examples, or the network.
Do not print or enumerate the complete logo inventory; use the skill's deterministic bulk workflow and check only the required bundle-level result.
The bundled export operation already performs exhaustive validation. After it exits successfully, do not run ad hoc shell loops, Python heredocs, directory listings, or secondary per-file checks.
