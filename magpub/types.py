"""
Type constants for the publications library.
"""

# Source names
SOURCE_USER_REPORTED = "user_reported"
SOURCE_SCOPUS = "scopus"
SOURCE_SEMANTIC_SCHOLAR = "semantic_scholar"
SOURCE_OPENALEX = "openalex"
SOURCE_SCIENCE_DIRECT = "science_direct"

ALL_SOURCES = [
    SOURCE_USER_REPORTED,
    SOURCE_SCOPUS,
    SOURCE_SEMANTIC_SCHOLAR,
    SOURCE_OPENALEX,
    SOURCE_SCIENCE_DIRECT,
]

# Publication statuses
STATUS_SUBMITTED = "submitted"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_DELETED = "deleted"
STATUS_REFERENCE_ONLY = "reference_only"
STATUS_PRODUCED_BY_CHAMELEON = "produced_by_chameleon"

# Publication type canonical values
PUB_TYPE_PREPRINT = "preprint"
PUB_TYPE_JOURNAL_ARTICLE = "journal article"
PUB_TYPE_CONFERENCE_PAPER = "conference paper"
PUB_TYPE_CONFERENCE_SHORT_PAPER = "conference short paper"
PUB_TYPE_CONFERENCE_POSTER = "conference poster"
PUB_TYPE_CONFERENCE_DEMO = "conference demo"
PUB_TYPE_TECH_REPORT = "tech report"
PUB_TYPE_MS_THESIS = "ms thesis"
PUB_TYPE_PHD_THESIS = "phd thesis"
PUB_TYPE_THESIS = "thesis"
PUB_TYPE_SOFTWARE = "software"
PUB_TYPE_BOOK_CHAPTER = "book chapter"
PUB_TYPE_PATENT = "patent"
PUB_TYPE_POSTER = "poster"
PUB_TYPE_OTHER = "other"
