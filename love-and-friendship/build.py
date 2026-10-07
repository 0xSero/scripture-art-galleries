#!/usr/bin/env python3
"""Build a reading page: the Bible on love, and the Bible on friendship.

The text is the King James Version, taken whole from the corpus the galleries use, so
every passage is quoted in full rather than excerpted. The notes are editorial.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
BIBLE = json.load(open("/Users/sero/psalm-verses/kjv-bible.json"))

LOVE = [
    ("1 John", "4", 7, 21, "God is love",
     "The clearest statement of the subject in the Bible, and the one that turns it "
     "into an obligation: if God loved us, we ought also to love one another.",
     [8, 16, 19]),
    ("John", "3", 14, 21, "For God so loved the world",
     "The verse everybody knows, in the argument it actually belongs to — love "
     "measured by what it is willing to give up.",
     [16]),
    ("Romans", "8", 31, 39, "Who shall separate us",
     "Paul at his most uncompromising: a list of everything that might come between "
     "God and his people, and the verdict that none of it can.",
     [35, 38, 39]),
    ("Hosea", "11", 1, 11, "When Israel was a child",
     "God as a parent teaching a child to walk, and then unable to let him go. The "
     "tenderest passage in the prophets.",
     [1, 3, 8]),
    ("Jeremiah", "31", 1, 6, "I have loved thee with an everlasting love",
     "The promise of return, given to a people already in exile, and grounded not in "
     "their faithfulness but in his.",
     [3]),
    ("Isaiah", "54", 4, 10, "With everlasting kindness",
     "A deserted wife told she will not be forgotten; the covenant of peace put in the "
     "language of a marriage.",
     [8, 10]),
    ("Deuteronomy", "6", 4, 9, "Thou shalt love the LORD thy God",
     "The Shema, and the first commandment of love: whole heart, whole soul, whole "
     "might, and taught to the children.",
     [4, 5]),
    ("Psalms", "103", 8, 14, "Like as a father pitieth his children",
     "Love described by what it remembers and what it does not hold against you.",
     [13]),
    ("1 Corinthians", "13", 1, 13, "The greatest of these is charity",
     "Thirteen verses that are read at weddings and funerals both, and the only place "
     "in the Bible where love is defined by what it does without.",
     [4, 13]),
    ("Song of Solomon", "2", 1, 17, "My beloved is mine",
     "Spring, and the voice of the beloved at the window. The Bible's love poem at its "
     "most lyrical.",
     [4, 16]),
    ("Song of Solomon", "8", 6, 7, "Love is strong as death",
     "One verse that puts love and death in the same scale, and finds love heavier — "
     "jealousy cruel as the grave, and many waters unable to quench it.",
     [6, 7]),
    ("Genesis", "29", 15, 20, "Jacob served seven years for Rachel",
     "Seven years that seemed but a few days, for the love he had to her. The plainest "
     "account of what love costs and how it feels.",
     [20]),
    ("Matthew", "22", 34, 40, "On these two commandments hang all the law",
     "The lawyer's question, and the answer that reduces everything to love of God and "
     "love of neighbour.",
     [37, 39, 40]),
    ("Leviticus", "19", 9, 18, "Thou shalt love thy neighbour as thyself",
     "The command in the law book, in a chapter mostly about leaving the corners of "
     "the field for the poor.",
     [18]),
    ("John", "13", 31, 35, "A new commandment I give unto you",
     "Given on the night he was betrayed, and given as a sign: by this shall all men "
     "know that ye are my disciples.",
     [34, 35]),
    ("John", "15", 9, 17, "Greater love hath no man than this",
     "The vine, the branches, and the command to love — the passage that also calls "
     "the disciples friends rather than servants.",
     [13, 15]),
    ("Romans", "12", 9, 21, "Let love be without dissimulation",
     "Love as a list of practical instructions: abhor evil, cleave to good, feed your "
     "enemy, overcome evil with good.",
     [9, 15, 21]),
    ("1 Peter", "4", 8, 11, "Charity shall cover the multitude of sins",
     "Love put among the ordinary duties of hospitality, and given the largest of "
     "promises.",
     [8]),
    ("1 John", "3", 14, 18, "Let us not love in word",
     "The test of love moved from feeling to deed: whoso hath this world's good, and "
     "shutteth up his bowels of compassion.",
     [16, 18]),
    ("Ruth", "1", 14, 18, "Thy people shall be my people",
     "A daughter-in-law's vow to a mother-in-law, made after both their husbands are "
     "dead — love and friendship in the same speech.",
     [16, 17]),
]

FRIENDSHIP = [
    ("1 Samuel", "18", 1, 4, "The soul of Jonathan was knit with the soul of David",
     "The Bible's first great friendship, made in a single verse and sealed with a robe "
     "and a sword.",
     [1, 3]),
    ("1 Samuel", "20", 12, 17, "The LORD be between thee and me for ever",
     "A covenant made in a field, between the heir to the throne and the man who will "
     "take it — Jonathan chooses David anyway.",
     [16, 17]),
    ("1 Samuel", "23", 14, 18, "Jonathan strengthened his hand in God",
     "The last meeting: Jonathan goes to David in the wilderness to tell him not to be "
     "afraid, though he knows what it costs him.",
     [16, 17]),
    ("2 Samuel", "1", 17, 27, "Very pleasant hast thou been unto me",
     "David's lament for Saul and Jonathan, and the one line that has kept their "
     "friendship alive: passing the love of women.",
     [23, 26]),
    ("Proverbs", "17", 17, 17, "A friend loveth at all times",
     "One verse, and a whole doctrine of friendship: constancy, and a brother born for "
     "adversity.",
     [17]),
    ("Proverbs", "18", 24, 24, "There is a friend that sticketh closer than a brother",
     "The other half of the proverb: the friend you keep is worth more than the family "
     "you are given.",
     [24]),
    ("Proverbs", "27", 5, 17, "Iron sharpeneth iron",
     "Friendship as plain dealing: open rebuke better than hidden love, the wounds of a "
     "friend faithful, and counsel that sharpens a face.",
     [6, 9, 17]),
    ("Ecclesiastes", "4", 7, 12, "Two are better than one",
     "The loneliest book in the Bible on company: a threefold cord is not quickly "
     "broken.",
     [9, 10, 12]),
    ("Job", "2", 11, 13, "They sat down with him seven days",
     "Three friends come to comfort Job, and do the one thing that helps: they say "
     "nothing for a week.",
     [11, 13]),
    ("Job", "6", 14, 21, "Pity should be shewed from his friend",
     "Job's reply to the friends who have just spoken: the disappointment of being "
     "argued with instead of comforted.",
     [14]),
    ("Job", "16", 20, 22, "Mine eye poureth out tears unto God",
     "Job with no one left to plead his case, asking for a friend who will stand "
     "between him and God.",
     [20, 21]),
    ("Exodus", "33", 7, 11, "As a man speaketh unto his friend",
     "Moses in the tabernacle, and God talking with him face to face — friendship "
     "with God described in the plainest human terms.",
     [11]),
    ("2 Kings", "2", 1, 14, "My father, my father",
     "Elisha will not leave Elijah, and asks for a double portion of his spirit; the "
     "chariot parts them at the Jordan.",
     [2, 6, 12]),
    ("John", "11", 1, 44, "Jesus wept",
     "Lazarus dead four days, and the shortest verse in the Bible standing in the "
     "middle of the longest friendship in the Gospels.",
     [3, 5, 35, 36]),
    ("John", "15", 12, 15, "I have called you friends",
     "The disciples promoted from servants to friends, on the ground that a servant does "
     "not know what his lord does.",
     [13, 15]),
    ("James", "2", 20, 24, "Abraham was called the friend of God",
     "Faith argued from a friendship: Abraham believed God, and it was imputed to him "
     "for righteousness.",
     [23]),
    ("Acts", "20", 17, 38, "Sorrowing most of all",
     "Paul's farewell to the elders of Ephesus: the parting that hurts most is the "
     "thought of not seeing a face again.",
     [36, 37, 38]),
    ("Romans", "16", 1, 16, "Greet Priscilla and Aquila",
     "A chapter that is mostly a list of names — the only place in the New Testament "
     "where the friends of one man are all recorded together.",
     [3, 4, 13]),
    ("Philippians", "4", 1, 3, "My joy and crown",
     "Paul to the church that supported him: the people he wants to see, and the two "
     "women he asks to agree.",
     [1, 3]),
    ("2 Timothy", "4", 9, 16, "Only Luke is with me",
     "The last letter, near the end: Demas has gone, and the list of the friends who "
     "stayed and the friends who did not.",
     [9, 11, 16]),
    ("Philemon", "1", 4, 22, "A brother beloved",
     "A whole letter written to ask a favour for a runaway slave who has become a "
     "friend — friendship as the ground of a request.",
     [7, 16]),
]


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def verses(book, ch, a, b):
    chapter = BIBLE[book][str(ch)]
    want = {v["v"]: v["t"] for v in chapter if a <= v["v"] <= b}
    missing = [n for n in range(a, b + 1) if n not in want]
    if missing:
        raise SystemExit(f"{book} {ch}: missing verses {missing}")
    return want


def passage_html(slug, p, num):
    book, ch, a, b, title, note, keys = p
    vs = verses(book, ch, a, b)
    ref = f"{book} {ch}:{a}" if a == b else f"{book} {ch}:{a}\u2013{b}"
    body = []
    for n in sorted(vs):
        cls = "v key" if n in keys else "v"
        body.append(f'          <p class="{cls}"><span class="vn">{n}</span>{esc(vs[n])}</p>')
    words = sum(len(t.split()) for t in vs.values())
    return f"""      <article class="passage" id="{slug}" data-search="{esc((title + ' ' + ref + ' ' + ' '.join(vs.values())).lower())}">
        <header class="ph">
          <p class="ref">{esc(ref)}<span class="wc">{words} words</span></p>
          <h3>{esc(title)}</h3>
          <p class="note">{esc(note)}</p>
        </header>
        <div class="text">
{chr(10).join(body)}
        </div>
      </article>
