Read ../prompt.md first. Use only the supplied pi-durable skill as a read-only resource. Keep all generated files, dependency caches and outputs inside this workspace. Do not read global Pi installations, credentials, other repositories or other skills. Do not run a nested model, start a service, refresh global Pi stores, activate an improvement or inspect account tokens. Public metadata requests to pi.dev are allowed; they require no credentials.

Generate exactly outputs/team using the bundled service generator with the map-reduce profile. Install its declared dependencies with lifecycle scripts disabled and project-local cache, then build it. Keep its initial application/configuration/manifest unchanged. The live example must use a task-aware current-model policy while the default remains faux/offline.

Run these actual generated commands from the workspace and save their JSON stdout at the exact paths shown:

```bash
node outputs/team/dist/src/models-cli.js list --provider openai-codex --source refresh > outputs/catalog.json
node outputs/team/dist/src/models-cli.js resolve --provider openai-codex --task coding > outputs/coding.json
node outputs/team/dist/src/models-cli.js resolve --provider openai-codex --task review > outputs/review.json
```

Do not interpret catalog presence as successful inference or account entitlement. Inspect the returned metadata and supported effort maps. Verify every initial scaffold-manifest file hash. Write exactly outputs/check.json describing the observed catalog source/time, current coding/review model IDs, their requested and supported reasoning efforts, version-selection basis, hash verification and limits. Write exactly outputs/report.md explaining the difference between model capability tier, model version and reasoning effort; how to list configured Pi models, inspect supported levels, refresh only project metadata, preserve an exact model/family pin, and lock all choices before a controlled evolution study. State when a long-running service observes newer models and how pending conversations are protected. Do not claim native macOS operation, universal intelligence scores, model inference or global account access from this preparation.

Required nonempty artifacts: outputs/team/config.codex.example.json, outputs/team/scaffold-manifest.json, outputs/catalog.json, outputs/coding.json, outputs/review.json, outputs/check.json, outputs/report.md.
