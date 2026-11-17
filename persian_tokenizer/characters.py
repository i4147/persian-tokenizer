"""Character-level maps and helpers for Persian text normalization.

This module holds every translation table used across the library:
Arabic/Persian digits, letter unification (Yeh/Kaf/Heh/Hamza and friends),
diacritics, punctuation and Kashida (tatweel).
"""

from __future__ import annotations

import re
from typing import Final, Dict, List

# ---------------------------------------------------------------------------
# Digits
# ---------------------------------------------------------------------------

# Eastern Arabic-Indic digits (used in Persian context) -> ASCII
PERSIAN_DIGITS: Final[str] = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS: Final[str] = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS: Final[str] = "0123456789"

_DIGIT_TABLE: Final[Dict[int, int]] = {}
for _i, _d in enumerate(PERSIAN_DIGITS):
    _DIGIT_TABLE[ord(_d)] = ord(ENGLISH_DIGITS[_i])
for _i, _d in enumerate(ARABIC_DIGITS):
    _DIGIT_TABLE[ord(_d)] = ord(ENGLISH_DIGITS[_i])

# ---------------------------------------------------------------------------
# Letter unification
# ---------------------------------------------------------------------------

# Variant letters -> canonical letter (based on Hazm's character-refinement
# conventions, adapted for this library's needs).
ARABIC_CHAR_REPLACEMENTS: Final[Dict[str, str]] = {
    "ك": "ک",  # Arabic Kaf -> Persian Kaf
    "ڪ": "ک",  # Swash Kaf
    "ﮎ": "ک",
    "ﮏ": "ک",
    "ﮐ": "ک",
    "ﮑ": "ک",
    "ى": "ی",  # Arabic Alef Maksura / dotless Yeh -> Persian Yeh
    "ي": "ی",  # Arabic Yeh -> Persian Yeh
    "ﻯ": "ی",
    "ﻰ": "ی",
    "ﭻ": "چ",  # Chah
    "ﭼ": "چ",
    "ﭽ": "چ",
    "ﭲ": "چ",
    "ﻩ": "ه",  # Arabic Heh variants -> Persian Heh
    "ۀ": "ه",  # Heh with Yeh above (when not treated separately)
    "ﮤ": "ه",
    "ﮥ": "ه",
    "ﮦ": "ه",
    "ﮫ": "ه",
    "ﮬ": "ه",
    "ﮭ": "ه",
    "أ": "ا",  # Alef with Hamza above
    "إ": "ا",  # Alef with Hamza below
    "ٱ": "ا",  # Alef Wasla
    "ﺃ": "ا",
    "ﺇ": "ا",
    "ﺍ": "ا",
    "ﺄ": "ا",
    "ﺉ": "ی",
    "ﺋ": "ی",
    "ﺌ": "ی",
    "ﻱ": "ی",
    "ﻲ": "ی",
    "ﺀ": "ء",  # Hamza standalone (kept)
    "ؤ": "و",  # Waw with Hamza -> Waw
    "ﻭ": "و",
    "ﻮ": "و",
    "ﺏ": "ب",
    "ﺐ": "ب",
    "ﺑ": "ب",
    "ﺒ": "ب",
    "ﭖ": "پ",
    "ﭗ": "پ",
    "ﭘ": "پ",
    "ﭙ": "پ",
    "ﺕ": "ت",
    "ﺖ": "ت",
    "ﺗ": "ت",
    "ﺘ": "ت",
    "ﺙ": "ث",
    "ﺚ": "ث",
    "ﺛ": "ث",
    "ﺜ": "ث",
    "ﺝ": "ج",
    "ﺞ": "ج",
    "ﺟ": "ج",
    "ﺠ": "ج",
    "ﭢ": "گ",
    "ﭣ": "گ",
    "ﭤ": "گ",
    "ﭥ": "گ",
    "ﭦ": "چ",
    "ﭷ": "ژ",
    "ﭸ": "ژ",
    "ﺡ": "ح",
    "ﺤ": "ح",
    "ﺥ": "خ",
    "ﺦ": "خ",
    "ﺧ": "خ",
    "ﺨ": "خ",
    "ﺩ": "د",
    "ﺪ": "د",
    "ﺫ": "ذ",
    "ﺬ": "ذ",
    "ﺭ": "ر",
    "ﺮ": "ر",
    "ﺯ": "ز",
    "ﺰ": "ز",
    "ﮊ": "ژ",
    "ﮋ": "ژ",
    "ﺱ": "س",
    "ﺲ": "س",
    "ﺳ": "س",
    "ﺴ": "س",
    "ﺵ": "ش",
    "ﺶ": "ش",
    "ﺷ": "ش",
    "ﺸ": "ش",
    "ﺹ": "ص",
    "ﺺ": "ص",
    "ﺻ": "ص",
    "ﺼ": "ص",
    "ﺽ": "ض",
    "ﺾ": "ض",
    "ﺿ": "ض",
    "ﻀ": "ض",
    "ﻁ": "ط",
    "ﻂ": "ط",
    "ﻃ": "ط",
    "ﻄ": "ط",
    "ﻅ": "ظ",
    "ﻆ": "ظ",
    "ﻋ": "ع",
    "ﻌ": "ع",
    "ﻍ": "غ",
    "ﻎ": "غ",
    "ﻑ": "ف",
    "ﻒ": "ف",
    "ﻓ": "ف",
    "ﻔ": "ف",
    "ﻕ": "ق",
    "ﻖ": "ق",
    "ﻗ": "ق",
    "ﻘ": "ق",
    "ﮎ": "ک",
    "ﮏ": "ک",
    "ﮐ": "ک",
    "ﮑ": "ک",
    "ﻙ": "ک",
    "ﻚ": "ک",
    "ﻛ": "ک",
    "ﻜ": "ک",
    "ﻝ": "ل",
    "ﻞ": "ل",
    "ﻟ": "ل",
    "ﻠ": "ل",
    "ﻡ": "م",
    "ﻢ": "م",
    "ﻣ": "م",
    "ﻤ": "م",
    "ﻥ": "ن",
    "ﻦ": "ن",
    "ﻧ": "ن",
    "ﻨ": "ن",
    "ﻩ": "ه",
    "ﻪ": "ه",
    "ﻫ": "ه",
    "ﻬ": "ه",
    "ﻭ": "و",
    "ﻮ": "و",
    "ﻱ": "ی",
    "ﻲ": "ی",
    "ﻳ": "ی",
    "ﻴ": "ی",
}

