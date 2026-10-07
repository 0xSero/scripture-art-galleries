#!/usr/bin/env python3
"""Build the gallery page from manifest.json."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(BASE, "manifest.json")))
BY = {w["slug"]: w for w in M}
VERSE = json.load(open(os.path.join(BASE, "verses.json")))

SECTIONS = [
    ("I", "Two Figures",
     "Friendship has no classical emblem, so art arrives at it through the "
     "pair: two bodies that have chosen each other, with the whole "
     "relationship carried in a stance.",
     ["ruth-naomi", "visitation", "achilles-patroclus", "david-jonathan",
      "two-men-moon"]),
    ("II", "Making Music Together",
     "The most reliable image of friendship in European painting is not an "
     "embrace but an ensemble: people who have to listen to each other in order "
     "to stay together.",
     ["the-concert-vermeer", "the-musicians-caravaggio", "three-musicians",
      "concert-honthorst", "music-in-the-tuileries"]),
    ("III", "A Portrait of Friends",
     "Artists painting the people they worked beside, which turns out to be a "
     "genre of its own: the studio, the homage, the friend at his easel.",
     ["hommage-delacroix", "studio-batignolles", "rue-de-la-condamine",
      "gauguin-sunflowers", "sargents-monet"]),
    ("IV", "Company in the Everyday",
     "Friendship as ordinary proximity: cards, a café table, a theatre box, a "
     "line of boys, a quarry full of men.",
     ["card-players", "absinthe-drinker", "the-balcony", "snap-the-whip",
      "swimming-hole"]),
    ("V", "Old Friends, and the Empty Chair",
     "What is left when company goes: two old men, a vacant chair, a house "
     "still waiting, and a chain of hands in the dark.",
     ["two-old-men-disputing", "two-old-men-soup", "gauguins-chair",
      "gassed", "yellow-house"]),
]

# fill in plate numbers in catalogue order
order, n = [], 0
for _, _, _, slugs in SECTIONS:
    for s in slugs:
        n += 1
        order.append((n, s))

missing = [s for _, s in order if s not in BY]
if missing:
    raise SystemExit("slugs missing from manifest: " + ", ".join(missing))
extra = set(BY) - {s for _, s in order}
if extra:
    raise SystemExit("manifest slugs not placed in a section: " + ", ".join(sorted(extra)))

NUM = {slug: n for n, slug in order}


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def plate(slug):
    w = BY[slug]
    n = NUM[slug]
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in w.get("tags", []))
    src = w["source_page"]
    host = "Wikimedia Commons"
    v = VERSE[slug]
    return f"""      <figure class="plate" id="p{n}">
        <button class="frame" type="button" data-plate="{n}"
                aria-label="Enlarge plate {n}: {esc(w['title'])}">
          <img src="img/versed-thumb/{slug}.jpg" width="700" alt="{esc(w['title'])} by {esc(w['artist'])}, with {esc(v['ref'])}" loading="lazy" decoding="async">
          <span class="zoom" aria-hidden="true">Enlarge</span>
        </button>
        <figcaption>
          <p class="no"><span class="plateno">Plate {n}</span><span class="dot">&middot;</span><span class="yr">{esc(w['date'])}</span></p>
          <h3 class="ttl">{esc(w['title'])}</h3>
          <p class="by">{esc(w['artist'])}</p>
          <p class="md">{esc(w['medium'])}{(' &middot; ' + esc(w['place'])) if w.get('place') else ''}</p>
          <p class="note">{esc(w['note'])}</p>
          <blockquote class="verse"><p>{esc(v['text'])}</p><cite>{esc(v['ref'])}</cite></blockquote>
          <p class="kw">{tags}</p>
          <p class="src"><a href="{esc(src)}" rel="noopener">{host}</a><span class="lic">{esc(w['source_license'])}</span></p>
        </figcaption>
      </figure>
