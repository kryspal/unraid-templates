#!/usr/bin/env python3
"""Replace the <Changes> block of templates/kryspal-media.xml with the highlights of one release.

Usage: scripts/set-changes.py --version 0.9.18 --date 2026-11-23 --notes deploy/release/notes/0.9.18.md

The notes file is the main project's release notes: this script reads the "## Highlights (en)" bullets and nothing else.
Only the latest version is kept, in the format Community Applications shows as the change log.
"""
import argparse
import re
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--version", required=True)
ap.add_argument("--date", required=True)
ap.add_argument("--notes", required=True)
ap.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "templates" / "kryspal-media.xml"))
a = ap.parse_args()

notes = Path(a.notes).read_text(encoding="utf-8")
m = re.search(r"^## Highlights \(en\)\n(.*?)(?=^## |\Z)", notes, re.S | re.M)
bullets = [l.strip() for l in (m.group(1) if m else "").splitlines() if l.strip().startswith("- ")]
if not bullets:
    sys.exit("error: no English highlights found in " + a.notes)
if any(re.search(r"[\u3400-\u9fff]", b) for b in bullets):
    sys.exit("error: the highlights must be English only")
body = "\n".join(bullets).replace("]]>", "]]]]><![CDATA[>")
block = f"  <Changes><![CDATA[\n### {a.version} ({a.date})\n{body}\n]]></Changes>\n"

p = Path(a.template)
xml = p.read_text(encoding="utf-8")
if "<Changes>" in xml:
    xml = re.sub(r"[ \t]*<Changes>.*?</Changes>\n", lambda _: block, xml, count=1, flags=re.S)
else:
    xml = re.sub(r"(  <Requires>.*?</Requires>\n)", lambda mm: mm.group(1) + block, xml, count=1, flags=re.S)
    if block not in xml:
        sys.exit("error: could not find <Requires> to place <Changes> after")
p.write_text(xml, encoding="utf-8")
print("updated", p)
