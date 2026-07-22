## Core model modules

### What is an LLM

#### Executive summary

A large language model is a transformer-based neural network trained to predict text autoregressively: given prior tokens, it estimates the next token and repeats that process until it reaches a stopping condition. Tokens are chunks of text rather than full words, and the model’s size usually refers to its number of learned parameters, not its context window or factual correctness. Modern LLM training and inference depend heavily on GPUs because transformers map well to parallel matrix operations, and larger models often improve capability on average, although scaling laws describe trends rather than guarantees. citeturn16search4turn34view0turn15search0turn16search3turn17search16turn17search0

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A large language model, or LLM, is software trained to continue text. You give it context, and it predicts the next token, then the next, then the next.” | `token_stream` flows left to right; caption: **Context → Next token → Repeat** |
| 0:15–0:30 | “That word ‘token’ matters. A token is not always a whole word. It can be punctuation, part of a word, or a short chunk of text.” | Split “understanding” into multiple token blocks; bottom ticker: **Tokens ≠ words** |
| 0:30–0:45 | “Most modern LLMs use the transformer architecture. The transformer became dominant because attention scales better than older sequence models for large language tasks.” | `context_window_box` expands; attention arcs animate between tokens |
| 0:45–1:00 | “Autoregressive means every newly generated token becomes part of the context for the next prediction. The model is always reading what has already been written.” | Loop animation: prior output folds back into prompt area |
| 1:00–1:15 | “When people say a model is seven billion or one hundred seventy-five billion, they usually mean parameters: the learned numeric weights inside the network.” | Huge parameter counter rises; subtitle: **Parameters = learned weights** |
| 1:15–1:30 | “More parameters often improve average performance, but size alone does not guarantee accuracy, reasoning quality, or cost efficiency.” | Capability meter grows while warning icon flashes **Not equal to truth** |
| 1:30–1:45 | “Running LLMs usually means GPUs. AI GPUs like NVIDIA H100 and H200 pair tensor cores with large, high-bandwidth memory to serve transformer workloads.” | `gpu_rack` slides in with H100/H200 memory labels |
| 1:45–2:00 | “So the simplest definition is this: an LLM is a token-predicting transformer running on parallel compute, guided by context, and scaled by parameters, data, and compute.” | Full-screen recap stack: **Tokens / Transformer / Parameters / GPUs / Context** |

Reference basis for narration and screen copy: transformer architecture, autoregressive generation, tokenization, scaling, and GPU design. citeturn16search4turn34view0turn15search0turn16search3turn17search0turn17search12

#### Shot and animation plan

- Reuse `token_stream`; show text splitting into tokens, then collapsing back into a sentence.
- Reuse `context_window_box`; animate older tokens fading while recent tokens stay bright.
- Morph token bars into an attention graph to introduce transformers.
- Reuse `parameter_counter`; scale from millions to billions with no brand-specific clutter.
- Reuse `gpu_rack`; pan from consumer GPU silhouette to data-center GPU rack.
- End with a four-tile summary card that can be reused as a chapter bumper in later videos.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What does LLM stand for? | Large language model. citeturn24search17turn16search1 | citeturn24search17turn16search1 |
| What does the model actually do? | It predicts tokens autoregressively from prior context. citeturn34view0 | citeturn34view0 |
| Is a token the same as a word? | No. Tokens can be shorter or longer than a word. citeturn15search0 | citeturn15search0 |
| What is a transformer? | The attention-based architecture behind most modern LLMs. citeturn16search4 | citeturn16search4 |
| What are parameters? | Learned weights inside the network. citeturn16search3turn34view0 | citeturn16search3turn34view0 |
| Does bigger always mean better? | Not always; scaling improves trends, not guarantees. citeturn16search3 | citeturn16search3 |
| Why are GPUs used? | Transformers rely on large parallel tensor operations that GPUs accelerate well. citeturn17search16turn17search0 | citeturn17search16turn17search0 |
| Is the context window the same as model size? | No. Context window and parameter count are different properties. citeturn15search7turn34view0 | citeturn15search7turn34view0 |

#### References

Primary references for this module: OpenAI token guide, GPT-3 paper, Transformer paper, scaling laws, NVIDIA H100/H200 product material. citeturn15search0turn34view0turn16search4turn16search3turn17search0turn17search12

### LLM Billing

#### Executive summary

LLM billing is best understood as “tokens in, tokens out, model selected, extras enabled.” GitHub Copilot now meters usage in AI credits where 1 credit equals $0.01 and actual spend depends on token counts and model rates; Anthropic’s API prices Claude models directly per million input, cached-input, and output tokens, while Claude subscriptions bundle or cap usage in different ways. Even “local” models are not free: they consume electricity, hardware life, and developer time, so local inference should be compared against API cost, latency, and opportunity cost instead of being treated as zero-cost. citeturn14search0turn13view0turn13view3turn14search1turn29view0turn35view3turn35view1turn28view0turn17search1turn19view1

#### Worked cost examples

| Example | Assumptions | Calculation | Estimated cost |
|---|---|---|---|
| Claude Sonnet API call | 120k input tokens, 20k output tokens on Claude Sonnet 4.6 at $3 input and $15 output per 1M tokens | `(0.12 × 3) + (0.02 × 15)` | **$0.66** citeturn29view0 |
| Claude Opus API call | 120k input, 20k output on Claude Opus 4.8 at $5 input and $25 output per 1M tokens | `(0.12 × 5) + (0.02 × 25)` | **$1.10** citeturn29view0 |
| GitHub Copilot GPT-5.4-style usage | 120k input, 20k output at $2.50 input and $15 output per 1M tokens | `(0.12 × 2.5) + (0.02 × 15)` | **$0.60 = 60 AI credits** citeturn13view0turn14search0 |
| Copilot Pro allowance intuition | Pro includes 1,500 AI credits per month | `1500 / 60` examples of the call above | **~25 such interactions** citeturn14search0turn13view3 |
| Local GPU electricity only | RTX 4090 at 450W; 2 hours/day; EIA March 2026 residential average 18.83¢/kWh | `0.45 × 2 × 0.1883` | **~$0.17/day** citeturn17search1turn19view1 |
| Local monthly electricity only | Same assumptions, 22 workdays/month | `0.17 × 22` | **~$3.73/month** citeturn17search1turn19view1 |
| Local hardware amortization | **Assumption:** $1,600 GPU over 24 months | `1600 / 24` | **~$66.67/month** |
| Local opportunity cost | **Assumption:** 10 extra waiting minutes/day at $80/hour over 22 workdays | `(10/60) × 80 × 22` | **~$293/month** |

