# ECharts Animated SVG release validation — 2026-09-02

## Outcome

PASS. Three fresh isolated Spark repetitions generated and validated the exact
static SVG, animated SVG, and validation report on one unchanged runtime
payload.

| Run | Strict gates | Tool calls | Duration |
| --- | --- | ---: | ---: |
| `20260902-echarts-runtime-bar-spark-4` | pass | 6 | 28.156 s |
| `20260902-echarts-runtime-bar-spark-5` | pass | 10 | 39.859 s |
| `20260902-echarts-runtime-bar-spark-6` | pass | 7 | 28.907 s |

Runtime payload: 10 files, SHA-256
`79c624db4183940ad301da52cf946d4cdc5014ffa5bae24ecc689dc01847903b`.
Every run observed `openai-codex/gpt-5.3-codex-spark`, emitted valid JSON
events, had zero tool errors, created all exact outputs, kept reads confined to
the copied skill and prompt, and left the payload unchanged.

Independent validation also passed 3/3. Each derivative preserves all 26 source
elements and labels, provides 20 animated marks, uses the bar profile, includes
keyframes, staggered delays, and a reduced-motion fallback, and contains no
remote reference. Chromium confirmed that the early and final frames differ,
the final frame is nonblank, all marks are visible after completion, horizontal
overflow is zero, and reduced-motion disables animations while keeping all 20
marks visible. The three final-frame hashes are identical.

Durable event/read-surface summaries:

- `evaluations/echarts-animated-svg-20260902-read-surface-4.json`
- `evaluations/echarts-animated-svg-20260902-read-surface-5.json`
- `evaluations/echarts-animated-svg-20260902-read-surface-6.json`
