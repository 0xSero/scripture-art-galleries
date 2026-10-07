#!/bin/bash
# Build the hope gallery end to end, in order, from the selected works.
#
#   1. write works.py from the reviewed selection
#   2. merge the curated quote pool and give every work a line
#   3. set the line into the plate (Baskerville over the foot gradient, no lining)
#   4. build the page
#   5. verify the page against the works, the lines and the corpus
set -e
cd "$(dirname "$0")"

echo "== 0/5 works"
HOPE_SELECTED=/tmp/hope3-selected-reviewed.json python3 gen_works.py

echo "== 1/5 manifest"
python3 rebuild_manifest.py

echo "== 2/5 lines"
python3 assign_quotes.py

echo "== 3/5 plates"
HOPE_FONT=baskerville HOPE_LINING=none python3 render_hope.py

echo "== 4/5 page"
python3 build_hope.py

echo "== 5/5 verify"
python3 verify_hope.py
