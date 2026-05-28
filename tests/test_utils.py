"""Tests for util.publications.utils"""
import unittest

from magpub.models import PublicationData
from magpub.utils import (
    decode_unicode_text,
    format_author_name,
    get_forum,
    get_link,
    get_month,
    get_pub_type,
    get_pub_type_from_str,
    how_similar,
    is_pub_similar,
)


class DecodeUnicodeTextTests(unittest.TestCase):
    def test_accent(self):
        self.assertEqual(decode_unicode_text("café"), "cafe")

    def test_german(self):
        self.assertEqual(decode_unicode_text("München"), "Munchen")

    def test_empty(self):
        self.assertEqual(decode_unicode_text(""), "")


class FormatAuthorNameTests(unittest.TestCase):
    def test_standard(self):
        self.assertEqual(format_author_name("Loic, P"), "P Loic")

    def test_single(self):
        self.assertEqual(format_author_name("Einstein"), "Einstein")


class GetMonthTests(unittest.TestCase):
    def test_numeric(self):
        self.assertEqual(get_month({"month": "3"}), 3)

    def test_abbrev(self):
        self.assertEqual(get_month({"month": "Mar"}), 3)

    def test_full(self):
        self.assertEqual(get_month({"month": "March"}), 3)

    def test_missing(self):
        self.assertIsNone(get_month({}))


class GetForumTests(unittest.TestCase):
    def test_journal(self):
        self.assertEqual(get_forum({"journal": "Nature"}), "Nature")

    def test_multiple_fields(self):
        entry = {"journal": "Nature", "booktitle": "Proceedings"}
        self.assertEqual(get_forum(entry), "Nature,Proceedings")

    def test_empty(self):
        self.assertEqual(get_forum({}), "")


class GetLinkTests(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(get_link({"url": "http://example.com"}), "http://example.com")

    def test_from_doi(self):
        self.assertEqual(get_link({"doi": "10.1234/test"}), "https://doi.org/10.1234/test")

    def test_from_note(self):
        self.assertEqual(get_link({"note": r"\url{http://example.com}"}), "http://example.com")

    def test_none(self):
        self.assertIsNone(get_link({}))


class GetPubTypeTests(unittest.TestCase):
    def test_article(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "article"}), "journal article")

    def test_inproceedings(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "inproceedings"}), "conference paper")

    def test_phdthesis(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "phdthesis"}), "phd thesis")

    def test_arxiv(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "misc", "eprint": "arxiv:1234"}), "preprint")

    def test_techreport(self):
        entry = {"ENTRYTYPE": "techreport", "institution": "MIT"}
        self.assertEqual(get_pub_type(entry), "tech report")

    def test_patent(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "misc", "title": "A patent"}), "patent")

    def test_unknown(self):
        self.assertEqual(get_pub_type({"ENTRYTYPE": "something weird"}), "other")


class GetPubTypeFromStrTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(get_pub_type_from_str("journal article"), "journal article")

    def test_heuristic(self):
        self.assertEqual(get_pub_type_from_str("some conference stuff"), "conference paper")

    def test_bibtex_prefix(self):
        self.assertEqual(get_pub_type_from_str("weird", bibtex_source="@article{...}"), "journal article")


class SimilarityTests(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(how_similar("hello world", "hello world"), 1.0)

    def test_same_title_similar(self):
        p1 = PublicationData(title="hello world paper", author="a", year=2020)
        p2 = PublicationData(title="hello world paper", author="b", year=2021)
        self.assertTrue(is_pub_similar(p1, p2))

    def test_different_title_not_similar(self):
        p1 = PublicationData(title="completely different", author="a", year=2020)
        p2 = PublicationData(title="another thing entirely", author="b", year=2020)
        self.assertFalse(is_pub_similar(p1, p2))
