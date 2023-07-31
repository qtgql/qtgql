This Tutorial will walk you threw creating a Qt project using qtgql
from ground up.
<!-- TODO: add link Final code at github -->

This subject of this project will be a QML application that shows
countries information using a public GraphQL API that can be found [here](https://countries.trevorblades.com/)

<!-- TODO: add link to code -->
### Prerequisites
* Required by QtGql:
    - Python <= 3.8
    - CMake
* Required for this tutorial:
    - Conan C++ Package manager
    - [Python-Poetry](https://python-poetry.org/docs/#installation) installed we we'll use it to manage python dependencies for this tutorial
    though feel free to use any other python package manager.

### Project layout
Create a new directory named countries and setup your git/github.

We will use the "src" + CMake layout.

```bash
countries
├── 3rdparty
├── CMakeLists.txt
└── src
    ├── main.cpp
    └── qml
        └── main.qml
```

### Setup Build requirements and QtGql
Add qtgql as a submodule to 3rdparty directory.
```bash
cd 3rdparty/ && git submodule add https://github.com/qtgql/qtgql.git
cd ..
```
In order to build qtgql you'll need Qt installed.
for this tutorial we will use a conan recipe that will install Qt and set the needed variables
for cmake, see the following note.
??? Note "Install Qt"

    First  lets setup Python virtualenv using poetry.

    ```bash
    poetry init
    ```
    just hit `Enter` until it is done.

    ```bash
    poetry add conan aqtinstall
    ```
    !!! Note
        from now on every command should be prefixed with `poetry run <command>`


    Now create this conan recipe. Note that this is not a usauall recipe because
    at the moment of creating this tutorial Qt6 wasn't working well with native conan.
    `./conanfile.py`
    ```py
    from __future__ import annotations

    import contextlib
    import glob
    import logging
    import os
    import subprocess
    from functools import cached_property
    from pathlib import Path
    from typing import ClassVar
    from venv import logger

    from conan import ConanFile
    from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


    class PATHS:
        PROJECT_ROOT: ClassVar[Path] = Path(__file__).parent


    ConanBool = [True, False]


    __version__: str = "0.1.0"


    class QtGqlCountriesRecipe(ConanFile):
        settings = "os", "compiler", "build_type", "arch"
        name = "countries"
        license = "MIT"
        version = __version__
        build_policy = "missing"


        exports_sources = "CMakeLists.txt", "src/*"

        def requirements(self) -> None:
            ...

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
        def qt_version(self) -> str:
            return "6.5.0"

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



        def generate(self) -> None:
            if not self.qt6_install_dir:
                subprocess.run(
                    f"poetry run aqt install-qt {self.os_name} "
                    f"desktop {self.qt_version} {self.qt_arch} "
                    f"--outputdir {self.aqt_install_dir} "
                    f"-m qtwebsockets".split(" "),
                ).check_returncode()
            os.environ.setdefault(
                "QT_PLUGIN_PATH",
                (self.qt6_install_dir.parent.parent.parent / "plugins").resolve(True).as_uri(),
            )
            os.environ.setdefault(
                "LD_LIBRARY_PATH",
                (self.qt6_install_dir.parent.parent.parent / "lib").resolve(True).as_uri(),
            )
            paths = os.environ.get("PATH").split(":")
            paths.append((self.qt6_install_dir.parent.parent.parent / "bin").resolve(True).as_uri())
            os.environ.setdefault("PATH", ":".join(paths))
            assert self.qt6_install_dir
            assert self.qt6_install_dir.exists()
            deps = CMakeDeps(self)
            deps.generate()
            tc = CMakeToolchain(self)
            tc.cache_variables["Qt6_DIR"] = str(self.qt6_install_dir)
            tc.generate()

        def build(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

        def package(self):
            cmake = CMake(self)
            cmake.install()
    ```

    Now to install Qt run:
    ```bash
    poetry run conan install .
    ```

To install the `qtgql` codegenerator we need to add it as a Python dependency:
```bash
poetry add "3rdparty/qtgql/"
```

Now lets setup CMake.
*Content of `./CMakeLists.txt`*
```cmake
cmake_minimum_required(VERSION 3.25.0)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(countries VERSION 0.1.0
        LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_subdirectory(3rdparty/qtgql)

file(GLOB_RECURSE SOURCES "src/*.cpp" "src/*.hpp")

file(GLOB_RECURSE HEADERS "src/*.hpp")
find_package(Qt6 REQUIRED COMPONENTS Core Quick)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} PRIVATE qtgql::qtgql
        Qt6::Core Qt6::Quick
        )
```

### Setup a QML window

Inside `main.cpp` past this code

```cpp
#include <QtGui>
#include <QtQuick>
#include "filesystem"

namespace fs = std::filesystem;

int main(int argc, char *argv[]){
    QGuiApplication app(argc, argv);
    QQmlApplicationEngine engine;
    QUrl url((fs::path(__FILE__).parent_path() / "qml" / "main.qml").c_str());
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
                if (!obj && url == objUrl)
                    QCoreApplication::exit(-1);
            }, Qt::QueuedConnection);
    engine.load(url);

    return QGuiApplication::exec();
}
```

Inside `main.qml` past this code:
```qml
import QtQuick

Window{
    width: 500;
    height: 400;
    visible: true;

    Rectangle{
        anchors.fill: parent;
        color: "red";
    }
}
```

Now lets build and run
```bash
poetry run conan build .
build/Debug/countries
```
Now you should see something like this:

![screenshot](../assets/red_win.png)

### Using the [countries'](https://countries.trevorblades.com/) schema.

Create a directory for graphql, we'll call it `graphql`

Inside `graphql` create 3 files
- `schema.graphql` - Copy the SDL from [here](https://github.com/Urigo/graphql-cli/blob/master/integration/test-project/schema/schema.graphql)
- `operations.graphql` - Here you would define your operations.
- `qtgqlconfig.py` - Here you would define configurations for `qtgql`

by now you should have the following tree:
```bash
countries
├── 3rdparty
│   └── qtgql
│       ├── <etc>
├── build
│   └── Debug
│       ├── <etc>
├── CMakeLists.txt
├── CMakeUserPresets.json
├── conanfile.py
├── poetry.lock
├── pyproject.toml
└── src
    ├── graphql
    │   ├── operations.graphql
    │   ├── qtgqlconfig.py
    │   └── schema.graphql
    ├── main.cpp
    └── qml
        └── main.qml
```

Content of `qtgqlconfig.py`
```py
from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig


config = QtGqlConfig(graphql_dir=Path(__file__).parent, env_name="Countries")
```
- `graphql_dir` - This would let qtgql know where to find your schema and operation definition.
- `env_name` - Will be used to namespace this schema at the generated code to avoid collisions
with other potential schemas.

### Writing your first query
QtGql is heavily relying on operations.
Each operation would generate it's own types that mirror concrete types that would be generated
inside `schema.hpp`

Inside `operations.graphql` create an operation that will query for all available countries:

```graphql
query AllCountries{
  countries{
    capital
    emoji
    code
  }
}
```
Now run the codegen:
```bash
poetry run qtgql gen
```
