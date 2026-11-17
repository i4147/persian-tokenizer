"""Persian tokenizer / normalizer — public API.

Quick start::

    from persian_tokenizer import PersianTokenizer

    tk = PersianTokenizer()
    tk.tokenize("می رود به خانه ها .")  # ['می‌رود', 'به', 'خانه‌ها', '.']
    tk.preprocess("براي ۳/۱۴ متر")  # 'برای 3.14 متر'
"""

from .characters import (
    ARABIC_CHAR_REPLACEMENTS,
    ARABIC_DIGITS,
    DIACRITICS_REGEX,
    ENGLISH_DIGITS,
    KASHIDA_CHAR,
    PERSIAN_DIGITS,
    strip_diacritics,
    strip_kashida,
    translate_digits,
    translate_letters,
    translate_punctuation,
)
from .tokenizer import (
    ZWNJ,
    fix_zwnj,
    normalize,
    sentence_tokenize,
    tokenize,
)
from .stopwords import STOPWORDS, is_stopword, remove_stopwords
from .stemmer import MIN_STEM_LEN, stem, stem_tokens
from ._pipeline import PersianTokenizer

__version__: str = "1.0.0"

__all__ = [
    # facade
    "PersianTokenizer",
    # tokenizer / normalization
    "ZWNJ",
    "normalize",
    "fix_zwnj",
    "tokenize",
    "sentence_tokenize",
    # stemming & stop words
    "stem",
    "stem_tokens",
    "MIN_STEM_LEN",
    "is_stopword",
    "remove_stopwords",
    "STOPWORDS",
    # character-level passes
    "strip_diacritics",
    "strip_kashida",
    "translate_digits",
    "translate_letters",
    "translate_punctuation",
    # data constants
    "ARABIC_CHAR_REPLACEMENTS",
    "DIACRITICS_REGEX",
    "KASHIDA_CHAR",
    "PERSIAN_DIGITS",
    "ARABIC_DIGITS",
    "ENGLISH_DIGITS",
    "__version__",
]
