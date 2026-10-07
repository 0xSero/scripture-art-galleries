#!/usr/bin/env python3
"""Validate the curated verse assignment against the fetched KJV corpora.

The friends and love galleries are built from the Psalms corpus (bible-api.com).
The parents gallery draws its lines from the whole Bible, so its references name a
book and resolve in the whole-Bible corpus. Every line on a parents plate must be
a literal contiguous run of words from its verse and at most ten words.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
PSALMS = json.load(open(os.path.join(BASE, "kjv-psalms.json")))
BIBLE = json.load(open(os.path.join(BASE, "kjv-bible.json")))
ASSIGN = json.load(open(os.path.join(BASE, "assignments.json")))

GALLERIES = ["friends-gallery", "love-gallery", "parents-gallery", "grief-gallery"]
MAX_WORDS = 10
problems = []
used = {}
rows = []


def parse_ref(ref):
    head, v = ref.rsplit(":", 1)
    if " " in head.strip():
        book, ch = head.rsplit(" ", 1)
        return book.strip(), ch.strip(), v.strip(), "bible"
    return "Psalms", head.strip(), v.strip(), "psalms"


def verse_of(ref):
    book, ch, v, kind = parse_ref(ref)
    if kind == "bible":
        verses = BIBLE.get(book, {}).get(ch)
        label = f"{book} {ch}:{v}"
    else:
        verses = PSALMS.get(ch)
        label = f"Psalm {ch}:{v}"
    if verses is None:
        return None, f"{label} not in corpus"
    match = [x for x in verses if str(x["v"]) == v]
    if not match:
        return None, f"{label} does not exist"
    return match[0]["t"], None


for g in GALLERIES:
    manifest = json.load(open(f"/Users/sero/{g}/manifest.json"))
    slugs = [w["slug"] for w in manifest]
    a = ASSIGN[g]
    missing = [s for s in slugs if s not in a]
    extra = [s for s in a if s not in slugs]
    if missing:
        problems.append(f"{g}: works without a verse: {missing}")
    if extra:
        problems.append(f"{g}: verses for unknown slugs: {extra}")
    for s in slugs:
        ref = a.get(s)
        if not ref:
            continue
        text, err = verse_of(ref)
        if err:
            problems.append(f"{g}/{s}: {err}")
            continue
        if "\n" in text or "  " in text or re.search(r"\s+[,.;:?!]", text):
            problems.append(f"{g}/{s}: whitespace artefact in {ref}")
        used.setdefault(ref, []).append(f"{g}/{s}")
        rows.append((g, s, ref, len(text), text))

dupes = {k: v for k, v in used.items() if len(v) > 1}
for k, v in dupes.items():
    problems.append(f"{k} reused by {v}")

print(f"{len(rows)} assignments validated\n")
for g in GALLERIES:
    print("=" * 72)
    print(g)
    print("=" * 72)
    for gg, s, ref, n, text in rows:
        if gg == g:
            print(f"  {s:<24} {ref:<18} {n:>3}ch  {text}")
    print()

lens = sorted(n for _, _, _, n, _ in rows)
print(f"verse length: min={lens[0]} median={lens[len(lens)//2]} max={lens[-1]}")

print()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("OK: every work has a unique, existing KJV verse.")

# every line set on a parents plate must be a short literal run of its verse
EXCERPTS = {k: v for k, v in
            json.load(open(os.path.join(BASE, "excerpts.json"))).items()
            if not k.startswith("_")}
by_slug = {s: ref for g in GALLERIES for s, ref in ASSIGN[g].items()}
print()
over = []
for slug, exc in EXCERPTS.items():
    ref = by_slug.get(slug)
    if ref is None:
        problems.append(f"line for unknown slug {slug}")
        continue
    full, err = verse_of(ref)
    if err:
        problems.append(f"{slug}: {err}")
        continue
    if exc not in full:
        problems.append(f"line for {slug} is not a literal run of {ref}")
    n = len(exc.split())
    if n > MAX_WORDS:
        over.append((slug, ref, n, exc))
    print(f"  {slug:<24} {ref:<18} {n:>2}w  {exc}")
if over:
    problems.append(f"lines longer than {MAX_WORDS} words: {over}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print(f"OK: every line is a literal run of its verse and at most {MAX_WORDS} words.")
