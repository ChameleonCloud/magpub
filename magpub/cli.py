"""magpub CLI entry point."""

import csv
import sys
from pathlib import Path
from typing import Optional

import click

from magpub.config import Config, ConfigError, DEFAULT_CONFIG_PATH
from magpub.csv_reader import read_csv
from magpub.csv_writer import FIELDNAMES, write_csv
from magpub.deduplicate import find_matches
from magpub.importer import (
    run_openalex,
    run_science_direct,
    run_scopus,
    run_semantic_scholar,
)
from magpub.models import PublicationData

RUNNERS = {
    "scopus": run_scopus,
    "semantic_scholar": run_semantic_scholar,
    "openalex": run_openalex,
    "science_direct": run_science_direct,
}


@click.group()
def cli():
    """magpub — import and deduplicate academic publications."""


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to TOML config file.",
)
@click.option(
    "--source",
    "-s",
    multiple=True,
    help="Source to run (can be given multiple times). Defaults to all configured.",
)
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default="-",
    help="Output CSV file. Defaults to stdout.",
)
@click.option(
    "--input-csv",
    "-i",
    type=click.File("r"),
    help="Existing CSV of known publications. New publications matching these are excluded from output.",
)
@click.option(
    "--reject-csv",
    "-r",
    type=click.File("r"),
    help="CSV of rejected/false-positive publications. Matches are excluded from output.",
)
@click.option(
    "--exclude-title/--no-exclude-title",
    default=True,
    help="Exclude when titles match (similarity >= 0.5).",
)
@click.option(
    "--exclude-doi/--no-exclude-doi",
    default=True,
    help="Exclude when DOI matches exactly.",
)
@click.option(
    "--exclude-source-id/--no-exclude-source-id",
    default=True,
    help="Exclude when source_id matches exactly.",
)
def import_cmd(
    config: Path,
    source: tuple,
    output,
    input_csv,
    reject_csv,
    exclude_title: bool,
    exclude_doi: bool,
    exclude_source_id: bool,
):
    """Run publication imports from configured sources.

    When --input-csv is provided, any newly found publication that matches
    an existing row (by DOI, source_id, or title similarity) is skipped in
    the output. This lets you review only genuinely new results.

    When --reject-csv is provided, matches against the reject list are also
    excluded so false positives don't reappear in subsequent runs.
    """
    try:
        cfg = Config.from_path(config)
    except ConfigError as exc:
        raise click.ClickException(str(exc))

    selected_sources = list(source) if source else None
    source_configs = cfg.get_sources(selected_sources)

    if not source_configs:
        sources_str = ", ".join(selected_sources) if selected_sources else "any"
        raise click.ClickException(f"No configured sources found for: {sources_str}")

    # Load baseline and reject lists
    existing_pubs = []
    if input_csv:
        existing_pubs = list(read_csv(input_csv))
        click.echo(
            f"Loaded {len(existing_pubs)} existing publications from {input_csv.name}",
            err=True,
        )

    reject_pubs = []
    if reject_csv:
        reject_pubs = list(read_csv(reject_csv))
        click.echo(
            f"Loaded {len(reject_pubs)} rejected publications from {reject_csv.name}",
            err=True,
        )

    all_publications = []
    for sc in source_configs:
        runner = RUNNERS.get(sc.name)
        if not runner:
            click.echo(f"Unknown source: {sc.name}", err=True)
            continue

        for query in sc.queries:
            count = 0
            new_count = 0
            for pub in runner(sc):
                if pub.extra.get("originating_query") != query:
                    continue
                count += 1
                if _is_new(pub, existing_pubs + reject_pubs, exclude_doi, exclude_source_id, exclude_title):
                    all_publications.append(pub)
                    new_count += 1
            click.echo(
                f"→ {sc.name}: {query} → {count} results ({new_count} new)",
                err=True,
            )

        for cid in sc.citations_of:
            count = 0
            new_count = 0
            target = f"citations_of:{cid}"
            for pub in runner(sc):
                if pub.extra.get("originating_query") != target:
                    continue
                count += 1
                if _is_new(pub, existing_pubs + reject_pubs, exclude_doi, exclude_source_id, exclude_title):
                    all_publications.append(pub)
                    new_count += 1
            click.echo(
                f"→ {sc.name}: citations_of:{cid} → {count} results ({new_count} new)",
                err=True,
            )

    write_csv(all_publications, output)

    total = len(all_publications)
    checked = len(existing_pubs) + len(reject_pubs)
    if output.name != "<stdout>":
        click.echo(
            f"Wrote {total} new publications to {output.name} ({checked} checked against input)",
            err=True,
        )
    else:
        click.echo(
            f"Wrote {total} new publications ({checked} checked against input)",
            err=True,
        )


