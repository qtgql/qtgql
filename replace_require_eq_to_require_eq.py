# TODO: no commit


import re
from pathlib import Path

tests_dir = Path(__file__).parent / 'tests'
tests = list(tests_dir.glob("**/test_*.cpp"))

def replacer(m: re.Match) -> str:
    begin, end = m.span()
    full_match = m.string[begin: end]
    replace = full_match.replace("REQUIRE(", "REQUIRE_EQ(").replace("==", ',')
    return replace

for tc in tests:
    migrated = re.sub(r"(REQUIRE\().*(==)", repl=replacer, string=tc.read_text(encoding='utf-8'))
    tc.write_text(migrated, 'utf-8')
def replacer_ne(m: re.Match) -> str:
    begin, end = m.span()
    full_match = m.string[begin: end]
    replace = full_match.replace("REQUIRE(", "REQUIRE_NE(").replace("!=", ',')
    return replace


for tc in tests:
    migrated = re.sub(r"(REQUIRE\().*(!=)", repl=replacer_ne, string=tc.read_text(encoding='utf-8'))
    tc.write_text(migrated, 'utf-8')