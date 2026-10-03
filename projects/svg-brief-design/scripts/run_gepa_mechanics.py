#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "gepa==0.1.2"]
# ///
"""Run the frozen follow-up through the already tested, unchanged GEPA adapter."""
from pathlib import Path
import json
import run_gepa_study as study

if __name__ == "__main__":
    study.STUDY = study.REPO / "evaluations/runs/svg-brief-design-mechanics-20260925"
    protocol = json.loads((study.STUDY / "protocol.json").read_text())
    assert study.digest(Path(__file__)) == protocol["launcher_sha256"]
    study.main()
