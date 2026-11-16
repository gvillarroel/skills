#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Materialize the reviewed documentary portraits and exact NVIDIA brand mark."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "resources/plugin/skills"
if not PLUGIN.is_dir():
    PLUGIN = ROOT.parent / "line-world-video/artifacts/packages/line-world-video-0.14.2/plugin/skills"


def main():
    sources = json.loads((ROOT / "artifacts/data/portrait-source-candidates.json").read_text(encoding="utf-8"))
    paper = "https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf"
    image_net = "https://www.image-net.org/static_files/papers/imagenet_cvpr09.pdf"
    selections = {
        "ian-buck": {"label": "Ian Buck", "role": "CUDA software development", "stage": "cuda-platform", "sourcePage": "https://www.nvidia.com/en-us/events/isc/", "identityEvidence": "Named NVIDIA speaker portrait; actual downloaded image inspected", "contributionEvidence": "https://developer.nvidia.com/blog/inside-the-programming-evolution-of-gpu-computing", "rights": {"creator": "NVIDIA; photographer unspecified", "license": "Institutional press photograph; no open license asserted", "credit": "Ian Buck portrait: NVIDIA ISC speaker material; retained for this educational example"}, "focus": [.5, .43]},
        "fei-fei-li": {"label": "Fei-Fei Li", "role": "ImageNet project leadership and coauthorship", "stage": "imagenet-scale", "identityEvidence": "Named Commons file, original ITU event image and Stanford biography; actual image inspected", "contributionEvidence": image_net, "focus": [.53, .25], "zoom": 1.6},
        "jia-deng": {"label": "Jia Deng", "role": "First author, ImageNet 2009 paper", "stage": "imagenet-scale", "sourcePage": "https://www.cs.princeton.edu/~jiadeng/", "identityEvidence": "Portrait linked directly from Jia Deng's Princeton faculty homepage; actual image inspected", "contributionEvidence": image_net, "rights": {"creator": "Jia Deng faculty homepage; photographer unspecified", "license": "Institutional portrait; no open license asserted", "credit": "Jia Deng portrait: personal faculty homepage, Princeton University; retained for this educational example"}},
        "alex-krizhevsky": {"label": "Alex Krizhevsky", "role": "AlexNet coauthor", "stage": "alexnet-model", "sourcePage": "https://qz.com/1307091/the-inside-story-of-how-ai-got-good-enough-to-dominate-silicon-valley", "identityEvidence": "Portrait attached to Quartz's named interview about the Toronto researcher; original academic page corroborates identity/context; actual image inspected. An unrelated ASOCS namesake profile was rejected.", "contributionEvidence": paper, "rights": {"creator": "Quartz article image; photographer unspecified", "license": "Editorial photograph; no open license asserted", "credit": "Alex Krizhevsky portrait: Quartz, The inside story of how AI got good enough to dominate Silicon Valley; retained for this educational example"}, "focus": [.55, .4], "zoom": 1.15},
        "ilya-sutskever": {"label": "Ilya Sutskever", "role": "AlexNet coauthor", "stage": "alexnet-model", "identityEvidence": "Commons Ilya Sutskever category and the original 2014 Steve Jurvetson event photograph; actual image inspected", "contributionEvidence": paper, "focus": [.58, .15], "zoom": 2},
        "geoffrey-hinton": {"label": "Geoffrey Hinton", "role": "AlexNet coauthor and doctoral adviser", "stage": "alexnet-model", "identityEvidence": "Named Commons lecture photograph at UBC; actual image inspected", "contributionEvidence": paper, "focus": [.5, .4]},
    }
    entries = []
    for source in sources:
        entry = {"id": source["id"], "kind": "portrait", "sourceFile": "../sources/portraits/" + Path(source["localSource"]).name, "reviewed": True, **selections[source["id"]]}
        if "sourcePage" not in entry:
            entry["sourcePage"] = source["sourcePage"]
        if "rights" not in entry:
            entry["rights"] = {"creator": source["creator"], "license": source["license"], "licenseUrl": source["licenseUrl"], "credit": source["id"].replace("-", " ") + ": " + source["creator"] + "; Wikimedia Commons source linked below"}
        entries.append(entry)
    provenance = json.loads((ROOT / "artifacts/sources/logos/nvidia.provenance.json").read_text(encoding="utf-8"))
    entries.append({"id": "nvidia", "kind": "logo", "label": "NVIDIA", "sourceFile": "../sources/logos/nvidia.svg", "reviewed": True, "sourcePage": provenance["source"]["sourceUrl"], "identityEvidence": "Exact ai-ecosystem-nvidia color SVG exported by the verified technical-logo-assets catalog", "contributionEvidence": "NVIDIA developed CUDA and the GPUs used in AlexNet training", "stage": "cuda-platform", "rights": {"creator": provenance["source"]["attribution"], "license": "MIT; NVIDIA trademark retained", "licenseUrl": provenance["source"]["licenseUrl"], "credit": "NVIDIA logo: Lobe Icons pinned source; brand remains property of NVIDIA"}})
    request = ROOT / "artifacts/data/media-request.json"
    request.write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    helper = PLUGIN / "line-world-video/scripts/media_assets.py"
    subprocess.run(["uv", "run", "--script", str(helper), "build", "--request", str(request), "--output", str(ROOT / "artifacts/media"), "--png"], check=True)
    for name in ["nvidia.license.txt", "nvidia.provenance.json"]:
        shutil.copyfile(ROOT / "artifacts/sources/logos" / name, ROOT / "artifacts/media/originals" / name)


if __name__ == "__main__":
    main()