The local-model rows deliberately separate **facts** from **assumptions**. GPU power draw and average U.S. electricity rate are sourced; purchase price and hourly loaded labor rate are scenario assumptions for planning, not vendor-quoted facts. citeturn17search1turn19view1

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “LLM billing looks confusing until you reduce it to four things: model, input tokens, output tokens, and whether a platform wraps that usage in a subscription.” | `credit_meter` with four labeled dials |
| 0:15–0:30 | “GitHub Copilot now measures usage in AI credits. One AI credit equals one cent, and token usage is converted into credits based on the selected model.” | Credit counter fills from token bars; text: **1 AI credit = $0.01** |
| 0:30–0:45 | “Copilot Pro includes one thousand five hundred credits a month, and Business includes one thousand nine hundred per seat in a pooled organization bucket.” | Split screen: individual vs pooled bucket |
| 0:45–1:00 | “Anthropic is more direct on the API side. Claude models are priced per million input, cached input, and output tokens, so more context and more output both matter.” | Claude pricing table cards animate in |
| 1:00–1:15 | “Subscriptions do not remove the underlying cost. They package it. Pro includes Claude Code, Team adds seats and controls, and Enterprise adds seat price plus usage at API rates.” | Subscription layers stack above raw token meter |
| 1:15–1:30 | “Now the hidden lesson: local models are not free. Your GPU draws power, your hardware ages, and slower responses can cost developer time.” | `gpu_rack` + power meter + clock icon |
| 1:30–1:45 | “If your workflow spends lots of time reading giant logs or retrying vague prompts, cost rises fast. Better prompts, smaller models, hooks, and skills usually save money.” | Before/after waterfall: waste vs optimized |
| 1:45–2:00 | “So when evaluating cost, compare subscription, API usage, and local opportunity cost together. The cheapest path is the one that finishes the work accurately with the fewest wasted loops.” | Final scorecard: **$ / latency / retries / human time** |

Reference basis for narration and examples: GitHub usage-based billing, Copilot plan pricing, Claude pricing, Claude cost-management guidance, GPU power, and EIA electricity data. citeturn14search0turn13view0turn13view3turn14search1turn29view0turn35view1turn28view0turn17search1turn19view1

#### Shot and animation plan

- Reuse `credit_meter` and `token_stream`; animate tokens converting into dollars or credits.
- Use a split panel for **API**, **subscription**, and **local GPU** so the audience sees the same workload through three billing lenses.
- Animate one costly “retry spiral” to show how bad prompting turns into real spend.
- Reuse `gpu_rack` and `power_curve` for local cost.
- Flash small “assumption” tags on amortization and hourly-rate examples.
- End with a reusable optimization infographic: **smaller model / tighter prompt / fewer loops / lower cost**.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What actually drives API cost? | Model choice plus input, cached-input, and output token counts. citeturn13view0turn29view0 | citeturn13view0turn29view0 |
| What is a GitHub AI credit? | A billing unit equal to $0.01. citeturn14search0turn14search1 | citeturn14search0turn14search1 |
| Does Copilot still have seat pricing? | Yes. It has seat pricing plus AI-credit usage. citeturn14search4turn14search0 | citeturn14search4turn14search0 |
| Does Claude Code have a subscription option? | Yes. Claude Pro includes Claude Code; Team and Enterprise add organization features. citeturn35view3turn35view1turn35view2 | citeturn35view3turn35view1turn35view2 |
| Is cached input cheaper? | Usually yes; both Copilot and Anthropic publish lower cached-input rates. citeturn13view0turn29view0 | citeturn13view0turn29view0 |
| Are code completions billed the same as chat in Copilot? | No. Paid plans keep code completions and next edit suggestions outside AI-credit billing. citeturn14search0turn14search1 | citeturn14search0turn14search1 |
| Are local models free? | No. Electricity, hardware, and human time still cost money. citeturn17search1turn19view1 | citeturn17search1turn19view1 |
| What usually saves the most money? | Smaller models when sufficient, less context, fewer retries, and preprocessing through hooks or skills. citeturn28view0 | citeturn28view0 |

#### References

Primary references for this module: GitHub Copilot pricing and billing docs, Anthropic pricing docs, Claude plan pricing, EIA electricity rates, NVIDIA RTX 4090 power specs. citeturn13view0turn13view3turn14search0turn14search1turn29view0turn35view1turn35view3turn28view0turn17search1turn19view1

### LLM Probabilities and Evaluation

#### Executive summary

LLMs do not “look up the one true answer” during generation; they assign probabilities over candidate next tokens and then select or sample from that distribution. Better context helps because it reshapes the distribution toward better tokens, but the output remains probabilistic. In coding and agentic systems, this is why **pass@N** matters: if you sample multiple candidates, you often get a higher chance that at least one is correct; practical evaluation then uses programmatic checks where possible and model-based judging where automation is harder. citeturn33search4turn33search1turn20search0turn32view0turn20search9turn20search6turn20search3

```mermaid
flowchart LR
    A[Prompt + context] --> B[Model computes token distribution]
    B --> C{Select token}
    C -->|greedy / sampled| D[Append token to context]
    D --> B
    D --> E[Candidate answer]
    E --> F{Evaluation}
    F -->|unit tests/schema/rules| G[Programmatic verdict]
    F -->|rubric or judge model| H[LLM-as-judge verdict]
    G --> I[pass@1 / pass@N / score]
    H --> I
```

The diagram highlights the main teaching point: generation and evaluation are separate loops. Token probabilities describe **how** text is produced; pass@N and verification describe **how** you decide whether the produced answer is good enough. citeturn33search4turn20search9turn20search3

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “Every token an LLM produces comes from a probability distribution. The model scores many possible next tokens, then one gets selected.” | `probability_bars` animate above a blinking cursor |
| 0:15–0:30 | “That means two things. First, outputs can vary across runs. Second, better context usually improves results because it changes the distribution.” | Same prompt with poor vs rich context, bars shift visibly |
| 0:30–0:45 | “Tools like log probabilities let you inspect confidence after generation, and logit bias can nudge certain tokens up or down.” | Confidence thermometer and boosted/suppressed token cards |
| 0:45–1:00 | “In coding, one answer is often not enough. So teams use pass at N: generate multiple candidates and ask whether at least one of them is correct.” | `passN_grid` fills with green and red boxes |
| 1:00–1:15 | “The classic example is HumanEval, where generated code is executed against tests. If any of N samples pass, that improves pass at N even if pass at one stays lower.” | Test runner panel; one out of five turns green |
| 1:15–1:30 | “Programmatic verification is the gold standard when you can use it: unit tests, schema checks, exact match, parsers, or tool-execution success.” | Checklist icons: tests, JSON schema, parser, sandbox |
| 1:30–1:45 | “When you cannot write objective checks, you can still use an LLM as judge, but only with a clear rubric and calibration against human review.” | Judge panel with rubric cards and agreement gauge |
| 1:45–2:00 | “So the big lesson is simple: treat LLM outputs like samples from a distribution, then build evaluation loops that make correctness measurable.” | Full-screen recap: **Distribution → Samples → Verification → Metrics** |

Reference basis for narration and evaluation framing: OpenAI logprobs/logit bias docs, HumanEval/Codex evaluation work, OpenAI eval best practices, and Anthropic evaluation guidance. citeturn33search4turn33search1turn20search0turn32view0turn20search9turn20search6turn20search3

