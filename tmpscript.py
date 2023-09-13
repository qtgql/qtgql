#
#
#

# TODO: don't commit this.

import re
from pathlib import Path

TESTS_DIR = Path(__file__).parent / "tests"

tests = TESTS_DIR.glob("**/test_*.cpp")

for test in tests:
    regex = ',\\s*"\\[.*?\\]"'
    original = test.read_text(encoding="utf-8")
    result = re.sub(regex, "", original)
    test.write_text(result, encoding="utf-8")
