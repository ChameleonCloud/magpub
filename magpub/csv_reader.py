"""Read PublicationData from CSV."""

import csv
from typing import Iterable, TextIO

from magpub.models import PublicationData


def read_csv(file: TextIO) -> Iterable[PublicationData]:
    """Yield PublicationData rows from an open CSV file."""
    reader = csv.DictReader(file)
    for row in reader:
        try:
            year = int(row["year"]) if row.get("year") else None
        except (ValueError, TypeError):
            year = None
        try:
            month = int(row["month"]) if row.get("month") else None
        except (ValueError, TypeError):
            month = None
        try:
            citation_count = int(row["citation_count"]) if row.get("citation_count") else 0
        except (ValueError, TypeError):
            citation_count = 0

        yield PublicationData(
            title=row.get("title", ""),
            author=row.get("author", ""),
            year=year,
            month=month,
            forum=row.get("forum") or None,
            publication_type=row.get("publication_type", "other"),
            doi=row.get("doi") or None,
            link=row.get("link") or None,
            source_name=row.get("source_name") or None,
            source_id=row.get("source_id") or None,
            citation_count=citation_count,
            extra={"originating_query": row.get("originating_query", "")},
        )
