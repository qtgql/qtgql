Release type: minor

### Features
- [x] add `version` endpoint to the cli
- [x] support recursive search of config file.
- [x] Create a QML module for each operation, you will be able to import it in qml
like this `Generated.<EnvName>.<OperationName>` This allows QtCreator to provide
code completion, and you can type your properties based on the operation types.
- [x] add qml wrapper to operation something like `Use<operationName>` component.
  This would alias the signals in the real operation and store the shared pointer to it.


### Trivial changes
- Add `Typer[all]` to dependencies.
- add static version to the root cmake and in `qtgqlcodegen` `__init__.py`
