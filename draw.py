#!/usr/bin/env python3
"""Draw the 24 Nov 2026 news front page (1024x1024 PNG) from stories.json."""
import json
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
GREY = (90, 88, 80)
GREEN = (18, 120, 60)
LIGHT = (238, 232, 218)
RULE = (200, 192, 172)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(d, x, y, lines, fnt, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def main():
    with open("stories.json") as f:
        s = json.load(f)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 30
    x0, x1 = M, W - M

    # ---------- masthead ----------
    d.text((W // 2, 18), s["masthead"], font=font(SERIF, 58), fill=INK, anchor="ma")
    d.line([(x0, 92), (x1, 92)], fill=INK, width=3)
    d.text((x0, 100), s["date"].upper(), font=font(SANS_B, 20), fill=INK)
    d.text((x1, 100), "THE WORLD IN ONE PAGE", font=font(SANS_B, 20), fill=INK, anchor="ra")
    d.line([(x0, 128), (x1, 128)], fill=INK, width=1)

    # ---------- hero ----------
    hy, hh = 142, 238
    d.rectangle([x0, hy, x1, hy + hh], outline=DARKRED, width=3)
    d.rectangle([x0 + 3, hy + 3, x1 - 3, hy + hh - 3], outline=RED, width=1)
    hero = s["hero"]
    d.text((x0 + 18, hy + 12), hero["kicker"], font=font(SANS_B, 16), fill=RED)
    d.text((x0 + 18, hy + 34), hero["headline"], font=font(SERIF, 62), fill=INK)
    d.text((x0 + 18, hy + 112), hero["deck"], font=font(SANS_B, 19), fill=(60, 58, 52))
    y = hy + 142
    for para in hero["body"]:
        lines = wrap(d, para, font(SANS, 16), x1 - x0 - 36)
        y = draw_text_block(d, x0 + 18, y, lines, font(SANS, 16), INK, 21)
        y += 2
    d.rectangle([x0 + 18, hy + hh - 30, x1 - 18, hy + hh - 8], fill=DARKRED)
    d.text(((x0 + x1) // 2, hy + hh - 26), hero["callout"],
           font=font(SANS_B, 15), fill=(255, 255, 255), anchor="ma")

    # ---------- tiles + IN BRIEF ----------
    ty = 396
    tiles_w = 640
    tile_w = (tiles_w - 12) // 2
    tile_h = 130
    brief_x = x0 + tiles_w + 24
    brief_w = x1 - brief_x
    tiles = s["tiles"]
    for i, t in enumerate(tiles):
        tx = x0 + (i % 2) * (tile_w + 12)
        tyy = ty + (i // 2) * (tile_h + 14)
        d.rectangle([tx, tyy, tx + tile_w, tyy + tile_h], outline=RULE, width=1)
        d.text((tx + 10, tyy + 8), t["kicker"], font=font(SANS_B, 12), fill=RED)
        hl = wrap(d, t["headline"], font(SANS_B, 17), tile_w - 20)
        yy = draw_text_block(d, tx + 10, tyy + 26, hl, font(SANS_B, 17), INK, 20)
        bl = wrap(d, t["body"], font(SANS, 13), tile_w - 20)
        draw_text_block(d, tx + 10, yy + 3, bl[:3], font(SANS, 13), (70, 68, 60), 16)

    # IN BRIEF column
    brief_h = 300
    d.rectangle([brief_x, ty, x1, ty + brief_h], outline=INK, width=2)
    d.text((brief_x + 12, ty + 8), "IN BRIEF", font=font(SERIF, 22), fill=INK)
    d.line([(brief_x + 12, ty + 38), (x1 - 12, ty + 38)], fill=INK, width=1)
    by = ty + 46
    for item in s["brief"]:
        d.ellipse([brief_x + 12, by + 5, brief_x + 18, by + 11], fill=RED)
        lines = wrap(d, item, font(SANS, 12), brief_w - 34)
        by = draw_text_block(d, brief_x + 26, by, lines, font(SANS, 12), INK, 15)
        by += 6

    # ---------- wide tile ----------
    wy = ty + brief_h + 16
    wide = s["wide"]
    d.rectangle([x0, wy, x1, wy + 100], fill=LIGHT, outline=INK, width=2)
    d.text((x0 + 16, wy + 8), wide["kicker"], font=font(SANS_B, 14), fill=RED)
    d.text((x0 + 16, wy + 28), wide["headline"], font=font(SERIF, 26), fill=INK)
    bl = wrap(d, wide["body"], font(SANS, 15), x1 - x0 - 32)
    draw_text_block(d, x0 + 16, wy + 62, bl, font(SANS, 15), INK, 19)

    # ---------- markets strip ----------
    my = wy + 100 + 16
    d.rectangle([x0, my, x1, my + 116], outline=INK, width=2)
    d.rectangle([x0, my, x1, my + 30], fill=INK)
    d.text(((x0 + x1) // 2, my + 4), s["markets_label"],
           font=font(SANS_B, 17), fill=(255, 255, 255), anchor="ma")
    mk = s["markets"]
    cell_w = (x1 - x0) / len(mk)
    for i, m in enumerate(mk):
        cx = x0 + i * cell_w
        if i:
            d.line([(cx, my + 34), (cx, my + 106)], fill=RULE, width=1)
        col = GREEN if m["chg"].startswith("+") else RED
        d.text((cx + cell_w / 2, my + 38), m["name"], font=font(SANS_B, 14),
               fill=INK, anchor="ma")
        d.text((cx + cell_w / 2, my + 60), m["value"], font=font(SANS_B, 16),
               fill=INK, anchor="ma")
        d.text((cx + cell_w / 2, my + 84), m["chg"], font=font(SANS_B, 16),
               fill=col, anchor="ma")

    # ---------- footer ----------
    fy = my + 116 + 10
    d.line([(x0, fy), (x1, fy)], fill=INK, width=1)
    d.text((x0, fy + 7), s["sources_note"], font=font(SANS, 13), fill=GREY)
    d.text((x1, fy + 7), s["date"], font=font(SANS_B, 13), fill=GREY, anchor="ra")

    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
