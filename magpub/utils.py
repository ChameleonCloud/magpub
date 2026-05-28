"""
Django-agnostic publication utilities.

Contains BibTeX parsing helpers, text normalization, similarity checks,
and publication type inference.
"""

import datetime
import logging
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, Optional

from magpub.types import (
    PUB_TYPE_BOOK_CHAPTER,
    PUB_TYPE_CONFERENCE_DEMO,
    PUB_TYPE_CONFERENCE_PAPER,
    PUB_TYPE_CONFERENCE_POSTER,
    PUB_TYPE_CONFERENCE_SHORT_PAPER,
    PUB_TYPE_JOURNAL_ARTICLE,
    PUB_TYPE_MS_THESIS,
    PUB_TYPE_OTHER,
    PUB_TYPE_PATENT,
    PUB_TYPE_PHD_THESIS,
    PUB_TYPE_POSTER,
    PUB_TYPE_PREPRINT,
    PUB_TYPE_SOFTWARE,
    PUB_TYPE_TECH_REPORT,
    PUB_TYPE_THESIS,
)

LOG = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.9
PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------

def decode_unicode_text(text: str) -> str:
    """Replace unicode characters with equivalent ASCII characters."""
    if not text:
        return ""
    decoded = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    if text != decoded:
        LOG.debug("Decoding %r to %r", text, decoded)
    return decoded


def format_author_name(author: str) -> str:
    """Convert 'Last, First' into 'First Last'.

    Returns the argument unchanged if it does not contain a comma.
    """
    names = [name.strip() for name in author.split(",")]
    if len(names) > 1:
        return f"{names[1]} {names[0]}"
    return names[0]


# ---------------------------------------------------------------------------
# BibTeX helpers
# ---------------------------------------------------------------------------

def get_month(bibtex_entry: Dict[str, str]) -> Optional[int]:
    """Extract a numeric month from a BibTeX entry dictionary."""
    month = bibtex_entry.get("month")
    if not month:
        return None

    # Try integer directly
    try:
        return int(month)
    except (ValueError, TypeError):
        pass

    # Try abbreviated month name
    for fmt in ("%b", "%B"):
        try:
            return datetime.datetime.strptime(month, fmt).month
        except (ValueError, TypeError):
            pass

    return None


def get_forum(bibtex_entry: Dict[str, str]) -> str:
    """Build a comma-separated forum string from BibTeX fields."""
    keys = ("journal", "booktitle", "series", "publisher", "school", "institution", "address")
    return ",".join(bibtex_entry[k] for k in keys if k in bibtex_entry)


def get_link(bibtex_entry: Dict[str, str]) -> Optional[str]:
    """Extract a URL from a BibTeX entry dictionary."""
    if "url" in bibtex_entry:
        return bibtex_entry["url"]
    if "doi" in bibtex_entry:
        return f"https://doi.org/{bibtex_entry['doi']}"
    for key in ("note", "howpublished"):
        if key in bibtex_entry:
            m = re.search(r"^\\url{(.+?)}$", bibtex_entry[key])
            if m:
                return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Publication type inference
# ---------------------------------------------------------------------------

# Exact string mapping used by ``normalize_pub_types`` and ``get_pub_type``.
_EXACT_TYPE_MAP = {
    "pre-print": PUB_TYPE_PREPRINT,
    "preprint": PUB_TYPE_PREPRINT,
    "journal article": PUB_TYPE_JOURNAL_ARTICLE,
    "research article": PUB_TYPE_JOURNAL_ARTICLE,
    "article": PUB_TYPE_JOURNAL_ARTICLE,
    "conference full paper": PUB_TYPE_CONFERENCE_PAPER,
    "conference short paper": PUB_TYPE_CONFERENCE_SHORT_PAPER,
    "conference poster": PUB_TYPE_CONFERENCE_POSTER,
    "conference demonstration": PUB_TYPE_CONFERENCE_DEMO,
    "conference demo": PUB_TYPE_CONFERENCE_DEMO,
    "conference paper": PUB_TYPE_CONFERENCE_PAPER,
    "conference": PUB_TYPE_CONFERENCE_PAPER,
    "inproceedings": PUB_TYPE_CONFERENCE_PAPER,
    "poster": PUB_TYPE_CONFERENCE_POSTER,
    "tech report": PUB_TYPE_TECH_REPORT,
    "techreport": PUB_TYPE_TECH_REPORT,
    "ms thesis": PUB_TYPE_MS_THESIS,
    "phd thesis": PUB_TYPE_PHD_THESIS,
    "dissertation": PUB_TYPE_PHD_THESIS,
    "thesis": PUB_TYPE_THESIS,
    "github": PUB_TYPE_SOFTWARE,
    "software": PUB_TYPE_SOFTWARE,
    "book chapter": PUB_TYPE_BOOK_CHAPTER,
    "patent": PUB_TYPE_PATENT,
    "misc": PUB_TYPE_OTHER,
    "other": PUB_TYPE_OTHER,
}

