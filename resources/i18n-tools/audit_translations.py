#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bz2, json, sys

def load_font(path):
    d = bz2.decompress(open(path, 'rb').read())
    i, s = 0, set()
    while i < len(d):
        cp = d[i] | (d[i+1] << 8) | (d[i+2] << 16)
        s.add(cp)
        i += 4 + 3 * d[i+3]
    return s

font = load_font(sys.argv[1] if len(sys.argv) > 1 else r'd:\G_GitHub_Repo\The-Powder-Toy_i18n\resources\font.bz2')
data = json.load(open(sys.argv[2] if len(sys.argv) > 2 else r'd:\G_GitHub_Repo\The-Powder-Toy_i18n\resources\translations.json', encoding='utf-8'))

# 1) non-ASCII chars used in values, and whether glyph exists
missing = {}
used = {}
for k, v in data.items():
    for ch in v:
        o = ord(ch)
        if o > 0x7F:
            used.setdefault(ch, 0)
            used[ch] += 1
            if o not in font:
                missing.setdefault(ch, [])
                if len(missing[ch]) < 4:
                    missing[ch].append(k)
print("== non-ASCII chars used in values ==")
for ch, n in sorted(used.items(), key=lambda x: -x[1]):
    print("U+%04X %s x%d %s" % (ord(ch), ch, n, "  <-- MISSING GLYPH" if ord(ch) not in font else ""))
print()
print("== chars MISSING from font (sample keys) ==")
for ch, ks in missing.items():
    print("U+%04X %s  e.g. %s" % (ord(ch), ch, ks[:3]))

# 2) ASCII punctuation inside CJK (non-ascii) values -> candidates for fullwidth
print()
print("== ASCII punct used inside CJK strings ==")
import collections
ascii_punct = collections.Counter()
for k, v in data.items():
    has_cjk = any(ord(c) > 0x2E80 for c in v)
    if not has_cjk:
        continue
    for ch in v:
        if ch in ',!?();:\'"~`[]':
            ascii_punct[ch] += 1
for ch, n in ascii_punct.most_common():
    print("ascii %r x%d" % (ch, n))

# 3) check keys that contain CJK (keys should be pure English)
badkeys = [k for k in data if any(ord(c) > 0x7F for c in k)]
print()
print("keys containing non-ASCII:", len(badkeys))
for k in badkeys[:10]:
    print("  ", repr(k))
