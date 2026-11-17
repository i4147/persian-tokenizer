"""Usage examples for the persian_tokenizer library.

Run with::

    python examples/examples.py

Each block prints its input and the library's output so the behavior of
every feature listed in the README can be seen at a glance.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from persian_tokenizer import (
    PersianTokenizer,
    ZWNJ,
    fix_zwnj,
    is_stopword,
    normalize,
    remove_stopwords,
    sentence_tokenize,
    stem,
    tokenize,
    translate_digits,
    translate_letters,
    translate_punctuation,
    strip_diacritics,
    strip_kashida,
)


def show(title: str, value: object) -> None:
    print(f"{title}\n  {value!r}\n")


# ---------------------------------------------------------------------------
# 1. ZWNJ (نیم‌فاصله) fixing
# ---------------------------------------------------------------------------
show("1a. 'می رود' ->", fix_zwnj("می رود"))
show("1b. 'کتاب ها' ->", fix_zwnj("کتاب ها"))
show("1c. 'نمی خواهم' ->", fix_zwnj("نمی خواهم"))
show("1d. whole sentence:", fix_zwnj("من به خانه هایمان می رویم"))

# ---------------------------------------------------------------------------
# 2. Punctuation conversion
# ---------------------------------------------------------------------------
show("2a. decimal '۳/۱۴' ->", normalize("۳/۱۴"))
show("2b. comma '،' ->", translate_punctuation("سلام، دنیا"))
show("2c. question '؟' ->", translate_punctuation("چطوری؟"))
show("2d. semicolon '؛' ->", translate_punctuation("یک؛ دو"))

# ---------------------------------------------------------------------------
# 3. Tokenization
# ---------------------------------------------------------------------------
show("3a. simple:", tokenize("سلام دنیا"))
show("3b. with punctuation:", tokenize("سلام، دنیا! چطوری؟"))
show("3c. sentences:", sentence_tokenize("سلام. چطوری؟ خوبم."))

# ---------------------------------------------------------------------------
# 4. Full normalization (canonical form)
# ---------------------------------------------------------------------------
show("4a. 'براي ۱۴۳ مي رود.' ->", normalize("براي ۱۴۳ مي رود."))

# ---------------------------------------------------------------------------
# 5. Letter unification (Yeh / Kaf / Heh / Hamza)
# ---------------------------------------------------------------------------
show("5a. 'براي' ->", translate_letters("براي"))
show("5b. Arabic kaf ->", translate_letters("يكي كد"))

# ---------------------------------------------------------------------------
# 6. Digit conversion
# ---------------------------------------------------------------------------
show("6a. '۱۴۳' ->", translate_digits("۱۴۳"))
show("6b. Arabic digits ->", translate_digits("٤٥٦"))
show("6c. inside text:", normalize("سال ۱۴۰۰ بود."))

# ---------------------------------------------------------------------------
# 7. Diacritics (اعراب)
# ---------------------------------------------------------------------------
show("7a. 'اَرّه' ->", strip_diacritics("اَرّه"))
show("7b. 'مُحَمَّد' ->", strip_diacritics("مُحَمَّد"))

# ---------------------------------------------------------------------------
# 8. Kashida
# ---------------------------------------------------------------------------
show("8a. 'بادبـــــادک' ->", strip_kashida("بادبـــــادک"))

# ---------------------------------------------------------------------------
# 9. Stop words
# ---------------------------------------------------------------------------
show("9a. is_stopword('از'):", is_stopword("از"))
show("9b. filter:", remove_stopwords(["من", "کتاب", "را", "خواندم"]))

# ---------------------------------------------------------------------------
# 10. Stemming
# ---------------------------------------------------------------------------
show("10a. 'کتاب‌ها' ->", stem("کتاب" + ZWNJ + "ها"))
show("10b. 'خانه‌های' ->", stem("خانه" + ZWNJ + "های"))
show("10c. 'خوب‌ترین' ->", stem("خوب" + ZWNJ + "ترین"))

# ---------------------------------------------------------------------------
# 11. One-object pipeline
# ---------------------------------------------------------------------------
tk = PersianTokenizer()
show("11a. preprocess:", tk.preprocess("براي ۳/۱۴ مي رود"))
show("11b. tokenize:", tk.tokenize("می رود به خانه ها ."))
show("11c. tokenize_filtered:", tk.tokenize_filtered("من به کتاب ها را خواندم ."))

full = PersianTokenizer(remove_stopwords=True, stem_tokens=True, keep_punctuation=False)
show("11d. full stack:", full.tokenize("من به خانه هایمان می رویم ."))

if __name__ == "__main__":
    print("Done. All examples executed successfully.")
