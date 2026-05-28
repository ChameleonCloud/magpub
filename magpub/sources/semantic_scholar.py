"""
Semantic Scholar source client for the publications library.
"""

import datetime
import logging
import time
from typing import Iterator, List, Optional

import requests

from magpub.models import PublicationData, CitationData
from magpub.types import SOURCE_SEMANTIC_SCHOLAR
from magpub.utils import decode_unicode_text, get_pub_type

logger = logging.getLogger("util.publications.semantic_scholar")

API_BASE = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = [
    "paperId",
    "externalIds",
    "url",
    "title",
    "venue",
    "year",
    "citationCount",
    "fieldsOfStudy",
    "publicationTypes",
    "publicationDate",
    "citationStyles",
    "journal",
    "authors",
    "abstract",
]


class SemanticScholarClient:
    """Client for the Semantic Scholar API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._headers = {}
        if self.api_key:
            self._headers["x-api-key"] = self.api_key

    # ------------------------------------------------------------------
    # Public search / citation methods
    # ------------------------------------------------------------------

    def search_citations(self, paper_id: str) -> Iterator[PublicationData]:
        """Yield PublicationData for all publications citing *paper_id*."""
        url = f"{API_BASE}/paper/{paper_id}/citations"
        for item in self._paginated_get(url, params={}):
            citing = item.get("citingPaper")
            if citing:
                data = self._raw_to_data(citing)
                if data:
                    data.source_name = SOURCE_SEMANTIC_SCHOLAR
                    data.source_id = citing.get("paperId")
                    data.extra["cites_chameleon_pub_id"] = paper_id
                    yield data

    def bulk_search(self, query: str) -> Iterator[PublicationData]:
        """Yield PublicationData from a bulk text search."""
        url = f"{API_BASE}/paper/search/bulk"
        params = {"query": query}
        for item in self._paginated_get(url, params=params):
            data = self._raw_to_data(item)
            if data:
                data.source_name = SOURCE_SEMANTIC_SCHOLAR
                data.source_id = item.get("paperId")
                data.extra["found_with_query"] = query
                yield data

    def search_paper(
        self, query: str, fields: Optional[List[str]] = None, limit: int = 10
    ) -> List[PublicationData]:
        """Return a list of PublicationData matching *query*."""
        if fields is None:
            fields = DEFAULT_FIELDS

        url = f"{API_BASE}/paper/search"
        params = {
            "query": query,
            "fields": ",".join(fields),
            "limit": limit,
        }

        time.sleep(1)
        resp = requests.get(url, params=params, headers=self._headers, timeout=30)
        if resp.status_code != 200:
            logger.warning("Semantic Scholar search failed (%s): %s", resp.status_code, resp.text)
            return []

        return [
            self._raw_to_data(item)
            for item in resp.json().get("data", [])
            if self._raw_to_data(item)
        ]

    def get_citation_count(self, paper_id: str) -> int:
        """Return the current citation count for *paper_id*."""
        url = f"{API_BASE}/paper/{paper_id}"
        for attempt in range(1, 4):
            time.sleep(2)
            resp = requests.get(
                url,
                params={"fields": "citationCount"},
                headers=self._headers,
                timeout=10,
            )
            logger.info("Citation count request for %s: %s", paper_id, resp.status_code)

            if resp.status_code == 200:
                data = resp.json()
                return data.get("citationCount", 0)
            if resp.status_code == 429:
                wait = 5
                logger.warning("Rate limited for %s, waiting %ss (attempt %s/3)", paper_id, wait, attempt)
                time.sleep(wait)
                continue

            time.sleep(2 * attempt)

        logger.error("Giving up getting citation count for %s", paper_id)
        return 0

    def get_citations(self, paper_id: str) -> CitationData:
        """Return CitationData for the given paper ID."""
        count = self.get_citation_count(paper_id)
        return CitationData(
            source_name=SOURCE_SEMANTIC_SCHOLAR,
            source_id=paper_id,
            citation_count=count,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _paginated_get(self, url: str, params: dict, fields: Optional[List[str]] = None, limit: int = 1000):
        """Yield raw response items from a paginated GET."""
        if fields is None:
            fields = DEFAULT_FIELDS

        offset = 0
        while True:
            req_params = params.copy()
            req_params.update({
                "fields": ",".join(fields),
                "offset": offset,
                "limit": limit,
            })

            time.sleep(1)
            resp = requests.get(url, params=req_params, headers=self._headers, timeout=30)

            if resp.status_code != 200:
                logger.warning("Request failed (%s): %s", resp.status_code, resp.text)
                break

            data = resp.json()
            items = data.get("data", [])
            if not items:
                break

            yield from items
            offset += limit

    @staticmethod
    def _raw_to_data(raw: dict) -> Optional[PublicationData]:
        """Map a raw Semantic Scholar result dict → PublicationData."""
        title = decode_unicode_text(raw.get("title", ""))
        pub_date_raw = raw.get("publicationDate")
        if pub_date_raw:
            try:
                published_on = datetime.datetime.strptime(pub_date_raw, "%Y-%m-%d")
                year = published_on.year
                month = published_on.month
            except ValueError:
                year = raw.get("year")
                month = None
        else:
            year = raw.get("year")
            month = None

        if not year:
            return None

        journal = raw.get("journal", {}) or {}
        forum = journal.get("name", "") if journal else raw.get("venue", "")

        external_ids = raw.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        link = f"https://www.doi.org/{doi}" if doi else raw.get("url", "")

        entry_type = ",".join(raw.get("publicationTypes", [])) if raw.get("publicationTypes") else ""
        bibtex = raw.get("citationStyles", {}) or {}

        return PublicationData(
            title=title,
            author=" and ".join(a.get("name", "") for a in raw.get("authors", [])),
            year=year,
            month=month,
            forum=forum,
            publication_type=get_pub_type({"ENTRYTYPE": entry_type, "forum": forum}),
            doi=doi,
            link=link,
            bibtex_source=str(bibtex) if bibtex else "{}",
            source_name=SOURCE_SEMANTIC_SCHOLAR,
            source_id=raw.get("paperId", ""),
        )
