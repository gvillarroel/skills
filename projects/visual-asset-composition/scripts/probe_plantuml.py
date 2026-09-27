#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare native PlantUML padding without changing font sizes or sources."""
from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/visual-asset-composition/artifacts/plantuml-final-probe"
JAR = ROOT / "projects/plantuml-colorset-renderer/artifacts/tools/plantuml-1.2026.6.jar"
CASES = {
    "flow": '@startuml\nrectangle "Receive request" as A\nrectangle "Validate record" as B\nrectangle "Save result" as C\nA --> B\nB --> C\n@enduml',
    "sequence": '@startuml\nparticipant Client\nparticipant Gateway\nparticipant Store\nClient -> Gateway: Submit request\nGateway -> Store: Persist result\nStore --> Gateway: Accepted\nGateway --> Client: Confirm\n@enduml',
    "class": '@startuml\nclass Request {\n+id: String\n+status: String\n+validate()\n}\nclass Result {\n+savedAt: Date\n}\nRequest --> Result\n@enduml',
    "activity": '@startuml\nstart\n:Receive request;\n:Validate record;\n:Save result;\nstop\n@enduml',
    "mindmap": '@startmindmap\n* Service\n** Intake\n*** Receive\n*** Validate\n** Storage\n*** Persist\n@endmindmap',
    "override": '@startuml\n<style>\nroot { Padding 18 }\n</style>\nstart\n:Preserve padding;\n:Second record;\nstop\n@enduml',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = subprocess.check_output(['git', 'show', 'bd10b36c:skills/plantuml-colorset-renderer/assets/themes/cs1.puml'], cwd=ROOT).decode('utf-8')
    compact = (ROOT / "skills/plantuml-colorset-renderer/assets/themes/cs1.puml").read_text(encoding='utf-8')
    variants = {'baseline': base, 'candidate': compact}
    rows = []
    for case, source in CASES.items():
        for variant, theme in variants.items():
            first, rest = source.split('\n', 1)
            themed = first + '\n' + theme + '\n' + rest
            run = subprocess.run(['java', '-jar', str(JAR), '-tsvg', '-pipe'], input=themed.encode(), capture_output=True, check=True)
            svg = ET.fromstring(run.stdout)
            assert 'Syntax Error' not in run.stdout.decode(), case
            output = OUT / f'{case}-{variant}.svg'
            output.write_bytes(run.stdout)
            row = {'case': case, 'variant': variant, 'width': svg.get('width'), 'height': svg.get('height'), 'viewBox': svg.get('viewBox'), 'rectHeights': [e.get('height') for e in svg.iter() if e.tag.endswith('}rect')], 'fontSizes': sorted({e.get('font-size') for e in svg.iter() if e.tag.endswith('}text')})}
            rows.append(row)
            print(json.dumps(row), flush=True)
    (OUT / 'candidate-theme.puml').write_text(compact, encoding='utf-8', newline='\n')
    (OUT / 'measurements.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
