# Production Notes

## Source Facts

- Model Context Protocol, or MCP, is an open standard for connecting AI clients to external systems such as tools, resources, and prompts.
- Official MCP documentation describes it as a standardized way for AI applications like Claude or ChatGPT to connect to data sources, tools, and workflows, and current ecosystem documentation shows support across clients including Claude, ChatGPT, VS Code, and GitHub Copilot.
- The practical risks are authentication, authorization, registry hygiene, and context sprawl: an MCP server that exposes too many tools or broad permissions can increase both attack surface and cost.

## Visual Metaphor Decision

- Visual pattern: dependency-map.
- Concept claim: a good What is an MCP explainer should show dependency direction, shared prerequisites, bottlenecks, cutover gates, and fallback routes as separate visual mechanisms.
- Mechanic: source nodes converge into an integration layer, risk and bottleneck callouts appear on the dependency path, and release waits for cutover proof before fallback is armed.
- Candidate metaphors: dependency map, phase timeline, and risk matrix.
- Rejected alternative: a phase timeline would show order but hide shared prerequisites, cross-cluster dependencies, and fallback routing.
- Chosen metaphor: dependency map with cluster boundaries, converging edges, risk edge, bottleneck, cutover gate, fallback path, and readiness meter.
- Visual vocabulary: brand red means dependency proof; dark red means cross-system prerequisites; status red means risk or bottleneck; mid gray means integration; black means fallback; dark gray means release readiness.
- Narration split: exact owners, lead times, and dependency weights should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- json { "server": "issue-tracker", "auth": "oauth", "tools": ["list_issues", "get_issue", "comment_issue"], "policy": { "allow_write": false, "require_approval_for": ["comment_issue"] } }
- The teaching point is that MCP integration is not just connectivity. It is capability exposure plus policy. Good MCP setup means least privilege, approved registries, and deliberate tool surface design. citeturn10view4turn7search10turn7search21turn25search11 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "MCP stands for Model Context Protocol. It is an open standard for connecting AI applications to external systems." |
- with multiple client and server ports | | 0:15-0:30 | "Instead of building one custom integration per assistant, MCP gives clients and servers a shared protocol." | One-to-many connector diagram replaces spaghetti lines | | 0:30-0:45 | "An MCP server can expose tools, resources, and prompts. That means an assistant can read data, execute actions, or import structured workflows." | Three lanes labeled **Tools / Resources / Prompts** | | 0:45-1:00 | "Today MCP is supported across major clients, including Claude, ChatGPT-related ecosystems, VS Code, and GitHub Copilot." | Client logos or neutral platform cards connect to the bus | | 1:00-1:15 | "But power creates risk. Authentication and authorization matter because MCP can expose real systems, not just toy tools." | Lock icons appear on the bus | | 1:15-1:30 | "That is why registries, allowlists, and approval policies matter. GitHub already lets organizations control registry URLs and server access." | Registry gate animation | | 1:30-1:45 | "MCP also affects cost. Every discovered tool, every tool description, and every tool call can add context or external API spend." | Context meter and external-billing icons rise | | 1:45-2:00 | "So define MCP as the standard plumbing for AI tools and context-but use least privilege, approval, and narrow tool design." | Final stamp: **Open standard, strict permissions** | Reference basis for narration: official MCP intro/spec docs, GitHub Copilot MCP docs and policy docs, Claude Code MCP docs, and VS Code MCP docs. citeturn38view3turn25search3turn25search9turn10view4turn8search17turn37search14turn7search10turn7search21turn25search11 #### Shot and animation plan - Reuse
- as the core visual identity for all integrations. - Show one messy point-to-point integration map transforming into one protocol bus. - Animate tools, resources, and prompts as different bus passengers. - Add a registry gate and approval shield before write-capable servers. - Reuse
- Tools / Resources / Prompts
- Open standard, strict permissions
- mcp_bus as the core visual identity for all integrations
- Show one messy point-to-point integration map transforming into one protocol bus
- Animate tools
- Add a registry gate and approval shield before write-capable servers
- credit_meter to show context and external API costs rising with tool sprawl
- End with a least-privilege checklist over the MCP bus
- circuit-signal-traces
- flow-tokens
- risk-bowtie
- masonry-wall
- dependency-map
- critical-bowtie-barrier

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-an-mcp --title "What is an MCP" --output-id what-is-an-mcp --pattern dependency-map
```