# ---------------------------------------------------------------------------
# Diacritics (اعراب / harakat) and other combining marks
# ---------------------------------------------------------------------------

# Unicode range U+064B..U+065F covers fathatan, dammatan, kasratan, fatha,
# damma, kasra, shadda, sukun, and assorted Arabic marks.
DIACRITICS_REGEX: Final[re.Pattern[str]] = re.compile(
    r"[\u064B-\u065F\u0670\u06D6-\u06ED\u08F0-\u08FF]"  # Arabic block marks
    r"|[\u0640]"  # Kashida / tatweel handled here too (removed)
)

# Kashida alone, for cases where we want to strip only tatweel.
KASHIDA_CHAR: Final[str] = "\u0640"

# ---------------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------------

# Persian/Arabic punctuation -> English/Latin equivalent.
PUNCTUATION_MAPPINGS: Final[Dict[str, str]] = {
    "،": ",",  # Arabic comma
    "؛": ";",  # Arabic semicolon
    "؟": "?",  # Arabic question mark
    "٬": ",",  # Arabic thousands separator
    "٭": "*",  # Arabic five-pointed star
}

# NOTE: ZWNJ (\u200C) is NOT punctuation; it is the half-space and must be
# preserved/produced by the ZWNJ pass, never removed here.

# Persian decimal separator: slash "/" between digits means decimal point,
# e.g. ۳/۱۴ -> 3.14.  Handled in the tokenizer pass because it requires
# digit context.
DECIMAL_SLASH_REGEX: Final[re.Pattern[str]] = re.compile(r"(?<=[0-9۰-۹])/(?=[0-9۰-۹])")

# ---------------------------------------------------------------------------
# Whitespace / control characters
# ---------------------------------------------------------------------------

