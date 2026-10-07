#!/usr/bin/env python3
"""Build the "Hope, and the Light" page from the works, the lines and the images.

Same dense catalogue format as the other galleries, but the treatment is different:
the quote sits on a clean flat panel at 85% rather than a blurred scrim, the type is
Gill Sans rather than Charter, and the text is the World English Bible.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from works import WORKS  # noqa: E402

M = json.load(open(os.path.join(BASE, "manifest.json")))
BY = {w["slug"]: w for w in M}
LINES = json.load(open(os.path.join(BASE, "lines.json")))
# the manifest is rebuilt while the page is built, so only works that have both an
# image and a line are shown; a work missing either is left out rather than crashing
SHOWN = [w for w in WORKS if w["slug"] in BY and w["slug"] in LINES]
CSS = open(os.path.join(BASE, "gallery.css")).read()

SECTIONS = [
    ("I", "Cubism \u2014 the world taken apart",
     "The first movement to break the picture into facets and put it back differently. "
     "Braque and Picasso are still in copyright; the men and women who built Cubism "
     "beside them are not, and their work is the spine of this section: Le Fauconnier's "
     "Brittany cliffs, Kupka's Babylon, Juan Gris drawing in Barcelona, Valmier's tulips "
     "and Popova's standing figure."),
    ("II", "Futurism \u2014 speed, light, noise",
     "The Italians who wanted the picture to move. Lines of force, a city seen from every "
     "side at once, light treated as a solid: Russolo's revolt and his music, Boccioni's "
     "elasticity and his cyclist, Sant'Elia's terraced houses with lifts, Bogomazov's tram."),
    ("III", "Constructivism \u2014 building the new",
     "Art turned into construction: the drawing board, the beam, the diagonal used as an "
     "argument. Malevich, Kliun, Rozanova, Popova and El Lissitzky, every one of them out "
     "of copyright, all of them building a picture the way an engineer builds a bridge."),
    ("IV", "The Blue Rider \u2014 colour as feeling",
     "Kandinsky, Klee, Marc, Macke, Jawlensky and Werefkin: colour used the way music is "
     "used, to say something that has no object in it at all. The most positive painting in "
     "the gallery is here, and it is positive without describing anything."),
    ("V", "De Stijl \u2014 the grid",
     "Mondrian and Van Doesburg reduced the picture to straight lines, right angles and three "
     "colours, and found in that reduction a kind of quiet. Nothing in the gallery is calmer, "
     "and nothing is more completely made of parts that agree with one another."),
    ("VI", "Merging \u2014 hands, circles, dancers",
     "Figures that join: hands held, circles closed, spirals turning, dancers paired, two "
     "people walking the same way. The oldest pictures of coming together, painted long before "
     "anyone had a word for abstraction."),
    ("VII", "Light and spring \u2014 the open window",
     "The positive subject at its plainest: rainbows, butterflies, open windows, bridges, "
     "spring coming back and light let into a room. The section is the reason the gallery "
     "exists, and it is the largest."),
    ("VIII", "The old light \u2014 painting before the moderns",
     "The paintings the moderns were arguing with. Flowers and fruit, dawn and water, "
     "made by hand three hundred years before the picture was broken into facets: "
     "De La Corte's roses around carved masks, Ruysch and Mignon and Van Huysum, "
     "and the first light of Elsheimer, Claude, Turner and Friedrich."),
]


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def order():
    return [(num, title, blurb, [w["slug"] for w in SHOWN if w["section"] == num])
            for num, title, blurb in SECTIONS]


ORDER = order()
NUM, _n = {}, 0
for _num, _t, _b, _slugs in ORDER:
    for _s in _slugs:
        _n += 1
        NUM[_s] = _n


def note_of(w):
    line = LINES.get(w["slug"], {})
    if line.get("approved") and line.get("theme"):
        return line["theme"]
    bits = [w["medium"] or "print", w["date"] or "undated"]
    if w["institution"]:
        bits.append(w["institution"])
    return ", ".join(bits)


def plate(slug):
    w = BY[slug]
    n = NUM[slug]
    v = LINES[slug]
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
          <p class="md">{esc(w['medium']) or '&mdash;'}{(' &middot; ' + esc(w['institution'])) if w['institution'] else ''}</p>
          <p class="note">{esc(note_of(w))}</p>
          <blockquote class="verse"><p>{esc(v['text'])}</p><cite>{esc(v['ref'])}</cite></blockquote>
          <p class="src"><a href="{esc(w['source_page'])}" rel="noopener">Wikimedia Commons</a><span class="lic">{esc(w['source_license'])}</span></p>
        </figcaption>
      </figure>
"""


def index_rows():
    rows = []
    for n, slug in sorted(((NUM[s], s) for s in BY if s in NUM)):
        w = BY[slug]
        v = LINES[slug]
        rows.append(
            f'          <tr><td class="c-no"><a href="#p{n}">{n}</a></td>'
            f'<td class="c-ttl"><a href="#p{n}">{esc(w["title"])}</a></td>'
            f'<td class="c-art">{esc(w["artist"]) or "&mdash;"}</td>'
            f'<td class="c-dat">{esc(w["date"]) or "&mdash;"}</td>'
            f'<td class="c-med">{esc(w["medium"]) or "&mdash;"}</td>'
            f'<td class="c-sec">{w["section"]}</td>'
            f'<td class="c-verse">{esc(v["ref"])}</td></tr>')
    return "\n".join(rows)


