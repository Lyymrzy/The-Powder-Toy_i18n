import re, os

files = [
    r'src\gui\game\GameView.cpp',
    r'src\gui\game\QuickOptions.cpp',
    r'src\gui\render\RenderView.cpp',
    r'src\gui\options\OptionsView.cpp',
    r'src\gui\filebrowser\FileBrowserActivity.cpp',
    r'src\gui\localbrowser\LocalBrowserView.cpp',
    r'src\gui\localbrowser\LocalBrowserController.cpp',
    r'src\gui\interface\SaveButton.cpp',
    r'src\gui\game\tool\PropertyTool.h',
    r'src\gui\game\IntroText.h',
]
root = r'd:\G_GitHub_Repo\The-Powder-Toy_i18n'
for rel in files:
    for i, ln in enumerate(open(os.path.join(root, rel), encoding='utf-8'), 1):
        if not any(0x4E00 <= ord(c) <= 0x9FFF for c in ln):
            continue
        # halfwidth '(' or ')' with CJK adjacent on either side (not inside \bg(...) hotkey-only)
        for m in re.finditer(r'[()]', ln):
            lo = max(0, m.start()-1)
            hi = min(len(ln), m.end()+1)
            seg = ln[lo:hi]
            if any(0x4E00 <= ord(c) <= 0x9FFF for c in seg):
                print('%s:%d: %s' % (rel, i, ln.strip()[:140]))
                break
