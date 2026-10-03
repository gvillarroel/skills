#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run final raster-canvas and HTML-composite payload trials sequentially."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
for skill,prompt,outputs in [
 ('plantuml-colorset-renderer','plantuml-runtime.md',['input/deployment.puml','renders/svg/deployment.svg','renders/png/deployment.png','render-report.json','review.md']),
 ('slidev-quality-audit','quality-runtime.md',['review.md','repairs.json']),
]:
 command=['uv','run','--script','scripts/run-pi-skill-eval.py',skill,'--prompt-file',f'evaluations/arrow-contrast-diagrams/{prompt}','--mode','json','--strict','--model','openai-codex/gpt-5.6-luna','--run-id',f'arrow-native-{skill}-luna2-20261003']
 for output in outputs:command+=['--expect-output',output]
 result=subprocess.run(command,cwd=ROOT);print(f'{skill}: harness exit {result.returncode}',flush=True)
