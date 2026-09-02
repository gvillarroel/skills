# What Is an Agent? A Regex-Loop Explanation

## Source Facts

| Field | Value |
| --- | --- |
| Title | `¿QUÉ ES UN AGENTE?` |
| Route | `topic-explainer` |
| Audience | Spanish-speaking mixed technical audience |
| Duration | 30 seconds |
| Key Assets | `lm-railroad.svg`, `agent-railroad.svg`, `harness-flow.svg` |
| Concepts | LM, agent loop, harness |
| Style/Audio | Dark technical 16:9 canvas; silent first iteration with on-screen explanation |

## Narrative Angle

Treat an LM, an agent, and a harness as increasingly expressive grammar: one pass, a repeated loop, and the runtime that governs that loop.

## Shot List

### Shot 1 — The metaphor

- Duration: 0–4 seconds.
- Purpose: Establish the regular-expression/railroad-diagram analogy.
- Source facts used: `¿QUÉ ES UN AGENTE?`.
- Visual frame: A large title, a single red syntax token, and an empty railroad baseline.
- Motion intent: Reveal the title, then scan the token across the baseline.
- Media: On-screen Spanish copy; no audio.
- Validation: The title is readable at full frame and the token establishes the persistent visual identity.

### Shot 2 — LM: one pass

- Duration: 4–9 seconds.
- Purpose: Show that the LM itself performs one context-to-response pass.
- Source facts used: `LM := CONTEXTO · MODELO · RESPUESTA`, `lm-pass`.
- Visual frame: A centered Mermaid railroad diagram with a left-to-right path.
- Motion intent: Route the red token once from context through LM to response.
- Media: Mermaid SVG and on-screen Spanish explanation.
- Validation: Context, LM, and response are all visible; no loop is shown.

### Shot 3 — Agent: repeated expression

- Duration: 9–18 seconds.
- Purpose: Add observation, action, and repetition around the LM.
- Source facts used: `AGENTE := OBJETIVO · (OBSERVAR · LM · ACTUAR)+ · TERMINAR`, `agent-loop`.
- Visual frame: A larger Mermaid railroad diagram whose repeated branch visibly returns to the loop.
- Motion intent: Match-cut the red token into the repeated branch, orbit it twice, and settle on the stopping path.
- Media: Mermaid SVG and on-screen Spanish explanation.
- Validation: The viewer can distinguish one-pass inference from the repeated agent cycle without relying on color alone.

### Shot 4 — Harness: the governing grammar

- Duration: 18–27 seconds.
- Purpose: Pull back and reveal the software around the loop.
- Source facts used: `HARNESS := REGLAS · MEMORIA · PERMISOS · AGENTE(HERRAMIENTAS) · EVALUAR`, `harness-runtime`.
- Visual frame: A Mermaid flowchart with an outer HARNESS boundary, an inner AGENTE boundary, and visible context, tools, permissions, evaluation, and outcomes.
- Motion intent: Pull the prior loop inward, reveal the harness boundary, then activate each governing surface in reading order.
- Media: Mermaid SVG and on-screen Spanish explanation.
- Validation: AGENTE remains visible inside HARNESS; the LM remains visible inside AGENTE.

### Shot 5 — Distinction

- Duration: 27–30 seconds.
- Purpose: Land the three-part mental model.
- Source facts used: `LM genera. El agente itera. El harness gobierna.`.
- Visual frame: Three aligned terms with the red token resting under HARNESS.
- Motion intent: Compress the system into one mnemonic and hold.
- Media: On-screen Spanish copy; no audio.
- Validation: The final mnemonic remains on screen for at least two seconds.

## Validation Anchors

- `¿QUÉ ES UN AGENTE?`
- `LM := CONTEXTO · MODELO · RESPUESTA`
- `AGENTE := OBJETIVO · (OBSERVAR · LM · ACTUAR)+ · TERMINAR`
- `HARNESS := REGLAS · MEMORIA · PERMISOS · AGENTE(HERRAMIENTAS) · EVALUAR`
- `LM genera. El agente itera. El harness gobierna.`
