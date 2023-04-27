import json
import re
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Optional

import pytest
from typing_extensions import TypedDict

build_dir = Path(__file__).parent.parent / "build"


class TestProperty(TypedDict):
    name: str
    value: str


class TestDefinition(TypedDict):
    name: str
    properties: list[TestProperty]


class CtestDiscoveryResult(TypedDict):
    tests: list[TestDefinition]


class CtestTestCommand:
    def __init__(self, test_name: str) -> None:
        self._data: list[str] = ["ctest", "-R"]
        self.test_name: str = test_name
        self.ret_res: Optional[subprocess.CompletedProcess] = None

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


test_commands = collect_tests()


@pytest.mark.parametrize("command", test_commands, ids=lambda v: v.test_name)
def test_cpp(command: CtestTestCommand):
    command.run()
    if log_file := command.failed_log:
        pytest.fail(msg=f"\n {'-'*8} Test {command.test_name} Failed {'-'*8} \n {log_file}")
