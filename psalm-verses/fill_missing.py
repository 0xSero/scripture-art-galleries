#!/usr/bin/env python3
"""Fill in chapters that the parallel fetch missed (bible-api 429s)."""
import json
import os
import time
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "kjv-psalms.json")
URL = "https://bible-api.com/psalms+{ch}?translation=kjv"

corpus = json.load(open(OUT))
missing = sorted((int(c) for c, v in corpus.items() if not v))

for ch in missing:
    ok = False
    for attempt in range(6):
        try:
            req = urllib.request.Request(
                URL.format(ch=ch), headers={"User-Agent": "psalm-gallery-verses/1.0"}
            )
            with urllib.request.urlopen(req, timeout=25) as r:
                d = json.loads(r.read().decode("utf-8"))
            verses = [{"v": v["verse"], "t": " ".join(v["text"].split())}
                      for v in d.get("verses", []) if " ".join(v["text"].split())]
            if verses:
                corpus[str(ch)] = verses
                print(f"  chapter {ch}: {len(verses)} verses")
                ok = True
                break
        except Exception as e:  # noqa: BLE001
            print(f"  chapter {ch} attempt {attempt + 1}: {e}")
            time.sleep(4.0 * (attempt + 1))
    if not ok:
        print(f"  chapter {ch}: STILL MISSING")
    time.sleep(2.0)

json.dump(corpus, open(OUT, "w"), ensure_ascii=False, indent=1)
still = [c for c, v in corpus.items() if not v]
print(f"\ntotal {sum(len(v) for v in corpus.values())} verses; still missing={sorted(still, key=int)}")
