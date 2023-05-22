import contextlib
import glob
import logging
import subprocess
from functools import cached_property
from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import CMakeToolchain
from conan.tools.scm import Git

from tests.conftest import PATHS


ConanBool = [True, False]


logger = logging.getLogger(__name__)


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
        self.test_requires("catch2/3.1.0")

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

    @cached_property
    def qt_version(self) -> str:
        op_version = self.options.qt_version.value
        if self.is_windows() and op_version == "6.5.0":
            logger.warning(
                "Can't compile with aqt installer on Windows just yet fall back to 6.4.3",
            )
            return "6.4.3"
        return op_version

    @property
    def qt_arch(self) -> str:
        if self.is_linux():
            return "gcc_64"
        elif self.is_windows():
            return "win64_mingw"

    @property
    def qt6_install_dir(self) -> Path | None:
        relative_to = self.aqt_install_dir / self.qt_version
        res = glob.glob("**/Qt6Config.cmake", root_dir=relative_to, recursive=True)
        with contextlib.suppress(IndexError):
            p = (relative_to / res[0]).resolve(True)
            return p.parent

    @property
    def should_test(self) -> bool:
        return True

    def generate(self) -> None:
        if not self.qt6_install_dir:
            subprocess.run(
                f"poetry run aqt install-qt {self.os_name} "
                f"desktop {self.qt_version} {self.qt_arch} "
                f"--outputdir {str(self.aqt_install_dir)} "
                f"-m qtwebsockets".split(" "),
            )
        assert self.qt6_install_dir
        assert self.qt6_install_dir.exists()
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables[
            "binaryDir"
        ] = PATHS.QTGQL_TEST_TARGET.as_posix()  # cmake works with posix paths only
        tc.variables["QTGQL_TESTING"] = self.should_test
        tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
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
