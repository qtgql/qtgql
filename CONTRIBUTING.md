### Fork
To contribute create a fork and clone your fork locally.

### Install dependencies
We use Poetry for managing dependencies.
```bash
poetry install
```

### Install pre-commit hooks
```bash
pre-commit install
```

### Add a `RELEASE.md` file that describes your PR.
```md
Release type: <patch/minor/major>

<description>
```

### Running tests
```bash
make test
```

### Documenting
Your changes require to update the docs?
We use mkdocs-material

run `poetry run mkdocs serve` for a local server.
