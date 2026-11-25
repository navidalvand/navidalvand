#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys
import xml.etree.ElementTree as ET

root=Path(sys.argv[1]).resolve()
class Check(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k not in ("src","href") or not v:
                continue
            u=urlsplit(v)
            if not u.scheme and not u.netloc and u.path:
                path=(root/unquote(u.path)).resolve()
                assert path.is_relative_to(root) and path.exists(), f"Missing or unsafe local path: {v}"
Check().feed((root/"index.html").read_text())
for f in (root/"assets").glob("*.svg"):
    ET.parse(f)
data=json.loads((root/"assets/activity.json").read_text())
assert data["total_commits"]==sum(data["days"].values())
assert data["active_days"]==len(data["days"])
print("Portfolio paths, SVG XML, and activity counts verified.")
