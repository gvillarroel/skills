# What Is An LLM Design Note

## Concept Claim

An LLM is a large neural prediction system that turns text into tokens, scores likely next tokens from context, samples one, appends it, and repeats. It can sound confident without being verified.

## Chosen Visual Metaphor

Use a token loop rather than a brain or magic box. The loop keeps the cause-and-effect visible:

- A prompt splits into token tiles.
- Tokens fill a context window.
- The model transforms context through weighted layers.
- Candidate next tokens race as probability bars.
- The selected token appends to the output and becomes new context.

## Rejected Metaphors

- Brain imagery: implies thought or consciousness.
- Factory imagery alone: useful for flow, but it hides probabilities.
- Database search imagery: suggests the model retrieves exact stored answers.

## Visual Vocabulary

- Token tiles: small colored rectangles with compact text and numeric IDs.
- Context: square matrix cells that light up over time.
- Model: stacked vertical layers with node traces.
- Probabilities: horizontal bars that update and pop a winner.
- Reliability limit: red verification warning that interrupts fluent output.
- Practical rule: four chips labeled context, constraints, examples, checks.

## Timing Contract

Target length is 70 seconds, with a visible mechanism change every 6-8 seconds. The final callback must show the whole loop and the line "prediction + context, not a mind."