#### Shot and animation plan

- Reuse `probability_bars`; show top three candidate tokens changing with richer context.
- Reuse `context_window_box`; animate a better prompt narrowing uncertainty.
- Show a compact `passN_grid` with one correct answer emerging only on sample four.
- Reuse `test_runner` asset from any existing code-verification scene.
- Animate a judge model rubric as cards scoring correctness, completeness, and policy compliance.
- End with the same summary formula card every later evaluation-focused video can reuse.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| Why do answers vary? | Because generation is probabilistic, not perfectly deterministic. citeturn33search4turn20search9 | citeturn33search4turn20search9 |
| What does logprobs show? | The log probabilities of returned tokens and some likely alternatives. citeturn33search0turn33search16 | citeturn33search0turn33search16 |
| What does logit bias do? | It changes the likelihood of specified tokens. citeturn33search1 | citeturn33search1 |
| What is pass@N? | A metric asking whether at least one of N sampled candidates is correct. citeturn20search0turn32view0 | citeturn20search0turn32view0 |
| Why is pass@N useful? | Some tasks benefit from multiple diverse samples plus a selection or verification step. citeturn32view0 | citeturn32view0 |
| What is the strongest evaluation method for code? | Executable tests or other programmatic verification. citeturn20search0turn20search4 | citeturn20search0turn20search4 |
| When should I use an LLM as judge? | When objective rules are hard to write, but only with a rubric and calibration. citeturn20search3turn20search6 | citeturn20search3turn20search6 |
| What simple metrics should beginners track? | pass@1, pass@N, exact match, tool success rate, and judged quality. citeturn20search9turn20search6 | citeturn20search9turn20search6 |

#### References

Primary references for this module: OpenAI logprobs and logit-bias docs, HumanEval/Codex evaluation paper, OpenAI evaluation best practices, Anthropic evaluation guidance. citeturn33search4turn33search1turn20search0turn32view0turn20search9turn20search6turn20search3

### What is an Agent

#### Executive summary

An agent is not just “an LLM with tools.” In current official platform guidance, an agentic system combines a model with tools, state or memory, and orchestration. For teaching, the cleanest minimal decomposition is: **context** the agent sees, **environment** it can observe or affect, **actions** it can take, and a **loop or policy** that decides what to do next. The crucial distinction is between a short, explicit workflow and an agent that can iteratively plan, act, read results, and continue. citeturn21search18turn21search1turn21search0turn9view1turn38view1

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “An agent is a system that does more than answer once. It can observe context, take actions, inspect results, and continue in a loop.” | `agent_loop_ring` appears with Observe / Act / Check / Continue |
| 0:15–0:30 | “At minimum, you need four pieces: context, environment, actions, and a policy that decides the next step.” | Four labeled cards slide into a square |
| 0:30–0:45 | “Context is what the agent knows right now: chat history, files, instructions, memory, and tool outputs.” | `context_window_box` fills with layered sources |
| 0:45–1:00 | “Environment is where it operates: a repo, terminal, browser, ticket system, docs, or database.” | Workspace transforms into repo + browser + issue tracker |
| 1:00–1:15 | “Actions are what it can do: read files, run tests, search docs, call APIs, or ask for approval.” | Tool icons animate around the loop |
| 1:15–1:30 | “The policy or loop is the runtime brain around the model. It decides whether to keep exploring, execute a tool, or stop.” | Loop slows at a decision fork |
| 1:30–1:45 | “This is why vendors separate workflows from agents. A workflow is fixed steps. An agent adapts based on what it finds.” | Left panel fixed DAG; right panel adaptive loop |
| 1:45–2:00 | “So when you hear ‘agent,’ think runtime system, not just model. The LLM is one part; the loop around it is what makes it agentic.” | Final recap: **Model + Tools + State + Loop** |

Reference basis for narration: OpenAI’s agent primitives, Anthropic’s workflow-versus-agent framing, and current coding-agent product behavior in Claude Code and VS Code. citeturn21search18turn21search1turn21search0turn9view1turn38view1

#### Shot and animation plan

- Reuse `agent_loop_ring` as the visual identity for every agent-related module.
- Represent context as stacked translucent panes rather than text walls.
- Animate environment changes: repo, terminal, browser, ticket system.
- Use one “fixed workflow” lane and one “adaptive agent” lane for contrast.
- Add approval checkpoint icon near the end to foreshadow guardrails and permissions.
- Reuse the final **Model + Tools + State + Loop** badge in harness and MCP videos.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| Is an agent just an LLM? | No. Current guidance treats models, tools, state, and orchestration as separate primitives. citeturn21search18turn21search1 | citeturn21search18turn21search1 |
| What is the minimum mental model? | Context, environment, actions, and loop or policy. citeturn21search18turn21search0 | citeturn21search18turn21search0 |
| What counts as context? | Instructions, chat history, files, memory, and tool outputs. citeturn21search18turn23search4 | citeturn21search18turn23search4 |
| What counts as environment? | The systems the agent can inspect or affect, such as repos or apps. citeturn9view1turn38view1 | citeturn9view1turn38view1 |
| Why do agents need tools? | Tools let them move from text generation to external action. citeturn21search18turn21search4 | citeturn21search18turn21search4 |
| What is the difference between a workflow and an agent? | A workflow follows predefined steps; an agent can decide the next step dynamically. citeturn21search0 | citeturn21search0 |
| Does memory make something an agent? | Memory helps, but the core distinction is iterative action under orchestration. citeturn21search18turn23search4 | citeturn21search18turn23search4 |
| Why is this distinction useful? | It helps teams scope complexity, cost, and risk before adding autonomy. citeturn21search1turn21search0 | citeturn21search1turn21search0 |

#### References

Primary references for this module: OpenAI building-agents guides, Anthropic building-effective-agents guidance, Claude Code and VS Code agent docs. citeturn21search18turn21search1turn21search0turn9view1turn38view1

## Control and extension modules

### What is a Guardrail

#### Executive summary

A guardrail is a control layer that checks inputs, outputs, or tool behavior and then blocks, routes, redacts, or escalates based on policy. Official guidance from both OpenAI and Google frames guardrails as validation and governance mechanisms rather than as “magic safety.” Google Cloud Model Armor is a particularly concrete example because it can screen prompts and responses for prompt injection, jailbreaks, sensitive data, malicious URLs, and related risks; it has a free tier up to two million tokens per month and then usage pricing beyond that. citeturn22search9turn22search2turn22search1turn22search4turn22search0turn22search13

#### Recommended implementation snippet

```python
# Pseudocode: input and action guardrail
risk = model_armor.scan(prompt)

if risk.prompt_injection >= HIGH:
    return block("Prompt injection risk too high")

if risk.sensitive_data_detected:
    prompt = redact(prompt)

if action in {"deploy", "delete", "write_prod"}:
    return require_human_approval(action)

return continue_run(prompt)
```

