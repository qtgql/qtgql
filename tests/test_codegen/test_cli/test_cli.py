from pathlib import Path

import qtgqlcodegen
from qtgqlcodegen.cli import app
from typer.testing import CliRunner

from tests.test_codegen.utils import temp_cwd

runner = CliRunner()

DIR_WITH_TWO_CONFIGS = Path(__file__).parent / "dir_with_two_config_files"
DIR_WITH_NO_CONFIG = Path(__file__).parent / "dir_with_no_config"


def test_version():
    res = runner.invoke(app, ["version"])
    assert qtgqlcodegen.__version__ in res.stdout


def test_found_more_than_one_config_file_aborts() -> None:
    with temp_cwd(DIR_WITH_TWO_CONFIGS.resolve(True)):
        res = runner.invoke(app, ["gen"])
    assert res.exception


def test_no_config_found_aborts() -> None:
    with temp_cwd(DIR_WITH_NO_CONFIG.resolve(True)):
        res = runner.invoke(app, ["gen"])
    assert res.exception
