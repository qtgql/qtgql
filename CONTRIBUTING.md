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
### Generate tests files
This would generate boilerplate code for the testcases in `tests/tests_codegen/testcases.py`
```bash
make generate_test_files
```
### Build
conan would generate cmake presets for IDE's usage as well.
```bash
poetry run conan build . -o test=True
```
### Testing
Run tests GraphQL server
```bash
make serve_tests
```
Run pytest, CTest is called from python and C++ tests are collected automatically.
```bash
make test
```

### Documenting
Your changes require to update the docs?
We use mkdocs-material

run `poetry run mkdocs serve` for a local server.
