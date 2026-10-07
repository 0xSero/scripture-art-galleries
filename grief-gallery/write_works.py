#!/usr/bin/env python3
"""Write works.py from the selected works, the assigned lines and the notes."""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, "/Users/sero/psalm-verses")
from notes import NOTES  # noqa: E402

SEL = json.load(open("/tmp/grief-selected.json"))
CAND = {c["file_title"]: c for c in json.load(open("/tmp/grief-candidates.json"))}
ASSIGN = json.load(open("/Users/sero/psalm-verses/assignments.json"))["grief-gallery"]
EXCERPTS = json.load(open("/Users/sero/psalm-verses/excerpts.json"))


JUNK = {"cm", "date", "de", "en", "fr", "unknown", "n/a", "-"}


def clean(s):
    return " ".join((s or "").split())


def licence_of(c):
    """The licence template the file page carries, as its short name."""
    sec = c.get("license_section", "")
    body = sec.split("==", 1)[1] if "==" in sec else sec
    if "cc-zero" in body.lower() or "cc0" in body.lower():
        return "CC0"
    for m in re.finditer(r"\{\{\s*([A-Za-z0-9\-_. :]+)", body):
        name = m.group(1).strip().rstrip(":").strip()
        low = name.lower()
        if low.startswith("pd"):
            parts = name.split("-")
            return "PD-" + "-".join(p if p.isupper() else p.lower()
                                     for p in parts[1:]) if len(parts) > 1 else "PD"
    return "public domain"


def title_of(t):
    t = clean(t)
    if len(t) > 78:
        t = t[:78].rsplit(" ", 1)[0] + " \u2026"
    return t


def field(s):
    s = clean(s)
    return "" if s.lower() in JUNK else s


def main():
    rows = []
    for w in SEL:
        slug = w["slug"]
        rows.append({
            "slug": slug,
            "file": clean(w["file_title"]),
            "title": title_of(w["title"]),
            "artist": clean(w["artist"]),
            "date": clean(w["date"]),
            "medium": field(w["medium"]),
            "place": field(w["institution"]),
            "dimensions": field(w["dimensions"]),
            "source": clean(w["source"]),
            "license": licence_of(CAND.get(w["file_title"]) or {}),
            "section": w["section"],
            "ref": ASSIGN[slug],
            "line": EXCERPTS[slug],
            "note": NOTES[slug],
        })
    out = ["#!/usr/bin/env python3",
           '"""The works of "Grief, and the Night", in catalogue order.',
           "",
           "Each work carries the Commons file it was taken from, the metadata the",
           "source record gave, the section it is shown in, and the line of the King",
           "James Bible set into the plate. Fields the record did not give are left",
           'empty rather than guessed."""',
           "",
           "WORKS = ["]
    for r in rows:
        out.append("    {")
        for k in ("slug", "file", "title", "artist", "date", "medium", "place",
                  "dimensions", "source", "license", "section", "ref",
                  "line", "note"):
            out.append(f"        {k!r}: {r[k]!r},")
        out.append("    },")
    out.append("]")
    out.append("")
    out.append("SECTIONS = {}")
    out.append("for _w in WORKS:")
    out.append("    SECTIONS.setdefault(_w['section'], []).append(_w['slug'])")
    out.append("")
    path = os.path.join(BASE, "works.py")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"wrote {path} with {len(rows)} works")
    for sec in sorted({r["section"] for r in rows}):
        print(f"  {sec}: {sum(1 for r in rows if r['section'] == sec)}")


if __name__ == "__main__":
    main()
