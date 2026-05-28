"""
ScienceDirect source client for the publications library.
"""

import datetime
import logging
from typing import Iterator

from magpub.models import PublicationData
from magpub.types import SOURCE_SCIENCE_DIRECT
from magpub.utils import decode_unicode_text, format_author_name

logger = logging.getLogger("util.publications.science_direct")


class ScienceDirectClient:
    """Client for searching ScienceDirect via pybliometrics."""

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
            from pybliometrics.sciencedirect import ScienceDirectSearch
            self._pybliometrics = pybliometrics
            self._ScienceDirectSearch = ScienceDirectSearch
        except ImportError as exc:
            raise ImportError("pybliometrics is required for ScienceDirect support") from exc

        self._pybliometrics.sciencedirect.init(
            keys=[self.api_key],
            inst_tokens=[self.institution_token],
        )

    def search(self, query: str) -> Iterator[PublicationData]:
        """Yield PublicationData for each result matching *query*."""
        search = self._ScienceDirectSearch(query)
        if not search.results:
            logger.info("No results for Science Direct query: %s", query)
            return

        for raw_pub in search.results:
            try:
                pub_data = self._raw_to_data(raw_pub)
                pub_data.source_name = SOURCE_SCIENCE_DIRECT
                pub_data.source_id = raw_pub.pii
                pub_data.extra["found_with_query"] = query
                yield pub_data
            except Exception as exc:
                logger.error("Error processing ScienceDirect publication %s: %s", getattr(raw_pub, "pii", "?"), exc)
                logger.exception(exc)
                continue

    @staticmethod
    def _raw_to_data(raw) -> PublicationData:
        title = decode_unicode_text(raw.title)
        try:
            published_on = datetime.datetime.strptime(raw.coverDate, "%Y-%m-%d")
        except (ValueError, AttributeError):
            published_on = None
        year = published_on.year if published_on else None
        month = published_on.month if published_on else None

        author_names = decode_unicode_text(raw.authors) if raw.authors else ""
        authors = [format_author_name(a) for a in author_names.split(";") if a.strip()]

        doi = raw.doi if raw.doi else ""
        link = f"https://www.doi.org/{doi}" if doi else ""

        return PublicationData(
            title=title,
            author=" and ".join(authors),
            year=year,
            month=month,
            forum=raw.publicationName,
            publication_type="journal article",  # Science Direct indexes journal articles
            doi=doi,
            link=link,
            bibtex_source="{}",
            source_name=SOURCE_SCIENCE_DIRECT,
            source_id=raw.pii,
        )
