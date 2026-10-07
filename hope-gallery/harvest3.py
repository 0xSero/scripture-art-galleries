#!/usr/bin/env python3
"""Harvest public-domain paintings in the hope/merging register from Commons.

The Commons API rate-limits this host to roughly one request a minute, so this
harvester uses only the page-view path, which is not throttled the same way:

  1. category pages (`/wiki/Category:X`) give the file titles, 200 per page, with
     `filefrom=` paging;
  2. `Special:Export` takes up to fifty titles per POST and returns their full
     wikitext, which carries both the licence template and the {{Artwork}} record;
  3. images come from `Special:FilePath/<name>?width=N`.

A work is kept only if its licence header carries a public-domain or CC0 template
and no attribution or share-alike template — the same rule the parents gallery used.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "HopeGalleryBuilder/1.0 (local personal art gallery)")
WIKI = "https://commons.wikimedia.org"
CACHE = "/tmp/hope3-cache"
OUT = "/tmp/hope3-candidates.json"

MAX_PAGES_PER_CAT = 3
EXPORT_BATCH = 50
PAUSE = 0.8

CATEGORIES = [
    "Category:Paintings by Wassily Kandinsky",
    "Category:Paintings by Paul Klee",
    "Category:Paintings by Kazimir Malevich",
    "Category:Paintings by Piet Mondrian",
    "Category:Paintings by Robert Delaunay",
    "Category:Paintings by Sonia Delaunay",
    "Category:Paintings by František Kupka",
    "Category:Paintings by Umberto Boccioni",
    "Category:Paintings by Gino Severini",
    "Category:Paintings by Carlo Carrà",
    "Category:Paintings by Luigi Russolo",
    "Category:Paintings by Giacomo Balla",
    "Category:Paintings by Franz Marc",
    "Category:Paintings by August Macke",
    "Category:Paintings by Alexej von Jawlensky",
    "Category:Paintings by Marianne von Werefkin",
    "Category:Paintings by Theo van Doesburg",
    "Category:Paintings by Henri Le Fauconnier",
    "Category:Paintings by Albert Gleizes",
    "Category:Paintings by Jean Metzinger",
    "Category:Paintings by Georges Valmier",
    "Category:Paintings by Lyubov Popova",
    "Category:Paintings by Olga Rozanova",
    "Category:Paintings by Ivan Kliun",
    "Category:Paintings by Alexandra Exter",
    "Category:Paintings by El Lissitzky",
    "Category:Paintings by Vladimir Tatlin",
    "Category:Paintings by Alexander Rodchenko",
    "Category:Paintings by Nikolai Suetin",
    "Category:Paintings by Ilya Chashnik",
    "Category:Paintings by Gustav Klucis",
    "Category:Paintings by Alexander Archipenko",
    "Category:Paintings by Jacques Lipchitz",
    "Category:Paintings by Louis Marcoussis",
    "Category:Paintings by André Lhote",
    "Category:Paintings by Roger de La Fresnaye",
    "Category:Paintings by Lyonel Feininger",
    "Category:Paintings by Johannes Itten",
    "Category:Paintings by Oskar Schlemmer",
    "Category:Paintings by László Moholy-Nagy",
    "Category:Paintings by Georges Vantongerloo",
    "Category:Paintings by Auguste Herbin",
    "Category:Paintings by Joaquín Torres-García",
    "Category:Cubist paintings",
    "Category:Futurist paintings",
    "Category:Suprematist paintings",
    "Category:Constructivist paintings",
    "Category:Abstract paintings",
    "Category:De Stijl",
]


PD_T = re.compile(r"\{\{\s*(PD|Cc-zero|CC0|PD-Art|PD-old|PD-self|PD-US)", re.I)
BAD_T = re.compile(r"\{\{\s*(Cc-by|GFDL|FAL|Non-free|Cc-by-sa)", re.I)
PD_WORD = re.compile(r"(cc[-_ ]?zero|\bcc0\b|public domain|pd-old|pd-art|"
                     r"pd-self|pd-us|pd-scan)", re.I)
BAD_WORD = re.compile(r"(cc[-_ ]?by|gfdl|\bfal\b|attribution|share[-_ ]?alike|"
                      r"non-free|fair use|copyrighted)", re.I)


def get(url, data=None, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            code = getattr(e, "code", None)
            time.sleep(15 * (i + 1) if code in (429, 503) else 3 * (i + 1))
    raise last


def cat_page(cat, filefrom=None):
    url = f"{WIKI}/wiki/{urllib.parse.quote(cat.replace(' ', '_'))}"
    if filefrom:
        url += "?filefrom=" + urllib.parse.quote(filefrom)
    h = get(url)
    files = list(dict.fromkeys(
        urllib.parse.unquote(x).replace("_", " ") for x in
        re.findall(r'href="/wiki/(File:[^"#?]+)"', h)))
    nxt = re.search(r'href="/w/index\.php\?title=[^"]*?&(?:amp;)?filefrom=([^"#]+)#mw-category-media"', h)
    return files, (urllib.parse.unquote(nxt.group(1)) if nxt else None)


def cat_files(cat):
    slug = re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")
    os.makedirs(CACHE, exist_ok=True)
    cache = os.path.join(CACHE, slug + ".json")
    if os.path.exists(cache):
        return json.load(open(cache))
    out, nxt, page = [], None, 0
    while page < MAX_PAGES_PER_CAT:
        try:
            files, nxt = cat_page(cat, nxt)
        except Exception as e:  # noqa: BLE001
            print(f"    page {page} failed: {str(e)[:50]}", flush=True)
            break
        out += files
        page += 1
        if not nxt:
            break
        time.sleep(PAUSE)
    out = list(dict.fromkeys(out))
    json.dump(out, open(cache, "w"), ensure_ascii=False)
    print(f"  {cat:<38} pages={page} files={len(out):>4}", flush=True)
    return out


def export(titles):
    pages = "\n".join(titles)
    data = urllib.parse.urlencode({"pages": pages, "action": "submit",
                                  "curonly": "1"}).encode()
    xml = get(f"{WIKI}/w/index.php?title=Special:Export", data=data)
    out = {}
    for m in re.finditer(r"<page>\s*<title>(.*?)</title>(.*?)</page>", xml, re.S):
        title = m.group(1).strip()
        tm = re.search(r"<text[^>]*>(.*?)</text>", m.group(2), re.S)
        if tm:
            out[title] = (tm.group(1).replace("&lt;", "<").replace("&gt;", ">")
                          .replace("&amp;", "&").replace("&quot;", '"'))
    return out


def templates(text):
    out, i = [], 0
    while True:
        i = text.find("{{", i)
        if i < 0:
            break
        depth, j = 0, i
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        out.append(text[i:j])
        i = max(j, i + 2)
    return out


def tname(t):
    head = t[2:].split("|")[0].split("\n")[0]
    return head.replace("}}", "").strip().lower()


def tparams(t):
    """Top-level | pairs of a template body, positional and named."""
    body = t[2:-2]
    parts, depth, cur = [], 0, ""
    k = 0
    while k < len(body):
        if body.startswith("{{", k) or body.startswith("[[", k):
            depth += 1
            cur += body[k:k + 2]
            k += 2
        elif body.startswith("}}", k) or body.startswith("]]", k):
            depth -= 1
            cur += body[k:k + 2]
            k += 2
        elif body[k] == "|" and depth == 0:
            parts.append(cur)
            cur = ""
            k += 1
        else:
            cur += body[k]
            k += 1
    parts.append(cur)
    out, pos = {}, 0
    for p in parts[1:]:
        if "=" in p:
            k2, v = p.split("=", 1)
            out[k2.strip().lower()] = v.strip()
        else:
            pos += 1
            out[str(pos)] = p.strip()
    return out


def matching_braces(s, start):
    depth, k = 0, start
    while k < len(s):
        if s.startswith("{{", k):
            depth += 1
            k += 2
        elif s.startswith("}}", k):
            depth -= 1
            k += 2
            if depth == 0:
                return k
        else:
            k += 1
    return len(s)


def devalue(s):
    """Read a template argument as text, resolving nested templates."""
    out, i = [], 0
    while i < len(s):
        j = s.find("{{", i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k = matching_braces(s, j)
        out.append(template_text(s[j:k]))
        i = k
    txt = "".join(out)
    txt = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", txt)
    txt = re.sub(r"\[\[([^\]]*)\]\]", r"\1", txt)
    txt = re.sub(r"<ref[^>]*>.*?</ref>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = txt.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", txt).strip(" .;,")


def template_text(t):
    name = tname(t)
    p = tparams(t)
    vals = [v for v in p.values() if v]
    if name.startswith("creator:"):
        return name.split(":", 1)[1].strip().title()
    if name in ("title", "object name"):
        for k in ("en", "de", "fr", "it", "es", "nl"):
            if p.get(k):
                return devalue(p[k])
        return devalue(vals[0]) if vals else ""
    if name in ("other date", "date"):
        got = [devalue(v) for v in vals]
        got = [g for g in got if not re.fullmatch(r"[a-z]", g)]
        nums = [g for g in got if re.match(r"^-?\d{3,4}$", g)]
        if len(nums) >= 2:
            return f"{nums[0]}-{nums[-1]}"
        return " ".join(got)
    if name == "technique":
        got = [devalue(v) for v in vals]
        return " on ".join(got)
    if name in ("size", "dimensions"):
        unit = devalue(p.get("1", ""))
        h = devalue(p.get("height", ""))
        w = devalue(p.get("width", ""))
        bits = [b for b in (h, w) if b]
        return f"{' x '.join(bits)} {unit}".strip()
    if name in ("defaultsort", "rkd", "wikidata", "creator", "information",
                 "artwork", "int:filedesc", "int:license-header", "self",
                 "location dec", "assessments", "qualityimage", "pd-old-100",
                 "cc-zero"):
        return ""
    return devalue(" ".join(vals))


def parse(title, wikitext):
    tpls = templates(wikitext)

    lic_section = wikitext
    m = re.search(r"license-header", wikitext, re.I)
    if m:
        lic_section = wikitext[m.start():]
    pd = bool(PD_T.search(lic_section)) or bool(PD_WORD.search(lic_section))
    bad = bool(BAD_T.search(lic_section)) or bool(BAD_WORD.search(lic_section))
    if not pd or bad:
        return None

    art = {}
    for t in tpls:
        if tname(t) in ("artwork", "art photo", "information", "photograph"):
            p = tparams(t)
            for k in ("artist", "author", "title", "object type", "description",
                      "date", "medium", "dimensions", "institution",
                      "accession number", "source", "department", "location"):
                if k in p and p[k] and k not in art:
                    art[k] = devalue(p[k])
    cats = [re.sub(r"\s+", " ", c).strip() for c in
            re.findall(r"\[\[Category:([^\]|]+)", wikitext)]
    return dict(file_title=title, license_section=lic_section[:200],
                 categories=cats,
                 **{k.replace(" ", "_"): v for k, v in art.items()})


def main():
    os.makedirs(CACHE, exist_ok=True)
    titles = []
    for cat in CATEGORIES:
        try:
            titles += cat_files(cat)
        except Exception as e:  # noqa: BLE001
            print(f"  {cat}: FAILED {str(e)[:60]}", flush=True)
        time.sleep(PAUSE)
    titles = list(dict.fromkeys(titles))
    print(f"\n{len(titles)} candidate files from {len(CATEGORIES)} categories")

    out, problems = [], []
    for i in range(0, len(titles), EXPORT_BATCH):
        batch = titles[i:i + EXPORT_BATCH]
        try:
            texts = export(batch)
        except Exception as e:  # noqa: BLE001
            problems.append((batch[0], str(e)[:60]))
            time.sleep(PAUSE)
            continue
        for t in batch:
            wt = texts.get(t)
            if not wt:
                continue
            r = parse(t, wt)
            if r:
                out.append(r)
        print(f"  export {i + len(batch):>4}/{len(titles)}: kept {len(out)}",
              flush=True)
        time.sleep(PAUSE)

    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\n{len(out)} public-domain / CC0 works with a licence header")
    for t, why in problems:
        print(f"  PROBLEM {t}: {why}")


if __name__ == "__main__":
    main()
