#!/usr/bin/env python3
"""Curate the hope quotes: the strongest passages, with the best line from each.

Rather than take the top of a scored list — which fills up with genealogies and
processions — this starts from the passages that actually say the thing, and mines
the best four-to-eight-word line out of each one. The text is the World English
Bible (public domain, modern English); the King James wording of the same verse is
shown beside it for comparison, and the page it writes is for approval.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from build_hope_lines import GLOOM, CONTEXT, REGISTER, norm, clauses  # noqa: E402

WEB = json.load(open(os.path.join(BASE, "web-bible.json")))
KJV = json.load(open(os.path.join(BASE, "kjv-bible.json")))
OUT_JSON = os.path.join(BASE, "hope-quotes.json")
OUT_HTML = "/Users/sero/hope-gallery/quotes.html"

# (book, chapter, first verse, last verse, theme)
PASSAGES = [
    ("Genesis", 9, 12, 17, "the bow in the cloud, a sign of the covenant"),
    ("Genesis", 28, 12, 17, "a ladder set up between earth and heaven"),
    ("Exodus", 15, 1, 6, "song at the sea"),
    ("Exodus", 33, 7, 11, "face to face, as one speaks to a friend"),
    ("Exodus", 40, 34, 38, "the cloud filling the tabernacle"),
    ("Numbers", 6, 24, 27, "the blessing put on the people"),
    ("Deuteronomy", 8, 7, 10, "a good land, brooks and springs"),
    ("Deuteronomy", 30, 1, 6, "gathered again and brought home"),
    ("Ruth", 1, 14, 18, "your people will be my people"),
    ("1 Samuel", 18, 1, 4, "the soul of Jonathan knit to David"),
    ("1 Samuel", 23, 14, 18, "Jonathan strengthens David's hand in God"),
    ("2 Samuel", 22, 17, 20, "drawn out of deep waters"),
    ("1 Kings", 19, 11, 13, "a still small voice after the fire"),
    ("2 Kings", 6, 15, 17, "the mountain full of horses and fire"),
    ("Nehemiah", 8, 9, 12, "the joy of the LORD is your strength"),
    ("Job", 11, 15, 19, "you will lift up your face without blemish"),
    ("Psalms", 16, 8, 11, "in your presence is fullness of joy"),
    ("Psalms", 23, 1, 6, "goodness and loving kindness follow"),
    ("Psalms", 27, 1, 6, "the LORD is my light and salvation"),
    ("Psalms", 30, 1, 12, "joy comes in the morning"),
    ("Psalms", 34, 1, 10, "those who seek the LORD lack nothing"),
    ("Psalms", 36, 5, 10, "your loving kindness reaches to the skies"),
    ("Psalms", 40, 1, 5, "he set my feet on a rock"),
    ("Psalms", 42, 5, 11, "hope in God, for I shall praise him"),
    ("Psalms", 46, 1, 7, "God is our refuge and strength"),
    ("Psalms", 51, 10, 12, "restore to me the joy of your salvation"),
    ("Psalms", 62, 1, 8, "my soul waits in silence for God"),
    ("Psalms", 65, 9, 13, "you crown the year with your bounty"),
    ("Psalms", 71, 14, 24, "I will hope continually"),
    ("Psalms", 84, 1, 7, "blessed are those who dwell in your house"),
    ("Psalms", 85, 8, 13, "mercy and truth meet together"),
    ("Psalms", 92, 12, 15, "they will still bear fruit in old age"),
    ("Psalms", 96, 10, 13, "let the heavens be glad"),
    ("Psalms", 98, 4, 9, "make a joyful noise before the King"),
    ("Psalms", 103, 1, 5, "who crowns you with loving kindness"),
    ("Psalms", 113, 1, 9, "from the rising of the sun"),
    ("Psalms", 118, 22, 24, "this is the day the LORD has made"),
    ("Psalms", 121, 1, 8, "he who keeps you will not slumber"),
    ("Psalms", 126, 1, 6, "those who sow in tears will reap"),
    ("Psalms", 130, 5, 8, "my soul hopes in his word"),
    ("Psalms", 133, 1, 3, "how good it is to dwell together"),
    ("Psalms", 136, 1, 9, "his loving kindness endures forever"),
    ("Psalms", 139, 7, 12, "if I take the wings of the morning"),
    ("Psalms", 147, 1, 6, "he heals the broken in heart"),
    ("Psalms", 148, 1, 6, "the heavens praise the LORD"),
    ("Proverbs", 3, 13, 18, "wisdom is a tree of life"),
    ("Proverbs", 4, 18, 19, "the path of the righteous shines"),
    ("Proverbs", 15, 13, 15, "a cheerful heart makes a cheerful face"),
    ("Proverbs", 17, 17, 22, "a friend loves at all times"),
    ("Proverbs", 18, 10, 24, "the name of the LORD is a strong tower"),
    ("Proverbs", 27, 5, 17, "iron sharpens iron"),
    ("Ecclesiastes", 3, 1, 8, "a time for everything"),
    ("Ecclesiastes", 4, 7, 12, "two are better than one"),
    ("Song of Solomon", 2, 8, 17, "the voice of my beloved"),
    ("Song of Solomon", 8, 6, 7, "love is strong as death"),
    ("Isaiah", 2, 1, 4, "swords into plowshares"),
    ("Isaiah", 6, 1, 8, "the whole earth is full of his glory"),
    ("Isaiah", 9, 1, 7, "the people who walked in darkness"),
    ("Isaiah", 11, 1, 9, "the wolf will live with the lamb"),
    ("Isaiah", 25, 6, 9, "he will swallow up death forever"),
    ("Isaiah", 26, 1, 4, "a strong city, salvation for walls"),
    ("Isaiah", 30, 18, 26, "the LORD waits to be gracious"),
    ("Isaiah", 35, 1, 10, "the desert will blossom"),
    ("Isaiah", 40, 1, 8, "the word of our God stands forever"),
    ("Isaiah", 40, 28, 31, "they will mount up with wings"),
    ("Isaiah", 41, 8, 13, "I will uphold you with my hand"),
    ("Isaiah", 43, 1, 7, "I have redeemed you, you are mine"),
    ("Isaiah", 43, 16, 21, "I am making a way in the desert"),
    ("Isaiah", 49, 8, 16, "I have engraved you on my hands"),
    ("Isaiah", 51, 9, 11, "the redeemed will return with singing"),
    ("Isaiah", 52, 7, 10, "how beautiful on the mountains"),
    ("Isaiah", 54, 9, 17, "my loving kindness will not depart"),
    ("Isaiah", 55, 1, 13, "come to the waters"),
    ("Isaiah", 58, 6, 12, "your light will rise in the darkness"),
    ("Isaiah", 60, 1, 7, "arise, shine, for your light has come"),
    ("Isaiah", 61, 1, 4, "he has sent me to bind up"),
    ("Isaiah", 65, 17, 25, "new heavens and a new earth"),
    ("Jeremiah", 17, 5, 8, "like a tree planted by the waters"),
    ("Jeremiah", 29, 10, 14, "plans for peace, to give you hope"),
    ("Jeremiah", 31, 1, 14, "I have loved you with everlasting love"),
    ("Lamentations", 3, 21, 26, "his mercies are new every morning"),
    ("Ezekiel", 36, 24, 28, "a new heart and a new spirit"),
    ("Ezekiel", 37, 1, 14, "the valley of dry bones, and breath"),
    ("Hosea", 2, 18, 23, "I will betroth you to me forever"),
    ("Joel", 2, 23, 27, "the floors full of grain"),
    ("Micah", 4, 1, 5, "they will beat swords into plowshares"),
    ("Micah", 7, 7, 9, "though I fall, I will rise"),
    ("Habakkuk", 3, 17, 19, "yet I will rejoice in the LORD"),
    ("Zephaniah", 3, 14, 20, "he will rejoice over you with singing"),
    ("Zechariah", 8, 1, 8, "I will bring them back, and they will dwell"),
    ("Malachi", 4, 1, 6, "the sun of righteousness will rise"),
    ("Matthew", 5, 1, 16, "the light of the world, a city on a hill"),
    ("Matthew", 6, 25, 34, "consider the lilies of the field"),
    ("Matthew", 11, 25, 30, "my yoke is easy, my burden light"),
    ("Matthew", 28, 1, 10, "he is not here, he has risen"),
    ("Mark", 4, 26, 32, "the seed growing by itself"),
    ("Mark", 9, 2, 8, "his garments became glistening white"),
    ("Luke", 1, 46, 55, "my soul magnifies the Lord"),
    ("Luke", 2, 8, 20, "good news of great joy"),
    ("Luke", 15, 11, 32, "this my son was dead and is alive"),
    ("Luke", 24, 1, 12, "why do you seek the living among the dead"),
    ("John", 1, 1, 18, "the light shines in the darkness"),
    ("John", 8, 12, 20, "I am the light of the world"),
    ("John", 10, 1, 18, "I came that they may have life"),
    ("John", 11, 1, 44, "I am the resurrection and the life"),
    ("John", 12, 20, 36, "unless a grain of wheat falls"),
    ("John", 14, 1, 14, "in my Father's house are many rooms"),
    ("John", 15, 1, 17, "I have called you friends"),
    ("John", 16, 16, 33, "in me you may have peace"),
    ("John", 20, 1, 18, "the stone taken away from the tomb"),
    ("Acts", 2, 1, 21, "I will pour out my Spirit"),
    ("Acts", 16, 22, 34, "believing in God with his household"),
    ("Romans", 5, 1, 11, "hope does not disappoint"),
    ("Romans", 8, 18, 39, "nothing will separate us from his love"),
    ("Romans", 12, 9, 21, "overcome evil with good"),
    ("Romans", 15, 1, 13, "the God of hope fill you with joy"),
    ("1 Corinthians", 13, 1, 13, "faith, hope and love remain"),
    ("1 Corinthians", 15, 50, 58, "death is swallowed up in victory"),
    ("2 Corinthians", 4, 16, 18, "momentary affliction, eternal weight of glory"),
    ("2 Corinthians", 5, 16, 21, "new creation, the old has passed"),
    ("Galatians", 5, 16, 26, "the fruit of the Spirit is love"),
    ("Ephesians", 2, 11, 22, "he is our peace, who made us one"),
    ("Ephesians", 4, 1, 16, "one body and one Spirit"),
    ("Philippians", 1, 3, 11, "he who began a good work"),
    ("Philippians", 4, 4, 13, "rejoice in the Lord always"),
    ("Colossians", 3, 12, 17, "love, which is the bond of perfection"),
    ("1 Thessalonians", 4, 13, 18, "we will be caught up together"),
    ("2 Thessalonians", 2, 15, 17, "comfort your hearts"),
    ("Hebrews", 11, 1, 3, "faith is assurance of things hoped for"),
    ("Hebrews", 12, 1, 2, "a cloud of witnesses surrounding us"),
    ("Hebrews", 13, 12, 16, "do not forget to do good"),
    ("James", 1, 12, 18, "every good gift comes down from above"),
    ("1 Peter", 1, 3, 9, "a living hope through the resurrection"),
    ("1 Peter", 5, 6, 11, "the God of all grace restore you"),
    ("2 Peter", 3, 10, 18, "new heavens and a new earth"),
    ("1 John", 1, 5, 10, "God is light, and in him no darkness"),
    ("1 John", 3, 1, 3, "we will be like him"),
    ("1 John", 4, 7, 21, "God is love, and we ought to love"),
    ("Revelation", 7, 9, 17, "he will wipe away every tear"),
    ("Revelation", 21, 1, 7, "a new heaven and a new earth"),
    ("Revelation", 21, 22, 27, "the river of water of life"),
    ("Revelation", 22, 1, 5, "no more night, they will reign forever"),
]


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def verses_of(corpus, book, ch, a, b):
    out = {}
    for v in corpus.get(book, {}).get(str(ch), []):
        if a <= v["v"] <= b:
            out[v["v"]] = v["t"]
    return out


# openers that name a scene or a speaker rather than say the thing
NARRATIVE = re.compile(
    r"(music director|said,|says:|saying|spoke|the son of|first day of the week|"
    r"days after|tent door|it happened|these are the generations|"
    r"the words of|the vision of|the burden of|the book of)", re.I)


def score(text):
    low = " " + text.lower() + " "
    return sum(w for k, w in REGISTER.items() if k in low)


def best_line(web, book, ch, a, b):
    """The best four-to-eight-word line in the passage, with its verse."""
    picked = []
    for v, text in sorted(verses_of(web, book, ch, a, b).items()):
        body = norm(text)
        for cl in clauses(body):
            n = len(cl.split())
            if n < 4 or n > 8 or GLOOM.search(cl) or CONTEXT.search(cl):
                continue
            if NARRATIVE.search(cl) or cl.endswith(":") or cl.endswith("\u2026"):
                continue
            if cl.startswith("\u201c") and not cl.endswith("\u201d"):
                continue
            sc = score(cl)
            low = " " + cl.lower() + " "
            top = max((w for k, w in REGISTER.items() if k in low), default=0)
            sc += 3 * (top >= 4)              # a line that carries the subject
            sc += 3 * body.startswith(cl)      # a line that opens its verse
            if cl[0].isupper() or cl[0] in "\u201c\u2018":
                sc += 1
            if cl.split()[0].lower() in ("and", "but", "for", "so", "then",
                                        "when", "neither", "nor", "as"):
                sc -= 2
            picked.append(dict(verse=v, text=cl, words=n, score=sc))
    strong = [c for c in picked if c["score"] >= 5] or \
        [c for c in picked if c["score"] >= 4]
    pool = strong or picked
    if pool:
        best = max(pool, key=lambda c: (c["score"], -c["words"]))
        return best
    # last resort: the opening of the passage, cut at a word boundary
    first = sorted(verses_of(web, book, ch, a, b).items())
    if first:
        v, text = first[0]
        words = norm(text).split()[:8]
        return dict(verse=v, text=" ".join(words) + "\u2026", words=len(words),
                    score=-1)
    return None


def main():
    quotes, rows = [], []
    for book, ch, a, b, theme in PASSAGES:
        pick = best_line(WEB, book, ch, a, b)
        if not pick:
            print(f"  no line for {book} {ch}:{a}-{b}")
            continue
        ref = f"{book} {ch}:{pick['verse']}"
        kjv = verses_of(KJV, book, ch, pick["verse"], pick["verse"]).get(pick["verse"], "")
        quotes.append(dict(ref=ref, text=pick["text"], words=pick["words"],
                          theme=theme, book=book, chapter=ch,
                          first=a, last=b, kjv=kjv))
    for i, q in enumerate(quotes, 1):
        rows.append(f"""      <tr>
        <td class="c-no"><label><input type="checkbox" class="pick" value="{esc(q['ref'])}" checked> {i}</label></td>
        <td class="c-ref">{esc(q['ref'])}</td>
        <td class="c-web">{esc(q['text'])} <span class="w">{q['words']}w</span></td>
        <td class="c-kjv">{esc(q['kjv'])}</td>
        <td class="c-th">{esc(q['theme'])}</td>
      </tr>""")
    json.dump(quotes, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hope quotes &mdash; approve the list</title>
<style>
body {{ margin: 0; background: #fcfbf9; color: #17161a;
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
.wrap {{ max-width: 1280px; margin: 0 auto; padding: 34px 22px 90px; }}
h1 {{ font-family: "Iowan Old Style", Palatino, Georgia, serif; font-weight: 400;
  font-size: 32px; margin: 0 0 10px; }}
p.lede {{ max-width: 80ch; color: #55524c; font-size: 14px; margin: 0 0 12px; }}
.bar {{ position: sticky; top: 0; background: #fcfbf9; border-bottom: 1px solid #ddd8d0;
  padding: 12px 0; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; z-index: 5; }}
button {{ font: inherit; font-size: 13px; padding: 7px 12px; border: 1px solid #17161a;
  background: none; cursor: pointer; }}
button:hover {{ background: #17161a; color: #fcfbf9; }}
#out {{ font-family: ui-monospace, Menlo, monospace; font-size: 12px; width: 100%;
  height: 54px; margin-top: 8px; display: none; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 16px; }}
th {{ text-align: left; font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
  color: #6c6862; border-bottom: 1px solid #ddd8d0; padding: 0 14px 8px 0; }}
td {{ border-bottom: 1px solid #ebe7e1; padding: 9px 14px 9px 0; vertical-align: top; }}
.c-no {{ width: 56px; color: #6c6862; }}
.c-ref {{ width: 150px; white-space: nowrap; }}
.c-web {{ font-family: "Iowan Old Style", Palatino, Georgia, serif; font-size: 15.5px; }}
.c-kjv {{ width: 32%; color: #6c6862; font-size: 13px; font-style: italic; }}
.c-th {{ width: 24%; color: #55524c; font-size: 12.5px; }}
.w {{ font-family: -apple-system, sans-serif; font-size: 10.5px; color: #6c6862; }}
tr.off {{ opacity: .35; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Hope quotes &mdash; approve the list</h1>
  <p class="lede">{len(quotes)} lines, one per passage, each a literal run of four to eight words
  from a verse of the <b>World English Bible</b> &mdash; public domain, modern English, the same
  register as the NIV. The King James wording of the same verse is shown beside it, and the last
  column says what the passage is about. Untick anything that reads wrong, then press the button and
  paste the result back.</p>
  <p class="lede">The NIV itself is under copyright (Biblica). Quoting it in a gallery needs their
  notice, and the text is not available to me to fetch whole. If you want the NIV wording, paste the
  approved verses and I will set those instead &mdash; the passages here are the ones to approve either way.</p>
  <div class="bar">
    <button id="all">Tick all</button>
    <button id="none">Untick all</button>
    <button id="copy">Copy approved list</button>
    <span id="count"></span>
    <textarea id="out" readonly></textarea>
  </div>
  <table>
    <thead><tr><th>Keep</th><th>Reference</th><th>Line to set on the plate</th>
      <th>King James wording</th><th>What it is about</th></tr></thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>
</div>
<script>
const boxes = () => Array.from(document.querySelectorAll('.pick'));
const count = document.getElementById('count');
function tally() {{
  const n = boxes().filter(b => b.checked).length;
  count.textContent = n + ' of ' + boxes().length + ' ticked';
  boxes().forEach(b => b.closest('tr').classList.toggle('off', !b.checked));
}}
boxes().forEach(b => b.addEventListener('change', tally));
document.getElementById('all').onclick = () => {{ boxes().forEach(b => b.checked = true); tally(); }};
document.getElementById('none').onclick = () => {{ boxes().forEach(b => b.checked = false); tally(); }};
document.getElementById('copy').onclick = () => {{
  const list = boxes().filter(b => b.checked).map(b => b.value + ' | ' +
    b.closest('tr').querySelector('.c-web').textContent.trim().replace(/\\s+\\d+w$/, ''));
  const out = document.getElementById('out');
  out.style.display = 'block';
  out.value = list.join('\\n');
  out.select();
  document.execCommand('copy');
  document.getElementById('copy').textContent = 'Copied ' + list.length + ' lines';
}};
tally();
</script>
</body>
</html>
"""
    open(OUT_HTML, "w").write(html)
    print(f"wrote {OUT_JSON} ({len(quotes)} quotes)")
    print(f"wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
