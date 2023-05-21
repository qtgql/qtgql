import glob
import subprocess
from functools import cached_property
from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import CMakeToolchain
from conan.tools.scm import Git
import sys
from tests.conftest import PATHS


ConanBool = [True, False]


def get_cmake_qt6_dir(version: str = "6.5.0") -> Path:
    root = Path(Path(sys.executable).anchor)
    res = glob.glob(f"Qt/{version}/**/Qt6Config.cmake", recursive=True, root_dir=root)
    return (root / res[0]).resolve(True).parent


def get_version_from_poetry():
    res = subprocess.run("poetry version".split(" "), capture_output=True)
    return res.stdout.decode().replace("qtgql ", "").rstrip()


class QtGqlRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    name = "qtgql"
    license = "MIT"
    author = "Nir Benlulu nrbnlulu@gmail.com"
    url = "https://github.com/qtgql/qtgql"
    description = "GraphQL codegen client library for Qt"
    topics = ("GraphQL", "Qt", "codegen")
    version = get_version_from_poetry()
    build_policy = "missing"
    options = {"qt_version": ["6.5.0"], "verbose": ConanBool}
    default_options = {
        "verbose": False,
        "qt_version": "6.5.0",
    }

    def source(self) -> None:
        git = Git(self)
        git.clone("https://github.com/qtgql/qtgql.git", target=".")
        git.checkout("migrate_to_cpp")

    def requirements(self) -> None:
        ...

    def build_requirements(self) -> None:
        ...

    def layout(self) -> None:
        cmake_layout(self)

    @cached_property
    def aqt_install_dir(self) -> Path:
        ret = Path.home() / "MyConnandeps" / "Qt"

        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def os_name(self):
        return self.settings.os.value.lower()

    def is_windows(self) -> bool:
        return self.os_name == "windows"

    def is_linux(self) -> bool:
        return self.os_name == "linux"

    @property
    def should_test(self) -> bool:
        return True

    def generate(self) -> None:
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables[
            "binaryDir"
        ] = PATHS.QTGQL_TEST_TARGET.as_posix()  # cmake works with posix paths only
        tc.variables["QTGQL_TESTING"] = self.should_test
        tc.cache_variables["Qt6_DIR"] = get_cmake_qt6_dir().as_posix()
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()


#

# if __name__ == "__main__":

#     rec
