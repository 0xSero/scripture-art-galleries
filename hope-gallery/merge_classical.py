#!/usr/bin/env python3
"""Merge the classical art the team found into the gallery selection.

The two finders wrote one JSON list each, shaped like a works.py record. This gives
every entry a slug, a section and a blurb, and appends it to the reviewed selection so
the ordinary pipeline downloads, sets a line and renders it.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SELECTION = os.environ.get("HOPE_SELECTED", "/tmp/hope3-selected-reviewed.json")
SOURCES = ["classical-flowers.json", "classical-light.json"]

SECTION = "VIII"
TITLE = "The old light — painting before the moderns"
BLURB = ("The paintings the moderns were arguing with. Flowers, fruit, dawn and water, "
         "made by hand three hundred years before the picture was broken into facets, "
         "and still the plainest argument for looking at the light.")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:40] or "work"


def main():
    selection = json.load(open(SELECTION))
    seen = {w["slug"] for w in selection}
    seen_files = {w["file_title"] for w in selection}
    added = 0
    for name in SOURCES:
        path = os.path.join(BASE, name)
        if not os.path.exists(path):
            print(f"  {name}: not written yet, skipped")
            continue
        rows = json.load(open(path))
        for i, w in enumerate(rows):
            file_title = w["file"].strip()
            if file_title in seen_files:
                continue
            surname = w["artist"].split()[-1] if w.get("artist") else ""
            slug = slugify(surname + " " + (w.get("title") or ""))
            n, base = 2, slug
            while slug in seen:
                slug = f"{base}-{n}"
                n += 1
            seen.add(slug)
            seen_files.add(file_title)
            year = None
            m = re.search(r"(1[5-9]\d\d|20[0-2]\d)", w.get("date") or "")
            if m:
                year = int(m.group(1))
            selection.append(dict(
                section=SECTION, section_title=TITLE, blurb=BLURB, slug=slug,
                artist=w.get("artist", ""), title=w.get("title", ""),
                date=w.get("date", ""), medium=w.get("medium", ""),
                institution=w.get("institution", ""), dimensions="",
                source="https://commons.wikimedia.org/wiki/" + file_title.replace(" ", "_"),
                file_title=file_title, score=len(rows) - i, year=year,
                categories=[w.get("why", "")]))
            added += 1
    json.dump(selection, open(SELECTION, "w"), ensure_ascii=False, indent=1)
    print(f"{added} classical works added, {len(selection)} in the selection now")


if __name__ == "__main__":
    main()
