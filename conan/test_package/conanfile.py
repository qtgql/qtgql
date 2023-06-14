import contextlib
import glob
import subprocess
from functools import cached_property
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class helloTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    options = {"qt_version": ["6.5.0"]}
    default_options = {
        "qt_version": "6.5.0",
    }

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self) -> None:
        # should be removed when https://github.com/conan-io/conan-center-index/pull/17539 gets merged.
        if not self.qt6_install_dir:
            subprocess.run(
                f"poetry run aqt install-qt {self.os_name} "
                f"desktop {self.qt_version} {self.qt_arch} "
                f"--outputdir {self.aqt_install_dir!s} "
                f"-m qtwebsockets".split(" "),
            ).check_returncode()
        assert self.qt6_install_dir
        assert self.qt6_install_dir.exists()
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc = CMakeToolchain(self)
        tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def os_name(self):
        return self.settings.os.value.lower()

    def is_windows(self) -> bool:
        return self.os_name == "windows"

    def is_linux(self) -> bool:
        return self.os_name == "linux"

    @cached_property
    def qt_version(self) -> str:
        qt_version = self.options.qt_version.value
        if self.is_windows() and "6.5" in qt_version:
            return "6.4.3"
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
        res = glob.glob("**/Qt6Config.cmake", root_dir=relative_to, recursive=True)
        with contextlib.suppress(IndexError):
            p = (relative_to / res[0]).resolve(True)
            return p.parent

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            cmd = (Path(self.cpp.build.bindir) / "example").resolve(True).absolute()
            self.run(str(cmd), env="conanrun")
