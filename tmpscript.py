import os
from pathlib import  Path


import shutil
root = Path(__file__).parent
testcases_dir = root / "tests" / "gen"
generated = list(testcases_dir.glob("**/qtgqlconfig.py"))

for g in generated:
    os.remove(g)