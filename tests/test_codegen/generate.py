from __future__ import annotations

import os

from tests.test_codegen.testcases import (
    generate_testcases,
    implemented_testcases,
)


def generate_testcases_by_name(testcases_names: list[str]) -> None:
    to_gen = []
    env_file = os.getenv("GITHUB_ENV")
    # this is a trick to avoid creating a whole GitHub action, instead we build
    #  the core tests only if we build the first testcase.
    with open(env_file, "a") as envfile:  # noqa: PTH123
        if implemented_testcases[0].test_name in testcases_names:
            envfile.write("SHOULD_TEST_CORE=True")
        else:
            envfile.write("SHOULD_TEST_CORE=False")

    for tc in implemented_testcases:
        if tc.test_name in testcases_names:
            to_gen.append(tc)

    generate_testcases(*to_gen)


if __name__ == "__main__":
    # fetch test cases names from environment
    testcases_array = os.getenv("MATRIX_TESTCASES")

    generate_testcases_by_name(testcases_array)
