from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(r"D:\Programming\Work\qtgql\tests\gen\ObjectWithListOfObjectTestCase\graphql"),
    env_name="ObjectWithListOfObjectTestCase",
    debug=True,
    qml_plugins_path="${CMAKE_BINARY_DIR}/tests",
)
