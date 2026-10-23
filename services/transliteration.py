import re

# Apostrophe variants commonly used in Uzbek typing:
# ' (U+0027 - Typewriter apostrophe)
# ‘ (U+2018 - Left single quote)
# ’ (U+2019 - Right single quote)
# ʻ (U+02BB - Modifier letter turned comma)
# ʼ (U+02BC - Modifier letter apostrophe)
# ` (U+0060 - Grave accent)
# ´ (U+00B4 - Acute accent)
APOSTROPHE_PATTERN = r"['\u2018\u2019\u02BB\u02BC`\u00B4]"

# Precompiled regex patterns
# Word boundary or case handling:
# O' / o' variants -> Ō / ō
RE_O_UPPER = re.compile(rf"O{APOSTROPHE_PATTERN}")
RE_O_LOWER = re.compile(rf"o{APOSTROPHE_PATTERN}")

# G' / g' variants -> Ğ / ğ
RE_G_UPPER = re.compile(rf"G{APOSTROPHE_PATTERN}")
RE_G_LOWER = re.compile(rf"g{APOSTROPHE_PATTERN}")

# SH / Sh / sh -> Ş / Ş / ş
RE_SH_ALL_CAPS = re.compile(r"SH")
RE_SH_TITLE = re.compile(r"Sh")
RE_SH_LOWER = re.compile(r"sh")

# CH / Ch / ch -> Ç / Ç / ç
RE_CH_ALL_CAPS = re.compile(r"CH")
RE_CH_TITLE = re.compile(r"Ch")
RE_CH_LOWER = re.compile(r"ch")


def transliterate_text(text: str) -> str:
    """
    Transliterates text from the traditional Uzbek Latin alphabet into the newly reformed alphabet.

    Conversions:
    - "CH" -> "Ç", "Ch" -> "Ç", "ch" -> "ç"
    - "SH" -> "Ş", "Sh" -> "Ş", "sh" -> "ş"
    - "O'" / "O‘" -> "Ō", "o'" / "o‘" -> "ō" (and common typographical apostrophes)
    - "G'" / "G‘" -> "Ğ", "g'" / "g‘" -> "ğ" (and common typographical apostrophes)

    Preserves standalone apostrophes (tutuk belgisi - e.g. "a'lo" -> "a'lo", "ma'no" -> "ma'no")
    and apostrophes used as quotation marks.
    """
    if not text:
        return text

    result = text

    # 1. Transliterate Sh variants
    result = RE_SH_ALL_CAPS.sub("Ş", result)
    result = RE_SH_TITLE.sub("Ş", result)
    result = RE_SH_LOWER.sub("ş", result)

    # 2. Transliterate Ch variants
    result = RE_CH_ALL_CAPS.sub("Ç", result)
    result = RE_CH_TITLE.sub("Ç", result)
    result = RE_CH_LOWER.sub("ç", result)

    # 3. Transliterate O' variants
    result = RE_O_UPPER.sub("Ō", result)
    result = RE_O_LOWER.sub("ō", result)

    # 4. Transliterate G' variants
    result = RE_G_UPPER.sub("Ğ", result)
    result = RE_G_LOWER.sub("ğ", result)

    return result
