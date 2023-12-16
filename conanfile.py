from __future__ import annotations

import os
import subprocess
import sys
from functools import cached_property
from pathlib import Path
from typing import ClassVar, Literal

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class PATHS:
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).parent


ConanBool = [True, False]

__version__: str = "0.138.0"

IS_GITHUB_ACTION = os.environ.get("IS_GITHUB_ACTION", False)


class EnvManager:
    def __init__(self, env_var: str = "PATH") -> None:
        self._env_avr = env_var
        self._paths: list[Path] = []

    def _add_to_environ(self, p: Path) -> None:
        path_delimiter = ":" if sys.platform == "linux" else ";"
        paths = os.environ.get(self._env_avr, "").split(path_delimiter)
        paths.append(p.resolve(True).as_uri())
        os.environ.setdefault(self._env_avr, path_delimiter.join(paths))

    def add(self, p: Path) -> None:
        self._paths.append(p)

    def commit(self) -> None:
        for p in self._paths:
            self._add_to_environ(p)


class Qt6Installer:
    def __init__(
        self,
        os_name: Literal["windows"] | Literal["linux"],
        version: str,
        arch: str,
        arch_folder: str,
    ):
        self.os_name = os_name
        self.is_windows = os_name == "windows"
        self.is_linux = os_name == "linux"
        self.version = version
        self.env_manager = EnvManager()
        self.arch = arch
        self.arch_folder = arch_folder  # aqt installs in different dir name than the cli.

    @cached_property
    def aqt_install_dir(self) -> Path:
        ret = Path.home() / "MyConnandeps" / "Qt"

        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def qt_root_dir(self) -> Path | None:
        aqt_versioned_root = self.aqt_install_dir / self.version
        if aqt_versioned_root.exists():
            for folder in os.scandir(aqt_versioned_root):
                if folder.name == self.arch_folder:
                    return Path(folder.path).resolve(True)

    @property
    def qt6_cmake_config(self) -> Path:
        assert self.qt_root_dir.exists()
        return next(self.qt_root_dir.glob("**/Qt6Config.cmake")).parent

    @property
    def dll_path(self) -> Path:
        assert self.qt_root_dir.exists()
        return self.qt_root_dir / "bin"

    def installed(self) -> bool:
        return bool(self.qt_root_dir)

    def set_env_vars(self) -> None:
        self.env_manager.add(self.dll_path.resolve(True))
        self.env_manager.commit()
        os.environ.setdefault(
            "QT_PLUGIN_PATH",
            (self.qt_root_dir / "plugins").resolve(True).as_uri(),
        )
        if self.is_linux:
            os.environ.setdefault(
                "LD_LIBRARY_PATH",
                (self.qt_root_dir / "lib").resolve(True).as_uri(),
            )

    def install(self) -> None:
        if not self.installed():
            subprocess.run(
                f"poetry run aqt install-qt {self.os_name} "
                f"desktop {self.version} {self.arch} "
                f"--outputdir {self.aqt_install_dir} "
                f"-m qtwebsockets".split(" "),
            ).check_returncode()
            assert self.qt6_cmake_config.exists()
        self.set_env_vars()


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
    options = {"qt_version": ["6.5.2", "6.6.0"], "verbose": ConanBool, "test": ConanBool}  # noqa
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

    @property
    def build_type(self) -> str:
        return self.settings.build_type.value

    @property
    def is_windows(self) -> bool:
        return self.os_name == "windows"

    @property
    def is_linux(self) -> bool:
        return self.os_name == "linux"

    @cached_property
    def qt_version(self) -> str:
        qt_version = self.options.qt_version.value
        return qt_version

    @cached_property
    def should_test(self) -> bool:
        if self.options.test.value in ("True", "true", True):
            return True
        return False

    def generate(self) -> None:
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # if self.is_linux() or IS_GITHUB_ACTION: # couldn't get this to build on Windows ATM.
        if self.is_linux:
            arch = "gcc_64"
            arch_folder = "gcc_64"
        elif self.is_windows:
            if "msvc" in self.settings.compiler.value:
                arch = "win64_msvc2019_64"
                arch_folder = "msvc2019_64"
            else:
                arch = "win64_mingw"
                arch_folder = "mingw_64"
        qt_installer = Qt6Installer(
            self.os_name,
            self.options.qt_version.value,
            arch=arch,
            arch_folder=arch_folder,
        )
        qt_installer.install()
        tc.cache_variables["QT_DL_LIBRARIES"] = str(
            qt_installer.dll_path,
        )  # used by catch2 to discover tests/
        tc.cache_variables["Qt6_DIR"] = str(qt_installer.qt6_cmake_config)
        tc.cache_variables["QTGQL_TESTING"] = self.should_test
        tc.cache_variables["TESTS_QML_DIR"] = (self.build_path / "tests").as_posix()
        if self.is_windows:
            tc.cache_variables["CMAKE_CXX_COMPILER"] = "c++.exe"

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
