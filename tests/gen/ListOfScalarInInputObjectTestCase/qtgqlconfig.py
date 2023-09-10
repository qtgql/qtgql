from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(
        r"D:\Programming\Work\qtgql\tests\gen\ListOfScalarInInputObjectTestCase\graphql",
    ),
    env_name="ListOfScalarInInputObjectTestCase",
    debug=False,
    qml_plugins_path="${CMAKE_BINARY_DIR}/tests",
)
