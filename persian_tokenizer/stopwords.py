"""A list of common Persian stop words.

Includes pronouns, prepositions, conjunctions, auxiliaries and other
high-frequency function words (از، به، که، را، این، ...).  The set is
matched after normalization, so entries containing ZWNJ will match
ZWNJ-corrected tokens such as "می‌رود" never appear here because they are
content-bearing; only pure function words are listed.
"""

from __future__ import annotations

from typing import Final, FrozenSet

_STOPWORDS_RAW: Final[tuple[str, ...]] = (
    # pronouns
    "من",
    "تو",
    "او",
    "ما",
    "شما",
    "آنها",
    "ایشان",
    "وی",
    "خود",
    "خودم",
    "خودت",
    "خودش",
    "خودمان",
    "خودتان",
    "خودشان",
    # demonstratives
    "این",
    "آن",
    "همین",
    "همان",
    "چنین",
    "چنان",
    # interrogatives / relatives
    "که",
    "چه",
    "چی",
    "کی",
    "کجا",
    "کدام",
    "چرا",
    "چطور",
    "چگونه",
    # prepositions & particles
    "را",
    "از",
    "به",
    "با",
    "برای",
    "بدون",
    "بی",
    "در",
    "به‌عنوان",
    "مثل",
    "مانند",
    "تا",
    "روی",
    "زیر",
    "بالای",
    "پایین",
    "بیرون",
    "داخل",
    "طی",
    "بر",
    "همانطور",
    "همچنین",
    "بر",
    "علیه",
    "نزد",
    "سوی",
    "جز",
    "مگر",
    "بجز",
    # conjunctions
    "و",
    "یا",
    "هم",
    "نیز",
    "اما",
    "اما",
    "ولی",
    "اگر",
    "اگرچه",
    "پس",
    "چون",
    "زیرا",
    "بنابراین",
    "درحالی",
    "که",
    "تا",
    # verbs: copulas & auxiliaries
    "است",
    "هست",
    "هستند",
    "هستیم",
    "هستی",
    "هستید",
    "بود",
    "بودم",
    "بودی",
    "بود",
    "بودیم",
    "بودید",
    "بودند",
    "باشد",
    "باشند",
    "باشیم",
    "نیست",
    "نیستند",
    "نبود",
    "شد",
    "شدم",
    "شدی",
    "شدیم",
    "شدید",
    "شدند",
    "نشده",
    "شده",
    "می",
    "می‌شود",
    "می‌شود",
    "خواهد",
    "خواهیم",
    "خواهند",
    "خواهی",
    "خواهید",
    "دارد",
    "داریم",
    "دارند",
    "داشته",
    "بایستد",
    "باید",
    "باید",
    "توان",
    "توانند",
    "می‌تواند",
    "بتواند",
    # adverbs / fillers
    "خیلی",
    "زیاد",
    "کم",
    "هنوز",
    "الان",
    "حالا",
    "همیشه",
    "هرگز",
    "هر",
    "همه",
    "همه",
    "بعضی",
    "برخی",
    "چند",
    "چند",
    "دیگر",
    "همچنان",
    "فقط",
    "تنها",
    "باز",
    "دوباره",
    "بعد",
    "قبل",
    "پیش",
    "سپس",
    "سپس",
    "وقتی",
    "آنگاه",
    "آنگاه",
    "گاهی",
    "وقتی",
    "چون",
    "بنابراین",
    "درمورد",
    "درباره",
    "مثل",
    "به‌طور",
    "به‌عنوان",
    # letters / misc
    "بلکه",
    "یعنی",
    "مثلا",
    "البته",
    "گرچه",
    "بی‌آنکه",
    "بدون‌آنکه",
)

#: Normalized stop-word set (ZWNJ inserted where appropriate).
STOPWORDS: Final[FrozenSet[str]] = frozenset(_STOPWORDS_RAW)


def is_stopword(token: str) -> bool:
    """Return True if *token* is a common Persian stop word.

    >>> is_stopword("از")
    True
    >>> is_stopword("کتاب")
    False
    """
    return token in STOPWORDS


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Drop stop words (and punctuation) from a token list.

    >>> remove_stopwords(["من", "کتاب", "را", "خواندم", "."])
    ['کتاب', 'خواندم']
    """
    return [t for t in tokens if not is_stopword(t)]
