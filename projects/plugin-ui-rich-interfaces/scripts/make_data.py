#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create one deterministic synthetic task shared by all host adapters."""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
RECORDS = [
    ("gateway", "Gateway", "Platform", "healthy", 74, 0.08, 6200, 70, 42),
    ("auth", "Identity", "Platform", "healthy", 51, 0.04, 3800, 265, 42),
    ("api", "Public API", "Platform", "healthy", 112, 0.12, 5140, 70, 156),
    ("orders", "Orders", "Commerce", "watch", 142, 0.31, 1200, 265, 156),
    ("catalog", "Catalog", "Commerce", "healthy", 86, 0.05, 1740, 465, 42),
    ("payments", "Payments", "Commerce", "degraded", 268, 0.84, 920, 465, 156),
    ("search", "Search", "Discovery", "healthy", 176, 0.09, 1120, 665, 42),
    ("cache", "Cache", "Data", "healthy", 12, 0.02, 7400, 665, 156),
    ("postgres", "Primary DB", "Data", "watch", 93, 0.07, 2640, 465, 270),
    ("events", "Events", "Async", "healthy", 38, 0.03, 280, 265, 270),
    ("warehouse", "Warehouse", "Data", "healthy", 221, 0.02, 190, 665, 270),
    ("notifications", "Notifications", "Async", "healthy", 95, 0.03, 90, 70, 270),
]
LINKS = [("gateway","auth",3800,"request"),("gateway","api",5140,"request"),("api","orders",1200,"request"),("api","catalog",1740,"request"),("catalog","search",1120,"request"),("orders","payments",920,"request"),("payments","postgres",920,"request"),("orders","postgres",1200,"request"),("catalog","cache",1740,"request"),("search","cache",1120,"request"),("orders","events",280,"event"),("events","warehouse",190,"event"),("events","notifications",90,"event")]

def main():
    services = []
    for index, (identifier, name, team, status, p95, error, requests, x, y) in enumerate(RECORDS):
        history = []
        for hour in range(24):
            base = p95 * (0.52 + 0.10 * math.sin((hour + index) / 3))
            if status == "degraded" and hour >= 14:
                base += (hour - 13) * 10
            history.append({"hour":hour,"p95":round(base),"error":round(error*(0.45+hour/46),3),"rps":round(requests*(0.65+0.18*math.sin(hour/5)))})
        history[-1].update(p95=p95,error=error,rps=requests)
        services.append({"id":identifier,"name":name,"team":team,"status":status,"p95":p95,"error":error,"rps":requests,"x":x,"y":y,"history":history,"owner":f"{team} on-call"})
    data={"schemaVersion":1,"synthetic":True,"revision":1,"updatedAt":"2026-11-12T00:05:00Z","windowStart":"2026-11-11T00:00:00Z","windowEnd":"2026-11-11T23:00:00Z","services":services,"edges":[{"id":f"{a}-{b}","source":a,"target":b,"rps":v,"kind":k} for a,b,v,k in LINKS],"incidents":[{"id":"INC-024","service":"payments","time":"14:00","severity":"High","title":"Latency above the 250 ms objective","status":"Investigating"},{"id":"INC-023","service":"orders","time":"13:20","severity":"Medium","title":"Queue time increasing","status":"Watching"},{"id":"INC-022","service":"postgres","time":"12:50","severity":"Medium","title":"Connection pool near capacity","status":"Watching"}]}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/observatory.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (ROOT/'web/data.js').write_text('window.SERVICE_DATA = '+json.dumps(data,ensure_ascii=True)+';\n',encoding='utf-8')
    print(f"Created {len(services)} synthetic services, {len(LINKS)} edges, and 24 hourly observations per service.")

if __name__=='__main__':
    main()
