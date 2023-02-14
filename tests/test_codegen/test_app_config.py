import contextlib
import importlib
import inspect
import sys
import tempfile
import uuid
from pathlib import Path
from types import ModuleType

import pytest
from qtgql.codegen.py.compiler.config import QtGqlConfig


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


def test_fetch_schema(schemas_server, tmp_path):
    file = tmp_path / "generate.py"
    assert not file.exists()
    config = QtGqlConfig(url=schemas_server.address.replace("ws", "http"), output=file)
    config.fetch()
    with open(file) as f:
        assert f.read(), "module was empty"
    mod_id = uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(mod_id, file)
    foo = importlib.util.module_from_spec(spec)
    sys.modules[mod_id] = foo

    spec.loader.exec_module(foo)
    assert inspect.isclass(
        importlib.import_module(mod_id).Query
    )  # Query should always be generated
