"""
Source clients for the publications library.

Each module provides a client class that can be instantiated with explicit
configuration (API keys, etc.) and exposes search/get_citations methods that
operate on PublicationData and CitationData.

Example:
    from magpub.sources.scopus import ScopusClient
    client = ScopusClient(api_key="...", institution_token="...")
    for pub in client.search("TITLE(chameleon)"):
        print(pub.title, pub.doi)
"""
