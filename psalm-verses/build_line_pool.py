#!/usr/bin/env python3
"""Build the pool of suggested short lines for the parents gallery.

Every line is checked to be a literal contiguous run of words in its KJV verse and
to be at most ten words. Lines currently on a plate are marked "on_plate": true, so
any of the others can be swapped in without touching the corpus.

The pool is weighted towards the register of the closing section, *Grief, and the
Night*: dust, darkness, the grave, mourning, and the small hours. Lines are drawn
from the whole Bible, not Psalms alone.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BIBLE = json.load(open(os.path.join(BASE, "kjv-bible.json")))
EXCERPTS = {k: v for k, v in
            json.load(open(os.path.join(BASE, "excerpts.json"))).items()
            if not k.startswith("_")}
ON_PLATE = set(EXCERPTS.values())

# (register, "Book chapter:verse", the line)
POOL = [
    # --- grief, and the night (the gallery's preferred register) --------------
    ("grief-night", "Job 1:21", "the LORD gave, and the LORD hath taken away"),
    ("grief-night", "Job 3:3", "Let the day perish wherein I was born"),
    ("grief-night", "Job 14:2", "He cometh forth like a flower, and is cut down"),
    ("grief-night", "Job 2:13", "they saw that his grief was very great"),
    ("grief-night", "Job 10:21", "the land of darkness and the shadow of death"),
    ("grief-night", "Job 17:11", "my purposes are broken off"),
    ("grief-night", "Job 19:25", "I know that my redeemer liveth"),
    ("grief-night", "Job 30:26", "when I waited for light, there came darkness"),
    ("grief-night", "Ecclesiastes 3:2", "a time to be born, and a time to die"),
    ("grief-night", "Ecclesiastes 3:4", "a time to weep, and a time to laugh"),
    ("grief-night", "Ecclesiastes 3:4", "a time to mourn, and a time to dance"),
    ("grief-night", "Ecclesiastes 12:7", "then shall the dust return to the earth"),
    ("grief-night", "Ecclesiastes 12:7", "the spirit shall return unto God who gave it"),
    ("grief-night", "Ecclesiastes 12:1", "Remember now thy Creator in the days of thy youth"),
    ("grief-night", "Ecclesiastes 1:4", "One generation passeth away, and another generation cometh"),
    ("grief-night", "Lamentations 1:1", "How doth the city sit solitary"),
    ("grief-night", "Lamentations 3:22", "It is of the LORD's mercies"),
    ("grief-night", "Lamentations 3:23", "great is thy faithfulness"),
    ("grief-night", "Lamentations 3:31", "the Lord will not cast off for ever"),
    ("grief-night", "Lamentations 1:12", "Is it nothing to you, all ye that pass by"),
    ("grief-night", "Isaiah 40:6", "All flesh is grass, and all the goodliness"),
    ("grief-night", "Isaiah 40:7", "the grass withereth, the flower fadeth"),
    ("grief-night", "Isaiah 53:3", "a man of sorrows, and acquainted with grief"),
    ("grief-night", "Isaiah 53:5", "he was wounded for our transgressions"),
    ("grief-night", "Isaiah 25:8", "he will swallow up death in victory"),
    ("grief-night", "Isaiah 43:2", "when thou passest through the waters"),
    ("grief-night", "Matthew 5:4", "Blessed are they that mourn: for they shall be comforted"),
    ("grief-night", "Matthew 11:28", "Come unto me, all ye that labour"),
    ("grief-night", "Matthew 26:39", "let this cup pass from me"),
    ("grief-night", "Matthew 27:46", "My God, my God, why hast thou forsaken me"),
    ("grief-night", "Luke 23:46", "Father, into thy hands I commend my spirit"),
    ("grief-night", "John 12:24", "Except a corn of wheat fall into the ground"),
    ("grief-night", "John 16:20", "your sorrow shall be turned into joy"),
    ("grief-night", "John 19:26", "Woman, behold thy son"),
    ("grief-night", "Revelation 21:4", "there shall be no more death"),
    ("grief-night", "Revelation 21:4", "neither sorrow, nor crying"),
    ("grief-night", "Revelation 22:5", "there shall be no night there"),
    ("grief-night", "Revelation 7:17", "wipe away all tears from their eyes"),
    ("grief-night", "1 Corinthians 15:26", "The last enemy that shall be destroyed is death"),
    ("grief-night", "1 Corinthians 15:55", "O death, where is thy sting?"),
    ("grief-night", "2 Corinthians 4:17", "our light affliction, which is but for a moment"),
    ("grief-night", "2 Corinthians 5:8", "to be absent from the body"),
    ("grief-night", "Romans 8:38", "neither death, nor life"),
    ("grief-night", "Hebrews 13:14", "here have we no continuing city"),
    ("grief-night", "1 Peter 1:24", "All flesh is as grass"),
    ("grief-night", "Genesis 3:19", "dust thou art, and unto dust shalt thou return"),
    ("grief-night", "Genesis 37:35", "I will go down into the grave unto my son"),
    ("grief-night", "2 Samuel 12:23", "I shall go to him, but he shall not return"),
    ("grief-night", "2 Samuel 18:33", "O my son Absalom, my son"),
    ("grief-night", "Genesis 21:16", "Let me not see the death of the child"),
    # --- parenthood ---------------------------------------------------------
    ("parenthood", "Proverbs 22:6", "Train up a child in the way he should go"),
    ("parenthood", "Proverbs 13:22", "A good man leaveth an inheritance to his children's children"),
    ("parenthood", "Proverbs 20:29", "the beauty of old men is the gray head"),
    ("parenthood", "Proverbs 31:28", "Her children arise up, and call her blessed"),
    ("parenthood", "Proverbs 17:6", "Children's children are the crown of old men"),
    ("parenthood", "Proverbs 23:24", "The father of the righteous shall greatly rejoice"),
    ("parenthood", "Proverbs 4:3", "I was my father's son, tender and only beloved"),
    ("parenthood", "Proverbs 15:20", "A wise son maketh a glad father"),
    ("parenthood", "Proverbs 29:15", "a child left to himself bringeth his mother to shame"),
    ("parenthood", "Proverbs 16:31", "The hoary head is a crown of glory"),
    ("parenthood", "Exodus 20:12", "Honour thy father and thy mother"),
    ("parenthood", "Deuteronomy 31:6", "he will not fail thee, nor forsake thee"),
    ("parenthood", "Genesis 22:2", "Take now thy son, thine only son Isaac"),
    ("parenthood", "Genesis 27:38", "Hast thou but one blessing, my father?"),
    ("parenthood", "1 Samuel 1:27", "For this child I prayed"),
    ("parenthood", "Isaiah 49:15", "Can a woman forget her sucking child"),
    ("parenthood", "Isaiah 66:13", "As one whom his mother comforteth"),
    ("parenthood", "Matthew 23:37", "even as a hen gathereth her chickens"),
    ("parenthood", "Luke 2:7", "she brought forth her firstborn son"),
    ("parenthood", "Luke 2:19", "Mary kept all these things, and pondered"),
    ("parenthood", "Luke 2:35", "a sword shall pierce through thy own soul"),
    ("parenthood", "Luke 2:51", "his mother kept all these sayings in her heart"),
    ("parenthood", "Mark 10:14", "Suffer the little children to come unto me"),
    ("parenthood", "Matthew 18:10", "their angels do always behold the face"),
    ("parenthood", "2 Timothy 1:5", "which dwelt first in thy grandmother Lois"),
    ("parenthood", "2 Timothy 3:15", "from a child thou hast known the holy scriptures"),
    ("parenthood", "1 Corinthians 11:15", "her hair is given her for a covering"),
    ("parenthood", "Genesis 3:8", "walking in the garden in the cool of the day"),
    ("parenthood", "Job 14:1", "Man that is born of a woman"),
    ("parenthood", "Job 10:9", "thou hast made me as the clay"),
    ("parenthood", "1 Corinthians 13:12", "we see through a glass, darkly"),
    ("parenthood", "Luke 15:13", "and there wasted his substance with riotous living"),
    # --- life ---------------------------------------------------------------
    ("life", "John 10:10", "I am come that they might have life"),
    ("life", "John 11:25", "I am the resurrection, and the life"),
    ("life", "John 14:6", "I am the way, the truth, and the life"),
    ("life", "Acts 17:28", "in him we live, and move, and have our being"),
    ("life", "1 John 5:11", "God hath given to us eternal life"),
    ("life", "Romans 6:23", "the gift of God is eternal life"),
    ("life", "Philippians 1:21", "to live is Christ, and to die is gain"),
    ("life", "2 Timothy 4:7", "I have finished my course, I have kept the faith"),
    ("life", "Hebrews 11:1", "faith is the substance of things hoped for"),
    ("life", "1 Peter 5:7", "he careth for you"),
    ("life", "Deuteronomy 30:19", "I have set before you life and death"),
]


def norm(s):
    """Collapse whitespace and fold straight quotes onto the corpus' curly ones."""
    s = s.replace("'", "\u2019").replace("\u2018", "\u2019")
    return re.sub(r"\s+", " ", s).strip()


