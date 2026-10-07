#!/usr/bin/env python3
"""Download the chosen works, using the page-view path rather than the API.

Commons rate-limits this host to about one API request a minute, so nothing here
calls api.php: images come from Special:FilePath, which is served like any other
page. Each work already carries the licence its file page was harvested for, so the
only check needed is that the downloaded bytes really are a JPEG.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from works import WORKS  # noqa: E402

FULL_W, THUMB_W = 1600, 700
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) GriefGalleryBuilder/1.0"


def file_url(file_title, width=None):
    """The upload.wikimedia.org URL for a file, or for a scaled copy of it.

    The path is derived from the MD5 of the file name, the way MediaWiki lays its
    image store out, so no redirect through commons.wikimedia.org is needed.
    """
    name = file_title[5:].replace(" ", "_") if file_title.startswith("File:") \
        else file_title.replace(" ", "_")
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    quoted = urllib.parse.quote(name, safe="")
    base = f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{quoted}"
    if width:
        return (f"https://upload.wikimedia.org/wikipedia/commons/thumb/"
                f"{h[0]}/{h[:2]}/{quoted}/{width}px-{quoted}")
    return base


def page_url(file_title):
    return ("https://commons.wikimedia.org/wiki/"
            + urllib.parse.quote(file_title.replace(" ", "_"), safe=":()',!"))


def is_jpeg(path):
    try:
        with open(path, "rb") as f:
            return f.read(3) == b"\xff\xd8\xff"
    except OSError:
        return False


def fetch(url, dest):
    subprocess.run(["curl", "-sSL", "--max-time", "240", "-A", UA, "-o", dest, url],
                   check=True, capture_output=True, timeout=260)
    return os.path.getsize(dest)


def fetch_any(file_title, dest, widths):
    """Try the scaled CDN copies, then the original, until real JPEG bytes land.

    upload.wikimedia.org throttles a burst of requests, so a 429 is waited out
    rather than treated as a failure.
    """
    for w in list(widths) + [None]:
        for attempt in range(4):
            try:
                size = fetch(file_url(file_title, w), dest)
            except Exception:  # noqa: BLE001
                size = 0
            if is_jpeg(dest) and size > 20000:
                return size
            if os.path.exists(dest) and os.path.getsize(dest) == 2255:
                time.sleep(30 * (attempt + 1))  # rate limited: wait it out
            else:
                break
    return 0


def download_original(file_title, dest):
    """Fetch the full-size file once, waiting out the CDN's burst limit."""
    for attempt in range(6):
        try:
            size = fetch(file_url(file_title, None), dest)
        except Exception:  # noqa: BLE001
            size = 0
        if size > 20000 and not is_html(dest):
            return size
        time.sleep(20 * (attempt + 1))
    return 0


def is_html(path):
    try:
        with open(path, "rb") as f:
            head = f.read(200).lstrip()
        return head.startswith(b"<")
    except OSError:
        return True


def to_jpeg(src, dest, max_edge):
    """Write a JPEG at most max_edge on the long side, via sips."""
    subprocess.run(["sips", "-s", "format", "jpeg", "-Z", str(max_edge),
                    src, "--out", dest],
                   check=True, capture_output=True, timeout=240)
    return os.path.getsize(dest)


def one(w):
    slug = w["slug"]
    full = os.path.join(BASE, "img/full", slug + ".jpg")
    thumb = os.path.join(BASE, "img/thumb", slug + ".jpg")
    have = os.path.exists(full) and os.path.getsize(full) > 20000 and is_jpeg(full)
    try:
        if not have:
            tmp = os.path.join(BASE, "img/full", "." + slug + ".orig")
            size = download_original(w["file"], tmp)
            if not size:
                return slug, "the CDN would not serve the file"
            to_jpeg(tmp, full, FULL_W)
            os.remove(tmp)
            if not is_jpeg(full) or os.path.getsize(full) < 20000:
                return slug, "could not be converted to JPEG"
        if not (os.path.exists(thumb) and os.path.getsize(thumb) > 5000
                and is_jpeg(thumb)):
            to_jpeg(full, thumb, THUMB_W)
        entry = dict(w)
        entry.update(source_page=page_url(w["file"]),
                     source_license=w["license"],
                     full=f"img/full/{slug}.jpg", thumb=f"img/thumb/{slug}.jpg")
        json.dump(entry, open(os.path.join(BASE, "meta", slug + ".json"), "w"),
                  ensure_ascii=False, indent=1)
        return slug, None
    except Exception as e:  # noqa: BLE001
        return slug, f"download error: {str(e)[:60]}"


def main():
    for d in ("img/full", "img/thumb", "meta"):
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    manifest, problems = [], []
    for w in WORKS:
        slug, why = one(w)
        if True:
            if why:
                problems.append((slug, why))
            else:
                manifest.append(json.load(open(os.path.join(BASE, "meta", slug + ".json"))))
            print(("ok   " if not why else "FAIL ") + slug +
                  ("" if not why else "  " + why), flush=True)
            time.sleep(0.4)
    json.dump(manifest, open(os.path.join(BASE, "manifest.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(manifest)}/{len(WORKS)} works in manifest")
    for slug, why in problems:
        print(f"  PROBLEM {slug}: {why}")


if __name__ == "__main__":
    main()
