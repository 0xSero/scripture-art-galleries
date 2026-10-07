#!/usr/bin/env python3
"""Mine candidate lines for the grief/night gallery out of the whole KJV Bible.

Every candidate is a literal clause of its verse: the verse is split at its punctuation
and a clause is kept only if it runs 4-10 words, so the line is always a clean phrase
that exists verbatim in the corpus. Candidates are scored by how heavily they carry the
register — death, the grave, night, darkness, weeping, dust, mourning — and by whether
they start and end on a clause boundary. The top of the ranked list is the pool the plates
are set from.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BIBLE = json.load(open(os.path.join(BASE, "kjv-bible.json")))
OUT = os.path.join(BASE, "grief-line-candidates.json")

REGISTER = {
    "death": 4, "dead": 4, "die": 3, "died": 3, "dieth": 3, "dying": 3,
    "grave": 4, "graves": 4, "hell": 3, "pit": 3,
    "night": 4, "darkness": 4, "dark": 3, "shadow": 3, "shadows": 3,
    "weep": 3, "wept": 3, "weeping": 3, "tears": 3, "tear": 2,
    "cry": 2, "cried": 2, "crying": 2,
    "mourn": 4, "mourning": 4, "mourneth": 4, "sorrow": 4, "sorrows": 4,
    "grief": 4, "griefs": 4,
    "dust": 3, "ashes": 3,
    "sleep": 2, "sleepeth": 2, "slept": 2,
    "widow": 3, "widows": 3, "fatherless": 3, "orphan": 2, "orphans": 2,
    "consume": 2, "consumed": 2, "wither": 2, "withereth": 2, "withered": 2,
    "faint": 2, "fainteth": 2, "perish": 3, "perished": 3,
    "broken": 3, "breaketh": 2,
    "forsake": 3, "forsaken": 3,
    "vanity": 3, "vanities": 3,
    "silence": 2, "silent": 2,
    "affliction": 3, "afflicted": 3,
    "comfort": 2, "comforted": 2, "comforteth": 2,
    "mercy": 2, "mercies": 2, "lovingkindness": 2,
    "remember": 1, "remembered": 1,
    "trouble": 2, "troubled": 2,
    "desolate": 3, "desolation": 3, "solitary": 3,
    "lament": 3, "lamentation": 3, "howl": 2, "wail": 2,
    "sigh": 2, "sighing": 2, "groan": 2, "groaning": 2,
    "tears": 3, "weeping": 3,
    "fade": 2, "fadeth": 2, "cut off": 3, "cut down": 3,
    "grave's": 3, "death's": 3,
    "evening": 2, "morning": 1, "midnight": 3, "twilight": 3,
    "moon": 2, "stars": 2, "star": 1,
    "rest": 2, "rested": 2, "resteth": 2,
    "swallow up": 3, "swallowed": 2,
    "sorrowful": 4, "heaviness": 3, "heavy": 2,
    "wounded": 3, "wounds": 2, "bruised": 3, "stricken": 3,
    "smitten": 2, "chastened": 2,
}

# books whose voice carries the register furthest
BOOK_WEIGHT = {
    "Job": 3, "Ecclesiastes": 3, "Lamentations": 4, "Isaiah": 2,
    "Jeremiah": 2, "Psalms": 2, "Matthew": 1, "Mark": 1, "Luke": 1,
    "John": 1, "Revelation": 3, "2 Samuel": 2, "1 Samuel": 1,
    "Genesis": 1, "Hosea": 1, "Micah": 1, "Habakkuk": 2,
    "Zephaniah": 1, "Nahum": 1, "Ezekiel": 1, "Daniel": 1,
    "Deuteronomy": 1, "Proverbs": 1,
}

# verses that are about vengeance rather than grief: demote
HARSH = re.compile(
    r"\b(enemies|enemy|sword|smite|smote|destroy|destroyed|destroyer|"
    r"vengeance|avenge|hatred|hate|curse|devour|slay|slain|kill|killed|"
    r"wrath|indignation|recompence|reward|rejoice|rejoiced)\b", re.I)

# runs starting or ending on a weak word read as dangling fragments
WEAK_START = {"and", "but", "for", "of", "in", "to", "that", "as", "with",
              "when", "then", "so", "if", "yet", "nor", "or", "his", "her",
              "their", "our", "from", "upon", "at", "by", "which", "who",
              "whom", "is", "was", "be", "hath", "have", "do", "did", "shall",
              "will", "let", "a", "an", "the", "it", "he", "she", "they",
              "ye", "you", "we", "us", "them", "him", "me", "my", "mine"}
WEAK_END = {"and", "but", "for", "of", "in", "to", "that", "as", "with",
            "the", "a", "an", "his", "her", "their", "my", "thy", "thine",
            "is", "was", "be", "shall", "will", "hath", "have", "not", "no",
            "so", "then", "when", "which", "who", "it", "he", "she", "they",
            "i", "we", "ye", "you", "him", "her", "them", "me", "us", "thee"}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def clauses(text):
    """Split a verse at its punctuation, keeping the clause text."""
    parts = re.split(r"[,;:.]\s*", text)
    return [norm(p) for p in parts if p]


def register_score(text):
    low = " " + text.lower() + " "
    s = 0
    for k, w in REGISTER.items():
        if k in low:
            s += w
    return s


def main():
    cands = []
    for book, chapters in BIBLE.items():
        bw = BOOK_WEIGHT.get(book, 0)
        for ch, verses in chapters.items():
            for v in verses:
                text = norm(v["t"])
                for cl in clauses(text):
                    n = len(cl.split())
                    if n < 4 or n > 10:
                        continue
                    sc = register_score(cl)
                    if sc < 4:
                        continue
                    # clean phrase: starts at verse start or a real clause start
                    starts_verse = text.startswith(cl)
                    first = cl.split()[0].lower().strip("\u201c\u201d")
                    last = cl.split()[-1].lower().strip("\u201d\u2019")
                    if not starts_verse and first in WEAK_START:
                        sc -= 3
                    if last in WEAK_END:
                        sc -= 2
                    if HARSH.search(cl):
                        sc -= 4
                    sc += bw
                    if sc < 4:
                        continue
                    cands.append(dict(
                        book=book, chapter=int(ch), verse=int(v["v"]),
                        ref=f"{book} {ch}:{v['v']}",
                        text=cl, words=n, score=sc,
                        full=text,
                    ))

    # one candidate per verse: keep the strongest clause in it
    best = {}
    for c in cands:
        k = c["ref"]
        if k not in best or c["score"] > best[k]["score"]:
            best[k] = c
    ranked = sorted(best.values(), key=lambda c: (-c["score"], c["ref"]))
    print(f"{len(cands)} clauses, {len(ranked)} verses after dedupe")
    json.dump(ranked, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {OUT}\n")
    for i, c in enumerate(ranked[:320]):
        print(f"{i:>3} {c['score']:>3} {c['ref']:<22} {c['words']:>2}w  {c['text']}")


if __name__ == "__main__":
    main()
