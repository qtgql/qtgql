from __future__ import annotations

import argparse
import json
import sys

from tests.test_codegen.testcases import (
    generate_testcases,
    implemented_testcases,
)


def generate_testcases_by_name(testcases_names: list[str]) -> None:
    to_gen = []
    for tc in implemented_testcases:
        if tc.test_name in testcases_names:
            to_gen.append(tc)

    generate_testcases(*to_gen)


if __name__ == "__main__":
    print(sys.argv)  # noqa
    parser = argparse.ArgumentParser(prog="find testcases")
    parser.add_argument("testcases_names_json", default="[]")

    args = parser.parse_args()
    generate_testcases_by_name(json.loads(args.testcases_names_json))
