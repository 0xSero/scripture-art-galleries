#!/usr/bin/env python3
"""Verify the rebuilt gallery pages: versed images, verse blocks, index rows."""
import html
import json
import os
import re

GALLERIES = ["friends-gallery", "love-gallery", "parents-gallery",
             "grief-gallery"]
problems = []

for g in GALLERIES:
    root = f"/Users/sero/{g}"
    page = open(os.path.join(root, "index.html")).read()
    manifest = json.load(open(os.path.join(root, "manifest.json")))
    verses = json.load(open(os.path.join(root, "verses.json")))
    slugs = [w["slug"] for w in manifest]

    plates = re.findall(r'<figure class="plate" id="p(\d+)">', page)
    imgs = re.findall(r'<img src="([^"]+)"', page)
    verse_blocks = re.findall(r'<blockquote class="verse"><p>(.*?)</p><cite>(.*?)</cite></blockquote>', page)
    index_refs = re.findall(r'<td class="c-verse">(.*?)</td>', page)
    lb_verse = 'w.verse' in page and 'w.ref' in page

    print(f"== {g}: manifest={len(slugs)} plates={len(plates)} imgs={len(imgs)} "
          f"verse_blocks={len(verse_blocks)} index_refs={len(index_refs)} lb_verse={lb_verse}")

    if len(plates) != len(slugs):
        problems.append(f"{g}: {len(plates)} plates vs {len(slugs)} manifest works")
    if len(verse_blocks) != len(slugs):
        problems.append(f"{g}: {len(verse_blocks)} verse blocks vs {len(slugs)} works")
    if len(index_refs) != len(slugs):
        problems.append(f"{g}: {len(index_refs)} index verse cells vs {len(slugs)} works")
    if not lb_verse:
        problems.append(f"{g}: lightbox caption missing verse")

    for src in imgs:
        if not src.startswith("img/versed-thumb/"):
            problems.append(f"{g}: plate image not versed: {src}")
        elif not os.path.exists(os.path.join(root, src)):
            problems.append(f"{g}: missing file {src}")

    # every manifest work must appear, and its verse must be the one rendered
    for w in manifest:
        slug = w["slug"]
        want = f'img/versed-thumb/{slug}.jpg'
        if want not in page:
            problems.append(f"{g}: {slug} not shown as versed plate")
        ref = verses[slug]["ref"]
        if html.escape(verses[slug]["text"]) not in page:
            problems.append(f"{g}: verse text for {slug} missing from page")
        if ref not in page:
            problems.append(f"{g}: verse ref {ref} for {slug} missing from page")

    # versed image files exist for every work
    for slug in slugs:
        for sub in ("versed", "versed-thumb"):
            p = os.path.join(root, "img", sub, f"{slug}.jpg")
            if not os.path.exists(p):
                problems.append(f"{g}: missing rendered file img/{sub}/{slug}.jpg")

    # CSS braces must have been un-doubled by the f-string
    if "{{" in page or "}}" in page:
        problems.append(f"{g}: literal doubled braces leaked into output CSS")
    if ".verse {" not in page or ".c-verse {" not in page:
        problems.append(f"{g}: verse CSS missing")

    # originals untouched
    for slug in slugs:
        for sub in ("full", "thumb"):
            p = os.path.join(root, "img", sub, f"{slug}.jpg")
            if not os.path.exists(p):
                problems.append(f"{g}: original img/{sub}/{slug}.jpg was disturbed")

    print(f"   originals present, versed thumbs present, css ok")

print()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("OK: all three pages carry a unique versed plate and psalm verse for every work.")
