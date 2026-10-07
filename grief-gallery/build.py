#!/usr/bin/env python3
"""Build the "Grief, and the Night" page from the works and the downloaded images."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, BASE)
from works import WORKS  # noqa: E402

M = json.load(open(os.path.join(BASE, "manifest.json")))
BY = {w["slug"]: w for w in M}
VERSE = json.load(open(os.path.join(BASE, "verses.json")))

SECTIONS = [
    ("I", "The Passion and the Pietà",
     "The oldest grief in the gallery is the one that was painted most: a body "
     "taken down, held, and then put somewhere. The descent, the lamentation, "
     "the dead Christ across his mother's lap — the subject Western painting "
     "returns to whenever it wants to say something about loss without saying it.",
     "I"),
    ("II", "Deathbeds and the Dead Child",
     "The room where someone is dying, and the hour after. A mother who has just "
     "stopped, a hero dying among mourners, a child's bed with the tribe around "
     "it. These are the smallest rooms in the gallery and the quietest.",
     "II"),
    ("III", "Memento Mori and Vanitas",
     "Skulls, hourglasses, mirrors, a snuffed candle, a letter rack with a skull "
     "behind it. The still life that says you will die was a genre before it was a "
     "moral, and painters kept finding new ways to make the same object strange.",
     "III"),
    ("IV", "The Grave, the Churchyard, the Coffin",
     "Cemeteries, churchyards, burials, epitaphs, a gravedigger at work and a "
     "funeral procession drawn in plan. Where the Passion is the subject, this is "
     "the place: the ground, the gate, the grave already dug.",
     "IV"),
    ("V", "Night, Moonlight, and Ruin",
     "Nocturnes, moonlit water, a wet moon over a London road, and the ruin "
     "standing under a dark sky. The night is not a mood here so much as a "
     "condition: the hour when grief is least interrupted.",
     "V"),
    ("VI", "Mourning, Widows, and Orphans",
     "The people left behind, and the clothes they wear. A widow in black, two "
     "orphans at a table, a mother mourning a village priest, a knight stopped at "
     "a crossroads. Mourning has a costume, and painters have always known it.",
     "VI"),
    ("VII", "Plague, War, and the Angel of Death",
     "Pestilence, battle, execution, and death coming for everyone at once. The "
     "plague of Athens, the martyrdom of the Jesuits in Japan, the execution of "
     "Mary, Queen of Scots. When grief is public it becomes a crowd.",
     "VII"),
]


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def order():
    out = []
    for num, title, blurb, key in SECTIONS:
        slugs = [w["slug"] for w in WORKS if w["section"] == num]
        out.append((num, title, blurb, slugs))
    return out


ORDER = order()
NUM, _n = {}, 0
for _num, _t, _b, _slugs in ORDER:
    for _s in _slugs:
        _n += 1
        NUM[_s] = _n


def plate(slug):
    w = BY[slug]
    n = NUM[slug]
    v = VERSE[slug]
    return f"""      <figure class="plate" id="p{n}">
        <button class="frame" type="button" data-plate="{n}"
                aria-label="Enlarge plate {n}: {esc(w['title'])}">
          <img src="img/versed-thumb/{slug}.jpg" width="700" alt="{esc(w['title'])}{(' by ' + esc(w['artist'])) if w['artist'] else ''}, with {esc(v['ref'])}" loading="lazy" decoding="async">
          <span class="zoom" aria-hidden="true">Enlarge</span>
        </button>
        <figcaption>
          <p class="no"><span class="plateno">Plate {n}</span><span class="dot">&middot;</span><span class="yr">{esc(w['date'])}</span></p>
          <h3 class="ttl">{esc(w['title'])}</h3>
          <p class="by">{esc(w['artist']) or '&mdash;'}</p>
          <p class="md">{esc(w['medium']) or '&mdash;'}{(' &middot; ' + esc(w['place'])) if w['place'] else ''}</p>
          <p class="note">{esc(w['note'])}</p>
          <blockquote class="verse"><p>{esc(v['text'])}</p><cite>{esc(v['ref'])}</cite></blockquote>
          <p class="src"><a href="{esc(w['source_page'])}" rel="noopener">Wikimedia Commons</a><span class="lic">{esc(w['source_license'])}</span></p>
        </figcaption>
      </figure>
