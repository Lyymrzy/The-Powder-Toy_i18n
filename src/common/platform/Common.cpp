#include "Platform.h"
#include "resource.h"
#include "common/tpt-rand.h"
#include "Config.h"
#include <memory>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sys/stat.h>

namespace Platform
{

std::string originalCwd;
std::string sharedCwd;

// 以二进制方式打开文件。Windows 上将 UTF-8 路径转为宽字符路径，
// 使中文等非 ASCII 文件名可以正常读写（窄路径会走 ANSI 代码页而失败）。
namespace
{
	FILE *OpenFileUTF8(ByteString filename, const char *mode)
	{
#ifdef _WIN32
		std::wstring wmode(mode, mode + std::strlen(mode));
		return _wfopen(WinWiden(filename).c_str(), wmode.c_str());
#else
		return std::fopen(filename.c_str(), mode);
#endif
	}
}

// Returns a list of all files in a directory matching a search
// search - list of search terms. extensions - list of extensions to also match
std::vector<ByteString> DirectorySearch(ByteString directory, ByteString search, std::vector<ByteString> extensions)
{
	//Get full file listing
	//Normalise directory string, ensure / or \ is present
	if (!directory.size() || (directory.back() != '/' && directory.back() != '\\'))
		directory.append(1, PATH_SEP_CHAR);
	auto directoryList = DirectoryList(directory);

	search = search.ToLower();

	std::vector<ByteString> searchResults;
	for (std::vector<ByteString>::iterator iter = directoryList.begin(), end = directoryList.end(); iter != end; ++iter)
	{
		ByteString filename = *iter, tempfilename = *iter;
		bool extensionMatch = !extensions.size();
		for (auto &extension : extensions)
		{
			if (filename.size() >= extension.size() && filename.EndsWith(extension))
			{
				extensionMatch = true;
				tempfilename = filename.SubstrFromEnd(0, extension.size()).ToLower();
				break;
			}
		}
		bool searchMatch = !search.size();
		if (search.size() && tempfilename.Contains(search))
			searchMatch = true;

		if (searchMatch && extensionMatch)
			searchResults.push_back(filename);
	}

	//Filter results
	return searchResults;
}

bool ReadFile(std::vector<char> &fileData, ByteString filename)
{
	FILE *f = OpenFileUTF8(filename, "rb");
	if (!f)
	{
		std::cerr << "ReadFile: " << filename << ": " << strerror(errno) << std::endl;
		return false;
	}
	bool ok = std::fseek(f, 0, SEEK_END) == 0;
	long size = ok ? std::ftell(f) : -1;
	ok = ok && size >= 0;
	if (ok)
	{
		std::fseek(f, 0, SEEK_SET);
		fileData.resize(std::size_t(size));
		if (size > 0 && std::fread(fileData.data(), 1, fileData.size(), f) != fileData.size())
			ok = false;
	}
	std::fclose(f);
	if (!ok)
	{
		std::cerr << "ReadFile: " << filename << ": " << strerror(errno) << std::endl;
		return false;
	}
	return true;
}

bool WriteFile(std::span<const char> fileData, ByteString filename)
{
	auto replace = FileExists(filename);
	auto writeFileName = filename;
	if (replace)
	{
		while (true)
		{
			writeFileName = ByteString::Build(filename, ".temp.", Format::Width(5), Format::Fill('0'), interfaceRng() % 100000);
			if (!FileExists(writeFileName))
			{
				break;
			}
		}
	}
	bool ok = false;
	{
		FILE *f = OpenFileUTF8(writeFileName, "wb");
		if (f)
		{
			ok = fileData.empty() || std::fwrite(fileData.data(), 1, fileData.size(), f) == fileData.size();
			std::fclose(f);
		}
	}
	if (!ok)
	{
		std::cerr << "WriteFile: " << filename << ": " << strerror(errno) << std::endl;
		if (replace)
		{
			RemoveFile(writeFileName);
		}
		return false;
	}
	if (replace)
	{
		if (!RenameFile(writeFileName, filename, true))
		{
			RemoveFile(writeFileName);
			return false;
		}
	}
	return true;
}
}
