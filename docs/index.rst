..  magpub documentation master file

magpub: import and deduplicate academic publications
=====================================================

**magpub** is a Python library for fetching academic publications from
open scholarly databases and detecting duplicates across sources.

It is used by the `Chameleon Cloud Portal`_ to track research outputs
that cite the testbed, but the library itself is Django-agnostic and
can be embedded in any Python project.

.. _Chameleon Cloud Portal: https://github.com/ChameleonCloud/portal

Installation
------------

.. code-block:: bash

   pip install magpub

Optional extras:

.. code-block:: bash

   # Scopus and ScienceDirect support (requires pybliometrics)
   pip install magpub[scopus]

   # Documentation build dependencies
   pip install magpub[docs]

Quick start
-----------

Searching a source
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from magpub.sources.scopus import ScopusClient

   client = ScopusClient(
       api_key="your-api-key",
       institution_token="your-token",
   )
   for pub in client.search('TITLE("Chameleon Cloud")'):
       print(pub.title, pub.doi)

Deduplicating publications
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from magpub.deduplicate import find_matches
   from magpub.models import PublicationData

   existing = [PublicationData(title="Hello", doi="10.1234/a", year=2020)]
   new_pub = PublicationData(title="Hello", doi="10.1234/a", year=2020)

   matches = find_matches(new_pub, existing)
   print(f"Found {len(matches)} duplicate(s).")

Working with BibTeX
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from magpub.utils import get_pub_type, get_forum, get_link, get_month

   entry = {
       "ENTRYTYPE": "article",
       "title": "My Paper",
       "journal": "Nature",
       "year": "2024",
       "month": "Mar",
       "doi": "10.1234/example",
   }

   print(get_pub_type(entry))   # "journal article"
   print(get_forum(entry))      # "Nature"
   print(get_link(entry))       # "https://doi.org/10.1234/example"
   print(get_month(entry))      # 3

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
