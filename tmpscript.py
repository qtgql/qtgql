import os
from pathlib import  Path


import shutil
root = Path(__file__).parent
testcases_dir = root / "tests" / "gen"
generated = list(testcases_dir.glob("**/__generated__"))

for g in generated:
    shutil.rmtree(g)