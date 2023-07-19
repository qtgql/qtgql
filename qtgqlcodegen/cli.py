from __future__ import annotations

import glob
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import rich
import typer

import qtgqlcodegen

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig

console = rich.console.Console()
app = typer.Typer(pretty_exceptions_show_locals=False)

QTGQL_CONFIG_FNAME = "qtgqlconfig.py"


def _create_path_link(path: Path) -> str:
    return f"[link={path.resolve()}]{path!s}[/link]"


def _get_config() -> QtGqlConfig:
    console.print("[bold blue]Looking for a config file...")
    res = glob.glob(f"**/{QTGQL_CONFIG_FNAME}", recursive=True)

    if len(res) > 1:
        cwd = Path.cwd()
        results = " \n".join([_create_path_link(cwd / rel) for rel in res])

        console.print(
            f"[bold red]Found more than one config file. {len(res)}" f" found:\n {results}",
        )
        raise typer.Abort()
    elif len(res) < 1:
        console.print(
            f"[bold red]Could not find a config file under {_create_path_link(Path.cwd())}",
        )
        raise typer.Abort()

    mod_path = Path(res[0]).resolve(True)
    spec = importlib.util.spec_from_file_location(QTGQL_CONFIG_FNAME, mod_path)
    assert spec
    module = importlib.util.module_from_spec(spec)
    sys.modules[QTGQL_CONFIG_FNAME] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module.config


@app.command()
def gen() -> None:
    """Generates types based on your `QtGqlConfig` configuration object."""
    console.print("[bold blue]Generating...")
    with console.status("Still generating...") as s:
        config = _get_config()
        s.update("[green]Configuration file loaded")
        s.update("[bold blue]Just a second I need some coffee ☕")
        config.generate()

    console.print(
        "[bold green]Generated to" f"{_create_path_link(config.generated_dir)} successfully!",
    )


@app.command()
def hotreload():  # pragma: no cover
    raise NotImplementedError


@app.command()
def version() -> None:
    """Show the version of qtgql."""
    console.print(f"[bold blue]{qtgqlcodegen.__version__}")


def entrypoint():  # pragma: no cover
    app()
