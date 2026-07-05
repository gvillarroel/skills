First action: read this prompt at `../prompt.md`. Then run the exact command below once from the current workspace root, without prepending `cd /mnt/data`, `pwd`, `ls`, or any directory/probe command. After it exits successfully, read only `projects/metro-series-pattern-plan/artifacts/reviews/metro-video-series-plan.json`, report whether `passed` is true, and stop.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_video_series.py --prompt-file ../prompt.md --output projects/metro-series-pattern-plan/artifacts/reviews/metro-video-series-plan.json --min-videos 5 --min-helper-diversity 4 --min-primary-diversity 4 --min-reusable-d3-patterns 6 --max-same-helper-run 2
```

Task: plan a Metro Minimal Tonal Motion video series. The series must use different visual metaphors per module, not one generic systems-flow scaffold.

### What is an LLM

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00-0:20 | Tokens become context, attention, and next-token probabilities. | Token stream, context window, attention matrix tiles, matmul tiles, GPU compute cells. |
| 0:20-0:40 | The transformer uses attention and parameters to predict the next token. | QKV projection, attention heads, matrix accumulation, output token append loop. |

### LLM Billing

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00-0:20 | Billing comes from model choice, input tokens, output tokens, credits, and local GPU cost. | Sankey bands split token input, cached input, output, credits, and local hardware cost. |
| 0:20-0:40 | Bad retry loops turn into spend. | Cost meter, loss branch, optimization branch, embedded bars. |

### What is a Guardrail

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00-0:20 | Guardrails are policies and checks around risky actions. | Bowtie barrier, threats, policy gates, mitigations, repair actions. |
| 0:20-0:40 | The safest design separates prevention, detection, and response. | Preventive controls, top event lock, consequence lanes, recovery path. |

### What is an MCP

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00-0:20 | MCP connects clients to tools, resources, prompts, and servers. | Circuit signal traces, ports, server blocks, permissions, handshake packets. |
| 0:20-0:40 | Tool sprawl increases risk and context cost. | Adjacency matrix, permission gates, fallback reroute, registry boundary. |

### What AI alternatives we have

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00-0:20 | Alternatives differ by home base: knowledge, personal productivity, coding, and research. | Comparison matrix, rows, embedded bars, platform columns, ranking shifts. |
| 0:20-0:40 | Choose by workflow gravity, cost model, and governance needs. | Scenario tree, decision gate, fallback route, selected outcome. |
