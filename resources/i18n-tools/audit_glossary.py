import json, re, os, glob

root = r'd:\G_GitHub_Repo\The-Powder-Toy_i18n'
gloss = json.load(open(os.path.join(root, 'resources', 'glossary.json'), encoding='utf-8'))

# identifier -> Name (anchor on Identifier, take the nearest following Name)
ident2name, names = {}, {}
for path in glob.glob(os.path.join(root, 'src', 'simulation', 'elements', '*.cpp')):
    s = open(path, encoding='utf-8', errors='replace').read()
    for mi in re.finditer(r'Identifier\s*=\s*"DEFAULT_PT_([A-Z0-9_]+)"', s):
        tail = s[mi.end():mi.end() + 4000]
        mn = re.search(r'\bName\s*=\s*"([A-Z0-9]{1,4})"', tail)
        if mn:
            ident2name[mi.group(1)] = mn.group(1)
            names[mn.group(1)] = os.path.basename(path)

keys = {k for k in gloss if not k.startswith('_')}
missing = sorted(n for n in names if n not in keys)
dead = sorted(k for k in keys if k not in names)

print('元素 Name 总数:', len(names), '| 词表条目:', len(keys))
print('--- 词表缺失(会显示裸码):%d ---' % len(missing))
print(' '.join(missing) if missing else '(none)')
print('--- 词表中无效键(不对应任何元素 Name):%d ---' % len(dead))
for k in dead:
    print('  %-6s %s' % (k, gloss[k]))
