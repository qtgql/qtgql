from __future__ import annotations

import glob
import pprint
import re
import subprocess
from typing import TYPE_CHECKING

from tests.conftest import PATHS
from pathlib import Path


pattern = re.compile(r"\b(TODO|FIXME)\b")
ALLOWED_TODO = re.compile("TODO\\((.+?)\\):\\s+(.*)")

def check_todos() -> list:
    tracked_files: list[Path] = []
    types = ("py", "cpp", "hpp", "jinja", "md", "yml")
    excludes = (Path(__file__), PATHS.PROJECT_ROOT / ".github/workflows/linters.yml")
    types = tuple(f".{t}" for t in types)
    for path_name in subprocess.run("git ls-tree -r HEAD --name-only".split(" "), capture_output=True, cwd=PATHS.PROJECT_ROOT).stdout.decode("utf-8").splitlines():
        file = (PATHS.PROJECT_ROOT / path_name.strip("")).resolve(True)
        if file.suffix in types and file not in excludes:
            tracked_files.append(file)

    errors: list[str] = []
    for file in tracked_files:
        for line_num, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
            if match := pattern.search(line):
                if not ALLOWED_TODO.search(line):
                    errors.append(
                        f"{match.group()} at {file.as_posix()} ({line_num}): {line}",
                    )
    if errors:
        raise Exception(f"Number of todos: {len(errors)} \n", pprint.pformat(errors))


if __name__ == "__main__":
    check_todos()
