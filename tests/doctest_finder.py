from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

exe_suffix = "exe" if sys.platform == "win32" else ".so"
PROJECT_ROOT = Path(__file__).parent.parent
build_dir = PROJECT_ROOT / "build" / "Debug"
test_executable = build_dir / f"test_qtgql.{exe_suffix}"


class DoctestTestcase:
    def __init__(self, test_exe: Path, test_name: str) -> None:
        self._args: str = f'{test_exe!s} -tc="{test_name}"'
        self.test_name: str = test_name

    def run(self) -> None:
        ret = subprocess.run(
            self._args,
            cwd=build_dir.resolve(True),
            capture_output=True,
            timeout=10,
            shell=True,  # noqa: S602
        )
        if ret.returncode != 0:
            pytest.fail(ret.stdout.decode("utf-8"))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.test_name}]"


def collect_tests() -> list[DoctestTestcase]:
    ret: list[DoctestTestcase] = []
    res = subprocess.run(
        [str(test_executable.resolve(True)), "-ltc"],
        cwd=build_dir.resolve(True),
        capture_output=True,
    )
    tests = list(res.stdout.decode("utf-8").splitlines())[2:-2]
    for test_name in tests:
        ret.append(DoctestTestcase(test_executable, test_name))
    return ret
