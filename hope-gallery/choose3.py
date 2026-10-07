#!/usr/bin/env python3
"""Choose the works of the hope/merging gallery out of the ranked pool.

The gallery is the positive side of the same subject: works about joining, rising,
light and growth, and the modernists who took the world apart to put it back together
— the Cubists, the Futurists, the Constructivists, the Blue Rider, De Stijl. Each
section is a strand, works are placed by the strand their record names, and the last
section takes everything that is about merging itself.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open("/tmp/hope3-ranked.json"))
DROP = []
if os.path.exists(os.path.join(BASE, "drop.txt")):
    DROP = [l.strip() for l in open(os.path.join(BASE, "drop.txt")) if l.strip()]

SECTIONS = [
    ("I", "Cubism \u2014 the world taken apart",
     "The movement that broke the picture into facets and put it back differently. "
     "Braque and Picasso are still in copyright; the painters who built Cubism "
     "beside them are not, and this section is made of their oil paintings alone.",
     r"\b(fauconnier|gleizes|metzinger|valmier|marcoussis|lipchitz|"
     r"archipenko|lhote|la fresnaye|gris|kupka|delaunay|villon|picabia|"
     r"tobeen|bruce|hayden|duchamp-villon|vill)\b", 24),
    ("II", "Futurism \u2014 speed, light, noise",
     "The Italians who wanted the picture to move: lines of force, a city seen from "
     "every side at once, light treated as a solid. Boccioni, Severini, Carr\u00e0, "
     "Russolo and Balla, nearly all of it painted before 1916.",
     r"\b(boccioni|severini|carr\u00e0|carra|russolo|balla|soffici|"
     r"sant'elia|bogomazov)\b", 22),
    ("III", "Constructivism \u2014 building the new",
     "Art turned into construction: the drawing board, the beam, the diagonal used as "
     "an argument. Malevich, Kliun, Rozanova, Popova, Exter and El Lissitzky, every "
     "one of them out of copyright.",
     r"\b(malevich|kliun|rozanova|popova|exter|lissitzky|tatlin|rodchenko|"
     r"suetin|chashnik|klucis|puni)\b", 22),
    ("IV", "The Blue Rider \u2014 colour as feeling",
     "Kandinsky, Klee, Marc, Macke, Jawlensky and Werefkin: colour used the way "
     "music is used, to say something that has no object in it at all.",
     r"\b(kandinsky|klee|marc|macke|jawlensky|werefkin)\b|"
     r"blue rider|blaue reiter|der blaue", 24),
    ("V", "De Stijl and the grid",
     "Mondrian, Van Doesburg and the painters of the straight line: the picture "
     "reduced to right angles and three colours, and to a kind of quiet that nothing "
     "else in the gallery reaches.",
     r"\b(mondrian|doesburg|vantongerloo|rietveld|herbin|h\u00e9lion|helion)\b|"
     r"de stijl|art concret|abstraction-cr\u00e9ation", 18),
    ("VI", "Merging \u2014 hands, circles, dancers",
     "Paintings of figures that join: hands held, circles closed, spirals turning, "
     "dancers paired, two people walking the same way. The oldest pictures of coming "
     "together, long before anyone had a word for abstraction.",
     r"hands in art|circles in art|spirals|embraces|dancing in art|"
     r"dance in art|kissing|hugging", 20),
    ("VII", "Light and spring \u2014 the open window",
     "The positive subject at its plainest: rainbows, butterflies, open windows, "
     "bridges, spring coming back and light let into a room. The largest section, and "
     "the reason the gallery exists.",
     r"rainbows|butterflies|windows in art|bridges in art|stained glass|"
     r"spring in art|doves in art|light in art|sunrise", 24),
]

PHOTO_MED = re.compile(
    r"(photograph|photographie|daguerreotype|albumen|gelatin|silver print|"
    r"collodion|ambrotype|tintype|film|negative)", re.I)
PAINT_MED = re.compile(
    r"(oil|tempera|watercolo|gouache|fresco|acrylic|pastel|chalk|charcoal|"
    r"pencil|ink|engraving|etching|lithograph|woodcut|aquatint|mezzotint|"
    r"marble|bronze|terracotta|plaster|canvas|panel|paper|vellum|wood|"
    r"cardboard|board|linen)", re.I)
JUNK_TITLE = re.compile(
    r"^(de|en|fr|it|es|nl|und|[0-9\s\-.,]*)$|"
    r"(book cover|bookcover|title page|frontispiece|ex libris|"
    r"cover of|page from|manuscript page)", re.I)


def g(c, k):
    return (c.get(k) or "").strip()


def slugify(s):
    s = s.lower().replace("\u00df", "ss")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:64]


def title_of(c):
    t = g(c, "title")
    if not t:
        f = g(c, "file_title")
        t = re.sub(r"\.(jpg|jpeg|png)$", "", f[5:] if f.startswith("File:") else f,
                   flags=re.I)
        t = re.sub(r"[_]+", " ", t)
    if len(t) > 78:
        t = t[:78].rsplit(" ", 1)[0] + " \u2026"
    return t


def hay(c):
    return " ".join([g(c, "artist"), g(c, "author"),
                     " ".join(c.get("categories") or [])]).lower()


def is_banned(c):
    artist = re.sub(r"\s*\(.*?\)", "", g(c, "artist")).split()
    slug = slugify(((artist[-1] if artist else "") + " " + title_of(c)).strip())
    key = slug[:40]
    return any(key == b[:40] for b in DROP)


def main():
    placed = {}
    for c in C:
        if is_banned(c):
            continue
        medium = g(c, "medium")
        if PHOTO_MED.search(medium) and not PAINT_MED.search(medium):
            continue
        if JUNK_TITLE.search(title_of(c)):
            continue
        h = hay(c)
        for num, title, blurb, pat, quota in SECTIONS:
            if re.search(pat, h):
                placed.setdefault(num, []).append(c)
                break
    chosen, seen_titles, out = {}, set(), []
    for num, title, blurb, pat, quota in SECTIONS:
        rows = sorted(placed.get(num, []),
                      key=lambda c: (0 if g(c, "artist") else 1, -c["_score"],
                                     -(c["_year"] or 0), g(c, "artist")))
        picked = []
        for c in rows:
            key = re.sub(r"[^a-z0-9]+", " ", title_of(c).lower()).strip()[:44]
            if key in seen_titles:
                continue
            seen_titles.add(key)
            picked.append(c)
            if len(picked) >= quota:
                break
        chosen[num] = picked
    seen_slugs = set()
    for num, title, blurb, pat, quota in SECTIONS:
        for c in chosen[num]:
            artist = g(c, "artist")
            surname = re.sub(r"\s*\(.*?\)", "", artist).split()
            slug = slugify(((surname[-1] if surname else "") + " " + title_of(c)).strip()) \
                or slugify(g(c, "file_title"))
            n, base = 2, slug
            while slug in seen_slugs:
                slug = f"{base}-{n}"
                n += 1
            seen_slugs.add(slug)
            out.append(dict(section=num, section_title=title, blurb=blurb, slug=slug,
                            artist=artist, title=title_of(c), date=g(c, "date"),
                            medium=g(c, "medium"), institution=g(c, "institution"),
                            dimensions=g(c, "dimensions"), source=g(c, "source"),
                            file_title=g(c, "file_title"), score=c["_score"],
                            year=c.get("_year"),
                            categories=(c.get("categories") or [])[:6]))
    json.dump(out, open("/tmp/hope3-selected.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(out)} works chosen")
    for num, title, blurb, pat, quota in SECTIONS:
        rows = [w for w in out if w["section"] == num]
        print(f"  {num:<4} {title[:44]:<46} {len(rows):>3}  (pool {len(placed.get(num, []))})")
    for w in out[:6]:
        print("   ", w["slug"], "|", w["artist"][:24], "|", w["title"][:40])


if __name__ == "__main__":
    main()
