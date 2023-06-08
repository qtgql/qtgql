import contextlib
import glob
from functools import cached_property
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import CMakeToolchain


class helloTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def generate(self) -> None:
        # should be removed when https://github.com/conan-io/conan-center-index/pull/17539 gets merged.
        assert self.qt6_install_dir
        assert self.qt6_install_dir.exists()
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
        tc.generate()

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @cached_property
    def aqt_install_dir(self) -> Path:
        ret = Path.home() / "MyConnandeps" / "Qt"

        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def qt6_install_dir(self) -> Path | None:
        relative_to = self.aqt_install_dir / "6.5.0"
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
