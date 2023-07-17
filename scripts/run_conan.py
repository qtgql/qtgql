import os
import sys
from pathlib import Path

from conans.conan import run

if __name__ == "__main__":
    TEST_PACKAGE = "conan test conan/test_package qtgql/0.119.9 --build=missing"
    CREATE = "conan create . --build=missing"
    BUILD_TESTS = "conan build . -o test=True"
    os.chdir(Path(__file__).parent.parent)  # change working dir to root
    sys.argv = BUILD_TESTS.split(" ")
    sys.exit(run())
