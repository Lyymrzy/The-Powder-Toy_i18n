#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a CJK + Latin preview PNG from resources/font.bz2 using the exact
layout rules TPT uses (FONT_H=12 rows, -2px top offset, per-glyph advance,
2-bit alpha blend). Pure stdlib (zlib) PNG writer. Use: python preview_cjk.py <font.bz2> <out.png>
"""
import bz2, sys, zlib, struct

FONT_H = 12

def load_font(path):
    d = bz2.decompress(open(path, 'rb').read())
    i, m = 0, {}
    while i < len(d):
        cp = d[i] | (d[i+1] << 8) | (d[i+2] << 16)
        w = d[i+3]
        data = d[i+4:i+4+3*w]
        # decode 2-bit pixels, 4 per byte, LSB-first
        rows = []
        bit = 0; byte = 0; p = 0
        for r in range(FONT_H):
            row = []
            for x in range(w):
                if bit == 0:
                    byte = data[p]; p += 1; bit = 8
                row.append(byte & 3); byte >>= 2; bit -= 2
            rows.append(row)
        m[cp] = (w, rows)
        i += 4 + 3 * w
    return m

def text_size(font, s):
    x = y = 0; mx = 0
    for ch in s:
        if ch == '\n':
            mx = max(mx, x); x = 0; y += FONT_H
        else:
            w, _ = font.get(ord(ch), (0, None))
            x += w
    return max(mx, x), y + FONT_H

class Canvas:
    def __init__(self, w, h, bg=(48, 48, 56)):
        self.w, self.h = w, h
        self.px = [list(bg) for _ in range(w * h)]
    def blend(self, x, y, c, a):  # a in 0..255
        if x < 0 or y < 0 or x >= self.w or y >= self.h or a <= 0:
            return
        i = y * self.w + x
        p = self.px[i]
        p[0] = p[0] + (c[0] - p[0]) * a // 255
        p[1] = p[1] + (c[1] - p[1]) * a // 255
        p[2] = p[2] + (c[2] - p[2]) * a // 255
    def glyph(self, x, y, font, cp, color):
        if cp not in font:
            return 0
        w, rows = font[cp]
        for r in range(FONT_H):
            row = rows[r]
            for xx, v in enumerate(row):
                if v:
                    self.blend(x + xx, y - 2 + r, color, v * 255 // 3)
        return w
    def text(self, x, y, font, s, color=(255, 255, 255)):
        x0 = x
        for ch in s:
            if ch == '\n':
                x = x0; y += FONT_H; continue
            x += self.glyph(x, y, font, ord(ch), color)
    def png(self, path):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            for x in range(self.w):
                raw += bytes(self.px[y * self.w + x])
        def chunk(tag, data):
            c = struct.pack('>I', len(data)) + tag + data
            return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        ihdr = struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)
        png = b'\x89PNG\r\n\x1a\n'
        png += chunk(b'IHDR', ihdr)
        png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
        png += chunk(b'IEND', b'')
        open(path, 'wb').write(png)

def main():
    font_path, out = sys.argv[1], sys.argv[2]
    font = load_font(font_path)

    lines = [
        ("LATIN", "Water. Conducts electricity, freezes"),
        ("CJK",   "水:可导电的液体,会冻结并灭火。"),
        ("CJK",   "沙:重颗粒,受热熔化成玻璃。"),
        ("CJK",   "火:可燃物质,燃烧产生高温。"),
        ("MIX",   "The Powder Toy 粉末玩具 汉化"),
        ("MIX",   "Ctrl+Z 撤销  Space 暂停  0-9 视图"),
        ("CJK",   "——测试:全角,顿号、句号。引号\u201c试\u201d!"),
    ]
    # check coverage of CJK sample text
    missing = sorted({ord(c) for _, s in lines for c in s if ord(c) > 0x2E80 and ord(c) not in font})
    if missing:
        print('MISSING in font:', ' '.join('U+%04X(%s)' % (c, chr(c)) for c in missing))

    maxw = max(text_size(font, s)[0] for _, s in lines)
    GUTTER = 12 + 8 * 6 + 6  # tag column width
    W, H = GUTTER + maxw + 12, len(lines) * 14 + 16
    c = Canvas(W, H)
    y = 14
    for tag, s in lines:
        col = {'LATIN': (160, 255, 160), 'CJK': (160, 220, 255), 'MIX': (255, 220, 120)}.get(tag, (255, 255, 255))
        c.text(12, y, font, tag.ljust(5) + ' | ', (140, 140, 140))
        c.text(12 + 8 * 6 + 4, y, font, s, col)
        y += 14

    # upscale 4x nearest (simulate window scale)
    S = 4
    big = Canvas(W * S, H * S, bg=c.px[0])
    for yy in range(H):
        for xx in range(W):
            p = c.px[yy * W + xx]
            for dy in range(S):
                base = (yy * S + dy) * big.w + xx * S
                for dx in range(S):
                    big.px[base + dx] = list(p)
    big.png(out)
    print('wrote', out, big.w, 'x', big.h)

if __name__ == '__main__':
    main()
