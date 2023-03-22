### Fork
To contribute create a fork and clone your fork locally.

### Install dependencies
We use Poetry for managing dependencies.
```console
poetry install -E codegen
```

### Add a `RELEASE.md` file that describes your PR.
```md
Release type: <patch/minor/major>

<description>
```

### Running tests
```console
make test
```

### Documenting
Your changes require to update the docs?
We use mkdocs-material

run `poetry run mkdocs serve` for a local server.
