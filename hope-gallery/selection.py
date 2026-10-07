#!/usr/bin/env python3
"""The full selected list, independent of the pruned works.py.

works.py is pruned to the works whose images have arrived, so the page only ever
shows plates it can display. The downloader must not read that pruned list, or it
would stop early: it reads the selection itself, with the licence label resolved the
same way gen_works.py resolves it.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SELECTED = os.environ.get("HOPE_SELECTED", "/tmp/hope3-selected.json")
CANDS = os.environ.get("HOPE_CANDIDATES", "/tmp/hope3-candidates.json")

LIC = re.compile(r"\{\{\s*(PD-[A-Za-z0-9\-_.]+|CC-zero|cc-zero|CC0[^}|]*)", re.I)
PREFER = re.compile(r"^(PD-Art|PD-old-70|PD-old|PD-US-expired|PD-scan|PD-1923|"
                    r"PD-self|PD-1996|CC-zero|PD-old-100)", re.I)


def label(text):
    found = [m.group(1).strip() for m in LIC.finditer(text or "")]
    if not found:
        return "public domain"
    for f in found:
        if PREFER.match(f):
            return f
    return found[0]


def load():
    selected = json.load(open(SELECTED))
    cands = {}
    if os.path.exists(CANDS):
        cands = {c["file_title"]: c for c in json.load(open(CANDS))}
    works = []
    for w in selected:
        c = cands.get(w["file_title"], {})
        works.append(dict(
            slug=w["slug"], file=w["file_title"],
            license=label(c.get("license_section")),
            artist=w["artist"], title=w["title"], date=w["date"],
            medium=w["medium"], institution=w["institution"],
            dimensions=w["dimensions"], source=w["source"],
            section=w["section"], section_title=w["section_title"],
            blurb=w["blurb"], categories=w["categories"]))
    return works


if __name__ == "__main__":
    works = load()
    print(f"{len(works)} selected works")