"""


def section(topic, title, blurb, items):
    arts, toc = [], []
    for i, p in enumerate(items, 1):
        slug = f"{topic}-{i}"
        arts.append(passage_html(slug, p, i))
        ref = f"{p[0]} {p[1]}:{p[2]}" if p[2] == p[3] else f"{p[0]} {p[1]}:{p[2]}\u2013{p[3]}"
        toc.append(f'          <li><a href="#{slug}">{esc(ref)}</a>'
                   f'<span class="tt">{esc(p[4])}</span></li>')
    return f"""    <section class="sec" id="sec-{topic}">
      <header class="sec-h">
        <h2>{esc(title)}</h2>
        <p class="blurb">{esc(blurb)}</p>
      </header>
      <nav class="mini" aria-label="{esc(title)} contents">
        <ol>
{chr(10).join(toc)}
        </ol>
      </nav>
{chr(10).join(arts)}    </section>
"""


def main():
    love = section("love", "Love",
                    "Twenty passages, in the order they are worth reading: the love of "
                    "God for people, the love of people for each other, and the one "
                    "chapter that is read aloud at both weddings and funerals.",
                    LOVE)
    friend = section("friendship", "Friendship",
                     "Twenty-one passages about friends — the covenant between David "
                     "and Jonathan, the proverbs that reduce the subject to a line, and "
                     "the farewells, which is where friendship is tested.",
                     FRIENDSHIP)
    total = len(LOVE) + len(FRIENDSHIP)
    nverses = sum(len(ch) for book in BIBLE.values() for ch in book.values())
    shown = 0
    for p in LOVE + FRIENDSHIP:
        shown += sum(len(t.split()) for t in verses(p[0], p[1], p[2], p[3]).values())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Love and Friendship &mdash; a reading list from the King James Bible</title>
<meta name="description" content="{total} passages of the King James Bible on love and on friendship, quoted whole, with notes.">
<style>
:root {{
  --paper: #fcfbf9;
  --ink: #17161a;
  --muted: #6c6862;
  --rule: #ddd8d0;
  --rule-soft: #ebe7e1;
  --accent: #7a2e2e;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --measure: 62ch;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --paper: #14140f; --ink: #ece8e1; --muted: #9b958c; --rule: #34322c;
           --rule-soft: #24231e; --accent: #d99a9a; }}
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans);
       font-size: 16px; line-height: 1.6; }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 28px 96px; }}
a {{ color: inherit; }}
a:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}

header.masthead {{ padding: 68px 0 0; border-bottom: 1px solid var(--rule); }}
.kicker {{ font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); margin: 0 0 18px; }}
h1 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(32px, 5.4vw, 52px); line-height: 1.05; letter-spacing: -.015em; margin: 0 0 16px; }}
h1 em {{ font-style: italic; color: var(--accent); }}
.lede {{ font-family: var(--serif); font-size: clamp(17px, 2vw, 20px); line-height: 1.5; max-width: var(--measure); margin: 0 0 14px; }}
.method {{ max-width: var(--measure); font-size: 14px; line-height: 1.65; color: var(--muted); margin: 0 0 34px; }}
.method b {{ color: var(--ink); font-weight: 600; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 14px; align-items: center; padding: 0 0 30px; border-bottom: 1px solid var(--rule); }}
.controls label {{ font-size: 11px; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); }}
.controls input {{ font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid var(--rule); background: transparent; color: inherit; min-width: 260px; }}
.controls .count {{ font-size: 12.5px; color: var(--muted); margin-left: auto; }}

.sec {{ padding-top: 70px; }}
.sec-h {{ border-top: 1px solid var(--ink); padding-top: 15px; margin-bottom: 26px; }}
.sec-h h2 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(24px, 3.6vw, 33px); margin: 0 0 10px; letter-spacing: -.01em; }}
.blurb {{ font-family: var(--serif); font-size: 16px; line-height: 1.55; color: var(--muted); max-width: var(--measure); margin: 0; }}

nav.mini {{ margin: 0 0 44px; }}
nav.mini ol {{ list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 34px; }}
nav.mini li {{ break-inside: avoid; padding: 6px 0; border-bottom: 1px solid var(--rule-soft); display: flex; gap: 10px; align-items: baseline; }}
nav.mini a {{ font-family: var(--serif); font-size: 15px; text-decoration: none; white-space: nowrap; }}
nav.mini a:hover {{ color: var(--accent); }}
nav.mini .tt {{ font-size: 12.5px; color: var(--muted); }}

.passage {{ margin: 0 0 54px; padding-top: 22px; border-top: 1px solid var(--rule-soft); max-width: 760px; }}
.ph {{ margin-bottom: 16px; }}
.ref {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 7px; display: flex; gap: 12px; }}
.ref .wc {{ color: var(--muted); letter-spacing: .08em; }}
.ph h3 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(20px, 2.8vw, 26px); line-height: 1.2; margin: 0 0 8px; }}
.note {{ font-size: 14px; line-height: 1.6; color: var(--muted); margin: 0; }}
.text {{ font-family: var(--serif); font-size: 17px; line-height: 1.62; }}
.text .v {{ margin: 0 0 9px; padding-left: 34px; text-indent: -34px; }}
.text .vn {{ display: inline-block; width: 26px; text-indent: 0; font-family: var(--sans); font-size: 11px; color: var(--muted); vertical-align: .18em; }}
.text .key {{ padding-left: 34px; }}
.text .key .vn {{ color: var(--accent); font-weight: 700; }}
.passage[hidden] {{ display: none; }}

footer {{ margin-top: 80px; border-top: 1px solid var(--rule); padding-top: 24px; font-size: 13.5px; line-height: 1.7; color: var(--muted); max-width: var(--measure); }}
footer h2 {{ font-family: var(--serif); font-weight: 400; font-size: 17px; color: var(--ink); margin: 0 0 12px; }}
footer code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
.companion {{ margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--rule-soft); }}
.companion a {{ color: var(--accent); }}
@media (max-width: 640px) {{
  .wrap {{ padding: 0 18px 72px; }}
  nav.mini ol {{ columns: 1; }}
  .controls .count {{ margin-left: 0; }}
}}
@media print {{
  nav.mini, .controls {{ display: none; }}
  .passage {{ break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <p class="kicker">A reading list &middot; King James Version &middot; {total} passages</p>
    <h1>Love, <em>and Friendship</em></h1>
    <p class="lede">The Bible talks about love more than it talks about almost anything else, and about friendship in a smaller, sharper set of passages &mdash; covenants made in fields, proverbs reduced to a line, and farewells, which is where friendship is tested. Every passage below is quoted whole, not excerpted, and every verse is the King James text.</p>
    <p class="method">Two sections. <b>Love</b> runs from the love of God for people, through the commandment to love one's neighbour, to the Song of Solomon and the one chapter that is read at weddings and funerals both. <b>Friendship</b> runs from David and Jonathan, through the proverbs, to Paul's last letters and the friends who stayed and the ones who left. The verses that carry the passage are marked in red; the rest are there because a passage read in pieces is not the passage.</p>
  </header>

  <div class="controls">
    <label for="q">Filter</label>
    <input id="q" type="search" placeholder="love, Jonathan, neighbour, wept&hellip;" autocomplete="off">
    <span class="count" id="count">{total} passages</span>
  </div>

  <main>
{love}
{friend}
    <footer>
      <h2>On the text</h2>
      <p>All {total} passages are quoted from the King James Version of 1611, in full, with verse numbers. The corpus holds {nverses:,} verses across the 66 books; the selection here comes to {shown:,} words of scripture. Nothing is paraphrased and nothing is cut, so a passage can be read aloud straight from the page.</p>
      <p>The notes are editorial and say what each passage does. Where a passage appears in both sections &mdash; John 15, Ruth 1, 2 Samuel 1 &mdash; it is set once under love and once under friendship, because it belongs to both.</p>
      <p class="companion">Companion galleries, where these subjects are the pictures: <a href="../love-gallery/index.html">Love, Abstracted</a> (46 works) &middot; <a href="../friends-gallery/index.html">Friends, Abstracted</a> (25 works) &middot; <a href="../parents-gallery/index.html">Parents, Abstracted</a> (25 works) &middot; <a href="../grief-gallery/index.html">Grief, and the Night</a> (201 works).</p>
    </footer>
  </main>
</div>

<script>
const q = document.getElementById('q');
const count = document.getElementById('count');
const arts = Array.from(document.querySelectorAll('.passage'));
const heads = Array.from(document.querySelectorAll('.sec'));
function apply() {{
  const s = q.value.trim().toLowerCase();
  let n = 0;
  arts.forEach(a => {{
    const hit = !s || a.dataset.search.includes(s);
    a.hidden = !hit;
    if (hit) n++;
  }});
  heads.forEach(sec => {{
    const vis = sec.querySelectorAll('.passage:not([hidden])').length;
    sec.hidden = vis === 0;
    const mini = sec.querySelector('nav.mini');
    if (mini) mini.hidden = !!s;
  }});
  count.textContent = s ? n + ' of ' + arts.length + ' passages' : arts.length + ' passages';
}}
q.addEventListener('input', apply);
</script>
</body>
</html>
"""
    out = os.path.join(BASE, "index.html")
    open(out, "w").write(html)
    print(f"wrote {out} ({len(html)} chars, {total} passages, {shown} words)")


if __name__ == "__main__":
    main()
