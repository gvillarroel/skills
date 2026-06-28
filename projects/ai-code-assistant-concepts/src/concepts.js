export const project = {
  id: "ai-code-assistant-concepts",
  title: "AI Code Assistant Concepts",
  width: 1920,
  height: 1080,
  runtimeSeconds: 42,
  sceneCount: 5,
  checkedDate: "2026-06-27",
  visualThesis: "One work packet travels through models, runtimes, controls, connectors, and governance.",
  recurringSymbols: [
    { id: "work-packet", meaning: "a user task, prompt, or data unit moving through the system" },
    { id: "blue-context-box", meaning: "the visible context available to the model or agent" },
    { id: "green-check", meaning: "verified output or allowed action" },
    { id: "red-shield", meaning: "policy, permission, guardrail, or governance boundary" },
    { id: "teal-bus", meaning: "standardized connection surface such as MCP" },
    { id: "amber-meter", meaning: "cost, latency, or operational load" }
  ]
};

export const palette = {
  ink: "#17212b",
  muted: "#526271",
  paper: "#f6f8f7",
  line: "#c9d2d6",
  blue: "#1b72a6",
  teal: "#168980",
  green: "#3c8a48",
  amber: "#d58922",
  red: "#b84545",
  purple: "#7650a6",
  slate: "#35475c",
  white: "#ffffff"
};

export const sources = [
  {
    label: "GitHub Copilot billing and AI credits",
    url: "https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises",
    note: "Usage-based billing converts model-priced token usage into AI credits; plan details change over time."
  },
  {
    label: "GitHub Copilot agent skills",
    url: "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills",
    note: "Skills are reusable instruction and resource folders for agent workflows."
  },
  {
    label: "Claude Code skills",
    url: "https://code.claude.com/docs/en/skills",
    note: "Skills load task-specific instructions and resources on demand."
  },
  {
    label: "Claude Code hooks",
    url: "https://code.claude.com/docs/en/hooks",
    note: "Hooks run commands, HTTP endpoints, or LLM prompts at lifecycle events."
  },
  {
    label: "Claude Code plugins",
    url: "https://code.claude.com/docs/en/plugins-reference",
    note: "Plugins can package skills, agents, hooks, MCP servers, and related runtime pieces."
  },
  {
    label: "Model Context Protocol introduction",
    url: "https://modelcontextprotocol.io/docs/getting-started/intro",
    note: "MCP standardizes connections between AI applications and external tools or data."
  },
  {
    label: "Google Cloud Model Armor",
    url: "https://cloud.google.com/security/products/model-armor",
    note: "Model Armor screens prompts and responses for AI security risks."
  },
  {
    label: "Atlassian Rovo usage limits",
    url: "https://support.atlassian.com/rovo/docs/rovo-usage-limits/",
    note: "Rovo exposes a product-specific usage and credit model."
  },
  {
    label: "Google AI plans",
    url: "https://one.google.com/about/google-ai-plans/",
    note: "Gemini product access and plan limits vary by plan and region."
  },
  {
    label: "OpenAI Evals guide",
    url: "https://developers.openai.com/api/docs/guides/evals",
    note: "Evaluation is built from datasets, graders, traces, and quality measurements."
  },
  {
    label: "Anthropic effective agents",
    url: "https://www.anthropic.com/engineering/building-effective-agents",
    note: "Agentic systems differ from fixed workflows by dynamically directing tool use."
  }
];

const sharedScenes = {
  close: {
    headline: "Use the concept to make better system choices",
    micro: "Compare behavior, risk, and cost at the boundary it controls.",
    terms: ["quality", "risk", "cost"]
  }
};