The pattern above matches current platform guidance: automatic validation first, human approval for sensitive actions, then continuation only if policy passes. citeturn22search9turn22search15turn22search4turn22search20

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A guardrail is a control layer around an agent. Its job is not to do the task. Its job is to decide whether the task should proceed.” | `shield_gate` closes over the agent loop |
| 0:15–0:30 | “Guardrails can inspect user prompts, model outputs, and tool calls. Then they can block, redact, route, or escalate.” | Three gates labeled **Input / Output / Action** |
| 0:30–0:45 | “That makes them different from prompting. A prompt suggests behavior. A guardrail enforces a policy.” | Split screen: prompt bubble vs hard gate |
| 0:45–1:00 | “Google Model Armor is a strong example. It can screen for prompt injection, jailbreaks, sensitive data, and malicious URLs.” | Model Armor filters fan out as colored lanes |
| 1:00–1:15 | “OpenAI’s guidance uses the same design idea: run automatic checks, and pause for human review before risky work continues.” | Human approval button appears over a deploy action |
| 1:15–1:30 | “For code assistants, guardrails often protect secrets, production systems, or destructive commands.” | `.env`, `rm`, and deploy icons light up red |
| 1:30–1:45 | “Good guardrails reduce risk and wasted retries. Bad guardrails create false positives and slow teams down.” | Balance scale: safety vs friction |
| 1:45–2:00 | “So define guardrails as enforceable policies over input, output, and actions, not as just another prompt trick.” | Recap card: **Policy checks over agent behavior** |

Reference basis for narration: OpenAI guardrail guidance and Google Model Armor product and docs. citeturn22search9turn22search2turn22search1turn22search4turn22search0turn22search13

#### Shot and animation plan

- Reuse `shield_gate` around the `agent_loop_ring`.
- Show three inspection layers: incoming prompt, generated text, outgoing tool call.
- Animate one positive case and one blocked case so the gate feels functional.
- Reuse a `risk_score` bar derived from `probability_bars`.
- Add a human approval modal for a production deploy.
- End with a green-yellow-red policy matrix that can be reused in hooks and permissions modules.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What does a guardrail do? | It validates behavior and decides whether a run should continue, pause, or stop. citeturn22search9turn22search2 | citeturn22search9turn22search2 |
| Is a guardrail just a prompt? | No. Prompts guide behavior; guardrails enforce policies. citeturn22search2turn22search9 | citeturn22search2turn22search9 |
| What can Model Armor check? | Prompt injection, jailbreaks, sensitive data, malicious URLs, and more. citeturn22search4turn22search20 | citeturn22search4turn22search20 |
| Does Model Armor have a free tier? | Yes, up to two million tokens per month. citeturn22search0turn22search13 | citeturn22search0turn22search13 |
| When do I need human review? | For sensitive or high-impact actions such as writes, deletes, or deploys. citeturn22search9turn22search15 | citeturn22search9turn22search15 |
| Can guardrails lower cost? | Yes, by blocking bad runs early and by reducing expensive retries. citeturn22search2turn28view0 | citeturn22search2turn28view0 |
| Can guardrails be too strict? | Yes. High false positives create friction and reduce usefulness. citeturn22search1turn22search8 | citeturn22search1turn22search8 |
| What is the easiest first guardrail? | Secret protection plus approval on destructive actions. citeturn22search15turn9view0 | citeturn22search15turn9view0 |

#### References

Primary references for this module: OpenAI guardrails and human review, OpenAI guardrail cookbook, Google Model Armor overview, filtering docs, and pricing. citeturn22search9turn22search2turn22search1turn22search4turn22search0turn22search13

### What is a Harness

#### Executive summary

A harness is the runtime wrapper that turns a raw model into a usable assistant or agent. It usually defines the instruction layers, default tools, permissions, model picker, execution loop, approvals, memory behavior, logging, and extensibility surface. In practice, choosing GitHub Copilot, Claude Code, OpenCode, or VS Code agents means choosing a harness with defaults that materially affect quality, latency, cost, and risk. citeturn38view0turn9view1turn38view2turn38view1

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A harness is the shell around the model. It decides how the assistant is instructed, what tools it can use, and how the loop is controlled.” | `comparison_grid` zooms into a single runtime stack |
| 0:15–0:30 | “Think of it as the difference between an engine and a car. The model is the engine. The harness is steering, brakes, dashboard, and controls.” | Engine icon morphs into a vehicle dashboard |
| 0:30–0:45 | “A harness usually includes instruction layers, default tools, permissions, memory rules, approvals, looping logic, and logging.” | Runtime stack assembles layer by layer |
| 0:45–1:00 | “That is why different harnesses feel different even when they can call the same model.” | Same model badge dropped into three different shells |
| 1:00–1:15 | “GitHub Copilot emphasizes GitHub-native workflows and explicit AI-credit accounting. Claude Code emphasizes skills, hooks, MCP, and coding autonomy. OpenCode emphasizes openness and provider choice.” | Three-column harness cards |
| 1:15–1:30 | “Harness choice also changes cost. More default tools, more context, more retries, and more autonomous loops usually mean more spend.” | `credit_meter` rises with tool count |
| 1:30–1:45 | “So a good harness is not the one with the most features. It is the one whose defaults fit your team’s tasks, controls, and budget.” | Features grid fades behind use-case matrix |
| 1:45–2:00 | “Use the comparison matrix in this report as your selection guide, then customize only the parts that matter most.” | Matrix reappears with highlighted selection path |

Reference basis for narration: harness product docs from GitHub Copilot, Claude Code, OpenCode, and VS Code agents. citeturn38view0turn9view1turn38view2turn38view1turn13view0turn29view0

#### Shot and animation plan

- Reuse `comparison_grid` and `agent_loop_ring`.
- Stack runtime layers: prompt, tools, permissions, loop, logging.
- Show same model icon in different harness shells.
- Use a simple “engine vs car” motion metaphor to make the abstraction sticky.
- Reuse `credit_meter` to show how harness defaults change spend.
- Close with a pointer back to the harness comparison matrix.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What is a harness? | The runtime shell around the model: instructions, tools, permissions, loop, and controls. citeturn38view0turn9view1turn38view2turn38view1 | citeturn38view0turn9view1turn38view2turn38view1 |
| Why do harnesses matter? | Because they change behavior even when using similar models. citeturn38view1turn27search4 | citeturn38view1turn27search4 |
| What normally lives inside a harness? | Instruction layers, tools, permissions, memory, loop logic, and logging. citeturn21search18turn23search3 | citeturn21search18turn23search3 |
| Why does harness choice affect cost? | Defaults influence token use, retries, and tool calls. citeturn28view0turn14search0 | citeturn28view0turn14search0 |
| Can two harnesses use the same model differently? | Yes. The runtime and tool surface still differ. citeturn38view1turn38view2 | citeturn38view1turn38view2 |
| What is the first selection criterion? | Fit to workflow, controls, and budget—not feature count alone. citeturn21search1turn28view0 | citeturn21search1turn28view0 |
| Is a harness the same as a model provider? | No. OpenCode and VS Code can route to many providers. citeturn27search21turn38view1 | citeturn27search21turn38view1 |
| What should teams customize first? | Instructions, permissions, approvals, and the most-used tools. citeturn23search1turn27search16turn22search9 | citeturn23search1turn27search16turn22search9 |

