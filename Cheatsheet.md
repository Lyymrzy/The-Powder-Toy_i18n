# 汉化工程速查(CJK / i18n Cheatsheet)

本仓库是 The Powder Toy 的中文汉化 fork。本文档只做开发速查用途,**不参与构建**(meson 不会读取它)。

---

## 1. 构建

工具链:WinLibs UCRT64 GCC 16.2,位于 `D:\_toolchain\mingw64\bin`(需先加入 PATH)

```powershell
$env:Path = "D:\_toolchain\mingw64\bin;" + $env:Path
ninja -C build
```

- 产物:`build\powder.exe`(运行所需的 3 个 GCC 运行时 DLL 已放在 `build\` 下)
- 若链接报 `cannot open output file powder.exe: Permission denied`,说明**游戏正在运行**,关掉再链接
- 首次配置(需要时):
  ```powershell
  meson setup build -Dstatic=prebuilt --buildtype=release -Dwindows_utf8cp=false
  ```
  `-Dwindows_utf8cp=false` 是必需的:binutils 2.47 会因 gcc 默认清单与 `.rc` 内嵌清单冲突而报 multiple manifests

## 2. 翻译数据流(重要)

```
resources/gen_translations.py   ← 权威源(ELEMENT_ZH / TOOL_ZH / FIXED 都在这里)
        │  python resources\gen_translations.py
        ▼
resources/translations.json     ← 自动生成,不要手改(会被覆盖)
resources/glossary.json         ← 元素词表(手改),补全后同样要重跑上面那条命令
        │  构建期由 resources/meson.build → to-array.py 内嵌成 *_json.h
        ▼
src/i18n.cpp (Tr / CodeName / CodeGloss / GlossCodes) → 运行时取词
```

改完词典/词表后**务必重跑**:

```powershell
python resources\gen_translations.py
```

## 3. 自查工具(`resources/i18n-tools/`)

| 工具 | 用途 |
| --- | --- |
| `file_glyph_check.py <文件>` | 检查某文件里的中文字符串是否有字形(缺字会显示成方框) |
| `audit_translations.py` | 审计 `translations.json`:缺字形 / 半角标点 / 键含非 ASCII |
| `audit_label_clip.py` | 扫描 `src/gui` 里 `ui::Label` 宽度是否够放中文(`Label` 会按 `Size` **裁剪文本**) |
| `audit_glossary.py` | 比对"元素 Name"与词表键:找出漏掉的和失效的条目 |
| `scan_inline_punct.py` | 扫描内联中文旁的半角 `, : ; ? !` |
| `scan_parens.py` | 扫描内联中文旁的半角 `( )` |
| `wrap_sim.py` | 复刻 `TextWrapper` 换行算法,用于验证中文断行/裁剪行为 |

用法示例:

```powershell
python resources\i18n-tools\file_glyph_check.py src\gui\options\OptionsView.cpp
python resources\i18n-tools\audit_translations.py
python resources\i18n-tools\audit_glossary.py
python resources\i18n-tools\audit_label_clip.py
```

## 4. 已踩过的坑(改代码前先看)

- **字库缺字形**:`—`(U+2014)、`“ ”`(U+201C/201D)、`…`(U+2026)、`℃`(U+2103)都没有。
  用 `：`、`「」`、`...`、`°C` 代替。中文标点一律用全角。
- **`String` 与字面量**:`src/common/String.h` 里"字面量 → `String`"的隐式构造已改为 **UTF-8 解码**
  (原本是 `FromAscii`,中文会乱码);`String::Build` / `StringBuilder <<` 本来就是 UTF-8。
- **`ui::Label` 会裁剪**:文本超过自身 `Size.X` 就被截断。中文比英文宽,遇到固定宽度的标签要
  同步加宽(用 `audit_label_clip.py` 体检)。
- **词表键 = 元素的 `Name`(显示码),不是文件名/identifier**。特例:
  `LO2.cpp`→`LOXY`、`O2.cpp`→`OXYG`、`H2.cpp`→`HYGN`、`LNTG.cpp`→`LN2`、`ICEI.cpp`→`ICE`、
  `IGNT.cpp`→`IGNC`、`GUNP.cpp`→`GUN`、`BANG.cpp`→`TNT`、`NBHL.cpp`→`BHOL`、`NWHL.cpp`→`WHOL`、
  `CBNW.cpp`→`BUBW`、`SPAWN.cpp`→`SPWN`、`SPAWN2.cpp`→`SPWN2`、`STKM2.cpp`→`STK2`、
  `BREC.cpp`→`BREL`、`WHOL.cpp`→`VENT`、`WIRE.cpp`→`WWLD`、`E116.cpp`→`EQVE`、`CFLM.cpp`→`CFLM`
- **`C-4` / `C-5`** 这类含连字符的名称不会被词表匹配(分词只认 `[A-Za-z0-9]`),保持原样显示。
- **未启用元素**(如 `BIZRG`/`BIZRS`/`INVIS`/`SHLD1-4`/`VACU`)没有中文描述,词表也就无需补。
- **中文件名存档**:`src/common/platform/Common.cpp` 已改用宽字符路径打开(`_wfopen` + `WinWiden`)。
  注意 `WinWiden` 只在 `Windows.cpp` 实现,平台相关代码要放进 `#ifdef _WIN32`。
- **在线存档名限制为 ASCII**:`ServerSaveActivity::Save()` 会拒绝非 ASCII 名称(与官方服务器一致)。
- 汉化文本尽量写成"一句话一段",换行由 `TextWrapper` 处理(已支持 CJK 逐字断行 + 避头尾)。

## 5. 字体(CJK 字形)

- `resources/font.bz2` 已注入 Fusion Pixel 12px 的 CJK 字形约 1.9 万个(原始拉丁字库备份:`resources/font.bz2.bak`)
- 追加字形(手动):`python fonttool.py addbdf <起始码位> <结束码位> <BDF文件> 0 -2`
  (`fonttool.py` 需要十进制码位;`-2` 是 y 偏移,否则汉字底部两行会被裁掉)

**一键复现(合并上游后如需重新注入,就用这个)**:

```powershell
# 1) 取得字体源文件 Fusion Pixel Font 12px monospaced zh_hans BDF
#    项目:https://github.com/TakWolf/fusion-pixel-font (OFL-1.1)
#    发布包内的文件名:fusion-pixel-12px-monospaced-zh_hans.bdf
#    SHA256 应为:9CB8F307B8835FF071E62EAA2FD473FA0683D0AE2C5AF8583EB9C5A183953F00
#    (脚本会自动校验,不匹配只会警告)

# 2) 重新注入(脚本会先把 font.bz2 重置到 HEAD,再注入 3000-303F / 4E00-9FFF / FF00-FFEF)
python resources\cjkfont\import_cjk.py <路径>\fusion-pixel-12px-monospaced-zh_hans.bdf
```

- 预览脚本与 OFL 许可证在 `resources/cjkfont/`(许可是分发要求,勿删)

## 6. 同步上游更新

本 fork 保留了上游完整历史,merge 即可:

```powershell
git remote add upstream https://github.com/The-Powder-Toy/The-Powder-Toy.git   # 只需一次
git fetch upstream master --no-tags
git switch -c sync/upstream-$(Get-Date -Format yyyyMM)
git merge upstream/master            # 用 merge,不要 rebase
```

合并后固定动作:

```powershell
python resources\gen_translations.py      # translations.json 必须重生成
python resources\cjkfont\import_cjk.py <BDF>   # 仅当 font.bz2 冲突(取上游版后重新注入)
ninja -C build
python resources\i18n-tools\audit_glossary.py
python resources\i18n-tools\audit_translations.py
```

容易冲突的地方(保留我们这一侧的改动):

| 文件 | 我们改了什么 |
| --- | --- |
| `resources/font.bz2` / `font.bz2.bak` | CJK 注入(二进制;已在 `.gitattributes` 标 `binary`) |
| `resources/translations.json`、`glossary.json` | 翻译数据(冲突后重跑 `gen_translations.py` 即可) |
| `src/common/String.h` | 字面量 → `String` 改走 UTF-8 解码 |
| `src/gui/interface/TextWrapper.cpp` | CJK 按字换行 + 避头尾规则 |
| `src/common/platform/Common.cpp` | `OpenFileUTF8()`:`_wfopen` 宽字符路径(中文文件名) |
| `resources/meson.build`、`src/meson.build` | 内嵌 `translations_json`/`glossary_json` 与 `i18n.cpp` |
| `src/gui/game/GameController.cpp`、`GameModel.cpp` | 翻译挂钩(`GlossCodes` / `AllocTool` 的 `Tr`);这两处上游也常改,最可能冲突 |
| `src/gui/**` 各界面文件 | 内联中文(整行替换,冲突时人工合一下) |

远端现状(2026-09-10 记录):仅 `origin`(本 fork)+ `upstream`(官方);本地 `master` 曾领先 `origin/master` 数个提交,
合并前先 `git push` 备份。
