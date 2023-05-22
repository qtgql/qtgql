from __future__ import annotations

import glob
import importlib
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import rich
import typer

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig

console = rich.console.Console()
app = typer.Typer(pretty_exceptions_show_locals=False)

QTGQL_CONFIG_FNAME = "qtgqlconfig.py"


def _get_config() -> QtGqlConfig:
    console.print("[bold blue]Looking for you config file...")
    res = glob.glob(f"{QTGQL_CONFIG_FNAME}")

    if not len(res) > 1:
        console.print(
            f"[bold red]Found more than one config file. {len(res)}"
            f" found: {os.linesep.join(res)}",
        )
        typer.Abort()
    if len(res) == 0:
        console.print("[bold red]Found more than one config file using the first one")
        typer.Abort()
    mod_path = Path(res[0]).resolve(True)
    spec = importlib.util.spec_from_file_location(QTGQL_CONFIG_FNAME, mod_path)
    assert spec
    module = importlib.util.module_from_spec(spec)
    sys.modules[QTGQL_CONFIG_FNAME] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module.config


@app.command()
def gen():
    """Generates types based on your `QtGqlConfig` configuration object."""
    console.print("[bold blue]Generating...")
    with console.status("Still generating...") as s:
        config = _get_config()
        s.update("[green]Configuration file loaded")
        s.update("[bold blue]Just a second I need some coffee ☕")
        config.generate()

    console.print(
        "[bold green]Types were generated to"
        f"[link={config.generated_dir.resolve()}]"
        f"file://{config.generated_dir.resolve()}[/link] successfully!",
    )


@app.command()
def hotreload():  # pragma: no cover
    raise NotImplementedError


def entrypoint():  # pragma: no cover
    app()