#### References

Primary references for this module: GitHub Copilot cloud agent and billing docs, Claude Code overview and prompt customization docs, OpenCode agents and model docs, VS Code agents docs. citeturn38view0turn13view0turn9view1turn27search4turn38view2turn27search21turn38view1

### What is a Harness Hook

#### Executive summary

A harness hook is an active interception point in the runtime lifecycle. Hooks are where policy becomes executable: before or after tool use, at session start or stop, on permission requests, during compaction, or when notifications fire. GitHub Copilot and Claude Code both expose first-class hook systems, while OpenCode exposes comparable event-driven interception through plugin events. Good hooks can reduce cost by preprocessing data and avoiding bad runs; poor hooks can increase latency or produce unnecessary extra work. citeturn10view0turn10view1turn9view3turn8search13turn12view4turn12view5

#### Recommended implementation snippet

```bash
# Pseudocode hook: block dangerous commands before tool use
event = read_json()

if event.type == "PreToolUse" and event.tool == "Bash":
    if matches(event.command, ["rm -rf", "kubectl delete", "terraform destroy"]):
        deny("Blocked by repository hook policy")
    else:
        allow()
```

That pattern is directly aligned with GitHub and Claude hook use cases: validation, audit, and execution control around tool calls. citeturn10view1turn10view0turn9view3

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A harness hook is an event-driven interception point. Something important happens in the runtime, and your custom logic gets a chance to react.” | `event_timeline` lights up event nodes |
| 0:15–0:30 | “Hooks are active guardrails because they run during execution, not just before a session begins.” | Timeline overlays the `shield_gate` |
| 0:30–0:45 | “GitHub Copilot hooks execute external commands at lifecycle points like session start, prompt submit, tool calls, and agent stop.” | GitHub hook events appear as badges |
| 0:45–1:00 | “Claude Code hooks go even wider. They can be shell commands, HTTP endpoints, or LLM prompts, and they cover session, turn, tool, compaction, and more.” | Claude event cloud expands around the loop |
| 1:00–1:15 | “OpenCode expresses similar control through plugin events such as tool execute before and after, shell environment injection, and session idle.” | OpenCode event list animates vertically |
| 1:15–1:30 | “Typical hook jobs are formatting, validation, secret protection, audit logging, notifications, and narrowing huge data before the model sees it.” | Examples cascade across the screen |
| 1:30–1:45 | “Hooks can lower cost by shrinking context. But they can raise cost or delay work if they call slow services or trigger too often.” | Speed-vs-cost slider |
| 1:45–2:00 | “So use hooks for enforcement and preprocessing at clear lifecycle boundaries, not as a place to hide random business logic.” | Final rule card: **hooks = lifecycle controls** |

Reference basis for narration: GitHub hooks docs and reference, Claude Code hooks reference, OpenCode event system. citeturn10view0turn10view1turn9view3turn8search13turn12view4turn12view5

#### Shot and animation plan

- Reuse `event_timeline` and `shield_gate`.
- Show a bright pulse moving through lifecycle events.
- Visualize one hook blocking a command and another filtering log output.
- Animate GitHub, Claude, and OpenCode event badges in the same timeline style.
- Add a token-savings counter when preprocessing reduces context.
- End with a “hooks are for lifecycle boundaries” stamp.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What is a hook? | Custom logic that runs at specific lifecycle events. citeturn10view1turn9view3 | citeturn10view1turn9view3 |
| Why call hooks active guardrails? | Because they intercept execution as it happens. citeturn10view1turn8search13 | citeturn10view1turn8search13 |
| Where do GitHub hooks run? | In Copilot CLI locally and in Copilot cloud agent sandboxes for supported events. citeturn10view0 | citeturn10view0 |
| What can Claude hooks be? | Shell commands, HTTP endpoints, or LLM prompts. citeturn9view3 | citeturn9view3 |
| What are common hook events? | Session lifecycle, prompt submit, pre/post tool use, permission requests, and stop events. citeturn10view0turn9view3 | citeturn10view0turn9view3 |
| What is OpenCode’s equivalent? | Event subscriptions in plugins, including tool and session events. citeturn12view4turn12view5 | citeturn12view4turn12view5 |
| How do hooks affect cost? | They can save tokens through preprocessing or waste time if overused. citeturn28view0 | citeturn28view0 |
| What is the best beginner hook? | Block destructive commands and filter noisy outputs before the model sees them. citeturn10view1turn28view0 | citeturn10view1turn28view0 |

#### References

Primary references for this module: GitHub hooks overview and reference, Claude Code hooks guide and reference, OpenCode plugin events. citeturn10view0turn10view1turn9view3turn8search13turn12view4turn12view5

### What is a Harness Plugin

#### Executive summary

A plugin is a distribution mechanism for reusable harness customization. The exact packaging differs by product, but the pattern is consistent: bundle runtime capabilities so teams can install, share, version, and govern them instead of hand-copying local setup. In current official docs, GitHub Copilot CLI plugins can bundle agents, skills, hooks, and MCP configuration; Claude Code plugins can bundle skills, agents, hooks, and MCP servers from marketplaces; OpenCode plugins are JS/TS modules loaded locally or from npm to add hooks, tools, and integrations. citeturn10view2turn9view0turn11view0turn11view1

#### Recommended implementation snippet

```json
{
  "name": "security-pack",
  "contains": ["hooks", "skills", "mcp", "agent-profile"],
  "defaultEnabled": true,
  "purpose": "secret scanning, safer tool use, shared deploy workflow"
}
```

The important design principle is not the exact file format. It is that plugins package multiple runtime behaviors into one installable unit that can be versioned and governed. citeturn10view2turn9view0

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A harness plugin is how you package and share runtime customization. Instead of copying files by hand, you install one reusable unit.” | `plugin_bundle_cube` assembles from smaller blocks |
| 0:15–0:30 | “The bundle usually contains behavior, not just visuals: skills, hooks, MCP config, special agents, or custom tools.” | Bundle opens to reveal labeled modules |
| 0:30–0:45 | “GitHub Copilot CLI plugins explicitly support reusable agents, skills, hooks, and MCP server configuration.” | GitHub plugin manifest card |
| 0:45–1:00 | “Claude Code’s plugin system also packages skills, agents, hooks, and MCP servers, and it supports controlled marketplaces and managed settings.” | Claude marketplace diagram with allowlist gate |
| 1:00–1:15 | “OpenCode keeps plugins very developer-friendly. They are JavaScript or TypeScript modules that subscribe to events and extend behavior.” | NPM package drops into OpenCode runtime |
| 1:15–1:30 | “This matters because distribution is governance. Plugins let you standardize the approved way to work.” | Team-wide install animation |
| 1:30–1:45 | “Plugins can lower cost by packaging efficient defaults. They can also raise cost if they inject noisy context or expensive tool calls everywhere.” | Good plugin vs bad plugin split |
| 1:45–2:00 | “So define a plugin as a shareable harness bundle for behavior, policy, and integrations—not as just another extension icon.” | Final text: **Plugin = packaged harness behavior** |

