# Text pairing command contract

Use only the read-only `skills/compose-synchronized-svg/` bundle and normal local tools. Keep every output in this workspace. Do not read acceptance examples, sibling skills, repository context, or the network. Do not edit the skill or patch SVG output.

Copy the compact brief template to `outputs/pairs/brief.json`. Keep its data, modules, and scenarios. Set `timeline` to null and set its theme to exactly this fragment:

```json
{"colors":{"canvas":"#ffffff","surface":"#ffffff","ink":"#767676","muted":"#767676"},"conceptColors":{"input-rate":"#888888"}}
```

Run preflight and save its JSON output to `outputs/pairs/preflight.json`. Compile to `outputs/pairs/plan.json`, compose `outputs/pairs/atlas.svg`, run the bundled static validator to `outputs/pairs/static.json`, and run the compact browser audit to `outputs/pairs/browser.json` with screenshot `outputs/pairs/overview.png`. The preflight, static, and browser reports must have `ok: true`; the browser report must have `metrics.textContrastIssueCount: 0`. Inspect the screenshot. Report the observed result and exact paths. Preserve all supplied colors in the brief and canonical plan. Treat unsupported behavior as a reported failure.
