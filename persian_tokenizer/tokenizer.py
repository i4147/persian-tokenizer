"""Half-space (ZWNJ, نیم‌فاصله) insertion and the main tokenizer.

The ZWNJ pass fixes the classic Persian spacing mistake where a space
separates a prefix/suffix from the word it is attached to: "می رود" should
be "می‌رود", "کتاب ها" should be "کتاب‌ها".  Rules implemented here follow
the well-known heuristics used by Hazm and Persian NLP toolkits:

Prefixes that attach with ZWNJ to the following word:
    می, نمی, بی, نی (verb "not"), چون‌, هم‌, ...

Suffixes that attach with ZWNJ to the preceding word:
    ها, های, هایم, هایت, هایش, هایمان, هایتان, هایشان,
    تر, ترین, ی (ezafe marker 'ی' after vowels is written with ZWNJ in
    some styles, e.g. "خانه‌ی"), ام / ات / اش (possessive clitics).

The tokenizer splits on whitespace and punctuation after the text has been
normalized; punctuation marks are kept as separate tokens so information
such as sentence boundaries is not silently lost.
"""

from __future__ import annotations

import re
from typing import Final, List

from .characters import (
    _TOKEN_SPLIT_REGEX,
    collapse_whitespace,
    remove_invisible_junk,
    strip_diacritics,
    strip_kashida,
    translate_digits,
    translate_letters,
    translate_punctuation,
)

ZWNJ: Final[str] = "\u200c"  # zero-width non-joiner

# ---------------------------------------------------------------------------
# ZWNJ affix lists
# ---------------------------------------------------------------------------

# Prefixes: "PREFIX SPACE WORD" -> "PREFIX ZWNJ WORD"
_ZWNJ_PREFIXES: Final[tuple[str, ...]] = (
    "می",  # verbal prefix: می رود -> می‌رود
    "نمی",  # negative prefix: نمی رود -> نمی‌رود
    "بی",  # privative prefix: بی نظیر -> بی‌نظیر
    "نی",  # verb negation: نی آید -> نی‌آید
    "هم",  # co- prefix: هم کار -> هم‌کار
    "چون",  # as- prefix (rare, literary)
    "همه",  # literary variant of هم
    "آن",  # demonstrative in compounds: آن زمان -> آن‌زمان (conservative)
)

# Words that would otherwise be wrongly glued by the "بی" prefix rule
# (they are real standalone words, not prefixes):
_BI_EXCEPTIONS: Final[frozenset[str]] = frozenset({
    "بیرون",
    "بی‌راه",
    "بیش",
    "بیشتر",
    "بیش",
    "بی‌حال",
})

# Suffixes: "WORD SPACE SUFFIX" -> "WORD ZWNJ SUFFIX"
_ZWNJ_SUFFIXES: Final[tuple[str, ...]] = (
    "هایشان",
    "هایمان",
    "هایتان",
    "هایم",
    "هایت",
    "هایش",
    "های",
    "تر",
    "ترین",
    "ها",  # plural: کتاب ها -> کتاب‌ها
    "ام",
    "ات",
    "اش",  # possessive clitics after consonant-ending words
)

# Words that are legitimate tokens on their own and must never be glued:
_PROTECTED_WORDS: Final[frozenset[str]] = frozenset({
    # "ها" and friends as independent words never occur, but common
    # words colliding with prefixes do:
    "می",
    "نی",
    "بی",
    "هم",
    "چون",
    "تر",
    "ترین",
    "اش",
    "ات",
    "ام",
    "آن",
    "همه",
    # frequent standalone words that must survive untouched:
    "است",
    "هست",
    "بود",
    "نیست",
})

# After-vowel possessive clitics are written with ZWNJ: خانه‌ی من، راهِ من
_VOWEL_POSSESSIVE_Y: Final[re.Pattern[str]] = re.compile(r"([اآویء])\s+ی(?=\s|$)")

# ---------------------------------------------------------------------------
# ZWNJ insertion
# ---------------------------------------------------------------------------

# PREFIX pattern at line start or after space, followed by space + word start
_PREFIX_RULE: Final[re.Pattern[str]] = re.compile(
    r"(^|\s)(" + "|".join(sorted(_ZWNJ_PREFIXES, key=len, reverse=True)) + r")\s+(?=[ا-ی])"
)


