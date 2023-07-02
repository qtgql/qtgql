from __future__ import annotations

import glob
import pprint
import re
from typing import TYPE_CHECKING

from tests.conftest import PATHS

if TYPE_CHECKING:
    from pathlib import Path

pattern = re.compile(r"\b(TODO|FIXME)\b")
ALLOWED_TODO = re.compile("TODO\\((.+?)\\):\\s+(.*)")


def check_todos() -> list:
    types = ("py", "cpp", "hpp")
    files_grabbed: list[Path] = []
    for f_type in types:
        files_grabbed.extend(
            [
                PATHS.PROJECT_ROOT / f
                for f in glob.glob(f"**/*.{f_type}", root_dir=PATHS.PROJECT_ROOT, recursive=True)
            ],
        )
    errors: list[str] = []
    for file in files_grabbed:
        for line_num, line in enumerate(file.read_text().splitlines(), start=1):
            if match := pattern.search(line):
                if not ALLOWED_TODO.search(line):
                    errors.append(
                        f"Found {match.group()} in {file.as_posix()} ({line_num}): {line}",
                    )
    if errors:
        raise Exception(pprint.pformat(errors))


if __name__ == "__main__":
    check_todos()
