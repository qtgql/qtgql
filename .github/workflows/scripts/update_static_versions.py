import os
import re
import subprocess

from autopub import autopub
from autopub.base import get_project_version
from tests.conftest import PATHS


def update_cmake_version() -> None:
    assert PATHS.ROOT_CMAKE.exists()
    cmake_ver_pattern = r"set\(QTGQL_VERSION\s+([\d.]+)\)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), get_project_version())

    replaced = re.sub(cmake_ver_pattern, ver_repl, PATHS.ROOT_CMAKE.read_text(), count=1)
    PATHS.ROOT_CMAKE.write_text(replaced, "UTF-8")


INIT_FILE = PATHS.QTGQLCODEGEN_ROOT / "__init__.py"


def update_python_version() -> None:
    assert INIT_FILE.exists()
    pattern = r"__version__: str = '([\d.]+)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), get_project_version())

    replaced = re.sub(pattern, ver_repl, INIT_FILE.read_text(), count=1)
    INIT_FILE.write_text(replaced, "UTF-8")


if __name__ == "__main__":
    a = str(INIT_FILE)
    os.chdir(PATHS.PROJECT_ROOT)
    args = None
    autopub.prepare(args)
    update_cmake_version()
    update_python_version()
    subprocess.run(
        f"git add {INIT_FILE!s} {PATHS.ROOT_CMAKE!s}".split(" "),
    ).check_returncode()
    autopub.build(args)
    autopub.commit(args)
    autopub.githubrelease(args)
