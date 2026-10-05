Render a compact small synthetic approval diagram using the supplied skill. Save this source exactly at `source/approval.puml`:

```text
@startuml approval
[Record received] as received
[Review decision] as review
[Approved archive] as archive
received --> review : inspect record
review --> archive : approved
@enduml
```

Read the skill's connected-layout guidance. Run these commands exactly, in separate shell calls:

```sh
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py source --output rendered --colorset colorset1 --format svg --format png --report render-report.json
```

```sh
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report render-report.json --output rendered --colorset colorset1
```

Inspect the PNG and create `review.md` stating what actual labels, head clearance and routes were checked. Exact required outputs are `source/approval.puml`, `rendered/svg/approval.svg`, `rendered/png/approval.png`, `render-report.json`, `review.md`. The source is non-sensitive synthetic evaluation work; remote fallback is permitted if a local renderer is unavailable. Keep `skills/plantuml-colorset-renderer/` read-only and generated files in the workspace. Do not read galleries or other skills.
