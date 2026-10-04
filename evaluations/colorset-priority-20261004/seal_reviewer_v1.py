#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preserve the original independent browser oracle before its documented amendment."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = HERE / "review_browser.py"
target = HERE / "review_browser_v1.py"
if target.exists():
    raise SystemExit("The original reviewer is already sealed; refusing to replace it.")
target.write_bytes(source.read_bytes())
record = {
    "schemaVersion": 1,
    "date": "2026-10-04",
    "originalReviewer": "review_browser_v1.py",
    "originalReviewerSha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "protocolSha256": hashlib.sha256((HERE / "protocol.md").read_bytes()).hexdigest(),
    "amendmentStatus": "post-sampling evaluator repair; original evidence retained",
    "findings": [
        "The naturalistic Mermaid chain prompt did not declare every process node a distinct category; an exact category index per node is unsupported by that prompt.",
        "All eighteen process nodes reuse the primary semantic role. A native same-fill one-pixel stroke has no contrasting decorative rim.",
        "A screen-area cutoff incorrectly rejected scaled mobile bodies. Containing-body qualification must use native geometry area.",
        "Original strict workflow errors remain failures; supplemental semantic review does not change the original literal-slot criterion's recorded result.",
    ],
    "applicationPolicy": "Apply the amended supplemental review to every retained Mermaid naturalistic output; preserve every original report and sampled failure. Keep all explicit indexed-slot/overflow contracts unchanged.",
}
(HERE / "reviewer-amendment.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record))
