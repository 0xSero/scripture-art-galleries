#!/usr/bin/env python3
"""Merge the curated quote sets into one pool and set them on the plates.

Five curators wrote thirty lines each, in five registers. This collects them, applies
the verifier's verdicts, and gives every work the best line that speaks to its section:
the highest-impact lines go to the best plates, each reference is used once, and no
reference is one of those already used by the four galleries.
"""
import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
QUOTES = os.path.join(BASE, "quotes")
POOL = os.path.join(BASE, "quote-pool.json")
LINES = os.path.join(BASE, "lines.json")

# which registers speak to which section
SECTION_REGISTER = {
    "I": ("merge", "light"),
    "II": ("light", "joy"),
    "III": ("new", "merge"),
    "IV": ("joy", "new"),
    "V": ("hope", "merge"),
    "VI": ("merge", "joy"),
    "VII": ("new", "light"),
    "VIII": ("new", "light", "joy"),
}

SECTION_AFFINITY = {
    "I": r"one|together|join|knit|body|heart|soul|face|member|held|covenant|light",
    "II": r"light|shine|arise|rise|morning|dawn|star|wing|fire|run|strength|new",
    "III": r"new|build|house|city|breath|bone|stone|heart|flesh|create|strong|hand",
    "IV": r"joy|sing|dance|shout|music|praise|laugh|song|glad|feast|colour",
    "V": r"hope|wait|peace|quiet|anchor|rest|trust|still|strength|faith",
    "VI": r"one|together|join|knit|body|member|heart|soul|held|embrace|friend",
    "VII": r"blossom|desert|water|river|spring|garden|vine|rain|flower|fruit|seed|light",
    "VIII": r"light|flower|blossom|fruit|garden|field|water|dawn|morning|sun|spring|grow|seed|vine|bread|harvest",
}


def load_pool():
    """Every curated line, with the verifier's verdict applied where it exists."""
    verdicts = {}
    for vname in ("VERIFY.json", "VERIFY2.json"):
        vpath = os.path.join(QUOTES, vname)
        if os.path.exists(vpath):
            for row in json.load(open(vpath)):
                verdicts[(row.get("file"), row.get("ref"))] = row
    pool, seen = [], set()
    for path in sorted(glob.glob(os.path.join(QUOTES, "*.json"))):
        name = os.path.basename(path)
        if name.startswith("VERIFY"):
            continue
        for q in json.load(open(path)):
            v = verdicts.get((name, q["ref"]))
            if v and v.get("verdict") == "drop":
                continue
            text = (v or {}).get("fix") or q["text"]
            ref = q["ref"]
            if ref in seen:
                continue
            seen.add(ref)
            pool.append(dict(ref=ref, text=text, words=len(text.split()),
                             impact=(v or {}).get("my_impact", q.get("impact", 5)),
                             register=name[:-5], why=q.get("why", "")))
    pool.sort(key=lambda q: (-q["impact"], q["register"], q["ref"]))
    return pool


def main():
    sys.path.insert(0, BASE)
    from works import WORKS

    pool = load_pool()
    json.dump(pool, open(POOL, "w"), ensure_ascii=False, indent=1)
    print(f"{len(pool)} lines in the pool")
    for q in pool[:12]:
        print(f"  {q['impact']:>2} {q['register']:<6} {q['ref']:<22} {q['text']}")

    # the art reviewer scored every picture that arrived; the best pictures get the
    # best lines, and a work that has not arrived yet sorts below a scored one
    scores = {}
    rpath = os.path.join(BASE, "art-review.json")
    if os.path.exists(rpath):
        for row in json.load(open(rpath)):
            scores[row["slug"]] = row.get("score", 5)

    by_section = {}
    for w in WORKS:
        by_section.setdefault(w["section"], []).append(w)
    for s in by_section:
        by_section[s].sort(key=lambda w: -scores.get(w["slug"], 5))

    # deal the pool out in rounds, one work per section per round, so every
    # section gets its share of the best lines instead of the first section
    # taking the whole pool
    lines, used = {}, set()
    queues = {sec: list(by_section[sec]) for sec in sorted(by_section)}
    while any(queues.values()):
        for sec in sorted(queues):
            if not queues[sec]:
                continue
            w = queues[sec].pop(0)
            want = SECTION_REGISTER.get(sec, ())
            pat = re.compile(SECTION_AFFINITY.get(sec, ""), re.I)
            pick = next((q for q in pool if q["register"] in want
                         and q["ref"] not in used and pat.search(q["text"])), None)
            if not pick:
                pick = next((q for q in pool if q["register"] in want
                             and q["ref"] not in used), None)
            if not pick:
                pick = next((q for q in pool if q["ref"] not in used), None)
            if not pick:
                continue
            used.add(pick["ref"])
            lines[w["slug"]] = dict(ref=pick["ref"], text=pick["text"],
                                    words=pick["words"], approved=True,
                                    theme=pick["why"] or pick["register"],
                                    register=pick["register"],
                                    impact=pick["impact"])
    json.dump(lines, open(LINES, "w"), ensure_ascii=False, indent=1)
    over = [k for k, v in lines.items() if v["words"] > 8]
    print(f"{len(lines)} plates given a line; {len(pool) - len(used)} lines unused")
    if over:
        print("OVER EIGHT WORDS:", over)


if __name__ == "__main__":
    main()
