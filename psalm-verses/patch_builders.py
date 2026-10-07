#!/usr/bin/env python3
"""Wire the versed plates and psalm verses into the three gallery builders.

Every replacement must match exactly once or the script aborts, so a silent
partial patch is impossible.
"""
import os

FILES = ["/Users/sero/love-gallery/build.py",
         "/Users/sero/friends-gallery/build.py",
         "/Users/sero/parents-gallery/build.py"]

EDITS = [
    # 1. load the verse map
    ('''M = json.load(open(os.path.join(BASE, "manifest.json")))
BY = {w["slug"]: w for w in M}''',
     '''M = json.load(open(os.path.join(BASE, "manifest.json")))
BY = {w["slug"]: w for w in M}
VERSE = json.load(open(os.path.join(BASE, "verses.json")))'''),

    # 2. plate(): resolve the verse for this work
    ('''    src = w["source_page"]
    host = "Wikimedia Commons"''',
     '''    src = w["source_page"]
    host = "Wikimedia Commons"
    v = VERSE[slug]'''),

    # 3. plate(): show the versed plate
    ('''          <img src="{w['thumb']}" width="700" alt="{esc(w['title'])} by {esc(w['artist'])}" loading="lazy" decoding="async">''',
     '''          <img src="img/versed-thumb/{slug}.jpg" width="700" alt="{esc(w['title'])} by {esc(w['artist'])}, with {esc(v['ref'])}" loading="lazy" decoding="async">'''),

    # 4. plate(): set the verse beside the note
    ('''          <p class="note">{esc(w['note'])}</p>
          <p class="kw">{tags}</p>''',
     '''          <p class="note">{esc(w['note'])}</p>
          <blockquote class="verse"><p>{esc(v['text'])}</p><cite>{esc(v['ref'])}</cite></blockquote>
          <p class="kw">{tags}</p>'''),

    # 5. index: verse reference column
    ('''            f'<td class="c-med">{esc(w["medium"])}</td></tr>')''',
     '''            f'<td class="c-med">{esc(w["medium"])}</td>'
            f'<td class="c-verse">{esc(VERSE[slug]["ref"])}</td></tr>')'''),
    ('''<tr><th>No.</th><th>Title</th><th>Artist</th><th>Date</th><th class="c-med">Medium</th></tr>''',
     '''<tr><th>No.</th><th>Title</th><th>Artist</th><th>Date</th><th class="c-med">Medium</th><th class="c-verse">Psalm</th></tr>'''),

    # 6. lightbox data: carry the verse and the versed full image
    ('''                 source=BY[slug]["source_page"],
                 license=BY[slug]["source_license"])''',
     '''                 source=BY[slug]["source_page"],
                 license=BY[slug]["source_license"],
                 verse=VERSE[slug]["text"], ref=VERSE[slug]["ref"])'''),
    ('''    data = [dict(n=NUM[slug], full=BY[slug]["full"], thumb=BY[slug]["thumb"],''',
     '''    data = [dict(n=NUM[slug], full="img/versed/%s.jpg" % slug, thumb=BY[slug]["thumb"],'''),

    # 7. lightbox caption: quote the verse
    ('''  cap.innerHTML = '<span class="t">Plate ' + w.n + '. ' + w.title + '</span> &mdash; ' +
    w.artist + ', ' + w.date + '. <span class="m">' + w.medium +
    (w.place ? ', ' + w.place : '') + '.</span>';''',
     '''  cap.innerHTML = '<span class="t">Plate ' + w.n + '. ' + w.title + '</span> &mdash; ' +
    w.artist + ', ' + w.date + '. <span class="m">' + w.medium +
    (w.place ? ', ' + w.place : '') + '.</span>' +
    '<span class="v">&ldquo;' + w.verse + '&rdquo;</span>' +
    '<span class="r">' + w.ref + '</span>';'''),

    # 8. CSS: verse block and index column
    ('''.note {{ font-family: var(--serif); font-size: 14.5px; line-height: 1.55; margin: 0 0 10px; }}''',
     '''.note {{ font-family: var(--serif); font-size: 14.5px; line-height: 1.55; margin: 0 0 10px; }}
.verse {{ margin: 0 0 11px; padding-left: 12px; border-left: 2px solid var(--accent); }}
.verse p {{ font-family: var(--serif); font-size: 14.5px; line-height: 1.5; margin: 0 0 4px; }}
.verse cite {{ font-style: normal; font-size: 10.5px; letter-spacing: .13em; text-transform: uppercase; color: var(--accent); }}'''),
    ('''.c-med {{ color: var(--muted); }}''',
     '''.c-med {{ color: var(--muted); }}
.c-verse {{ white-space: nowrap; font-size: 12px; letter-spacing: .06em; color: var(--accent); }}'''),
    ('''.lb-cap .m {{ color: #b8b2a8; }}''',
     '''.lb-cap .m {{ color: #b8b2a8; }}
.lb-cap .v {{ display: block; margin-top: 6px; font-family: var(--serif); font-size: 14.5px; }}
.lb-cap .r {{ display: block; margin-top: 3px; font-size: 10.5px; letter-spacing: .13em; text-transform: uppercase; color: #b8b2a8; }}'''),

    # 9. prose: say the verses are there
    ('''Click any plate to enlarge it; use the arrow keys to move through the catalogue.</p>''',
     '''Each plate carries a psalm verse set into the image itself, in the King James Version. Click any plate to enlarge it; use the arrow keys to move through the catalogue.</p>'''),
    ('''Each plate links to its source record. Images are downloaded into <code>img/full</code> at 1600&nbsp;px on the long edge, with 700&nbsp;px copies in <code>img/thumb</code> for this page.''',
     '''Each plate links to its source record. Images are downloaded into <code>img/full</code> at 1600&nbsp;px on the long edge, with 700&nbsp;px copies in <code>img/thumb</code> for this page; the plates shown here are the versed copies in <code>img/versed</code> and <code>img/versed-thumb</code>.'''),
]


def main():
    for path in FILES:
        text = open(path).read()
        for old, new in EDITS:
            n = text.count(old)
            if n != 1:
                raise SystemExit(f"{path}: pattern matched {n} times, expected 1:\n{old[:120]}")
            text = text.replace(old, new)
        open(path, "w").write(text)
        print(f"patched {path}")


if __name__ == "__main__":
    main()
