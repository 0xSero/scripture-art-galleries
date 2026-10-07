#!/usr/bin/env python3
"""Mine candidate lines for the hope/merging gallery out of the World English Bible.

Same machinery as the grief pool: a candidate is a literal clause of a verse, split at
the verse's punctuation, kept only at 4-8 words so it reads as a clean phrase. Here the
scoring is inverted — the register is light, rising, joining and joyful — and anything that
carries the grief register is thrown out, because this gallery is the other side of the same
subject.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BIBLE = json.load(open(os.path.join(BASE, "web-bible.json")))
OUT = os.path.join(BASE, "hope-line-candidates.json")

REGISTER = {
    # joining, being made one
    "together": 5, "one body": 5, "one spirit": 5, "one mind": 5,
    "one fold": 5, "knit": 4, "cleave": 3, "embrace": 3, "fold": 2,
    "gather": 3, "gathered": 3, "unite": 4, "united": 4,
    "fellowship": 4, "communion": 4, "brethren": 3, "partakers": 3,
    "accord": 3, "at peace": 4, "joined": 4, "join": 3, "mingle": 3,
    "whole": 3, "altogether": 3, "one another": 4, "each other": 3,
    # rising, going up
    "arise": 4, "arisen": 4, "arose": 3, "rise": 3, "risen": 4,
    "mount": 3, "wing": 4, "wings": 4, "fly": 4, "flew": 3,
    "flight": 3, "eagle": 4, "lift": 3, "lifted": 3, "ascend": 4,
    "high": 2, "height": 3, "up": 1, "climb": 3, "ladder": 3,
    "stairs": 2, "morning": 3, "dawn": 3, "day": 2, "spring": 3,
    # light
    "light": 4, "lights": 3, "shine": 4, "shineth": 4, "shone": 3,
    "bright": 3, "candle": 3, "lamp": 3, "sun": 3, "star": 3,
    "stars": 3, "glory": 3, "glorious": 3, "white": 2, "pure": 3,
    "clean": 2, "clear": 2, "open": 3, "door": 3, "gate": 3,
    "window": 3, "windows": 3, "behold": 2, "beautiful": 3,
    # joy
    "joy": 4, "rejoice": 4, "rejoiced": 3, "glad": 4, "gladness": 4,
    "sing": 3, "singing": 3, "sang": 3, "praise": 3, "thanks": 3,
    "thank": 3, "bless": 3, "blessed": 3, "hallelujah": 5,
    "hosanna": 4, "shout": 3, "dance": 3, "dancing": 3, "harp": 3,
    "merry": 2, "joyful": 4, "joyfully": 4, "comfort": 3,
    "comforted": 3, "sing unto": 3, "o give thanks": 3,
    # growth, the garden, the feast
    "grow": 3, "grew": 2, "fruit": 3, "seed": 3, "vine": 4,
    "branch": 3, "branches": 3, "water": 2, "fountain": 3, "river": 2,
    "well": 2, "tree": 2, "leaf": 2, "flower": 3, "garden": 3,
    "harvest": 3, "reap": 3, "bread": 2, "feast": 3, "wedding": 3,
    "bride": 3, "bridegroom": 3, "marriage": 3, "new": 3, "renew": 4,
    # peace, mercy, life
    "peace": 5, "rest": 3, "quiet": 3, "still": 2, "safety": 3,
    "salvation": 4, "saved": 3, "save": 3, "mercy": 4, "mercies": 3,
    "grace": 3, "lovingkindness": 4, "heal": 4, "healed": 3,
    "restore": 4, "restored": 3, "life": 4, "live": 3, "lived": 2,
    "everlasting": 4, "eternal": 4, "for ever": 3, "promise": 4,
    "promised": 3, "covenant": 3, "inherit": 3, "kingdom": 3,
    "dwell": 3, "abide": 3, "remain": 3, "hope": 5, "hoped": 4,
    "trust": 3, "faith": 3, "believe": 3, "truth": 3, "wisdom": 3,
    "knowledge": 2, "understanding": 2, "righteous": 2, "upright": 2,
    "holy": 2, "good": 2, "city": 2, "house": 2, "home": 2,
    "children": 2, "sons": 2, "daughters": 2, "father": 2,
    "mother": 2, "friend": 3, "love": 4, "beloved": 4, "charity": 4,
    "earth": 1, "heaven": 3, "heavens": 3, "mountain": 2,
}

# books whose voice carries the register furthest
BOOK_WEIGHT = {
    "Psalms": 3, "Isaiah": 3, "Revelation": 3, "John": 2,
    "Song of Solomon": 3, "1 Corinthians": 2, "Romans": 2,
    "Ephesians": 2, "Philippians": 2, "Colossians": 2,
    "1 John": 3, "1 Peter": 2, "Hebrews": 2, "Matthew": 2,
    "Luke": 2, "Acts": 1, "Zechariah": 2, "Micah": 2,
    "Habakkuk": 2, "Zephaniah": 2, "Jeremiah": 2, "Hosea": 2,
    "Genesis": 1, "Exodus": 1, "Numbers": 1, "Deuteronomy": 1,
    "Ruth": 2, "1 Samuel": 1, "2 Samuel": 2, "1 Kings": 1,
    "2 Kings": 2, "Nehemiah": 1, "Ezra": 1, "Proverbs": 3,
    "Job": 1, "Ecclesiastes": 1, "James": 2, "2 Timothy": 2,
    "Titus": 1, "Philemon": 1,
}

# the other side of the subject: anything carrying the grief register is out
GLOOM = re.compile(
    r"\b(death|dead|die|died|dying|grave|graves|hell|pit|"
    r"night|dark|darkness|shadow|shadows|midnight|twilight|evening|"
    r"weep|wept|weeping|tears?|cry|cried|crying|"
    r"mourn\w*|sorrow\w*|grief\w*|lament\w*|howl|wail|sigh\w*|groan\w*|"
    r"dust|ashes|widow\w*|fatherless|orphan\w*|"
    r"consume\w*|wither\w*|faint\w*|perish\w*|broken|breaks|"
    r"forsake\w*|forsaken|vanity|vanities|desolate|desolation|"
    r"afflict\w*|trouble\w*|plague|war|wars|blood|sword|"
    r"destroy\w*|strike|struck|kill\w*|wrath|indignation|"
    r"curse\w*|famine|enemies|enemy|hatred|vengeance|avenge\w*|"
    r"chastened|stricken|wounded|bruised|fades|fade|"
    r"cut off|cut down|swallow\w*)\b", re.I)

# a line that is only a scene, not a promise: narrative and crowd words
CONTEXT = re.compile(
    r"\b(Pharisees|Sadducees|scribes?|disciples?|answered|said|saying|"
    r"spoke|spoke to|went|goes|it happened|came to pass|"
    r"multitude|crowd|assembly|congregation|elders|priests|"
    r"Pharaoh|Herod|Saul|Absalom|Ahab|Balaam|Balak|"
    r"the people|all the people|children of Israel|"
    r"three times|whose son|whose daughter|"
    r"this day|that day|those days|these things|"
    r"the LORD said|the LORD spoke|word of the LORD)\b", re.I)

# a line that only survives on a negative is not a line for this gallery
NEGATIVE = re.compile(
    r"\b(not|no|never|nor|neither|without|nothing|none|nought|"
    r"cannot|canst not|shall not|will not|hath not|doth not)\b", re.I)

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
            "i", "we", "ye", "you", "him", "her", "them", "me", "us",
            "thee", "this", "these", "those", "there", "unto", "up", "out"}


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
                    if n < 4 or n > 8:
                        continue
                    sc = register_score(cl)
                    if sc < 5:
                        continue
                    if GLOOM.search(cl):
                        continue
                    if CONTEXT.search(cl):
                        continue
                    # a line that only reads as a negation is not hope
                    if NEGATIVE.search(cl) and sc < 9:
                        continue
                    starts_verse = text.startswith(cl)
                    first = cl.split()[0].lower().strip("\u201c\u201d")
                    last = cl.split()[-1].lower().strip("\u201d\u2019")
                    if not starts_verse and first in WEAK_START:
                        sc -= 3
                    if last in WEAK_END:
                        sc -= 2
                    sc += bw
                    if sc < 8:
                        continue
                    cands.append(dict(
                        book=book, chapter=int(ch), verse=int(v["v"]),
                        ref=f"{book} {ch}:{v['v']}",
                        text=cl, words=n, score=sc, full=text,
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
    for i, c in enumerate(ranked[:200]):
        print(f"{i:>3} {c['score']:>3} {c['ref']:<22} {c['words']:>2}w  {c['text']}")


if __name__ == "__main__":
    main()
