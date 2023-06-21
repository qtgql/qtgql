from __future__ import annotations

import json
import re
import subprocess
from functools import cached_property
from pathlib import Path

from typing_extensions import TypedDict

PROJECT_ROOT = Path(__file__).parent.parent
build_dir = PROJECT_ROOT / "build" / "Debug"


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
