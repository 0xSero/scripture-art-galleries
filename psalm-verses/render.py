#!/usr/bin/env python3
"""Bake a short KJV psalm line onto every work in the three galleries.

Originals in img/full and img/thumb are never touched. Versed copies are written
to img/versed and img/versed-thumb. The line is set in Charter (Bitstream
Charter, Apple's system text face) — a low-contrast book serif chosen for
readability rather than display — left-aligned over an adaptive scrim: the bottom
band of the artwork is blurred and tinted either dark or light depending on how
bright that band is, so the type stays legible on both pale and near-black
paintings without flattening the picture.

For the parents gallery every plate carries a short line of at most ten words; the
lines live in excerpts.json and the full verse stays in verses.json as the record.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PSALMS = json.load(open(os.path.join(BASE, "kjv-psalms.json")))
BIBLE = json.load(open(os.path.join(BASE, "kjv-bible.json")))
ASSIGN = json.load(open(os.path.join(BASE, "assignments.json")))
EXCERPTS = {k: v for k, v in
            json.load(open(os.path.join(BASE, "excerpts.json"))).items()
            if not k.startswith("_")}

GALLERIES = ["friends-gallery", "love-gallery", "parents-gallery", "grief-gallery"]
FONT = "/System/Library/Fonts/Supplemental/Charter.ttc"
FACE = {"roman": 0, "italic": 1, "bold": 3}

DARK_TINT = (13, 12, 11)
LIGHT_TINT = (246, 242, 234)
CREAM_INK = (248, 245, 238)
DARK_INK = (22, 20, 18)
MUTED_ON_DARK = (218, 212, 200)
MUTED_ON_LIGHT = (88, 82, 74)


def parse_ref(ref):
    """'Book chapter:verse' -> (book, chapter, verse); 'chapter:verse' -> Psalms."""
    head, v = ref.rsplit(":", 1)
    if " " in head.strip():
        book, ch = head.rsplit(" ", 1)
        return book.strip(), ch.strip(), v.strip()
    return "Psalms", head.strip(), v.strip()


def verse_text(gallery, slug):
    """Return (reference, full KJV verse, text to set on the plate).

    A reference is either "Book chapter:verse" (resolved in the whole-Bible
    corpus) or a bare "chapter:verse", which is a Psalm and resolves in the
    Psalms corpus the friends and love galleries were built from.
    """
    ref = ASSIGN[gallery][slug]
    book, ch, v = parse_ref(ref)
    if " " in ref.rsplit(":", 1)[0]:
        verses = BIBLE[book][ch]
        shown = f"Psalm {ch}:{v}" if book == "Psalms" else f"{book} {ch}:{v}"
    else:
        verses = PSALMS[ch]
        shown = f"Psalm {ch}:{v}"
    match = [x for x in verses if str(x["v"]) == v]
    if not match:
        raise SystemExit(f"missing {ref} for {gallery}/{slug}")
    full = match[0]["t"]
    return shown, full, EXCERPTS.get(slug, full)


def load_font(size, face="roman"):
    return ImageFont.truetype(FONT, size, index=FACE[face])


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def band_luminance(im, top):
    """Mean luminance of the band below `top`, 0-255."""
    band = im.crop((0, top, im.width, im.height)).convert("L")
    small = band.resize((1, 1), Image.Resampling.BOX)
    return small.getpixel((0, 0))


def gradient_mask(w, h, ramp_px):
    """Vertical L mask: 0 at the top edge, ramping to 255 over ramp_px."""
    ramp = max(1, min(int(ramp_px), h))
    strip = Image.new("L", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = 255 if y >= ramp else int(255 * (y / ramp))
    return strip.resize((w, h), Image.Resampling.BILINEAR)


def letterspaced(draw, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def render(im, ref, text):
    W, H = im.size
    im = im.convert("RGB")

    margin = max(24, round(W * 0.060))
    max_w = W - margin * 2
    size = max(24, min(108, round(min(W * 0.052, H * 0.082))))
    lh_ratio = 1.40

    while True:
        font = load_font(size, "roman")
        probe = ImageDraw.Draw(im)
        lines = wrap(probe, text, font, max_w)
        lh = round(size * lh_ratio)
        block_h = len(lines) * lh
        if block_h <= H * 0.44 or size <= 24:
            break
        size = max(24, int(size * 0.94))

    ref_font = load_font(max(14, round(size * 0.42)), "bold")
    ref_gap = round(size * 0.95)
    ref_spacing = max(1.0, size * 0.15)
    ref_h = round(size * 0.42 * 1.2)

    block_h = len(lines) * lh + ref_gap + ref_h
    bottom_pad = max(margin, round(H * 0.038))
    text_top = H - bottom_pad - block_h
    band_top = max(0, text_top - round(size * 1.05))

    dark_art = band_luminance(im, band_top) < 148
    tint = DARK_TINT if dark_art else LIGHT_TINT
    ink = CREAM_INK if dark_art else DARK_INK
    muted = MUTED_ON_DARK if dark_art else MUTED_ON_LIGHT

    blur = max(3, round(W * 0.019))
    band = im.crop((0, band_top, W, H)).filter(ImageFilter.GaussianBlur(blur))
    fade = gradient_mask(W, H - band_top, ramp_px=text_top - band_top)
    tint_mask = fade.point(lambda v: int(v * 0.88))
    band = Image.composite(Image.new("RGB", band.size, tint), band, tint_mask)
    im.paste(band, (0, band_top), fade)

    draw = ImageDraw.Draw(im)
    y = text_top
    for line in lines:
        draw.text((margin, y), line, font=font, fill=ink)
        y += lh
    y = text_top + len(lines) * lh + ref_gap - round(size * 0.16)
    letterspaced(draw, (margin, y), ref.upper(), ref_font, muted, ref_spacing)
    return im


def main():
    wanted = sys.argv[1:] or GALLERIES
    for g in wanted:
        if g not in GALLERIES:
            raise SystemExit(f"unknown gallery {g}")
    total = 0
    for g in wanted:
        root = f"/Users/sero/{g}"
        manifest = json.load(open(os.path.join(root, "manifest.json")))
        out_full = os.path.join(root, "img", "versed")
        out_thumb = os.path.join(root, "img", "versed-thumb")
        os.makedirs(out_full, exist_ok=True)
        os.makedirs(out_thumb, exist_ok=True)

        verses = {}
        for w in manifest:
            slug = w["slug"]
            ref, full, text = verse_text(g, slug)
            _, ch, v = parse_ref(ASSIGN[g][slug])
            verses[slug] = {"ref": ref, "text": text, "full": full,
                            "excerpt": text != full,
                            "chapter": int(ch), "verse": int(v)}

            src = Image.open(os.path.join(root, "img", "full", f"{slug}.jpg"))
            out = render(src.copy(), ref, text)
            full_out = os.path.join(out_full, f"{slug}.jpg")
            out.save(full_out, "JPEG", quality=93, subsampling=0, optimize=True)

            tw, th = Image.open(os.path.join(root, "img", "thumb", f"{slug}.jpg")).size
            thumb = out.resize((tw, th), Image.Resampling.LANCZOS)
            thumb.save(os.path.join(out_thumb, f"{slug}.jpg"), "JPEG",
                       quality=90, subsampling=0, optimize=True)
            total += 1
            print(f"  {g}/{slug}: {ref} -> {out.size[0]}x{out.size[1]}")

        json.dump(verses, open(os.path.join(root, "verses.json"), "w"),
                  ensure_ascii=False, indent=1)

    print(f"\nrendered {total} versed images")


if __name__ == "__main__":
    main()
