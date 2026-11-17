"""The :class:`PersianTokenizer` pipeline class.

One object, four knobs:

* ``tokenize``        raw text -> tokens (punctuation kept as tokens)
* ``preprocess``     raw text -> normalized clean text (no tokens)
* ``tokenize_filtered`` tokens without stop words / punctuation
* ``stem_tokens``     tokens with common suffixes removed
"""

from __future__ import annotations

import re
from typing import List, Final

from .tokenizer import normalize, sentence_tokenize, tokenize
from .stopwords import is_stopword
from .stemmer import stem, stem_tokens as _stem_all

_PUNCT_RE: Final[re.Pattern[str]] = re.compile(r"^[!\"#$%&'()*+,\-.:;<=>?@\[\\\]^_`{|}~«»‹›]$")


class PersianTokenizer:
    """High-level facade over the whole normalization + tokenization stack.

    Args:
        remove_stopwords: also drop stop words in :meth:`tokenize`.
        stem_tokens: also stem tokens in :meth:`tokenize`.
        keep_punctuation: keep punctuation marks as separate tokens.

    Example:
        >>> PersianTokenizer().tokenize("می رود به خانه ها .")
        ['می\u200cرود', 'خانه', '.']
    """

    def __init__(
        self,
        remove_stopwords: bool = False,
        stem_tokens: bool = False,
        keep_punctuation: bool = True,
    ) -> None:
        self.remove_stopwords: bool = bool(remove_stopwords)
        self.stem_tokens: bool = bool(stem_tokens)
        self.keep_punctuation: bool = bool(keep_punctuation)

    # -- text level --------------------------------------------------

    def preprocess(self, text: str) -> str:
        """Return the fully normalized text (no tokenization)."""
        return normalize(text)

    def sentences(self, text: str) -> List[str]:
        """Return normalized sentences (kept punctuation included)."""
        return sentence_tokenize(text)

    # -- token level -------------------------------------------------

    def tokenize(self, text: str) -> List[str]:
        """Tokenize *text*; honour the constructor flags.

        Pipeline: normalize -> tokenize -> (drop punctuation?) ->
        (drop stopwords?) -> (stem?).
        """
        tokens: List[str] = tokenize(text)
        if not self.keep_punctuation:
            tokens = [t for t in tokens if not _PUNCT_RE.match(t)]
        if self.remove_stopwords:
            tokens = [t for t in tokens if not is_stopword(t)]
        if self.stem_tokens:
            tokens = [stem(t) for t in tokens]
        return tokens

    def tokenize_filtered(self, text: str) -> List[str]:
        """Convenience: tokens without stop words or punctuation."""
        tokens = [t for t in tokenize(text) if not _PUNCT_RE.match(t)]
        tokens = [t for t in tokens if not is_stopword(t)]
        return tokens

    def stem_all(self, tokens: List[str]) -> List[str]:
        """Stem an existing token list."""
        return _stem_all(tokens)

    def __repr__(self) -> str:  # pragma: no cover
        opts = (
            f"remove_stopwords={self.remove_stopwords}, "
            f"stem_tokens={self.stem_tokens}, "
            f"keep_punctuation={self.keep_punctuation}"
        )
        return f"PersianTokenizer({opts})"
