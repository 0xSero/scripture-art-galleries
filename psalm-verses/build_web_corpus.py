#!/usr/bin/env python3
"""Build a modern-English Bible corpus from the World English Bible.

The King James text reads archaic beside a Cubist painting, and the NIV is under
copyright, so the hope gallery sets its lines from the World English Bible: a
public-domain modern-English translation that can be fetched and reproduced whole.
This script downloads the 66 books once and writes them in the same shape as
kjv-bible.json, so every other script keeps working unchanged.
"""
import json
import os
import re
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/TehShrike/world-english-bible/master/json/"
OUT = os.path.join(BASE, "web-bible.json")
CACHE = "/tmp/web-books"

BOOKS = [
    ("genesis", "Genesis"), ("exodus", "Exodus"), ("leviticus", "Leviticus"),
    ("numbers", "Numbers"), ("deuteronomy", "Deuteronomy"), ("joshua", "Joshua"),
    ("judges", "Judges"), ("ruth", "Ruth"), ("1samuel", "1 Samuel"),
    ("2samuel", "2 Samuel"), ("1kings", "1 Kings"), ("2kings", "2 Kings"),
    ("1chronicles", "1 Chronicles"), ("2chronicles", "2 Chronicles"),
    ("ezra", "Ezra"), ("nehemiah", "Nehemiah"), ("esther", "Esther"),
    ("job", "Job"), ("psalms", "Psalms"), ("proverbs", "Proverbs"),
    ("ecclesiastes", "Ecclesiastes"), ("songofsolomon", "Song of Solomon"),
    ("isaiah", "Isaiah"), ("jeremiah", "Jeremiah"), ("lamentations", "Lamentations"),
    ("ezekiel", "Ezekiel"), ("daniel", "Daniel"), ("hosea", "Hosea"),
    ("joel", "Joel"), ("amos", "Amos"), ("obadiah", "Obadiah"),
    ("jonah", "Jonah"), ("micah", "Micah"), ("nahum", "Nahum"),
    ("habakkuk", "Habakkuk"), ("zephaniah", "Zephaniah"), ("haggai", "Haggai"),
    ("zechariah", "Zechariah"), ("malachi", "Malachi"), ("matthew", "Matthew"),
    ("mark", "Mark"), ("luke", "Luke"), ("john", "John"), ("acts", "Acts"),
    ("romans", "Romans"), ("1corinthians", "1 Corinthians"),
    ("2corinthians", "2 Corinthians"), ("galatians", "Galatians"),
    ("ephesians", "Ephesians"), ("philippians", "Philippians"),
    ("colossians", "Colossians"), ("1thessalonians", "1 Thessalonians"),
    ("2thessalonians", "2 Thessalonians"), ("1timothy", "1 Timothy"),
    ("2timothy", "2 Timothy"), ("titus", "Titus"), ("philemon", "Philemon"),
    ("hebrews", "Hebrews"), ("james", "James"), ("1peter", "1 Peter"),
    ("2peter", "2 Peter"), ("1john", "1 John"), ("2john", "2 John"),
    ("3john", "3 John"), ("jude", "Jude"), ("revelation", "Revelation"),
]


def norm(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s


def fetch(slug):
    path = os.path.join(CACHE, slug + ".json")
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        subprocess.run(["curl", "-sSL", "--max-time", "120", "-A", "Mozilla/5.0",
                        RAW + slug + ".json", "-o", path], check=True,
                       capture_output=True, timeout=150)
    return json.load(open(path))


def main():
    os.makedirs(CACHE, exist_ok=True)
    bible, verses = {}, 0
    for slug, name in BOOKS:
        raw = fetch(slug)
        chapters = {}
        for item in raw:
            # poetry is stored as "line text" and prose as "paragraph text";
            # keeping only the prose drops every psalm, most of Isaiah and Job
            if item.get("type") not in ("paragraph text", "line text"):
                continue
            ch, v, text = item.get("chapterNumber"), item.get("verseNumber"), \
                norm(item.get("value"))
            if not ch or not v or not text:
                continue
            # the source splits some verses across paragraph entries, so a verse
            # number can appear more than once and the parts are joined
            key = str(ch)
            row = next((r for r in chapters.setdefault(key, [])
                        if r["v"] == int(v)), None)
            if row:
                row["t"] = (row["t"] + " " + text).strip()
            else:
                chapters[key].append({"v": int(v), "t": text})
        for ch in chapters:
            chapters[ch].sort(key=lambda x: x["v"])
            verses += len(chapters[ch])
        bible[name] = chapters
        print(f"  {name:<16} {len(chapters):>4} chapters {verses:>6} verses so far")
    json.dump(bible, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\nwrote {OUT}: {len(bible)} books, {verses} verses")


if __name__ == "__main__":
    import subprocess  # noqa: E402
    main()
