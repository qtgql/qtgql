import os
import sys
from pathlib import Path

from conans.conan import run

if __name__ == "__main__":
    TEST = "conan test conan/test_package qtgql/0.119.9 --build=missing -pr=profiles/Linux"
    CREATE = "conan create . -pr=profiles/Linux --build=missing"
    os.chdir(Path(__file__).parent.parent)  # change working dir to root
    sys.argv = TEST.split(" ")
    sys.exit(run())
