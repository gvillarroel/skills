# AI Code Assistant Concepts Storyboard

This storyboard is the global dependency map for the fifteen compact concept videos. Each video keeps one learning objective and reuses the same symbolic language.

## 01. What Is an LLM?

Learning objective: A large language model predicts tokens from context; it is not a database lookup.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Text becomes tokens | Words, spaces, punctuation, and word pieces enter the context box. | tokens, context, input |
| 8.4-16.8s | The model ranks next tokens | Many candidates get scores before one continuation is selected. | rank, score, next |
| 16.8-25.2s | Output loops back | Each generated token becomes part of the next step's context. | append, repeat, sequence |
| 25.2-33.6s | Size is not the same as truth | Parameters, context window, training data, and verification are different concerns. | parameters, window, verify |
| 33.6-42.0s | Better context changes odds | Clearer task context reshapes the token distribution. | prompt, examples, constraints |

## 02. LLM Billing

Learning objective: Cost follows model work, even when a product wraps usage as seats, credits, or subscriptions.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | The same work can wear different price labels | Subscription, credit, API, and local costs are packaging around real compute. | seat, credit, API |
| 8.4-16.8s | Input and output both matter | Long prompts, long answers, and repeated tool loops add up. | input, output, retry |
| 16.8-25.2s | Model choice changes the meter | A stronger model can cost more but may reduce retries on hard work. | model, latency, success |
| 25.2-33.6s | Cache and trim before scaling | Repeated context should be cached or summarized when the harness supports it. | cache, trim, reuse |
| 33.6-42.0s | Track cost per accepted result | The useful metric is completed work, not one isolated call. | accepted, task, budget |

## 03. Probabilities and Evaluation

Learning objective: LLM output is sampled from probabilities; evaluation decides whether the sample is good enough.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Likely is not guaranteed | The model scores candidate continuations instead of fetching one fixed answer. | probability, sample, variance |
| 8.4-16.8s | Context reshapes the distribution | Examples and constraints can move probability toward useful outputs. | context, examples, odds |
| 16.8-25.2s | Tests beat vibes when possible | Schemas, unit tests, parsers, and exact checks make quality measurable. | tests, schema, parser |
| 25.2-33.6s | pass@N trades attempts for cost | More samples can improve success, but every attempt consumes time and budget. | pass@N, attempts, cost |
| 33.6-42.0s | Agent evals need traces | For multi-step work, grade the path as well as the final answer. | trace, grader, regression |

## 04. What Is an Agent?

Learning objective: An agent is a goal-directed loop that observes, acts, reads results, and continues until it should stop.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | A prompt answers; an agent pursues | The system can choose steps after seeing new information. | goal, state, loop |
| 8.4-16.8s | Context defines what it sees | Files, chat history, tool output, and rules become the working state. | context, memory, rules |
| 16.8-25.2s | Tools define what it can change | Reading, running, editing, searching, and calling APIs create real effects. | tools, action, effect |
| 25.2-33.6s | Stop conditions keep work bounded | The harness must know when to finish, ask, or hand off. | done, ask, handoff |
| 33.6-42.0s | Autonomy requires controls | Permissions, guardrails, and evaluation rise in importance as loops get longer. | autonomy, control, eval |

## 05. What Is a Guardrail?

Learning objective: A guardrail enforces policy around inputs, outputs, or actions.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Prompting asks; guardrails enforce | Policy checks can block, redact, route, or require review. | policy, block, review |
| 8.4-16.8s | Check ingress and egress separately | Incoming prompts, tool results, final output, and actions have different risks. | input, output, action |
| 16.8-25.2s | Protect secrets and destructive actions | Secret scans and approval gates are pragmatic first controls. | secrets, delete, deploy |
| 25.2-33.6s | Precision matters | A broad block can stop useful work; a narrow block can miss risk. | precision, recall, friction |
| 33.6-42.0s | Log decisions for improvement | Guardrail events become evidence for tuning policy. | log, audit, tune |

## 06. What Is a Harness?

Learning objective: A harness is the runtime shell that turns a raw model into a usable assistant or agent.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | The product is not just the model | Instructions, tools, permissions, memory, and defaults shape behavior. | runtime, tools, rules |
| 8.4-16.8s | Instruction layers set priorities | System, organization, repository, and user rules can compete. | system, repo, user |
| 16.8-25.2s | The harness mediates actions | A model proposes; the runtime approves, executes, observes, or blocks. | route, execute, observe |
| 25.2-33.6s | Defaults change cost and risk | More context, more tools, and more autonomy can mean more spend and exposure. | context, tooling, budget |
| 33.6-42.0s | Choose the shell for the job | Workflow fit matters more than a feature checklist. | fit, controls, workflow |

## 07. What Is a Harness Hook?

Learning objective: A hook is an event-driven interception point inside the harness lifecycle.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | An event fires | Session start, prompt submit, pre-tool use, permission request, and stop events are common. | event, lifecycle, payload |
| 8.4-16.8s | Custom logic inspects the payload | A hook can validate, log, transform, notify, approve, or deny. | inspect, decide, record |
| 16.8-25.2s | Hooks turn policy into execution | They are useful for secrets, destructive commands, formatting, and context shaping. | secrets, format, shape |
| 25.2-33.6s | Latency is part of the design | Slow or over-broad hooks can become a hidden tax. | latency, scope, fail |
| 33.6-42.0s | Package useful hooks for reuse | A hook pattern that works once often belongs in a plugin or skill. | reuse, plugin, skill |

## 08. What Is a Harness Plugin?

