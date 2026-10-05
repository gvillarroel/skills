Create a self-contained seeded SVG explaining an ordered message route. The stationary concepts are Source, Check, Destination. Show visible directional connections, reveal the accent route first, then move a token along it. Preserve readable labels and a complete stationary reduced-motion state. Use colorset1 and seed 104729. Execute this exact build command after the required helper help command:

```bash
uv run --script skills/procedural-svg-animation/scripts/build_connected_scene.py build --label Source --label Check --label Destination --seed 104729 --palette colorset1 --output artifacts/route.svg
```

Deliver artifacts/route.svg, artifacts/preview.png and artifacts/browser.json. Use the dedicated validator and bundled browser capture, and inspect ordinary and reduced-motion states. Keep skills/procedural-svg-animation read-only and all generated files in this workspace outside skills/. Do not browse the network or discover other skills.
