# Production Notes

## Source Facts

- The named alternatives map to different home bases for AI work.
- Atlassian Rovo is strongest for organizational knowledge across Jira, Confluence, and connected tools.
- Gemini App is a consumer and prosumer assistant with subscription tiers and deep Google ecosystem ties.
- GitHub Copilot is strongest as a coding harness inside developer workflows.
- Claude Desktop and Claude Code are strong for coding and research workflows with connectors, skills, hooks, plugins, and MCP.
- Rovo ships in paid Atlassian cloud subscriptions and Rovo Dev uses a credit model per developer.
- Copilot has Free through Enterprise plans and AI-credit billing.
- Claude blends subscriptions with API-style usage, while Gemini uses plan tiers and region-dependent availability.

## Visual Metaphor Decision

- Visual pattern: comparison-matrix.
- Concept claim: a good AI alternatives explainer should compare options against shared criteria, expose tradeoffs, and delay recommendation until evidence is visible.
- Mechanic: option columns stay fixed while criteria rows fill, score-shift markers explain changing preference, and recommendation plus guardrail panels appear after the comparison is legible.
- Candidate metaphors: decision matrix, ranking podium, and pros/cons ledger.
- Rejected alternative: a ranking podium would show a winner but hide which criteria changed the decision.
- Chosen metaphor: comparison matrix with shared criteria rows, per-option score bars, tradeoff lens, recommendation, and guardrail.
- Visual vocabulary: brand red means the selected option or score movement; dark gray means quality balance; status red means cost or risk; dark red means guardrail; black marks the decision cursor.
- Narration split: exact scores and weighting can be explained in narration or source notes unless the prompt supplies them.

## Strategy Anchors

- comparison grid
- Atlassian suite knowledge graph feeding Rovo
- Gemini plan cards
- Copilot runtime stack
- Claude desktop to terminal transition
- use-case quadrants
- four cost meters
- choose by workflow gravity selector

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/ai-alternatives --title "What AI alternatives we have" --output-id ai-alternatives --pattern comparison-matrix
```
