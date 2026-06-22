export const palette = {
  brandPrimary: "#9e1b32",
  brandNeutral: "#333e48",
  red: "#9e1b32",
  orange: "#e77204",
  yellow: "#f1c319",
  green: "#45842a",
  blue: "#007298",
  purple: "#652f6c",
  black: "#000000",
  white: "#ffffff",
  gray100: "#e7e7e7",
  gray200: "#cfcfcf",
  gray300: "#b5b5b5",
  gray400: "#9c9c9c",
  gray500: "#828282",
  gray600: "#696969",
  gray700: "#4f4f4f",
  gray800: "#363636",
  gray900: "#1c1c1c",
  blueHover: "#004d66",
  orangeHover: "#994a00",
  yellowHover: "#98700c",
  greenHover: "#294d19",
  purpleHover: "#431f47",
  redHover: "#6d1222",
  redHighlight: "#ffccd5",
  orangeHighlight: "#ffe5cc",
  yellowHighlight: "#fff4cc",
  greenHighlight: "#dbffcc",
  blueHighlight: "#cdf3ff",
  purpleHighlight: "#f9ccff",
  success: "#36b300",
  information: "#00ace6",
  caution: "#ffd332",
  warning: "#ff9633",
  special: "#9e00b3",
  page: "#f7f7f7"
};

export const beats = [
  { id: "hook", label: "Hook", start: 0, end: 12 },
  { id: "definition", label: "Core definition", start: 12, end: 36 },
  { id: "mechanism", label: "Mechanism", start: 36, end: 66 },
  { id: "implication", label: "Practical implication", start: 66, end: 100 },
  { id: "handoff", label: "Cost, caution, or handoff", start: 100, end: 120 }
];

