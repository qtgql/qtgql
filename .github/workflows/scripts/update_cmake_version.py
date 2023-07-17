import re

import regex
from autopub.base import get_project_version
from tests.conftest import PATHS


def update_cmake_version() -> None:
    assert PATHS.ROOT_CMAKE.exists()
    version = get_project_version()
    cmake_ver_pattern = r"set\(QTGQL_VERSION\s+([\d.]+)\)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), version)

    replaced = regex.sub(cmake_ver_pattern, ver_repl, PATHS.ROOT_CMAKE.read_text(), count=1)
    PATHS.ROOT_CMAKE.write_text(replaced)


if __name__ == "__main__":
    update_cmake_version()
