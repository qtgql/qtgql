from functools import partial
from pathlib import Path

import pytest
import toml
from qtgql.codegen.cli import (
    QTGQL_CONFIG_KEY,
    TOOL_NAME,
    _find_pyproject,
    _get_app_import_path,
    app,
)
from typer.testing import CliRunner


@pytest.fixture
def monkey_pyproject(monkeypatch, tmp_path) -> Path:
    def fake_cwd():
        return tmp_path / "nest"  # this will force recursive lookup for pyproject.toml

    monkey_toml = tmp_path / "pyproject.toml"
    pp_toml = _find_pyproject(Path.cwd())
    cop = toml.load(pp_toml).copy()
    with open(monkey_toml, "w") as tf:
        toml.dump(cop, tf)

    from qtgql.codegen import cli

    monkeypatch.setattr(cli, _get_app_import_path.__name__, partial(_get_app_import_path, tmp_path))
    yield monkey_toml


runner = CliRunner()


def test_cant_find_pyproject(monkeypatch, monkey_pyproject, tmp_path):
    clone = toml.load(monkey_pyproject).copy()
    clone["tool"][TOOL_NAME].pop(QTGQL_CONFIG_KEY)
    with open(monkey_pyproject, "w") as fh:
        toml.dump(clone, fh)
    res = runner.invoke(app, ["gen"])
    assert isinstance(res.exception, KeyError)


def test_fetch_success(monkey_pyproject, monkeypatch, mini_server):
    from tests.test_sample_ui.main import qtgqlconfig

    monkeypatch.setattr(qtgqlconfig, "url", mini_server.address.replace("ws", "http"))
    res = runner.invoke(app, ["gen"])
    assert res.exit_code == 0
