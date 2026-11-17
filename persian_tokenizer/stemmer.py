"""Light Persian stemmer.

Removes common Persian suffixes (ها, های, تر, ترین, ...) from normalized
tokens.  The algorithm is a simplified, Hazm-inspired "affix stripping"
stemmer: it repeatedly peels the longest matching suffix while the stem
stays long enough (>= 3 characters) and is not itself a stop word or an
irregular form.

Design notes:

* Input must already be normalized (letters unified, ZWNJ fixed), so
  suffixes are matched against the canonical form.
* ZWNJ separates the stem from the suffix in properly written text
  ("کتاب‌ها"); a plain space or no separator is also handled so sloppy
  input ("کتابها") still stems.
* Suffix removal never lets a stem drop below MIN_STEM_LEN characters.
"""

from __future__ import annotations

import re
from typing import Final, List

from .stopwords import STOPWORDS

ZWNJ: Final[str] = "\u200c"

#: Shortest stem allowed after suffix stripping.
MIN_STEM_LEN: Final[int] = 3

#: Suffixes ordered longest-first; each is stripped with a preceding ZWNJ,
#: space, or nothing at all.
_SUFFIXES: Final[tuple[str, ...]] = (
    # possessive + plural combos
    "هایشان",
    "هایمان",
    "هایتان",
    "هایم",
    "هایت",
    "هایش",
    "های",
    # superlative / comparative
    "ترین",
    "تر",
    # plural / indefinite / ...
    "ها",
    "ان",
    "ات",
    # ezafe & indefinite 'ی' (kept conservative: only after consonants
    # where removal leaves >= 3 chars)
    "ی",
)

# Words that would be destroyed by stemming (they ARE the suffix shape):
_PROTECTED: Final[frozenset[str]] = frozenset({
    "ها",
    "تر",
    "ترین",
    "های",
    "هایم",
    "هایت",
    "هایش",
    "هایمان",
    "هایتان",
    "هایشان",
    "ان",
    "ات",
    "است",
    "دان",
    "بان",
    "ستان",
    "یاران",
    "جان",
    "ام",
    "ات",
    "اش",
    # words ending in letters that look like suffixes:
    "همی",
    "بدان",
    "زنان",
    "شهران",
    "مردان",
})

_ZWNJ_SUFFIX_RE: Final[re.Pattern[str]] = re.compile(
    r"^(.+?)(?:\s|" + ZWNJ + r")(" + "|".join(sorted(_SUFFIXES, key=len, reverse=True)) + r")$"
)

_DIRECT_SUFFIX_RE: Final[re.Pattern[str]] = re.compile(
    r"^(.+?)(" + "|".join(sorted(_SUFFIXES, key=len, reverse=True)) + r")$"
)


def stem(token: str) -> str:
    """Stem a single normalized Persian token.

    >>> stem("کتاب‌ها")
    'کتاب'
    >>> stem("خانه‌ها")
    'خانه'
    >>> stem("دانشگاه")
    'دانشگاه'
    """
    if len(token) < MIN_STEM_LEN + 2 or token in _PROTECTED or token in STOPWORDS:
        return token

    # 1. try "stem ZWNJ suffix" (canonical spelling)
    m = _ZWNJ_SUFFIX_RE.match(token)
    if m:
        base, suffix = m.group(1), m.group(2)
        if len(base) >= MIN_STEM_LEN:
            return _stem_once(base)

    # 2. try "stemsuffix" glued (sloppy spelling)
    m = _DIRECT_SUFFIX_RE.match(token)
    if m:
        base, suffix = m.group(1), m.group(2)
        if len(base) >= MIN_STEM_LEN and _suffix_glued_ok(base, suffix):
            return _stem_once(base)

    return token


def _stem_once(token: str) -> str:
    """Apply at most a single additional peel to catch double suffixes
    like 'خانه‌هایم' -> 'خانه' (هایم peeled once, then ها)."""
    if token in _PROTECTED or token in STOPWORDS:
        return token
    m = _ZWNJ_SUFFIX_RE.match(token) or _DIRECT_SUFFIX_RE.match(token)
    if m:
        base, suffix = m.group(1), m.group(2)
        if len(base) >= MIN_STEM_LEN and ("\u200c" in token or _suffix_glued_ok(base, suffix)):
            return base
    return token


def _suffix_glued_ok(base: str, suffix: str) -> bool:
    """Guard against eating real word-final letters.

    'ی' and 'ان' glued directly onto a consonant stem often are part of
    the word (دانشگاه), not a suffix; require a vowel/ه end or a known
    plural cue before removing them.
    """
    if suffix == "ی":
        # glued 'ی' almost always belongs to the word: دانشگاه
        return False
    if suffix in {"ان", "ات"}:
        # only strip glued ان/ات from stems already >= 4 chars ending
        # in ه or consonant clusters typical of plurals (باغ‌ان …);
        # be conservative:
        return False
    return True


def stem_tokens(tokens: List[str]) -> List[str]:
    """Stem every token in a list (punctuation passes through untouched).

    >>> stem_tokens(["کتاب‌ها", "خواندم", "."])
    ['کتاب', 'خواندم', '.']
    """
    return [stem(t) for t in tokens]
