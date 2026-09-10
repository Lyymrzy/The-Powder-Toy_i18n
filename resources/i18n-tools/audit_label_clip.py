import bz2, re, os, sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = bz2.decompress(open(os.path.join(root, 'resources', 'font.bz2'), 'rb').read())
w = {}
i = 0
while i < len(d):
    cp = d[i] | (d[i+1] << 8) | (d[i+2] << 16)
    w[cp] = d[i+3]
    i += 4 + 3 * d[i+3]

def textw(s):
    # 多行标签(源码里含 \n)按“最宽的一行”计算,而不是整串求和
    best = 0
    for part in s.split('\\n'):
        part = re.sub(r'\\[a-zA-Z]', '', part)   # 去掉 \bg 这类色码(零宽)
        best = max(best, sum(w.get(ord(c), 8) for c in part))
    return best

files = []
for dp, dn, fn in os.walk(os.path.join(root, 'src', 'gui')):
    for f in fn:
        if f.endswith(('.cpp', '.h')):
            files.append(os.path.join(dp, f))

pat = re.compile(r'ui::Label\s*\(\s*ui::Point\s*\([^)]*\)\s*,\s*ui::Point\s*\(\s*(\d+)\s*,')
found = 0
for path in files:
    for n, ln in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
        if 'ui::Label' not in ln or not any(0x4E00 <= ord(c) <= 0x9FFF for c in ln):
            continue
        m = pat.search(ln)
        if not m:
            continue
        width = int(m.group(1))
        # collect CJK literals on this line
        strs = [s for s in re.findall(r'"((?:\\.|[^"\\])*)"', ln)
                if any(0x4E00 <= ord(c) <= 0x9FFF for c in s)]
        if not strs:
            continue
        need = max(textw(s) for s in strs)
        if need > width:
            found += 1
            print('%s:%d  labelW=%d need=%d  %s' % (os.path.relpath(path, root), n, width, need, ln.strip()[:110]))
print('--- potential clipped labels:', found)
