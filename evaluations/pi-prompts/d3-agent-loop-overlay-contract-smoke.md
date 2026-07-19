Use the loaded `d3-animated-svg` skill. Read `../prompt.md` first, then run this exact command from the workspace root:

```bash
uv run --script skills/d3-animated-svg/scripts/build_agent_loop_overlay.py outputs/agent-loop-overlay.html --force
```

The command is the deterministic acceptance gate and validates the canonical pattern ID, embedded image, five region IDs, and absence of external or repository dependencies. Do not inspect the builder source, enumerate directories, open the generated HTML, or run additional shell checks after the command returns `ok: true`. Keep `skills/d3-animated-svg/` read-only. The exact required output is `outputs/agent-loop-overlay.html`.