# Zero-width characters that carry no meaning (except ZWNJ) + exotic spaces.
_INVISIBLE_JUNK: Final[str] = "\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff\u00ad"

_WHITESPACE_VARIANTS: Final[List[str]] = [
    "\u00a0",  # NBSP
    "\u2000",  # EN QUAD
    "\u2001",  # EM QUAD
    "\u2002",  # EN SPACE
    "\u2003",  # EM SPACE
    "\u2004",  # THREE-PER-EM SPACE
    "\u2005",  # FOUR-PER-EM SPACE
    "\u2006",  # SIX-PER-EM SPACE
    "\u2007",  # FIGURE SPACE
    "\u2008",  # PUNCTUATION SPACE
    "\u2009",  # THIN SPACE
    "\u200a",  # HAIR SPACE
    "\u202f",  # NARROW NBSP
    "\u205f",  # MEDIUM MATH SPACE
    "\u3000",  # IDEOGRAPHIC SPACE
    "\t",
    "\r",
    "\n",
    "\f",
    "\v",
]

# ---------------------------------------------------------------------------
# Precompiled helpers
# ---------------------------------------------------------------------------

_DIGIT_TRANSLATION: Final[Dict[int, int]] = dict(_DIGIT_TABLE)

_LETTER_TRANSLATION: Final[Dict[int, str]] = {ord(k): v for k, v in ARABIC_CHAR_REPLACEMENTS.items()}

# Everything that counts as a token separator when tokenizing on
# whitespace + punctuation.
PUNCT_TOKEN_SPLIT: Final[str] = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~«»،؛؟…ـ"

# Arabic punctuation that survives mapping is converted first, then this
# class is used to split tokens.
_TOKEN_SPLIT_REGEX: Final[re.Pattern[str]] = re.compile(r"[!\"#$%&'()*+,\-.:;<=>?@\[\\\]^_`{|}~«»‹›]")


def translate_digits(text: str) -> str:
    """Convert Persian/Arabic digits to English digits.

    >>> translate_digits("۱۴۳")
    '143'
    >>> translate_digits("٤٥")
    '45'
    """
    return text.translate(_DIGIT_TRANSLATION)


def translate_letters(text: str) -> str:
    """Unify Arabic variants of Yeh/Kaf/Heh/Hamza (and friends) to Persian.

    >>> translate_letters("براي")
    'برای'
    """
    return text.translate(_LETTER_TRANSLATION)


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics (اعراب) and Kashida from text.

    >>> strip_diacritics("اَرّه")
    'اره'
    >>> strip_diacritics("بادبـــــادک")
    'بادبادک'
    """
    return DIACRITICS_REGEX.sub("", text)


def strip_kashida(text: str) -> str:
    """Remove Kashida (tatweel) characters only.

    >>> strip_kashida("بادبـــــادک")
    'بادبادک'
    """
    return text.replace(KASHIDA_CHAR, "")


def translate_punctuation(text: str) -> str:
    """Convert Persian punctuation to its English equivalent.

    Commas, semicolons, question marks and star are remapped; the Persian
    decimal slash (۳/۱۴) is turned into a dot *only between digits*.

    >>> translate_punctuation("سلام، حال شما؟")
    'سلام, حال شما?'
    """
    out = text
    for src, dst in PUNCTUATION_MAPPINGS.items():
        out = out.replace(src, dst)
    out = DECIMAL_SLASH_REGEX.sub(".", out)
    return out


def collapse_whitespace(text: str) -> str:
    """Turn every exotic whitespace char into a plain space and collapse runs."""
    out = text
    for ws in _WHITESPACE_VARIANTS:
        out = out.replace(ws, " ")
    # collapse repeated spaces
    out = re.sub(r" {2,}", " ", out)
    return out.strip()


def remove_invisible_junk(text: str) -> str:
    """Strip BOM, bidi controls, soft hyphens and zero-width spaces (not ZWNJ)."""
    return re.sub(r"[\u200B\u200E\u200F\u202A-\u202E\u2066-\u2069\uFEFF\u00AD]", "", text)