_BIBTEX_TYPE_RULES = [
    (("inproceedings", "conference paper", "conference full paper"), PUB_TYPE_CONFERENCE_PAPER),
    (("phdthesis",), PUB_TYPE_PHD_THESIS),
    (("mastersthesis",), PUB_TYPE_MS_THESIS),
    (("thesis",), PUB_TYPE_THESIS),
    (("article", "review", "journal article", "journalarticle"), PUB_TYPE_JOURNAL_ARTICLE),
    (("book", "inbook", "booklet", "incollection"), PUB_TYPE_BOOK_CHAPTER),
    (("techreport", "report"), PUB_TYPE_TECH_REPORT),
    (("software", "code"), PUB_TYPE_SOFTWARE),
    (("dataset", "data"), PUB_TYPE_OTHER),
    (("manual",), PUB_TYPE_OTHER),
    (("patent",), PUB_TYPE_PATENT),
    (("online", "webpage"), PUB_TYPE_OTHER),
    (("unpublished",), PUB_TYPE_OTHER),
    (("misc",), PUB_TYPE_OTHER),
]


def get_pub_type(bibtex_entry: Dict[str, str]) -> str:
    """Infer the canonical publication type from a BibTeX entry dictionary.

    The inference logic is intentionally the same as the original implementation
    so that existing data is not changed.
    """
    entry_type = (bibtex_entry.get("ENTRYTYPE", "") or "").lower()
    entry_type_parts = [p.strip() for p in entry_type.split(",") if p.strip()]

    # Defensive copy so we do not mutate the caller's dict
    text_dict = dict(bibtex_entry)
    text_dict.pop("abstract", None)
    text_as_str = str(text_dict).lower()

    # Keyword-based shortcuts (same precedence as original)
    if "arxiv" in text_as_str:
        return PUB_TYPE_PREPRINT
    if "poster" in text_as_str:
        return PUB_TYPE_POSTER
    if "thesis" in text_as_str:
        if "ms" in text_as_str or "master thesis" in text_as_str:
            return PUB_TYPE_MS_THESIS
        if "phd" in text_as_str:
            return PUB_TYPE_PHD_THESIS
        return PUB_TYPE_THESIS
    if "github" in text_as_str:
        return PUB_TYPE_SOFTWARE
    if "patent" in text_as_str:
        return PUB_TYPE_PATENT

    # Exact entry-type mapping
    for part in entry_type_parts:
        mapped = _EXACT_TYPE_MAP.get(part)
        if mapped:
            return mapped

    # Fallback: keyword-in-text rules
    if "techreport" in text_as_str or "tech report" in text_as_str or "internal report" in text_as_str:
        return PUB_TYPE_TECH_REPORT
    if "proceeding" in text_as_str:
        return PUB_TYPE_CONFERENCE_PAPER

    return PUB_TYPE_OTHER


def get_pub_type_from_str(value: str, bibtex_source: Optional[str] = None) -> str:
    """Normalize a plain-string publication type (e.g. from a UI dropdown).

    Used by management commands that normalise legacy types in the database.
    """
    if not value:
        return PUB_TYPE_OTHER

    val = value.strip().lower()
    if val in _EXACT_TYPE_MAP:
        return _EXACT_TYPE_MAP[val]

    # Fallback heuristic
    if "pre" in val and "print" in val:
        return PUB_TYPE_PREPRINT
    if "conference" in val or "proceed" in val:
        return PUB_TYPE_CONFERENCE_PAPER
    if "poster" in val:
        return PUB_TYPE_CONFERENCE_POSTER
    if "thesis" in val:
        if "phd" in val:
            return PUB_TYPE_PHD_THESIS
        if "ms" in val or "master" in val:
            return PUB_TYPE_MS_THESIS
        return PUB_TYPE_THESIS
    if "journal" in val:
        return PUB_TYPE_JOURNAL_ARTICLE
    if "tech" in val and "report" in val:
        return PUB_TYPE_TECH_REPORT

    # BibTeX source prefix rules
    if bibtex_source:
        src = bibtex_source.strip().lower()
        if src.startswith("@"):
            for prefixes, result_type in _BIBTEX_TYPE_RULES:
                if any(src.startswith("@" + prefix) for prefix in prefixes):
                    return result_type

    return PUB_TYPE_OTHER


# ---------------------------------------------------------------------------
# Similarity helpers
# ---------------------------------------------------------------------------

def how_similar(str1: str, str2: str) -> float:
    """Return difflib.SequenceMatcher ratio between two strings."""
    return SequenceMatcher(None, str1, str2).ratio()


def is_pub_similar(pub1, pub2) -> bool:
    """Return True if two publications are likely duplicates.

    Checks only title similarity (threshold 0.5) because forum can be
    abbreviated and authors can have aliases.
    """
    return how_similar(pub1.title, pub2.title) > PUB_TITLE_DUPLICATE_CHECK_SIMILARITY_THRESHOLD
