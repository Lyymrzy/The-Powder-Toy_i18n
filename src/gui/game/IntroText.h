#pragma once
#include "Config.h"
#include "SimulationConfig.h"
#include "common/String.h"

inline ByteString VersionInfo()
{
	ByteStringBuilder sb;
	sb << DISPLAY_VERSION[0] << "." << DISPLAY_VERSION[1];
	if constexpr (!SNAPSHOT)
	{
		sb << "." << APP_VERSION.build;
	}
	sb << " " << IDENT;
	if constexpr (MOD)
	{
		sb << " MOD " << MOD_ID << " UPSTREAM " << UPSTREAM_VERSION.build;
	}
	if constexpr (SNAPSHOT)
	{
		sb << " SNAPSHOT " << APP_VERSION.build;
	}
	if constexpr (LUACONSOLE)
	{
		sb << " LUACONSOLE";
	}
	if constexpr (NOHTTP)
	{
		sb << " NOHTTP";
	}
	else if constexpr (ENFORCE_HTTPS)
	{
		sb << " HTTPS";
	}
	if constexpr (DEBUG)
	{
		sb << " DEBUG";
	}
	return sb.Build();
}

inline ByteString IntroText()
{
	ByteStringBuilder sb;
	sb << "\bl\bU" << APPNAME << "\bU - Version " << DISPLAY_VERSION[0] << "." << DISPLAY_VERSION[1] << " - https://powdertoy.co.uk, irc.libera.chat #powder, https://tpt.io/discord\n"
	      "\n"
	      "\n"
	      "\bg按\bo'F1'\bg 显示或隐藏本说明。\n"
	      "\n"
	      "\bg选择材料：把鼠标移到右侧的分类图标上，即可展开该类别下的元素。\n"
	      "\bg用\bo鼠标左/右键\bg从菜单中选取材料。\n"
	      "\bg按住\bo鼠标左/右键\bg在绘图区拖拽，即可自由画出线条。\n"
	      "\n"
	      "\bg用\bo鼠标滚轮\bg或\bo'['\bg、\bo']'\bg键改变粒子工具大小；按\boTab\bg切换笔刷形状。\n"
	      "\bo鼠标中键\bg或\boAlt+单击\bg可取样粒子。\n"
	      "\boCtrl+C/V/X\bg 分别为复制、粘贴与剪切。\n"
	      "\bg粘贴时用\bo'R'\bg旋转，\boShift+R\bg 与 \boShift+Ctrl+R\bg 分别做垂直、水平镜像。\n"
	      "\boShift+拖拽\bg可画直线粒子；\boShift+Alt+拖拽\bg可画水平、垂直与对角线。\n"
	      "\boCtrl+拖拽\bg填充实心矩形，\boCtrl+Alt+拖拽\bg填充实心正方形；\boCtrl+Shift+单击\bg对封闭区域填充。\n"
	      "\n"
	      "\bo空格\bg可暂停物理模拟。用\bo'F'\bg逐帧前进，\bo'F5'\bg重新加载模拟。\n"
	      "\boCtrl+Z\bg撤销，\boCtrl+Y\bg或\boCtrl+Shift+Z\bg重做。\n"
	      "\bg用\bo'S'\bg把窗口的一部分保存为印章；\bo'L'\bg载入最近保存的印章；\bo'K'\bg打开印章库。\n"
	      "\n"
	      "\bg用\bo0-9\bg选择视图模式。\n"
	      "\bg用\bo'H'\bg开关 HUD。用\bo'D'\bg在 HUD 中切换调试模式。\n"
	      "\bg用\bo'Z'\bg放大镜：单击让放大窗口固定，用滚轮调整放大强度。\n"
	      "\bg用\boCtrl+F\bg在屏幕上高亮指定的元素。\n"
	      "\n";
	if constexpr (BETA)
	{
		sb << "\br这是测试版（BETA），无法公开保存，也无法在旧版本中打开本版制作的本地存档与印章。\n"
		      "\br若要公开发布存档，请使用正式版本。\n";
	}
	else
	{
		sb << "\bg要使用在线功能（如保存存档），请先在 \br" << SERVER << "/Register.html \bg注册。\n";
	}
	sb << "\n\bt" << VersionInfo();
	return sb.Build();
}
