from __future__ import annotations

import logging
import subprocess
from functools import cached_property
from pathlib import Path
from typing import ClassVar

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class PATHS:
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).parent
    QTGQL_TEST_TARGET: ClassVar[Path] = PROJECT_ROOT / "tests" / "build"


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
    options = {"qt_version": ["6.5.0"], "verbose": ConanBool, "test": ConanBool}  # noqa
    default_options = {  # noqa
        "verbose": False,
        "qt_version": "6.5.0",
        "test": False,
    }

    exports_sources = "CMakeLists.txt", "include/*", "pyproject.toml"

    def requirements(self) -> None:
        self.requires("qt/6.5.0")

    def build_requirements(self) -> None:
        self.test_requires("catch2/3.4.0")

    def configure(self) -> None:
        self.options["qt"].qtwebsockets = True

    def layout(self) -> None:
        cmake_layout(self)

    @property
    def os_name(self):
        return self.settings.os.value.lower()

    def is_windows(self) -> bool:
        return self.os_name == "windows"

    def is_linux(self) -> bool:
        return self.os_name == "linux"

    @cached_property
    def should_test(self) -> bool:
        if self.options.test.value in ("True", "true", True):
            if not PATHS.QTGQL_TEST_TARGET.exists():
                PATHS.QTGQL_TEST_TARGET.mkdir()
            return True
        return False

    def generate(self) -> None:
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables[
            "binaryDir"
        ] = PATHS.QTGQL_TEST_TARGET.as_posix()  # cmake works with posix paths only
        tc.cache_variables["QTGQL_TESTING"] = self.should_test
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qtgql"]  # checks that can link against this lib name.
