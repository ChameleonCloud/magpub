"""
Scopus source client for the publications library.

This module is Django-agnostic. Configuration (API keys, etc.) is passed
explicitly via the ScopusClient constructor.
"""

import datetime
import logging
from typing import Iterator

from magpub.models import PublicationData, CitationData
from magpub.types import SOURCE_SCOPUS
from magpub.utils import decode_unicode_text, format_author_name, get_pub_type

logger = logging.getLogger("util.publications.scopus")


class ScopusClient:
    """Client for searching Scopus and retrieving citation counts."""

    def __init__(
        self,
        api_key: str,
        institution_token: str,
    ):
        self.api_key = api_key
        self.institution_token = institution_token
        self._init_pybliometrics()

    def _init_pybliometrics(self):
        try:
            import pybliometrics
            from pybliometrics.scopus import ScopusSearch
            self._pybliometrics = pybliometrics
            self._ScopusSearch = ScopusSearch
            self._AbstractRetrieval = None  # imported lazily
        except ImportError as exc:
            raise ImportError("pybliometrics is required for Scopus support") from exc

        self._pybliometrics.scopus.init(
            keys=[self.api_key],
            inst_tokens=[self.institution_token],
        )

    def search(self, query: str) -> Iterator[PublicationData]:
        """Yield PublicationData for each result matching *query*."""
        search = self._ScopusSearch(query)
        if not search.results:
            return

        for raw_pub in search.results:
            try:
                pub_data = self._raw_to_data(raw_pub)
                pub_data.source_name = SOURCE_SCOPUS
                pub_data.source_id = raw_pub.eid
                yield pub_data
            except Exception as exc:
                logger.error("Error processing Scopus publication %s: %s", getattr(raw_pub, "eid", "?"), exc)
                logger.exception(exc)
                continue

    def _raw_to_data(self, raw) -> PublicationData:
        title = decode_unicode_text(raw.title)
        try:
            published_on = datetime.datetime.strptime(raw.coverDate, "%Y-%m-%d")
        except (ValueError, AttributeError):
            published_on = None
        year = published_on.year if published_on else None
        month = published_on.month if published_on else None

        author_names = decode_unicode_text(raw.author_names) if raw.author_names else ""
        authors = [format_author_name(a) for a in author_names.split(";") if a.strip()]

        doi = raw.doi if raw.doi else ""
        link = f"https://www.doi.org/{doi}" if doi else ""

        return PublicationData(
            title=title,
            author=" and ".join(authors),
            year=year,
            month=month,
            forum=raw.publicationName,
            publication_type=get_pub_type({"ENTRYTYPE": raw.subtypeDescription}),
            doi=doi,
            link=link,
            bibtex_source="{}",
            source_name=SOURCE_SCOPUS,
            source_id=raw.eid,
        )

    def get_citations(self, source_id: str) -> CitationData:
        """Return citation count for the Scopus document identified by *source_id*."""
        if self._AbstractRetrieval is None:
            from pybliometrics.scopus import AbstractRetrieval
            self._AbstractRetrieval = AbstractRetrieval

        ab = self._AbstractRetrieval(source_id)
        return CitationData(
            source_name=SOURCE_SCOPUS,
            source_id=source_id,
            citation_count=ab.citedby_count or 0,
        )
