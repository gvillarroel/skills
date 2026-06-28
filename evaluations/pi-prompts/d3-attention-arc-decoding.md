Create a self-contained D3 animated SVG HTML artifact using the exact pattern `d3-pattern-attention-arc-decoding`.

Requirements:

- Write the final artifact to exactly `attention-arc-decoding.html` in the workspace root.
- Do not create or use any other output filename.
- Use the bundled deterministic builder if it is available, passing the exact requested output path.
- Before finishing, verify that `attention-arc-decoding.html` exists and is non-empty.
- The visual must show the phrase-building sequence `The model predicts the next word`.
- Start with visible prompt tokens `The`, `model`, and `predicts`, followed by three empty future slots.
- Animate three decode steps:
  - Step 1 draws attention arcs into the first empty slot and reveals `the`.
  - Step 2 draws attention arcs from the prompt tokens plus `the` into the next empty slot and reveals `next`.
  - Step 3 draws attention arcs from the prompt tokens plus `the` and `next` into the final empty slot and reveals `word`.
- The generated tokens must visually join the context for later steps, such as by using their token color on outgoing attention arcs.
- Include SVG-native animation, not D3 transitions that disappear from exported markup.
- Expose `data-pattern-id="d3-pattern-attention-arc-decoding"` on the SVG.
- Expose `data-decode-step`, `data-source-token`, `data-target-token`, and `data-attention-weight` on attention arc paths.
- Do not read or write inside `skills/d3-animated-svg/assets/examples/`.
- Do not use CDN scripts, remote fonts, or network resources.
