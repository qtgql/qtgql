import subprocess

from tests.conftest import IS_GITHUB_ACTION
from tests.test_codegen.testcases import generate_testcases, implemented_testcases


def generate_all_testscases() -> None:
    generate_testcases(*implemented_testcases)

    if not IS_GITHUB_ACTION:
        # run pc hooks to reduce diffs
        subprocess.run("pre-commit run -a".split(" "), check=False)
        subprocess.run("pre-commit run -a".split(" "), check=False)


if __name__ == "__main__":
    generate_all_testscases()
