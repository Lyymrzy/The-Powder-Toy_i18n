[English](README.md) | [简体中文](README.zh.md)

The Powder Toy - 2026 年 6 月
==========================

请[从 Powder Toy 官网](https://powdertoy.co.uk/Download.html)获取最新版本。我们也上架了 [Steam](https://store.steampowered.com/app/1148350/The_Powder_Toy/)。

若要使用存档等在线功能，你需要先[注册账号](https://powdertoy.co.uk/Register.html)。
你也可以访问 [TPT 官方论坛](https://powdertoy.co.uk/Discussions/Categories/Index.html)。

你有没有想过炸点什么？或者一直梦想亲手操作一座核电站？还是想造一块自己的 CPU？The Powder Toy 都能满足你，而且远不止这些！

The Powder Toy 是一款免费的物理沙盒游戏，它模拟气压、气流速度、热量、重力，以及各种物质之间数不清的相互作用！游戏提供了各种建筑材料、液体、气体和电子元件，你可以用它们搭建复杂的机械、枪械、炸弹、逼真的地形，几乎任何东西。之后你还能把它们挖开、欣赏酷炫的爆炸、接上复杂的电路、摆弄小人，或者操作你的机器。你可以浏览并游玩社区制作的成千上万个存档，也可以上传你自己的作品——我们欢迎你的创作！

游戏还提供 Lua API——你可以把自己的操作自动化，甚至为游戏编写插件。The Powder Toy 是免费软件，源代码以 GNU 通用公共许可证分发，因此你可以自行修改游戏，或者参与开发。

构建说明
===========================================================================

请参阅 wiki 主页上的 _Powder Toy 开发帮助（Powder Toy Development Help）_ 一节。

特别鸣谢
===========================================================================

* Stanislaw K Skowronek - 设计了最初的 Powder Toy
* Simon Robertshaw - 编写了网站，现任服务器所有者
* Skresanov Savely
* Pilihp64
* Catelite
* Victoria Hoyle
* Nathan Cousins
* jacksonmj
* Felix Wallin
* Lieuwe Mosch
* Anthony Boot
* Me4502
* MaksProg
* jacob1
* mniip
* LBPHacker

使用的第三方库与素材
===========================================================================

* [bzip2](http://www.bzip.org/)
* [FFTW](http://fftw.org/)
* [JsonCpp](https://github.com/open-source-parsers/jsoncpp)
* [libcurl](https://curl.se/libcurl/)
* [libpng](http://www.libpng.org/pub/png/libpng.html)
* [Lua](https://www.lua.org/)
* [LuaJIT](https://luajit.org/)
* [Mallangche](https://github.com/JammPark/Mallangche)
* [mbedtls](https://www.trustedfirmware.org/projects/mbed-tls/)
* [SDL](https://libsdl.org/)

玩法说明
===========================================================================

用鼠标点选元素并在画面中绘制，就像用 MS Paint 一样。剩下的就是在游戏中慢慢摸索会发生什么。

操作按键
===========================================================================

| 按键 | 功能 |
| ----------------------- | --------------------------------------------------------------- |
| TAB | 在圆形／方形／三角形笔刷之间切换 |
| Space | 暂停 |
| Q / Esc | 退出 |
| Z | 缩放 |
| S | 保存图章（STK2 取出时配合 Ctrl 使用） |
| L | 载入上次保存的图章 |
| K | 图章库 |
| 0-9 | 设置显示模式 |
| P / F2 | 将截图保存为 .png |
| E | 打开元素搜索 |
| F | 暂停并单步前进一帧 |
| G | 增大网格间距 |
| Shift + G | 减小网格间距 |
| H | 显示／隐藏 HUD |
| Ctrl + H / F1 | 显示说明文字 |
| D / F3 | 调试模式（STK2 取出时配合 Ctrl 使用） |
| I | 反转压力与速度显示 |
| W | 循环切换重力模式（STK2 取出时配合 Ctrl 使用） |
| Y | 循环切换空气模式 |
| Ctrl + E | 循环切换边界模式 |
| B | 进入装饰编辑器菜单 |
| Ctrl + B | 开关装饰层 |
| N | 开关牛顿引力 |
| U | 开关环境热 |
| Ctrl + I | 安装 Powder Toy，以便双击载入存档／图章 |
| 点号键（`） | 开关控制台 |
| = | 重置压力与速度场 |
| Ctrl + = | 重置电力 |
| \[ | 减小笔刷尺寸 |
| \] | 增大笔刷尺寸 |
| Alt + \[ | 笔刷尺寸减 1 |
| Alt + \] | 笔刷尺寸加 1 |
| Ctrl + C/V/X | 复制／粘贴／剪切 |
| Ctrl + Z | 撤销 |
| Ctrl + Y | 重做 |
| Ctrl + 拖动光标 | 矩形 |
| Shift + 拖动光标 | 直线 |
| 中键单击 | 取样元素 |
| Alt + 左键单击 | 取样元素 |
| 鼠标滚轮 | 改变笔刷尺寸 |
| Ctrl + 鼠标滚轮 | 改变笔刷竖直尺寸 |
| Shift + 鼠标滚轮 | 改变笔刷水平尺寸 |
| Shift + R | 粘贴图章时水平镜像所选区域 |
| Ctrl + Shift + R | 粘贴图章时竖直镜像所选区域 |
| R | 粘贴图章时逆时针旋转所选区域 |
| F11 | 开关全屏 |

命令行
---------------------------------------------------------------------------

| 命令 | 说明 | 示例 |
| --------------------- | ------------------------------------------------ | --------------------------------------------|
| `scale:SIZE` | 改变窗口缩放系数 | `scale:2` |
| `kiosk` | 全屏模式 | |
| `proxy:SERVER[:PORT]` | 要使用的代理服务器 | `proxy:wwwcache.lancs.ac.uk:8080` |
| `open FILE` | 以图章或存档的形式打开文件 | |
| `ddir DIRECTORY` | 用于保存图章与首选项的目录 | |
| `ptsave:SAVEID` | 打开在线存档，供 ptsave: 链接使用 | `ptsave:2198` |
| `disable-network` | 禁用网络连接 | |
| `disable-bluescreen` | 禁用蓝屏处理程序 | |
| `redirect` | 把输出重定向到 stdout.txt / stderr.txt | |
| `console` | 在 Windows 上把输出重定向到新的控制台 | |
| `cafile:CAFILE` | 设置证书捆绑包路径 | `cafile:/etc/ssl/certs/ca-certificates.crt` |
| `capath:CAPATH` | 设置证书目录路径 | `capath:/etc/ssl/certs` |
