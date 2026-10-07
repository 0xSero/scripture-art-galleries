#!/usr/bin/env python3
"""Choose the works for "Grief, and the Night" and sort them into seven sections.

A work is placed by the Commons category it was harvested from — the categories that
name the subject are the reliable signal, and the order below is the reading order of the
gallery. Only the deathbed section falls back to words, because Commons has no deathbed
category of its own. Within a section the best-catalogued works come first.
"""
import json
import os
import re
import unicodedata

SECTIONS = [
    ("I", "The Passion and the Pietà",
     "The descent, the lamentation, the dead Christ held.",
     ["piet", "crucifixion-of-christ", "descent-from-the-cross",
      "lamentation-of-christ", "entombment-of-christ"],
     32),
    ("II", "Deathbeds and the Dead Child",
     "The room where someone is dying, and the hour after.",
     ["deathbed", "death of", "dying", "postmortem", "post-mortem",
      "last hour", "dead child", "death watch", "last rites",
      "extreme unction", "mortuary", "death mask", "death struggle",
      "mother died", "the dead child"],
     13),
    ("III", "Memento Mori and Vanitas",
     "Skulls, hourglasses, and the still life that says you will die.",
     ["memento-mori", "vanitas", "skulls-in-art", "skeletons-in-art",
      "danse-macabre", "death-and-the-maiden"],
     34),
    ("IV", "The Grave, the Churchyard, the Coffin",
     "Cemeteries, tombs, burials, and the gravedigger at work.",
     ["cemeteries-in-art", "coffins-in-art", "funerals-in-art",
      "funerary-art", "epitaphs", "burials-in-art", "graveyards-in-art",
      "tomb-sculptures"],
     32),
    ("V", "Night, Moonlight, and Ruin",
     "Nocturnes, moonlit water, and the ruin under a dark sky.",
     ["night-in-art", "moon-in-art", "moonlight", "nocturnes",
      "starry-sky-in-art", "ruins-in-art", "melancholia"],
     34),
    ("VI", "Mourning, Widows, and Orphans",
     "The people left behind, and the clothes they wear.",
     ["mourning", "widows", "orphans-in-art", "grief-in-art"],
     32),
    ("VII", "Plague, War, and the Angel of Death",
     "Pestilence, battle, and death coming for everyone at once.",
     ["plague-in-art", "executions-in-art", "wars-in-art",
      "angel-of-death"],
     24),
]

JUNK_TITLE = re.compile(r"^(de|en|fr|it|es|nl|und|[0-9\s\-.,]*)$", re.I)
JUNK_WORK = re.compile(r"(book cover|cover of|title page|titlepage|bookplate|"
                       r"ex libris|frontispiece|advertisement|book jacket)", re.I)
# a photograph of a church or a shrine is documentation, not a work
PHOTO_WORK = re.compile(r"^(\d{4}[-.]\d{2}[-.]\d{2}|\d{4}-\d{2}|img[_ ]|dsc[_ ]|p10\d|"
                        r"photo\d|img\d)", re.I)
DEATH_WORDS = ["deathbed", "death of", "dying", "postmortem", "post-mortem",
               "last hour", "dead child", "death watch", "last rites",
               "extreme unction", "mortuary", "death mask", "death struggle",
               "mother died", "the dead child"]


def g(c, k):
    return (c.get(k) or "").strip()


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s.lower())


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-"))[:64]


def category_map():
    out, cache = {}, "/tmp/grief-cache2"
    for f in os.listdir(cache):
        for t in json.load(open(os.path.join(cache, f))):
            out.setdefault(t, []).append(f[:-5])
    return out


def title_of(c):
    t = g(c, "title")
    if JUNK_TITLE.match(t) or not t:
        t = re.sub(r"\.(jpg|jpeg|png|tif|tiff)$", "", g(c, "file_title")[5:],
                   flags=re.I)
        t = re.sub(r"^\s*[A-Z][^\-]{0,28}\s+-\s+", "", t)
    return t


def dropped():
    """Slugs rejected after reviewing the contact sheets."""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "drop.txt")) as f:
            return {ln.strip() for ln in f
                    if ln.strip() and not ln.startswith("#")}
    except FileNotFoundError:
        return set()


