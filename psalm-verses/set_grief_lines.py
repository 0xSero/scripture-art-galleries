#!/usr/bin/env python3
"""Assign the grief/night gallery its 202 Bible lines, one per work.

The gallery is grouped by subject, so the lines are grouped the same way and a work
draws from the bucket its section belongs to, falling back to the next bucket when one
runs out. Lines the earlier pass chose that read as rebuke, as a dangling fragment, or
as a repetition of another line were dropped and replaced from the 963-line pool.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
CAND = json.load(open(os.path.join(BASE, "grief-line-candidates.json")))
KEPT = json.load(open(os.path.join(BASE, "grief-lines.json")))
ASSIGN = json.load(open(os.path.join(BASE, "assignments.json")))
EXCERPTS = json.load(open(os.path.join(BASE, "excerpts.json")))
WORKS = json.load(open("/tmp/grief-selected.json"))

BUCKETS = [
    ("tears", re.compile(r"\b(weep|wept|weeping|tears?|cry|cried|crying|howl|wail|lament)\w*\b", re.I)),
    ("mourning", re.compile(r"\b(mourn\w*|sorrow\w*|grief\w*|sigh\w*|groan\w*|heaviness|afflict\w*|desolate|desolation|comfort\w*)\b", re.I)),
    ("widows", re.compile(r"\b(widow\w*|fatherless|orphan\w*)\b", re.I)),
    ("grave", re.compile(r"\b(grave\w*|dust|ashes|death|dead|die|died|dieth|dying|pit|sepulchre|tomb\w*|coffin\w*|buried|burial\w*)\b", re.I)),
    ("night", re.compile(r"\b(night\w*|dark\w*|shadow\w*|moon|stars?|midnight|twilight|evening|cloud\w*)\b", re.I)),
    ("vanity", re.compile(r"\b(vanity|vanities|consume\w*|wither\w*|perish\w*|fadeth|fade|broken|breaketh|cut off|cut down|swallow\w*)\b", re.I)),
]
PASSION = {
    ("Matthew", 26), ("Matthew", 27), ("Mark", 14), ("Mark", 15),
    ("Luke", 22), ("Luke", 23), ("John", 18), ("John", 19),
    ("Isaiah", 53), ("Psalms", 22), ("Psalms", 69), ("Psalms", 88),
    ("Zechariah", 12), ("Zechariah", 13), ("Lamentations", 1),
}
REJECT = re.compile(
    r"\b(smite|smote|slay|slain|kill|killed|destroy|destroyed|destroyer|"
    r"vengeance|avenge|devour|sword|wrath|indignation|recompence|"
    r"studieth destruction|cut off the ropes|graven images|"
    r"babes|dashed|forsaken the LORD|forsaken thy covenant|"
    r"forsaken the right way|forsaken his covert|have forsaken me)\b", re.I)

# lines dropped from the first pass: rebuke rather than grief, dangling
# fragments, one obscure genealogy, and three copies of the same verse
WEAK = {
    "Mark 14:30", "Ezekiel 7:16", "Jeremiah 8:1", "Amos 8:3",
    "Genesis 36:39", "Genesis 50:16", "Job 28:22", "Luke 20:32",
    "Mark 12:22", "Matthew 22:27", "Job 34:22", "Luke 11:34",
    "Matthew 6:23", "Proverbs 4:19", "1 John 2:11", "Isaiah 10:2",
    "Luke 18:5", "Psalms 83:10", "Isaiah 14:28", "Isaiah 1:28",
    "Jeremiah 46:23", "Ezekiel 39:10", "Isaiah 10:18",
    "Deuteronomy 26:14", "Isaiah 15:4", "1 Timothy 5:16", "Acts 6:1",
    "Ezekiel 22:25", "Ezekiel 22:7", "Jeremiah 48:36", "Isaiah 24:7",
    "Jeremiah 16:7", "Matthew 27:53", "Psalms 78:64",
}

# the section a bucket of lines may serve, in order of preference
FOR_SECTION = {
    "I": ["passion", "tears", "grave"],
    "II": ["tears", "grave", "mourning"],
    "III": ["vanity", "grave", "mourning"],
    "IV": ["grave", "mourning", "tears"],
    "V": ["night", "grave", "mourning"],
    "VI": ["mourning", "widows", "tears"],
    "VII": ["widows", "grave", "tears", "passion"],
}


def bucket_of(c):
    if (c["book"], c["chapter"]) in PASSION:
        return "passion"
    for name, pat in BUCKETS:
        if pat.search(c["text"]):
            return name
    return "general"


def usable(c):
    return not REJECT.search(c["text"]) and 4 <= c["words"] <= 10


def main():
    used_elsewhere = {r for g, d in ASSIGN.items() for r in d.values()}
    pool = []
    for c in CAND:
        if not usable(c):
            continue
        c = dict(c, bucket=bucket_of(c))
        pool.append(c)
    by_bucket = {}
    for c in pool:
        by_bucket.setdefault(c["bucket"], []).append(c)
    for b in by_bucket:
        by_bucket[b].sort(key=lambda c: -c["score"])

    kept = [c for c in KEPT if c["ref"] not in WEAK]
    print(f"kept {len(kept)} of {len(KEPT)} first-pass lines, dropped {len(KEPT) - len(kept)}")

    chosen = [dict(c) for c in kept]
    have = {c["ref"] for c in chosen}
    have |= used_elsewhere
    rest = sorted((c for c in pool if c["ref"] not in have),
                  key=lambda c: -c["score"])
    for c in rest:
        if len(chosen) >= len(WORKS):
            break
        have.add(c["ref"])
        chosen.append(dict(c))
    if len(chosen) < len(WORKS):
        raise SystemExit(f"only {len(chosen)} lines for {len(WORKS)} works")

    # deal the lines out section by section, from the bucket each section prefers
    by_bucket = {}
    for c in chosen:
        by_bucket.setdefault(c["bucket"], []).append(c)
    for b in by_bucket:
        by_bucket[b].sort(key=lambda c: -c["score"])
    taken, assign, excerpts = set(), {}, {}
    for w in WORKS:
        slug, sec = w["slug"], w["section"]
        line = None
        for b in FOR_SECTION[sec] + ["general"]:
            for c in by_bucket.get(b, []):
                if c["ref"] not in taken:
                    line = c
                    break
            if line:
                break
        if not line:
            raise SystemExit(f"no line left for {slug} ({sec})")
        taken.add(line["ref"])
        assign[slug] = line["ref"]
        excerpts[slug] = line["text"]

    ASSIGN["grief-gallery"] = assign
    for slug, text in excerpts.items():
        EXCERPTS[slug] = text
    json.dump(ASSIGN, open(os.path.join(BASE, "assignments.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(EXCERPTS, open(os.path.join(BASE, "excerpts.json"), "w"),
              ensure_ascii=False, indent=1)

    counts = {}
    for slug, ref in assign.items():
        sec = next(w["section"] for w in WORKS if w["slug"] == slug)
        counts[sec] = counts.get(sec, 0) + 1
    print(f"{len(assign)} lines for {len(WORKS)} works")
    for sec in sorted(counts):
        print(f"  {sec}: {counts[sec]}")
    print(f"excerpts now {len([k for k in EXCERPTS if not k.startswith('_')])}")


if __name__ == "__main__":
    main()
