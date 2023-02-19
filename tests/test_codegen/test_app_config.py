import contextlib
import importlib
import sys
import tempfile
import uuid
from pathlib import Path
from types import ModuleType

import pytest
from qtgql.codegen.py.compiler.config import QtGqlConfig

from tests.test_codegen.test_py.testcases import ScalarsTestCase


@contextlib.contextmanager
def get_fake_module() -> ModuleType:
    with tempfile.TemporaryDirectory() as tmp_path:
        id_ = uuid.uuid4().hex
        file = Path(tmp_path) / f"{id_}.py"
        with open(file, "w") as f:
            f.write("")

        spec = importlib.util.spec_from_file_location(id_, file)
        foo = importlib.util.module_from_spec(spec)
        sys.modules[id_] = foo
        spec.loader.exec_module(foo)
        yield foo


@pytest.fixture()
def fake_module(tmp_path) -> ModuleType:
    with get_fake_module() as m:
        yield m


def test_generate_from_schema(tmp_path):
    config = QtGqlConfig(graphql_dir=tmp_path)
    config.schema_path.write_text(str(ScalarsTestCase.schema))
    config.operations_dir.write_text(ScalarsTestCase.query)
    config.generate()
    assert config.generated_types_dir.read_text()
    assert config.generated_handlers_dir.read_text()
