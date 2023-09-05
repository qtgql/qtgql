from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(r"D:\Programming\Work\qtgql\tests\gen\NonNodeUnionTestCase\graphql"),
    env_name="NonNodeUnionTestCase",
    debug=False,
    qml_plugins_path="${CMAKE_BINARY_DIR}/tests",
)
