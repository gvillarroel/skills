Create exactly `scene.html` and `validation.json` at the workspace root.
Treat `skills/threejs-animated-3d/` as read-only and use only that bundle and
local tools, without network resources or package installation.

Use this command after reading the skill:

```sh
python skills/threejs-animated-3d/scripts/build_standalone_threejs.py scene.html
```

Validate `scene.html` with the bundled standalone validator and write its report
to `validation.json`. The final scene must render, animate, replay, and support
camera dragging at desktop and mobile widths. Report the outcome.
