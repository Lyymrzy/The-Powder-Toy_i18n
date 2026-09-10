import json, re, os, glob

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gloss = json.load(open(os.path.join(root, 'resources', 'glossary.json'), encoding='utf-8'))

# ELEMENT_ZH: 文件名/标识符 -> 中文描述(没有条目的元素通常是未启用的)
src = open(os.path.join(root, 'resources', 'gen_translations.py'), encoding='utf-8').read()
body = re.search(r'ELEMENT_ZH\s*=\s*\{(.*?)\n\}', src, re.S).group(1)
zh = dict(re.findall(r'"([A-Z0-9_]{2,8})"\s*:\s*"((?:[^"\\]|\\.)*)"', body))

# identifier -> Name (anchor on Identifier, take the nearest following Name)
ident2name, names = {}, {}
for path in glob.glob(os.path.join(root, 'src', 'simulation', 'elements', '*.cpp')):
    fn = os.path.basename(path)[:-4]
    s = open(path, encoding='utf-8', errors='replace').read()
    for mi in re.finditer(r'Identifier\s*=\s*"DEFAULT_PT_([A-Z0-9_]+)"', s):
        tail = s[mi.end():mi.end() + 4000]
        mn = re.search(r'\bName\s*=\s*"([A-Z0-9-]{1,6})"', tail)
        if mn:
            ident2name[mi.group(1)] = mn.group(1)
            names[mn.group(1)] = (os.path.basename(path)[:-4], zh.get(fn, ''))

keys = {k for k in gloss if not k.startswith('_')}
missing = sorted(n for n in names if n not in keys)
dead = sorted(k for k in keys if k not in names)

print('元素 Name 总数:', len(names), '| 词表条目:', len(keys))
print('--- 词表缺失(会显示裸码):%d ---' % len(missing))
for n in missing:
    fn, desc = names[n]
    print('  %-5s file=%-7s %s' % (n, fn, desc[:24] if desc else '(无中文描述 -> 很可能未启用)'))
print('--- 词表中无效键(不对应任何元素 Name):%d ---' % len(dead))
for k in dead:
    print('  %-6s %s' % (k, gloss[k]))
