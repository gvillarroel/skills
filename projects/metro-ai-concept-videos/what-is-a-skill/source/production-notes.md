# Production Notes

## Source Facts

- A skill is a reusable capability package for specialized tasks.
- A skill gives the harness structured instructions, scripts, and supporting resources.
- Skills support progressive disclosure because they load when relevant instead of forcing long procedures into every prompt.
- GitHub Copilot describes skills as folders of instructions, scripts, and resources.
- Claude Code says long reference material in a skill costs almost nothing until it is needed.
- OpenCode loads SKILL.md-based skills on demand.
- Skills are useful for deploy checklists, debugging routines, architecture explainers, onboarding flows, and codebase maps.
- The common mistake is making a skill too broad, verbose, or always relevant.

## Visual Metaphor Decision

- Visual pattern: dependency-map.
- Concept claim: a good What is a Skill explainer should show dependency direction, shared prerequisites, bottlenecks, cutover gates, and fallback routes as separate visual mechanisms.
- Mechanic: source nodes converge into an integration layer, risk and bottleneck callouts appear on the dependency path, and release waits for cutover proof before fallback is armed.
- Candidate metaphors: dependency map, phase timeline, and risk matrix.
- Rejected alternative: a phase timeline would show order but hide shared prerequisites, cross-cluster dependencies, and fallback routing.
- Chosen metaphor: dependency map with cluster boundaries, converging edges, risk edge, bottleneck, cutover gate, fallback path, and readiness meter.
- Visual vocabulary: brand red means dependency proof; dark red means cross-system prerequisites; status red means risk or bottleneck; mid gray means integration; black means fallback; dark gray means release readiness.
- Narration split: exact owners, lead times, and dependency weights should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- skill card stack
- long prompt wall shrinking into one skill card
- compatible folder structures
- cost meter staying flat until activation
- example skill cards
- tool badges snapping onto the skill card
- bloated card being trimmed down
- progressive disclosure callout

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-a-skill --title "What is a Skill" --output-id what-is-a-skill --pattern dependency-map
```
