#include "i18n.h"
#include <json/json.h>
#include <unordered_map>
#include <mutex>
#include "translations_json.h"
#include "glossary_json.h"

namespace
{
	using Dict = std::unordered_map<std::u32string, std::u32string>;

	Dict &TrDict()
	{
		static Dict dict;
		return dict;
	}
	std::once_flag &TrFlag()
	{
		static std::once_flag flag;
		return flag;
	}

	Dict &NameDict()
	{
		static Dict dict;
		return dict;
	}
	Dict &WordDict()
	{
		static Dict dict;
		return dict;
	}
	std::once_flag &GlossFlag()
	{
		static std::once_flag flag;
		return flag;
	}

	String FromBytes(std::string const &bytes)
	{
		return ByteString(bytes.c_str(), bytes.size()).FromUtf8();
	}
	std::u32string ToU32(String const &s)
	{
		return std::u32string(s.data(), s.size());
	}
	String FromU32(std::u32string const &s)
	{
		return String(s.data(), s.size());
	}

	void LoadTr()
	{
		Json::Value root;
		Json::Reader reader;
		auto const translations = translations_json.AsCharSpan();
		if (!reader.parse(translations.data(), translations.data() + translations.size(), root, false) || !root.isObject())
		{
			return;
		}
		auto &dict = TrDict();
		for (auto const &name : root.getMemberNames())
		{
			auto const &value = root[name];
			if (!value.isString())
			{
				continue;
			}
			dict.emplace(ToU32(FromBytes(name)), ToU32(FromBytes(value.asString())));
		}
	}

	void LoadGloss()
	{
		Json::Value root;
		Json::Reader reader;
		auto const gloss = glossary_json.AsCharSpan();
		if (!reader.parse(gloss.data(), gloss.data() + gloss.size(), root, false) || !root.isObject())
		{
			return;
		}
		auto &nm = NameDict();
		auto &wd = WordDict();
		for (auto const &code : root.getMemberNames())
		{
			auto const &obj = root[code];
			if (!obj.isObject())
			{
				continue;
			}
			auto const ck = ToU32(FromBytes(code));
			if (obj["zh"].isString())
			{
				nm.emplace(ck, ToU32(FromBytes(obj["zh"].asString())));
			}
			if (obj["word"].isString())
			{
				wd.emplace(ck, ToU32(FromBytes(obj["word"].asString())));
			}
		}
	}

	bool IsCodeChar(String::value_type c)
	{
		return (c >= U'A' && c <= U'Z') || (c >= U'0' && c <= U'9');
	}

	// Rebuild "PHOTon"-style expansion: code letters (uppercase) in word order,
	// letters that the code omits stay lowercase.
	std::u32string Expansion(std::u32string const &code, std::u32string const &word)
	{
		std::u32string out;
		size_t k = 0;
		for (auto wc : word)
		{
			char32_t up = wc;
			if (wc >= U'a' && wc <= U'z')
			{
				up = wc - (U'a' - U'A');
			}
			if (k < code.size() && up == code[k])
			{
				out.push_back(code[k]);
				++k;
			}
			else
			{
				out.push_back(wc);
			}
		}
		return out;
	}
}

namespace i18n
{
	String Tr(String const &source)
	{
		std::call_once(TrFlag(), LoadTr);
		auto &dict = TrDict();
		auto it = dict.find(source);
		if (it == dict.end())
		{
			return source;
		}
		return it->second;
	}

	String CodeName(String const &code)
	{
		std::call_once(GlossFlag(), LoadGloss);
		auto &nm = NameDict();
		auto ck = ToU32(code);
		auto it = nm.find(ck);
		if (it == nm.end())
		{
			return code;
		}
		std::u32string res = it->second;
		res.push_back(U'（');
		res += ck;
		res.push_back(U'）');
		return FromU32(res);
	}

	String CodeGloss(String const &code)
	{
		std::call_once(GlossFlag(), LoadGloss);
		auto &nm = NameDict();
		auto &wd = WordDict();
		auto ck = ToU32(code);
		auto it = nm.find(ck);
		if (it == nm.end())
		{
			return code;
		}
		std::u32string res = it->second;
		res.push_back(U'（');
		res += ck;
		auto wit = wd.find(ck);
		if (wit != wd.end() && !wit->second.empty())
		{
			res.push_back(U'，');
			res += Expansion(ck, wit->second);
		}
		res.push_back(U'）');
		return FromU32(res);
	}

	// Replace bare element-code tokens in text with their gloss.
	String GlossCodes(String const &text)
	{
		std::call_once(GlossFlag(), LoadGloss);
		auto &nm = NameDict();
		String out;
		out.reserve(text.size() + 16);
		size_t i = 0;
		size_t const n = text.size();
		while (i < n)
		{
			if (IsCodeChar(text[i]))
			{
				size_t j = i;
				while (j < n && IsCodeChar(text[j]))
				{
					++j;
				}
				auto run = text.Substr(i, j - i);
				if (j - i >= 2 && nm.find(ToU32(run)) != nm.end())
				{
					out += CodeGloss(run);
				}
				else
				{
					out += run;
				}
				i = j;
			}
			else
			{
				out += text[i];
				++i;
			}
		}
		return out;
	}
}