Reference basis for narration: GitHub Copilot CLI plugin docs, Claude Code plugin configuration, OpenCode plugin docs. citeturn10view2turn9view0turn11view0turn11view1

#### Shot and animation plan

- Reuse `plugin_bundle_cube` with detachable inner parts.
- Show GitHub, Claude, and OpenCode bundles resolving into comparable capabilities.
- Add a marketplace / allowlist lane for enterprise governance.
- Visualize versioning and upgrade arrows over the same plugin pack.
- Use a red “noisy plugin” example that adds unnecessary tools everywhere.
- End with a package-install visual that can be reused in skills and MCP modules.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What problem do plugins solve? | Repeatable distribution and governance of harness customization. citeturn10view2turn9view0 | citeturn10view2turn9view0 |
| What can a Copilot CLI plugin contain? | Agents, skills, hooks, and MCP configurations. citeturn10view2 | citeturn10view2 |
| What can a Claude Code plugin contain? | Skills, agents, hooks, and MCP servers. citeturn9view0 | citeturn9view0 |
| What is an OpenCode plugin technically? | A JS/TS module that returns hook implementations. citeturn11view0 | citeturn11view0 |
| Why do enterprises care? | Plugins centralize standards, marketplaces, and policy control. citeturn10view2turn9view0 | citeturn10view2turn9view0 |
| Can plugins affect cost? | Yes. Efficient plugins can reduce prompts; noisy or heavy plugins can increase spend. citeturn28view0 | citeturn28view0 |
| Are plugins the same as MCP servers? | No. MCP is a protocol; a plugin may configure or bundle MCP usage. citeturn10view2turn38view3 | citeturn10view2turn38view3 |
| What is a good first plugin pack? | A small quality pack with one skill, one hook policy, and one approved MCP server. | — |

#### References

Primary references for this module: GitHub Copilot CLI plugin docs, Claude Code plugin configuration docs, OpenCode plugin docs. citeturn10view2turn9view0turn11view0turn11view1

### What is a Skill

#### Executive summary

A skill is a reusable capability package that gives the harness structured instructions, scripts, and supporting resources for a specialized task. The cost insight is important: skills support **progressive disclosure** because they load when relevant instead of forcing long procedures into every prompt. GitHub Copilot defines skills as folders of instructions, scripts, and resources; Claude Code says long reference material in a skill “costs almost nothing until you need it”; OpenCode also loads `SKILL.md`-based skills on demand. citeturn10view3turn7search1turn9view2turn11view2

#### Recommended implementation snippet

```markdown
# SKILL.md
---
name: deploy-preview
description: Build, test, and deploy a preview safely
tools:
  - bash
  - read
  - write
---

1. Run targeted tests first.
2. Validate required environment variables.
3. Deploy only to preview environment.
4. Summarize URL and rollback command.
```

The point of a skill is not fancy syntax. It is reusable, scoped expertise that the harness can invoke when relevant instead of re-learning the same workflow every session. citeturn10view3turn9view2turn11view2

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “A skill is a reusable task package. It gives the assistant a named way to perform a specialized job again and again.” | `skill_card_stack` fans open |
| 0:15–0:30 | “Good skills are not giant permanent prompts. They are loaded only when relevant, which keeps normal sessions lighter.” | Long prompt wall shrinks into one skill card |
| 0:30–0:45 | “GitHub Copilot describes skills as folders of instructions, scripts, and resources. Claude and OpenCode use similar SKILL-dot-MD patterns.” | Three compatible folder structures align |
| 0:45–1:00 | “This is progressive disclosure. You keep rich procedures available, but you only pay the token cost when the procedure is actually used.” | Cost meter stays flat until skill activates |
| 1:00–1:15 | “That makes skills perfect for deploy checklists, debugging routines, architecture explainers, onboarding flows, or codebase maps.” | Example skill cards cycle quickly |
| 1:15–1:30 | “A skill can also call scripts or specify approved tools, which makes the workflow more repeatable and safer.” | Tool badges snap onto the skill card |
| 1:30–1:45 | “The common mistake is turning skills into mini novels. Keep them sharp, task-scoped, and reusable.” | A huge bloated card gets trimmed down |
| 1:45–2:00 | “So define a skill as on-demand domain expertise for the harness: reusable, composable, and usually cheaper than repeating the same long prompt.” | Final tag: **Skill = on-demand reusable workflow** |

Reference basis for narration: GitHub skill docs, Claude skill docs, OpenCode skill docs. citeturn10view3turn7search1turn9view2turn11view2

#### Shot and animation plan

- Reuse `skill_card_stack` and show activation only when relevant.
- Show one giant static prompt turning into three small skills.
- Use a cost line that stays flat until the skill is invoked.
- Animate a deploy workflow skill from checklist to executed steps.
- Reuse the same visual card style later for instruction layers.
- End with a reusable “progressive disclosure” callout.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What is a skill? | A reusable set of instructions, scripts, and resources for specialized tasks. citeturn10view3turn7search1 | citeturn10view3turn7search1 |
| Why are skills useful? | They make recurring workflows repeatable and easier to discover. citeturn10view3turn9view2 | citeturn10view3turn9view2 |
| What is progressive disclosure here? | Long procedures stay available but load only when needed. citeturn9view2 | citeturn9view2 |
| Do skills reduce cost? | Often yes, because they avoid repeating long instructions every session. citeturn9view2turn28view0 | citeturn9view2turn28view0 |
| Where do Copilot skills live? | In project or personal skill folders, including `.github/skills`, `.claude/skills`, or `skills`. citeturn10view3 | citeturn10view3 |
| Can Claude skills be invoked directly? | Yes, via slash-style invocation as skills or commands. citeturn9view2 | citeturn9view2 |
| Does OpenCode support Claude-style skills? | Yes. It discovers Claude-compatible `SKILL.md` locations. citeturn11view2 | citeturn11view2 |
| What is the usual beginner mistake? | Writing skills that are too broad, verbose, or always relevant. | — |

#### References

Primary references for this module: GitHub Copilot agent skills docs, Claude Code skills docs, OpenCode skills docs. citeturn10view3turn7search1turn9view2turn11view2

### What is an MCP

#### Executive summary

Model Context Protocol, or MCP, is an open standard for connecting AI clients to external systems such as tools, resources, and prompts. Official MCP documentation describes it as a standardized way for AI applications like Claude or ChatGPT to connect to data sources, tools, and workflows, and current ecosystem documentation shows support across clients including Claude, ChatGPT, VS Code, and GitHub Copilot. The practical risks are authentication, authorization, registry hygiene, and context sprawl: an MCP server that exposes too many tools or broad permissions can increase both attack surface and cost. citeturn38view3turn25search3turn25search9turn10view4turn8search17turn37search14turn25search11turn7search10turn7search21

