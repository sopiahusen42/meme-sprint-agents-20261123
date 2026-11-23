#!/usr/bin/env python3
"""Build tool: draw entry.png (1024x1024) for "Meme Sprint: AI Agents Ship Games".

Pillow is required and this script runs only on the build machine. The artefact
it produces, entry.png, is committed and shipped beside main.py, which is
standard-library only.

Layout, top to bottom:

    "MY AGENT SHIPPED / THE WHOLE GAME"     white bold caps, upper third
    720x420 card: "NEON VELOCITY" title, a 3/4 arc spinner, "LOADING... 99%",
    a progress bar at 99%, and a grey build line reading
    "v1.0 - 40,812 lines - all tests passing"
    "THE GAME IS A / LOADING SCREEN"        white bold caps, larger, lower third

Caption sizes come from real font metrics and are fitted to the canvas, so the
layout cannot silently drift out of the frame.
"""

import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "entry.png"

W = H = 1024
SIZE_LIMIT = 1_048_576
SIDE_MARGIN = 40
SS = 3  # supersample factor for crisp condensed captions
# One condensation factor shared by every caption, so both blocks look like the
# same condensed display face rather than two different squeezes. DejaVu Sans
# Bold is wide; at natural width the bottom line could only reach a 73 px cap
# height, well under the 110 px the design calls for.
SQUEEZE = 0.655

BG = (11, 11, 15)
WHITE = (255, 255, 255)
CARD_FILL = (17, 17, 25)
CARD_BORDER = (231, 232, 240)
CARD_TEXT = (206, 209, 220)
CARD_DIM = (136, 139, 152)
ACCENT = (54, 226, 255)
TRACK = (41, 43, 56)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TOP_LINES = ["MY AGENT SHIPPED", "THE WHOLE GAME"]
BOTTOM_LINES = ["THE GAME IS A", "LOADING SCREEN"]
TOP_TEXT = "MY AGENT SHIPPED THE WHOLE GAME"
BOTTOM_TEXT = "THE GAME IS A LOADING SCREEN"

GAME_TITLE = "NEON VELOCITY"
LOADING_TEXT = "LOADING\u2026 99%"
VERSION_TEXT = "v1.0 \u00b7 40,812 lines \u00b7 all tests passing"

CARD_W, CARD_H = 720, 420
CARD_RADIUS = 26
CARD_BORDER_W = 6


def font(size):
    return ImageFont.truetype(FONT_PATH, int(size))


def ink(draw, text, f):
    """Ink box of text drawn at the origin: (left, top, right, bottom)."""
    return draw.textbbox((0, 0), text, font=f)


