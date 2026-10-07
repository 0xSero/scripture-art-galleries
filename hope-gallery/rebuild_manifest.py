#!/usr/bin/env python3
"""Rebuild manifest.json from the per-work records in meta/.

The resolver writes its manifest as it goes, so a run that is interrupted or
rate-limited leaves works downloaded but unlisted. Every downloaded work already has
a meta/<slug>.json beside its images, so the manifest is rebuilt from those.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
META = os.path.join(BASE, "meta")

import sys
sys.path.insert(0, BASE)
from works import WORKS  # noqa: E402
WANTED = {w["slug"]: w for w in WORKS}


def main():
    rows = []
    for name in sorted(os.listdir(META)):
        if not name.endswith(".json"):
            continue
        w = json.load(open(os.path.join(META, name)))
        full = os.path.join(BASE, w.get("full", ""))
        thumb = os.path.join(BASE, w.get("thumb", ""))
        if w["slug"] not in WANTED:
            continue
        if os.path.exists(full) and os.path.exists(thumb):
            rows.append(w)
    json.dump(rows, open(os.path.join(BASE, "manifest.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"manifest rebuilt from meta/: {len(rows)} works")


if __name__ == "__main__":
    main()
