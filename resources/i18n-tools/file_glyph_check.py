import bz2, re, sys

d = bz2.decompress(open(r'd:\G_GitHub_Repo\The-Powder-Toy_i18n\resources\font.bz2', 'rb').read())
i = 0
font = set()
while i < len(d):
    cp = d[i] | (d[i+1] << 8) | (d[i+2] << 16)
    font.add(cp)
    i += 4 + 3 * d[i+3]

src = open(sys.argv[1], encoding='utf-8').read()
miss = set()
for m in re.finditer(r'"((?:\\.|[^"\\])*)"', src):
    s = m.group(1)
    if not any(0x4E00 <= ord(c) <= 0x9FFF for c in s):
        continue
    s = re.sub(r'\\.', '', s)
    for ch in s:
        o = ord(ch)
        if o > 0x7F and o not in font:
            miss.add(ch)
print('%s missing glyphs:' % sys.argv[1],
      [('%s U+%04X' % (c, ord(c))) for c in sorted(miss)] if miss else 'none')
