#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract public authored blog records without changing the source repository."""
from pathlib import Path
import hashlib
import json
import re

BLOG=Path('C:/Users/villa/dev/blog')
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/data'
FILES={
    'architecture':'src/content/posts/ai-architecture-old-ideas-new-probability.md',
    'evaluation':'src/content/posts/from-benchmarks-to-skill-evolution.md',
    'agent-context':'knowledge/public/agent-systems/context.md',
    'agent-skills':'knowledge/public/agent-systems/skills.md',
    'agent-harnesses':'knowledge/public/agent-systems/harnesses.md',
    'agent-overview':'knowledge/public/agent-systems/README.md',
}


def plain(value):
    value=re.sub(r'!\[([^\]]*)\]\[[^\]]+\]',r'\1',value)
    value=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',value)
    return re.sub(r'[*`]', '', value).strip()


def tables(text):
    result=[];current=None;heading='';fence=False
    for number,line in enumerate(text.splitlines(),1):
        if line.startswith('```'):fence=not fence
        if fence:continue
        if line.startswith('#'):heading=line.lstrip('# ')
        if line.startswith('|'):
            cells=[c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.fullmatch(r'[: -]+',c or '-') for c in cells):continue
            if current is None:
                current=dict(heading=heading,line=number,headers=[plain(c) for c in cells],rows=[])
            else:
                current['rows'].append(dict(cells=[plain(c) for c in cells],markdown_cells=cells,
                    urls=re.findall(r'https?://[^\s)]+',line),line=number))
        elif current is not None:
            result.append(current);current=None
    if current:result.append(current)
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True);sources=[];all_tables={}
    for ident,relative in FILES.items():
        path=BLOG/relative;raw=path.read_bytes();text=raw.decode('utf-8')
        front=text.split('---',2)[1] if text.startswith('---') else ''
        title=re.search(r'^title:\s*"?([^\n]+?)"?$',front,re.M)
        dates=dict(re.findall(r'^(pubDate|updatedDate):\s*(\S+)',front,re.M))
        authors=re.search(r'^authors:\n((?:\s+-[^\n]+\n)+)',front,re.M)
        sources.append(dict(id=ident,path=relative,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),title=title.group(1) if title else None,authors=re.findall(r'-\s*(.+)',authors.group(1)) if authors else [],dates=dates))
        all_tables[ident]=tables(text)
        if ident=='architecture':
            charts=[json.loads(s) for s in re.findall(r'```d3\s*\n(.*?)\n```',text,re.S)]
            heatmap=next(c for c in charts if c['type']=='annual-milestone-heatmap')
            assert len(heatmap['data'])==60
            records=[]
            for i,row in enumerate(heatmap['data'],1):
                records.append(dict(id=f'history-{i:02d}',**row))
            (OUT/'milestones.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (OUT/'source-tables.json').write_text(json.dumps(all_tables,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (OUT/'sources.json').write_text(json.dumps(dict(source_repository=str(BLOG),selection='Two published articles and the authored public agent-systems knowledge collection. Private books, private retrieval text, unrelated output folders and the stale LangChain draft are outside this display.',files=sources),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(milestones=60,sources=len(sources),tables={key:[dict(index=i,heading=t['heading'],rows=len(t['rows'])) for i,t in enumerate(value)] for key,value in all_tables.items()})))


if __name__=='__main__':main()
