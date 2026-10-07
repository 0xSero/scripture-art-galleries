#!/usr/bin/env python3
"""Choose the lines for the grief/night gallery, bucketed so each fits its picture.

The gallery is grouped by subject, so the lines are grouped the same way: the Passion
and the Pietà, the grave, mourning, widows and orphans, the night, and vanity. A work
is assigned a line from the bucket its source category belongs to, and only falls back to
the general pool when a bucket runs out.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
CAND = json.load(open(os.path.join(BASE, "grief-line-candidates.json")))
OUT = os.path.join(BASE, "grief-lines.json")

# bucket rules, checked in order: (bucket, pattern)
BUCKETS = [
    ("tears", re.compile(
        r"\b(weep|wept|weeping|tears?|cry|cried|crying|howl|wail|lament)\w*\b",
        re.I)),
    ("mourning", re.compile(
        r"\b(mourn\w*|sorrow\w*|grief\w*|sigh\w*|groan\w*|heaviness|"
        r"afflict\w*|desolate|desolation|comfort\w*)\b", re.I)),
    ("widows", re.compile(
        r"\b(widow\w*|fatherless|orphan\w*)\b", re.I)),
    ("grave", re.compile(
        r"\b(grave\w*|dust|ashes|death|dead|die|died|dieth|dying|pit|"
        r"sepulchre|tomb\w*|coffin\w*|buried|burial\w*)\b", re.I)),
    ("night", re.compile(
        r"\b(night\w*|dark\w*|shadow\w*|moon|stars?|midnight|twilight|"
        r"evening|cloud\w*)\b", re.I)),
    ("vanity", re.compile(
        r"\b(vanity|vanities|consume\w*|wither\w*|perish\w*|fadeth|fade|"
        r"broken|breaketh|cut off|cut down|swallow\w*)\b", re.I)),
]

# the Passion itself, identified by reference rather than by word: the arrest, the
# trial, the cross, the deposition and the tomb
PASSION = {
    ("Matthew", 26), ("Matthew", 27), ("Mark", 14), ("Mark", 15),
    ("Luke", 22), ("Luke", 23), ("John", 18), ("John", 19),
    ("Isaiah", 53), ("Psalms", 22), ("Psalms", 69), ("Psalms", 88),
    ("Zechariah", 12), ("Zechariah", 13), ("Lamentations", 1),
}

# lines whose voice is vengeance rather than grief, a rebuke of Israel for
# forsaking God, or a dangling fragment
REJECT = re.compile(
    r"\b(smite|smote|slay|slain|kill|killed|destroy|destroyed|destroyer|"
    r"vengeance|avenge|devour|sword|wrath|indignation|recompence|"
    r"studieth destruction|cut off the ropes|graven images|"
    r"babes|dashed|forsaken the LORD|forsaken thy covenant|"
    r"forsaken the right way|forsaken his covert|have forsaken me)\b", re.I)


def bucket_of(c):
    if (c["book"], c["chapter"]) in PASSION:
        return "passion"
    for name, pat in BUCKETS:
        if pat.search(c["text"]):
            return name
    return "general"


def main():
    by_bucket = {}
    for c in CAND:
        if REJECT.search(c["text"]):
            continue
        b = bucket_of(c)
        c["bucket"] = b
        by_bucket.setdefault(b, []).append(c)

    order = ["passion", "tears", "mourning", "grave", "night", "widows",
             "vanity", "general"]
    print("candidates by bucket:")
    for b in order:
        print(f"  {b:<10} {len(by_bucket.get(b, []))}")

    chosen, seen_ref = [], set()
    # how many lines each bucket may contribute to a 200-work gallery
    quota = {"passion": 34, "tears": 30, "mourning": 34, "grave": 40,
             "night": 34, "widows": 16, "vanity": 12, "general": 0}
    for b in order:
        want = quota[b]
        for c in by_bucket.get(b, []):
            if want <= 0:
                break
            if c["ref"] in seen_ref:
                continue
            seen_ref.add(c["ref"])
            chosen_line = c
            chosen_line["bucket"] = b
            chosen.append(chosen_line)
            want -= 1

    json.dump(chosen, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\n{len(chosen)} lines chosen -> {OUT}")
    for b in order:
        items = [c for c in chosen if c["bucket"] == b]
        print(f"\n=== {b} ({len(items)})")
        for c in items:
            print(f"  {c['score']:>3} {c['ref']:<22} {c['words']:>2}w  {c['text']}")


if __name__ == "__main__":
    chosen = []
    main()