def _is_new(
    pub: PublicationData,
    existing: list,
    check_doi: bool,
    check_source_id: bool,
    check_title: bool,
) -> bool:
    """Return True if *pub* does not match any in *existing*."""
    if not existing:
        return True
    matches = find_matches(
        pub,
        existing,
        doi_match=check_doi,
        source_id_match=check_source_id,
    )
    if matches:
        return False
    if check_title:
        from magpub.utils import how_similar
        for e in existing:
            if how_similar(pub.title, e.title) >= 0.5:
                return False
    return True


@cli.command("find-duplicates")
@click.argument(
    "reviewed",
    type=click.File("r"),
)
@click.argument(
    "new",
    type=click.File("r"),
)
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default="-",
    help="Output CSV file. Defaults to stdout.",
)
@click.option(
    "--match-doi/--no-match-doi",
    default=True,
    help="Match by DOI.",
)
@click.option(
    "--match-source-id/--no-match-source-id",
    default=True,
    help="Match by source_id.",
)
@click.option(
    "--match-title/--no-match-title",
    default=True,
    help="Match by title similarity (>= 0.5).",
)
def find_duplicates_cmd(
    reviewed,
    new,
    output,
    match_doi: bool,
    match_source_id: bool,
    match_title: bool,
):
    """Flag publications from NEW that are similar to ones in REVIEWED.

    Reads two CSV files and writes a CSV containing only the rows from NEW
    that have at least one match in REVIEWED.  The output includes an
    extra ``reviewed_matches`` column listing the matched titles for
    review.
    """
    reviewed_pubs = list(read_csv(reviewed))
    new_pubs = list(read_csv(new))

    click.echo(f"Loaded {len(reviewed_pubs)} reviewed publications", err=True)
    click.echo(f"Loaded {len(new_pubs)} new publications", err=True)

    duplicates = []
    for pub in new_pubs:
        matches = find_matches(
            pub,
            reviewed_pubs,
            doi_match=match_doi,
            source_id_match=match_source_id,
        )
        if not matches and match_title:
            from magpub.utils import how_similar
            matches = [
                c for c in reviewed_pubs
                if how_similar(pub.title, c.title) >= 0.5
            ]

        if matches:
            # Store matching reviewed titles in extra for CSV output
            pub.extra["reviewed_matches"] = "; ".join(
                m.title for m in matches
            )
            duplicates.append(pub)

    if duplicates:
        click.echo(f"Found {len(duplicates)} potential duplicate(s):", err=True)
        for pub in duplicates:
            click.echo(
                f'  → "{pub.title}" matches reviewed: {pub.extra["reviewed_matches"]}',
                err=True,
            )
    else:
        click.echo("No duplicates found.", err=True)

    write_csv_with_matches(duplicates, output)

    if output.name != "<stdout>":
        click.echo(f"Wrote {len(duplicates)} duplicates to {output.name}", err=True)


def write_csv_with_matches(publications, output) -> None:
    """Write publications to CSV, including reviewed_matches column."""
    fieldnames = list(FIELDNAMES) + ["reviewed_matches"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for pub in publications:
        row = {
            "title": pub.title,
            "author": pub.author,
            "year": pub.year,
            "month": pub.month,
            "forum": pub.forum,
            "publication_type": pub.publication_type,
            "doi": pub.doi,
            "link": pub.link,
            "source_name": pub.source_name,
            "source_id": pub.source_id,
            "citation_count": pub.citation_count,
            "originating_query": pub.extra.get("originating_query", ""),
            "reviewed_matches": pub.extra.get("reviewed_matches", ""),
        }
        writer.writerow(row)


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to write the config file.",
)
def init(config: Path):
    """Create a configuration file interactively."""
    from magpub.config import run_init_wizard

    run_init_wizard(config)


if __name__ == "__main__":
    cli()
