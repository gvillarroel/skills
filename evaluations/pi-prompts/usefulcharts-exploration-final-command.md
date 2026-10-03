Your shell tool is Bash. Read the supplied skill and its `references/visible-discovery.md` file. Run these two commands exactly, without adding arguments:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --script skills/usefulcharts-style/scripts/test_exploration_review.py
```

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --script skills/usefulcharts-style/scripts/test_illustrated_review.py
```

Create `control.json` at the workspace root with the two observed test counts and outcomes. Explain the distinction between declared exploration evidence, a reviewer’s actual visual judgment, and independently measured reference-density parity. Keep the copied skill unchanged. Do not discover directories or read acceptance examples or unrelated files.
