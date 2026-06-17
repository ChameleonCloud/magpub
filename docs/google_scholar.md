# Identifying Candidate Publications Using Google Scholar

## Why Google Scholar

Google Scholar is the most permissive of all the sources we use. It indexes
arXiv papers, GitHub-hosted papers, and — critically — PhD and master's
theses. Almost no other aggregator indexes theses, which makes Google Scholar
uniquely valuable for capturing a category of impact that would otherwise be
invisible.

The downside is that Google Scholar cannot be accessed programmatically. There
is no Google-endorsed API, so
practically speaking Google Scholar has to be worked manually.

## Overview of the process

Google Scholar candidate collection has two parts:

1. **Citation tracking** — for each of your project's key publications, find
   papers that cite it.
2. **Keyword search** — search for your project name or related terms to find
   papers that mention the project but may not formally cite it.

Both use Google Scholar's built-in [library][gs-library] feature to keep
track of what has already been processed, so you don't re-process the same
papers on subsequent passes.

[gs-library]: https://scholar.google.com/intl/en/scholar/help.html#library

## Setting up your Google Scholar library

Before you begin, make sure you have a Google account and can access the
library feature — click "My library" at the top of
[scholar.google.com](https://scholar.google.com). The library lets you save
articles and organize them with [labels][gs-library]. Labels function as
named lists and are the primary way to track which papers have already been
processed.

Create the following labels:

- **One label per project publication** you want to track citations for. Name
  each label after the paper (e.g., "Citing: Lessons Learned from the
  Chameleon Testbed"). These labels will hold papers that cite that specific
  publication.
- **One general keyword search label** for papers found via keyword searches
  (e.g., "Keyword: Chameleon Cloud"). This label holds papers that mention
  your project but were not found through citation tracking.

To create and manage labels, click "Manage labels" in the left sidebar of
your library page. See the [Google Scholar library help][gs-library] for
details on saving articles and applying labels.

## Citation tracking

For each of your project's publications:

1. Go to [scholar.google.com](https://scholar.google.com) and search for the
   paper by title.
2. Below the result, click the **"Cited by [N]"** link. This shows all papers
   Google Scholar has found that cite it. (See [Google Scholar search
   help][gs-search] for more on exploring citations.)
   - If there is no "Cited by" link, Google Scholar has no record of
     citations for that paper. This does not mean it hasn't been cited
     elsewhere — other sources may still find citations.
3. Work through the citing papers. For each one, click **"Save"** to add it
   to your library, then apply the label for that publication. Papers already
   in your library will be marked, so you can skip those — the label is how
   you track what has already been processed.
4. Once you have added all new papers, go to your library and select the
   label in the left sidebar to view only those papers. Click **"Export
   All"** at the top of the list and select **"BibTeX"** to download all
   papers in that label at once.

[gs-search]: https://scholar.google.com/intl/en/scholar/help.html#searching
[gs-export]: https://scholar.google.com/intl/en/scholar/help.html#export

## Keyword search

In addition to citation tracking, search for your project by name to catch
papers that mention it without formally citing one of your publications:

1. Search Google Scholar for your project name or relevant terms (e.g.,
   `"Chameleon Cloud" OR "Chameleon Testbed"`).
2. Work through the results the same way — save new papers to your library
   and apply the keyword search label, skipping any already labeled.
3. Export the labeled papers via **"Export All"** → **"BibTeX"** the same way.

## Importing into magpub

Google Scholar candidates need to be converted into the CSV format used by
`magpub` so they can be deduplicated and reviewed alongside results from the
programmatic sources. To do this:

1. Collect the BibTeX entries you exported during citation tracking and
   keyword search.
2. Convert them to a CSV matching the candidate schema (see
   [candidate_template.csv](candidate_template.csv)). Set `source_name` to
   `google_scholar`. The `magpub.utils` module provides helpers for parsing
   BibTeX fields — `get_pub_type`, `get_forum`, `get_link`, and `get_month`
   can extract the relevant columns from a BibTeX entry dictionary.
3. Use the resulting CSV as input to `magpub find-duplicates` or as part of
   your reviewed/rejected lists in `magpub import`.

## Example: publications we track for Chameleon

For Chameleon, we track citations for the following project publications:

- Lessons Learned from the Chameleon Testbed. Keahey K., Anderson J., Zhen Z., Riteau P., Ruth P., Stanzione D., Cevik M., Colleran J., Gunawi H.S., Hammock C., Mambretti J., Barnes A., Halbach F., Rocha A., Stubbs J. In Proceedings of the 2020 USENIX Annual Technical Conference (USENIX ATC '20), July 2020.
- CHI@Edge: Supporting Experimentation in the Edge to Cloud Continuum. Keahey K., Sherman M., Anderson J., Powers M. In Practice and Experience in Advanced Research Computing (PEARC '25), July 2025.
- CHI-in-a-Box: Reducing Operational Costs of Research Testbeds. Keahey K., Anderson J., Sherman M., et al. In Practice and Experience in Advanced Research Computing (PEARC '22), July 2022.
- Chameleon: A Large-Scale, Deeply Reconfigurable Testbed for Computer Science Research. Keahey K., Mambretti J., Ruth P., and Stanzione D. In Proceedings of MERIT 2019 at ICNP 2019, October 2019.
- Operational Lessons from Chameleon. Keahey K., Anderson J., Ruth P., et al. In Proceedings of HARC'19 at PEARC'19, July 2019.
- Chameleon: a Scalable Production Testbed for Computer Science Research. Keahey K., Riteau P., Stanzione D., et al. In Contemporary High Performance Computing, Volume 3. Chapman & Hall/CRC, May 2019.
- Keahey et al. (2021). Chameleon@Edge Community Workshop Report. https://doi.org/10.5281/zenodo.5777344
- Mambretti, Chen, and Yeh. "Next generation clouds, the chameleon cloud testbed, and software defined networking (sdn)." In ICCCRI 2015, IEEE.

Our keyword searches use: `"Chameleon Cloud" OR "Chameleon Testbed"`.

If you are adapting this process for your own project, replace these with your
project's key publications and relevant search terms.
