Use only skills/reflex-xy/ as a read-only skill resource and normal tools. Do not read installed examples, other skills, repository docs or personal settings. Keep all task output inside this workspace and outside the skill. Do not render through a live service or install/deploy a plugin.

Create deliverables/ and write deliverables/route.md first. Run this exact command as a standalone bash call:

```bash
uv run --script skills/reflex-xy/scripts/xy_colorsets.py --colorset colorset1 > deliverables/design.json
```

Inspect the palette and the focused chart recipes. Explain the connected Sankey endpoint identity contract and a concrete way to keep an upward trend's last value clear of its legend in deliverables/route.md.