#### Recommended implementation snippet

```json
{
  "server": "issue-tracker",
  "auth": "oauth",
  "tools": ["list_issues", "get_issue", "comment_issue"],
  "policy": {
    "allow_write": false,
    "require_approval_for": ["comment_issue"]
  }
}
```

The teaching point is that MCP integration is not just connectivity. It is capability exposure plus policy. Good MCP setup means least privilege, approved registries, and deliberate tool surface design. citeturn10view4turn7search10turn7search21turn25search11

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “MCP stands for Model Context Protocol. It is an open standard for connecting AI applications to external systems.” | `mcp_bus` with multiple client and server ports |
| 0:15–0:30 | “Instead of building one custom integration per assistant, MCP gives clients and servers a shared protocol.” | One-to-many connector diagram replaces spaghetti lines |
| 0:30–0:45 | “An MCP server can expose tools, resources, and prompts. That means an assistant can read data, execute actions, or import structured workflows.” | Three lanes labeled **Tools / Resources / Prompts** |
| 0:45–1:00 | “Today MCP is supported across major clients, including Claude, ChatGPT-related ecosystems, VS Code, and GitHub Copilot.” | Client logos or neutral platform cards connect to the bus |
| 1:00–1:15 | “But power creates risk. Authentication and authorization matter because MCP can expose real systems, not just toy tools.” | Lock icons appear on the bus |
| 1:15–1:30 | “That is why registries, allowlists, and approval policies matter. GitHub already lets organizations control registry URLs and server access.” | Registry gate animation |
| 1:30–1:45 | “MCP also affects cost. Every discovered tool, every tool description, and every tool call can add context or external API spend.” | Context meter and external-billing icons rise |
| 1:45–2:00 | “So define MCP as the standard plumbing for AI tools and context—but use least privilege, approval, and narrow tool design.” | Final stamp: **Open standard, strict permissions** |

Reference basis for narration: official MCP intro/spec docs, GitHub Copilot MCP docs and policy docs, Claude Code MCP docs, and VS Code MCP docs. citeturn38view3turn25search3turn25search9turn10view4turn8search17turn37search14turn7search10turn7search21turn25search11

#### Shot and animation plan

- Reuse `mcp_bus` as the core visual identity for all integrations.
- Show one messy point-to-point integration map transforming into one protocol bus.
- Animate tools, resources, and prompts as different bus passengers.
- Add a registry gate and approval shield before write-capable servers.
- Reuse `credit_meter` to show context and external API costs rising with tool sprawl.
- End with a least-privilege checklist over the MCP bus.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What is MCP? | An open standard for connecting AI applications to external systems. citeturn38view3turn10view4 | citeturn38view3turn10view4 |
| What can an MCP server expose? | Tools, resources, and prompts. citeturn25search3turn25search9 | citeturn25search3turn25search9 |
| Why is MCP important? | It reduces custom integration work and enables broader interoperability. citeturn38view3 | citeturn38view3 |
| Which major clients support it? | Official MCP docs list support across Claude, ChatGPT-related ecosystems, VS Code, and others. citeturn38view3 | citeturn38view3 |
| What is the main security issue? | Over-broad capability exposure without strong authentication, authorization, or approvals. citeturn25search11turn7search10 | citeturn25search11turn7search10 |
| How do enterprises control MCP? | With registry settings, allowlists, and access policies. citeturn7search10turn7search21 | citeturn7search10turn7search21 |
| Does MCP affect cost? | Yes. Tool discovery, tool context, tool calls, and downstream APIs all add cost. citeturn28view0turn10view4 | citeturn28view0turn10view4 |
| What is the best beginner rule? | Start read-only, keep the tool list narrow, and require approval for writes. citeturn22search15turn7search10 | citeturn22search15turn7search10 |

#### References

Primary references for this module: official MCP intro and spec docs, GitHub MCP docs and org policy docs, Claude Code MCP docs, VS Code MCP docs. citeturn38view3turn25search3turn25search9turn10view4turn8search17turn37search14turn7search10turn7search21turn25search11

## AI alternatives and added instructional modules

### What AI alternatives we have

#### Executive summary

The four alternatives named by the user map to four different “home bases” for AI work. **Atlassian Rovo** is strongest when the center of gravity is organizational knowledge across Jira, Confluence, and connected tools; **Gemini App** is a consumer and prosumer assistant with subscription tiers and deep Google ecosystem ties; **GitHub Copilot** is strongest as a coding harness inside developer workflows; and **Claude Desktop/Code** is strongest as a high-capability coding and research assistant with strong connector, skill, hook, and MCP patterns. Rovo now ships in paid Atlassian cloud subscriptions, Gemini offers Free/AI Pro/AI Ultra plans, Copilot has Free through Enterprise and AI-credit billing, and Claude offers Free through Enterprise plus API pricing. citeturn26search6turn6search4turn26search21turn29view5turn29view4turn29view3turn6search5turn13view4turn14search1turn35view3turn35view1turn35view2

#### Quick comparison

| Alternative | Best fit | Main strengths | Main limitation |
|---|---|---|---|
| Atlassian Rovo | Enterprise knowledge and workflow automation in Jira/Confluence-heavy companies | Search, Chat, Agents, Studio, permissions-aware connected knowledge, Rovo Dev option | Not a general-purpose open coding harness in the same sense as Copilot, Claude Code, or OpenCode citeturn26search6turn26search3turn26search2turn26search21turn29view5turn29view4 |
| Gemini App | General AI assistant for Google ecosystem users | Deep Google integration, Deep Research, consumer-friendly plans, strong multimodal surface | Consumer pricing is regional and feature availability varies by plan and account type citeturn29view3turn6search9 |
| GitHub Copilot | Developer IDE and GitHub-native coding workflows | Agent mode, cloud agent, CLI, code review, skills, hooks, MCP, GitHub ecosystem fit | Credits and premium-model usage need active budget management citeturn38view0turn38view1turn14search0turn14search1 |
| Claude Desktop/Code | Developers who want strong coding autonomy plus flexible extensions | CLI, desktop, hooks, skills, plugins, MCP, subagents, broad coding workflow coverage | API and enterprise usage can scale quickly without tight context discipline citeturn9view1turn9view0turn9view2turn9view3turn28view0 |

#### Timed narration and visuals

