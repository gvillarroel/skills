# Production Notes

## Source Facts

- A guardrail is a control layer that checks inputs, outputs, or tool behavior and then blocks, routes, redacts, or escalates based on policy.
- Official guidance from both OpenAI and Google frames guardrails as validation and governance mechanisms rather than as “magic safety.” Google Cloud Model Armor is a particularly concrete example because it can screen prompts and responses for prompt injection, jailbreaks, sensitive data, malicious URLs, and related risks; it has a free tier up to two million tokens per month and then usage pricing beyond that.

## Visual Metaphor Decision

- Visual pattern: risk-bowtie.
- Concept claim: a good What is a Guardrail explainer should show enforceable policy acting around an agent loop through input, output, and action gates.
- Mechanic: prompt, output, and tool-call packets hit separate gates; a shield closes around the agent loop, risk score and policy matrix activate outcomes, and human approval pauses protected actions.
- Candidate metaphors: guardrail gate megacanvas, generic risk bowtie, and state-machine lifecycle.
- Rejected alternative: a generic risk bowtie would show threats and consequences but hide the specific guardrail mechanic: inspect, block, redact, route, escalate, approve, or continue.
- Chosen metaphor: guardrail gate megacanvas with shield_gate around agent_loop_ring, three inspection gates, risk score, Model Armor-style lanes, policy outcome tiles, human approval modal, protected action tiles, and safety-friction balance.
- Visual vocabulary: brand red means allowed or primary policy flow; status red means blocked or high-risk paths; dark red means hard policy enforcement; grays separate background, zones, modules, connectors, inactive marks, and active marks. Colorset2 is not used; the requested green-yellow-red policy matrix is encoded with colorset1 gray, dark red, and status red because hue is not needed for state separation.
- Narration split: vendor details, exact threshold names, and final policy copy stay in narration or source facts; the frame carries the policy mechanics without explanatory text.

## Strategy Anchors

- python # Pseudocode: input and action guardrail risk = model_armor.scan(prompt) if risk.prompt_injection >= HIGH: return block("Prompt injection risk too high") if risk.sensitive_data_detected: prompt = redact(prompt) if action in {"deploy", "delete", "write_prod"}: return require_human_approval(action) return continue_run(prompt)
- The pattern above matches current platform guidance: automatic validation first, human approval for sensitive actions, then continuation only if policy passes. citeturn22search9turn22search15turn22search4turn22search20 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "A guardrail is a control layer around an agent. Its job is not to do the task. Its job is to decide whether the task should proceed." |
- closes over the agent loop | | 0:15-0:30 | "Guardrails can inspect user prompts, model outputs, and tool calls. Then they can block, redact, route, or escalate." | Three gates labeled **Input / Output / Action** | | 0:30-0:45 | "That makes them different from prompting. A prompt suggests behavior. A guardrail enforces a policy." | Split screen: prompt bubble vs hard gate | | 0:45-1:00 | "Google Model Armor is a strong example. It can screen for prompt injection, jailbreaks, sensitive data, and malicious URLs." | Model Armor filters fan out as colored lanes | | 1:00-1:15 | "OpenAI's guidance uses the same design idea: run automatic checks, and pause for human review before risky work continues." | Human approval button appears over a deploy action | | 1:15-1:30 | "For code assistants, guardrails often protect secrets, production systems, or destructive commands." |
- ,
- , and deploy icons light up red | | 1:30-1:45 | "Good guardrails reduce risk and wasted retries. Bad guardrails create false positives and slow teams down." | Balance scale: safety vs friction | | 1:45-2:00 | "So define guardrails as enforceable policies over input, output, and actions, not as just another prompt trick." | Recap card: **Policy checks over agent behavior** | Reference basis for narration: OpenAI guardrail guidance and Google Model Armor product and docs. citeturn22search9turn22search2turn22search1turn22search4turn22search0turn22search13 #### Shot and animation plan - Reuse
- around the
- - Show three inspection layers: incoming prompt, generated text, outgoing tool call. - Animate one positive case and one blocked case so the gate feels functional. - Reuse a
- bar derived from
- Input / Output / Action
- Policy checks over agent behavior
- shield_gate around the agent_loop_ring
- Show three inspection layers: incoming prompt
- Animate one positive case and one blocked case so the gate feels functional
- a risk_score bar derived from probability_bars
- Add a human approval modal for a production deploy
- End with a green-yellow-red policy matrix that can be reused in hooks and permissions modules
- risk-bowtie
- critical-bowtie-barrier

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-guardrail --title "What is a Guardrail" --output-id what-is-a-guardrail --pattern risk-bowtie
```
