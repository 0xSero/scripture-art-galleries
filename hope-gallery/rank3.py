#!/usr/bin/env python3
"""Rank the scraped paintings for the hope/merging gallery.

Keeps works that read as art rather than documentation — a named artist, a date, and
either an art category or an object type — and scores them so the best-catalogued
works come first. Near-duplicates of the same painting are collapsed to one.
"""
import json
import re
import sys

C = json.load(open("/tmp/hope3-candidates.json"))

ART_CAT = re.compile(
    r"(paintings|painting|engravings|etchings|drawings|woodcuts|lithographs|"
    r"oil on canvas|oil on panel|oil on oak|tempera|frescoes|sculptures|"
    r"altarpieces|triptychs|diptychs|prints|still lifes|vanitas|memento mori|"
    r"illuminated manuscripts|portrait|art of|in art|museums|galleries|"
    r"collections|national gallery|rijksmuseum|louvre|hermitage|uffizi|prado|"
    r"metropolitan museum|british museum|tate|art institute|museum of art|"
    r"cubism|futurism|constructivism|suprematism|bauhaus|de stijl|orphism|"
    r"vorticism|rayonism|synchromism|abstract|modernism|avant-garde|"
    r"paintings by|works by)",
    re.I)
JUNK_CAT = re.compile(
    r"(photographs by|photographs of|media contributed|uploaded by|files by user|"
    r"own work|cemetery|cemeteries|grave of|graves of|tombstone|headstone|"
    r"panorama|aerial|satellite|maps|documents|books|newspapers|stamps|"
    r"coins|postcards|screenshots|videos|audio|3d|sculpture in|"
    r"interiors|churchyards|funerals in|burials in)",
    re.I)
ART_TYPE = re.compile(
    r"(painting|print|drawing|sculpture|engraving|etching|lithograph|"
    r"watercolor|watercolour|illumination|pastel|tapestry|fresco|icon|"
    r"relief|altarpiece|triptych|woodcut|oil)", re.I)
BAD_ARTIST = re.compile(
    r"^(unknown|anonymous|unidentified|various|after|follower|circle|school|"
    r"manner|workshop|studio|copy|artist|author|painter|sculptor|uploader|"
    r"see file|no artist|not known)", re.I)
AFTER_ARTIST = re.compile(r"^(after|follower of|circle of|manner of|school of|"
                          r"workshop of|studio of|copy after)", re.I)


PHOTO_MED = re.compile(
    r"(photograph|photographie|daguerreotype|albumen|gelatin|silver print|"
    r"collodion|ambrotype|tintype|film|negative)", re.I)
PAINT_MED = re.compile(
    r"(oil|tempera|watercolo|gouache|fresco|acrylic|pastel|chalk|charcoal|"
    r"pencil|ink|engraving|etching|lithograph|woodcut|aquatint|mezzotint|"
    r"marble|bronze|terracotta|plaster|canvas|panel|paper|vellum|wood)", re.I)
JUNK_TITLE = re.compile(
    r"^(de|en|fr|it|es|nl|und|[0-9\s\-.,]*)$|^[0-9a-f]{16,}$", re.I)


def g(c, k):
    return (c.get(k) or "").strip()


