from __future__ import annotations

import contextlib
import glob
import os
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

__version__: str = "0.135.4"


class PathManager:
    def __init__(self, recipe: QtGqlRecipe) -> None:
        self._paths: list[Path] = []
        self.recipe = recipe

    def _add_to_environ(self, p: Path) -> None:
        path_name = "PATH"
        path_delimiter = ":" if self.recipe.is_linux() else ";"
        gh_action_path = os.getenv("GITHUB_PATH")
        if gh_action_path:
            with open(gh_action_path, "a") as f:  # noqa: PTH123
                f.write(f"{p!s}{path_delimiter}")
        paths = os.environ.get(path_name).split(path_delimiter)
        paths.append(p.resolve(True).as_uri())
        os.environ.setdefault(path_name, path_delimiter.join(paths))

    def add(self, p: Path) -> None:
        self._paths.append(p)

    def commit(self) -> None:
        for p in self._paths:
            self._add_to_environ(p)


class QtGqlRecipe(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    name = "qtgql"
    license = "MIT"
    author = "Nir Benlulu nrbnlulu@gmail.com"
    url = "https://github.com/qtgql/qtgql"
    description = "GraphQL codegen client library for Qt"
    topics = ("GraphQL", "Qt", "codegen")
    version = __version__
    build_policy = "missing"
    options = {"qt_version": ["6.5.0"], "verbose": ConanBool, "test": ConanBool}  # noqa
    default_options = {  # noqa
        "verbose": False,
        "qt_version": "6.5.0",
        "test": False,
    }

    exports_sources = "CMakeLists.txt", "include/*", "pyproject.toml"

    def requirements(self) -> None:
        ...

    def build_requirements(self) -> None:
        self.test_requires("catch2/3.4.0")

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
    def pathmanager(self) -> PathManager:
        return PathManager(self)

    @cached_property
    def qt_version(self) -> str:
        qt_version = self.options.qt_version.value
        return qt_version

    @property
    def qt_arch(self) -> str:
        if self.is_linux():
            return "gcc_64"
        elif self.is_windows():
            return "win64_mingw"

    @cached_property
    def aqt_install_dir(self) -> Path:
        ret = Path.home() / "MyConnandeps" / "Qt"

        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def qt6_install_dir(self) -> Path | None:
        relative_to = self.aqt_install_dir / self.qt_version
        if relative_to.exists():
            prev = Path.cwd()
            os.chdir(relative_to)
            res = glob.glob("**/Qt6Config.cmake", recursive=True)
            os.chdir(prev)
            with contextlib.suppress(IndexError):
                p = (relative_to / res[0]).resolve(True)
                return p.parent

    @cached_property
    def should_test(self) -> bool:
        if self.options.test.value in ("True", "true", True):
            if not PATHS.QTGQL_TEST_TARGET.exists():
                PATHS.QTGQL_TEST_TARGET.mkdir()
            return True
        return False

    def generate(self) -> None:
        if not self.qt6_install_dir:
            subprocess.run(
                f"poetry run aqt install-qt {self.os_name} "
                f"desktop {self.qt_version} {self.qt_arch} "
                f"--outputdir {self.aqt_install_dir} "
                f"-m qtwebsockets".split(" "),
            ).check_returncode()
        assert self.qt6_install_dir.exists()
        os.environ.setdefault(
            "QT_PLUGIN_PATH",
            (self.qt6_install_dir.parent.parent.parent / "plugins").resolve(True).as_uri(),
        )
        if self.is_linux():
            os.environ.setdefault(
                "LD_LIBRARY_PATH",
                (self.qt6_install_dir.parent.parent.parent / "lib").resolve(True).as_uri(),
            )

        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        qt_dl_path = self.qt6_install_dir.parent.parent.parent / "bin"
        self.pathmanager.add(qt_dl_path)
        tc.cache_variables["QT_DL_LIBRARIES"] = str(qt_dl_path)
        tc.variables[
            "binaryDir"
        ] = PATHS.QTGQL_TEST_TARGET.as_posix()  # cmake works with posix paths only
        tc.cache_variables["QTGQL_TESTING"] = self.should_test
        tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
        if self.is_windows():
            tc.cache_variables["CMAKE_CXX_COMPILER"] = "c++.exe"

        self.pathmanager.commit()
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
