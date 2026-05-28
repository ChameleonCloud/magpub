"""Tests for util.publications.deduplicate"""
import unittest

from magpub.deduplicate import find_matches, group_duplicates, is_duplicate
from magpub.models import PublicationData


class FindMatchesTests(unittest.TestCase):
    def test_by_doi(self):
        candidate = PublicationData(title="a", author="x", doi="10.1234/foo")
        existing = [
            PublicationData(title="b", author="y", doi="10.1234/foo"),
            PublicationData(title="c", author="z", doi="10.9999/other"),
        ]
        matches = find_matches(candidate, existing)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].doi, "10.1234/foo")

    def test_by_source_id(self):
        candidate = PublicationData(title="a", author="x", source_id="abc123")
        existing = [
            PublicationData(title="b", author="y", source_id="abc123"),
        ]
        matches = find_matches(candidate, existing)
        self.assertEqual(len(matches), 1)

    def test_by_similar_title(self):
        candidate = PublicationData(title="Hello World Paper", author="x", year=2020)
        existing = [
            PublicationData(title="Hello World Paper", author="y", year=2020),
        ]
        matches = find_matches(candidate, existing)
        self.assertEqual(len(matches), 1)

    def test_no_match(self):
        candidate = PublicationData(title="A", author="x", year=2020)
        existing = [
            PublicationData(title="B", author="y", year=2020),
        ]
        matches = find_matches(candidate, existing)
        self.assertEqual(len(matches), 0)

    def test_doi_prioritised_over_title(self):
        """If DOI matches we should return immediately, even with a dissimilar title."""
        candidate = PublicationData(title="foo", author="x", doi="10.1234/test")
        existing = [
            PublicationData(title="bar", author="y", doi="10.1234/test"),
        ]
        matches = find_matches(candidate, existing)
        self.assertEqual(len(matches), 1)

    def test_disabled_doi(self):
        candidate = PublicationData(title="foo", author="x", doi="10.1234/test")
        existing = [
            PublicationData(title="bar", author="y", doi="10.1234/test"),
        ]
        matches = find_matches(candidate, existing, doi_match=False)
        self.assertEqual(len(matches), 0)


class GroupDuplicatesTests(unittest.TestCase):
    def test_basic(self):
        items = [
            PublicationData(title="Original Paper", author="a", year=2020),
            PublicationData(title="Original Paper", author="b", year=2020),
        ]
        groups = group_duplicates(items)
        self.assertEqual(len(groups), 1)
        duplicate, originals = groups[0]
        self.assertEqual(duplicate.title, "Original Paper")
        self.assertEqual(len(originals), 1)
        self.assertEqual(originals[0].title, "Original Paper")

    def test_none(self):
        items = [
            PublicationData(title="A", author="a", year=2020),
            PublicationData(title="B", author="b", year=2020),
        ]
        groups = group_duplicates(items)
        self.assertEqual(len(groups), 0)

    def test_skips_no_year(self):
        items = [
            PublicationData(title="Has Year", author="a", year=2020),
            PublicationData(title="No Year", author="b", year=None),
        ]
        groups = group_duplicates(items)
        self.assertEqual(len(groups), 0)


class IsDuplicateTests(unittest.TestCase):
    def test_true(self):
        p1 = PublicationData(title="Hello World", author="a", year=2020)
        p2 = PublicationData(title="Hello World", author="b", year=2020)
        self.assertTrue(is_duplicate(p1, p2))

    def test_false(self):
        p1 = PublicationData(title="A", author="a", year=2020)
        p2 = PublicationData(title="B", author="b", year=2020)
        self.assertFalse(is_duplicate(p1, p2))
