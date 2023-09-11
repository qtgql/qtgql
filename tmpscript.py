# TODO delete this

from pathlib import Path
import os
import shutil

dirs_and_files = list((Path(__file__).parent / "tests" / "gen").glob("**/*Testcase*"))

for p in dirs_and_files:
    os.rename(p, p.parent / p.name.replace("Testcase", ""))