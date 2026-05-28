"""Source-specific import runners."""

from typing import Iterator

from magpub.config import SourceConfig
from magpub.models import PublicationData
from magpub.sources.openalex import OpenAlexClient
from magpub.sources.science_direct import ScienceDirectClient
from magpub.sources.scopus import ScopusClient
from magpub.sources.semantic_scholar import SemanticScholarClient


def _tag_query(pub: PublicationData, query: str) -> PublicationData:
    pub.extra["originating_query"] = query
    return pub


def run_scopus(cfg: SourceConfig) -> Iterator[PublicationData]:
    client = ScopusClient(
        api_key=cfg.api_key,
        institution_token=cfg.institution_token,
    )
    for query in cfg.queries:
        for pub in client.search(query):
            yield _tag_query(pub, query)


def run_semantic_scholar(cfg: SourceConfig) -> Iterator[PublicationData]:
    client = SemanticScholarClient(api_key=cfg.api_key)
    for query in cfg.queries:
        for pub in client.bulk_search(query):
            yield _tag_query(pub, query)


def run_openalex(cfg: SourceConfig) -> Iterator[PublicationData]:
    client = OpenAlexClient(mailto=cfg.mailto)
    for work_id in cfg.citations_of:
        for pub in client.get_citations(work_id):
            yield _tag_query(pub, f"citations_of:{work_id}")


def run_science_direct(cfg: SourceConfig) -> Iterator[PublicationData]:
    client = ScienceDirectClient(
        api_key=cfg.api_key,
        institution_token=cfg.institution_token,
    )
    for query in cfg.queries:
        for pub in client.search(query):
            yield _tag_query(pub, query)