"""


def index_rows():
    rows = []
    for n, slug in sorted(((NUM[s], s) for s in BY)):
        w = BY[slug]
        rows.append(
            f'          <tr><td class="c-no"><a href="#p{n}">{n}</a></td>'
            f'<td class="c-ttl"><a href="#p{n}">{esc(w["title"])}</a></td>'
            f'<td class="c-art">{esc(w["artist"]) or "&mdash;"}</td>'
            f'<td class="c-dat">{esc(w["date"]) or "&mdash;"}</td>'
            f'<td class="c-med">{esc(w["medium"]) or "&mdash;"}</td>'
            f'<td class="c-verse">{esc(VERSE[slug]["ref"])}</td></tr>')
    return "\n".join(rows)


def main():
    sections_html = []
    for numeral, title, blurb, slugs in ORDER:
        plates = "\n".join(plate(s) for s in slugs)
        sections_html.append(f"""    <section class="sec" id="sec-{numeral}">
      <header class="sec-h">
        <p class="numeral">{numeral}</p>
        <h2>{esc(title)}</h2>
        <p class="blurb">{esc(blurb)}</p>
      </header>
      <div class="plates">
{plates}      </div>
    </section>
""")

    nav = "".join(
        f'<li><a href="#sec-{num}"><span class="n">{num}</span> {esc(t)}</a></li>'
        for num, t, _, _ in ORDER)

    data = [dict(n=NUM[slug], full="img/versed/%s.jpg" % slug,
                 thumb=BY[slug]["thumb"], title=BY[slug]["title"],
                 artist=BY[slug]["artist"] or "unknown",
                 date=BY[slug]["date"], medium=BY[slug]["medium"],
                 place=BY[slug]["place"], note=BY[slug]["note"],
                 source=BY[slug]["source_page"],
                 license=BY[slug]["source_license"],
                 verse=VERSE[slug]["text"], ref=VERSE[slug]["ref"])
            for slug in BY]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grief, and the Night &mdash; a gallery of classical art</title>
<meta name="description" content="{len(M)} public-domain works of grief, mourning and the night, each carrying a short line from the King James Bible.">
<style>
:root {{
  --paper: #fcfbf9;
  --ink: #17161a;
  --muted: #6c6862;
  --rule: #ddd8d0;
  --rule-soft: #ebe7e1;
  --accent: #3f4a63;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --measure: 68ch;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --paper: #14140f;
    --ink: #ece8e1;
    --muted: #9b958c;
    --rule: #34322c;
    --rule-soft: #24231e;
    --accent: #9aa8c4;
  }}
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.55;
  text-rendering: optimizeLegibility;
}}
.wrap {{ max-width: 1120px; margin: 0 auto; padding: 0 28px 96px; }}
a {{ color: inherit; }}
a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}

header.masthead {{ padding: 72px 0 0; border-bottom: 1px solid var(--rule); }}
.kicker {{ font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); margin: 0 0 20px; }}
h1 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(34px, 6vw, 58px); line-height: 1.04; letter-spacing: -.015em; margin: 0 0 18px; }}
h1 em {{ font-style: italic; color: var(--accent); }}
.lede {{ font-family: var(--serif); font-size: clamp(17px, 2.1vw, 21px); line-height: 1.5; max-width: var(--measure); margin: 0 0 16px; }}
.method {{ max-width: var(--measure); font-size: 14px; line-height: 1.65; color: var(--muted); margin: 0 0 40px; }}
.method b {{ color: var(--ink); font-weight: 600; }}

nav.toc {{ padding: 34px 0 30px; border-bottom: 1px solid var(--rule); }}
nav.toc ol {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px 26px; }}
nav.toc a {{ text-decoration: none; font-size: 13.5px; color: var(--ink); border-bottom: 1px solid transparent; }}
nav.toc a:hover {{ border-bottom-color: var(--accent); }}
nav.toc .n {{ font-family: var(--serif); color: var(--accent); margin-right: 5px; }}

.sec {{ padding-top: 76px; }}
.sec-h {{ border-top: 1px solid var(--ink); padding-top: 16px; margin-bottom: 40px; }}
.numeral {{ font-family: var(--serif); font-size: 12px; letter-spacing: .2em; color: var(--accent); margin: 0 0 8px; }}
.sec-h h2 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(23px, 3.4vw, 31px); letter-spacing: -.01em; margin: 0 0 12px; }}
.blurb {{ font-family: var(--serif); font-size: 16px; line-height: 1.55; color: var(--muted); max-width: var(--measure); margin: 0; }}

.plates {{ column-width: 268px; column-gap: 30px; }}
.plate {{ margin: 0 0 40px; break-inside: avoid; }}
.frame {{ display: block; position: relative; padding: 0; border: 0; background: none; cursor: zoom-in; width: 100%; line-height: 0; }}
.frame img {{ width: 100%; height: auto; display: block; border: 1px solid var(--rule); background: #fff; }}
.zoom {{ position: absolute; right: 9px; bottom: 9px; font-family: var(--sans); font-size: 10px; letter-spacing: .13em; text-transform: uppercase; color: var(--paper); background: rgba(23,22,26,.72); padding: 4px 8px; opacity: 0; transition: opacity .18s ease; }}
.frame:hover .zoom, .frame:focus-visible .zoom {{ opacity: 1; }}
figcaption {{ padding-top: 11px; }}
.no {{ font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 0 0 7px; }}
.dot {{ margin: 0 7px; }}
.ttl {{ font-family: var(--serif); font-weight: 400; font-size: 18px; line-height: 1.25; margin: 0 0 4px; }}
.by {{ font-size: 13px; margin: 0 0 2px; }}
.md, .kw, .src {{ font-size: 12.5px; color: var(--muted); margin: 0; }}
.md {{ margin-bottom: 9px; }}
.note {{ font-family: var(--serif); font-size: 14.5px; line-height: 1.55; margin: 0 0 10px; }}
.verse {{ margin: 0 0 11px; padding-left: 12px; border-left: 2px solid var(--accent); }}
.verse p {{ font-family: var(--serif); font-size: 14.5px; line-height: 1.5; margin: 0 0 4px; }}
.verse cite {{ font-style: normal; font-size: 10.5px; letter-spacing: .13em; text-transform: uppercase; color: var(--accent); }}
.src {{ border-top: 1px solid var(--rule-soft); padding-top: 8px; display: flex; justify-content: space-between; gap: 12px; }}
.src a {{ color: var(--muted); }}
.src a:hover {{ color: var(--accent); }}
.lic {{ white-space: nowrap; }}

#index {{ padding-top: 76px; }}
#index h2 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(23px, 3.4vw, 31px); border-top: 1px solid var(--ink); padding-top: 16px; margin: 0 0 22px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
caption {{ text-align: left; font-size: 12.5px; color: var(--muted); padding-bottom: 12px; }}
th {{ text-align: left; font-weight: 600; font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--rule); padding: 0 14px 8px 0; }}
td {{ border-bottom: 1px solid var(--rule-soft); padding: 9px 14px 9px 0; vertical-align: top; }}
td a {{ text-decoration: none; border-bottom: 1px solid var(--rule); }}
td a:hover {{ color: var(--accent); border-bottom-color: var(--accent); }}
.c-no {{ width: 46px; font-family: var(--serif); color: var(--accent); }}
.c-dat {{ white-space: nowrap; }}
.c-med {{ color: var(--muted); }}
.c-verse {{ white-space: nowrap; font-size: 12px; letter-spacing: .06em; color: var(--accent); }}
tbody tr:hover {{ background: var(--rule-soft); }}

footer {{ margin-top: 84px; border-top: 1px solid var(--rule); padding-top: 26px; font-size: 13px; line-height: 1.7; color: var(--muted); max-width: var(--measure); }}
footer h2 {{ font-family: var(--serif); font-weight: 400; font-size: 17px; color: var(--ink); margin: 0 0 12px; }}
footer code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}

.companion {{ margin-top: 20px; padding-top: 14px; border-top: 1px solid var(--rule-soft); }}
.companion a {{ color: var(--accent); }}
.lb {{ position: fixed; inset: 0; z-index: 50; display: none; background: rgba(12,11,10,.985); color: #f2efe9; padding: 22px; }}
.lb[data-open="1"] {{ display: grid; grid-template-rows: 1fr auto; }}
.lb-stage {{ position: relative; display: flex; align-items: center; justify-content: center; min-height: 0; }}
.lb-stage img {{ max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; }}
.lb-x {{ position: absolute; top: 0; right: 0; background: none; border: 1px solid rgba(242,239,233,.4); color: inherit; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; padding: 7px 11px; cursor: pointer; }}
.lb-cap {{ max-width: 760px; margin: 16px auto 0; font-size: 13px; line-height: 1.5; }}
.lb-cap .t {{ font-family: var(--serif); font-size: 17px; }}
.lb-cap .m {{ color: #b8b2a8; }}
.lb-cap .v {{ display: block; margin-top: 6px; font-family: var(--serif); font-size: 14.5px; }}
.lb-cap .r {{ display: block; margin-top: 3px; font-size: 10.5px; letter-spacing: .13em; text-transform: uppercase; color: #b8b2a8; }}
.lb-nav {{ display: flex; gap: 10px; justify-content: center; margin-top: 14px; }}
.lb-nav button {{ background: none; border: 1px solid rgba(242,239,233,.4); color: inherit; padding: 7px 14px; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; cursor: pointer; }}
.lb-nav button:hover {{ border-color: #f2efe9; }}
body.lb-open {{ overflow: hidden; }}
@media (hover: none) {{ .zoom {{ opacity: 1; }} }}
@media (max-width: 640px) {{
  .wrap {{ padding: 0 18px 72px; }}
  .c-med {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
@media print {{
  .frame .zoom, .lb, nav.toc {{ display: none; }}
  .plates {{ column-width: 45%; }}
  .plate {{ break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <p class="kicker">A gallery of classical art &middot; {len(M)} public-domain works</p>
    <h1>Grief, <em>and the Night</em></h1>
    <p class="lede">Grief is the oldest subject in art and the one it has painted most, so most of the works here hold two things at once: the body that has stopped and the people who have not &mdash; a son taken down and held, a mother who will not let go, a grave already dug, a night that will not lift. The register is dark, and the pictures are almost all dark, and that is the point.</p>
    <p class="method">The selection follows the same bias as the other three galleries: <b>works where the subject is legible and the record is honest</b>. It runs from the Passion and the Pietà, through the deathbed, the memento mori and the vanitas, the grave and the churchyard, the night and the ruin, the people left behind, and last the plague and the angel of death. Every image is public domain or CC0, reproduced from <b>Wikimedia Commons</b> and stored locally beside this page so the gallery works offline. Each plate carries a short line from the <b>King James Bible</b> &mdash; never more than ten words &mdash; set into the image itself, and every line is unique across all four galleries. Click any plate to enlarge it; use the arrow keys to move through the catalogue.</p>
  </header>

  <nav class="toc" aria-label="Contents">
    <ol>
      {nav}
    </ol>
  </nav>

  <main>
{chr(10).join(sections_html)}
    <section id="index">
      <h2>Index of works</h2>
      <table>
        <caption>All {len(M)} plates in catalogue order, with artist, date and medium.</caption>
        <thead>
          <tr><th>No.</th><th>Title</th><th>Artist</th><th>Date</th><th class="c-med">Medium</th><th class="c-verse">Verse</th></tr>
        </thead>
        <tbody>
{index_rows()}
        </tbody>
      </table>
    </section>

    <footer>
      <h2>On the images</h2>
      <p>All {len(M)} reproductions are public domain or released under CC0, taken from Wikimedia Commons and the open-access programmes of the Metropolitan Museum of Art, the Rijksmuseum, the British Museum, the National Gallery of Art, the Harvard Art Museums, the Yale Center for British Art, the Cleveland Museum of Art and the Google Art Project. Each plate links to its source record. Images are downloaded into <code>img/full</code> at 1600&nbsp;px on the long edge, with 700&nbsp;px copies in <code>img/thumb</code> for this page; the plates shown here are the versed copies in <code>img/versed</code> and <code>img/versed-thumb</code>. No photograph carrying a share-alike or attribution licence was used.</p>
      <p>Captions give the artist, date, medium and holding collection as recorded by the source institution, and are left blank where the record does not give them; the notes are editorial and describe what each work does with the body. The gallery is ordered by argument, not by date &mdash; the index at the end gives the works in catalogue order.</p>
      <p class="companion">Companion galleries: <a href="../parents-gallery/index.html">Parents, Abstracted</a> (25 works) &middot; <a href="../love-gallery/index.html">Love, Abstracted</a> (46 works) &middot; <a href="../friends-gallery/index.html">Friends, Abstracted</a> (25 works) &mdash; in the same format.</p>
    </footer>
  </main>
</div>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Enlarged plate">
  <div class="lb-stage">
    <img id="lb-img" alt="">
    <button class="lb-x" id="lb-x" type="button">Close</button>
  </div>
  <div>
    <div class="lb-cap" id="lb-cap"></div>
    <div class="lb-nav">
      <button id="lb-prev" type="button">&larr; Previous</button>
      <button id="lb-next" type="button">Next &rarr;</button>
    </div>
  </div>
</div>

<script>
const WORKS = {json.dumps(data, ensure_ascii=False)};
const lb = document.getElementById('lb');
const img = document.getElementById('lb-img');
const cap = document.getElementById('lb-cap');
let at = 0, last = null;

function render(i) {{
  at = (i + WORKS.length) % WORKS.length;
  const w = WORKS[at];
  img.src = w.full;
  img.alt = w.title + (w.artist ? ' by ' + w.artist : '');
  cap.innerHTML = '<span class="t">Plate ' + w.n + '. ' + w.title + '</span> &mdash; ' +
    (w.artist || 'unknown artist') + (w.date ? ', ' + w.date : '') + '. <span class="m">' + (w.medium || '') +
    (w.place ? (w.medium ? ', ' : '') + w.place : '') + '.</span>' +
    '<span class="v">&ldquo;' + w.verse + '&rdquo;</span>' +
    '<span class="r">' + w.ref + '</span>';
}}
function open(i) {{
  last = document.activeElement;
  render(i);
  lb.dataset.open = '1';
  document.body.classList.add('lb-open');
  document.getElementById('lb-x').focus();
}}
function close() {{
  lb.dataset.open = '0';
  document.body.classList.remove('lb-open');
  img.removeAttribute('src');
  if (last) last.focus();
}}
document.querySelectorAll('.frame').forEach(b => {{
  b.addEventListener('click', () => open(Number(b.dataset.plate) - 1));
}});
document.getElementById('lb-x').addEventListener('click', close);
document.getElementById('lb-prev').addEventListener('click', () => render(at - 1));
document.getElementById('lb-next').addEventListener('click', () => render(at + 1));
lb.addEventListener('click', e => {{ if (e.target === lb) close(); }});
document.addEventListener('keydown', e => {{
  if (lb.dataset.open !== '1') return;
  if (e.key === 'Escape') close();
  if (e.key === 'ArrowLeft') render(at - 1);
  if (e.key === 'ArrowRight') render(at + 1);
}});
</script>
</body>
</html>
"""
    out = os.path.join(BASE, "index.html")
    open(out, "w").write(html)
    print(f"wrote {out} ({len(html)} bytes, {len(M)} plates)")


if __name__ == "__main__":
    main()
