"""Tests for persian_tokenizer — run with: python -m pytest tests/ -v
(or: python tests/test_all.py).
"""

import sys
import os
import unittest

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


class TestDigits(unittest.TestCase):
    def test_persian_digits(self):
        self.assertEqual(translate_digits("۱۴۳"), "143")

    def test_arabic_digits(self):
        self.assertEqual(translate_digits("٤٥٦"), "456")

    def test_mixed_digits(self):
        self.assertEqual(translate_digits("۱۲٣٤"), "1234")

    def test_digits_inside_text(self):
        self.assertEqual(normalize("سال ۱۴۰۰"), "سال 1400")

    def test_english_digits_untouched(self):
        self.assertEqual(translate_digits("42"), "42")


class TestLetterUnification(unittest.TestCase):
    def test_arabic_yeh_to_persian(self):
        self.assertEqual(translate_letters("براي"), "برای")

    def test_arabic_kaf_to_persian(self):
        # Arabic Yeh + Arabic Kaf (0x643) must become Persian forms
        self.assertEqual(translate_letters("يكي كد"), "یکی کد")

    def test_alef_with_hamza(self):
        self.assertEqual(translate_letters("أحمد"), "احمد")

    def test_alef_maksura(self):
        self.assertEqual(translate_letters("الى"), "الی")

    def test_heh_variants(self):
        self.assertEqual(translate_letters("ﻩ"), "ه")

    def test_waw_hamza(self):
        self.assertEqual(translate_letters("ؤ"), "و")


class TestDiacritics(unittest.TestCase):
    def test_fatha(self):
        self.assertEqual(strip_diacritics("اَرّه"), "اره")

    def test_kasra_damma(self):
        self.assertEqual(strip_diacritics("مُحَمَّد"), "محمد")

    def test_tanween(self):
        self.assertEqual(strip_diacritics("کتابٌ"), "کتاب")

    def test_full_normalize(self):
        self.assertEqual(normalize("اَرّه"), "اره")

    def test_clean_text_untouched(self):
        self.assertEqual(strip_diacritics("کتاب"), "کتاب")


class TestKashida(unittest.TestCase):
    def test_kashida_removed(self):
        self.assertEqual(strip_kashida("بادبـــــادک"), "بادبادک")

    def test_kashida_in_sentence(self):
        self.assertEqual(normalize("سلامــــ"), "سلام")

    def test_no_kashida(self):
        self.assertEqual(strip_kashida("کتاب"), "کتاب")


class TestPunctuation(unittest.TestCase):
    def test_decimal_slash(self):
        self.assertEqual(normalize("۳/۱۴"), "3.14")

    def test_arabic_comma(self):
        self.assertEqual(translate_punctuation("سلام، دنیا"), "سلام, دنیا")

    def test_arabic_question(self):
        self.assertEqual(translate_punctuation("چطوری؟"), "چطوری?")

    def test_arabic_semicolon(self):
        self.assertEqual(translate_punctuation("خب؛"), "خب;")

    def test_slash_not_between_digits_untouched(self):
        # slash between words is a separator, not a decimal point
        self.assertEqual(normalize("و/یا"), "و/یا")

    def test_date_like_slash(self):
        # ۱۴۰۰/۰۵ -> 1400.05 (library treats digit-digit slash as decimal)
        self.assertEqual(normalize("۱۴۰۰/۰۵"), "1400.05")


class TestZWNJ(unittest.TestCase):
    def test_mi_prefix(self):
        self.assertEqual(fix_zwnj("می رود"), "می" + ZWNJ + "رود")

    def test_nami_prefix(self):
        self.assertEqual(fix_zwnj("نمی رود"), "نمی" + ZWNJ + "رود")

    def test_bi_prefix(self):
        self.assertEqual(fix_zwnj("بی نظیر"), "بی" + ZWNJ + "نظیر")

    def test_plural_ha(self):
        self.assertEqual(fix_zwnj("کتاب ها"), "کتاب" + ZWNJ + "ها")

    def test_plural_ha_mid_sentence(self):
        self.assertEqual(fix_zwnj("کتاب ها را"), "کتاب" + ZWNJ + "ها را")

    def test_hay(self):
        self.assertEqual(fix_zwnj("خانه های"), "خانه" + ZWNJ + "های")

    def test_tar_tarin(self):
        self.assertEqual(fix_zwnj("خوب تر"), "خوب" + ZWNJ + "تر")
        self.assertEqual(fix_zwnj("خوب ترین"), "خوب" + ZWNJ + "ترین")

    def test_no_change_when_fine(self):
        self.assertEqual(fix_zwnj("سلام دنیا"), "سلام دنیا")

    def test_existing_zwnj_preserved(self):
        self.assertEqual(fix_zwnj("می‌رود"), "می" + ZWNJ + "رود")

    def test_sentence_full(self):
        self.assertEqual(
            fix_zwnj("من می خواهم کتاب ها را بخوانم"),
            "من می" + ZWNJ + "خواهم کتاب" + ZWNJ + "ها را بخوانم",
        )


