import qtgqlcodegen
from qtgqlcodegen.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version():
    res = runner.invoke(app, ["version"])
    assert qtgqlcodegen.__version__ in res.stdout