export const concepts = [
  {
    id: "01-what-is-an-llm",
    order: 1,
    title: "What Is an LLM?",
    shortTitle: "LLM",
    kind: "llm",
    accent: palette.blue,
    thesis: "A large language model predicts tokens from context; it is not a database lookup.",
    scenes: [
      { headline: "Text becomes tokens", micro: "Words, spaces, punctuation, and word pieces enter the context box.", terms: ["tokens", "context", "input"] },
      { headline: "The model ranks next tokens", micro: "Many candidates get scores before one continuation is selected.", terms: ["rank", "score", "next"] },
      { headline: "Output loops back", micro: "Each generated token becomes part of the next step's context.", terms: ["append", "repeat", "sequence"] },
      { headline: "Size is not the same as truth", micro: "Parameters, context window, training data, and verification are different concerns.", terms: ["parameters", "window", "verify"] },
      { headline: "Better context changes odds", micro: "Clearer task context reshapes the token distribution.", terms: ["prompt", "examples", "constraints"] }
    ]
  },
  {
    id: "02-llm-billing",
    order: 2,
    title: "LLM Billing",
    shortTitle: "Billing",
    kind: "billing",
    accent: palette.amber,
    thesis: "Cost follows model work, even when a product wraps usage as seats, credits, or subscriptions.",
    scenes: [
      { headline: "The same work can wear different price labels", micro: "Subscription, credit, API, and local costs are packaging around real compute.", terms: ["seat", "credit", "API"] },
      { headline: "Input and output both matter", micro: "Long prompts, long answers, and repeated tool loops add up.", terms: ["input", "output", "retry"] },
      { headline: "Model choice changes the meter", micro: "A stronger model can cost more but may reduce retries on hard work.", terms: ["model", "latency", "success"] },
      { headline: "Cache and trim before scaling", micro: "Repeated context should be cached or summarized when the harness supports it.", terms: ["cache", "trim", "reuse"] },
      { headline: "Track cost per accepted result", micro: "The useful metric is completed work, not one isolated call.", terms: ["accepted", "task", "budget"] }
    ]
  },
  {
    id: "03-probabilities-and-evaluation",
    order: 3,
    title: "Probabilities and Evaluation",
    shortTitle: "Evaluation",
    kind: "evaluation",
    accent: palette.green,
    thesis: "LLM output is sampled from probabilities; evaluation decides whether the sample is good enough.",
    scenes: [
      { headline: "Likely is not guaranteed", micro: "The model scores candidate continuations instead of fetching one fixed answer.", terms: ["probability", "sample", "variance"] },
      { headline: "Context reshapes the distribution", micro: "Examples and constraints can move probability toward useful outputs.", terms: ["context", "examples", "odds"] },
      { headline: "Tests beat vibes when possible", micro: "Schemas, unit tests, parsers, and exact checks make quality measurable.", terms: ["tests", "schema", "parser"] },
      { headline: "pass@N trades attempts for cost", micro: "More samples can improve success, but every attempt consumes time and budget.", terms: ["pass@N", "attempts", "cost"] },
      { headline: "Agent evals need traces", micro: "For multi-step work, grade the path as well as the final answer.", terms: ["trace", "grader", "regression"] }
    ]
  },
  {
    id: "04-what-is-an-agent",
    order: 4,
    title: "What Is an Agent?",
    shortTitle: "Agent",
    kind: "agent",
    accent: palette.purple,
    thesis: "An agent is a goal-directed loop that observes, acts, reads results, and continues until it should stop.",
    scenes: [
      { headline: "A prompt answers; an agent pursues", micro: "The system can choose steps after seeing new information.", terms: ["goal", "state", "loop"] },
      { headline: "Context defines what it sees", micro: "Files, chat history, tool output, and rules become the working state.", terms: ["context", "memory", "rules"] },
      { headline: "Tools define what it can change", micro: "Reading, running, editing, searching, and calling APIs create real effects.", terms: ["tools", "action", "effect"] },
      { headline: "Stop conditions keep work bounded", micro: "The harness must know when to finish, ask, or hand off.", terms: ["done", "ask", "handoff"] },
      { headline: "Autonomy requires controls", micro: "Permissions, guardrails, and evaluation rise in importance as loops get longer.", terms: ["autonomy", "control", "eval"] }
    ]
  },
  {
    id: "05-what-is-a-guardrail",
    order: 5,
    title: "What Is a Guardrail?",
    shortTitle: "Guardrail",
    kind: "guardrail",
    accent: palette.red,
    thesis: "A guardrail enforces policy around inputs, outputs, or actions.",
    scenes: [
      { headline: "Prompting asks; guardrails enforce", micro: "Policy checks can block, redact, route, or require review.", terms: ["policy", "block", "review"] },
      { headline: "Check ingress and egress separately", micro: "Incoming prompts, tool results, final output, and actions have different risks.", terms: ["input", "output", "action"] },
      { headline: "Protect secrets and destructive actions", micro: "Secret scans and approval gates are pragmatic first controls.", terms: ["secrets", "delete", "deploy"] },
      { headline: "Precision matters", micro: "A broad block can stop useful work; a narrow block can miss risk.", terms: ["precision", "recall", "friction"] },
      { headline: "Log decisions for improvement", micro: "Guardrail events become evidence for tuning policy.", terms: ["log", "audit", "tune"] }
    ]
  },
  {
    id: "06-what-is-a-harness",
    order: 6,
    title: "What Is a Harness?",
    shortTitle: "Harness",
    kind: "harness",
    accent: palette.slate,
    thesis: "A harness is the runtime shell that turns a raw model into a usable assistant or agent.",
    scenes: [
      { headline: "The product is not just the model", micro: "Instructions, tools, permissions, memory, and defaults shape behavior.", terms: ["runtime", "tools", "rules"] },
      { headline: "Instruction layers set priorities", micro: "System, organization, repository, and user rules can compete.", terms: ["system", "repo", "user"] },
      { headline: "The harness mediates actions", micro: "A model proposes; the runtime approves, executes, observes, or blocks.", terms: ["route", "execute", "observe"] },
      { headline: "Defaults change cost and risk", micro: "More context, more tools, and more autonomy can mean more spend and exposure.", terms: ["context", "tooling", "budget"] },
      { headline: "Choose the shell for the job", micro: "Workflow fit matters more than a feature checklist.", terms: ["fit", "controls", "workflow"] }
    ]
  },
  {
    id: "07-what-is-a-harness-hook",
    order: 7,
    title: "What Is a Harness Hook?",
    shortTitle: "Hook",
    kind: "hook",
    accent: palette.purple,
    thesis: "A hook is an event-driven interception point inside the harness lifecycle.",
    scenes: [
      { headline: "An event fires", micro: "Session start, prompt submit, pre-tool use, permission request, and stop events are common.", terms: ["event", "lifecycle", "payload"] },
      { headline: "Custom logic inspects the payload", micro: "A hook can validate, log, transform, notify, approve, or deny.", terms: ["inspect", "decide", "record"] },
      { headline: "Hooks turn policy into execution", micro: "They are useful for secrets, destructive commands, formatting, and context shaping.", terms: ["secrets", "format", "shape"] },
      { headline: "Latency is part of the design", micro: "Slow or over-broad hooks can become a hidden tax.", terms: ["latency", "scope", "fail"] },
      { headline: "Package useful hooks for reuse", micro: "A hook pattern that works once often belongs in a plugin or skill.", terms: ["reuse", "plugin", "skill"] }
    ]
  },
  {
    id: "08-what-is-a-harness-plugin",
    order: 8,
    title: "What Is a Harness Plugin?",
    shortTitle: "Plugin",
    kind: "plugin",
    accent: palette.teal,
    thesis: "A plugin packages reusable harness behavior so teams can install and govern it.",
    scenes: [
      { headline: "Plugins turn setup into a package", micro: "Instead of copying local files, a team installs a named bundle.", terms: ["package", "install", "share"] },
      { headline: "Bundles can contain runtime pieces", micro: "Skills, hooks, agents, MCP servers, tools, and settings may travel together.", terms: ["skills", "hooks", "MCP"] },
      { headline: "Manifest plus permissions", micro: "Discovery should not imply unlimited access.", terms: ["manifest", "scope", "allow"] },
      { headline: "Distribution is governance", micro: "Versioning, review, source trust, and rollback matter.", terms: ["version", "review", "rollback"] },
      { headline: "Good plugins reduce drift", micro: "Shared defaults make teams more consistent and less repetitive.", terms: ["defaults", "teams", "reuse"] }
    ]
  },
  {
    id: "09-what-is-a-skill",
    order: 9,
    title: "What Is a Skill?",
    shortTitle: "Skill",
    kind: "skill",
    accent: palette.green,
    thesis: "A skill is on-demand domain expertise: instructions, resources, and scripts for a repeatable task.",
    scenes: [
      { headline: "Stop pasting the same checklist", micro: "Name the workflow and make it discoverable.", terms: ["workflow", "trigger", "repeat"] },
      { headline: "Keep the core concise", micro: "A short SKILL file should route to references only when needed.", terms: ["concise", "route", "load"] },
      { headline: "Progressive disclosure saves context", micro: "Large details stay available without entering every prompt.", terms: ["context", "on-demand", "cheap"] },
      { headline: "Scripts make the process repeatable", micro: "Deterministic helpers reduce copying mistakes and variance.", terms: ["script", "fixture", "validate"] },
      { headline: "Validate the skill alone", micro: "A good skill should work in isolation, not only with hidden repo memory.", terms: ["isolated", "harness", "proof"] }
    ]
  },
  {
    id: "10-what-is-an-mcp",
    order: 10,
    title: "What Is MCP?",
    shortTitle: "MCP",
    kind: "mcp",
    accent: palette.teal,
    thesis: "Model Context Protocol is standardized plumbing between AI clients and external tools or data.",
    scenes: [
      { headline: "MCP replaces bespoke glue", micro: "Clients and servers meet through a shared protocol.", terms: ["client", "server", "standard"] },
      { headline: "Servers expose capabilities", micro: "Tools, resources, and prompts become discoverable.", terms: ["tools", "resources", "prompts"] },
      { headline: "The host still controls policy", micro: "Authentication, authorization, and approval are separate design decisions.", terms: ["auth", "approval", "least"] },
      { headline: "Tool sprawl creates cost and risk", micro: "Every exposed tool can add context, decision load, and attack surface.", terms: ["sprawl", "surface", "budget"] },
      { headline: "Start narrow and read-only", micro: "Expand write capability only after approval and auditing are clear.", terms: ["read-only", "audit", "expand"] }
    ]
  },
  {
    id: "11-ai-alternatives",
    order: 11,
    title: "AI Alternatives",
    shortTitle: "Alternatives",
    kind: "alternatives",
    accent: palette.blue,
    thesis: "Choose assistants by workflow gravity: where context lives, what actions matter, and how control works.",
    scenes: [
      { headline: "There is no universal winner", micro: "Compare the job, not only the model name.", terms: ["job", "context", "action"] },
      { headline: "Products have centers of gravity", micro: "Knowledge work, coding, productivity, research, and custom harnesses differ.", terms: ["knowledge", "coding", "suite"] },
      { headline: "Use the same checklist", micro: "Context, tools, permissions, evaluation, billing, and governance.", terms: ["context", "tools", "billing"] },
      { headline: "Pilot with real tasks", micro: "Measure accepted results, corrections, latency, and permission friction.", terms: ["pilot", "accepted", "friction"] },
      { headline: "Live plan facts change", micro: "Keep exact prices and limits in source notes, not in evergreen animation.", terms: ["plans", "limits", "verify"] }
    ]
  },
  {
    id: "12-observability",
    order: 12,
    title: "Observability",
    shortTitle: "Observability",
    kind: "observability",
    accent: palette.purple,
    thesis: "Observability makes agent behavior inspectable through traces, spans, events, costs, and outcomes.",
    scenes: [
      { headline: "You cannot improve what you cannot inspect", micro: "Agent failures hide inside prompts, tool calls, and retries.", terms: ["trace", "span", "event"] },
      { headline: "Record the run tree", micro: "Model calls, tool calls, inputs, outputs, latency, and cost belong together.", terms: ["model", "tool", "cost"] },
      { headline: "Grade traces, not only answers", micro: "A correct final result can still take a risky or wasteful path.", terms: ["path", "risk", "waste"] },
      { headline: "Find regressions over time", micro: "Compare success rate, drift, error causes, and budget by version.", terms: ["version", "drift", "rate"] },
      { headline: "Feed learning back into skills and hooks", micro: "Reusable fixes should become runtime guidance, not tribal memory.", terms: ["learn", "skill", "hook"] }
    ]
  },
  {
    id: "13-instruction-layers",
    order: 13,
    title: "Instruction Layers",
    shortTitle: "Instructions",
    kind: "instructions",
    accent: palette.slate,
    thesis: "Instruction layers are the rule stack that shapes behavior before the model sees the task.",
    scenes: [
      { headline: "Instructions have precedence", micro: "System, organization, project, user, and skill instructions do not all weigh the same.", terms: ["system", "project", "user"] },
      { headline: "Conflicts must be explicit", micro: "If rules disagree, the harness needs a deterministic priority order.", terms: ["conflict", "priority", "resolve"] },
      { headline: "Local rules encode local reality", micro: "Repo conventions, deploy rules, test commands, and style constraints belong near the work.", terms: ["repo", "style", "tests"] },
      { headline: "Too many rules create fog", micro: "Long stale instruction files cost attention and can misroute the agent.", terms: ["stale", "noise", "route"] },
      { headline: "Promote stable patterns into skills", micro: "Repeated procedural guidance should become a scoped capability.", terms: ["pattern", "skill", "scope"] }
    ]
  },
  {
    id: "14-tools-and-permissions",
    order: 14,
    title: "Tools and Permissions",
    shortTitle: "Permissions",
    kind: "permissions",
    accent: palette.red,
    thesis: "Tool permission is the boundary between helpful suggestion and real-world action.",
    scenes: [
      { headline: "Tools change the environment", micro: "Read, write, run, browse, deploy, and message tools have different risk.", terms: ["read", "write", "run"] },
      { headline: "Default to least privilege", micro: "Give the agent the smallest tool surface that can complete the task.", terms: ["least", "scope", "allow"] },
      { headline: "Approve high-impact actions", micro: "Deletes, production writes, payments, and external messages need checkpoints.", terms: ["delete", "prod", "send"] },
      { headline: "Permission prompts need context", micro: "Humans approve better when they see command, target, reason, and blast radius.", terms: ["target", "reason", "radius"] },
      { headline: "Audit what actually happened", micro: "Tool history turns permission policy into reviewable evidence.", terms: ["history", "audit", "evidence"] }
    ]
  },
  {
    id: "15-data-governance",
    order: 15,
    title: "Data Governance",
    shortTitle: "Governance",
    kind: "governance",
    accent: palette.teal,
    thesis: "Data governance decides what the assistant may see, retain, train on, and reveal.",
    scenes: [
      { headline: "Context is data movement", micro: "Every prompt, file, connector, and tool result moves information across a boundary.", terms: ["data", "context", "boundary"] },
      { headline: "Permissions should follow the user", micro: "The agent should not access more than the person it represents.", terms: ["identity", "access", "sync"] },
      { headline: "Retention and training policies matter", micro: "Teams need to know what is logged, stored, retained, or used for improvement.", terms: ["retention", "logs", "training"] },
      { headline: "Connectors inherit source-system risk", micro: "A badly scoped integration can leak data even if the model is well behaved.", terms: ["connector", "scope", "leak"] },
      { headline: "Governance is part of product selection", micro: "Choose tools whose controls match your regulatory and operational needs.", terms: ["controls", "policy", "fit"] }
    ]
  }
].map((concept) => ({
  ...concept,
  runtimeSeconds: project.runtimeSeconds,
  scenes: concept.scenes.map((scene, index) => ({
    ...sharedScenes.close,
    ...scene,
    index,
    beat: ["open", "define", "mechanism", "tradeoff", "landing"][index]
  }))
}));
