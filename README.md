# magpub

This repository describes the end-to-end workflow for collecting, deduplicating,
and reviewing publications that cite or use a research project's resources, and
provides a tool — `magpub` — that automates several steps of that workflow. The
workflow was developed for [Chameleon Cloud][portal] but is intended as a
reusable model for any testbed or research infrastructure project that needs to
track its publication impact.

A detailed description of this methodology and its application to Chameleon
is published in:

> Kate Keahey, Paul Marshall, Mark Powers, Marc Richardson, and Michael
> Sherman. 2026. Practical Evaluation Methods for Scientific Instruments.
> In *Practice and Experience in Advanced Research Computing (PEARC '26)*,
> July 26–30, 2026, Minneapolis, MN, USA. ACM, New York, NY, USA, 12 pages.
> https://doi.org/10.1145/3785462.3815804

Below we first describe the general process for collecting and reviewing
publications. Detailed instructions for using `magpub` follow in the
[Usage guide](#usage-guide).

The process has three main stages, each producing a spreadsheet (CSV) that
feeds the next.

### 1. Generate candidate publication lists

Candidates come from two kinds of sources:

**Programmatic sources** — We use OpenAlex, Scopus, Semantic Scholar, and
ScienceDirect, which can be queried automatically with `magpub import`. Each source
has different coverage, so you will want to review which are best for your given domain. Configure which sources to use via `magpub init`; see the
[Usage guide](#usage-guide) below for details.

**Google Scholar** — the most permissive source. It indexes arXiv papers,
GitHub-hosted papers, and — critically — PhD and master's theses that almost
no other aggregator covers. However, Google Scholar cannot be accessed
programmatically, so it requires a separate [manual process](docs/google_scholar.md).

Each source produces a candidate list as a CSV. See
[docs/candidate_template.csv](docs/candidate_template.csv) for the suggested column
schema.

### 2. Deduplicate candidates

Deduplication happens at two levels.

**Automated deduplication** — `magpub import` and `magpub find-duplicates`
flag candidates that match previously reviewed or rejected publications using
three criteria applied in order:

1. **Exact DOI match** (case-insensitive)
2. **Exact source_id match**
3. **Title similarity ≥ 0.5** (using `difflib.SequenceMatcher`)

If any criterion matches, the candidate is flagged as a likely duplicate.

**Manual deduplication review** — Flagged candidates are reviewed by comparing
their metadata against the existing publication they matched. The key fields
we compare are title, authors, venue, and publication year. Generally, if
these fields all match (or nearly match), the candidate is confirmed as a
duplicate and merged with the existing publication record. Source information is retained — a single publication
can have records from multiple sources, which is useful for analyzing
source coverage.

In particularly ambiguous cases, the reviewer may compare the actual content
of the publications to determine whether the work is substantially different.

Most automated flags are real duplicates — the same paper appearing in a new
source or re-imported from a source already processed. However, there are
edge cases where the metadata overlap is misleading and a different policy
applies:

- **Preprint → published paper.** A paper first posted on arXiv and later
  published at a conference or journal is treated as *one publication*, not
  two. The earlier record is merged into the later one, and metadata is
  updated to reflect the published version (venue, DOI, publication type).
  The reasoning: this is an evolution of the same work, not a new publication.

- **Near-duplicates with slight title variations.** Different sources
  sometimes report the same paper with minor title differences (punctuation,
  subtitles). The automated title similarity check catches most of these,
  but borderline cases require manual comparison of the other metadata fields
  to confirm.

- **Same title and authors, different venues.** On rare occasion, two
  publications will share the same title and authors but have different
  venues and DOIs. These are treated as *separate publications*, not
  duplicates — they were published in different venues, vetted by different
  committees, and represent distinct publication events. This is different
  from the preprint→published case (where the venue upgrade replaces the
  earlier record) and from the multi-source case (where the same publication
  appears in multiple databases).

The output of this stage is a deduplicated candidate list — publications that
have not been previously reviewed or rejected and are not duplicates of each
other. This list is what goes into human review.

### 3. Human review

The deduplicated candidate list is reviewed by a human to determine which
publications should be approved. No publication is approved automatically.
Review covers three things:

**Metadata verification** — Check that the title, authors, venue, publication
type, and other fields are correct. Automated imports often produce inaccurate
metadata, especially for publication type. The reviewer corrects these based
on the actual publication.

**Usage verification** — Confirm that the publication actually used the
project's resources. For Chameleon, "using Chameleon" is interpreted broadly:
it includes work where Chameleon helped achieve results even if final
experiments ran on another platform. The spirit of the test is *"did access
to these resources contribute to this research?"* rather than requiring that
every reported result was produced directly using the resource.

Verification falls into three tiers:

1. **Citation** — The paper explicitly cites the project in the context of
   using its resources. Most common and most straightforward.
2. **Acknowledgement** — The paper does not formally cite the project but
   mentions or acknowledges using it, e.g. in the acknowledgements section
   or in the experimental setup ("we used two H100 nodes at Chameleon Cloud
   for these evaluations").
3. **User attestation** — The paper contains no mention of the project, but
   the author has confirmed usage through another channel: a portal
   submission with an explicit confirmation checkbox, an allocation renewal
   request describing work done with the resources, or direct email
   correspondence.

**Categorization** — Each reviewed publication is assigned to one of these
categories:

| Category | Description |
|----------|-------------|
| **Approved** | Used the project's resources; appears on the public publications list |
| **Rejected** | Does not meet inclusion criteria |
| **References only** | Cites or mentions the project but did not use its resources |
| **Produced by project team** | Written by project staff or in collaboration; held out from the community impact count |

#### Publication types

Publication type is assigned during review by examining the publication
itself — the venue it appeared in, how the venue categorizes it, and the
content of the work. For example, a paper in a conference proceedings is a
conference paper; a paper in a peer-reviewed journal is a journal article; a
dissertation submitted to a university is a thesis. The source databases
often misclassify or omit publication type, so the reviewer determines the
correct type rather than trusting the imported metadata.

The main categories we use are:

- **Conference paper** — includes workshop papers and short papers
- **Journal article**
- **Thesis/dissertation** — PhD and MS theses
- **Self-published** — publications with no formal publication venue. Typically these are papers found on open-access aggregators like arXiv, as well as white papers produced by organizations and technical reports
- **Other** — patents, presentations, software, books, posters, etc.

---

**magpub** is a Python library and CLI for collecting academic publications from
open scholarly databases and detecting duplicates across sources. It is used by
the [Chameleon Cloud Portal][portal] to track research outputs, but the library
can be used in any project, or standalone via the CLI.

Magpies are birds known for collecting shiny things, which is the inspiration behind the name.

[portal]: https://github.com/ChameleonCloud/portal

## Quick start

```bash
pip install magpub
magpub init
magpub import -o results.csv
```

---

## Usage guide

### 1. Install magpub

```bash
pip install magpub
```

Optional extras for source clients that need additional dependencies:

```bash
pip install magpub[scopus]      # Scopus / ScienceDirect via pybliometrics
```

### 2. Configure sources with `magpub init`

Run the interactive wizard once to create a config file:

```bash
$ magpub init
magpub init — create a configuration file

Config path [~/.config/magpub/config.toml]:
Sources to configure [scopus, semantic_scholar, openalex, science_direct]: openalex

Source: openalex
  mailto address: contact@example.com
  citations_of IDs (blank line to finish):
  > W4297744025
  >

Config written to ~/.config/magpub/config.toml
```

The config file is a plain TOML file. You can also edit it by hand:

```toml
[openalex]
mailto = "contact@example.com"
citations_of = ["W4297744025", "W0987654321"]

[scopus]
api_key = "..."
institution_token = "..."
queries = ['TITLE("Chameleon Cloud")']

[semantic_scholar]
api_key = "..."
queries = ["chameleon cloud testbed"]
```

### 3. First import: get everything

The first time you run `magpub`, you will want to import everything into a single CSV file.

```bash
magpub import -o results-2024-01.csv
```

This runs every source configured in the config file and writes all results to
a CSV with these columns:

```
title,author,year,month,forum,publication_type,doi,link,source_name,source_id,citation_count,originating_query
```

### 4. Build a reviewed list

Open `results-2024-01.csv` in your preferred editor. Review each row and keep the
publications that are real citations of your project. Save the kept rows as:

```
reviewed.csv
```

### 5. Build a reject list

During review you may also see false positives — publications that matched
your queries but aren't of interest to your project. Save those rows as:

```
rejected.csv
```

The reject list prevents false positives from reappearing in future imports.

### 6. Incremental import: only new results

Now that you have `reviewed.csv` and `rejected.csv`, subsequent imports skip
anything that matches either list:

```bash
magpub import \
  -i reviewed.csv \
  -r rejected.csv \
  -o new-results.csv
```

Output:

```
Loaded 847 reviewed publications from reviewed.csv
Loaded 23 rejected publications from rejected.csv
→ openalex: citations_of:W4297744025 → 6 results (5 new)
→ scopus: TITLE("Chameleon Cloud") → 150 results (12 new)
Wrote 17 new publications to new-results.csv (870 checked against input)
```

### 7. Check for duplicates before merging

Before adding `new-results.csv` to `reviewed.csv`, run `find-duplicates` to
see which new rows are similar to already-reviewed ones:

```bash
magpub find-duplicates reviewed.csv new-results.csv -o flagged.csv
```

Output:

```
Loaded 847 reviewed publications
Loaded 17 new publications
Found 2 potential duplicate(s):
  → "Hello World Paper" matches reviewed: Hello World Paper
  → "Hello World a conference paper" matches reviewed: Hello World Paper
Wrote 2 duplicates to flagged.csv
```

The output CSV contains an extra `reviewed_matches` column showing which
reviewed publication(s) each row matched.

### 8. Review cycle

1. Open `flagged.csv` and decide for each row whether it is a genuine new
citation or a duplicate of something already in `reviewed.csv`.

2. Add new citations to `reviewed.csv`.

3. Add false positives to `rejected.csv`.

4. Re-run `magpub import -i reviewed.csv -r rejected.csv ...` to get the
next batch.

---

## CLI reference

### `magpub init`

```bash
magpub init -c ~/.config/magpub/config.toml
```

Interactive wizard that creates a TOML config file with source credentials
and queries.

### `magpub import`

```bash
magpub import [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-c, --config PATH` | TOML config file. Default: `~/.config/magpub/config.toml` |
| `-s, --source TEXT` | Run only this source (multiple allowed). Default: all configured |
| `-o, --output FILENAME` | Output CSV. Default: stdout |
| `-i, --input-csv FILENAME` | Reviewed publications CSV — matches are excluded |
| `-r, --reject-csv FILENAME` | Rejected publications CSV — matches are excluded |
| `--exclude-title / --no-exclude-title` | Exclude by title similarity (≥ 0.5). Default: yes |
| `--exclude-doi / --no-exclude-doi` | Exclude by exact DOI. Default: yes |
| `--exclude-source-id / --no-exclude-source-id` | Exclude by exact source_id. Default: yes |

### `magpub find-duplicates`

```bash
magpub find-duplicates REVIEWED.csv NEW.csv [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-o, --output FILENAME` | Output CSV. Default: stdout |
| `--match-doi / --no-match-doi` | Match by DOI. Default: yes |
| `--match-source-id / --no-match-source-id` | Match by source_id. Default: yes |
| `--match-title / --no-match-title` | Match by title similarity. Default: yes |

---

## Library usage

You can also use magpub as a Python library. For full reference, see the [docs](https://magpub.readthedocs.io).

```python
from magpub.sources.scopus import ScopusClient

client = ScopusClient(api_key="...", institution_token="...")
for pub in client.search('TITLE("Chameleon Cloud")'):
    print(pub.title, pub.doi)
```

```python
from magpub.deduplicate import find_matches
from magpub.models import PublicationData

existing = [PublicationData(title="Hello", doi="10.1234/a", year=2020)]
new_pub = PublicationData(title="Hello", doi="10.1234/a", year=2020)

matches = find_matches(new_pub, existing)
print(f"Found {len(matches)} duplicate(s).")
```

```python
from magpub.utils import get_pub_type, get_forum, get_link, get_month

entry = {
    "ENTRYTYPE": "article",
    "title": "My Paper",
    "journal": "Nature",
    "year": "2024",
    "month": "Mar",
    "doi": "10.1234/example",
}

print(get_pub_type(entry))
print(get_forum(entry))
print(get_link(entry))
print(get_month(entry))
```

---

## Testing

```bash
cd magpub
pip install -e ".[dev]"
pytest
```

Or via unittest:

```bash
python -m unittest discover tests/
```

---

## Development

*   **Black** line-length = 88
*   **flake8** max-line-length = 80 (for Bugbear `B950` compatibility)

```bash
black magpub/
flake8 magpub/
```

---

## License

MIT — see `pyproject.toml` for details.
