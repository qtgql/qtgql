# TODO delete this
import re
from pathlib import Path
import os
import shutil

tests = list((Path(__file__).parent / "tests" / "gen").glob("**/test_*.cpp"))

for p in tests:
    updated = re.sub(
        'get_server_address\\("([A-Za-z])*"\\)',
        f'get_server_address(QString::fromStdString(ENV_NAME))',
        p.read_text("utf-8"),
    )
    p.write_text(updated, "UTF-8")