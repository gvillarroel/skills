# Production Notes

## Source Facts

- A guardrail is a control layer around an agent, input, output, or tool action.
- A guardrail decides whether a task should proceed, pause, be changed, or stop.
- Guardrails can inspect user prompts, model outputs, and tool calls.
- Guardrail actions include block, redact, route, and escalate.
- A prompt suggests behavior, while a guardrail enforces a policy.
- Google Model Armor can screen prompts and responses for prompt injection, jailbreaks, sensitive data, malicious URLs, and related risks.
- OpenAI-style guidance uses automatic checks plus human review before sensitive or high-impact work continues.
- For code assistants, common guardrails protect secrets, production systems, and destructive commands.

## Visual Metaphor Decision

- Visual pattern: risk-bowtie.
- Concept claim: a good What is a Guardrail explainer should show threats, preventive barriers, the top event, mitigative barriers, consequences, degraded controls, and repair action as separate mechanisms.
- Mechanic: threats converge through preventive barriers into a top event, then mitigative barriers reduce consequences while degraded controls and repair action expose the control gap.
- Candidate metaphors: risk bowtie, causal loop, and dependency map.
- Rejected alternative: a causal loop would show influence but blur whether a control prevents the event or mitigates consequences after the event.
- Chosen metaphor: risk-bowtie map with threat set, preventive barriers, top event, mitigative barriers, consequences, degraded barrier, residual risk, and repair action.
- Visual vocabulary: status red means threats, consequences, and degraded control gaps; brand red means preventive control; dark gray means mitigative control; dark red means repair action.
- Narration split: exact likelihood, severity, control owners, and assurance evidence should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- shield gate around agent loop
- input gate
- output gate
- action gate
- prompt bubble versus hard gate
- Model Armor filter fan-out
- human approval control
- secrets and destructive command warnings
- safety versus friction balance
- residual risk block

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-a-guardrail --title "What is a Guardrail" --output-id what-is-a-guardrail --pattern risk-bowtie
```
