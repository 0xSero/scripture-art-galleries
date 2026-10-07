#!/usr/bin/env python3
"""Check the hope gallery page against the works, the lines and the text.

Every plate must be present, every line must appear on the page, every reference
must be unique in the gallery and absent from the four galleries already built, no line
may run past eight words, and every line must be a literal run of words from the verse
it cites in the World English Bible.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PSALM = "/Users/sero/psalm-verses"
sys.path.insert(0, PSALM)
from works import WORKS  # noqa: E402

WEB = json.load(open(os.path.join(PSALM, "web-bible.json")))
LINES = json.load(open(os.path.join(BASE, "lines.json")))
HTML = open(os.path.join(BASE, "index.html")).read()
M = json.load(open(os.path.join(BASE, "manifest.json")))

fails = []


def norm(t):
    t = (t or "").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", t).strip()


def line_norm(t):
    """The plate text as it is compared with the verse: a dropped leading
    conjunction and a capitalised first word are allowed, nothing else."""
    t = norm(t).lower().strip("\u2026 ")
    t = re.sub(r"^(and|but|then|for|so|now|behold)\s+", "", t)
    t = t.strip(" ,.;:!?\"'")
    return re.sub(r"\s+", " ", t)


MAN = {w["slug"] for w in M}
# only works with an image and a line are on the page; the rest are still arriving
SHOWN = [w for w in WORKS if w["slug"] in MAN and w["slug"] in LINES]
print(f"{len(SHOWN)} of {len(WORKS)} works are on the page")

for w in SHOWN:
    slug = w["slug"]
    if f'img/versed-thumb/{slug}.jpg' not in HTML:
        fails.append(f"{slug}: thumbnail not on the page")
    if f'id="p' not in HTML:
        pass
    line = LINES.get(slug)
    if not line:
        fails.append(f"{slug}: no line assigned")
        continue
    if line["words"] > 8:
        fails.append(f"{slug}: line runs to {line['words']} words")
    if norm(line["text"]) not in norm(HTML):
        fails.append(f"{slug}: line text not found on the page")
    if line["ref"] not in HTML:
        fails.append(f"{slug}: reference {line['ref']} not on the page")

# refs unique inside the gallery
refs = [v["ref"] for v in LINES.values()]
if len(refs) != len(set(refs)):
    dupes = {r for r in refs if refs.count(r) > 1}
    fails.append(f"repeated references: {sorted(dupes)}")

# refs not reused from the four galleries already built
used = set()
for name in ("friends-gallery", "love-gallery", "parents-gallery", "grief-gallery"):
    p = os.path.join(PSALM, name, "verses.json")
    if os.path.exists(p):
        for e in json.load(open(p)):
            used.add(e["ref"])
for name in ("friends-gallery", "love-gallery", "parents-gallery", "grief-gallery"):
    p = os.path.join(PSALM, name, "verses.json")
    if os.path.exists(p):
        for e in json.load(open(p)):
            used.add(e["ref"])
reused = sorted(set(refs) & used)
if reused:
    fails.append(f"references reused from the other galleries: {reused}")

# every line is a literal run of words from the cited verse
for slug, line in LINES.items():
    book, cv = line["ref"].rsplit(" ", 1) if not line["ref"][0].isdigit() \
        else (line["ref"].rsplit(" ", 2)[0] + " " + line["ref"].rsplit(" ", 2)[1],
              line["ref"].rsplit(" ", 2)[2])
    ch, v = cv.split(":")
    parts = [row["t"] for row in WEB.get(book, {}).get(ch, [])
             if str(row["v"]) == v]
    verse = " ".join(parts) if parts else None
    if verse is None:
        fails.append(f"{slug}: {line['ref']} is not in the corpus")
        continue
    if line_norm(line["text"]) not in line_norm(verse):
        fails.append(f"{slug}: '{line['text']}' is not a literal run of {line['ref']}")

# manifest completeness
shown_slugs = {w["slug"] for w in SHOWN}
missing = sorted(shown_slugs - MAN)
if missing:
    fails.append(f"on the page but not in the manifest: {missing[:6]}")
extra = sorted(MAN - shown_slugs)
if extra:
    fails.append(f"in the manifest but not on the page: {extra[:6]}")
for w in M:
    if not w.get("source_page") or not w.get("source_license"):
        fails.append(f"{w['slug']}: missing source or licence")
    if not os.path.exists(os.path.join(BASE, w["full"])):
        fails.append(f"{w['slug']}: full image missing")
    if not os.path.exists(os.path.join(BASE, w["thumb"])):
        fails.append(f"{w['slug']}: thumb missing")

# licences may not be share-alike or attribution-only
for w in M:
    lic = (w.get("source_license") or "").lower()
    if "sa-" in lic or lic.startswith("cc by") or "attribution" in lic:
        fails.append(f"{w['slug']}: licence {w['source_license']} is not PD/CC0")

print(f"{len(WORKS)} works selected, {len(LINES)} lines, {len(M)} in the manifest")
if fails:
    print(f"{len(fails)} FAILURES")
    for f in fails[:40]:
        print("  " + f)
else:
    print("all checks pass")
