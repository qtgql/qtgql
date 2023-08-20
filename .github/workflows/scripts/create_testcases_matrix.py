"""Script to split tests.yml runners for faster builds."""
from __future__ import annotations

import json

import attrs
from attr import Factory, define
from tests.test_codegen.testcases import implemented_testcases


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


TESTCASES_PER_RUNNER = 6


@define
class Runner:
    testcases: list[str]
    os: str = "ubuntu-latest"
    qt_version: list[str] = Factory(lambda: ["6.5.0"])
    python_version: list[str] = Factory(lambda: ["3.9", "3.10", "3.11"])


def main() -> None:
    chunked_testcases = list(chunks(implemented_testcases, TESTCASES_PER_RUNNER))
    ubuntu_runners = [
        attrs.asdict(
            Runner(
                testcases=[testcase.test_name for testcase in chunk],
            ),
        )
        for chunk in chunked_testcases
    ]

    print(json.dumps(ubuntu_runners))  # noqa


if __name__ == "__main__":
    main()
