#!/usr/bin/env python3
"""Fetch modern-English Bible text for the hope candidates and mine lines from it.

The King James text reads archaic next to a Cubist painting, so the hope gallery sets
its lines from the World English Bible instead: a public-domain modern-English
translation, close in register to the NIV, which can be fetched verse by verse and
reproduced without a permission notice. Clauses are mined from the fetched text with
the same rule as before — a literal run of four to eight words — so every line is
still a real phrase of a real verse.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from build_hope_lines import (GLOOM, CONTEXT, NEGATIVE, WEAK_START,  # noqa: E402
                             WEAK_END, norm, clauses)

KJV_POOL = json.load(open(os.path.join(BASE, "hope-line-candidates.json")))
KJV = json.load(open(os.path.join(BASE, "kjv-bible.json")))
CACHE = "/tmp/web-verses.json"
OUT = os.path.join(BASE, "web-line-candidates.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) HopeGalleryBuilder/1.0"

REGISTER = {
    "together": 5, "one body": 5, "one spirit": 5, "one mind": 5,
    "one fold": 5, "knit": 4, "cleave": 3, "embrace": 3,
    "gather": 3, "gathered": 3, "unite": 4, "united": 4,
    "fellowship": 4, "communion": 4, "brethren": 3, "partakers": 3,
    "accord": 3, "peace": 5, "joined": 4, "join": 3, "mingle": 3,
    "whole": 3, "altogether": 3, "one another": 4, "each other": 3,
    "meet together": 5, "meet": 3, "met": 3, "reconcil": 4,
    "arise": 4, "arisen": 4, "arose": 3, "rise": 3, "risen": 4,
    "mount": 3, "wing": 4, "wings": 4, "fly": 4, "flight": 3,
    "eagle": 4, "lift": 3, "lifted": 3, "ascend": 4, "high": 2,
    "height": 3, "climb": 3, "ladder": 3, "morning": 3, "dawn": 3,
    "light": 4, "lights": 3, "shine": 4, "shines": 4, "shone": 3,
    "bright": 3, "lamp": 3, "sun": 3, "star": 3, "stars": 3,
    "glory": 3, "glorious": 3, "white": 2, "pure": 3, "clean": 2,
    "clear": 2, "open": 3, "door": 3, "gate": 3, "window": 3,
    "beautiful": 3, "joy": 4, "rejoice": 4, "glad": 4, "gladness": 4,
    "sing": 3, "singing": 3, "praise": 3, "thanks": 3, "bless": 3,
    "blessed": 3, "hallelujah": 5, "hosanna": 4, "shout": 3,
    "dance": 3, "dancing": 3, "harp": 3, "joyful": 4, "comfort": 3,
    "grow": 3, "fruit": 3, "seed": 3, "vine": 4, "branch": 3,
    "branches": 3, "water": 2, "fountain": 3, "river": 2, "tree": 2,
    "flower": 3, "garden": 3, "harvest": 3, "reap": 3, "bread": 2,
    "feast": 3, "wedding": 3, "bride": 3, "bridegroom": 3,
    "marriage": 3, "new": 3, "renew": 4, "rest": 3, "quiet": 3,
    "still": 2, "safety": 3, "salvation": 4, "saved": 3, "save": 3,
    "mercy": 4, "mercies": 3, "grace": 3, "lovingkindness": 4,
    "heal": 4, "healed": 3, "restore": 4, "restored": 3, "life": 4,
    "live": 3, "everlasting": 4, "eternal": 4, "forever": 3,
    "promise": 4, "promised": 3, "covenant": 3, "inherit": 3,
    "kingdom": 3, "dwell": 3, "abide": 3, "remain": 3, "hope": 5,
    "hoped": 4, "trust": 3, "faith": 3, "believe": 3, "truth": 3,
    "wisdom": 3, "righteous": 2, "upright": 2, "holy": 2,
    "good": 2, "city": 2, "house": 2, "home": 2, "children": 2,
    "sons": 2, "daughters": 2, "father": 2, "mother": 2,
    "friend": 3, "love": 4, "beloved": 4, "charity": 4,
    "heaven": 3, "heavens": 3, "mountain": 2, "earth": 1,
    "no more": 4, "wipe away": 3, "dwell with": 4, "with them": 3,
    "all things": 3, "all nations": 3, "every nation": 3,
}

BOOK_WEIGHT = json.load(open(os.path.join(BASE, "kjv-bible.json"))) and {
    "Psalms": 3, "Isaiah": 3, "Revelation": 3, "John": 2,
    "Song of Solomon": 3, "1 Corinthians": 2, "Romans": 2,
    "Ephesians": 2, "Philippians": 2, "Colossians": 2,
    "1 John": 3, "1 Peter": 2, "Hebrews": 2, "Matthew": 2,
    "Luke": 2, "Acts": 1, "Zechariah": 2, "Micah": 2,
    "Habakkuk": 2, "Zephaniah": 2, "Jeremiah": 2, "Hosea": 2,
    "Genesis": 1, "Exodus": 1, "Numbers": 1, "Deuteronomy": 1,
    "Ruth": 2, "1 Samuel": 1, "2 Samuel": 2, "1 Kings": 1,
    "2 Kings": 2, "Nehemiah": 1, "Ezra": 1, "Proverbs": 3,
    "Job": 1, "Ecclesiastes": 1, "James": 2, "2 Timothy": 2,
    "Titus": 1, "Philemon": 1,
}


def api_ref(ref):
    """'1 Samuel 18:1' -> '1+samuel+18:1' for bible-api.com."""
    head, v = ref.rsplit(":", 1)
    parts = head.split(" ")
    if parts[0].isdigit() and len(parts) >= 3:
        book, ch = parts[0] + " " + parts[1], parts[2]
    else:
        book, ch = parts[0], parts[1]
    return urllib.parse.quote(f"{book.lower().replace(' ', '+')}+{ch}:{v}",
                              safe=":+")


def fetch(ref, translation="web"):
    url = f"https://bible-api.com/{api_ref(ref)}?translation={translation}"
    out = subprocess.run(["curl", "-sS", "--max-time", "40", "-A", UA, url],
                         capture_output=True, text=True, timeout=60)
    try:
        d = json.loads(out.stdout)
    except Exception:  # noqa: BLE001
        return None
    return d.get("text", "").strip() or None


def register_score(text):
    low = " " + text.lower() + " "
    s = 0
    for k, w in REGISTER.items():
        if k in low:
            s += w
    return s


def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    refs = [c["ref"] for c in KJV_POOL[:420]]
    todo = [r for r in refs if r not in cache]
    print(f"{len(refs)} refs, {len(todo)} to fetch")
    for i, r in enumerate(todo, 1):
        text = fetch(r)
        if text:
            cache[r] = text
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}", flush=True)
            json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
        time.sleep(0.35)
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
    print(f"cached {len(cache)} verses in {CACHE}")

    # mine clauses from the modern text
    cands = []
    for ref, text in cache.items():
        book = ref.rsplit(" ", 1)[0] if not ref[0].isdigit() else \
            ref.split(" ", 2)[0] + " " + ref.split(" ", 2)[1]
        book = re.sub(r" \d+:\d+$", "", ref)
        bw = BOOK_WEIGHT.get(book, 0)
        body = norm(text)
        for cl in clauses(body):
            n = len(cl.split())
            if n < 4 or n > 8:
                continue
            sc = register_score(cl)
            if sc < 8:
                continue
            if GLOOM.search(cl) or CONTEXT.search(cl):
                continue
            if NEGATIVE.search(cl) and sc < 12:
                continue
            starts = body.startswith(cl)
            first = cl.split()[0].lower().strip("\u201c")
            last = cl.split()[-1].lower().strip("\u201d")
            if not starts and first in WEAK_START:
                sc -= 3
            if last in WEAK_END:
                sc -= 2
            sc += bw
            if sc < 8:
                continue
            cands.append(dict(ref=ref, text=cl, words=n, score=sc, web=body))
    best = {}
    for c in cands:
        k = c["ref"]
        if k not in best or c["score"] > best[k]["score"]:
            best[k] = c
    ranked = sorted(best.values(), key=lambda c: (-c["score"], c["ref"]))
    json.dump(ranked, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"{len(ranked)} verses mined -> {OUT}")
    for c in ranked[:90]:
        print(f"{c['score']:>3} {c['ref']:<24} {c['words']}w  {c['text']}")


if __name__ == "__main__":
    main()
