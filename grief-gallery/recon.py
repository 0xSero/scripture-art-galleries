#!/usr/bin/env python3
"""Recon: how much public-domain art exists on Commons in the grief/night register?

For each candidate category, count the image files it holds (directly and one level of
subcategories down), then licence-check a bounded sample of them with the same filter the
parents gallery uses: public domain or CC0, no attribution/share-alike required, a raster
image at least 450 px wide.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://commons.wikimedia.org/w/api.php"
UA = "GriefGalleryBuilder/1.0 (local personal art gallery)"
ACCEPT = ("public domain", "cc0", "pd-", "pdm")
MIN_W = 450
BAD_EXT = re.compile(r"\.(svg|pdf|tif|tiff|webm|ogv|djvu|gif)$", re.I)

CATEGORIES = [
    "Category:Paintings of death",
    "Category:Death in art",
    "Category:Memento mori",
    "Category:Pietà",
    "Category:Lamentation of Christ",
    "Category:Entombment of Christ",
    "Category:Descent from the Cross",
    "Category:Crucifixion of Christ",
    "Category:Deathbeds",
    "Category:Mourning",
    "Category:Funerals in art",
    "Category:Burials in art",
    "Category:Coffins in art",
    "Category:Graveyards in art",
    "Category:Cemeteries in art",
    "Category:Widows",
    "Category:Orphans in art",
    "Category:Vanitas",
    "Category:Skulls in art",
    "Category:Skeletons in art",
    "Category:Hourglasses",
    "Category:Danse Macabre",
    "Category:Last Judgment in art",
    "Category:Melancholia",
    "Category:Night in art",
    "Category:Moonlight",
    "Category:Nocturnes",
    "Category:Starry sky in art",
    "Category:Ruins in art",
    "Category:Plague in art",
    "Category:Executions in art",
    "Category:Death and the maiden",
    "Category:Tears",
    "Category:Grief in art",
    "Category:Sleeping people in art",
    "Category:Wars in art",
    "Category:Angel of Death",
    "Category:Death in painting",
    "Category:Night landscapes",
    "Category:Mourning in art",
]


def api(params, tries=4):
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
            time.sleep(3 * (i + 1))
    raise last


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def allowed(lic):
    return any(k in (lic or "").lower() for k in ACCEPT)


def members(cat, ctype, limit):
    out, cont = [], None
    while len(out) < limit:
        p = dict(action="query", list="categorymembers", cmtitle=cat,
                 cmtype=ctype, cmlimit=500)
        if cont:
            p["cmcontinue"] = cont
        d = api(p)
        out += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        cont = d.get("continue", {}).get("cmcontinue")
        if not cont:
            break
        time.sleep(0.3)
    return out[:limit]


def usable(titles):
    """Licence-check up to 200 titles, 50 per request. Returns usable count."""
    ok = 0
    for i in range(0, min(len(titles), 200), 50):
        chunk = titles[i:i + 50]
        try:
            d = api(dict(action="query", prop="imageinfo", titles="|".join(chunk),
                         iiprop="url|extmetadata|size", iiurlwidth=1600))
        except Exception:  # noqa: BLE001
            continue
        for p in (d.get("query", {}).get("pages") or {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                continue
            em = ii.get("extmetadata", {})
            lic = clean(em.get("LicenseShortName", {}).get("value"))
            w = ii.get("thumbwidth") or ii.get("width") or 0
            if allowed(lic) and w >= MIN_W and not BAD_EXT.search(p["title"]):
                ok += 1
        time.sleep(0.4)
    return ok


def scan(cat):
    try:
        direct = members(cat, "file", 500)
        subs = members(cat, "subcat", 40)
        extra = []
        for s in subs[:12]:
            if len(direct) + len(extra) >= 400:
                break
            try:
                extra += members(s, "file", 120)
            except Exception:  # noqa: BLE001
                pass
        titles = list(dict.fromkeys(direct + extra))
        ok = usable(titles)
        return dict(cat=cat, files=len(titles), subs=len(subs), usable=ok)
    except Exception as e:  # noqa: BLE001
        return dict(cat=cat, error=str(e)[:80])


def main():
    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(scan, CATEGORIES):
            results.append(r)
            if "error" in r:
                print(f"  {r['cat']:<44} ERROR {r['error']}", flush=True)
            else:
                print(f"  {r['cat']:<44} files={r['files']:>4} subcats={r['subs']:>3} "
                      f"usable={r['usable']:>4}", flush=True)

    tot_f = sum(r.get("files", 0) for r in results)
    tot_u = sum(r.get("usable", 0) for r in results)
    print(f"\nTOTAL sampled files={tot_f} usable={tot_u}")
    print("note: usable is measured on at most the first 200 titles per category, "
          "so it is a floor, not the true total")
    json.dump(results, open("/tmp/grief-recon.json", "w"), indent=1)


if __name__ == "__main__":
    main()
