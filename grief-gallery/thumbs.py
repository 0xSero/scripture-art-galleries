#!/usr/bin/env python3
"""Download thumbnails for the chosen works and build one contact sheet per section.

Images come from Special:FilePath, the page-view path, so nothing here touches the
rate-limited Commons API.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

SEL = json.load(open("/tmp/grief-selected.json"))
THUMBS = "/tmp/grief-thumbs"
SHEETS = "/tmp/grief-sheets"
CELL, COLS = 300, 6
FONT = "/System/Library/Fonts/Supplemental/Charter.ttc"


def fetch(i, work):
    path = os.path.join(THUMBS, f"{i:03d}.jpg")
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        return path
    name = work["file_title"][5:].replace(" ", "_")
    url = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
           + urllib.parse.quote(name, safe="") + f"?width={CELL}")
    try:
        subprocess.run(["curl", "-sSL", "--max-time", "60", "-A",
                        "GriefGalleryBuilder/1.0", "-o", path, url],
                       check=True, capture_output=True)
    except Exception:  # noqa: BLE001
        return None
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        return path
    return None


def sheet(rows, out_path, title):
    n = len(rows)
    cols = COLS
    lines = (n + cols - 1) // cols
    pad, head = 8, 34
    W = cols * (CELL + pad) + pad
    H = head + lines * (CELL + pad + 22) + pad
    canvas = Image.new("RGB", (W, H), (247, 246, 243))
    d = ImageDraw.Draw(canvas)
    try:
        ft = ImageFont.truetype(FONT, 20)
        fn = ImageFont.truetype(FONT, 18)
    except Exception:  # noqa: BLE001
        ft = fn = ImageFont.load_default()
    d.text((pad, 8), title, fill=(20, 20, 20), font=ft)
    for k, (idx, path) in enumerate(rows):
        r, c = divmod(k, cols)
        x = pad + c * (CELL + pad)
        y = head + r * (CELL + pad + 22)
        if path:
            try:
                im = Image.open(path).convert("RGB")
                im.thumbnail((CELL, CELL))
                canvas.paste(im, (x + (CELL - im.width) // 2,
                                  y + (CELL - im.height) // 2))
            except Exception:  # noqa: BLE001
                d.rectangle([x, y, x + CELL, y + CELL], outline=(180, 180, 180))
        else:
            d.rectangle([x, y, x + CELL, y + CELL], outline=(180, 180, 180))
            d.text((x + 8, y + 8), "no image", fill=(150, 60, 60), font=fn)
        d.text((x, y + CELL + 2), str(idx), fill=(90, 90, 90), font=fn)
    canvas.save(out_path, "JPEG", quality=82)
    return out_path


def main():
    os.makedirs(THUMBS, exist_ok=True)
    os.makedirs(SHEETS, exist_ok=True)
    jobs = list(enumerate(SEL))
    with ThreadPoolExecutor(max_workers=4) as ex:
        paths = list(ex.map(lambda t: fetch(*t), jobs))
    got = sum(1 for p in paths if p)
    print(f"thumbnails: {got}/{len(SEL)}")
    by_sec = {}
    for i, w in enumerate(SEL):
        by_sec.setdefault(w["section"], []).append((i, paths[i]))
    for num, rows in by_sec.items():
        t = next(w["section_title"] for w in SEL if w["section"] == num)
        out = sheet(rows, os.path.join(SHEETS, f"section-{num}.jpg"),
                    f"{num}  {t}  ({len(rows)})")
        print("  ", out)


if __name__ == "__main__":
    main()
