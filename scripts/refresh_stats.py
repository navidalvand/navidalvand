#!/usr/bin/env python3
"""Refresh the profile's public GitHub repository statistics only."""
import collections
import datetime
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/github-stats.json"
CHART = ROOT / "assets/github-stats.svg"
USER = "navidalvand"

def get_repos():
    page = 1
    repos = []
    while True:
        url = f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "navidalvand-profile"}
        if os.environ.get("GH_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
        with urlopen(Request(url, headers=headers), timeout=25) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Unexpected response from GitHub")
        repos.extend(r for r in batch if r.get("visibility") == "public" and not r.get("private")
                     and r.get("owner", {}).get("login", "").lower() == USER)
        if len(batch) < 100:
            break
        page += 1
    if not repos:
        raise ValueError("No public repositories returned; refusing to erase chart")
    return repos

def summarize(repos):
    langs = collections.Counter(r.get("language") or "Unclassified" for r in repos)
    years = collections.Counter(r["created_at"][:4] for r in repos)
    return {"repositories": len(repos),
            "primary_languages": dict(sorted(langs.items(), key=lambda kv: (-kv[1], kv[0]))),
            "created_by_year": dict(sorted(years.items()))}

def render(data):
    bg, line, white, muted, mint, blue = "#101820", "#344652", "#F1F5F4", "#A9BEC7", "#7DE1C3", "#9CC4FF"
    colors = {"JavaScript": "#E8C66A", "TypeScript": blue, "C": mint, "Unclassified": muted}
    langs = list(data["primary_languages"].items())
    if len(langs) > 6:
        langs = langs[:5] + [("Other", sum(v for _, v in langs[5:]))]
    years = list(data["created_by_year"].items())
    if len(years) > 7:
        years = [(years[0][0] + "-" + years[-7][0], sum(v for _, v in years[:-6]))] + years[-6:]
    bottom = max(335, 123 + 51 * len(langs))
    height = bottom + 55
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" width="900" height="{height}" role="img">',
         '<title>Public GitHub repository statistics</title>',
         f'<rect x="1" y="1" width="898" height="{height-2}" rx="18" fill="{bg}" stroke="{line}" stroke-width="2"/>']
    def text(x,y,value,size=18,color=white,weight=400):
        s.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(value))}</text>')
    def rect(x,y,w,h,color,r=4):
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{color}"/>')
    text(30,37,"PUBLIC CODE / GITHUB SNAPSHOT",16,mint,700)
    text(30,63,f'{data["repositories"]} public repositories',29,white,700)
    text(30,87,"Primary language by repository count",16,muted)
    text(490,87,"Public repositories created by year",16,muted)
    s.append(f'<path d="M455 76V{bottom}" stroke="{line}"/>')
    maximum = max(v for _,v in langs)
    for i,(name,n) in enumerate(langs):
        y = 123 + 51*i
        c = colors.get(name,blue)
        text(30,y,name,17)
        text(400,y,n,17,c,700)
        rect(30,y+10,380,9,line)
        rect(30,y+10,round(380*n/maximum,2),9,c)
    step = 374/len(years)
    baseline = bottom-26
    peak = max(v for _,v in years)
    for i,(year,n) in enumerate(years):
        w = min(50,step-12)
        x = round(490+i*step+(step-w)/2,2)
        h = round((baseline-135)*n/peak,2)
        rect(x,baseline-h,w,h,mint if n==peak else "#597F97",5)
        text(x+4,baseline-h-9,n,17,white,700)
        text(x-2,baseline+23,year,12 if len(years)>5 else 16,muted)
    s.append(f'<path d="M30 {bottom+14}H870" stroke="{line}"/>')
    text(30,bottom+38,data["snapshot_date"]+"  /  Public repository metadata; not commits or language proficiency.",15,muted)
    s.append("</svg>")
    return "\n".join(s)+"\n"

def main():
    snapshot = summarize(get_repos())
    previous = json.loads(DATA.read_text()) if DATA.exists() else {}
    if all(previous.get(k)==v for k,v in snapshot.items()) and CHART.exists():
        print("Public repository statistics unchanged.")
        return
    data = {"snapshot_date": datetime.datetime.now(datetime.timezone.utc).date().isoformat(), **snapshot}
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    CHART.write_text(render(data), encoding="utf-8")
    print("Updated public repository statistics.")

if __name__ == "__main__":
    main()
