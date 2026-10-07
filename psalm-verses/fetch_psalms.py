#!/usr/bin/env python3
"""Fetch the KJV Psalms (150 chapters) from bible-api.com into a local corpus.

KJV is public domain. Every request is bounded by a hard timeout so a hung
socket returns instead of stalling the turn.
"""
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "kjv-psalms.json")
URL = "https://bible-api.com/psalms+{ch}?translation=kjv"


def fetch(ch):
    req = urllib.request.Request(
        URL.format(ch=ch), headers={"User-Agent": "psalm-gallery-verses/1.0"}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                d = json.loads(r.read().decode("utf-8"))
            verses = []
            for v in d.get("verses", []):
                text = " ".join(v["text"].split())
                if text:
                    verses.append({"v": v["verse"], "t": text})
            if verses:
                return ch, verses
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                print(f"  chapter {ch}: FAILED {e}")
            else:
                time.sleep(1.5 * (attempt + 1))
    return ch, []


def main():
    corpus = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for ch, verses in ex.map(fetch, range(1, 151)):
            corpus[str(ch)] = verses
            if verses:
                print(f"  chapter {ch}: {len(verses)} verses")
            else:
                print(f"  chapter {ch}: EMPTY")

    missing = [c for c, v in corpus.items() if not v]
    json.dump(corpus, open(OUT, "w"), ensure_ascii=False, indent=1)
    total = sum(len(v) for v in corpus.values())
    print(f"\nwrote {OUT}: {len(corpus)} chapters, {total} verses, missing={missing}")


if __name__ == "__main__":
    main()