def main():
    works = json.load(open("/tmp/grief-ranked.json"))
    banned = dropped()
    catmap = category_map()
    placed = {}
    def predicts(c):
        artist = g(c, "artist")
        surname = re.sub(r"\s*\(.*?\)", "", artist).split()
        return slugify(((surname[-1] if surname else "") + " " + title_of(c)).strip()) \
            or slugify(g(c, "file_title"))

    def is_banned(c):
        key = predicts(c)[:40]
        return any(key == b[:40] for b in banned)

    works = [c for c in works if not is_banned(c)]

    # place every work by the category it was harvested from; the deathbed
    # section is the one subject Commons does not have a category for, so it reads
    # the title instead, and it never takes a work another section has claimed
    passion = {k for num, _, _, keys, _ in SECTIONS if num == "I" for k in keys}
    placed = {}
    for c in works:
        cats = catmap.get(g(c, "file_title"), [])
        sec = None
        # a work whose own title says a death is a deathbed work, unless it is
        # one of the Passion subjects, which the first section claims
        if (any(w in norm(title_of(c)) for w in DEATH_WORDS)
                and not any(k in cat for k in passion for cat in cats)):
            sec = "II"
        if sec is None:
            for num, title, blurb, keys, quota in SECTIONS:
                if num == "II":
                    continue
                if any(k in cat for k in keys for cat in cats):
                    sec = num
                    break
        if sec:
            placed.setdefault(sec, []).append(c)
    for num in placed:
        placed[num].sort(key=lambda c: (-c["_score"], -(c.get("_year") or 0),
                                       g(c, "artist")))

    chosen = {}
    for num, title, blurb, keys, quota in SECTIONS:
        chosen[num] = placed.get(num, [])[:quota]

    # fill the short sections only with works that belong to them, then with the
    # best works left anywhere, so the page still reaches the same size
    spare = []
    for num, title, blurb, keys, quota in SECTIONS:
        spare += placed.get(num, [])[quota:]
    spare.sort(key=lambda c: -c["_score"])
    short = sum(max(0, q - len(chosen[num])) for num, _, _, _, q in SECTIONS)
    for c in spare:
        if short <= 0:
            break
        cats = catmap.get(g(c, "file_title"), [])
        for num, title, blurb, keys, quota in SECTIONS:
            if len(chosen[num]) >= quota:
                continue
            if num == "II" or any(k in cat for k in keys for cat in cats):
                chosen[num].append(c)
                short -= 1
                break
    if short > 0:
        for c in spare:
            if short <= 0:
                break
            for num, title, blurb, keys, quota in SECTIONS:
                if len(chosen[num]) < quota:
                    chosen[num].append(c)
                    short -= 1
                    break

    out, seen = [], set()
    for num, title, blurb, keys, quota in SECTIONS:
        for c in chosen[num]:
            artist, t = g(c, "artist"), title_of(c)
            surname = re.sub(r"\s*\(.*?\)", "", artist).split()
            slug = slugify(((surname[-1] if surname else "") + " " + t).strip()) \
                or slugify(g(c, "file_title"))
            n, base = 2, slug
            while slug in seen:
                slug = f"{base}-{n}"
                n += 1
            seen.add(slug)
            out.append(dict(section=num, section_title=title, blurb=blurb,
                            slug=slug, artist=artist, title=t, date=g(c, "date"),
                            medium=g(c, "medium"),
                            institution=g(c, "institution"),
                            dimensions=g(c, "dimensions"),
                            source=g(c, "source"), file_title=g(c, "file_title"),
                            score=c["_score"], year=c.get("_year"),
                            categories=(c.get("categories") or [])[:6]))
    json.dump(out, open("/tmp/grief-selected.json", "w"),
              ensure_ascii=False, indent=1)
    print(f"{len(out)} works chosen")
    for num, title, blurb, keys, quota in SECTIONS:
        rows = [c for c in out if c["section"] == num]
        print(f"  {num:<4} {title:<42} {len(rows):>3}  (pool {len(placed.get(num, []))})")
    for c in out[:8]:
        print("   ", c["slug"], "|", c["artist"], "|", c["title"][:44])


if __name__ == "__main__":
    main()
