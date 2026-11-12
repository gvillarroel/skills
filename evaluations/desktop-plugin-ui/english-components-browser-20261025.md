# Generated component browser-language audit

Date: 2026-10-25. Three generated support-queue components were independently inspected in an actual local browser. **Authored English-copy checks pass 3/3**, at both desktop and narrow widths. Functional and accessibility limitations below remain retained; this is not a complete UX or accessibility acceptance result.

The subjects are the immutable `workspace/ui/status-panel.html` and `component-copy.json` artifacts from:

- [component run 1](../runs/20261025-desktop-ui-english-components-v1-luna-1/);
- [component run 2](../runs/20261025-desktop-ui-english-components-v1-luna-2/);
- [component run 3](../runs/20261025-desktop-ui-english-components-v1-luna-3/).

Their manifests bind the same 19-file skill payload, SHA256 `565602a9d166c18e15f07dce0a47c2a8587089085159572ca0094084886471ba`, and prompt SHA256 `53a03c1e58adf321341c959be448d6d7ba2aa368c6a6ff381aee9cd30bf5d988`. The separate [source/trace review](english-components-v1-luna.md) covers the model runs and JSON contracts; this report adds observed browser evidence after generation.

## Method and evidence

The [project probe](../../projects/desktop-plugin-ui/mcp-probe/generated-language-probe.ts) uses already installed Playwright 1.64.1 and Edge **156.0.4314.42**, headless, in fresh offline contexts. It navigates directly to each local generated file. HTTP(S) routes are blocked; none was attempted. No installation, network service, model provider, account or assistant host was used. The browser context uses `en-US`; OS/account/assistant locale was not changed.

Run from `projects/desktop-plugin-ui/mcp-probe`:

```powershell
npx --no-install tsx generated-language-probe.ts
```

The executed script SHA256 was `36b3245f1a586b18405b30abbb3de8b7af39056cfe1322218dffb87758e7fc37`. After execution, one English comment clarified the quoted legacy strings as source/test fixtures; no behavior changed and no rerun was needed. The final script SHA256 is `cbd190874f6b6582e146ed44c33980a3cc5ab876c7d8392d30446c0c8b5e5ee3`. The [structured browser report](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/report.json), SHA256 `493c0b296e98a2d27b74b1fc382c22683e50db973a5f6b87c60de845c657f676`, retains all findings. Its sibling `run-N/desktop/` and `run-N/narrow/` folders contain `states.json`, full-page screenshots and local CSV downloads. Every state records visible text, Playwright's accessible-tree snapshot, relevant accessible/tooltip/placeholder/option attributes, geometry and action results.

The probe captured **91 state snapshots** at 1100×820 and 360×780: default, source-ticket selection, refresh busy/success, invalid priority, cancellation, failed refresh, retry, empty result/recovery, saved priority, help/fallback disclosure, tooltip, local export, and Explain selection where reachable. Runs 1 and 2 also expose asynchronous save-busy states. Run 3 saves synchronously, so its save-busy state was not asserted; refresh still supplies observed busy feedback.

## Language outcomes

| Component | Desktop / narrow captures | Document and authored-copy outcome | Functional scope |
| --- | --- | --- | --- |
| Run 1 | 16 / 16 | Pass; `lang="en"`; observed visible and accessible state/control copy is English | Retained narrow table scrolling and native-tooltip paint limitation |
| Run 2 | 15 / 15 | Pass; `lang="en"`; observed visible and accessible state/control copy is English | Explain selection is absent |
| Run 3 | 15 / 14 | Pass; `lang="en"`; observed visible and accessible state/control copy is English | One narrow pointer action was blocked by its tooltip; tooltip association is incomplete |

The language judgment uses actual English meanings, not only absence of accents or source declarations. Browser snapshots and source inspection show English headings, ticket subjects, search/priority labels, options, placeholders, buttons, help, accessible names, live status/error text, empty-state recovery, cancellation, saved feedback, fallback content and tooltip wording. Expected English state phrases and control names are present. Legacy localized display strings are absent from the captured DOM text, accessible trees and UI attributes. Original legacy records preserved only in JSON source-provenance fields are not treated as authored display failures.

`T-104` remains visible and accessible in every viewport. HTML select values and the local CSV retain machine enum codes, while their display labels remain English. The exact original ID, `high`, `pending`, `queue_update_priority`, and `E_INVALID_PRIORITY` remain in each JSON contract's separate identifier/source records. No code identifier was translated to satisfy the display-language rule.

All six contexts have zero unhandled page errors. Cancelling a staged edit restored the original `high` priority; failed refresh retained `T-104`; empty-state recovery returned focus to search; valid saves displayed English success; local CSV downloads retained the selected ID and `pending` enum. These are observed synthetic-browser outcomes, not server or assistant-host acceptance.

Representative screenshots manually inspected include all three narrow defaults and desktop invalid/error/tooltip states:

- [Run 1 narrow](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-1/narrow/default.png) and [desktop refresh error](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-1/desktop/refresh-error.png).
- [Run 2 narrow](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-2/narrow/default.png) and [desktop invalid input](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-2/desktop/invalid.png).
- [Run 3 narrow](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-3/narrow/default.png), [desktop tooltip](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-3/desktop/tooltip.png), and [narrow tooltip](../../projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/run-3/narrow/tooltip.png).

## Retained functional and accessibility findings

1. **Run 1 narrow table:** the table container is 306 CSS px wide but has 620 px scrollable content. The document itself stays within 360 px. Several table cells are outside the initial viewport and require horizontal scrolling. English-copy success does not remove this layout limitation.
2. **Run 1 tooltip:** the Export control has the exact English native `title` attribute. Hover and focus were exercised, but the browser's native tooltip popup was not captured in headless rendering. Authored attribute content is verified; native popup paint remains unverified.
3. **Run 2 missing action:** there is no Explain selection control. The probe retains that operation as unavailable in both viewports. Other observed English copy does not satisfy the missing functionality.
4. **Run 3 pointer obstruction:** after hovering/focusing Export and downloading, the 360 px Explain selection click timed out. The retained Playwright log identifies the visible `#export-tip` element intercepting pointer events. Its screenshot shows the tooltip over the lower editor area. No force click, DOM change, generated-output repair or favorable retry was used. This is a failure of that observed pointer sequence; it does not establish that every possible route is blocked.
5. **Run 3 tooltip association:** the authored English tooltip renders on hover/focus, but Export has no `aria-describedby` link to it. Its text appears in the captured accessible tree when exposed, without proving a correct control-description relationship or screen-reader announcement. Run 2 does have the description link.

No comprehensive contrast or palette audit was performed here. The independent source review records other non-language concerns, including optional numeric contrast inaccuracies. They are not silently cleared by this language-only browser result.

## Immutability and limits

Before/after SHA256 values match for all six generated HTML/JSON files. The probe writes only project artifacts. There were no generated-output or canonical-skill changes, model reruns, or hidden repairs. The browser report retains unavailable/failed operations alongside successful language checks.

Evidence layer: **observed-working for authored language in the local generated browser previews**, with the specific functional failure/limitations above. This does not verify Claude/Codex/ChatGPT/Copilot host rendering, native terminal controls, host chrome locale, real server authorization or cancellation, host-mediated downloads, complete accessibility, or representative-user usability. Host acceptance and user testing remain unverified.
