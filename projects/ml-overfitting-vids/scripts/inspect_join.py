#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13"]
# ///
"""Locate exact changed pixels at the draft native-browser join."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json
r=Path(__file__).resolve().parent.parent/'artifacts/images'
a=Image.open(r/'01-generalize.png').convert('RGB');b=Image.open(r/'02-start.png').convert('RGB');d=ImageChops.difference(a,b)
print(json.dumps({'box':d.getbbox(),'mean':ImageStat.Stat(d).mean}));d.save(r/'join-difference.png')
