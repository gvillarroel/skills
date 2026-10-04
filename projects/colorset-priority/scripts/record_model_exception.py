#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Record the observed provider blocker before the fallback model dispatch."""

from pathlib import Path

root = Path(__file__).resolve().parents[3]
path = root / "SKILLS.md"
owners = {"echarts-animated-svg", "slidev-echarts", "vectorize-art-patterns"}
note = " Recorded CS1 priority model exception: `openai-codex/gpt-5.6-luna` after each own-skill mandated Spark attempt failed before tools because the provider does not support `gpt-5.3-codex-spark` on this ChatGPT account; retain those attempts as failures."
lines = path.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if line.startswith("| ") and line.split("|")[1].strip() in owners:
        fields = line.split("|")
        if note.strip() not in fields[-2]:
            fields[-2] = fields[-2].rstrip() + note + " "
        lines[index] = "|".join(fields)
path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("Recorded three own-skill Luna model exceptions after provider failures.")