EXTRA_CSS = """
.c-sec { width: 34px; font-family: var(--serif); color: var(--accent); }
.verse p { font-family: var(--sans); }
.plate .verse p { font-size: 15px; line-height: 1.45; }
.qsrc { font-size: 11.5px; color: var(--muted); margin: 8px 0 0; }
.prov { font-size: 11.5px; color: var(--muted); margin: 6px 0 0; }
"""


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
                 place=BY[slug]["institution"], note=note_of(BY[slug]),
                 source=BY[slug]["source_page"],
                 license=BY[slug]["source_license"],
                 verse=LINES[slug]["text"], ref=LINES[slug]["ref"],
                 approved=LINES[slug].get("approved", False))
            for slug in BY if slug in NUM]

    napp = sum(1 for s in NUM if LINES.get(s, {}).get("approved"))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hope, and the Light &mdash; a gallery of modern art</title>
<meta name="description" content="{len(SHOWN)} public-domain works of hope, merging and light, each carrying a short line from the World English Bible.">
<style>
{CSS}
{EXTRA_CSS}
</style>
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <p class="kicker">Hopecore &middot; a gallery of modern art &middot; {len(SHOWN)} public-domain works</p>
    <h1>Hope, <em>and the Light</em></h1>
    <p class="lede">The other galleries gather what is lost. This one gathers what is joined: facets put back together, colour that means nothing and lifts anyway, lines that agree, two figures walking the same way, a window with the light coming through it. Picasso and Escher are still in copyright, so the pictures here are by the people who did the same work beside them &mdash; the Cubists, the Futurists, the Constructivists, the Blue Rider, De Stijl &mdash; and by the older painters of merging, light and spring.</p>
    <p class="method">Each plate carries one line of scripture, <b>never more than eight words</b>, set into the image on a flat panel at 85% so the art still shows through and the type stays fully legible. The wording is the <b>World English Bible</b>, a public-domain modern-English translation; the <b>New International Version</b> is under copyright and is not reproduced here. Of the {len(SHOWN)} lines, <b>{napp}</b> were taken from the curated list and the rest from a mined list of literal four-to-eight-word clauses; every reference is unique across all five galleries. All reproductions are public domain or CC0, stored locally beside this page. Click any plate to enlarge it; use the arrow keys to move through the catalogue.</p>
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
        <caption>All {len(M)} plates in catalogue order, with artist, date, medium and section.</caption>
        <thead>
          <tr><th>No.</th><th>Title</th><th>Artist</th><th>Date</th><th class="c-med">Medium</th><th>Sec.</th><th class="c-verse">Verse</th></tr>
        </thead>
        <tbody>
{index_rows()}
        </tbody>
      </table>
    </section>

    <footer>
      <h2>On the images and the text</h2>
      <p>All {len(M)} reproductions are public domain or released under CC0, taken from Wikimedia Commons and the open-access programmes of the Metropolitan Museum of Art, the Rijksmuseum, the National Gallery of Art, the Art Institute of Chicago, the Cleveland Museum of Art and the Google Art Project. Each plate links to its source record. Images are downloaded into <code>img/full</code> at 1600&nbsp;px on the long edge, with 700&nbsp;px copies in <code>img/thumb</code>; the plates shown here are the versed copies in <code>img/versed</code> and <code>img/versed-thumb</code>. Nothing made after 1945 was used, and no photograph carrying a share-alike or attribution licence.</p>
      <p>The scripture text is the <b>World English Bible</b>, which is in the public domain; the wording was not taken from the New International Version, which is copyright &copy; Biblica and is quoted here only by reference. Lines are literal runs of four to eight words from the verse cited beneath them, and the reference is given with each plate. Captions give the artist, date, medium and holding collection as recorded by the source institution, and are left blank where the record does not give them; the notes are editorial, and describe what the picture is doing rather than what it is of.</p>
      <p>The gallery is ordered by argument, not by date &mdash; seven strands of the same positive subject &mdash; and the index at the end gives every work in catalogue order.</p>
      <p class="companion">Companion galleries: <a href="../grief-gallery/index.html">Grief, and the Night</a> (201 works) &middot; <a href="../parents-gallery/index.html">Parents, Abstracted</a> (25) &middot; <a href="../love-gallery/index.html">Love, Abstracted</a> (46) &middot; <a href="../friends-gallery/index.html">Friends, Abstracted</a> (25) &middot; <a href="../love-and-friendship/index.html">Love and Friendship in the Bible</a> (41 passages).</p>
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
    '<span class="r">' + w.ref + ' &middot; World English Bible</span>';
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
    print(f"wrote {out} ({len(html)} bytes, {len(NUM)} plates, {napp} approved lines)")


if __name__ == "__main__":
    main()
