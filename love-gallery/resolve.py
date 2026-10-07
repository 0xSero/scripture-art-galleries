#!/usr/bin/env python3
"""Resolve curated works to verified public-domain images and download them."""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
UA = "ParentsGalleryBuilder/1.0 (local personal art gallery)"
API = "https://commons.wikimedia.org/w/api.php"
FULL_W, THUMB_W = 1600, 700
ACCEPT = ("public domain", "cc0", "pd-", "pdm")
MIN_W = 450

sys.path.insert(0, BASE)
from works import WORKS


def api(params, tries=5):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(4 * (i + 1))
    raise last


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def allowed(lic):
    l = (lic or "").lower()
    return any(k in l for k in ACCEPT)


def pack(p):
    ii = (p.get("imageinfo") or [None])[0]
    if not ii:
        return None
    em = ii.get("extmetadata", {})
    lic = clean(em.get("LicenseShortName", {}).get("value"))
    return dict(file_title=p["title"], img=(ii.get("thumburl") or ii.get("url")).split("?")[0],
                license=lic, artist=clean(em.get("Artist", {}).get("value"))[:120],
                width=ii.get("thumbwidth") or ii.get("width"),
                height=ii.get("thumbheight") or ii.get("height"),
                page="https://commons.wikimedia.org/wiki/"
                     + urllib.parse.quote(p["title"].replace(" ", "_")))


def good(res):
    if not res or not allowed(res["license"]):
        return False
    if re.search(r"\.(svg|pdf|tif|tiff|webm|ogv|djvu|gif)$", res["file_title"], re.I):
        return False
    return (res.get("width") or 0) >= MIN_W


def by_title(title):
    d = api(dict(action="query", prop="imageinfo", titles=title,
                 iiprop="url|extmetadata|size", iiurlwidth=FULL_W))
    for p in d.get("query", {}).get("pages", {}).values():
        res = pack(p)
        if good(res):
            return res
    return None


def by_search(query):
    """Try every search hit, not just the first, until one is PD/CC0 and usable."""
    d = api(dict(action="query", generator="search", gsrsearch=query, gsrnamespace=6,
                 gsrlimit=10, prop="imageinfo", iiprop="url|extmetadata|size",
                 iiurlwidth=FULL_W))
    pages = sorted((d.get("query", {}).get("pages") or {}).values(),
                   key=lambda p: p.get("index", 99))
    for p in pages:
        res = pack(p)
        if good(res):
            return res
    return None


def is_jpeg(path):
    try:
        with open(path, "rb") as f:
            return f.read(3) == b"\xff\xd8\xff"
    except OSError:
        return False


def fetch(url, dest):
    subprocess.run(["curl", "-sSL", "--max-time", "180", "-A", UA, "-o", dest, url],
                   check=True, capture_output=True, timeout=200)
    return os.path.getsize(dest)


def main():
    for d in ("img/full", "img/thumb", "meta"):
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    manifest, problems = [], []

    for w in WORKS:
        full = os.path.join(BASE, "img/full", w["slug"] + ".jpg")
        thumb = os.path.join(BASE, "img/thumb", w["slug"] + ".jpg")
        meta_path = os.path.join(BASE, "meta", w["slug"] + ".json")
        have = os.path.exists(full) and os.path.getsize(full) > 20000 and is_jpeg(full)

        try:
            if os.path.exists(meta_path):
                res = json.load(open(meta_path))
            else:
                res = by_title(w["file"]) if w.get("file") else by_search(w["q"])
                time.sleep(2)
        except Exception as e:  # noqa: BLE001
            problems.append((w["slug"], f"resolve error: {e}"))
            continue
        if not res:
            problems.append((w["slug"], "no public-domain result"))
            continue
        if not os.path.exists(meta_path):
            json.dump(res, open(meta_path, "w"), indent=1)

        if not (have and os.path.exists(thumb)):
            try:
                size = fetch(res["img"], full)
                if not is_jpeg(full) or size < 20000:
                    problems.append((w["slug"], f"bad image ({size} bytes)"))
                    continue
                subprocess.run(["sips", "-Z", str(THUMB_W), full, "--out", thumb],
                               check=True, capture_output=True, timeout=90)
            except Exception as e:  # noqa: BLE001
                problems.append((w["slug"], f"download error: {e}"))
                continue

        entry = {k: v for k, v in w.items() if k not in ("file", "q")}
        entry.update(source_title=res["file_title"], source_page=res["page"],
                     source_license=res["license"], source_artist=res.get("artist", ""),
                     full=f"img/full/{w['slug']}.jpg", thumb=f"img/thumb/{w['slug']}.jpg",
                     px=f"{res.get('width')}x{res.get('height')}")
        manifest.append(entry)
        print(f"{'cached' if have else 'new   '} {w['slug']:24s} {res['license']:16s} "
              f"{res['file_title'][:56]}", flush=True)

    json.dump(manifest, open(os.path.join(BASE, "manifest.json"), "w"), indent=1)
    print(f"\n{len(manifest)}/{len(WORKS)} works in manifest")
    for slug, why in problems:
        print(f"  PROBLEM {slug}: {why}")


if __name__ == "__main__":
    main()
