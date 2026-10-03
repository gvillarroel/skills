#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Freeze interval reporting without new inference or changing quality decisions."""
from pathlib import Path
import shutil
from svg_excellence import REPO,read,sha,write
from svg_curated_pairs import ROOT


def main():
    old=REPO/"projects/svg-brief-design/evaluation/art-direction-v5.1"
    new=REPO/"projects/svg-brief-design/evaluation/art-direction-v5.2";new.mkdir(exist_ok=False)
    shutil.copy2(old/"job.json",new/"job.json")
    shutil.copy2(old.parent/"art-direction-v5/visual-pair-prompt.txt",new/"visual-pair-prompt.txt")
    protocol=read(old/"protocol.json")|{
        "version":"5.2.0","maximum_jev_calls":0,
        "previous":"v5.1 supplied valid complete decisions, including six unresolved records. Preserve every decision and abstention. No new model call and no outcome-based rerun.",
        "uncertainty":"Map unresolved artistic dimensions to their entire possible 50–100 interval. The optimization reward is its conservative lower bound; report the interval and no point score. Overall preference is diagnostic, not a seventh weighted dimension. Unknown candidate subject still has no reward.",
        "acceptance":"Unchanged numerical thresholds, checked against the upper bound of candidate quality. Order stability uses the worst possible distance between intervals. No cases are dropped.",
        "promotion":"A selected candidate with unresolved dimensions requires human review before promotion; the optimization reward alone cannot resolve uncertainty.",
    }
    write(new/"protocol.json",protocol)
    sources=[new/"job.json",new/"protocol.json",new/"visual-pair-prompt.txt",Path(__file__).with_name("curated_quality_v52.py"),ROOT/"scoring-v5.1/jev-effective/decisions.jsonl"]
    write(ROOT/"bounds-lock.json",{"files":{p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in sources},"additional_model_calls":0})
    print("Frozen explicit uncertainty intervals; all existing semantic decisions retained.")


if __name__=="__main__":main()
