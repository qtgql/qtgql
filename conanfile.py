import subprocess
from functools import cached_property
from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import CMakeToolchain
from conan.tools.scm import Git

ConanBool = [True, False]


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
        self.test_requires("catch2/3.3.2")

    def build_requirements(self) -> None:
        self.tool_requires("cmake/3.26.3")

    def layout(self) -> None:
        cmake_layout(self)

    @cached_property
    def aqt_install_dir(self) -> Path:
        ret = Path.home() / "MyConnandeps" / "Qt"
        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def qt_arch(self) -> str:
        os_name = self.settings.os.value.lower()
        if os_name == "linux":
            return "gcc_64"
        return self.settings.arch.value

    @cached_property
    def qt6_install_dir(self):
        qt_version = "6.5.0"
        return self.aqt_install_dir / qt_version / self.qt_arch / "lib" / "cmake" / "Qt6"

    @property
    def should_test(self) -> bool:
        return self.settings.get_safe("build_type", default="Debug") == "Debug"

    def generate(self) -> None:
        qt_version = "6.5.0"
        os_name = self.settings.os.value.lower()
        if not self.qt6_install_dir.exists():
            subprocess.run(
                f"aqt install-qt {os_name} desktop {qt_version} {self.qt_arch} --outputdir {str(self.aqt_install_dir)} -m qtwebsockets".split(
                    " ",
                ),
            )
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["QTGQL_TESTING"] = self.should_test
        tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self.should_test:
            cmake.test(build_type="Debug", target="test_qtgql")

    def package(self):
        cmake = CMake(self)
        cmake.install()


#
# if __name__ == "__main__":
#     rec