Learning objective: A plugin packages reusable harness behavior so teams can install and govern it.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Plugins turn setup into a package | Instead of copying local files, a team installs a named bundle. | package, install, share |
| 8.4-16.8s | Bundles can contain runtime pieces | Skills, hooks, agents, MCP servers, tools, and settings may travel together. | skills, hooks, MCP |
| 16.8-25.2s | Manifest plus permissions | Discovery should not imply unlimited access. | manifest, scope, allow |
| 25.2-33.6s | Distribution is governance | Versioning, review, source trust, and rollback matter. | version, review, rollback |
| 33.6-42.0s | Good plugins reduce drift | Shared defaults make teams more consistent and less repetitive. | defaults, teams, reuse |

## 09. What Is a Skill?

Learning objective: A skill is on-demand domain expertise: instructions, resources, and scripts for a repeatable task.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Stop pasting the same checklist | Name the workflow and make it discoverable. | workflow, trigger, repeat |
| 8.4-16.8s | Keep the core concise | A short SKILL file should route to references only when needed. | concise, route, load |
| 16.8-25.2s | Progressive disclosure saves context | Large details stay available without entering every prompt. | context, on-demand, cheap |
| 25.2-33.6s | Scripts make the process repeatable | Deterministic helpers reduce copying mistakes and variance. | script, fixture, validate |
| 33.6-42.0s | Validate the skill alone | A good skill should work in isolation, not only with hidden repo memory. | isolated, harness, proof |

## 10. What Is MCP?

Learning objective: Model Context Protocol is standardized plumbing between AI clients and external tools or data.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | MCP replaces bespoke glue | Clients and servers meet through a shared protocol. | client, server, standard |
| 8.4-16.8s | Servers expose capabilities | Tools, resources, and prompts become discoverable. | tools, resources, prompts |
| 16.8-25.2s | The host still controls policy | Authentication, authorization, and approval are separate design decisions. | auth, approval, least |
| 25.2-33.6s | Tool sprawl creates cost and risk | Every exposed tool can add context, decision load, and attack surface. | sprawl, surface, budget |
| 33.6-42.0s | Start narrow and read-only | Expand write capability only after approval and auditing are clear. | read-only, audit, expand |

## 11. AI Alternatives

Learning objective: Choose assistants by workflow gravity: where context lives, what actions matter, and how control works.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | There is no universal winner | Compare the job, not only the model name. | job, context, action |
| 8.4-16.8s | Products have centers of gravity | Knowledge work, coding, productivity, research, and custom harnesses differ. | knowledge, coding, suite |
| 16.8-25.2s | Use the same checklist | Context, tools, permissions, evaluation, billing, and governance. | context, tools, billing |
| 25.2-33.6s | Pilot with real tasks | Measure accepted results, corrections, latency, and permission friction. | pilot, accepted, friction |
| 33.6-42.0s | Live plan facts change | Keep exact prices and limits in source notes, not in evergreen animation. | plans, limits, verify |

## 12. Observability

Learning objective: Observability makes agent behavior inspectable through traces, spans, events, costs, and outcomes.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | You cannot improve what you cannot inspect | Agent failures hide inside prompts, tool calls, and retries. | trace, span, event |
| 8.4-16.8s | Record the run tree | Model calls, tool calls, inputs, outputs, latency, and cost belong together. | model, tool, cost |
| 16.8-25.2s | Grade traces, not only answers | A correct final result can still take a risky or wasteful path. | path, risk, waste |
| 25.2-33.6s | Find regressions over time | Compare success rate, drift, error causes, and budget by version. | version, drift, rate |
| 33.6-42.0s | Feed learning back into skills and hooks | Reusable fixes should become runtime guidance, not tribal memory. | learn, skill, hook |

## 13. Instruction Layers

Learning objective: Instruction layers are the rule stack that shapes behavior before the model sees the task.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Instructions have precedence | System, organization, project, user, and skill instructions do not all weigh the same. | system, project, user |
| 8.4-16.8s | Conflicts must be explicit | If rules disagree, the harness needs a deterministic priority order. | conflict, priority, resolve |
| 16.8-25.2s | Local rules encode local reality | Repo conventions, deploy rules, test commands, and style constraints belong near the work. | repo, style, tests |
| 25.2-33.6s | Too many rules create fog | Long stale instruction files cost attention and can misroute the agent. | stale, noise, route |
| 33.6-42.0s | Promote stable patterns into skills | Repeated procedural guidance should become a scoped capability. | pattern, skill, scope |

## 14. Tools and Permissions

Learning objective: Tool permission is the boundary between helpful suggestion and real-world action.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Tools change the environment | Read, write, run, browse, deploy, and message tools have different risk. | read, write, run |
| 8.4-16.8s | Default to least privilege | Give the agent the smallest tool surface that can complete the task. | least, scope, allow |
| 16.8-25.2s | Approve high-impact actions | Deletes, production writes, payments, and external messages need checkpoints. | delete, prod, send |
| 25.2-33.6s | Permission prompts need context | Humans approve better when they see command, target, reason, and blast radius. | target, reason, radius |
| 33.6-42.0s | Audit what actually happened | Tool history turns permission policy into reviewable evidence. | history, audit, evidence |

## 15. Data Governance

Learning objective: Data governance decides what the assistant may see, retain, train on, and reveal.

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
| 0.0-8.4s | Context is data movement | Every prompt, file, connector, and tool result moves information across a boundary. | data, context, boundary |
| 8.4-16.8s | Permissions should follow the user | The agent should not access more than the person it represents. | identity, access, sync |
| 16.8-25.2s | Retention and training policies matter | Teams need to know what is logged, stored, retained, or used for improvement. | retention, logs, training |
| 25.2-33.6s | Connectors inherit source-system risk | A badly scoped integration can leak data even if the model is well behaved. | connector, scope, leak |
| 33.6-42.0s | Governance is part of product selection | Choose tools whose controls match your regulatory and operational needs. | controls, policy, fit |
