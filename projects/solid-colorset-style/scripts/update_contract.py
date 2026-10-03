#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Publish finite solid-fill ordering and contrast decisions to every bundle."""
import json
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * w for c, w in zip(linear, (.2126, .7152, .0722)))


def readable_text(color):
    value = luminance(color)
    return "#000000" if (value + .05) / .05 >= 1.05 / (value + .05) else "#ffffff"


def merge_contract(existing, canonical):
    result = copy.deepcopy(existing)
    for key, value in canonical.items():
        result[key] = merge_contract(result.get(key, {}), value) if isinstance(value, dict) else copy.deepcopy(value)
    return result


def main():
    source = ROOT / "docs/colorsets.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    document["presentation"] = {
        "default": "solid-fill-no-outline",
        "text": "maximum-black-white-relative-luminance-contrast",
        "excludeFromSolidSequence": "actual-canvas-color",
        "overflow": "only-after-all-usable-solid-fills",
        "overflowChannels": ["border-color", "border-dash", "border-width"],
        "preserve": ["semantic-connectors", "axes", "line-art", "source-fidelity", "explicit-user-style"],
    }
    neutral = ["#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c", "#b5b5b5", "#1c1c1c", "#363636", "#000000", "#cfcfcf", "#e7e7e7"]
    red = ["#9e1b32", "#6d1222", "#e8002a"]
    for name, palette in document["colorsets"].items():
        start = ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a"] if name == "colorset1" else ["#9e1b32", "#007298", "#e77204", "#45842a", "#652f6c", "#f1c319", "#6d1222", "#004d66", "#994a00", "#294d19", "#431f47", "#98700c", "#e8002a", "#00ace6", "#ff9633", "#36b300", "#9e00b3", "#ffd332"]
        tail = ["#ffccd5", "#cdf3ff", "#dbffcc", "#f9ccff", "#ffe5cc", "#fff4cc", "#ffffff", "#f7f7f7"]
        palette["solidSequence"] = list(dict.fromkeys(c for c in start + red + neutral + tail if c in palette["allowed"]))
        assert set(palette["solidSequence"]) == set(palette["allowed"])
        palette["textOnFill"] = {c: readable_text(c) for c in palette["allowed"]}
    rendered = json.dumps(document, indent=2) + "\n"
    source.write_text(rendered, encoding="utf-8")
    copies = list((ROOT / "skills").glob("*/assets/palettes/colorsets.json"))
    for target in copies:
        existing = json.loads(target.read_text(encoding="utf-8"))
        target.write_text(json.dumps(merge_contract(existing, document), indent=2) + "\n", encoding="utf-8")
    print(f"Updated canonical style policy and {len(copies)} independent palette copies.")


if __name__ == "__main__":
    main()
