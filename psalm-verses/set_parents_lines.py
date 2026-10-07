#!/usr/bin/env python3
"""Set the psalm and Bible lines for the parents gallery.

Every line is located inside its KJV verse and the *exact corpus text* is written
out, so each line is a literal contiguous run of words by construction. The script
aborts if a line is not found, if a line exceeds ten words, or if a verse is used
twice anywhere in the three galleries.

Sections I-IV now draw on the whole Bible rather than Psalms alone, in the register
of the closing section; section V keeps its psalm lines.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BIBLE = json.load(open(os.path.join(BASE, "kjv-bible.json")))
ASSIGN = json.load(open(os.path.join(BASE, "assignments.json")))
EXCERPTS = {k: v for k, v in
            json.load(open(os.path.join(BASE, "excerpts.json"))).items()
            if not k.startswith("_")}

MAX_WORDS = 10

# (slug, "Book chapter:verse", the line I want, as a literal run from that verse)
LINES = [
    # I. Madonna and Child
    ("madonna-litta", "Luke 2:7", "she brought forth her firstborn son"),
    ("madonna-granduca", "Luke 2:19", "Mary kept all these things, and pondered"),
    ("madonna-pomegranate", "Isaiah 49:15", "Can a woman forget her sucking child"),
    ("madonna-dove", "Isaiah 66:13", "As one whom his mother comforteth"),
    ("virgin-child-st-anne", "2 Timothy 1:5", "which dwelt first in thy grandmother Lois"),
    # II. Fathers and Sons
    ("banjo-lesson", "Proverbs 22:6", "Train up a child in the way he should go"),
    ("tobit-anna", "Proverbs 13:22", "A good man leaveth an inheritance to his children's children"),
    ("old-man-grandson", "Proverbs 20:29", "the beauty of old men is the gray head"),
    ("isaac-blessing-jacob", "Genesis 27:38", "Hast thou but one blessing, my father?"),
    ("prodigal-tavern", "Luke 15:13", "and there wasted his substance with riotous living"),
    # III. The Artist's Own Parents
    ("cezanne-mother", "Proverbs 31:28", "Her children arise up, and call her blessed"),
    ("orlai-mother", "Ecclesiastes 12:7", "then shall the dust return to the earth"),
    ("tanner-mother", "Job 14:1", "Man that is born of a woman"),
    ("ensor-father", "1 Corinthians 13:12", "we see through a glass, darkly"),
    ("mancini-father", "Job 10:9", "thou hast made me as the clay"),
    # IV. The Everyday Work of Care
    ("cassatt-oval-mirror", "Matthew 23:37", "even as a hen gathereth her chickens"),
    ("cassatt-combing", "1 Corinthians 11:15", "her hair is given her for a covering"),
    ("cassatt-nurse-reading", "2 Timothy 3:15", "from a child thou hast known the holy scriptures"),
    ("morisot-garden", "Genesis 3:8", "walking in the garden in the cool of the day"),
    ("morisot-meadow", "Isaiah 40:6", "All flesh is grass, and all the goodliness"),
    # V. Grief, and the Night — the register the gallery is being pushed towards
    ("bouguereau-pieta", "Psalms 22:1", "My God, my God, why hast thou forsaken me"),
    ("michelangelo-pieta", "Psalms 34:18", "nigh unto them that are of a broken heart"),
    ("klimt-death-life", "Psalms 16:11", "Thou wilt shew me the path of life"),
    ("munch-deathbed", "Psalms 39:4", "LORD, make me to know mine end"),
    ("munch-sickroom", "Psalms 41:3", "The LORD will strengthen him upon the bed of languishing"),
]

FOLD = {"'": "\u2019", "\u2018": "\u2019"}


def norm(s):
    for a, b in FOLD.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def parse_ref(ref):
    """'Book chapter:verse' or legacy 'chapter:verse' (Psalms)."""
    head, v = ref.rsplit(":", 1)
    if " " in head.strip():
        book, ch = head.rsplit(" ", 1)
        return book.strip(), ch.strip(), v.strip()
    return "Psalms", head.strip(), v.strip()


def verse_text(ref):
    book, ch, v = parse_ref(ref)
    chapters = BIBLE.get(book)
    if chapters is None:
        raise SystemExit(f"book {book!r} not in corpus (ref {ref})")
    verses = chapters.get(ch)
    if verses is None:
        raise SystemExit(f"{book} {ch} not in corpus (ref {ref})")
    for x in verses:
        if str(x["v"]) == v:
            return re.sub(r"\s+", " ", x["t"]).strip()
    raise SystemExit(f"{book} {ch}:{v} not in corpus")


def locate(full, want):
    f, w = norm(full), norm(want)
    i = f.lower().find(w.lower())
    if i < 0:
        return None
    return f[i:i + len(w)]


parents = {}
problems = []
used = {}

for g in ("friends-gallery", "love-gallery"):
    for slug, ref in ASSIGN[g].items():
        used.setdefault(ref, []).append(f"{g}/{slug}")

for slug, ref, want in LINES:
    full = verse_text(ref)
    exact = locate(full, want)
    if exact is None:
        problems.append(f"{slug}: not a run of {ref}: {full}")
        continue
    n = len(exact.split())
    if n > MAX_WORDS:
        problems.append(f"{slug}: {n} words > {MAX_WORDS}")
    used.setdefault(ref, []).append(f"parents-gallery/{slug}")
    parents[slug] = ref
    EXCERPTS[slug] = exact
    print(f"  {slug:<24} {ref:<16} {n:>2}w  {exact}")

dupes = {k: v for k, v in used.items() if len(v) > 1}
for k, v in dupes.items():
    problems.append(f"{k} used by {v}")

print(f"\n{len(parents)} lines for {len(LINES)} works")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)

ASSIGN["parents-gallery"] = parents
json.dump(ASSIGN, open(os.path.join(BASE, "assignments.json"), "w"),
          ensure_ascii=False, indent=1)

out = {"_note": ("Short lines for the plates, at most ten words each. Each one is "
                 "a literal contiguous run of words from its KJV verse, located "
                 "and written out by set_parents_lines.py; the full verse stays "
                 "in verses.json as the record.")}
out.update(EXCERPTS)
json.dump(out, open(os.path.join(BASE, "excerpts.json"), "w"),
          ensure_ascii=False, indent=1)
print("wrote assignments.json and excerpts.json")
