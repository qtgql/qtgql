"""Script to split tests.yml runners for faster builds."""
from __future__ import annotations

import json

import attrs
from attr import Factory, define
from tests.test_codegen.testcases import QtGqlTestCase, implemented_testcases


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


TESTCASES_PER_RUNNER = 5


@define
class Matrix:
    testcases: list[str]
    os: list[str] = Factory(lambda: ["ubuntu-22.04", "windows-2022"])
    qt_version: list[str] = Factory(lambda: ["6.5.2"])
    python_version: list[str] = Factory(lambda: ["3.9", "3.10", "3.11"])


def main() -> None:
    chunked_testcases = list(chunks(implemented_testcases, TESTCASES_PER_RUNNER))

    def tst_names(tests: list[QtGqlTestCase]) -> list[str]:
        return [tst.test_name for tst in tests]

    matrix = attrs.asdict(
        Matrix(
            testcases=[(tst_names(chunk)) for chunk in chunked_testcases],
        ),
    )

    print(json.dumps(matrix))  # noqa


if __name__ == "__main__":
    main()
