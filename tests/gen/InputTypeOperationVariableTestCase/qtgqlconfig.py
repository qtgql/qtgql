from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(
        r"D:\Programming\Work\qtgql\tests\gen\InputTypeOperationVariableTestCase\graphql",
    ),
    env_name="InputTypeOperationVariableTestCase",
    debug=False,
    qml_plugins_path="${CMAKE_BINARY_DIR}/tests",
)