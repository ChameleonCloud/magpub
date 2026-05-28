"""
Django-agnostic deduplication logic for publications.

Functions operate on PublicationData (or any duck-typed object with
.title, .doi, .source_id, .year attributes).
"""

import logging
from typing import Iterable, List, TypeVar

from magpub.utils import how_similar, PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD

LOG = logging.getLogger(__name__)

T = TypeVar("T")


def find_matches(
    candidate,
    existing: Iterable,
    *,
    similarity_threshold: float = PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD,
    doi_match: bool = True,
    source_id_match: bool = True,
) -> List:
    """Return existing publications that match the candidate.

    Matching order:
      1. Exact DOI match (case-insensitive), if candidate has a DOI.
      2. Exact source_id match, if candidate has a source_id and *source_id_match* is True.
      3. Title similarity above *similarity_threshold*.

    Args:
        candidate: An object with ``title``, ``doi``, ``source_id`` attributes.
        existing: Iterable of objects with the same attributes.
        similarity_threshold: Minimum title similarity ratio (0.0–1.0).
        doi_match: Whether to consider DOI matches.
        source_id_match: Whether to consider source_id matches.

    Returns:
        List of objects from *existing* that are considered duplicates of
        *candidate*.
    """
    existing_list = list(existing)
    matches = []

    if doi_match and candidate.doi:
        for pub in existing_list:
            if pub.doi and pub.doi.lower() == candidate.doi.lower():
                matches.append(pub)
        if matches:
            return matches

    if source_id_match and candidate.source_id:
        for pub in existing_list:
            if pub.source_id and pub.source_id == candidate.source_id:
                matches.append(pub)
        if matches:
            return matches

    for pub in existing_list:
        if how_similar(candidate.title, pub.title) > similarity_threshold:
            matches.append(pub)

    return matches


def group_duplicates(
    publications: Iterable,
    similarity_threshold: float = PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD,
) -> List:
    """Return a list of (duplicate, originals) tuples for likely duplicates.

    The algorithm assumes earlier items in *publications* are the "originals"
    and later items are checked against all earlier items.

    Args:
        publications: Ordered iterable of publication objects.
        similarity_threshold: Minimum title similarity ratio.

    Returns:
        List of (duplicate, list_of_originals) tuples.
    """
    items = list(publications)
    result = []
    for i, pub in enumerate(items):
        if not pub.year:
            LOG.info("%s does not have year – ignoring", pub.title)
            continue
        candidates = items[:i]
        matches = [c for c in candidates if is_duplicate(c, pub, similarity_threshold=similarity_threshold)]
        if matches:
            result.append((pub, matches))
    return result


def is_duplicate(pub1, pub2, similarity_threshold: float = PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD) -> bool:
    """Return True if *pub1* and *pub2* are likely duplicates.

    This is a convenience wrapper around ``find_matches`` for pairwise checks.
    """
    matches = find_matches(pub1, [pub2], similarity_threshold=similarity_threshold)
    return bool(matches)
