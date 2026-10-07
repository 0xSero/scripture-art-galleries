#!/usr/bin/env python3
"""Build a local King James Version corpus for the whole Bible.

Source: the `en_kjv.json` dataset of the thiagobodruk/bible project (KJV text,
public domain), cached beside this script as `raw-en_kjv.json`. Book names in that
dataset are Portuguese, so this script renames the 66 books to their standard
English names in canonical order and writes `kjv-bible.json`:

    {book: {chapter: [{"v": verse_number, "t": text}, ...]}}

The Psalms corpus (`kjv-psalms.json`) stays as it is for the friends and love
galleries; this corpus covers every book for the parents gallery.
"""
import json
import os
import re
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw-en_kjv.json")
OUT = os.path.join(BASE, "kjv-bible.json")
URL = ("https://raw.githubusercontent.com/thiagobodruk/bible/master/"
       "json/en_kjv.json")

# canonical order of the 66 books of the Protestant Bible
BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation",
]


def normalise(text):
    """The source dataset leaves a space before punctuation ("LORD ,"); tighten it."""
    t = " ".join(str(text).split())
    t = re.sub(r"\s+([,.;:?!])", r"\1", t)
    t = re.sub(r"\s+(\u2019|\u201d)", r"\1", t)
    return t


def main():
    if not os.path.exists(RAW):
        print(f"downloading {URL}")
        req = urllib.request.Request(URL, headers={"User-Agent": "psalm-gallery-verses/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(RAW, "wb") as f:
            f.write(r.read())

    raw = json.load(open(RAW))
    if len(raw) != len(BOOKS):
        raise SystemExit(f"expected 66 books, got {len(raw)}")

    corpus = {}
    total = 0
    for name, book in zip(BOOKS, raw):
        chapters = {}
        for i, verses in enumerate(book["chapters"], start=1):
            out = []
            for j, text in enumerate(verses, start=1):
                t = normalise(text)
                if t:
                    out.append({"v": j, "t": t})
            if out:
                chapters[str(i)] = out
                total += len(out)
        corpus[name] = chapters
        print(f"  {name:<16} {len(chapters):>3} chapters {sum(len(v) for v in chapters.values()):>4} verses")

    left = sum(1 for chs in corpus.values() for vs in chs.values()
               for v in vs if re.search(r"\s+[,.;:?!]", v["t"]))
    json.dump(corpus, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\nwrote {OUT}: {len(corpus)} books, {total} verses, "
          f"{left} verses still with space-before-punctuation")


if __name__ == "__main__":
    main()