class TestNormalize(unittest.TestCase):
    def test_combined(self):
        self.assertEqual(normalize("براي ۱۴۳ مي رود."), "برای 143 می" + ZWNJ + "رود.")

    def test_double_space_collapsed(self):
        self.assertEqual(normalize("سلام   دنیا"), "سلام دنیا")

    def test_nbsp(self):
        self.assertEqual(normalize("سلام\u00a0دنیا"), "سلام دنیا")

    def test_remove_bidi_controls(self):
        self.assertEqual(normalize("\u202bسلام\u202c"), "سلام")

    def test_strip(self):
        self.assertEqual(normalize("  سلام  "), "سلام")

    def test_tabs_newlines(self):
        self.assertEqual(normalize("سلام\tدنیا\n"), "سلام دنیا")


class TestTokenize(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(tokenize("سلام دنیا"), ["سلام", "دنیا"])

    def test_punct_tokens_kept(self):
        self.assertEqual(
            tokenize("سلام، دنیا! چطوری؟"),
            ["سلام", ",", "دنیا", "!", "چطوری", "?"],
        )

    def test_period_end(self):
        self.assertEqual(tokenize("می رود."), ["می" + ZWNJ + "رود", "."])

    def test_digits(self):
        self.assertEqual(tokenize("عدد ۱۲۳ است"), ["عدد", "123", "است"])

    def test_decimal_number(self):
        self.assertEqual(tokenize("۳/۱۴ متر"), ["3.14", "متر"])

    def test_empty(self):
        self.assertEqual(tokenize(""), [])

    def test_only_punct(self):
        self.assertEqual(tokenize("!!!"), ["!", "!", "!"])


class TestSentenceTokenize(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            sentence_tokenize("سلام. چطوری؟ خوبم."),
            ["سلام.", "چطوری?", "خوبم."],
        )

    def test_single(self):
        self.assertEqual(sentence_tokenize("سلام"), ["سلام"])

    def test_decimal_not_split(self):
        # 3.14 must NOT be read as a sentence boundary
        self.assertEqual(sentence_tokenize("عدد ۳/۱۴ است."), ["عدد 3.14 است."])


class TestStopwords(unittest.TestCase):
    def test_is_stopword(self):
        self.assertTrue(is_stopword("از"))
        self.assertTrue(is_stopword("به"))
        self.assertTrue(is_stopword("که"))
        self.assertFalse(is_stopword("کتاب"))

    def test_remove_stopwords(self):
        out = remove_stopwords(["من", "کتاب", "را", "خواندم"])
        self.assertEqual(out, ["کتاب", "خواندم"])

    def test_empty(self):
        self.assertEqual(remove_stopwords(["از", "به", "و"]), [])


class TestStemmer(unittest.TestCase):
    def test_plural_ha(self):
        self.assertEqual(stem("کتاب" + ZWNJ + "ها"), "کتاب")

    def test_plural_hay(self):
        self.assertEqual(stem("خانه" + ZWNJ + "های"), "خانه")

    def test_superlative(self):
        self.assertEqual(stem("خوب" + ZWNJ + "ترین"), "خوب")

    def test_glued_plural(self):
        self.assertEqual(stem("کتابها"), "کتاب")

    def test_no_stem_short(self):
        self.assertEqual(stem("اب"), "اب")

    def test_protected_word(self):
        self.assertEqual(stem("دانشگاه"), "دانشگاه")

    def test_possessive(self):
        self.assertEqual(stem("خانه" + ZWNJ + "هایم"), "خانه")

    def test_no_change_for_clean(self):
        self.assertEqual(stem("خواندم"), "خواندم")

    def test_stopword_not_stemmed(self):
        self.assertEqual(stem("است"), "است")


class TestPipeline(unittest.TestCase):
    def test_default(self):
        tk = PersianTokenizer()
        self.assertEqual(tk.tokenize("می رود به خانه ها ."), ["می" + ZWNJ + "رود", "به", "خانه" + ZWNJ + "ها", "."])

    def test_filtered(self):
        tk = PersianTokenizer()
        out = tk.tokenize_filtered("من به کتاب ها را خواندم .")
        self.assertEqual(out, ["کتاب" + ZWNJ + "ها", "خواندم"])

    def test_full_stack(self):
        tk = PersianTokenizer(remove_stopwords=True, stem_tokens=True, keep_punctuation=False)
        out = tk.tokenize("من به خانه هایمان می رویم .")
        self.assertEqual(out, ["خانه" + ZWNJ + "مان", "می" + ZWNJ + "رویم"]) if False else None
        # خانه هایمان -> خانه; می رویم -> می‌رویم
        self.assertEqual(out, ["خانه", "می" + ZWNJ + "رویم"])

    def test_preprocess(self):
        tk = PersianTokenizer()
        self.assertEqual(tk.preprocess("براي ۳/۱۴ مي رود"), "برای 3.14 می" + ZWNJ + "رود")

    def test_sentences(self):
        tk = PersianTokenizer()
        self.assertEqual(tk.sentences("سلام. چطوری؟"), ["سلام.", "چطوری?"])

    def test_repr(self):
        r = repr(PersianTokenizer())
        self.assertIn("PersianTokenizer", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
