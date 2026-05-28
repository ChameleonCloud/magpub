"""
OpenAlex source client for the publications library.
"""

import datetime
import logging
import time
from typing import Iterator, Optional

import requests

from magpub.models import PublicationData, CitationData
from magpub.types import SOURCE_OPENALEX
from magpub.utils import decode_unicode_text, get_pub_type

logger = logging.getLogger("util.publications.openalex")

DEFAULT_BASE = "https://api.openalex.org/works"
DEFAULT_PER_PAGE = 200


class OpenAlexClient:
    """Client for the OpenAlex API."""

    def __init__(self, mailto: str = "contact@chameleoncloud.org", base_url: Optional[str] = None):
        self.mailto = mailto
        self.base_url = base_url or DEFAULT_BASE
        self.per_page = DEFAULT_PER_PAGE

    def get_citations(self, work_id: str) -> Iterator[PublicationData]:
        """Yield PublicationData for all works citing *work_id*."""
        page = 1
        while True:
            params = {
                "filter": f"cites:{work_id}",
                "sort": "cited_by_count:desc",
                "page": page,
                "per_page": self.per_page,
                "mailto": self.mailto,
            }
            resp = requests.get(self.base_url, params=params, timeout=30)

            if resp.status_code != 200:
                logger.warning("OpenAlex request failed (%s): %s", resp.status_code, resp.text)
                break

            data = resp.json()
            results = data.get("results", [])
            if not results:
                break

            for work in results:
                normalized = self._normalize_work(work)
                pub = self._build_data(normalized)
                if pub:
                    pub.source_name = SOURCE_OPENALEX
                    pub.source_id = work.get("id", "")
                    pub.extra["cites_chameleon_work_id"] = work_id
                    yield pub

            meta = data.get("meta", {})
            total_pages = meta.get("page_count")
            if total_pages and page >= total_pages:
                break

            page += 1
            time.sleep(0.5)

    @staticmethod
    def _normalize_work(work: dict) -> dict:
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append({"name": author["display_name"]})

        doi = ""
        if work.get("doi"):
            doi = work["doi"].replace("https://doi.org/", "")

        venue = work.get("host_venue", {}) or {}

        return {
            "title": work.get("title"),
            "publicationDate": work.get("publication_date"),
            "year": work.get("publication_year"),
            "venue": venue.get("display_name", ""),
            "journal": {"name": venue.get("display_name")} if venue else {},
            "externalIds": {"DOI": doi} if doi else {},
            "url": work.get("id"),
            "authors": authors,
            "publicationTypes": [work.get("type")] if work.get("type") else [],
        }

    @staticmethod
    def _build_data(normalized: dict) -> Optional[PublicationData]:
        title = decode_unicode_text(normalized.get("title", ""))

        pub_date_raw = normalized.get("publicationDate")
        if pub_date_raw:
            try:
                published_on = datetime.datetime.strptime(pub_date_raw, "%Y-%m-%d")
                year = published_on.year
                month = published_on.month
            except ValueError:
                year = normalized.get("year")
                month = None
        else:
            year = normalized.get("year")
            month = None

        if not year:
            return None

        journal = normalized.get("primary_location", {})
        forum = journal.get("raw_source_name", "")

        external_ids = normalized.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        entry_type = ",".join(normalized.get("publicationTypes", []))
        link = f"https://www.doi.org/{doi}" if doi else normalized.get("url", "")

        return PublicationData(
            title=title,
            author=" and ".join(a["name"] for a in normalized.get("authors", [])),
            year=year,
            month=month,
            forum=forum,
            publication_type=get_pub_type({"ENTRYTYPE": entry_type, "forum": forum}),
            doi=doi,
            link=link,
            bibtex_source="{}",
            source_name=SOURCE_OPENALEX,
            source_id=normalized.get("url", ""),
        )
