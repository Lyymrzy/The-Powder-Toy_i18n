#pragma once
#include "common/String.h"

// Lightweight translation layer: looks up an English source string in the
// embedded dictionary (resources/translations.json -> translations_json)
// and returns the Chinese translation; falls back to the original string.
// Element-code glossary (resources/glossary.json -> glossary_json) provides
// canonical Chinese names for codes and optional word expansions.
namespace i18n
{
	String Tr(String const &source);
	String CodeName(String const &code);   // 中文（CODE）
	String CodeGloss(String const &code);  // 中文（CODE，PHOTon）when a word is known
	String GlossCodes(String const &text); // replace bare code tokens with CodeGloss
}
