import bz2, os, re

root = r'd:\G_GitHub_Repo\The-Powder-Toy_i18n'
d = bz2.decompress(open(os.path.join(root, 'resources', 'font.bz2'), 'rb').read())
w = {}
i = 0
while i < len(d):
    cp = d[i] | (d[i+1] << 8) | (d[i+2] << 16)
    w[cp] = d[i+3]
    i = i + 4 + 3 * d[i+3]

def cw(c):
    return w.get(ord(c), 6)

def may_break_after(c):
    o = ord(c)
    return (0x2E80 <= o <= 0x303F) or (0x3040 <= o <= 0x9FFF) or (0xAC00 <= o <= 0xD7AF) \
        or (0xF900 <= o <= 0xFAFF) or (0xFE30 <= o <= 0xFE4F) or (0xFF00 <= o <= 0xFF60) \
        or (0xFFE0 <= o <= 0xFFE6) or (0x20000 <= o <= 0x2FA1F)

NO_BREAK_BEFORE = set('、。，．！？：；」』】〕）］｝》〉…')
NO_BREAK_AFTER = set('「『【〔（［｛《〈')

def wrap(text, max_width, cjk_breaks):
    """strict port of ui::TextWrapper::Update (wrapping part)"""
    out = []
    line_width = 0
    word_begins_at = -1
    word_width = 0

    def wrap_if_needed(width_to_consider, char_width):
        nonlocal line_width
        if width_to_consider + char_width > max_width:
            out.append(('\n', 0))
            line_width = 0
            return True
        return False

    it, n = 0, len(text)
    while it < n:
        ch = text[it]
        c = cw(ch)
        seq = 2 if ch == '\b' else (1 if ch == '\x0e' else (4 if ch == '\x0f' else 0))
        if ch == ' ':
            if wrap_if_needed(line_width, c):
                if out and out[-1][0] == '\n':
                    pass          # C++: may_eat_space makes this space disappear
                else:
                    out.append((ch, c)); line_width += c
            else:
                out.append((ch, c)); line_width += c
            word_begins_at = -1
        elif ch == '\n':
            out.append((ch, max_width - line_width)); line_width = 0; word_begins_at = -1
        else:
            if seq:
                for k in range(it, min(it + seq, n)):
                    out.append((text[k], 0))
                it += seq
                continue
            if word_begins_at == -1:
                word_begins_at = len(out); word_width = 0
            if wrap_if_needed(word_width, c):
                word_begins_at = len(out)
                word_width = 0
            if wrap_if_needed(line_width, c):
                nl = out.pop()
                out.insert(word_begins_at, nl)
                word_begins_at += 1
                line_width = word_width
            out.append((ch, c)); word_width += c; line_width += c
            if ch in '?;,:.-!':
                word_begins_at = -1
            elif cjk_breaks and may_break_after(ch) and ch not in NO_BREAK_AFTER \
                    and not (it + 1 < n and text[it + 1] in NO_BREAK_BEFORE):
                word_begins_at = -1
        it += 1

    cur, lines = [], []
    for ch, wd in out:
        if ch == '\n':
            lines.append(cur); cur = []
        else:
            cur.append(ch)
    lines.append(cur)
    return [re.sub(r'[\x00-\x1f]', '', ''.join(l)) for l in lines]

para = ("以 \bt~\bw 开头即可进行高级搜索。这种搜索会同时匹配存档标题、描述、用户名与标签，而不只限于标题与标签。"
        " 它还会把搜索词之间按「与（AND）」处理，而不是「或」。")

for tag, cjk in (('修复前', False), ('修复后', True)):
    print('===== %s (max_width=372) =====' % tag)
    for ln in wrap(para, 372, cjk):
        print('  [%3d] %s' % (sum(cw(c) for c in ln), ln))