export const researchNotes = [
  {
    topic: "Tokens and billing categories",
    note: "OpenAI describes tokens as text units that may be characters, partial words, spaces, or punctuation, and lists input, output, cached, and reasoning token usage categories.",
    url: "https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them",
    checked: "2026-06-20"
  },
  {
    topic: "Tokenizer verification",
    note: "OpenAI's tiktoken cookbook documents encoding-specific token splits; this video uses cl100k_base, where 'AI tools write code' splits into ['AI', ' tools', ' write', ' code'] with token IDs [15836, 7526, 3350, 2082].",
    url: "https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken",
    checked: "2026-06-20"
  },
  {
    topic: "Training scale and data",
    note: "Hoffmann et al. show that useful language model capability depends on model size, training tokens, and compute budget together; size alone is not the only driver.",
    url: "https://arxiv.org/abs/2203.15556",
    checked: "2026-06-21"
  },
  {
    topic: "Model choice tradeoffs",
    note: "OpenAI's model documentation presents smaller models as lower-latency and lower-cost options for many workloads, while larger frontier models target more complex work.",
    url: "https://developers.openai.com/api/docs/models",
    checked: "2026-06-21"
  },
  {
    topic: "Inference latency and cost",
    note: "NVIDIA's LLM inference benchmarking guidance frames latency, throughput, responsiveness, and acceptable accuracy as central to deployment cost.",
    url: "https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/",
    checked: "2026-06-21"
  },
  {
    topic: "Context window",
    note: "Google Cloud defines context window as the tokens a foundation model can process in a prompt; longer context lets a model use more information but increases work.",
    url: "https://docs.cloud.google.com/docs/generative-ai/glossary",
    checked: "2026-06-21"
  },
  {
    topic: "Gemma 4 model specs and memory",
    note: "Google's Gemma 4 documentation lists E4B, 31B, 26B A4B, 12B, and E2B variants; small models use 128K context, medium models use 256K, and the published inference memory table lists E4B at 17.9GB BF16 / 4.5GB Q4 and 31B at 69.9GB BF16 / 17.5GB Q4.",
    url: "https://ai.google.dev/gemma/docs/core",
    checked: "2026-06-21"
  },
  {
    topic: "Gemma 4 benchmark comparison",
    note: "Google's Gemma 4 model card reports instruction-tuned benchmark results including MMLU Pro, GPQA Diamond, LiveCodeBench v6, and AIME 2026 for Gemma 4 E4B and 31B.",
    url: "https://ai.google.dev/gemma/docs/core/model_card_4",
    checked: "2026-06-21"
  },
  {
    topic: "Gemma 4 model comparison chart",
    note: "Artificial Analysis lists Gemma 4 E4B and 31B reasoning variants with Intelligence Index, context window, token-use, price, speed, and model-size comparison sections; a cropped PNG from the Gemma 4 31B page is saved in the video assets.",
    url: "https://artificialanalysis.ai/models/gemma-4-31b",
    checked: "2026-06-21"
  },
  {
    topic: "Gemma 4 31B API price tracker",
    note: "PricePerToken currently lists Gemma 4 31B Instruct at $0.120 input, $0.060 cached, and $0.350 output per 1M tokens.",
    url: "https://pricepertoken.com/pricing-page/model/google-gemma-4-31b-it",
    checked: "2026-06-21"
  },
  {
    topic: "Gemma 4 E4B API price tracker",
    note: "PricePerToken currently lists Gemma 4 E4B IT at $0.200 input, $0.100 cached, and $0.200 output per 1M tokens.",
    url: "https://pricepertoken.com/pricing-page/model/google-gemma-4-e4b-it",
    checked: "2026-06-21"
  },
  {
    topic: "Google AI token pricing",
    note: "The Gemini API pricing page lists Gemini 3.5 Flash standard pricing at $1.50 input and $9.00 output per 1M tokens, and Gemini 3.1 Pro Preview standard pricing at $2.00 input and $12.00 output per 1M tokens for prompts up to 200k tokens.",
    url: "https://ai.google.dev/gemini-api/docs/pricing",
    checked: "2026-06-21"
  },
  {
    topic: "GPT-5.5 API pricing",
    note: "OpenAI's API pricing page lists GPT-5.5 at $5.00 input, $0.50 cached input, and $30.00 output per 1M tokens in standard processing.",
    url: "https://openai.com/api/pricing/",
    checked: "2026-06-21"
  },
  {
    topic: "Claude Opus 4.7 API pricing",
    note: "Anthropic's Claude API pricing page lists Claude Opus 4.7 at $5 input and $25 output per million tokens, with separate prompt-cache write and cache-hit prices.",
    url: "https://platform.claude.com/docs/en/about-claude/pricing",
    checked: "2026-06-21"
  },
  {
    topic: "DeepSWE v1.1 aggregate benchmark data",
    note: "DeepSWE v1.1 publishes aggregate leaderboard rows with pass@1, average cost, average input and output tokens, steps, context, and duration across 113 software engineering tasks; the implication scene uses the leaderboard-live artifact to draw a cost-versus-pass-rate chart.",
    url: "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json",
    checked: "2026-06-21"
  },
  {
    topic: "Llama 4 Scout and Maverick size",
    note: "Meta describes Llama 4 Scout as 109B total parameters with 17B active parameters and 16 experts, and Llama 4 Maverick as 400B total parameters with 17B active parameters and 128 experts.",
    url: "https://ai.meta.com/blog/llama-4-multimodal-intelligence/",
    checked: "2026-06-21"
  },
  {
    topic: "Llama 4 active parameter caveat",
    note: "Meta's Llama 4 model card states that Scout and Maverick have 109B and 400B total parameters respectively, while both use 17B active parameters per token.",
    url: "https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/",
    checked: "2026-06-21"
  },
  {
    topic: "Llama 4 Scout hosted cost",
    note: "Together AI lists Llama 4 Scout with 109B parameters, 1M context, $0.18 per 1M input tokens, and $0.59 per 1M output tokens.",
    url: "https://www.together.ai/models/llama-4-scout",
    checked: "2026-06-21"
  },
  {
    topic: "Llama 4 Maverick hosted cost",
    note: "Together AI lists Llama 4 Maverick with 401.6B parameters, 1048K context, $0.27 per 1M input tokens, and $0.85 per 1M output tokens.",
    url: "https://www.together.ai/models/llama-4-maverick",
    checked: "2026-06-21"
  },
  {
    topic: "H100 infrastructure reference",
    note: "NVIDIA lists H100 SXM at 80GB GPU memory and 3.35TB/s memory bandwidth; Google Cloud lists A3 High and A3 Edge machine types with NVIDIA H100 80GB GPUs for training and serving workloads.",
    url: "https://www.nvidia.com/en-us/data-center/h100/",
    checked: "2026-06-21"
  },
  {
    topic: "Evaluation framing",
    note: "OpenAI's current Evals guide frames evaluation as datasets plus graders, including string, text-similarity, Python, score-model, label-model, and multi graders.",
    url: "https://developers.openai.com/api/docs/guides/evals",
    checked: "2026-06-21"
  },
  {
    topic: "pass@k estimator",
    note: "The Codex HumanEval paper estimates pass@k with 1 - C(n-c,k) / C(n,k) for n sampled completions and c correct completions, which avoids a naive independent-trial shortcut.",
    url: "https://arxiv.org/pdf/2107.03374",
    checked: "2026-06-21"
  },
  {
    topic: "Agent workflow evaluation",
    note: "Anthropic describes agent evals as extending ordinary input-plus-grader checks into multi-turn environments where traces, tool use, and policy adherence need to be graded.",
    url: "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents",
    checked: "2026-06-21"
  },
  {
    topic: "Agent architecture",
    note: "Anthropic distinguishes predefined workflows from agents that dynamically direct their own process and tool use.",
    url: "https://www.anthropic.com/engineering/building-effective-agents",
    checked: "2026-06-20"
  },
  {
    topic: "Agent evals",
    note: "Anthropic describes evals as inputs plus grading logic, with agent evals expanding from single-turn checks to multi-turn tool-loop environments.",
    url: "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents",
    checked: "2026-06-20"
  },
  {
    topic: "Guardrails",
    note: "Anthropic separates direct jailbreak/prompt injection from indirect prompt injection through third-party content such as web pages, email, documents, or tool results.",
    url: "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks",
    checked: "2026-06-20"
  },
  {
    topic: "Hooks",
    note: "Claude Code documents hooks as commands, HTTP endpoints, or LLM prompts that run at lifecycle events such as session, prompt, and tool-call events.",
    url: "https://code.claude.com/docs/en/hooks",
    checked: "2026-06-20"
  },
  {
    topic: "Plugins",
    note: "Claude Code plugins can package skills, agents, hooks, MCP servers, LSP servers, and monitors in a self-contained extension directory.",
    url: "https://code.claude.com/docs/en/plugins-reference",
    checked: "2026-06-20"
  },
  {
    topic: "Skills",
    note: "Claude Code describes skills as task-specific instructions and resources that load only when used, reducing repeated prompt pasting and context load.",
    url: "https://code.claude.com/docs/en/skills",
    checked: "2026-06-20"
  },
  {
    topic: "MCP",
    note: "The MCP specification defines an open protocol for integrating LLM applications with external data sources and tools.",
    url: "https://modelcontextprotocol.io/specification/2025-03-26",
    checked: "2026-06-20"
  },
  {
    topic: "MCP authorization",
    note: "The MCP authorization specification applies to HTTP transports; stdio transports are expected to retrieve credentials from their environment instead.",
    url: "https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization",
    checked: "2026-06-20"
  },
  {
    topic: "Copilot billing",
    note: "GitHub Copilot usage-based billing measures input, output, and cached tokens and converts model-priced usage into GitHub AI Credits.",
    url: "https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises",
    checked: "2026-06-20"
  },
  {
    topic: "Copilot model pricing",
    note: "GitHub states Copilot interaction cost depends on the model and token consumption, with included AI Credit allowances varying by plan.",
    url: "https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing",
    checked: "2026-06-20"
  },
  {
    topic: "Rovo",
    note: "Atlassian currently describes Rovo as included in paid Jira, Confluence, Service Collection, and Teamwork Collection cloud subscriptions, with per-user monthly credit allowances.",
    url: "https://support.atlassian.com/rovo/docs/rovo-usage-limits/",
    checked: "2026-06-20"
  },
  {
    topic: "Rovo Dev CLI",
    note: "Atlassian positions Rovo Dev CLI around coding, review, refactoring, debugging, documentation, Jira, Confluence, tools, subagents, and MCP.",
    url: "https://support.atlassian.com/rovo/docs/use-rovo-dev-cli/",
    checked: "2026-06-20"
  },
  {
    topic: "Google AI plans",
    note: "Google AI plans are positioned around Gemini app access, Google productivity integrations, NotebookLM, Flow, AI Studio, and plan-specific limits.",
    url: "https://one.google.com/about/google-ai-plans/",
    checked: "2026-06-20"
  },
  {
    topic: "Claude Agent SDK",
    note: "The Claude Agent SDK exposes Claude Code's tools, loop, and context management as Python and TypeScript libraries for production agents.",
    url: "https://code.claude.com/docs/en/agent-sdk/overview",
    checked: "2026-06-20"
  },
  {
    topic: "OpenAI Agents SDK",
    note: "OpenAI describes its updated Agents SDK as a harness for long-horizon agents that can inspect files, run commands, edit code, and work in controlled sandboxes.",
    url: "https://openai.com/index/the-next-evolution-of-the-agents-sdk/",
    checked: "2026-06-20"
  }
];

