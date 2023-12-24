from __future__ import annotations

import os

from tests.test_codegen.testcases import (
    generate_testcases,
    implemented_testcases,
)


def generate_testcases_by_name(testcases_names: list[str]) -> None:
    to_gen = []
    first_testcase = implemented_testcases[0]
    for tc in implemented_testcases:
        if tc.test_name in testcases_names:
            to_gen.append(tc)
        if tc.test_name == first_testcase.test_name:
            env_file = os.getenv("GITHUB_ENV")
            with open(env_file, "a") as envfile:  # noqa: PTH123
                envfile.write("SHOULD_TEST_CORE=1")
            os.environ.setdefault("SHOULD_TEST_CORE", "1")

    generate_testcases(*to_gen)


if __name__ == "__main__":
    # fetch test cases names from environment
    testcases_array = os.getenv("MATRIX_TESTCASES")

    generate_testcases_by_name(testcases_array)
