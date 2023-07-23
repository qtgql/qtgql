import contextlib
import os
from pathlib import Path


@contextlib.contextmanager
def temp_cwd(to: Path) -> None:
    prev = Path.cwd()
    os.chdir(to)
    try:
        yield
    finally:
        os.chdir(prev)
