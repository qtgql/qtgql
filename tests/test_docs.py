from pathlib import Path

import pytest
from mktestdocs import check_md_file

docs_dir = Path(__file__).parent.parent / "docs"
assert docs_dir.exists()
docs = list(docs_dir.glob("**/*.md"))
assert docs


@pytest.mark.parametrize("fpath", docs, ids=str)
def test_files_good(fpath, qtbot):
    fpath = fpath.resolve(True)
    check_md_file(fpath=fpath, memory=True)
