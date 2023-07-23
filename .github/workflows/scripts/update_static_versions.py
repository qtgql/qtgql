import re

from autopub.base import get_project_version
from tests.conftest import PATHS

CURRENT_VERSION = get_project_version()


def update_cmake_version() -> None:
    assert PATHS.ROOT_CMAKE.exists()
    cmake_ver_pattern = r"set\(QTGQL_VERSION\s+([\d.]+)\)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), CURRENT_VERSION)

    replaced = re.sub(cmake_ver_pattern, ver_repl, PATHS.ROOT_CMAKE.read_text(), count=1)
    PATHS.ROOT_CMAKE.write_text(replaced, "UTF-8")


def update_python_version() -> None:
    init_file = PATHS.QTGQLCODEGEN_ROOT / "__init__.py"
    assert init_file.exists()
    pattern = r"__version__: str = '([\d.]+)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), CURRENT_VERSION)

    replaced = re.sub(pattern, ver_repl, init_file.read_text())
    init_file.write_text(replaced, "UTF-8")


if __name__ == "__main__":
    update_cmake_version()
    update_python_version()
