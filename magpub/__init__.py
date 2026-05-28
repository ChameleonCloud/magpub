"""
Django-agnostic publications library.

This package provides tools for importing and deduplicating academic
publications from external sources (Scopus, Semantic Scholar, OpenAlex,
ScienceDirect). It operates on plain PublicationData dataclasses so that
callers can integrate with any storage backend (Django ORM, SQLAlchemy,
filesystem, etc.).

Usage:
    from magpub.models import PublicationData
    from magpub.sources.scopus import ScopusClient

    client = ScopusClient(api_key="...", institution_token="...")
    for pub in client.search("TITLE(chameleon)"):
        print(pub.title)
"""
