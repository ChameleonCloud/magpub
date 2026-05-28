"""Write PublicationData to CSV."""

import csv
import sys
from typing import Iterable, Optional, TextIO

from magpub.models import PublicationData


FIELDNAMES = [
    "title",
    "author",
    "year",
    "month",
    "forum",
    "publication_type",
    "doi",
    "link",
    "source_name",
    "source_id",
    "citation_count",
    "originating_query",
]


def write_csv(
    publications: Iterable[PublicationData],
    output: Optional[TextIO] = None,
) -> None:
    """Write publications to CSV."""
    out = output or sys.stdout
    writer = csv.DictWriter(out, fieldnames=FIELDNAMES)
    writer.writeheader()
    for pub in publications:
        row = {
            "title": pub.title,
            "author": pub.author,
            "year": pub.year,
            "month": pub.month,
            "forum": pub.forum,
            "publication_type": pub.publication_type,
            "doi": pub.doi,
            "link": pub.link,
            "source_name": pub.source_name,
            "source_id": pub.source_id,
            "citation_count": pub.citation_count,
            "originating_query": pub.extra.get("originating_query", ""),
        }
        writer.writerow(row)
