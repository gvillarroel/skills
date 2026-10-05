#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Interleave existing CS1 categorical neutrals without changing paint values."""
from pathlib import Path
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[3]
NEUTRALS = {
    "#000000", "#1c1c1c", "#363636", "#333e48", "#4f4f4f", "#696969",
    "#828282", "#9c9c9c", "#b5b5b5", "#cfcfcf", "#e7e7e7", "#f7f7f7",
}
PRIORITY = ["primary-red", "grays", "white", "remaining-colors"]


def luminance(token):
    channels = [int(token[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * w for c, w in zip(linear, (.2126, .7152, .0722)))


def lightness(token):
    """CIE lightness from D65-relative sRGB luminance; not full color distance."""
    y = luminance(token)
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else (24389 / 27) * y


def metrics(order):
    grays = [token for token in order if token in NEUTRALS]
    gaps = [abs(lightness(a) - lightness(b)) for a, b in zip(grays, grays[1:])]
    contrasts = [(max(luminance(a), luminance(b)) + .05) / (min(luminance(a), luminance(b)) + .05)
                 for a, b in zip(grays, grays[1:])]
    return {"neutralOrder": grays, "lightnessGaps": gaps,
            "minimumLightnessGap": min(gaps), "maximumLightnessGap": max(gaps),
            "meanLightnessGap": statistics.mean(gaps), "gapStandardDeviation": statistics.pstdev(gaps),
            "minimumAdjacentNeutralContrast": min(contrasts)}


def main():
    sorted_grays = sorted(NEUTRALS, key=luminance)
    half = (len(sorted_grays) + 1) // 2
    interleaved = [token for pair in zip(sorted_grays[:half], sorted_grays[half:]) for token in pair]
    order = ["#9e1b32", *interleaved, "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]
    paths = [ROOT / "docs/colorsets.json", *sorted((ROOT / "skills").glob("*/assets/palettes/colorsets.json"))]
    records = []
    before_order = None
    for path in paths:
        before = path.read_bytes()
        payload = json.loads(before)
        old = json.loads(before)
        row = payload["colorsets"]["colorset1"]
        if set(order) != set(row["allowed"]) or len(order) != len(row["allowed"]):
            raise ValueError(f"Unexpected CS1 token membership: {path.relative_to(ROOT)}")
        if before_order is None:
            before_order = row["solidSequence"].copy()
        row["sequence"] = order.copy()
        row["solidSequence"] = order.copy()
        row["categoryPriority"] = PRIORITY.copy()
        assert payload["colorsets"]["colorset2"] == old["colorsets"]["colorset2"]
        for key, value in old["colorsets"]["colorset1"].items():
            if key not in {"sequence", "solidSequence", "categoryPriority"}:
                assert row[key] == value, (path, key)
        after = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
        path.write_bytes(after)
        records.append({"path": path.relative_to(ROOT).as_posix(),
                        "beforeSha256": hashlib.sha256(before).hexdigest(),
                        "afterSha256": hashlib.sha256(after).hexdigest(),
                        "cs2AndOtherCs1ValuesUnchanged": True})
    report = ROOT / "projects/grayscale-interleave/artifacts/manifests/palette-update.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"order": order, "priority": PRIORITY, "count": len(records),
                                 "before": metrics(before_order), "after": metrics(order),
                                 "metricSource": "https://www.w3.org/TR/css-color-4/#color-conversion-code",
                                 "records": records}, indent=2) + "\n", encoding="utf-8")
    print(f"Updated CS1 categorical order in {len(records)} contracts; paint tokens, roles, text choices and CS2 are unchanged.")


if __name__ == "__main__":
    main()
