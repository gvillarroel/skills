#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Read-only diagnostic of a completed native job; never runs an agent."""
from pathlib import Path
import importlib.util,json,traceback
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925'
spec=importlib.util.spec_from_file_location('pareto','/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
config=module.normalize_config(STUDY/'generation-000.json')
candidate=config['candidates'][0]
staged=STUDY/'search/development/generation-000/candidate-staging/baseline/skills/svg-brief-design'
candidate.update({'evaluatedSkill':staged,'sourceSkillDigest':module.compute_skill_digest(staged)})
job=STUDY/'search/development/generation-000/harbor-jobs/svg-brief-luna-g000-development-baseline'
try:
    result=module.load_native_job(job,candidate=candidate,reward_key=config['rewardKey'],pass_threshold=config['passThreshold'],required_reward_thresholds=config['requiredRewards'])
    (STUDY/'baseline-diagnostic.json').write_text(json.dumps(result,indent=2,default=str))
    print('Native baseline analysis passed.')
except Exception:
    detail=traceback.format_exc();(STUDY/'baseline-analysis-error.txt').write_text(detail);print(detail)
