#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record focused deterministic producer tests for the solid-fill revision."""
import concurrent.futures,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3]
out=root/'projects/composition-solid-style/artifacts/tests';out.mkdir(parents=True,exist_ok=True)
cases=[('diagram-composition',s) for s in ['test_composition.py','test_native_panels.py','test_shared_colors.py','test_connector_quality.py']]
cases += [('usefulcharts-style',s) for s in ['test_chart.py','test_editorial.py','test_panel_poster.py']]
cases += [('hierarchy-lens','test_explorer.py')]
def run(case):
    skill,script=case;cmd=['uv','run','--script',f'skills/{skill}/scripts/{script}']
    result=subprocess.run(cmd,cwd=root,text=True,capture_output=True,encoding='utf-8',errors='replace')
    log=out/f'{skill}-{script}.txt';log.write_text(result.stdout+result.stderr,encoding='utf-8')
    record={'command':cmd,'exitCode':result.returncode,'log':str(log.relative_to(root))}
    print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,cases))
(out/'commands.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
if any(r['exitCode'] for r in results):raise SystemExit(1)
