#!/usr/bin/env python3
"""Public, author-matched default-branch commit calendar; not GitHub contribution totals."""
import collections
import datetime as dt
import json
import html
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
import os
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"
USER="navidalvand"
SCOPE="Author-matched default-branch commits in public repositories owned by navidalvand; deduplicated by SHA. Not GitHub's full contribution graph."
COLORS=["#253641","#326958","#469A80","#7DE1C3","#B2F5DD"]
def pages(path, params):
    page=1
    while True:
        query=urlencode(dict(params,per_page=100,page=page))
        headers={"Accept":"application/vnd.github+json","User-Agent":"navidalvand-public-activity"}
        if os.environ.get("GH_TOKEN"):
            headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
        with urlopen(Request("https://api.github.com"+path+"?"+query,headers=headers),timeout=25) as r:
            batch=json.load(r)
        if not isinstance(batch,list):
            raise ValueError("Unexpected GitHub API response")
        yield from batch
        if len(batch)<100:
            break
        page+=1
def collect():
    end=dt.datetime.now(dt.timezone.utc).date()
    start=end-dt.timedelta(days=364)
    repos=[r for r in pages("/users/"+USER+"/repos",{"type":"owner"}) if not r.get("private") and r.get("visibility")=="public" and r.get("owner",{}).get("login","").lower()==USER]
    if not repos:
        raise ValueError("No public repositories; retaining last snapshot")
    seen=set()
    counts=collections.Counter()
    for repo in repos:
        if repo.get("size")==0:
            continue
        path="/repos/"+USER+"/"+quote(repo["name"],safe="")+"/commits"
        params={"author":USER,"sha":repo["default_branch"],"since":str(start)+"T00:00:00Z","until":str(end)+"T23:59:59Z"}
        for commit in pages(path,params):
            if (commit.get("author") or {}).get("login","").lower()!=USER:
                continue
            sha=commit["sha"]
            day=commit["commit"]["author"]["date"][:10]
            if sha not in seen and str(start)<=day<=str(end):
                counts[day]+=1
                seen.add(sha)
    return {"start":str(start),"end":str(end),"public_repositories_scanned":len(repos),"total_commits":sum(counts.values()),"active_days":len(counts),"days":dict(sorted(counts.items())),"scope":SCOPE}
def text(x,y,s,size=16,color="#A9BEC7",weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(s))}</text>'
def frame(h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}" role="img"><title>{title}</title><rect x="1" y="1" width="898" height="{h-2}" rx="18" fill="#101820" stroke="#344652" stroke-width="2"/>{body}</svg>\n'
def render(data):
    start=dt.date.fromisoformat(data["start"])
    offset=start.weekday()
    cells=[]
    blocks=[]
    for i in range(365):
        day=str(start+dt.timedelta(days=i))
        count=data["days"].get(day,0)
        week,d=divmod(i+offset,7)
        x,y=40+week*15.5,99+d*15.5
        c=COLORS[min(count,4)]
        label=f"<title>{day}: {count} commits</title>"
        cells.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{c}">{label}</rect>')
        bx,by=44+week*14.1+d*7.4,179-week*1.4+d*10
        h=10+min(55,count*9) if count else 0
        sides=f'<path d="M{bx} {by-h}l8 4v{h}l-8 -4z" fill="#326958"/><path d="M{bx+8} {by-h+4}l8 -4v{h}l-8 4z" fill="#469A80"/>' if h else ""
        blocks.append(f'<g>{label}<path d="M{bx} {by-h}l8 -4 8 4 -8 4z" fill="{c}"/>{sides}</g>')
    metric=f'{data["total_commits"]} commits   ·   {data["active_days"]} active days   ·   {data["public_repositories_scanned"]} public repos'
    scan='<style>.scan{animation:scan 3s ease-out 1;opacity:0}@keyframes scan{0%{transform:translateX(0);opacity:.65}100%{transform:translateX(817px);opacity:0}}@media(prefers-reduced-motion:reduce){.scan{display:none}}</style>'
    fade='<style>.sky{animation:fade 1.2s ease-out 1}@keyframes fade{from{opacity:.2}to{opacity:1}}@media(prefers-reduced-motion:reduce){.sky{animation:none}}</style>'
    heat=frame(263,"Public commit activity, 365 days",scan+text(30,35,"PUBLIC COMMIT ACTIVITY / 365 DAYS",16,"#7DE1C3",700)+text(30,68,metric,26,"#F1F5F4",700)+"".join(cells)+'<rect class="scan" x="40" y="95" width="6" height="112" rx="3" fill="#B2F5DD"/>'+text(40,231,data["start"],15)+text(733,231,data["end"],15)+text(40,250,"Public owned repositories / author-matched default-branch commits only",13))
    terrain=frame(280,"Isometric public commit activity",fade+text(30,35,"ACTIVITY TERRAIN / ISOMETRIC VIEW",16,"#7DE1C3",700)+text(30,63,"Height represents daily public commits (capped)",19,"#F1F5F4",700)+'<g class="sky">'+"".join(blocks)+"</g>"+text(30,265,data["start"]+" — "+data["end"]+" / Same data as calendar; not private contributions.",14))
    for content in (heat,terrain):
        ET.fromstring(content)
    return heat,terrain
def main():
    data=collect()
    heat,terrain=render(data)
    for path,content in [(ASSETS/"activity.json",json.dumps(data,indent=2)+"\n"),(ASSETS/"activity-heatmap.svg",heat),(ASSETS/"activity-3d.svg",terrain)]:
        if not path.exists() or path.read_text(encoding="utf-8")!=content:
            path.write_text(content,encoding="utf-8")
if __name__=="__main__":
    main()
