#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate primary-red attention, quantitative points and semantic category paint."""
import copy
import json
import math
from pathlib import Path

PRIMARY_RED='#9e1b32'
DEFAULT_ATTENTION={'guideColor':PRIMARY_RED,'baseRadius':9,'travelRadius':6,'focusRadius':22,'emitRadius':32,'pointRadius':4.5,'emissionSeconds':.34,'flightSeconds':.55,'unitPerPoint':None,'categoryColors':{},'emissionViews':['network','circle-pack','donut']}


def validate_attention(story):
    supplied=story.get('attention',{})
    if not isinstance(supplied,dict) or set(supplied)-set(DEFAULT_ATTENTION):raise ValueError('attention must contain supported choreography fields.')
    config={**copy.deepcopy(DEFAULT_ATTENTION),**copy.deepcopy(supplied)}
    if config['guideColor']!=PRIMARY_RED:raise ValueError('The guide must use primary red #9e1b32.')
    for key in ('baseRadius','travelRadius','focusRadius','emitRadius','pointRadius','emissionSeconds','flightSeconds'):
        value=config[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:raise ValueError(f'attention.{key} must be finite and positive.')
    if not config['travelRadius']<=config['baseRadius']<=config['focusRadius']<=config['emitRadius']<=64:raise ValueError('Require travelRadius <= baseRadius <= focusRadius <= emitRadius <=64.')
    if config['pointRadius']>12 or max(config['emissionSeconds'],config['flightSeconds'])>3:raise ValueError('Data-point radius must be <=12 and motion intervals <=3 seconds.')
    unit=config['unitPerPoint']
    if unit is not None and (isinstance(unit,bool) or not isinstance(unit,(int,float)) or not math.isfinite(unit) or unit<=0):raise ValueError('unitPerPoint must be positive or null for automatic scaling.')
    if unit and any(math.ceil(r['after']/unit-1e-10)>64 for r in story['rows']):raise ValueError('Choose a larger unitPerPoint; at most 64 points per entity.')
    colors=config['categoryColors'];ids={r['id'] for r in story['rows']}
    if not isinstance(colors,dict) or set(colors)-ids:raise ValueError('categoryColors must map existing entity IDs to exact palette colors.')
    if colors:
        if story['palette']!='colorset2' or not story.get('paletteReason','').strip():raise ValueError('Semantic category-point colors require colorset2 and a paletteReason.')
        palettes=json.loads((Path(__file__).resolve().parent.parent/'assets/palettes/colorsets.json').read_text(encoding='utf-8'))
        allowed=set(palettes['colorsets']['colorset2']['allowed'])-{'#9e1b32','#e8002a','#ffffff'}
        if any(not isinstance(c,str) or c not in allowed for c in colors.values()) or len(set(colors.values()))!=len(colors):raise ValueError('Use distinct allowed category colors; reserve primary red for the guide.')
    if not isinstance(config['emissionViews'],list) or any(v not in ('network','circle-pack','donut') for v in config['emissionViews']):raise ValueError('emissionViews supports network, circle-pack and donut.')
    story['attention']=config
    return story
