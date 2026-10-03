#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare independent treemap reports while allowing intended paint changes."""

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference",type=Path)
    parser.add_argument("reports",type=Path,nargs="+")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    key=lambda state:(state["viewportWidth"],state["reducedMotion"],state["replay"])
    reference=json.loads(args.reference.read_text(encoding="utf-8"))
    known={key(state):state for state in reference["states"]}
    findings=[]
    comparisons=[]
    for path in args.reports:
        report=json.loads(path.read_text(encoding="utf-8"))
        count=0
        for state in report["states"]:
            prior=known.get(key(state))
            if prior is None:
                findings.append(f"{path}: unknown reference state {key(state)}.")
                continue
            previous={node["name"]:node for node in prior["nodes"]}
            current={node["name"]:node for node in state["nodes"]}
            if current.keys()!=previous.keys():
                findings.append(f"{path}: node names/count changed in {key(state)}.")
            for name,node in current.items():
                old=previous.get(name)
                if old is None or any(node[field]!=old[field] for field in ("depth","value","branch","geometry")):
                    findings.append(f"{path}: {name} geometry/data/relationship changed in {key(state)}.")
                count+=1
        comparisons.append({"report":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"states":len(report["states"]),"nodeComparisons":count})
    result={"clean":not findings,"reference":str(args.reference),"referenceSha256":hashlib.sha256(args.reference.read_bytes()).hexdigest(),"comparisons":comparisons,"findings":findings}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if result["clean"] else 1


if __name__=="__main__":
    raise SystemExit(main())
