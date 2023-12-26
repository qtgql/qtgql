### Fork
To contribute create a fork and clone your fork locally.

### Install dependencies
We use [Poetry](https://python-poetry.org/) for managing dependencies.
```bash
poetry install
```

### Install [pre-commit](https://pre-commit.com/) hooks
```bash
pre-commit install
```

### Add a `RELEASE.md` file that describes your PR  in the project root.
```md
Release type: <patch/minor/major>

<description>
```
### Generate tests cases files
Go to `tests/tests_codegen/testcases.py` call https://github.com/qtgql/qtgql/blob/a40852623739394dc3418df42831a17bb99997a5/tests/test_codegen/testcases.py#L1076
with the desired testcases.

### Build
conan would generate cmake presets for IDE's usage as well.
add the option `test_core` to build the tests for the core library.
add the option `test_gen` to build the tests for the generated code.
 ```bash
poetry run conan build . -o test_core=True -o test_gen=True
```
```
### Testing
Run tests GraphQL server
```bash
poetry run python -m tests.scripts.tests_server
```
Run pytest, CTest is called from python and C++ tests are collected automatically.
```bash
poetry run pytest
```

### Documenting
Your changes require to update the docs?
We use mkdocs-material

run `poetry run mkdocs serve` for a local server.
