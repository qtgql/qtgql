import importlib
from pathlib import Path
from typing import Optional

import rich
import toml
import typer

from qtgql.codegen.py.config import QtGqlConfig

console = rich.console.Console()

# these lines are covered coverage failed to catch them.
def _get_pyproject(p: Path) -> Optional[Path]:
    pproject = p / "pyproject.toml"
    if pproject.exists():
        return pproject
    return None  # pragma: no cover


def _find_pyproject(p: Path) -> Optional[Path]:
    if pp := _get_pyproject(p):
        return pp
    for parent in p.parents:  # pragma: no cover
        return _find_pyproject(parent)
    return None


def _get_app_import_path(root: Path = Path.cwd()) -> str:
    pyproject = _find_pyproject(root)
    assert pyproject
    pp = toml.load(pyproject)
    try:
        return pp["tool"][TOOL_NAME][QTGQL_CONFIG_KEY]
    except KeyError as e:
        raise KeyError(
            f"Could not find 'tool.{TOOL_NAME}' in your pyproject.toml.",
            f"or you haven't defined '{QTGQL_CONFIG_KEY}'",
            "Make sure you have configured your project properly",
        ) from e


app = typer.Typer(pretty_exceptions_show_locals=False)

TOOL_NAME = "qtgql"
QTGQL_CONFIG_KEY = "config"


def _get_config() -> QtGqlConfig:
    console.print("[bold blue]Running system checks")
    mod, conf = _get_app_import_path().split(":")
    return getattr(importlib.import_module(mod), conf)


@app.command()
def gen():
    """Generates types based on your `QtGqlConfig` configuration object."""
    with console.status("Fetching schema and generating types...") as s:
        config = _get_config()
        s.update("[bold blue]Configuration file loaded")
        config.fetch()
    console.print(
        f"[bold green]Types were generated to [link={config.output.resolve()}]file://{config.output.resolve()}[/link] successfully!"
    )


@app.command()
def hotreload():  # pragma: no cover
    raise NotImplementedError


def entrypoint():  # pragma: no cover
    app()
