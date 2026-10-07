# Scripture art galleries

Six galleries of public-domain paintings with a short line of scripture set into each
plate. Every picture is a painting that is out of copyright, taken from Wikimedia
Commons; every line is a literal run of words from the verse it cites, printed on the
plate in Baskerville over a gradient that starts a quarter of the way up from the
bottom edge and darkens downward. Nothing here is generated: the paintings are real, the
lines are quoted, and the only work of ours is the choosing, the type and the page.

Open any `index.html` straight from the checkout. There is no build step and no server;
each page is one file with its own `img/` beside it.

| Gallery | Plates | Text | Register |
| --- | ---: | --- | --- |
| [`parents-gallery`](parents-gallery/index.html) | 25 | King James Version | parents and children |
| [`friends-gallery`](friends-gallery/index.html) | 25 | King James Version | friendship |
| [`love-gallery`](love-gallery/index.html) | 46 | King James Version | love |
| [`grief-gallery`](grief-gallery/index.html) | 201 | King James Version | grief and the night |
| [`hope-gallery`](hope-gallery/index.html) | 205 | World English Bible | hope, light, merging and the old light |
| [`love-and-friendship`](love-and-friendship/index.html) | 41 passages | World English Bible | love and friendship, to read |

`hope-gallery` is the largest: eight sections, from Cubism and Futurism through
Constructivism, the Blue Rider, De Stijl, merging, light and spring, and a closing section
of the classical painting the moderns were arguing with — De La Corte's roses, Ruysch and
Mignon, and the first light of Elsheimer, Claude Lorrain, Turner and Friedrich.

## What is in here

- `*/index.html` — the gallery itself, self-contained, with its own CSS and JavaScript.
- `*/img/versed/` — each plate with its line set into the picture (the lightbox image).
- `*/img/versed-thumb/` — the grid thumbnail of the same plate.
- `*/works.py` — the catalogue: for every plate, the exact Commons file, the artist, the
  title, the date, the medium, the collection, the licence and the section it is shown in.
- `*/verses.json` or `*/lines.json` — the line set into each plate and its reference.
- `*/manifest.json`, `*/meta/` — what was actually fetched, so a plate is never broken.
- `*/resolve.py`, `*/harvest*.py`, `*/rank*.py`, `*/choose*.py`, `*/build*.py`,
  `*/render_hope.py`, `*/verify_hope.py` — the pipeline that found, ranked and rendered
  the work, kept so the galleries can be rebuilt from scratch.
- `hope-gallery/art-review.json` — an image-by-image verdict on every picture that
  arrived, with the reason each rejected one was rejected.
- `hope-gallery/quotes/` — the curated lines and the independent verification of every
  one of them against the World English Bible.
- `psalm-verses/` — the Bible text the lines were taken from, and the scripts that
  curated them.

The raw Commons originals (`img/full`) are deliberately not committed: they are not our
work, they are large, and `resolve.py` fetches them again from the file named in
`works.py`.

## The lines

Every line is four to eight words and a literal run of the verse it cites, so it can be
checked against the text in `psalm-verses/`. No reference is used twice in a gallery, and no
reference is shared between the galleries. The lines were curated in registers — light, merging,
joy, hope, new life — and then independently verified, first for the literal run and then for
whether the line is actually worth reading; the verifier's verdicts are in
`hope-gallery/quotes/VERIFY.json` and `VERIFY2.json`.

The World English Bible is used for the hope gallery because the New International Version is
still in copyright and cannot be reproduced. It is public domain, as is the King James Version
used by the other four.

## Licences

- The paintings are public domain or CC0, each one recorded with its own licence label in
  `works.py` and `manifest.json`. The underlying files are on Wikimedia Commons, and their
  page carries the authoritative licence and attribution.
- The scripture is public domain: the King James Version, and the World English Bible
  (public domain, dedicated by its publisher).
- Everything of ours — the pages, the type treatment, the pipeline — is released under
  [CC0 1.0](LICENCE.md), so it can be used without conditions.

## Rebuilding

Each gallery carries the scripts that made it. From inside a gallery directory, `resolve.py`
downloads the originals from the file named in `works.py` into `img/full`, and the build script
writes `index.html`. `hope-gallery/make_hope.sh` runs that gallery end to end, including the
verification of every plate against the corpus. The Commons API is rate limited to roughly one
request a minute, so a full rebuild takes time and resumes where it left off.
