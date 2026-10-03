#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Theme and recolor the presentation cast while preserving recording evidence."""
import json
import argparse
import hashlib
import re
from pathlib import Path
from colorset_contract import nearest

ANSI = {
    "colorset1": ("1c1c1c", "9e1b32", "4f4f4f", "6d1222", "333e48", "9e1b32", "696969", "e7e7e7", "828282", "e8002a", "b5b5b5", "9c9c9c", "cfcfcf", "6d1222", "9c9c9c", "ffffff"),
    "colorset2": ("1c1c1c", "9e1b32", "45842a", "98700c", "007298", "652f6c", "004d66", "e7e7e7", "828282", "e8002a", "36b300", "f1c319", "00ace6", "9e00b3", "cdf3ff", "ffffff"),
}
SGR = re.compile(r"\x1b\[([0-9;:]*)m")
OSC_PAINT = re.compile(r"\x1b\](?:4|10|11|12|104|110|111|112)(?:;[^\x07\x1b]*)?(?:\x07|\x1b\\)")


def agg_theme(mode: str) -> str:
    return ",".join(("f7f7f7", "333e48", *ANSI[mode]))


def indexed_rgb(index: int) -> tuple[int, int, int]:
    if index < 16:
        standard = ("000000", "800000", "008000", "808000", "000080", "800080", "008080", "c0c0c0", "808080", "ff0000", "00ff00", "ffff00", "0000ff", "ff00ff", "00ffff", "ffffff")
        return tuple(int(standard[index][i:i + 2], 16) for i in (0, 2, 4))
    if index >= 232:
        value = 8 + 10 * (index - 232)
        return (value, value, value)
    value = index - 16
    ramp = (0, 95, 135, 175, 215, 255)
    return (ramp[value // 36], ramp[(value // 6) % 6], ramp[value % 6])


def recolor_sgr(text: str, mode: str) -> str:
    def replace(match: re.Match[str]) -> str:
        # Colon-form truecolor allows an empty optional color-space field.
        raw = re.sub(r"(38|48|58):2:(?:[0-9]*:)?([0-9]+):([0-9]+):([0-9]+)", r"\1;2;\2;\3;\4", match[1]).replace(":", ";")
        parts = raw.split(";")
        output, index = [], 0
        while index < len(parts):
            token = parts[index]
            if token in {"38", "48", "58"} and index + 2 < len(parts):
                if parts[index + 1] == "2":
                    start = index + 2
                    if parts[start] == "":
                        start += 1
                    channels = parts[start:start + 3]
                    if len(channels) == 3 and all(v.isdigit() and 0 <= int(v) <= 255 for v in channels):
                        color = nearest(tuple(map(int, channels)), mode)
                        output.extend((token, "2", *(str(v) for v in color)))
                        index = start + 3
                        continue
                elif parts[index + 1] == "5" and parts[index + 2].isdigit() and 0 <= int(parts[index + 2]) <= 255:
                    color = nearest(indexed_rgb(int(parts[index + 2])), mode)
                    output.extend((token, "2", *(str(v) for v in color)))
                    index += 3
                    continue
            output.append(token)
            index += 1
        return "\x1b[" + ";".join(output) + "m"
    return SGR.sub(replace, OSC_PAINT.sub("", text))


def write_presentation_cast(source: Path, target: Path, mode: str) -> None:
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    records[0]["theme"] = {"bg": "#f7f7f7", "fg": "#333e48", "palette": ":".join("#" + v for v in ANSI[mode])}
    pending = ""
    final_output = None
    for event in records[1:]:
        if isinstance(event, list) and len(event) >= 3 and event[1] == "o" and isinstance(event[2], str):
            text = pending + event[2]
            pending = ""
            escape_start = text.rfind("\x1b")
            if escape_start >= 0:
                tail = text[escape_start:]
                if re.fullmatch(r"\x1b(?:\[[0-9;:]*|\][^\x07]*)?", tail):
                    text, pending = text[:escape_start], tail
            event[2] = recolor_sgr(text, mode)
            final_output = event
    if pending and final_output is not None:
        final_output[2] += pending
    target.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--colorset", choices=tuple(ANSI), default="colorset1")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if len({args.source.resolve(), args.target.resolve(), args.report.resolve()}) != 3:
        parser.error("Source, target and report paths must be distinct.")
    original = args.source.read_bytes()
    write_presentation_cast(args.source, args.target, args.colorset)
    before = [json.loads(line) for line in original.decode("utf-8").splitlines() if line and not line.startswith("#")]
    after = [json.loads(line) for line in args.target.read_text(encoding="utf-8").splitlines() if line]
    assert len(before) == len(after), "Event count changed"
    assert {key: value for key, value in after[0].items() if key != "theme"} == {key: value for key, value in before[0].items() if key != "theme"}, "Non-theme header data changed"
    assert all(a[:2] == b[:2] for a, b in zip(before[1:], after[1:])), "Event timing/type changed"
    assert original == args.source.read_bytes(), "Original cast changed"
    report = {"colorset": args.colorset, "aggTheme": agg_theme(args.colorset), "sourceSha256": hashlib.sha256(original).hexdigest(), "sourceUnchanged": True, "eventCount": len(after) - 1, "eventTimingPreserved": True, "presentationHeaderThemeReplaced": True}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