def draw_caption_block(img, lines, cx, y_ink_top, size, squeeze, fill=WHITE):
    """Draw caption lines at `size`, compressed by one shared factor `squeeze`.

    One factor for the whole block keeps the letterforms consistent between
    lines (a real condensed face, not per-line stretching). Rendered at SS
    times target size and downsampled in one pass so edges stay sharp.
    """
    d = ImageDraw.Draw(img)
    big = font(size * SS)
    pad = 16
    boxes, rendered = [], []
    for line in lines:
        b = ink(d, line, big)
        w_big, h_big = int(b[2] - b[0]), int(b[3] - b[1])
        layer = Image.new("RGBA", (w_big + 2 * pad, h_big + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(
            (pad - b[0], pad - b[1]), line, font=big, fill=fill + (255,)
        )
        final_w = max(1, round(w_big / SS * squeeze))
        final_h = max(1, round(layer.height / SS))
        rendered.append((layer.resize((final_w, final_h), Image.Resampling.LANCZOS), h_big / SS))

    y = y_ink_top
    for layer, cap_h in rendered:
        img.paste(layer, (round(cx - layer.width / 2), round(y - pad / SS)), layer)
        boxes.append(
            (round(cx - layer.width / 2), round(y),
             round(cx + layer.width / 2), round(y + cap_h))
        )
        y += cap_h + round(size * 0.10)
    return boxes, round(rendered[0][1])


def fit_caption(lines, max_w, max_h, hi, lo, squeeze=SQUEEZE, gap_ratio=0.10):
    """Largest size at which the block, condensed by `squeeze`, fits the canvas.

    Returns (size, cap_height). Widths are measured before condensing, so the
    check is that width * squeeze stays inside max_w.
    """
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    for size in range(hi, lo, -2):
        f = font(size)
        widths = [(ink(d, ln, f)[2] - ink(d, ln, f)[0]) * squeeze for ln in lines]
        cap = max(ink(d, ln, f)[3] - ink(d, ln, f)[1] for ln in lines)
        if max(widths) > max_w:
            continue
        if 2 * cap + int(size * gap_ratio) <= max_h:
            return size, cap
    raise SystemExit("no caption size fits the canvas")


def main():
    assert " ".join(TOP_LINES) == TOP_TEXT, "top caption words changed"
    assert " ".join(BOTTOM_LINES) == BOTTOM_TEXT, "bottom caption words changed"

    img = Image.new("RGB", (W, H), BG)

    # The bottom caption is the biggest element, so it sets the type scale.
    max_text_w = W - 2 * SIDE_MARGIN
    b_size, b_cap = fit_caption(BOTTOM_LINES, max_text_w, 260, 152, 62)
    b_h = 2 * b_cap + int(b_size * 0.10)
    b_top = H - 48 - b_h

    t_size, t_cap = fit_caption(
        TOP_LINES, max_text_w, 260, min(b_size - 16, 124), 44
    )
    t_h = 2 * t_cap + int(t_size * 0.10)
    t_top = 52

    # Card sits centred in the band between the two captions.
    band_top = t_top + t_h + int(t_size * 0.22)
    band_bottom = b_top - int(b_size * 0.14)
    assert band_bottom - band_top >= CARD_H + 8, (
        f"only {band_bottom - band_top}px between captions, card needs {CARD_H}"
    )
    card_y = round((band_top + band_bottom) / 2 - CARD_H / 2)
    card_y = max(card_y, band_top + 4)
    card_x = (W - CARD_W) // 2
    card_bottom = card_y + CARD_H
    assert card_bottom <= band_bottom, f"card bottom {card_bottom} hits caption {band_bottom}"

    # ---- captions
    top_boxes, _ = draw_caption_block(img, TOP_LINES, W / 2, t_top, t_size, SQUEEZE)
    bot_boxes, _ = draw_caption_block(img, BOTTOM_LINES, W / 2, b_top, b_size, SQUEEZE)

    # ---- card body
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        [card_x, card_y, card_x + CARD_W - 1, card_y + CARD_H - 1],
        radius=CARD_RADIUS,
        fill=CARD_FILL,
        outline=CARD_BORDER,
        width=CARD_BORDER_W,
    )

    tf = font(34)
    tb = ink(d, GAME_TITLE, tf)
    d.text(
        (W / 2 - (tb[2] - tb[0]) / 2 - tb[0], card_y + 32 - tb[1]),
        GAME_TITLE,
        font=tf,
        fill=CARD_TEXT,
    )

    # spinner: faint full ring plus a bright three-quarter arc
    cx, cy, r, ring = W // 2, card_y + 168, 58, 13
    box = [cx - r, cy - r, cx + r, cy + r]
    d.arc(box, start=0, end=360, fill=TRACK, width=ring)
    d.arc(box, start=0, end=270, fill=ACCENT, width=ring)
    for px, py in ((cx + r, cy), (cx, cy - r)):
        d.ellipse(
            [px - ring / 2, py - ring / 2, px + ring / 2, py + ring / 2], fill=ACCENT
        )

    lf = font(50)
    lb = ink(d, LOADING_TEXT, lf)
    l_y = cy + r + 34
    d.text(
        (W / 2 - (lb[2] - lb[0]) / 2 - lb[0], l_y - lb[1]),
        LOADING_TEXT,
        font=lf,
        fill=CARD_TEXT,
    )

    bar_w, bar_h = 512, 20
    bar_x = (W - bar_w) // 2
    bar_y = card_y + 334
    d.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=bar_h // 2, fill=TRACK
    )
    d.rounded_rectangle(
        [bar_x, bar_y, bar_x + round(bar_w * 0.99), bar_y + bar_h],
        radius=bar_h // 2,
        fill=ACCENT,
    )

    vf = font(27)
    vb = ink(d, VERSION_TEXT, vf)
    d.text(
        (W / 2 - (vb[2] - vb[0]) / 2 - vb[0], bar_y + bar_h + 20 - vb[1]),
        VERSION_TEXT,
        font=vf,
        fill=CARD_DIM,
    )

    # ---- numeric proof of the layout
    for name, boxes in (("top", top_boxes), ("bottom", bot_boxes)):
        for left, top, right, bottom in boxes:
            assert left >= SIDE_MARGIN, f"{name} caption past left margin ({left})"
            assert right <= W - SIDE_MARGIN, f"{name} caption past right margin ({right})"
            assert top >= SIDE_MARGIN, f"{name} caption past top margin ({top})"
            assert bottom <= H - SIDE_MARGIN, f"{name} caption past bottom margin ({bottom})"
    for boxes in (top_boxes, bot_boxes):
        assert boxes[-1][3] < card_y or boxes[0][1] > card_bottom, "caption overlaps card"

    print(f"top caption    : {t_size}px, cap {t_cap}px, block {t_h}px, ink y {t_top}")
    print(f"bottom caption : {b_size}px, cap {b_cap}px, block {b_h}px, ink y {b_top}")
    print(f"card           : {CARD_W}x{CARD_H} at ({card_x},{card_y}), bottom {card_bottom}")

    # ---- save, shrinking the palette only if the PNG is over the gate
    img.save(OUT, "PNG", optimize=True)
    if OUT.stat().st_size > SIZE_LIMIT:
        img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            OUT, "PNG", optimize=True
        )

    raw = OUT.read_bytes()
    size = len(raw)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "output is not a PNG"
    iw, ih = struct.unpack(">II", raw[16:24])
    assert (iw, ih) == (W, H), f"canvas is {iw}x{ih}, expected {W}x{H}"
    assert size <= SIZE_LIMIT, f"PNG is {size} bytes, over the {SIZE_LIMIT} limit"
    print(f"wrote {OUT} : {iw}x{ih}, {size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
