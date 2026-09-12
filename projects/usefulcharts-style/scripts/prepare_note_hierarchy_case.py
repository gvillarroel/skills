#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare development cases for paragraph hierarchy and illustration ownership."""

import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[3]
prompts=root/'evaluations/pi-prompts'
original=(prompts/'usefulcharts-contextual-art.md').read_text(encoding='utf-8')
original=original.replace('# Naturalistic case: contextual illustration composition','# Naturalistic case: note hierarchy and illustration ownership')
request='Use short running paragraphs for ordinary events: emphasize the lead-in and let the explanation continue on the same line when it fits. Give the coastal convention, the ridge railway and the civic charter separate prominent headings. Check each picture beside its preceding and following events; the clock must clearly explain the 1820 schools, not the 1808 harbor survey. Keep every image with its own explanation, without moving the numeric date. '
original=original.replace('Create these exact files:',request.rstrip()+'\n\nCreate these exact files:')
(prompts/'usefulcharts-note-hierarchy.md').write_text(original,encoding='utf-8')
control=(prompts/'usefulcharts-contextual-art-contract.md').read_text(encoding='utf-8')
data=json.loads(re.search(r'```json\s*(.*?)\s*```',control,re.S).group(1))
data['id']='note-hierarchy-contract'
data['events'].insert(0,dict(id='previous',lane='region',year=1820,label='Earlier harbor survey',detail='Pilots mark the safe channels.',size=18,detail_size=15,text_layout='paragraph'))
for event in data['events']:
    if event['id']!='bridge':event['text_layout']='paragraph'
    if event['id']=='clock':event['art_position']='auto'
control=re.sub(r'```json\s*.*?\s*```','```json\n'+json.dumps(data,ensure_ascii=False)+'\n```',control,flags=re.S)
control=control.replace('# Exact command contract: dated illustration arrangements','# Exact command contract: mixed paragraphs and automatic illustration ownership')
control=control.replace('Preserve all fields except the event offsets and widths assigned by the helper.','Preserve all fields except the event offsets and widths assigned by the helper, and resolve the clock\'s automatic image position. Explicit image positions must stay unchanged.')
(prompts/'usefulcharts-note-hierarchy-contract.md').write_text(control,encoding='utf-8')
print('Prepared two development prompts while retaining the supplied regional history.')
