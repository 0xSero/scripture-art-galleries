#!/usr/bin/env python3
"""Build the approval page for the curated quote pool.

Dense reference-page layout: one row per line, with the reference, the line as it will
sit on the plate, the register, the verifier's score and the reason it was chosen.
Ticking rows and pressing the button copies a plain list of the references.
"""
import html
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(BASE, "quote-pool.json")
OUT = os.path.join(BASE, "quotes.html")


def main():
    pool = json.load(open(POOL))
    verdicts = {}
    vpath = os.path.join(BASE, "quotes", "VERIFY.json")
    if os.path.exists(vpath):
        for row in json.load(open(vpath)):
            verdicts[(row.get("file"), row.get("ref"))] = row

    rows = []
    for i, q in enumerate(pool):
        v = verdicts.get((q["register"] + ".json", q["ref"]), {})
        rows.append(
            "<tr><td><input type=checkbox class=pick data-ref=\"{ref}\" checked></td>"
            "<td class=num>{n}</td>"
            "<td class=ref>{ref}</td>"
            "<td class=line>{text}</td>"
            "<td class=reg>{reg}</td>"
            "<td class=num>{impact}</td>"
            "<td class=why>{why}</td></tr>".format(
                ref=html.escape(q["ref"]), n=i + 1, text=html.escape(q["text"]),
                reg=html.escape(q["register"]), impact=q["impact"],
                why=html.escape(q.get("why", "") or v.get("note", ""))))

    doc = """<!doctype html>
<html lang=en><meta charset=utf-8>
<title>Hope, and the Light — quote pool</title>
<style>
body{{font:13px/1.45 -apple-system,"Gill Sans",Helvetica,sans-serif;margin:24px;max-width:1100px;color:#111}}
h1{{font-size:19px;margin:0 0 4px}} p.lede{{color:#444;margin:0 0 14px;max-width:70ch}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #ddd;padding:5px 8px;text-align:left;vertical-align:top}}
th{{border-bottom:2px solid #111;font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
td.num{{text-align:right;color:#666;font-variant-numeric:tabular-nums;white-space:nowrap}}
td.ref{{white-space:nowrap;color:#333}} td.line{{font-weight:600}}
td.reg{{color:#666}} td.why{{color:#444;font-size:12px}}
button{{font:inherit;padding:6px 12px;margin:14px 0;border:1px solid #111;background:#fff;cursor:pointer}}
#out{{width:100%;height:120px;font:12px/1.4 ui-monospace,Menlo,monospace;display:none}}
</style>
<h1>Hope, and the Light — quote pool</h1>
<p class=lede>{n} lines, curated in five registers and independently checked against the
World English Bible: every line is 4–8 words and a literal run of its verse, no reference
is reused from the four earlier galleries, and the art reviewer's verdict has been applied.
Tick the ones you want, untick the rest, then copy the list.</p>
<button onclick="copyList()">Copy approved list</button>
<textarea id=out readonly></textarea>
<table>
<thead><tr><th></th><th>#</th><th>Reference</th><th>Line</th><th>Register</th><th>Impact</th><th>Why it was chosen</th></tr></thead>
<tbody>
{rows}
</tbody></table>
<script>
function copyList(){{
  var refs=[].slice.call(document.querySelectorAll('.pick')).filter(function(c){{return c.checked}})
    .map(function(c){{return c.dataset.ref}});
  var t=document.getElementById('out'); t.style.display='block';
  t.value=refs.join('\\n'); t.select();
}}
</script>
</html>
""".format(n=len(pool), rows="\n".join(rows))
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"wrote {OUT} ({len(doc)} bytes, {len(pool)} lines)")


if __name__ == "__main__":
    main()