def parse_ref(ref):
    head, v = ref.rsplit(":", 1)
    book, ch = head.rsplit(" ", 1)
    return book.strip(), ch.strip(), v.strip()


def verse_text(ref):
    book, ch, v = parse_ref(ref)
    verses = BIBLE.get(book, {}).get(ch)
    if verses is None:
        raise SystemExit(f"{ref} not in corpus")
    match = [x for x in verses if str(x["v"]) == v]
    if not match:
        raise SystemExit(f"{ref} does not exist")
    return norm(match[0]["t"])


out, problems = [], []
for register, ref, want in POOL:
    full = verse_text(ref)
    w = norm(want)
    i = full.lower().find(w.lower())
    if i < 0:
        problems.append(f"not a run of {ref}: {want}")
        continue
    exact = full[i:i + len(w)]
    n = len(exact.split())
    if n > 10:
        problems.append(f"{n} words: {exact}")
    out.append(dict(register=register, ref=ref, text=exact, words=n,
                    on_plate=exact in ON_PLATE))

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)

json.dump(out, open(os.path.join(BASE, "parents-line-pool.json"), "w"),
          ensure_ascii=False, indent=1)
by_reg = {}
for x in out:
    by_reg.setdefault(x["register"], []).append(x)
print(f"{len(out)} verified lines, "
      f"{sum(1 for x in out if x['on_plate'])} of them on a plate now")
for reg, items in by_reg.items():
    free = sum(1 for x in items if not x["on_plate"])
    print(f"  {reg:<12} {len(items):>3} lines, {free:>3} free to swap in")
print(f"word range {min(x['words'] for x in out)}-{max(x['words'] for x in out)}")
for x in out:
    mark = "*" if x["on_plate"] else " "
    print(f" {mark} {x['register']:<12} {x['ref']:<18} {x['words']:>2}w  {x['text']}")
