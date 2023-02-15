from pathlib import Path

import pytest
from mktestdocs import check_docstring, check_md_file
from qtgql.tools import define_properties
from qtgql.codegen.py.runtime.custom_scalars import BaseCustomScalar

docs_dir = Path(__file__).parent.parent / "docs"
assert docs_dir.exists()
docs = list(docs_dir.glob("**/*.md"))
assert docs


@pytest.mark.parametrize("fpath", docs, ids=str)
def test_md(fpath, qtbot):
    fpath = fpath.resolve(True)
    check_md_file(fpath=fpath, memory=True)


@pytest.mark.parametrize(
    "documented",
    [define_properties, BaseCustomScalar],
    ids=lambda d: d.__name__,
)
def test_docstring(documented):
    check_docstring(obj=documented)
