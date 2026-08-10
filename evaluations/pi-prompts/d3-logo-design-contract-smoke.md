Use the loaded `d3-logo-design` skill to run a deterministic build-and-validate contract smoke test.

Work only from this prompt and the loaded skill at `skills/d3/`. Treat the entire skill directory as read-only. Do not edit, copy back into, or generate files inside it. Do not inspect or search parent directories, sibling skills, repository documentation, evaluation files, hidden context, or the network. Do not enumerate the workspace or look for alternative examples. Do not install packages or substitute tools.

Run this Bash command block exactly as written from the workspace root:

```bash
mkdir -p outputs
uv run --script skills/d3/scripts/build_logo_studio.py --output outputs/northlight-logo.html --brand "Northlight" --tagline "Signal in motion" --colorset colorset1 --pattern d3-logo-type-orbit --texture d3-logo-diagonal-hatch --font geometric --seed 731
uv run --script skills/d3/scripts/validate_logo_artifact.py outputs/northlight-logo.html --expect-patterns 30 --expect-textures 10 --expect-compositions 30 --require-colorset colorset1 --json-report outputs/northlight-validation.json
python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("outputs/northlight-validation.json").read_text(encoding="utf-8"))
if data.get("ok") is not True:
    raise SystemExit("Expected outputs/northlight-validation.json to contain ok=true.")
print(json.dumps({key: data[key] for key in ("ok", "patternCount", "textureCount", "compositionCount", "selectedColorset")}, indent=2))
PY
```

Do not change the commands, flags, values, or output paths. The required artifacts are exactly `outputs/northlight-logo.html` and `outputs/northlight-validation.json`. The HTML must contain the adjustable D3 logo studio with 30 patterns, 10 textures, and 30 finished compositions; the validation report must contain `"ok": true`, `patternCount: 30`, `textureCount: 10`, `compositionCount: 30`, and `selectedColorset: "colorset1"`.

At the end, report the two output paths and the observed validation fields. Keep `skills/d3/` unchanged.
