"""Load, validate, and scaffold magpub TOML config."""

from pathlib import Path
from typing import Any, Dict, List

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

import tomli_w


def _require_click():
    try:
        import click  # noqa: F401
    except ImportError as exc:
        raise ImportError("click is required for magpub init. Install: pip install magpub[cli]") from exc


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "magpub" / "config.toml"

# CLI prompt helpers
CLI_PROMPTS = {
    "scopus": {"api_key": "API key", "institution_token": "Institution token"},
    "semantic_scholar": {"api_key": "API key (optional)"},
    "openalex": {"mailto": "mailto address"},
    "science_direct": {"api_key": "API key", "institution_token": "Institution token"},
}


class ConfigError(Exception):
    pass


class SourceConfig:
    """Configuration for a single source."""

    VALID_KEYS = {"queries", "citations_of"} | {
        "api_key",
        "institution_token",
        "mailto",
    }

    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.api_key = data.get("api_key")
        self.institution_token = data.get("institution_token")
        self.mailto = data.get("mailto")
        self.queries: List[str] = data.get("queries", [])
        self.citations_of: List[str] = data.get("citations_of", [])

        unknown = set(data.keys()) - self.VALID_KEYS
        if unknown:
            raise ConfigError(
                f"Unknown keys for source '{name}': {', '.join(sorted(unknown))}"
            )

    def has_search(self) -> bool:
        return bool(self.queries or self.citations_of)


class Config:
    """Top-level parsed config."""

    SOURCES = ("scopus", "semantic_scholar", "openalex", "science_direct")

    def __init__(self, path: Path, raw: Dict[str, Any]):
        self.path = path
        self.sources: Dict[str, SourceConfig] = {}
        for name in self.SOURCES:
            if name in raw:
                self.sources[name] = SourceConfig(name, raw[name])

    @classmethod
    def from_path(cls, path: Path) -> "Config":
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls(path, raw)

    def get_sources(self, names=None) -> List[SourceConfig]:
        """Return active source configs, optionally filtered by name."""
        result = []
        for name in names or self.SOURCES:
            cfg = self.sources.get(name)
            if cfg and cfg.has_search():
                result.append(cfg)
        return result


def run_init_wizard(path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Interactive TOML config scaffold."""
    _require_click()
    import click

    click.echo("magpub init — create a configuration file")
    click.echo("")

    # Ask for path
    path_input = click.prompt("Config path", default=str(path), type=str)
    path = Path(path_input).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not click.confirm(
        f"{path} already exists. Overwrite?", default=False
    ):
        click.echo("Aborting.")
        return

    # Ask which sources to configure
    source_choices = ", ".join(Config.SOURCES)
    sources_input = click.prompt(
        "Sources to configure",
        default=source_choices,
        type=str,
    )
    selected = [s.strip() for s in sources_input.split(",") if s.strip()]

    raw: Dict[str, Any] = {}

    for source_name in selected:
        click.echo(f"\nSource: {source_name}")
        source_data: Dict[str, Any] = {}

        # Collect credentials
        for key, prompt_text in CLI_PROMPTS.get(source_name, {}).items():
            val = click.prompt(f"  {prompt_text}", default="", show_default=False)
            if val:
                source_data[key] = val

        # Collect queries or citations_of
        if source_name == "openalex":
            items: List[str] = []
            click.echo("  citations_of IDs (blank line to finish):")
            while True:
                line = click.prompt("  >", default="", show_default=False)
                if not line:
                    break
                items.append(line.strip())
            if items:
                source_data["citations_of"] = items
        else:
            items = []
            click.echo("  Queries (blank line to finish):")
            while True:
                line = click.prompt("  >", default="", show_default=False)
                if not line:
                    break
                items.append(line.strip())
            if items:
                source_data["queries"] = items

        if source_data:
            raw[source_name] = source_data

    with open(path, "wb") as f:
        tomli_w.dump(raw, f)

    click.echo(f"\nConfig written to {path}")
