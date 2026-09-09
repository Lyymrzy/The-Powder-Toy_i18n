# resources/cjkfont — CJK 字模来源与再生成

本目录记录了 `../font.bz2` 中新增中文字形的**来源、授权与可复现步骤**。

## 改了什么
`../font.bz2` 在原有拉丁字库基础上**纯新增**了 19,387 个 CJK 字形,覆盖:

| 区间 | 内容 |
|---|---|
| U+3000 – U+303F | CJK 符号与标点(`。、`等) |
| U+4E00 – U+9FFF | CJK 统一表意文字(常用简体全覆盖) |
| U+FF00 – U+FFEF | 全角形式(`,`、`。`、`０-９` 等全角标点/数字) |

- 原拉丁/ASCII 区字形**零改动**(注入工具只添加缺失码点,不覆盖已有字形)。
- 2026-09-09 定稿版 `../font.bz2` = 307,993 字节;原始拉丁版可在 git 历史 `HEAD:resources/font.bz2` 找到(本目录生成时用 `resources/font.bz2.bak` 作对照)。

## 字体来源(上游)
- **Fusion Pixel Font(缝合像素字体)12px Mono zh_hans**
  - 作者/版权:`Copyright (c) 2022, TakWolf (https://takwolf.com)`
  - 授权:**SIL Open Font License 1.1**(见本目录 `LICENSE-OFL.txt`;官方文本由 openfontlicense.org 提供)
  - 项目:https://github.com/TakWolf/fusion-pixel-font
  - 发布版:2026.09.01
  - 用到的字形源文件:`fusion-pixel-12px-monospaced-bdf-v2026.09.01.zip` 内的 `fusion-pixel-12px-monospaced-zh_hans.bdf`

### 下载与校验(SHA-256)
- 发布包 zip:
  `https://github.com/TakWolf/fusion-pixel-font/releases/download/2026.09.01/fusion-pixel-font-12px-monospaced-bdf-v2026.09.01.zip`
  `5B1CAC9253FA9E20B9FEA5FD582EEED985819A3CE4B7F7FB108F8D6E599AD211`
- 其中 `fusion-pixel-12px-monospaced-zh_hans.bdf`:
  `9CB8F307B8835FF071E62EAA2FD473FA0683D0AE2C5AF8583EB9C5A183953F00`

## 授权/合规要点
- 从融合字库抽取并转码进 `font.bz2` 的部分构成 OFL 意义上的"修改版",须**继续按 OFL-1.1 分发**,并随分发携带版权声明与本许可文本。
- 允许随本软件(含商业软件)捆绑、内嵌、再分发;**禁止把字体本身单独售卖**;不得使修改版使用上游保留名称(本仓库不使用 "Fusion Pixel Font" 作为衍生字模名称)。
- 若日后改用以其他字体,请同步更新本 README 与许可文件。

## 再生成步骤(可复现)
前置:仓库根有 `fonttool.py`(Python3,内置 bz2);本机已装 Python。
1. 下载上述 zip 并解压,取得 `fusion-pixel-12px-monospaced-zh_hans.bdf`(核对上方 sha256)。
2. 从原始拉丁字库重新开始(确保幂等):
   ```powershell
   git checkout HEAD -- resources/font.bz2
   ```
3. 一键导入(等价于下面三条 `fonttool.py addbdf`,关键参数 **yoffs=-2**,否则会裁掉汉字底部两行):
   ```powershell
   python fonttool.py addbdf 12288  12351  <bdf> 0 -2   # U+3000-303F
   python fonttool.py addbdf 19968  40959  <bdf> 0 -2   # U+4E00-9FFF
   python fonttool.py addbdf 65280  65519  <bdf> 0 -2   # U+FF00-FFEF
   ```
   或直接:
   ```powershell
   python resources/cjkfont/import_cjk.py <path-to-zh_hans.bdf>
   ```
4. 校验:字库仅新增、拉丁区零改动;抽查 `水`(U+6C34)应为 11 行完整字高。

> 说明:`fonttool.py addbdf` 码点参数是**十进制**;默认映射会把 BDF y=0 对齐记录第 11 行、裁掉融合字 y<0 的底部两行,因此必须传 `yoffs=-2`。

## 目录文件
- `LICENSE-OFL.txt` — OFL-1.1 官方全文(openfontlicense.org 纯文本)
- `README.md` — 本说明
- `import_cjk.py` — 一键再生成脚本(校验源文件后重灌三个区间)
- `preview_cjk.py` — 中英混排预览生成器(纯标准库,便于翻译 QA 时目检渲染与对齐):
  `python preview_cjk.py <font.bz2> <out.png>`

## 字体渲染管线备忘(供后续汉化)
- `resources/font.bz2` 构建期经 `resources/to-array.py` 嵌入为 `font_bz2` 字节数组。
- 逐字形格式:3B 小端码点 + 1B 宽度 + `宽度*3` 字节(每字节 4 像素、2-bit alpha),字形高固定 12 行(`FONT_H=12`)。
- 绘制:缺字形回落 `0xFFFD`(方块);`BlendText`/`TextSize` 逐 Unicode 码点取字,天然支持 CJK。
- 相关源:`src/graphics/FontReader.{h,cpp}`、`src/graphics/RasterDrawMethodsImpl.h`。
