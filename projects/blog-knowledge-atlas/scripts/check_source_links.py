#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check known public source URLs without changing the source repository."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
URLS=[
    'https://gvillarroel.github.io/blog/posts/ai-architecture-old-ideas-new-probability/',
    'https://gvillarroel.github.io/blog/posts/from-benchmarks-to-skill-evolution/',
    'https://github.com/gvillarroel/blog/blob/main/knowledge/public/agent-systems/context.md',
    'https://agentskills.io/specification',
    'https://www.anthropic.com/engineering/building-effective-agents',
    'https://www.harborframework.com/docs/run-jobs/skills',
    'https://arxiv.org/abs/2507.19457',
]
def check(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (source-link validation)'})
        with urllib.request.urlopen(req,timeout=25) as response:
            return dict(url=url,status=response.status,final_url=response.url)
    except Exception as error:
        return dict(url=url,error=str(error))
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(check,URLS))
    (ROOT/'artifacts/reviews/source-links.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
