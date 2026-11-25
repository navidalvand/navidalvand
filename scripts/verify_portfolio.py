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
def parse_svg(path):
    try:
        tree=ET.parse(path)
    except ET.ParseError as error:
        raise SystemExit(f"Invalid SVG {path.relative_to(root)}: {error}") from error
    if not tree.getroot().tag.endswith("svg"):
        raise SystemExit(f"Not an SVG: {path.relative_to(root)}")
    return tree

for f in sorted((root/"assets").rglob("*.svg")):
    parse_svg(f)
data=json.loads((root/"assets/activity.json").read_text())
assert data["total_commits"]==sum(data["days"].values())
assert data["active_days"]==len(data["days"])
print("Portfolio paths, SVG XML, and activity counts verified.")

# Validate the shared skills catalog and every individual icon.
skills=json.loads((root/"assets/skills.json").read_text(encoding="utf-8"))
assert skills["schema_version"]==1
ids=set()
groups=set()
for group in skills["categories"]:
    assert group["id"] not in groups and group["skills"]
    groups.add(group["id"])
    for skill in group["skills"]:
        assert skill["id"] not in ids
        ids.add(skill["id"])
        assert skill["experience"] in skills["experience_labels"]
        assert skill["name"] and skill["description"]
        assert skill["icon_kind"] in ("devicon","simple-icons","custom")
        icon=(root/skill["icon"]).resolve()
        assert icon.is_relative_to(root) and icon.suffix==".svg" and icon.is_file(), skill["icon"]
        tree=parse_svg(icon)
        assert tree.getroot().tag.endswith("svg"), skill["icon"]
print(f"Verified {len(ids)} skills across {len(groups)} disciplines and every SVG icon.")
