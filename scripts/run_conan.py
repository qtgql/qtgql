import os
import sys
from pathlib import Path

from conans.conan import run

if __name__ == "__main__":
    TEST_PACKAGE = "conan test conan/test_package qtgql/0.119.9 --build=missing"
    CREATE = "conan create . --build=missing"
    BUILD_TESTS = "conan build . -o test=True "
    os.environ.setdefault("NOT_ON_C3I", "1")
    WINDOWS_CLANG = "conan build . -o test=True -s build_type=Debug --build=missing -pr=profiles/Windows_clang"
    WINDOWS_MINGW = "conan build . -o test=True -s build_type=Debug --build=missing -pr=profiles/Windows_mingw"
    CONFIG_SHOW = "conan config show '*' -pr=profiles/Windows_mingw"
    os.chdir(Path(__file__).parent.parent)  # change working dir to root
    sys.argv = WINDOWS_MINGW.split(" ")
    try:
        run()
    except BaseException as e:
        ...