"""


def index_rows():
    rows = []
    for n, slug in sorted(order):
        w = BY[slug]
        rows.append(
            f'          <tr><td class="c-no"><a href="#p{n}">{n}</a></td>'
            f'<td class="c-ttl"><a href="#p{n}">{esc(w["title"])}</a></td>'
            f'<td class="c-art">{esc(w["artist"])}</td>'
            f'<td class="c-dat">{esc(w["date"])}</td>'
            f'<td class="c-med">{esc(w["medium"])}</td>'
            f'<td class="c-verse">{esc(VERSE[slug]["ref"])}</td></tr>')
    return "\n".join(rows)


def main():
    sections_html = []
    for numeral, title, blurb, slugs in SECTIONS:
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
        for num, t, _, _ in SECTIONS)

    data = [dict(n=NUM[slug], full="img/versed/%s.jpg" % slug, thumb=BY[slug]["thumb"],
                 title=BY[slug]["title"], artist=BY[slug]["artist"],
                 date=BY[slug]["date"], medium=BY[slug]["medium"],
                 place=BY[slug].get("place", ""), note=BY[slug]["note"],
                 source=BY[slug]["source_page"],
                 license=BY[slug]["source_license"],
                 verse=VERSE[slug]["text"], ref=VERSE[slug]["ref"])
            for slug in BY]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friends, Abstracted &mdash; a gallery of classical art</title>
<meta name="description" content="{len(M)} public-domain works on friendship, in which company is dissolved into posture, rhythm and geometry while remaining unmistakably human.">
<style>
:root {{
  --paper: #fcfbf9;
  --ink: #17161a;
  --muted: #6c6862;
  --rule: #ddd8d0;
  --rule-soft: #ebe7e1;
  --accent: #8a3b3b;
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
    --accent: #d08a7a;
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
.lede {{ font-family: var(--serif); font-size: clamp(17px, 2.1vw, 21px); line-height: 1.5; max-width: var(--measure); color: var(--ink); margin: 0 0 16px; }}
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
.tag {{ display: inline-block; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); border: 1px solid var(--rule); padding: 2px 7px; margin: 0 5px 5px 0; }}
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
    <h1>Friends, <em>Abstracted</em></h1>
    <p class="lede">Friendship has no classical emblem &mdash; there is no Venus of it and no Madonna &mdash; so art arrives at it through the pair instead: two bodies that have chosen each other, standing, listening, working or waiting, with the whole relationship carried in a stance.</p>
    <p class="method">The selection follows the same bias as the love and parents galleries: <b>works where the abstraction and the human survive together</b>. It runs from the pair in ancient sculpture, through ensembles making music, through artists painting the people they worked beside, into ordinary company and the empty chair it leaves. Every image is public domain or CC0, reproduced from <b>Wikimedia Commons</b> and stored locally beside this page so the gallery works offline. Each plate carries a psalm verse set into the image itself, in the King James Version. Click any plate to enlarge it; use the arrow keys to move through the catalogue.</p>
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
          <tr><th>No.</th><th>Title</th><th>Artist</th><th>Date</th><th class="c-med">Medium</th><th class="c-verse">Psalm</th></tr>
        </thead>
        <tbody>
{index_rows()}
        </tbody>
      </table>
    </section>

    <footer>
      <h2>On the images</h2>
      <p>All {len(M)} reproductions are public domain or released under CC0, taken from Wikimedia Commons and the open collections of Alte Nationalgalerie, Amon Carter Museum, Antikensammlung, Butler Institute of American Art, Gemäldegalerie, Hermitage Museum, Imperial War Museum, Isabella Stewart Gardner Museum, Museo del Prado, Musée d'Orsay, Musée du Louvre, National Gallery, National Gallery of Victoria, Scrovegni Chapel, Tate Britain, The Metropolitan Museum of Art and Van Gogh Museum, with further images from the Google Art Project. Each plate links to its source record. Images are downloaded into <code>img/full</code> at 1600&nbsp;px on the long edge, with 700&nbsp;px copies in <code>img/thumb</code> for this page; the plates shown here are the versed copies in <code>img/versed</code> and <code>img/versed-thumb</code>. No photograph carrying a share-alike or attribution licence was used.</p>
      <p>Captions give the artist, date, medium and holding collection as recorded by the source institution; the notes are editorial and describe what each work does to the pair or the group. The gallery is ordered by argument, not by date &mdash; the index at the end gives the works in catalogue order.</p>
      <p class="companion">Companion galleries: <a href="../love-gallery/index.html">Love, Abstracted</a> &middot; <a href="../parents-gallery/index.html">Parents, Abstracted</a> &mdash; twenty-five works each, in the same format.</p>
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
  img.alt = w.title + ' by ' + w.artist;
  cap.innerHTML = '<span class="t">Plate ' + w.n + '. ' + w.title + '</span> &mdash; ' +
    w.artist + ', ' + w.date + '. <span class="m">' + w.medium +
    (w.place ? ', ' + w.place : '') + '.</span>' +
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
