#!/usr/bin/env python3
"""Set the quote on every hope plate.

The type sits on a gradient that starts a quarter of the way up from the bottom edge and
gets darker towards the foot, so the art is untouched above it and the line is legible
below it. The type is set in a classic face, with a hairline lining around the block and
the reference letterspaced beneath the line.

The whole overlay — gradient, quote, lining, reference — is drawn on a canvas twice the
size of the plate and then reduced, so the edges of the letters stay clean at thumbnail
size instead of being drawn small and soft.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
SUP = "/System/Library/Fonts/Supplemental"

# face name -> (file, index for the quote, index for the small caps reference)
FONTS = {
    "baskerville": (f"{SUP}/Baskerville.ttc", 0, 4),
    "iowan": (f"{SUP}/Iowan Old Style.ttc", 0, 1),
    "didot": (f"{SUP}/Didot.ttc", 0, 2),
    "bodoni": (f"{SUP}/Bodoni 72.ttc", 0, 2),
    "hoefler": (f"{SUP}/Hoefler Text.ttc", 0, 1),
    "caslon": (f"{SUP}/BigCaslon.ttf", 0, 0),
    "charter": (f"{SUP}/Charter.ttc", 0, 3),
    "palatino": ("/System/Library/Fonts/Palatino.ttc", 0, 1),
    "optima": ("/System/Library/Fonts/Optima.ttc", 0, 2),
    "georgia": (f"{SUP}/Georgia.ttf", 0, 0),
    "gill": (f"{SUP}/GillSans.ttc", 0, 4),
}

FACE = os.environ.get("HOPE_FONT", "baskerville")
LINING = os.environ.get("HOPE_LINING", "none")
ONLY = os.environ.get("HOPE_ONLY", "")

CREAM = (248, 245, 238)
DARK = (16, 15, 14)
RULE = (214, 207, 194)
MUTED = (222, 216, 204)
SHADOW = (8, 8, 9)
PALE = (247, 244, 238)
INK_DARK = (26, 24, 22)
MUTED_DARK = (92, 87, 80)
LIGHT_ART = 135       # at or above this the painting is treated as light
MAX_ALPHA = 172          # the gradient is kept soft, never a solid bar
LIGHT_SOFT = 0.42          # a light picture gets proportionally less of it
SHADOW_STRENGTH = 0.62
SUPER = 2  # the overlay is drawn at twice the size and reduced


def load_font(size, face="quote"):
    path, quote_idx, ref_idx = FONTS[FACE]
    return ImageFont.truetype(path, size, index=quote_idx if face == "quote" else ref_idx)


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


def spaced_w(draw, text, font, spacing):
    if not text:
        return 0
    return sum(draw.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)


def letterspaced(draw, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def layout(draw, W, H, text, ref):
    margin = max(26, round(W * 0.062))
    max_w = W - margin * 2
    size = max(26, min(116, round(min(W * 0.058, H * 0.088))))
    while True:
        font = load_font(size)
        lines = wrap(draw, text, font, max_w)
        lh = round(size * 1.34)
        if len(lines) * lh <= H * 0.46 or size <= 26:
            break
        size = max(26, int(size * 0.94))
    ref_size = max(14, round(size * 0.36))
    ref_font = load_font(ref_size, "ref")
    ref_spacing = max(1.0, size * 0.155)
    ref_gap = round(size * 0.80)
    ref_h = round(ref_size * 1.25)
    ref_w = spaced_w(draw, ref.upper(), ref_font, ref_spacing)
    quote_w = max([draw.textlength(l, font=font) for l in lines] or [0])
    block_w = max(quote_w, ref_w)
    pad_x = round(size * 0.62)
    pad_y = round(size * 0.46)
    block_h = len(lines) * lh + ref_gap + ref_h
    bottom_pad = max(margin, round(H * 0.055))
    text_top = H - bottom_pad - block_h
    return dict(margin=margin, font=font, lines=lines, lh=lh, size=size,
                 ref_font=ref_font, ref_size=ref_size, ref_gap=ref_gap,
                 ref_spacing=ref_spacing, ref_h=ref_h, block_w=block_w,
                 quote_w=quote_w, pad_x=pad_x, pad_y=pad_y,
                 text_top=text_top, block_h=block_h, W=W, H=H)


def gradient_mask(W, h, hold=0, power=1.9, alpha=MAX_ALPHA):
    """A vertical mask that is clear at the top and darkest from `hold` down.

    The ramp reaches full darkness at `hold` rows and stays there, so the ground
    under the first line of type is already dark and the line reads cleanly.
    """
    strip = Image.new("L", (1, h))
    px = strip.load()
    for y in range(h):
        t = (y / hold) if hold > 0 else (y / max(1, h - 1))
        px[0, y] = int(alpha * (min(1.0, t) ** power))
    return strip.resize((W, h), Image.Resampling.BILINEAR)


def draw_lining(d, L, S, oy=0):
    """The lining around the text block, drawn on the doubled canvas.

    oy is the top of the panel in image coordinates, so every y is measured from it.
    """
    style = LINING
    if style == "none":
        return
    w = max(1, round(1 * S))
    x0 = round((L["margin"] - L["pad_x"]) * S)
    x1 = round((L["margin"] + L["block_w"] + L["pad_x"]) * S)
    top = round((L["text_top"] - oy - L["pad_y"]) * S)
    foot = round((L["text_top"] - oy + L["block_h"] + L["pad_y"]) * S)
    mid = round((L["text_top"] - oy + len(L["lines"]) * L["lh"]
                 + L["ref_gap"] * 0.42) * S)
    if style == "rule":
        d.line([(x0, top), (x1, top)], fill=RULE, width=w)
        return
    if style == "rules":
        d.line([(x0, top), (x1, top)], fill=RULE, width=w)
        d.line([(x0, foot), (x1, foot)], fill=RULE, width=w)
        return
    if style == "under":
        d.line([(x0, mid), (x1, mid)], fill=RULE, width=w)
        return
    if style == "side":
        d.line([(x0, top), (x0, foot)], fill=RULE, width=w)
        return
    if style == "ticks":
        # four small corner ticks, the way a plate is marked rather than boxed
        arm_x = round((x1 - x0) * 0.045)
        arm_y = round((foot - top) * 0.16)
        for cx, cy, sx, sy in ((x0, top, 1, 1), (x1, top, -1, 1),
                               (x0, foot, 1, -1), (x1, foot, -1, -1)):
            d.line([(cx, cy), (cx + sx * arm_x, cy)], fill=RULE, width=w)
            d.line([(cx, cy), (cx, cy + sy * arm_y)], fill=RULE, width=w)
        return
    if style == "frame":
        # a hairline inset from the plate edge, as a printed plate is ruled
        inset = round(min(L["W"], L["H"]) * 0.028)
        d.rectangle([inset, inset, L["W"] - inset, L["H"] - inset],
                    outline=RULE, width=w)
        return
    # box: a thin rectangle around the quote and the reference
    d.rectangle([x0, top, x1, foot], outline=RULE, width=w)


def band_luma(im, band_top):
    """How light the picture is where the gradient will fall, 0-255."""
    band = im.crop((0, band_top, im.width, im.height)).convert("L")
    return band.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))


def text_shadow(panel, L, S, oy, fonts, colour=SHADOW):
    """A soft dark shadow behind the type, so cream still reads on light art."""
    layer = Image.new("L", panel.size, 0)
    d = ImageDraw.Draw(layer)
    off = max(1, round(L["size"] * 0.05 * S))
    y = (L["text_top"] - oy) * S
    for line in L["lines"]:
        d.text((L["margin"] * S + off, y + off), line, font=fonts[0], fill=255)
        y += L["lh"] * S
    y = (L["text_top"] - oy + len(L["lines"]) * L["lh"] + L["ref_gap"]
         - round(L["size"] * 0.14)) * S
    letterspaced(d, (L["margin"] * S + off, y + off), ref_upper(L),
                 fonts[1], 255, L["ref_spacing"] * S)
    blur = max(2, round(L["size"] * 0.085 * S))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    layer = layer.point(lambda v: int(v * SHADOW_STRENGTH))
    panel.paste(Image.new("RGB", panel.size, colour), (0, 0), layer)


def ref_upper(L):
    return L["ref"].upper()


def draw_quote(im, ref, text):
    """Set the line into a gradient that starts a quarter of the way up.

    A dark picture gets a dark gradient and cream type. A picture that is already
    light gets much less of it, and the type turns dark, because a dark bar over a
    white painting reads as a bar rather than as a shadow.
    """
    im = im.convert("RGB")
    W, H = im.size
    S = SUPER
    L = layout(ImageDraw.Draw(im), W, H, text, ref)
    L["ref"] = ref

    # the gradient starts 25% away from the bottom edge, and never later than a
    # little above the first line, so the type always sits on the dark part
    band_top = min(round(H * 0.75), max(0, L["text_top"] - round(L["size"] * 0.75)))
    h = H - band_top

    # how light the picture is where the gradient will fall
    lum = band_luma(im, band_top)
    light_art = lum >= LIGHT_ART
    ground = PALE if light_art else DARK
    ink = INK_DARK if light_art else CREAM
    muted = MUTED_DARK if light_art else MUTED
    shadow = PALE if light_art else SHADOW

    panel = Image.new("RGB", (W * S, h * S), ground)
    big = load_font(L["size"] * S)
    big_ref = load_font(L["ref_size"] * S, "ref")
    # a pale ground needs no halo; a dark one does
    if not light_art:
        text_shadow(panel, L, S, band_top, (big, big_ref), shadow)
    d = ImageDraw.Draw(panel)
    y = (L["text_top"] - band_top) * S
    for line in L["lines"]:
        d.text((L["margin"] * S, y), line, font=big, fill=ink)
        y += L["lh"] * S
    y = (L["text_top"] - band_top + len(L["lines"]) * L["lh"] + L["ref_gap"]
         - round(L["size"] * 0.14)) * S
    letterspaced(d, (L["margin"] * S, y), ref.upper(), big_ref, muted,
                 L["ref_spacing"] * S)
    draw_lining(d, L, S, band_top)

    # a light picture takes a much lighter gradient, so the panel never reads
    # as a bar laid over the painting
    alpha = max(70, round(MAX_ALPHA * (1.0 - LIGHT_SOFT * lum / 255.0)))
    if light_art:
        alpha = round(alpha * 0.78)
    hold = max(1, round((L["text_top"] - band_top) * 1.15))
    small = panel.resize((W, h), Image.Resampling.LANCZOS)
    mask = gradient_mask(W * S, h * S, hold * S, 1.9,
                         alpha).resize((W, h), Image.Resampling.LANCZOS)
    im.paste(small, (0, band_top), mask)
    return im


def main():
    import sys
    sys.path.insert(0, BASE)
    from works import WORKS
    lines = json.load(open(os.path.join(BASE, "lines.json")))
    full = os.path.join(BASE, "img/full")
    out = os.path.join(BASE, "img/versed")
    thumb = os.path.join(BASE, "img/versed-thumb")
    os.makedirs(out, exist_ok=True)
    os.makedirs(thumb, exist_ok=True)
    todo = [w for w in WORKS if not ONLY or w["slug"] == ONLY]
    made, missing = 0, []
    for w in todo:
        src = os.path.join(full, w["slug"] + ".jpg")
        line = lines.get(w["slug"])
        if not line or not os.path.exists(src):
            missing.append(w["slug"])
            continue
        im = draw_quote(Image.open(src), line["ref"], line["text"])
        im.save(os.path.join(out, w["slug"] + ".jpg"), "JPEG", quality=93)
        th = im.copy()
        th.thumbnail((700, 700), Image.Resampling.LANCZOS)
        th.save(os.path.join(thumb, w["slug"] + ".jpg"), "JPEG", quality=90)
        made += 1
    print(f"{FACE}/{LINING}: {made} plates set, {len(missing)} missing")


if __name__ == "__main__":
    main()
