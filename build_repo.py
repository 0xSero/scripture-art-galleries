#!/usr/bin/env python3
"""Assemble the galleries we made into one repository.

Every gallery keeps its own directory and its own relative paths, so each page still
opens straight from the checkout. The plates are re-encoded for the web: the lightbox
copy is capped at 1300 px and the grid thumbnail at 700 px, which is what the pages
already display. The raw Commons originals (img/full) are left out — the resolver in
each gallery fetches them again, and they are not our work.
"""
import json
import os
import re
import shutil
import sys

from PIL import Image

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "art-galleries")
GALLERIES = ["parents-gallery", "friends-gallery", "love-gallery", "grief-gallery",
             "hope-gallery", "love-and-friendship"]
# code worth keeping beside each page, and the data the pages are built from
KEEP = {
    "parents-gallery": ["build.py", "resolve.py", "works.py", "verses.json", "manifest.json"],
    "friends-gallery": ["build.py", "resolve.py", "works.py", "verses.json", "manifest.json"],
    "love-gallery": ["build.py", "resolve.py", "works.py", "verses.json", "manifest.json"],
    "grief-gallery": ["build.py", "resolve.py", "choose.py", "harvest.py", "harvest2.py",
                      "rank.py", "rank_hope.py", "recon.py", "thumbs.py", "notes.py",
                      "write_works.py", "works.py", "verses.json", "manifest.json",
                      "drop.txt"],
    "hope-gallery": ["build_hope.py", "resolve.py", "selection.py", "gen_works.py",
                     "rebuild_manifest.py", "assign_quotes.py", "render_hope.py",
                     "verify_hope.py", "harvest3.py", "rank3.py", "choose3.py",
                     "merge_classical.py", "build_quote_page.py", "gallery.css",
                     "make_hope.sh", "watch_hope.sh", "lines.json", "works.py",
                     "manifest.json", "quote-pool.json", "art-review.json",
                     "art-review.md"],
    "love-and-friendship": ["build.py"],
}
MAX = {"versed": 1300, "versed-thumb": 700}


def curated(src):
    """The slugs the gallery actually shows, so dropped work stays out."""
    path = os.path.join(src, "works.py")
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8").read()
    return set(re.findall(r"['\"]?slug['\"]?\s*[=:]\s*['\"]([^'\"]+)", text))


def copy_images(src, dest, slugs):
    made = 0
    for kind, cap in MAX.items():
        s = os.path.join(src, "img", kind)
        if not os.path.isdir(s):
            continue
        d = os.path.join(dest, "img", kind)
        os.makedirs(d, exist_ok=True)
        for name in sorted(os.listdir(s)):
            if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            if slugs is not None and name[:-4] not in slugs:
                continue
            im = Image.open(os.path.join(s, name)).convert("RGB")
            im.thumbnail((cap, cap), Image.Resampling.LANCZOS)
            im.save(os.path.join(d, name[:-4] + ".jpg"), "JPEG", quality=82,
                    optimize=True, progressive=True)
            made += 1
    return made


def main():
    if os.path.exists(REPO):
        shutil.rmtree(REPO)
    os.makedirs(REPO)
    report = []
    for g in GALLERIES:
        src = os.path.join(HOME, g)
        dest = os.path.join(REPO, g)
        os.makedirs(dest, exist_ok=True)
        for name in os.listdir(src):
            p = os.path.join(src, name)
            if os.path.isfile(p) and (name == "index.html" or name in KEEP.get(g, [])):
                shutil.copy2(p, os.path.join(dest, name))
        n = copy_images(src, dest, curated(src))
        size = sum(os.path.getsize(os.path.join(r, f))
                   for r, _, fs in os.walk(dest) for f in fs)
        report.append((g, n, size))
        print(f"  {g:<22} {n:>4} plates  {size / 1e6:>7.1f} MB")

    # the Bible text and the curation that produced the lines, so the repo stands alone
    ps = os.path.join(REPO, "psalm-verses")
    os.makedirs(ps, exist_ok=True)
    for name in sorted(os.listdir(os.path.join(HOME, "psalm-verses"))):
        if name.endswith((".json", ".py", ".html")) and os.path.getsize(
                os.path.join(HOME, "psalm-verses", name)) < 20_000_000:
            shutil.copy2(os.path.join(HOME, "psalm-verses", name), os.path.join(ps, name))
    for name in ("build_repo.py",):
        shutil.copy2(os.path.join(HOME, name), os.path.join(REPO, name))
    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(REPO) for f in fs)
    print(f"total {total / 1e6:.1f} MB in {REPO}")
    json.dump(report, open("/tmp/repo-report.json", "w"))


if __name__ == "__main__":
    main()
