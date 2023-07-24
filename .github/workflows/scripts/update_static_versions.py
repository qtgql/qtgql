import os
import re
from pathlib import Path

from autopub import autopub
from autopub.base import get_project_version, git
from tests.conftest import PATHS


def update_cmake_version() -> None:
    assert PATHS.ROOT_CMAKE.exists()
    cmake_ver_pattern = r"set\(QTGQL_VERSION\s+([\d.]+)\)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), get_project_version())

    replaced = re.sub(cmake_ver_pattern, ver_repl, PATHS.ROOT_CMAKE.read_text(), count=1)
    PATHS.ROOT_CMAKE.write_text(replaced, "UTF-8")


INIT_FILE = PATHS.QTGQLCODEGEN_ROOT / "__init__.py"
CONANFILE = PATHS.PROJECT_ROOT / "conanfile.py"


def update_python_versions() -> None:
    assert INIT_FILE.exists()
    assert CONANFILE.exists()
    pattern = r'__version__: str = "([\d.]+)"'

    def replace__version__(file: Path) -> None:
        def ver_repl(match: re.Match) -> str:
            return match.group(0).replace(match.group(1), get_project_version())

        replaced = re.sub(pattern, ver_repl, file.read_text(), count=1)
        file.write_text(replaced, "UTF-8")
        git(["add", str(file)])

    replace__version__(INIT_FILE)
    replace__version__(CONANFILE)


update_python_versions()

if __name__ == "__main__":
    os.chdir(PATHS.PROJECT_ROOT)
    args = None
    autopub.prepare(args)
    update_cmake_version()
    update_python_versions()
    git(["add", str(PATHS.ROOT_CMAKE)])
    autopub.build(args)
    autopub.commit(args)
    autopub.githubrelease(args)
