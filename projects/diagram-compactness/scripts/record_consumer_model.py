#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record the consumer release model exception before launching its trials."""
from pathlib import Path

root = Path(__file__).resolve().parents[3]
skills = {"video", "slidev-animejs", "slidev-echarts", "echarts-animated-svg", "slidev-quality-audit"}
path = root / "SKILLS.md"
note = (" Consumer release model exception: `openai-codex/gpt-5.6-sol`, "
        "locally catalogued, after retaining Luna's sampled execution/visual failures. "
        "Use fresh exact-output strict cohorts and the same independent visual gates; "
        "do not relabel the prior attempts as passes. ")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
for index, line in enumerate(lines):
    if not line.startswith("| "):
        continue
    cells = line.rstrip("\r\n").split("|")
    if cells[1].strip() in skills and "Consumer release model exception:" not in cells[-2]:
        cells[-2] = cells[-2].rstrip() + note
        lines[index] = "|".join(cells) + "\n"
path.write_text("".join(lines), encoding="utf-8", newline="")
print("Recorded gpt-5.6-sol consumer release exception in five backlog rows.")
