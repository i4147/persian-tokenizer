# persian_tokenizer

A pure-Python (stdlib only, zero dependencies) library for tokenizing,
normalizing and stemming Persian (Farsi) text. Fully type-annotated,
tested (69 unit tests), Python ≥ 3.9.

## Features

| # | Feature | Example (input → output) |
|---|---------|---------------------------|
| 1 | Fix half-space (ZWNJ / نیم‌فاصله) | `می رود` → `می‌رود` |
| 2 | Persian punctuation → English | `۳/۱۴` → `3.14`، `،` → `,`، `؟` → `?`، `؛` → `;` |
| 3 | Tokenize on whitespace + punctuation | `سلام، دنیا!` → `['سلام', ',', 'دنیا', '!']` |
| 4 | Normalize into one canonical form | `براي ۱۴۳ مي رود.` → `برای 143 می‌رود.` |
| 5 | Unify Yeh/Kaf/Heh/Hamza variants | `براي` → `برای`، `يكي` → `یکی` |
| 6 | Persian & Arabic digits → English | `۱۴۳` → `143`، `٤٥٦` → `456` |
| 7 | Remove diacritics (اِعراب) | `اَرّه` → `اره` |
| 8 | Remove Kashida (ـ) | `بادبـــــادک` → `بادبادک` |
| 9 | Remove stop words | `من کتاب را خواندم` → `کتاب خواندم` |
| 10 | Stem (strip suffixes) | `کتاب‌ها` → `کتاب`، `خانه‌های` → `خانه` |

Decimal numbers are protected: `3.14` survives tokenization as one token
and never triggers a false sentence boundary.

## Install

No build step — copy the `persian_tokenizer/` folder next to your code, or
pip-install from the project root:

```bash
pip install .
```

(`pyproject.toml` included.)

## Quick start

```python
from persian_tokenizer import PersianTokenizer

tk = PersianTokenizer()

tk.preprocess("براي ۳/۱۴ مي رود.")
# -> 'برای 3.14 می‌رود.'

tk.tokenize("می رود به خانه ها .")
# -> ['می‌رود', 'به', 'خانه‌ها', '.']

tk.tokenize_filtered("من به کتاب ها را خواندم .")
# -> ['کتاب‌ها', 'خواندم']

full = PersianTokenizer(remove_stopwords=True, stem_tokens=True, keep_punctuation=False)
full.tokenize("من به خانه هایمان می رویم .")
# -> ['خانه', 'می‌رویم']
```

### Function API

Every step is also usable standalone:

```python
from persian_tokenizer import (
    fix_zwnj,
    normalize,
    tokenize,
    sentence_tokenize,
    stem,
    translate_digits,
    translate_letters,
    translate_punctuation,
    strip_diacritics,
    strip_kashida,
    is_stopword,
    remove_stopwords,
    STOPWORDS,
)

fix_zwnj("می رود")  # 'می‌رود'
normalize("براي ۱۴۳")  # 'برای 143'
tokenize("سلام، دنیا!")  # ['سلام', ',', 'دنیا', '!']
sentence_tokenize("سلام. چطوری؟")  # ['سلام.', 'چطوری?']
stem("کتاب‌ها")  # 'کتاب'
translate_digits("۱۴۳")  # '143'
translate_letters("براي")  # 'برای'
strip_diacritics("اَرّه")  # 'اره'
strip_kashida("بادبـــــادک")  # 'بادبادک'
is_stopword("از")  # True
remove_stopwords(["من", "کتاب", "را"])  # ['کتاب']
```

## ZWNJ rules (نیم‌فاصله)

The half-space fixer re-attaches detached affixes:

- **Prefixes** glued with ZWNJ: `می`، `نمی`، `بی`، `نی`، `هم`، `چون`
  (`می رود` → `می‌رود`، `بی نظیر` → `بی‌نظیر`).
- **Suffixes** glued with ZWNJ: `ها`، `های`، `هایم/هایت/هایش/هایمان/هایتان/هایشان`،
  `تر`، `ترین` (`کتاب ها` → `کتاب‌ها`).
- Possessive `ی` after vowels: `خانه ی من` → `خانه‌ی من`.
- Text already written with ZWNJ is left untouched.

## Stemmer rules

Strips common suffixes from normalized tokens, longest-suffix-first,
keeping a minimum stem length of 3 and protecting words that *are* the
suffix (`ترین` stays `ترین`) or that merely look like they carry one
(`دانشگاه` stays `دانشگاه`). Supports both canonical (`کتاب‌ها`) and
glued (`کتابها`) spellings, and peels stacked suffixes
(`خانه‌هایم` → `خانه`).

Suffixes: `هایشان، هایمان، هایتان، هایم، هایت، هایش، های، ترین، تر، ها، ان، ات`.

## Running the tests

```bash
python tests/test_all.py          # unittest runner
# or
python -m pytest tests/ -v        # if pytest is installed
```

69 tests cover digits, letter unification, diacritics, kashida,
punctuation (incl. decimal-slash), ZWNJ insertion, normalization,
tokenization, sentence splitting, stop words, stemming and the
`PersianTokenizer` facade.

## Usage examples

`examples/examples.py` demonstrates every feature with printed
before/after output:

```bash
python examples/examples.py
```

## API at a glance

### `PersianTokenizer(remove_stopwords=False, stem_tokens=False, keep_punctuation=True)`

| Method | Returns |
|--------|---------|
| `preprocess(text)` | normalized `str` |
| `tokenize(text)` | `list[str]` (flags applied) |
| `tokenize_filtered(text)` | `list[str]` (no stop words, no punctuation) |
| `sentences(text)` | `list[str]` |
| `stem_all(tokens)` | stemmed `list[str]` |

### Module functions

`fix_zwnj`, `normalize`, `tokenize`, `sentence_tokenize`, `stem`,
`stem_tokens`, `is_stopword`, `remove_stopwords`, `translate_digits`,
`translate_letters`, `translate_punctuation`, `strip_diacritics`,
`strip_kashida`, plus the data constants (`STOPWORDS`,
`ARABIC_CHAR_REPLACEMENTS`, …).

## Design notes

- **Deterministic order**: invisible junk → letters → digits → diacritics →
  kashida → punctuation → ZWNJ → whitespace. Each pass assumes the
  previous one has run.
- **`؟` → `?`**: punctuation conversion is by design, so `sentence_tokenize`
  outputs English marks. Keep the raw text if you need the original marks.
- **Glued suffixes are conservative**: `ی`/`ان` attached directly (no ZWNJ)
  are usually part of the word (`دانشگاه`), so they are only stripped
  after an explicit ZWNJ.
- **Type-annotated end-to-end** (`Final`, `Dict[str, str]`, `List[str]`,
  `frozenset`, …) and mypy-friendly.

## License

MIT — see `LICENSE`.
