#!/usr/bin/env python3
"""One day of world news, drawn as a newspaper front page.

Writes a 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output). Python 3.13 standard library only, no network,
no randomness, no clock: two runs write byte-identical files.

The page sums up Tuesday 24 November 2026: the masthead names the
day, the lead story is Nvidia reinstating Jensen Huang, four panels
cover Hormuz, Ukraine, the Myanmar genocide ruling and the COP31
collapse, and an IN BRIEF strip adds Riyadh, Huawei and Grok.
Every word is drawn from a small 5x7 pixel font embedded below,
so the text stays crisp at any size the page is viewed at.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (251, 247, 238)
INK = (17, 17, 17)
RED = (163, 22, 33)

# 5x7 pixel font. Each glyph is 7 rows of 5 bits, top row first.
FONT = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01110', '10001', '10000', '10000', '10000', '10001', '01110'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01110', '10001', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('01110', '00100', '00100', '00100', '00100', '00100', '01110'),
    'J': ('00111', '00010', '00010', '00010', '00010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    'a': ('00000', '00000', '01110', '00001', '01111', '10001', '01111'),
    'b': ('10000', '10000', '11110', '10001', '10001', '10001', '11110'),
    'c': ('00000', '00000', '01110', '10001', '10000', '10001', '01110'),
    'd': ('00001', '00001', '01111', '10001', '10001', '10001', '01111'),
    'e': ('00000', '00000', '01110', '10001', '11111', '10000', '01110'),
    'f': ('00110', '01001', '01000', '11110', '01000', '01000', '01000'),
    'g': ('00000', '01111', '10001', '10001', '01111', '00001', '01110'),
    'h': ('10000', '10000', '11110', '10001', '10001', '10001', '10001'),
    'i': ('00100', '00000', '01100', '00100', '00100', '00100', '01110'),
    'j': ('00010', '00000', '00110', '00010', '00010', '10010', '01100'),
    'k': ('10000', '10000', '10010', '10100', '11000', '10100', '10010'),
    'l': ('01100', '00100', '00100', '00100', '00100', '00100', '01110'),
    'm': ('00000', '00000', '11010', '10101', '10101', '10101', '10101'),
    'n': ('00000', '00000', '11110', '10001', '10001', '10001', '10001'),
    'o': ('00000', '00000', '01110', '10001', '10001', '10001', '01110'),
    'p': ('00000', '00000', '11110', '10001', '10001', '11110', '10000'),
    'q': ('00000', '00000', '01111', '10001', '10001', '01111', '00001'),
    'r': ('00000', '00000', '10110', '11001', '10000', '10000', '10000'),
    's': ('00000', '00000', '01111', '10000', '01110', '00001', '11110'),
    't': ('01000', '01000', '11110', '01000', '01000', '01001', '00110'),
    'u': ('00000', '00000', '10001', '10001', '10001', '10011', '01101'),
    'v': ('00000', '00000', '10001', '10001', '10001', '01010', '00100'),
    'w': ('00000', '00000', '10001', '10101', '10101', '10101', '01010'),
    'x': ('00000', '00000', '10001', '01010', '00100', '01010', '10001'),
    'y': ('00000', '00000', '10001', '10001', '01111', '00001', '01110'),
    'z': ('00000', '00000', '11111', '00010', '00100', '01000', '11111'),
    '0': ('01110', '10001', '10011', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00110', '01000', '10000', '11111'),
    '3': ('11111', '00010', '00100', '00010', '00001', '10001', '01110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('00110', '01000', '10000', '11110', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00010', '01100'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
    '.': ('00000', '00000', '00000', '00000', '00000', '01100', '01100'),
    ',': ('00000', '00000', '00000', '00000', '01100', '00100', '01000'),
    ':': ('00000', '01100', '01100', '00000', '01100', '01100', '00000'),
    ';': ('00000', '01100', '01100', '00000', '01100', '00100', '01000'),
    "'": ('00100', '00100', '01000', '00000', '00000', '00000', '00000'),
    '"': ('01010', '01010', '00000', '00000', '00000', '00000', '00000'),
    '!': ('00100', '00100', '00100', '00100', '00100', '00000', '00100'),
    '?': ('01110', '10001', '00001', '00110', '00100', '00000', '00100'),
    '-': ('00000', '00000', '00000', '01110', '00000', '00000', '00000'),
    '(': ('00010', '00100', '01000', '01000', '01000', '00100', '00010'),
    ')': ('01000', '00100', '00010', '00010', '00010', '00100', '01000'),
    '%': ('11001', '11010', '00010', '00100', '01000', '01011', '10011'),
    '/': ('00001', '00010', '00010', '00100', '01000', '01000', '10000'),
    '+': ('00000', '00100', '00100', '11111', '00100', '00100', '00000'),
    '=': ('00000', '00000', '11111', '00000', '11111', '00000', '00000'),
    '&': ('01100', '10010', '10100', '01000', '10101', '10010', '01101'),
    '$': ('00100', '01111', '10100', '01110', '00101', '11110', '00100'),
}

BUF = bytearray(W * H * 3)
for _i in range(0, W * H * 3, 3):
    BUF[_i] = PAPER[0]
    BUF[_i + 1] = PAPER[1]
    BUF[_i + 2] = PAPER[2]


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        BUF[o] = color[0]
        BUF[o + 1] = color[1]
        BUF[o + 2] = color[2]


def rect(x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, color)


def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)


def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)


def line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        px(x, y, color)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def circle(cx, cy, r, color):
    for dx in range(-r, r + 1):
        dy = int((r * r - dx * dx) ** 0.5)
        px(cx + dx, cy + dy, color)
        px(cx + dx, cy - dy, color)
        px(cx + dy, cy + dx, color)
        px(cx - dy, cy + dx, color)


def disc(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, color)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s:
        rows = FONT.get(ch, FONT[' '])
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == '1':
                    rect(cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return cx - scale


def center_text(cx, y, s, scale, color):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    words = s.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, color, max_w, leading):
    yy = y
    for ln in wrap(s, scale, max_w):
        draw_text(x, yy, ln, scale, color)
        yy += leading
    return yy


# ---- small pictograms, one per panel (36x36 box) ----

def icon_tanker(x, y):
    rect(x + 2, y + 20, 32, 8, INK)
    line(x + 2, y + 20, x + 6, y + 28, INK)
    line(x + 34, y + 20, x + 30, y + 28, INK)
    rect(x + 6, y + 10, 8, 10, RED)
    rect(x + 15, y + 10, 8, 10, INK)
    rect(x + 24, y + 10, 8, 10, INK)
    hline(x, y + 31, 36, INK, 2)
    hline(x + 4, y + 34, 28, INK, 1)


def icon_burst(x, y):
    cx, cy = x + 18, y + 18
    for k in range(8):
        ang = k * 3.141592653589793 / 4.0
        c = 1 if k % 2 == 0 else 0
        import math
        r1 = 6
        r2 = 17 if c else 12
        x1 = int(cx + r1 * math.cos(ang))
        y1 = int(cy + r1 * math.sin(ang))
        x2 = int(cx + r2 * math.cos(ang))
        y2 = int(cy + r2 * math.sin(ang))
        line(x1, y1, x2, y2, INK)
    disc(cx, cy, 4, RED)


def icon_court(x, y):
    line(x + 18, y + 2, x + 2, y + 12, INK)
    line(x + 18, y + 2, x + 34, y + 12, INK)
    hline(x + 2, y + 12, 33, INK, 2)
    rect(x + 5, y + 15, 4, 14, INK)
    rect(x + 16, y + 15, 4, 14, INK)
    rect(x + 27, y + 15, 4, 14, INK)
    hline(x + 2, y + 30, 33, INK, 2)
    hline(x, y + 33, 37, INK, 2)


def icon_globe(x, y):
    cx, cy = x + 18, y + 18
    circle(cx, cy, 15, INK)
    hline(cx - 15, cy, 31, INK, 1)
    line(cx, cy - 15, cx, cy + 15, INK)
    for dx in (-8, 8):
        for sgn in (-1, 1):
            px(cx + dx, cy + sgn * 12, INK)
            px(cx + dx, cy + sgn * 13, INK)
    disc(cx - 6, cy - 8, 2, RED)


def icon_chip(x, y, w, h):
    # computer chip: body, inner die, pins, NVDA label
    rect(x, y, w, h, INK)
    rect(x + 6, y + 6, w - 12, h - 12, PAPER)
    rect(x + 26, y + 26, w - 52, h - 52, INK)
    rect(x + 32, y + 32, w - 64, h - 64, PAPER)
    for i in range(5):
        px0 = x + 20 + i * 34
        rect(px0, y - 12, 12, 12, INK)
        rect(px0, y + h, 12, 12, INK)
        py0 = y + 20 + i * 30
        rect(x - 12, py0, 12, 12, INK)
        rect(x + w, py0, 12, 12, INK)
    label = 'NVDA'
    draw_text(x + (w - text_w(label, 4)) // 2, y + (h - 28) // 2, label, 4, RED)


# ---- page layout ----

def draw_page():
    # double border
    rect(14, 14, W - 28, 3, INK)
    rect(14, H - 17, W - 28, 3, INK)
    rect(14, 14, 3, H - 28, INK)
    rect(W - 17, 14, 3, H - 28, INK)
    rect(21, 21, W - 42, 1, INK)
    rect(21, H - 22, W - 42, 1, INK)
    rect(21, 21, 1, H - 42, INK)
    rect(W - 22, 21, 1, H - 42, INK)

    # nameplate
    center_text(W // 2, 32, 'THE DAILY WORLD', 10, INK)
    hline(48, 116, W - 96, INK, 2)
    center_text(W // 2, 128, 'TUESDAY, 24 NOVEMBER 2026', 5, INK)
    hline(48, 174, W - 96, RED, 3)

    # lead story
    draw_text(48, 194, 'TECHNOLOGY - UNITED STATES', 3, RED)
    draw_text(48, 224, 'HUANG BACK', 7, INK)
    draw_text(48, 282, 'AT NVIDIA', 7, INK)
    para(48, 342, 'Board reinstates Jensen Huang as chief executive days '
         'after his resignation; shares jump about 30%.', 3, INK, 640, 28)
    icon_chip(742, 200, 190, 170)

    hline(48, 428, W - 96, INK, 2)

    # four panels, 2 x 2
    panels = [
        (48, 448, 'MIDDLE EAST', 'THREE TANKERS HIT MINES IN HORMUZ',
         'Iran refuses talks until its seven conditions are met.', icon_tanker),
        (528, 448, 'UKRAINE', 'STRIKE ON ZAPORIZHZHIA KILLS 2',
         'Russian attack wounds about 40; Kyiv says drones hit a '
         'warship.', icon_burst),
        (48, 672, 'WORLD COURT', 'MYANMAR GUILTY OF GENOCIDE',
         'World court rules Myanmar committed genocide against the '
         'Rohingya.', icon_court),
        (528, 672, 'CLIMATE', 'CLIMATE TALKS END WITH NO DEAL',
         'COP31 collapses without agreement on fossil fuels.', icon_globe),
    ]
    for (px0, py0, kicker, head, deck, icon) in panels:
        draw_text(px0, py0, kicker, 3, RED)
        icon(px0 + 452 - 36, py0 - 8)
        yy = py0 + 34
        for ln in wrap(head, 4, 452):
            draw_text(px0, yy, ln, 4, INK)
            yy += 34
        yy += 6
        para(px0, yy, deck, 3, INK, 452, 27)

    hline(48, 884, W - 96, INK, 2)

    # in brief: three full-width lines, each one line high
    draw_text(48, 896, 'IN BRIEF', 3, RED)
    briefs = [
        'Houthi missile hits Riyadh tower; 11 hurt',
        'Huawei found guilty of U.S. criminal charges',
        'States sue Musk firms over Grok images',
    ]
    by = 926
    for item in briefs:
        rect(48, by + 6, 8, 8, RED)
        draw_text(66, by, item, 3, INK)
        by += 26


def chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += BUF[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', ihdr)
    data += chunk(b'IDAT', comp)
    data += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


def main():
    draw_page()
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'entry.png')
    size = write_png(path)
    print('wrote %s (%d bytes, %dx%d)' % (path, size, W, H))


if __name__ == '__main__':
    main()