| Time | Spoken narration | On-screen text and visual cues |
|---|---|---|
| 0:00–0:15 | “Not all AI assistants are trying to be the same thing. The easiest comparison is to ask: where does each one live, and what work does it want to own?” | Four-column comparison grid |
| 0:15–0:30 | “Atlassian Rovo lives in organizational knowledge and workflow. It connects Jira, Confluence, search, chat, and agents in one system.” | Jira/Confluence graph feeds into Rovo hub |
| 0:30–0:45 | “Gemini App is the broad personal assistant option in the Google ecosystem, with free and paid plans plus stronger access at higher tiers.” | Gemini plan cards fan out |
| 0:45–1:00 | “GitHub Copilot is the GitHub-native coding harness: IDE agent mode, cloud agent, CLI, code review, skills, hooks, and MCP.” | Copilot runtime stack builds up |
| 1:00–1:15 | “Claude Desktop and Claude Code combine desktop use, coding workflows, connectors, skills, hooks, plugins, and MCP into a very flexible assistant shell.” | Claude desktop to terminal transition |
| 1:15–1:30 | “So the choice is not ‘which AI is smartest.’ The better question is which system matches your center of gravity: knowledge, personal productivity, coding, or mixed-depth research and coding.” | One axis turns into four use-case quadrants |
| 1:30–1:45 | “Costs also differ. Rovo Dev uses credits per developer, Copilot uses AI credits per token usage, Gemini uses subscription tiers, and Claude blends subscriptions with API-style usage.” | Four cost meters under the four products |
| 1:45–2:00 | “Pick the product that matches your workflow home, then add guardrails, permissions, and observability around it. That is usually a better strategy than chasing a single winner.” | Final card: **Choose by workflow gravity** |

Reference basis for narration: Atlassian Rovo docs and pricing, Gemini plans, GitHub Copilot plans and credits, Claude plans and features. citeturn26search6turn26search3turn26search2turn26search21turn29view5turn29view4turn29view3turn6search9turn13view4turn14search1turn35view3turn35view1turn35view2

#### Shot and animation plan

- Reuse `comparison_grid` with one strong icon per platform.
- Show each alternative anchored to its natural workspace: Atlassian suite, Google suite, IDE/GitHub, desktop/terminal.
- Use one shared radar chart for **knowledge**, **coding**, **extensibility**, and **budgetability**.
- Reuse `credit_meter` but relabel for each pricing model.
- Fade in “home base” text for each tool rather than feature walls.
- End with a use-case selector the audience can mentally replay later.

#### Q&A

| Question | Answer | Source |
|---|---|---|
| What is Rovo best at? | Enterprise search, chat, agents, and connected knowledge in Atlassian-heavy environments. citeturn26search6turn26search21turn26search3 | citeturn26search6turn26search21turn26search3 |
| Is Rovo included in Atlassian subscriptions? | Yes, in paid Jira, Confluence, Service Collection/Jira Service Management, and Teamwork Collection cloud subscriptions. citeturn26search6 | citeturn26search6 |
| How is Rovo Dev priced? | $20 per developer per month with 2,000 credits, then $0.01 per extra credit. citeturn29view5turn29view4 | citeturn29view5turn29view4 |
| What is Gemini App best at? | Broad personal productivity and Google ecosystem workflows. citeturn29view3turn6search9 | citeturn29view3turn6search9 |
| What is Copilot best at? | Coding workflows integrated into IDEs, GitHub, code review, and agent loops. citeturn38view0turn38view1 | citeturn38view0turn38view1 |
| What is Claude Code best at? | Flexible coding and research workflows with strong extensions, skills, hooks, and MCP. citeturn9view1turn9view2turn9view3 | citeturn9view1turn9view2turn9view3 |
| Which option is most provider-open? | OpenCode and VS Code BYOK are the most provider-agnostic in this report; Copilot, Rovo, Gemini, and Claude are more opinionated product surfaces. citeturn27search21turn38view1 | citeturn27search21turn38view1 |
| What is the safest selection rule? | Choose the assistant whose natural workspace matches where your real context and approvals already live. | — |

#### References

Primary references for this module: Atlassian Rovo product and pricing docs, Google Gemini subscription docs, GitHub Copilot plans and billing docs, Claude pricing docs. citeturn26search6turn26search3turn26search21turn26search2turn29view5turn29view4turn29view3turn6search9turn13view4turn14search1turn35view3turn35view1turn35view2

### Recommended additional modules

The original list is strong, but current tooling makes four extra modules important enough to deserve their own videos.

| Missing module | Why it should be added | What the video should cover | Key references |
|---|---|---|---|
| **Observability** | Agents are difficult to improve without traces, spans, and usage analytics | Traces, run trees, tool-call logs, cost attribution, regression detection, trace grading | OpenAI traces and observability; Claude Code tracing and analytics citeturn23search3turn23search15turn8search3turn8search15 |
| **Instruction layers** | Behavior is often controlled by layered instructions more than by raw model choice | System prompt, repo rules, personal rules, organization rules, output styles, precedence | GitHub instruction precedence; Claude `CLAUDE.md`, output styles, settings precedence; OpenCode rule precedence citeturn23search1turn23search5turn23search4turn23search16turn23search0turn23search2 |
| **Tools and permissions** | Tool approval is the practical boundary between assistance and risk | Read vs write tools, terminal approval, allow/ask/deny, least privilege, approval caching | VS Code tool approvals; OpenCode permissions; Claude deny rules and managed settings; OpenAI approval guidance citeturn13view2turn27search16turn23search14turn9view0turn22search9 |
| **Data governance** | Enterprise deployment decisions quickly become privacy and policy decisions | Training use, retention, permissions sync, zero data retention, connectors, admin controls | GitHub Copilot policies and model governance; Claude no-training defaults for Team/Enterprise and opt-in development partner program; Gemini data governance and zero data retention options; Rovo permissions-aware access citeturn24search16turn24search4turn24search8turn35view1turn24search9turn24search6turn24search14turn24search22turn24search7turn24search15 |

These four additions should be treated as **dependency modules**. They are the shortest path to avoiding repetition in later videos because they centralize concepts that otherwise leak into nearly every other topic. citeturn23search3turn23search1turn13view2turn24search16

## References and limitations

This report prioritizes official documentation, pricing pages, research papers, and vendor support material from GitHub, Anthropic, Google, Atlassian, OpenAI, VS Code, NVIDIA, EIA, and the official MCP project. Product pricing and capability surfaces are current to **June 15, 2026** but remain subject to change, especially around subscriptions, model catalogs, and preview features. GitHub Copilot’s billing changed materially on **June 1, 2026**, so older “premium request” explanations are now legacy unless explicitly marked as such. citeturn14search6turn14search0turn14search1

Two limitations should be called out directly. First, **OpenCode’s official docs do not present an official seat-pricing page**, so the matrix treats OpenCode primarily as an open harness whose spend is model/provider-driven rather than seat-driven. Second, **Gemini subscription pages are locale-sensitive**; the captured page in this research exposed Australian-dollar pricing, so any final production artifact should present Gemini plan pricing as region-dependent unless your target market is explicitly fixed. citeturn27search21turn29view3

A final production note: exact repository paths for `ai-code-assistant-tools`, `ai-cat-by-concept`, and `efx_manim` were not provided in the request, so asset and file-placement recommendations are intentionally path-agnostic. The safest implementation pattern is to store reusable primitives under `efx_manim`, keep per-concept scene composition in the concept package, and reference shared overlays rather than duplicating geometry, labels, or timing logic. That is an implementation recommendation, not a source-derived fact.
