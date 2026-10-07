#!/usr/bin/env python3
"""Harvest public-domain works in the grief/night register from Wikimedia Commons.

One generator query per category returns the files *and* their imageinfo and
categories together, so licence-checking costs no extra request. Requests are strictly
sequential with a pause between them, and each category is cached under
/tmp/grief-cache/, because the Commons API rate-limits parallel callers hard.

Filter, as in the parents gallery: public domain or CC0, no attribution or
share-alike, a raster image at least 800 px wide. Catalogue metadata comes from the
Commons record: object name, artist, date, description, medium, credit.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "GriefGalleryBuilder/1.0 (local personal art gallery; contact: local user)"
CACHE = "/tmp/grief-cache"
OUT = "/tmp/grief-candidates.json"

ACCEPT = ("public domain", "cc0", "pd-", "pdm")
BAD_EXT = re.compile(r"\.(svg|pdf|tif|tiff|webm|ogv|djvu|gif|stl|ogg|oga|mp3)$", re.I)
MIN_W = 800

JUNK_CAT = re.compile(
    r"(photographs by|photographs of|media contributed by|uploaded by|own work|"
    r"self-published|files by user|flickr|panoramas|aerial photograph|"
    r"screenshots|satellite|maps of|diagrams|banknotes|stamps|"
    r"coats of arms|graffiti|street art|photographs taken|images from|"
    r"video|audio|3d|pdf files)", re.I)
ART_CAT = re.compile(
    r"(paintings|painting|engravings|etchings|drawings|woodcuts|lithographs|"
    r"oil on canvas|oil on panel|tempera|frescoes|sculptures|marble|bronze|"
    r"in art|art of|museums|galleries|collections|altarpieces|portrait|"
    r"national gallery|rijksmuseum|louvre|hermitage|uffizi|prado|"
    r"metropolitan museum|prints|artists|tomb|sarcophagus|relief)", re.I)

CATEGORIES = [
    # the largest categories first, one request each, no subcategory walk
    "Category:Memento mori", "Category:Funerals in art", "Category:Ruins in art",
    "Category:Cemeteries in art", "Category:Crucifixion of Christ",
    "Category:Lamentation of Christ", "Category:Mourning", "Category:Pietà",
    "Category:Burials in art", "Category:Death and the maiden",
    "Category:Descent from the Cross", "Category:Night in art",
    "Category:Vanitas", "Category:Moonlight", "Category:Graveyards in art",
    "Category:Coffins in art", "Category:Entombment of Christ",
    "Category:Skulls in art", "Category:Skeletons in art",
    "Category:Sleeping people in art", "Category:Orphans in art",
    "Category:Widows", "Category:Epitaphs", "Category:Deposition of Christ",
    "Category:Starry sky in art", "Category:Melancholia",
    "Category:Grief in art", "Category:Executions in art",
    "Category:Plague in art", "Category:Night landscapes",
    "Category:Moon in art", "Category:Nocturnes", "Category:Tomb sculptures",
    "Category:Funerary art", "Category:Wars in art",
]

MAX_FILES_PER_CAT = 500
MAX_SUBCATS = 0
SUBCAT_FILES = 0
PAUSE = 12.0


def api(params, tries=5):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            last = e
            code = getattr(e, "code", None)
            wait = 60 * (i + 1) if code == 429 else 6 * (i + 1)
            print(f"    retry in {wait}s ({str(e)[:40]})", flush=True)
            time.sleep(wait)
    raise last


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def allowed(lic):
    return any(k in (lic or "").lower() for k in ACCEPT)


def pack(page):
    ii = (page.get("imageinfo") or [None])[0]
    if not ii:
        return None
    em = ii.get("extmetadata", {})
    title = page["title"]
    lic = clean(em.get("LicenseShortName", {}).get("value"))
    w = ii.get("thumbwidth") or ii.get("width") or 0
    h = ii.get("thumbheight") or ii.get("height") or 0
    if not allowed(lic) or w < MIN_W or BAD_EXT.search(title):
        return None
    return dict(
        file_title=title,
        img=(ii.get("thumburl") or ii.get("url")).split("?")[0],
        license=lic, width=w, height=h,
        object_name=clean(em.get("ObjectName", {}).get("value")),
        artist=clean(em.get("Artist", {}).get("value"))[:200],
        date=clean(em.get("DateTimeOriginal", {}).get("value"))[:120],
        medium=clean(em.get("Medium", {}).get("value"))[:160],
        description=clean(em.get("ImageDescription", {}).get("value"))[:400],
        credit=clean(em.get("Credit", {}).get("value"))[:160],
        categories=[c["title"] for c in (page.get("categories") or [])],
        page="https://commons.wikimedia.org/wiki/"
             + urllib.parse.quote(title.replace(" ", "_")),
    )


def gen(title, ctype, limit):
    """One generator call: members of a category with imageinfo + categories."""
    out, cont = [], None
    while len(out) < limit:
        p = dict(action="query", generator="categorymembers", gcmtitle=title,
                 gcmtype=ctype, gcmlimit=min(250, limit - len(out)),
                 prop="imageinfo|categories", cllimit=50,
                 iiprop="url|extmetadata|size", iiurlwidth=1600)
        if cont:
            p["gcmcontinue"] = cont
        d = api(p)
        out += list((d.get("query", {}).get("pages") or {}).values())
        cont = d.get("continue", {}).get("gcmcontinue")
        if not cont:
            break
        time.sleep(PAUSE)
    return out


def harvest_category(cat):
    slug = re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")
    cache = os.path.join(CACHE, slug + ".json")
    if os.path.exists(cache):
        raw = json.load(open(cache))
        print(f"  {cat:<40} cached pages={len(raw):>4}", flush=True)
        return raw

    pages = gen(cat, "file", MAX_FILES_PER_CAT)
    time.sleep(PAUSE)
    try:
        subs = gen(cat, "subcat", 100)
    except Exception:  # noqa: BLE001
        subs = []
    time.sleep(PAUSE)
    for s in subs[:MAX_SUBCATS]:
        try:
            pages += gen(s["title"], "file", SUBCAT_FILES)
        except Exception as e:  # noqa: BLE001
            print(f"    subcat failed {s['title'][:40]}: {str(e)[:40]}", flush=True)
        time.sleep(PAUSE)

    keep = []
    seen = set()
    for p in pages:
        if p.get("title") in seen or not p.get("title", "").startswith("File:"):
            continue
        seen.add(p["title"])
        r = pack(p)
        if r:
            keep.append(r)
    json.dump(keep, open(cache, "w"), ensure_ascii=False, indent=1)
    print(f"  {cat:<40} pages={len(pages):>4} usable={len(keep):>4}", flush=True)
    return keep


def main():
    os.makedirs(CACHE, exist_ok=True)
    allr = []
    for cat in CATEGORIES:
        try:
            allr += harvest_category(cat)
        except Exception as e:  # noqa: BLE001
            print(f"  {cat:<40} FAILED {str(e)[:60]}", flush=True)
        time.sleep(PAUSE)

    seen, uniq = set(), []
    for r in allr:
        if r["file_title"] in seen:
            continue
        seen.add(r["file_title"])
        uniq.append(r)

    with_artist = [r for r in uniq if r["artist"]]
    art_cat = [r for r in with_artist if any(ART_CAT.search(c) for c in r["categories"])]
    clean_art = [r for r in art_cat
                 if not any(JUNK_CAT.search(c) for c in r["categories"])]

    print(f"\n{len(uniq)} unique PD/CC0 candidates, width >= {MIN_W}")
    print(f"  with an artist:        {len(with_artist)}")
    print(f"  ...in an art category: {len(art_cat)}")
    print(f"  ...not a photograph:   {len(clean_art)}")
    print(f"  ...with a date:        {len([r for r in clean_art if r['date']])}")
    print(f"  ...with a medium:      {len([r for r in clean_art if r['medium']])}")

    json.dump(uniq, open(OUT, "w"), ensure_ascii=False, indent=1)
    json.dump(clean_art, open("/tmp/grief-clean.json", "w"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
