#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run three sequential isolated native/quality release cases, retaining every attempt."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CASES=[
 ('mermaid','mermaid-runtime.md',['diagram.mmd','style.json','check.json','diagram.static.svg','diagram.animated.svg','review.md']),
 ('plantuml-colorset-renderer','plantuml-runtime.md',['input/deployment.puml','renders/svg/deployment.svg','renders/png/deployment.png','render-report.json','review.md']),
 ('slidev-quality-audit','quality-runtime.md',['review.md','repairs.json']),
]
for skill,prompt,outputs in CASES:
 command=['uv','run','--script','scripts/run-pi-skill-eval.py',skill,'--prompt-file',f'evaluations/arrow-contrast-diagrams/{prompt}','--mode','json','--strict','--model','openai-codex/gpt-5.6-luna','--run-id',f'arrow-native-{skill}-luna1-20261003']
 for output in outputs:command+=['--expect-output',output]
 result=subprocess.run(command,cwd=ROOT)
 print(f'{skill}: harness exit {result.returncode}',flush=True)
