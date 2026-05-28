# magpub

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