def resolve_qids(works):
    """Turn artist values that are bare Wikidata ids into labels."""
    import urllib.parse
    import urllib.request
    ids = sorted({g(c, "artist") for c in works
                  if re.fullmatch(r"Q[0-9]+", g(c, "artist"))})
    labels = {}
    for qid in ids:
        try:
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
            req = urllib.request.Request(url, headers={"User-Agent": "GriefGalleryBuilder/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode())
            ent = d["entities"][qid]
            lab = (ent.get("labels", {}).get("en", {}).get("value")
                   or next(iter(ent.get("labels", {}).values()))["value"])
            labels[qid] = lab
        except Exception:  # noqa: BLE001
            pass
    for c in works:
        a = g(c, "artist")
        if a in labels:
            c["artist"] = labels[a]
    print(f"resolved {len(labels)} of {len(ids)} Wikidata artist ids")
    return works


def year(s):
    m = re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", s or "")
    return int(m[0]) if m else None


PAINT_CAT = re.compile(
    r"(paintings by|paintings of|paintings in|oil on canvas|oil on panel|"
    r"oil paintings|tempera paintings|watercolor paintings|watercolour paintings|"
    r"gouache paintings|pastel|frescoes|triptychs|altarpieces|"
    r"cubist paintings|futurist paintings|suprematist paintings|"
    r"constructivist paintings|abstract paintings|landscape paintings|"
    r"portrait paintings|still life paintings)", re.I)
PAINT_MED = re.compile(
    r"\b(oil on canvas|oil on panel|oil on board|oil on wood|oil on cardboard|"
    r"oil on paper|tempera|watercolou?r|gouache|pastel|acrylic|encaustic|"
    r"canvas|panel)\b", re.I)
JUNK_CAT = re.compile(
    r"(photographs|photograph of|caricatures|costumes|costume design|posters|"
    r"book covers|book illustrations|magazine covers|journal covers|"
    r"advertisements|ex libris|sculptures|architecture drawings|"
    r"theatre|stage design|set designs|puppets|masks|drawings by)", re.I)
JUNK_TITLE2 = re.compile(
    r"^(caricature|cartoon|costume|poster|cover|design for|sketch for a|"
    r"portrait of a man\b|study for a)|"
    r"\b(caricature|costume|poster|cover of|title page|book jacket)\b", re.I)


def key(c):
    a = g(c, "artist") or g(c, "author")
    t = g(c, "title") or ""
    f = g(c, "file_title")
    base = f[5:] if f.startswith("File:") else f
    base = re.sub(r"\.(jpg|jpeg|png)$", "", base, flags=re.I)
    return re.sub(r"[^a-z0-9]+", " ", (a + " " + (t or base)).lower()).strip()


def main():
    resolve_qids(C)
    kept, dropped = [], 0
    seen = {}
    for c in C:
        cats = c.get("categories") or []
        artist = g(c, "artist") or g(c, "author")
        title = g(c, "title")
        date = g(c, "date")
        y = year(date)
        medium = g(c, "medium")
        otype = g(c, "object_type")
        artcat = any(ART_CAT.search(x) for x in cats)
        junkcat = any(JUNK_CAT.search(x) for x in cats)
        # a work must look like art, not a photograph of a place
        if junkcat and not artcat:
            dropped += 1
            continue
        if not artist or BAD_ARTIST.match(artist):
            dropped += 1
            continue
        is_painting = bool(PAINT_CAT.search(" ".join(cats))) or \
            bool(PAINT_MED.search(medium)) or \
            bool(PAINT_MED.search(g(c, "object_type"))) or \
            bool(PAINT_MED.search(g(c, "description")))
        if not is_painting:
            dropped += 1
            continue
        # nothing that is a caricature, a costume, a poster, a cover or a scan
        if JUNK_CAT.search(" ".join(cats)) or JUNK_TITLE2.search(title):
            dropped += 1
            continue
        if (PHOTO_MED.search(medium) and not PAINT_MED.search(medium)
                and not ART_TYPE.search(otype)):
            dropped += 1
            continue
        # nothing made after the modernist window belongs here, and an upload is not
        # a work: photographs of exhibitions, book covers and scans all read as junk
        if y and y > 1945:
            dropped += 1
            continue
        if not y:
            score_pen = 6
        else:
            score_pen = 0
        cats_l = " ".join(cats)
        if not y and re.search(r"(photographs|images from|scans of|"
                              r"screenshots|taken with)", cats_l, re.I):
            dropped += 1
            continue
        if re.search(r"(book covers|bookcover|title pages|frontispieces|"
                      r"magazine covers|journal covers|advertisements|"
                      r"ex libris|posters)", cats_l, re.I):
            dropped += 1
            continue
        if JUNK_TITLE.match(title):
            title = ""
        score = -score_pen
        score += 6 if PAINT_CAT.search(" ".join(cats)) else 0
        if date:
            score += 2
        if y:
            score += 4 if 1900 <= y <= 1935 else (2 if y <= 1900 else 1)
        if y and y > 1930:
            score -= 6
        if medium:
            score += 3
        if title:
            score += 2
        if g(c, "institution"):
            score += 2
        if g(c, "dimensions"):
            score += 1
        if otype:
            score += 2
        if artcat:
            score += 2
        if re.search(r"(cubism|futurism|constructivism|suprematism|bauhaus|"
                     r"de stijl|orphism|vorticism|rayonism|synchromism|"
                     r"abstract|modernism|avant-garde)", cats_l, re.I):
            score += 3
        if AFTER_ARTIST.match(artist):
            score -= 2
        c["_score"] = score
        c["_year"] = y
        k = key(c)
        if k in seen:
            if seen[k]["_score"] >= score:
                continue
        seen[k] = c
    kept = list(seen.values())
    kept.sort(key=lambda c: (-c["_score"], -(c["_year"] or 0), g(c, "artist")))
    json.dump(kept, open("/tmp/hope3-ranked.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(kept)} ranked works ({dropped} dropped as non-art or unattributed)")
    for i, c in enumerate(kept[:60]):
        print(f"{i:>3} {c['_score']:>3} {c['_year'] or '----'} "
              f"{g(c,'artist')[:30]:<30} | {g(c,'title')[:38]:<38} | "
              f"{g(c,'medium')[:24]:<24} | {(c.get('categories') or [''])[0][:30]}")


if __name__ == "__main__":
    main()
