#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Add a prospective text-contract cohort to the unchanged native routing runner."""
from pathlib import Path
import hashlib
import json
import subprocess

import validate_creation_routing as native

RUN = native.REPO / "evaluations/runs/svg-brief-design-prompt-contract-20260926"
CASES = [
    {"id": "three-stage-cleaning-flow", "output": "workflow.svg",
     "required_text": {"Captura": 1, "Limpieza": 1, "Entrega": 1},
     "prompt": "Crea /app/workflow.svg: un flujo sencillo de tres etapas, Captura, Limpieza y Entrega, conectadas en ese orden con flechas. Negro sobre fondo transparente, sin adornos. Usa texto SVG editable para esos tres nombres, una vez cada uno, sin añadir otros textos."},
    {"id": "specimen-identification-label", "output": "specimen.svg",
     "required_text": {"MUESTRA 07": 1, "LAB-A": 1},
     "prompt": "Crea /app/specimen.svg: una etiqueta de laboratorio sobria, con MUESTRA 07 como título y LAB-A más pequeño debajo. Solo esos dos textos, una vez cada uno, con texto SVG editable. Usa negro y fondo transparente; no añadas códigos de barras ni adornos."},
    {"id": "energy-input-output-diagram", "output": "energy.svg",
     "required_text": {"Sol": 1, "Consumo": 1},
     "prompt": "Crea /app/energy.svg: un diagrama simple de balance de energía con un depósito central. La flecha Sol entra desde la izquierda; la flecha Consumo sale hacia la derecha. Usa negro, fondo transparente y solo esos dos textos SVG editables, una vez cada uno."},
]
REQUIRED = {case["output"]: case["required_text"] for case in CASES}
BASE_WRITE_JSON = native.write_json

# The model-side setup is reused byte-for-byte. Only evaluator-side checks and
# the new prospective case/protocol globals differ in this separate process.
CHECK = native.CHECK.replace(
    "print(json.dumps({'artifact_valid':True,'verifier_version':module.VERSION,'metadata':metadata,'reference_accessed':False,'fitness_computed':False}))",
    """
from collections import Counter
from defusedxml import ElementTree as ET
root=ET.fromstring(data)
texts=[''.join(node.itertext()).strip() for node in root.iter() if node.tag.rsplit('}',1)[-1]=='text']
expected=REQUIRED_TEXT[sys.argv[1]]
counts=dict(Counter(texts))
print(json.dumps({'artifact_valid':True,'verifier_version':module.VERSION,'metadata':metadata,'reference_accessed':False,'fitness_computed':False,'text_contract':{'expected':expected,'observed':counts,'passed':counts==expected,'scope':'Exact XML text counts only, not semantic relationships or visual readability'}}))
""".replace("REQUIRED_TEXT", repr(REQUIRED)),
)
assert CHECK != native.CHECK


def record(path, value):
    if path.name == "protocol.json":
        value["max_calls"] = 3
        value["scope"] = "New prospective prompt-contract cohort on unchanged baseline. No comparison reference or fitness; text presence does not establish diagram relationships or legibility. Prior routing studies remain unchanged."
        value["required_text_counts"] = REQUIRED
        value["entrypoint_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        value["technical_check_sha256"] = hashlib.sha256(CHECK.encode()).hexdigest()
        value["expected"] += " Exact XML text nodes and counts with no additional text. Manual relationship review remains separate."
    if path.name == "receipt.json":
        value["text_contract_passed"] = value["technical"].get("text_contract", {}).get("passed", False)
        value["passed"] = value["passed"] and value["text_contract_passed"]
    BASE_WRITE_JSON(path, value)


def main():
    native.RUN = RUN
    native.CASES = CASES
    native.CHECK = CHECK
    native.write_json = record
    native.main()
    # Preview rendering is independent post-processing after all model calls.
    preview = """
from pathlib import Path
from PIL import Image
import io,resvg_py
for source in Path('/outputs').glob('*/*.svg'):
    raw=resvg_py.svg_to_bytes(svg_string=source.read_text(),width=640,skip_system_fonts=True,font_dirs=['/usr/share/fonts/truetype/dejavu'],font_family='DejaVu Sans',sans_serif_family='DejaVu Sans')
    rgba=Image.open(io.BytesIO(raw)).convert('RGBA')
    Image.alpha_composite(Image.new('RGBA',rgba.size,'white'),rgba).convert('RGB').save(source.with_suffix('.preview.jpg'))
print('Rendered three contract previews')
"""
    subprocess.run(["docker", "run", "--rm", "--network", "none", "--cpus", "1", "--memory", "1g", "--mount", f"type=bind,source={RUN},target=/outputs", native.VERIFIER_IMAGE, "python", "-c", preview], check=True, timeout=40)


if __name__ == "__main__":
    main()