def fix_zwnj(text: str) -> str:
    """Insert ZWNJ wherever a space acts as a half-space separator.

    >>> fix_zwnj("می رود")
    'می\u200cرود'
    >>> fix_zwnj("کتاب ها")
    'کتاب\u200cها'
    >>> fix_zwnj("نمی خواهم")
    'نمی\u200cخواهم'
    """
    out = text

    # 1. Prefix gluing: "می رود" -> "می‌رود"
    def _prefix_sub(m: re.Match[str]) -> str:
        lead, prefix = m.group(1), m.group(2)
        return f"{lead}{prefix}{ZWNJ}"

    out = _PREFIX_RULE.sub(_prefix_sub, out)

    # 2. Suffix gluing: "کتاب ها" -> "کتاب‌ها"
    for suffix in sorted(_ZWNJ_SUFFIXES, key=len, reverse=True):
        pattern = re.compile(r"(?<=[ا-ی])\s+" + suffix + r"(?=\s|$)")
        out = pattern.sub(ZWNJ + suffix, out)

    # 3. Possessive 'y' after vowels: "خانه ی من" -> "خانه‌ی من"
    out = _VOWEL_POSSESSIVE_Y.sub(r"\1" + ZWNJ + "ی", out)

    return out


# ---------------------------------------------------------------------------
# Normalization pipeline
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Normalize Persian text into a single canonical form.

    Applies, in order: invisible-junk removal, letter unification,
    digit translation, diacritic + kashida removal, punctuation mapping,
    ZWNJ fixing and whitespace collapsing.

    >>> normalize("براي ۱۴۳ مي رود.")
    'برای 143 می\u200cرود.'
    """
    out = remove_invisible_junk(text)
    out = translate_letters(out)
    out = translate_digits(out)
    out = strip_diacritics(out)
    out = strip_kashida(out)
    out = translate_punctuation(out)
    out = fix_zwnj(out)
    out = collapse_whitespace(out)
    return out


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


#: Decimal numbers must survive tokenization intact (3.14 stays one token).
_DECIMAL_GUARD: Final[re.Pattern[str]] = re.compile(r"(?<=[0-9])\.(?=[0-9])")

_DECIMAL_PLACEHOLDER: Final[str] = "\ue000"  # private-use sentinel


def tokenize(text: str) -> List[str]:
    """Tokenize normalized Persian text on whitespace and punctuation.

    Punctuation characters become their own tokens (so '.' remains
    available for sentence splitting); whitespace is dropped. Decimal
    numbers such as 3.14 are kept as single tokens.

    >>> tokenize("سلام، دنیا! چطوری؟")
    ['سلام', ',', 'دنیا', '!', 'چطوری', '?']
    """
    normalized = normalize(text)
    # protect decimal points from being treated as punctuation
    guarded = _DECIMAL_GUARD.sub(_DECIMAL_PLACEHOLDER, normalized)
    # split on whitespace and on punctuation runs (keep punctuation)
    parts = re.split(r"(\s+|" + _TOKEN_SPLIT_REGEX.pattern + r")", guarded)
    tokens: List[str] = []
    for part in parts:
        if part is None or part == "":
            continue
        if part.isspace():
            continue
        if _TOKEN_SPLIT_REGEX.fullmatch(part):
            # punctuation run: split each mark separately
            for ch in part:
                tokens.append(ch)
        else:
            tokens.append(part.replace(_DECIMAL_PLACEHOLDER, "."))
    return tokens


def sentence_tokenize(text: str) -> List[str]:
    """Split normalized text into sentences on . ! ? and newline.

    Decimal numbers (3.14) are protected so a dot between digits never
    ends a sentence.

    >>> sentence_tokenize("سلام. چطوری؟ خوبم.")
    ['سلام.', 'چطوری؟', 'خوبم.']
    """
    normalized = normalize(text)
    guarded = _DECIMAL_GUARD.sub(_DECIMAL_PLACEHOLDER, normalized)
    parts = re.split(r"([.!?])\s+", guarded)
    sentences: List[str] = []
    current = ""
    for part in parts:
        if not part:
            continue
        current += part
        if part in {".", "!", "?"}:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return [s.replace(_DECIMAL_PLACEHOLDER, ".") for s in sentences if s]
