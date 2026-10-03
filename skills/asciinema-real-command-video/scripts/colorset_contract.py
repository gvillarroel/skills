#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve exact colorset tokens without depending on another skill."""
import json
from pathlib import Path


def tokens(mode: str) -> tuple[str, ...]:
    source = Path(__file__).resolve().parent.parent / "assets/palettes/colorsets.json"
    return tuple(json.loads(source.read_text(encoding="utf-8"))["colorsets"][mode]["allowed"])


def colors(mode: str) -> tuple[tuple[int, int, int], ...]:
    return tuple(tuple(int(token[i:i + 2], 16) for i in (1, 3, 5)) for token in tokens(mode))


def nearest(color: tuple[int, int, int], mode: str) -> tuple[int, int, int]:
    return min(colors(mode), key=lambda item: sum((a - b) ** 2 for a, b in zip(item, color)))
