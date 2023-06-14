from __future__ import annotations

import json
import os
import re
import subprocess
from functools import cached_property
from pathlib import Path

import pytest
from typing_extensions import TypedDict

from tests.conftest import PATHS, MiniServer

build_dir = PATHS.PROJECT_ROOT / "build" / "Debug"
if not build_dir.exists():
    build_dir.mkdir(parents=True)


class CtestTestProperty(TypedDict):
    name: str
    value: str


class CtestTestDefinition(TypedDict):
    name: str
    properties: list[CtestTestProperty]


class CtestDiscoveryResult(TypedDict):
    tests: list[CtestTestDefinition]


class CtestTestCommand:
    def __init__(self, test_name: str) -> None:
        self._data: list[str] = ["ctest", "-R"]
        self.test_name: str = test_name
        self.ret_res: subprocess.CompletedProcess | None = None

    def add_command(self, command: str):
        self._data.append(command)

    @cached_property
    def failed_log(self) -> str | None:
        assert self.ret_res
        try:
            match = re.findall("(in: )(.*)(\\.log)", self.ret_res.stderr.decode())
            log_file = match[0][1]
        except IndexError:
            return None
        return Path(log_file + ".log").resolve(True).read_text()

    def run(self) -> None:
        self.ret_res = subprocess.run(
            [*self._data, self.test_name],
            cwd=build_dir.resolve(True),
            capture_output=True,
        )


def collect_tests() -> list[CtestTestCommand]:
    ret: list[CtestTestCommand] = []
    res = subprocess.run(
        ["ctest", "--show-only=json-v1"],
        cwd=build_dir.resolve(True),
        capture_output=True,
    )
    data: CtestDiscoveryResult = json.loads(res.stdout)
    for test in data["tests"]:
        ret.append(CtestTestCommand(test["name"]))
    return ret


@pytest.mark.parametrize("command", collect_tests(), ids=lambda v: v.test_name)
def test_generated_tests(command: CtestTestCommand, schemas_server: MiniServer):
    os.environ.setdefault("SCHEMAS_SERVER_ADDR", schemas_server.address.replace("graphql", ""))
    command.run()
    if log_file := command.failed_log:
        if "All tests passed" not in log_file:
            pytest.fail(  # noqa: PT016
                reason=f"\n {'-'*8} Test {command.test_name} Failed {'-'*8} \n {log_file}",
            )
