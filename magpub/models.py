"""
Django-agnostic publication data models for the publications library.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class PublicationData:
    """Represents a publication from any source.

    This dataclass is the primary interchange format used throughout
    the publications library. Callers using Django models can map
    between this and their ORM objects in an adapter layer.
    """

    title: str = ""
    author: str = ""
    year: Optional[int] = None
    month: Optional[int] = None
    forum: Optional[str] = None
    publication_type: str = "other"
    doi: Optional[str] = None
    link: Optional[str] = None
    bibtex_source: Optional[str] = None
    source_name: Optional[str] = None
    source_id: Optional[str] = None
    citation_count: int = 0
    # Flexible metadata for caller-specific data (e.g. cites_chameleon_pub id)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "month": self.month,
            "forum": self.forum,
            "publication_type": self.publication_type,
            "doi": self.doi,
            "link": self.link,
            "bibtex_source": self.bibtex_source,
            "source_name": self.source_name,
            "source_id": self.source_id,
            "citation_count": self.citation_count,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublicationData":
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            year=data.get("year"),
            month=data.get("month"),
            forum=data.get("forum"),
            publication_type=data.get("publication_type", "other"),
            doi=data.get("doi"),
            link=data.get("link"),
            bibtex_source=data.get("bibtex_source"),
            source_name=data.get("source_name"),
            source_id=data.get("source_id"),
            citation_count=data.get("citation_count", 0),
            extra=data.get("extra", {}),
        )


@dataclass
class CitationData:
    """Represents citation information from a single source."""

    source_name: str = ""
    source_id: str = ""
    citation_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_id": self.source_id,
            "citation_count": self.citation_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CitationData":
        return cls(
            source_name=data.get("source_name", ""),
            source_id=data.get("source_id", ""),
            citation_count=data.get("citation_count", 0),
        )
