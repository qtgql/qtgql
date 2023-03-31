from functools import partial
from pathlib import Path

import pytest
import toml
from typer.testing import CliRunner

from qtgql.codegen.cli import _find_pyproject
from qtgql.codegen.cli import _get_app_import_path
from qtgql.codegen.cli import app
from qtgql.codegen.cli import QTGQL_CONFIG_KEY
from qtgql.codegen.cli import TOOL_NAME


@pytest.fixture
def monkey_pyproject(monkeypatch, tmp_path) -> Path:
    def fake_cwd():
        return tmp_path / "nest"  # this will force recursive lookup for pyproject.toml

    monkey_toml = tmp_path / "pyproject.toml"
    pp_toml = _find_pyproject(Path.cwd())
    cop = toml.load(pp_toml).copy()
    with monkey_toml.open("w") as tf:
        toml.dump(cop, tf)

    from qtgql.codegen import cli

    monkeypatch.setattr(cli, _get_app_import_path.__name__, partial(_get_app_import_path, tmp_path))
    return monkey_toml


runner = CliRunner()


def test_cant_find_pyproject(monkeypatch, monkey_pyproject, tmp_path):
    clone = toml.load(monkey_pyproject).copy()
    clone["tool"][TOOL_NAME].pop(QTGQL_CONFIG_KEY)
    with monkey_pyproject.open("w") as fh:
        toml.dump(clone, fh)
    res = runner.invoke(app, ["gen"])
    assert isinstance(res.exception, KeyError)


def test_generate_success(monkey_pyproject, monkeypatch):
    res = runner.invoke(app, ["gen"])
    assert res.exit_code == 0
