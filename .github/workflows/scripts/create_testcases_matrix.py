"""Script to split tests.yml runners for faster builds."""
from __future__ import annotations

import json
from typing import Literal

import attrs
from attr import Factory, define
from tests.test_codegen.testcases import QtGqlTestCase, implemented_testcases


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


@define
class ConanProfile:
    runner_os: Literal["ubuntu-latest"] | Literal["windows-latest"]
    profile: str


CONAN_PROFILES = (
    ConanProfile(runner_os="ubuntu-latest", profile="profiles/Linux"),
    ConanProfile(runner_os="windows-latest", profile="profiles/Windows_mingw"),
)


@define
class Matrix:
    testcases: list[str]
    profile: list[ConanProfile]
    qt_version: list[str] = Factory(lambda: ["6.5.0"])
    python_version: list[str] = Factory(lambda: ["3.9", "3.10", "3.11"])


TESTCASES_PER_RUNNER = 9


def tst_names(tests: list[QtGqlTestCase]) -> list[str]:
    return [tst.test_name for tst in tests]


def main() -> None:
    chunked_testcases = list(chunks(implemented_testcases, TESTCASES_PER_RUNNER))

    matrix = attrs.asdict(
        Matrix(
            profile=CONAN_PROFILES,
            testcases=[(tst_names(chunk)) for chunk in chunked_testcases],
        ),
    )

    print(json.dumps(matrix))  # noqa


if __name__ == "__main__":
    main()