export const concepts = [
  {
    id: "01-what-is-an-llm",
    title: "What Is an LLM?",
    shortTitle: "LLM",
    kind: "llm",
    visualOnly: true,
    runtimeSeconds: 120,
    coreIdea: "Tokens -> context -> rank -> loop.",
    outcome: "Split, stack, score, append.",
    sourceIds: ["Tokens", "Context", "Next token"],
    scenes: [
      {
        beat: "hook",
        headline: "Text goes in",
        bullets: ["Split", "Rank", "Loop"],
        callout: "Not lookup"
      },
      {
        beat: "definition",
        headline: "Tokens stack",
        bullets: ["Words", "Pieces", "Marks"],
        callout: "Context shifts odds"
      },
      {
        beat: "mechanism",
        headline: "Pick then append",
        bullets: ["Score", "Choose", "Repeat"],
        callout: "One token at a time"
      },
      {
        beat: "implication",
        headline: "Context matters",
        bullets: ["Prompt", "History", "System"],
        callout: "Better context changes ranking"
      },
      {
        beat: "handoff",
        headline: "Work is metered",
        bullets: ["Input", "Output", "Retry"],
        callout: "Tokens drive load"
      }
    ],
    metrics: [
      { label: "Context", value: 0.78, color: palette.blue },
      { label: "Loop", value: 0.58, color: palette.green },
      { label: "Compute", value: 0.72, color: palette.orange }
    ],
    references: [
      "https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them",
      "https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken",
      "https://docs.cloud.google.com/docs/generative-ai/glossary",
      "https://arxiv.org/abs/2203.15556",
      "https://developers.openai.com/api/docs/models",
      "https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/",
      "https://ai.google.dev/gemma/docs/core",
      "https://ai.google.dev/gemma/docs/core/model_card_4",
      "https://artificialanalysis.ai/models/gemma-4-31b",
      "https://pricepertoken.com/pricing-page/model/google-gemma-4-31b-it",
      "https://pricepertoken.com/pricing-page/model/google-gemma-4-e4b-it",
      "https://ai.google.dev/gemini-api/docs/pricing",
      "https://openai.com/api/pricing/",
      "https://platform.claude.com/docs/en/about-claude/pricing",
      "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json",
      "https://ai.meta.com/blog/llama-4-multimodal-intelligence/",
      "https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/",
      "https://www.together.ai/models/llama-4-scout",
      "https://www.together.ai/models/llama-4-maverick",
      "https://www.nvidia.com/en-us/data-center/h100/",
      "https://docs.cloud.google.com/compute/docs/gpus",
      "https://papers.nips.cc/paper_files/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html"
    ]
  },
  {
    id: "02-llm-billing",
    title: "LLM Billing",
    shortTitle: "Billing",
    kind: "billing",
    runtimeSeconds: 120,
    coreIdea: "LLM cost follows model work, even when products package it as subscriptions, credits, or token prices.",
    outcome: "Input tokens, output tokens, model tiers, retries, caching, tool loops, and hosted versus local cost.",
    sourceIds: ["AI credits", "Token rates", "Cache reads"],
    scenes: [
      {
        beat: "hook",
        headline: "The price tag is packaging",
        bullets: ["Subscription", "Credits", "API token rates", "Usage budgets"],
        callout: "Different labels can meter the same underlying work"
      },
      {
        beat: "definition",
        headline: "Main cost drivers",
        bullets: ["Input tokens and output tokens", "Model choice and context length", "Retries, tools, and cache behavior"],
        callout: "Output length matters because generation is work"
      },
      {
        beat: "mechanism",
        headline: "Agent sessions multiply calls",
        bullets: ["Model call", "Tool result enters context", "Another model call", "Final answer"],
        callout: "Tool loops are often several billable model turns"
      },
      {
        beat: "implication",
        headline: "Control cost per successful task",
        bullets: ["Trim irrelevant context", "Use the lowest adequate model", "Cache repeated prefixes", "Cap retries"],
        callout: "Measure completed tasks, not isolated prompts"
      },
      {
        beat: "handoff",
        headline: "Local is not automatically free",
        bullets: ["Hardware", "Energy", "Operations", "Developer time"],
        callout: "Probability and evaluation also affect spend"
      }
    ],
    metrics: [
      { label: "Input", value: 0.5, color: palette.blue },
      { label: "Output", value: 0.86, color: palette.red },
      { label: "Cached", value: 0.3, color: palette.green }
    ],
    references: [
      "https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing",
      "https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises",
      "https://code.claude.com/docs/en/costs",
      "https://www.atlassian.com/licensing/rovo"
    ]
  },
  {
    id: "03-probabilities-and-evaluation",
    title: "LLM Probabilities and Evaluation",
    shortTitle: "Evaluation",
    kind: "evaluation",
    runtimeSeconds: 120,
    coreIdea: "LLM outputs are probabilistic, so quality has to be measured against the task.",
    outcome: "Distributions, context sensitivity, tests, rubrics, graders, pass rates, and attempt cost.",
    sourceIds: ["Distributions", "Graders", "pass@N"],
    scenes: [
      {
        beat: "hook",
        headline: "Likely is not the same as guaranteed",
        bullets: ["The model ranks possible continuations", "Sampling can produce different valid attempts", "Correctness needs a checker"],
        callout: "Think probability distribution, not answer key"
      },
      {
        beat: "definition",
        headline: "Context shifts the odds",
        bullets: ["Vague prompts spread probability", "Constraints narrow the target", "Examples and data can improve the chance"],
        callout: "Better context improves odds but does not guarantee truth"
      },
      {
        beat: "mechanism",
        headline: "Evaluation wraps the output",
        bullets: ["Programmatic tests for deterministic tasks", "Rubrics for open-ended work", "Model graders and human review when needed"],
        callout: "Agent traces can be graded across tool decisions"
      },
      {
        beat: "implication",
        headline: "pass@N trades attempts for cost",
        bullets: ["More samples can improve success probability", "Every attempt adds latency and spend", "Use the estimator, not a naive shortcut"],
        callout: "Six good patches in twenty samples still need careful pass@5 math"
      },
      {
        beat: "handoff",
        headline: "Agents need evals because actions compound",
        bullets: ["Uncertain calls happen inside loops", "Tool actions change state", "Regression tests catch workflow drift"],
        callout: "The next concept is the agent loop"
      }
    ],
    metrics: [
      { label: "Prompt clarity", value: 0.64, color: palette.blue },
      { label: "Pass rate", value: 0.42, color: palette.green },
      { label: "Attempt cost", value: 0.74, color: palette.orange }
    ],
    references: [
      "https://arxiv.org/pdf/2107.03374",
      "https://developers.openai.com/api/docs/guides/evals",
      "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents"
    ]
  },
  {
    id: "04-what-is-an-agent",
    title: "What Is an Agent?",
    shortTitle: "Agent",
    kind: "agent",
    runtimeSeconds: 120,
    coreIdea: "An agent is a goal-directed system that uses model calls, tools, observations, and stopping rules.",
    outcome: "A single prompt is not the same as an action loop with autonomy, tools, and risk.",
    sourceIds: ["Goal", "Tools", "Observation loop"],
    scenes: [
      {
        beat: "hook",
        headline: "A prompt answers; an agent pursues",
        bullets: ["The user gives a goal", "The system chooses steps", "Tools and observations update the path"],
        callout: "Agent = goal-directed loop"
      },
      {
        beat: "definition",
        headline: "Required pieces",
        bullets: ["Goal and context", "Tools and environment", "Observations and stop condition"],
        callout: "The harness decides what the model can do"
      },
      {
        beat: "mechanism",
        headline: "Decide, act, observe, repeat",
        bullets: ["Plan the next move", "Call a tool or ask a model", "Read the result", "Continue or stop"],
        callout: "Unknown paths are where agents become useful"
      },
      {
        beat: "implication",
        headline: "Use agents when the path branches",
        bullets: ["Research", "Debugging", "Migration", "Triage", "Multi-step code tasks"],
        callout: "Fixed checklists do not need much autonomy"
      },
      {
        beat: "handoff",
        headline: "Autonomy increases requirements",
        bullets: ["Permissions", "Evaluation", "Observability", "Guardrails"],
        callout: "The next concept draws boundaries around the loop"
      }
    ],
    metrics: [
      { label: "Autonomy", value: 0.76, color: palette.purple },
      { label: "Tool surface", value: 0.68, color: palette.blue },
      { label: "Risk controls", value: 0.58, color: palette.red }
    ],
    references: [
      "https://openai.com/index/new-tools-for-building-agents/",
      "https://openai.com/index/the-next-evolution-of-the-agents-sdk/",
      "https://www.anthropic.com/engineering/building-effective-agents",
      "https://code.claude.com/docs/en/agent-sdk/overview"
    ]
  },
  {
    id: "05-what-is-a-guardrail",
    title: "What Is a Guardrail?",
    shortTitle: "Guardrail",
    kind: "guardrail",
    runtimeSeconds: 120,
    coreIdea: "A guardrail checks AI inputs, outputs, or actions against policy before harm occurs.",
    outcome: "Allow, block, redact, transform, ask, monitor, ingress checks, egress checks, and tradeoffs.",
    sourceIds: ["Allow", "Block", "Redact"],
    scenes: [
      {
        beat: "hook",
        headline: "A guardrail is an active control",
        bullets: ["Allow safe work", "Block unsafe paths", "Redact secrets", "Ask for permission"],
        callout: "Control behavior before damage happens"
      },
      {
        beat: "definition",
        headline: "Checks can run at several points",
        bullets: ["Before the model", "Before tools", "After tools", "Before final output"],
        callout: "Ingress and egress are easier to reason about separately"
      },
      {
        beat: "mechanism",
        headline: "Risk maps to policy outcome",
        bullets: ["Prompt injection blocked", "API key redacted", "Dangerous command requires permission", "Unsafe final answer refused"],
        callout: "Indirect prompt injection can arrive through tool results"
      },
      {
        beat: "implication",
        headline: "Precise beats broad",
        bullets: ["Keep useful work moving", "Stop only the dangerous part", "Log decisions for review"],
        callout: "Over-blocking can become its own product failure"
      },
      {
        beat: "handoff",
        headline: "Controls add latency and design work",
        bullets: ["Policy clarity", "Classifier checks", "Human review", "Fail-open or fail-closed"],
        callout: "The harness is where guardrails are wired"
      }
    ],
    metrics: [
      { label: "Detection", value: 0.72, color: palette.blue },
      { label: "Precision", value: 0.61, color: palette.green },
      { label: "Friction", value: 0.38, color: palette.orange }
    ],
    references: [
      "https://docs.cloud.google.com/model-armor/overview",
      "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks"
    ]
  },
  {
    id: "06-what-is-a-harness",
    title: "What Is a Harness?",
    shortTitle: "Harness",
    kind: "harness",
    runtimeSeconds: 120,
    coreIdea: "A harness is the runtime wrapper that turns a model into a usable product or agent.",
    outcome: "Prompts, context rules, tools, permissions, MCP connections, environment, loop, and orchestration.",
    sourceIds: ["Runtime wrapper", "Tools", "Policy"],
    scenes: [
      {
        beat: "hook",
        headline: "The product is not just the model",
        bullets: ["Model", "Instructions", "Tools", "Permissions", "Runtime defaults"],
        callout: "Same model, different harness, different behavior"
      },
      {
        beat: "definition",
        headline: "The harness controls the operating context",
        bullets: ["System prompt", "Context rules", "Tool availability", "MCP connections", "Stop conditions"],
        callout: "It is the wrapper around the model call"
      },
      {
        beat: "mechanism",
        headline: "The harness routes decisions",
        bullets: ["User request becomes context", "Model proposes an action", "Harness executes or blocks", "Observation returns"],
        callout: "Tool access is mediated, not magic"
      },
      {
        beat: "implication",
        headline: "Different products expose different harnesses",
        bullets: ["Coding assistant", "Enterprise search assistant", "Desktop automation assistant"],
        callout: "Context sources and permission defaults shape results"
      },
      {
        beat: "handoff",
        headline: "Quality affects cost, safety, and reliability",
        bullets: ["Extra loop iterations cost money", "Weak policy increases risk", "Poor context causes drift"],
        callout: "Hooks are named interception points in the lifecycle"
      }
    ],
    metrics: [
      { label: "Context", value: 0.7, color: palette.blue },
      { label: "Tools", value: 0.82, color: palette.green },
      { label: "Policy", value: 0.66, color: palette.red }
    ],
    references: [
      "https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/agent-loop",
      "https://www.anthropic.com/engineering/managed-agents",
      "https://openai.com/index/the-next-evolution-of-the-agents-sdk/"
    ]
  },
  {
    id: "07-what-is-a-harness-hook",
    title: "What Is a Harness Hook?",
    shortTitle: "Hook",
    kind: "hook",
    runtimeSeconds: 120,
    coreIdea: "A hook is an event-driven interception point inside a harness lifecycle.",
    outcome: "Lifecycle events, pre-tool checks, permission checks, post-tool checks, fail-open, fail-closed, and audit value.",
    sourceIds: ["Event", "Check", "Decision"],
    scenes: [
      {
        beat: "hook",
        headline: "A hook pauses the lifecycle",
        bullets: ["An event fires", "A check runs", "A decision is returned"],
        callout: "Event plus check plus decision"
      },
      {
        beat: "definition",
        headline: "Common hook events",
        bullets: ["Session start", "Prompt submit", "Pre-tool use", "Permission request", "Tool result", "Session end"],
        callout: "Event names vary by harness"
      },
      {
        beat: "mechanism",
        headline: "Payload in, decision out",
        bullets: ["Inspect JSON context", "Approve, deny, modify, log, notify, or ask", "Record latency and effect"],
        callout: "Hooks can run synchronously and delay the workflow"
      },
      {
        beat: "implication",
        headline: "Useful hooks enforce repeatable policy",
        bullets: ["Secret scanning", "Permission enforcement", "Audit trails", "Context shaping"],
        callout: "Hooks are stronger than advisory instructions"
      },
      {
        beat: "handoff",
        headline: "Choose failure behavior deliberately",
        bullets: ["Fail-open can let risk pass", "Fail-closed can block useful work", "Packaging matters for reuse"],
        callout: "Plugins distribute reusable hook behavior"
      }
    ],
    metrics: [
      { label: "Coverage", value: 0.77, color: palette.blue },
      { label: "Latency", value: 0.34, color: palette.orange },
      { label: "Audit value", value: 0.83, color: palette.purple }
    ],
    references: [
      "https://docs.github.com/en/copilot/concepts/agents/hooks",
      "https://docs.github.com/en/copilot/reference/hooks-reference",
      "https://code.claude.com/docs/en/hooks",
      "https://opencode.ai/docs/plugins/"
    ]
  },
  {
    id: "08-what-is-a-harness-plugin",
    title: "What Is a Harness Plugin?",
    shortTitle: "Plugin",
    kind: "plugin",
    runtimeSeconds: 120,
    coreIdea: "A plugin packages reusable harness extensions so teams can install, share, govern, and update them.",
    outcome: "Plugins can package agents, skills, hooks, MCP configuration, integrations, tools, policy defaults, and metadata.",
    sourceIds: ["Package", "Install", "Govern"],
    scenes: [
      {
        beat: "hook",
        headline: "A plugin turns setup into an installable unit",
        bullets: ["One-off configuration becomes reusable", "Capabilities travel together", "Teams can standardize behavior"],
        callout: "Packaged harness customization"
      },
      {
        beat: "definition",
        headline: "Plugin contents depend on the harness",
        bullets: ["Skills", "Agents", "Hooks", "MCP servers", "Integrations", "Environment setup"],
        callout: "Do not assume every product means the same thing by plugin"
      },
      {
        beat: "mechanism",
        headline: "Discovery exposes capabilities",
        bullets: ["Install package", "Read manifest", "Expose allowed capabilities", "Load only what is needed"],
        callout: "Permission scope is separate from discoverability"
      },
      {
        beat: "implication",
        headline: "Plugins help teams repeat good practice",
        bullets: ["Review policy", "Secret scanning hook", "MCP server config", "Domain workflows"],
        callout: "Shared setup reduces drift across repositories"
      },
      {
        beat: "handoff",
        headline: "Govern the package supply chain",
        bullets: ["Source trust", "Versioning", "Review", "Permissions", "Rollback"],
        callout: "One useful plugin component is a skill"
      }
    ],
    metrics: [
      { label: "Reuse", value: 0.86, color: palette.green },
      { label: "Capability scope", value: 0.74, color: palette.blue },
      { label: "Governance", value: 0.7, color: palette.red }
    ],
    references: [
      "https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins",
      "https://code.claude.com/docs/en/plugins-reference",
      "https://code.claude.com/docs/en/plugin-marketplaces",
      "https://opencode.ai/docs/plugins/"
    ]
  },
  {
    id: "09-what-is-a-skill",
    title: "What Is a Skill?",
    shortTitle: "Skill",
    kind: "skill",
    runtimeSeconds: 120,
    coreIdea: "A skill is an on-demand capability bundle with task-specific instructions, resources, and procedures.",
    outcome: "Trigger descriptions, progressive disclosure, reusable procedures, supporting files, scripts, templates, and context efficiency.",
    sourceIds: ["Trigger", "Instructions", "Resources"],
    scenes: [
      {
        beat: "hook",
        headline: "A skill is a reusable procedure",
        bullets: ["Stop pasting the same checklist", "Name the workflow", "Load it when the task needs it"],
        callout: "A skill is more than a long prompt"
      },
      {
        beat: "definition",
        headline: "Skill anatomy",
        bullets: ["Description that triggers use", "Workflow instructions", "References", "Scripts", "Templates"],
        callout: "Keep the core concise and move detail into resources"
      },
      {
        beat: "mechanism",
        headline: "Progressive disclosure protects context",
        bullets: ["Match task to description", "Load detailed instructions", "Open supporting files only when needed"],
        callout: "Unused reference material should cost almost nothing"
      },
      {
        beat: "implication",
        headline: "Skills fit repeated specialized work",
        bullets: ["Document generation", "Review process", "Migration recipe", "Data cleanup", "Artifact generation"],
        callout: "If you paste it three times, consider a skill"
      },
      {
        beat: "handoff",
        headline: "Good skills reduce repetition; bad skills add confusion",
        bullets: ["Vague triggers misfire", "Bloated instructions waste context", "Validation keeps behavior real"],
        callout: "External systems still need connectors"
      }
    ],
    metrics: [
      { label: "Trigger clarity", value: 0.78, color: palette.blue },
      { label: "Context efficiency", value: 0.84, color: palette.green },
      { label: "Validation", value: 0.7, color: palette.purple }
    ],
    references: [
      "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills",
      "https://code.claude.com/docs/en/skills",
      "https://opencode.ai/docs/skills/"
    ]
  },
  {
    id: "10-what-is-an-mcp",
    title: "What Is an MCP?",
    shortTitle: "MCP",
    kind: "mcp",
    runtimeSeconds: 120,
    coreIdea: "MCP is a standard connector layer for AI applications to access external tools and data.",
    outcome: "Hosts, clients, servers, tools, resources, prompts, transports, authorization, reuse, and security responsibility.",
    sourceIds: ["Host", "Client", "Server"],
    scenes: [
      {
        beat: "hook",
        headline: "MCP standardizes connections",
        bullets: ["Files", "Databases", "SaaS apps", "Ticket systems", "Internal APIs"],
        callout: "A common protocol replaces bespoke glue"
      },
      {
        beat: "definition",
        headline: "Roles matter",
        bullets: ["Host is the AI application", "Client lives inside the host", "Server exposes tools, resources, or prompts"],
        callout: "The connector is not the model"
      },
      {
        beat: "mechanism",
        headline: "Discovery and exchange",
        bullets: ["Server advertises capabilities", "Client requests a tool or resource", "Result returns into the harness context"],
        callout: "Reusable connector patterns reduce integration friction"
      },
      {
        beat: "implication",
        headline: "Govern every server",
        bullets: ["Auth mode", "Allowed tools", "User consent point", "Audit log", "Fallback plan"],
        callout: "Remote HTTP and local stdio have different security shapes"
      },
      {
        beat: "handoff",
        headline: "MCP helps access, not judgment",
        bullets: ["External APIs still add latency", "Credentials still matter", "Tool outputs still need guardrails"],
        callout: "Product choice depends on workflow fit"
      }
    ],
    metrics: [
      { label: "Integration reuse", value: 0.84, color: palette.green },
      { label: "Latency", value: 0.42, color: palette.orange },
      { label: "Security work", value: 0.76, color: palette.red }
    ],
    references: [
      "https://modelcontextprotocol.io/docs/getting-started/intro",
      "https://modelcontextprotocol.io/specification/2025-03-26",
      "https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization",
      "https://docs.github.com/en/copilot/concepts/context/mcp"
    ]
  },
  {
    id: "11-ai-alternatives",
    title: "AI Alternatives",
    shortTitle: "Alternatives",
    kind: "alternatives",
    runtimeSeconds: 120,
    coreIdea: "The best AI product depends on workflow context, integration surface, control model, and cost structure.",
    outcome: "Compare alternatives through task fit, context source, actions, governance, evaluation, and billing.",
    sourceIds: ["Workflow fit", "Context", "Cost"],
    scenes: [
      {
        beat: "hook",
        headline: "Replace universal ranking with workflow fit",
        bullets: ["Where is the context?", "What actions can it take?", "How is usage billed?"],
        callout: "Best for what job, with which constraints?"
      },
      {
        beat: "definition",
        headline: "Each product has a center of gravity",
        bullets: ["Enterprise knowledge", "Productivity suite", "GitHub-native coding", "Customizable agent harness"],
        callout: "Compare centers, not brand names alone"
      },
      {
        beat: "mechanism",
        headline: "Use the same checklist",
        bullets: ["Context source", "Available actions", "Permission model", "Evaluation path", "Billing model"],
        callout: "Fair comparisons hold the questions constant"
      },
      {
        beat: "implication",
        headline: "Pilot on real tasks",
        bullets: ["Time saved", "Correction rate", "Permission friction", "Integration misses", "Cost per accepted result"],
        callout: "A demo is not the same as a workflow pilot"
      },
      {
        beat: "handoff",
        headline: "Live facts change quickly",
        bullets: ["Prices", "Model access", "Plan limits", "Connector support"],
        callout: "The framework is stable; purchasing facts are not"
      }
    ],
    metrics: [
      { label: "Workflow fit", value: 0.82, color: palette.blue },
      { label: "Governance", value: 0.67, color: palette.red },
      { label: "Cost clarity", value: 0.58, color: palette.green }
    ],
    references: [
      "https://support.atlassian.com/rovo/docs/what-is-rovo/",
      "https://support.atlassian.com/rovo/docs/use-rovo-dev-cli/",
      "https://one.google.com/about/google-ai-plans/",
      "https://docs.github.com/en/copilot/get-started/features",
      "https://code.claude.com/docs/en/overview"
    ]
  }
];
