Build this eight-state sequencing pattern, then validate the output. Treat skills/procedural-svg-animation/ as read-only; do not read acceptance fixtures, other skills or outside context. Keep task files in this workspace.

```bash
uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py procedural-svg-state-sequencer --output sequencer.svg --palette colorset2 --seed 31 --duration-ms 4000
```
